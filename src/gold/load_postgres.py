"""Load Gold Parquet tables into the analytical PostgreSQL database."""
from __future__ import annotations

import os
import re
from contextlib import closing
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
_BATCH_SIZE = 10_000


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória não definida: {name}")
    return value


def _postgres_type(data_type: pa.DataType) -> str:
    if pa.types.is_string(data_type) or pa.types.is_large_string(data_type):
        return "TEXT"
    if pa.types.is_boolean(data_type):
        return "BOOLEAN"
    if pa.types.is_int8(data_type) or pa.types.is_int16(data_type):
        return "SMALLINT"
    if pa.types.is_int32(data_type):
        return "INTEGER"
    if pa.types.is_int64(data_type):
        return "BIGINT"
    if pa.types.is_float32(data_type):
        return "REAL"
    if pa.types.is_float64(data_type):
        return "DOUBLE PRECISION"
    if pa.types.is_decimal(data_type):
        return f"NUMERIC({data_type.precision},{data_type.scale})"
    if pa.types.is_date(data_type):
        return "DATE"
    if pa.types.is_timestamp(data_type):
        return "TIMESTAMP WITH TIME ZONE" if data_type.tz else "TIMESTAMP WITHOUT TIME ZONE"
    if pa.types.is_binary(data_type) or pa.types.is_large_binary(data_type):
        return "BYTEA"
    raise TypeError(f"Tipo Parquet não suportado para PostgreSQL: {data_type}")


def _connect(database: str):
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=database,
        user=_required_env("POSTGRES_USER"),
        password=_required_env("POSTGRES_PASSWORD"),
    )


def _ensure_database(database: str) -> None:
    with closing(_connect("postgres")) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
                print(f"Banco analítico criado: {database}")


def _load_table(connection, table_dir: Path, table_name: str) -> None:
    parquet_files = sorted(table_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado para {table_name} em {table_dir}")

    schema = pq.ParquetFile(parquet_files[0]).schema_arrow
    columns = schema.names
    if not columns or len(columns) != len(set(columns)):
        raise ValueError(f"Schema Parquet inválido para a tabela {table_name}")

    staging_name = f"__load_{table_name}"
    column_definitions = sql.SQL(", ").join(
        sql.SQL("{} {}").format(sql.Identifier(field.name), sql.SQL(_postgres_type(field.type)))
        for field in schema
    )
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
        sql.Identifier(staging_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(staging_name))
            )
            cursor.execute(
                sql.SQL("CREATE TABLE {} ({})").format(
                    sql.Identifier(staging_name),
                    column_definitions,
                )
            )

            row_count = 0
            for parquet_path in parquet_files:
                parquet_file = pq.ParquetFile(parquet_path)
                if parquet_file.schema_arrow.names != columns:
                    raise ValueError(f"Schema inconsistente entre arquivos Parquet da tabela {table_name}")
                for batch in parquet_file.iter_batches(batch_size=_BATCH_SIZE):
                    rows = [
                        tuple(row[column] for column in columns)
                        for row in batch.to_pylist()
                    ]
                    if rows:
                        execute_values(cursor, insert_query, rows, page_size=_BATCH_SIZE)
                        row_count += len(rows)

            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name))
            )
            cursor.execute(
                sql.SQL("ALTER TABLE {} RENAME TO {}").format(
                    sql.Identifier(staging_name),
                    sql.Identifier(table_name),
                )
            )

    print(f"Tabela {table_name} substituída: {row_count:,} linhas.")


def load_gold_to_postgres(
    gold_dir: Path | None = None,
    database: str | None = None,
) -> None:
    project_root = Path(__file__).resolve().parents[2]
    source_dir = gold_dir or project_root / "Data_gold"
    target_database = database or os.environ.get("GOLD_DB_NAME", "territorial_gold")

    if not _IDENTIFIER.fullmatch(target_database):
        raise ValueError("GOLD_DB_NAME deve conter apenas letras minúsculas, números e underscores.")
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Diretório Gold não encontrado: {source_dir}")

    table_dirs = sorted(
        path for path in source_dir.iterdir()
        if path.is_dir() and _IDENTIFIER.fullmatch(path.name)
    )
    if not table_dirs:
        raise FileNotFoundError(f"Nenhuma pasta de tabela Gold encontrada em {source_dir}")

    _ensure_database(target_database)
    with closing(_connect(target_database)) as connection:
        for table_dir in table_dirs:
            _load_table(connection, table_dir, table_dir.name)


if __name__ == "__main__":
    load_gold_to_postgres()
