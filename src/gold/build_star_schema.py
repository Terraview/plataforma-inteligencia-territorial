#!/usr/bin/env python3
"""
src/gold/build_star_schema.py  (ponto de entrada / CLI)
=======================================================
Constrói e valida o esquema estrela (Gold) a partir dos JSON do CAGED e do IBGE.
A lógica está nos módulos vizinhos (paths, readers, dimensions, facts, pipeline,
validation, writer); este arquivo só lê os argumentos e chama o pipeline.

Execução (SEMPRE a partir da raiz do projeto, com a venv do Spark ativa):
    python -m src.gold.build_star_schema --show     # constrói, mostra schemas e amostras, valida
    python -m src.gold.build_star_schema --write    # também grava Parquet em Data_gold/

Argumentos de caminho (relativos à raiz do projeto, ou absolutos):
    --root       raiz do projeto (padrão: env PROJECT_ROOT ou duas pastas acima de src/gold)
    --caged-dir  padrão "Caged_json"
    --ibge-dir   padrão "ibge"
    --out-dir    padrão "Data_gold"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .paths import resolve_inputs
from .pipeline import build_star_schema
from .readers import get_spark
from .validation import validate_star_schema
from .writer import write_parquet

# <raiz>/src/gold/build_star_schema.py -> parents[0]=gold, [1]=src, [2]=<raiz>
PROJECT_ROOT_DEFAULT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    default_root = os.environ.get("PROJECT_ROOT") or PROJECT_ROOT_DEFAULT
    ap.add_argument("--root", default=str(default_root))
    ap.add_argument("--caged-dir", default="Caged_json")
    ap.add_argument("--ibge-dir", default="ibge")
    ap.add_argument("--out-dir", default="Data_gold")
    ap.add_argument("--write", action="store_true", help="grava Parquet em --out-dir (sobrescreve as pastas das tabelas)")
    ap.add_argument("--show", action="store_true", help="mostra 5 linhas de cada tabela")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    paths = resolve_inputs(root, args.caged_dir, args.ibge_dir)
    print("Arquivos de entrada:")
    for k, v in paths.items():
        print(f"  {k}: {v}")

    spark = get_spark()
    try:
        tables = build_star_schema(spark, paths)

        print("\nEstrutura das tabelas do modelo:")
        for name, df in tables.items():
            if name.startswith("_"):
                continue
            print(f"\n== {name} ==")
            df.printSchema()
            if args.show:
                df.show(5, truncate=False)

        print("\nValidações:")
        results = validate_star_schema(tables)
        for name, ok, detail in results:
            print(f"  [{'OK' if ok else 'FALHA'}] {name}" + (f"  ({detail})" if detail else ""))
        falhas = [r for r in results if not r[1]]

        if falhas:
            print(f"\n{len(falhas)} validação(ões) falharam. Gravação NÃO realizada.")
            return 1
        if args.write:
            out_dir = Path(args.out_dir)
            out_dir = out_dir if out_dir.is_absolute() else root / out_dir
            print(f"\nGravando Parquet em {out_dir} ...")
            write_parquet(tables, out_dir)
        print("\nConcluído.")
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
