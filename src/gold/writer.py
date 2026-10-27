"""Gravação opcional das tabelas em Parquet."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from pyspark.sql import DataFrame


def write_parquet(tables: dict[str, DataFrame], out_dir: Path) -> None:
    """Grava Parquet em <out_dir>/<tabela>/. mode=overwrite SUBSTITUI apenas a
    pasta de cada tabela gerada aqui; nada mais em out_dir é tocado."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        if name.startswith("_"):
            continue
        output_dir = out_dir / name
        with tempfile.TemporaryDirectory(prefix=f"{name}_") as temporary_dir:
            temporary_output = Path(temporary_dir) / name
            df.write.mode("overwrite").parquet(temporary_output.as_posix())

            with tempfile.TemporaryDirectory(prefix=f".{name}_", dir=out_dir) as staging_dir:
                staging_root = Path(staging_dir)
                staged_output = staging_root / name
                staged_output.mkdir()

                for source in temporary_output.rglob("*"):
                    destination = staged_output / source.relative_to(temporary_output)
                    if source.is_dir():
                        destination.mkdir(parents=True, exist_ok=True)
                    elif source.is_file():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, destination)

                backup_dir = staging_root / f"{name}_backup"
                if output_dir.exists():
                    output_dir.replace(backup_dir)
                try:
                    staged_output.replace(output_dir)
                except Exception:
                    if backup_dir.exists() and not output_dir.exists():
                        backup_dir.replace(output_dir)
                    raise

                if backup_dir.exists():
                    shutil.rmtree(backup_dir)

        print(f"  gravado: {output_dir}")
