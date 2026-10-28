"""Sessão Spark e leitura dos JSON brutos (CAGED e IBGE/SIDRA)."""
from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from .config import CAGED_SCHEMA, SIDRA_SCHEMA


def get_spark(app_name: str = "gold_star_schema") -> SparkSession:
    spark = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "8")
        # Casts inválidos viram NULL (comportamento do Spark 3.x) em vez de
        # erro (padrão do Spark 4.x). Os NULLs gerados são contados nas validações.
        .config("spark.sql.ansi.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_caged_raw(spark: SparkSession, paths: list[str]) -> DataFrame:
    """NDJSON, esquema explícito. FAILFAST: linha malformada interrompe a leitura."""
    df = spark.read.schema(CAGED_SCHEMA).option("mode", "FAILFAST").json(paths)
    return df.select(*[F.trim(F.col(c)).alias(c) for c in CAGED_SCHEMA.fieldNames()])


def read_sidra_raw(spark: SparkSession, path: str) -> DataFrame:
    """Array JSON no padrão SIDRA. O 1º elemento é um dicionário de cabeçalho
    (NC = 'Nível Territorial (Código)'); só linhas com NC numérico são dados."""
    df = (
        spark.read.schema(SIDRA_SCHEMA)
        .option("multiLine", True)
        .option("mode", "FAILFAST")
        .json(path)
    )
    return df.filter(F.col("NC").rlike(r"^\d+$")).select(
        F.col("NC").alias("nivel_cod"),
        F.col("NN").alias("nivel_nome"),
        F.col("MC").alias("unidade_cod"),
        F.col("MN").alias("unidade_nome"),
        F.col("V").alias("valor_txt"),
        F.col("D1C").alias("territorio_cod"),
        F.col("D1N").alias("territorio_nome"),
        F.col("D2C").alias("variavel_cod"),
        F.col("D2N").alias("variavel_nome"),
        F.col("D3C").alias("periodo_cod"),
        F.col("D3N").alias("periodo_nome"),
    )
