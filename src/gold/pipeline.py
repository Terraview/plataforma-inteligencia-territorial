"""Orquestração em memória: lê os brutos e monta todas as tabelas do modelo."""
from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession

from .dimensions import (build_dim_ano, build_dim_cbo, build_dim_municipio,
                         build_dim_tempo, build_dim_uf)
from .facts import (build_fato_caged, build_fato_ipca_mensal, build_fato_pib,
                    build_fato_populacao_uf)
from .readers import read_caged_raw, read_sidra_raw


def build_star_schema(spark: SparkSession, paths: dict) -> dict[str, DataFrame]:
    caged_raw = read_caged_raw(spark, paths["caged"])
    pop_raw = read_sidra_raw(spark, paths["populacao"])
    pib_raw = read_sidra_raw(spark, paths["pib"])
    ipca_raw = read_sidra_raw(spark, paths["ipca"])

    dim_uf = build_dim_uf(pop_raw, pib_raw)
    dim_municipio = build_dim_municipio(pib_raw, dim_uf)
    tables = {
        "dim_uf": dim_uf,
        "dim_municipio": dim_municipio,
        "dim_ano": build_dim_ano(spark),
        "dim_tempo": build_dim_tempo(spark),
        "dim_cbo": build_dim_cbo(caged_raw),
        "fato_caged": build_fato_caged(caged_raw, dim_uf, dim_municipio),
        "fato_pib": build_fato_pib(pib_raw, dim_municipio),
        "fato_populacao_uf": build_fato_populacao_uf(pop_raw, dim_uf),
        "fato_ipca_mensal": build_fato_ipca_mensal(ipca_raw),
    }
    # Brutos (para conferência de contagens); não fazem parte do modelo.
    tables["_raw_caged"] = caged_raw
    tables["_raw_pib"] = pib_raw
    tables["_raw_populacao"] = pop_raw
    tables["_raw_ipca"] = ipca_raw
    return tables
