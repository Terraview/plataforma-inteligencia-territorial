"""Tabelas fato do esquema estrela (uma por fonte/granularidade)."""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T


def build_fato_caged(caged_raw: DataFrame, dim_uf: DataFrame, dim_municipio: DataFrame) -> DataFrame:
    """Grão: 1 linha por registro do arquivo de origem (restrito às UFs-alvo).
    Não há chave natural -> sem PK (atribuir uma BIGSERIAL na carga do PostgreSQL).
    Registros idênticos são preservados."""
    ponte = dim_municipio.select("cod_municipio", "cod_municipio_6")

    f = (
        caged_raw
        .withColumn("cod_uf", F.col("uf").cast("int"))
        .join(F.broadcast(dim_uf.select("cod_uf")), "cod_uf", "left_semi")  # filtra CO + Sul
        .withColumn("cod_municipio_6", F.col("municipio").cast("int"))
        .join(F.broadcast(ponte), "cod_municipio_6", "left")                # N:1, sem multiplicar
    )

    # Salário: com vírgula -> vírgula é o separador decimal ("004441,00");
    # sem vírgula -> ponto é o separador decimal ("12697.64", observado a partir
    # de 2023-09). Casas decimais excedentes são arredondadas pelo cast.
    s = F.col("salario")
    s_norm = F.when(s.contains(","), F.regexp_replace(s, ",", ".")).otherwise(s)
    salario = F.when(
        s_norm.rlike(r"^(\d+(\.\d*)?|\.\d+)$"), s_norm.cast(T.DecimalType(12, 2))
    )

    competencia = F.col("competencia").cast("int")
    return f.select(
        competencia.alias("competencia"),                       # FK dim_tempo
        F.col("cod_municipio").alias("cod_municipio"),          # FK dim_municipio
        F.col("cbo").alias("cod_cbo"),                          # FK dim_cbo
        # Hipótese derivada: os códigos categóricos de 2019 e de 2020+ seguem
        # dicionários distintos. Este campo evita misturá-los acidentalmente.
        F.when(competencia < 202001, "legado_2019").otherwise("novo_2020_mais").alias("layout_codigos"),
        F.col("movimento").alias("movimento_cod"),              # CRU (sem dicionário)
        F.col("sexo").alias("sexo_cod"),                        # CRU
        F.col("escolaridade").alias("escolaridade_cod"),        # CRU
        F.col("idade").cast("int").alias("idade"),
        salario.alias("salario_nominal"),                       # nominal, sem deflação
    )


def build_fato_pib(pib_raw: DataFrame, dim_municipio: DataFrame) -> DataFrame:
    """Grão: município x ano. PK: (cod_municipio, ano). Mil reais, preços correntes."""
    return (
        pib_raw
        .select(
            F.col("territorio_cod").cast("int").alias("cod_municipio"),
            F.col("periodo_cod").cast("int").alias("ano"),
            F.col("valor_txt").cast(T.DecimalType(20, 2)).alias("pib_correntes_mil_reais"),
        )
        .join(F.broadcast(dim_municipio.select("cod_municipio")), "cod_municipio", "left_semi")
    )


def build_fato_populacao_uf(pop_raw: DataFrame, dim_uf: DataFrame) -> DataFrame:
    """Grão: UF x ano (fonte só tem UF, 2019-2021). PK: (cod_uf, ano)."""
    return (
        pop_raw
        .select(
            F.col("territorio_cod").cast("int").alias("cod_uf"),
            F.col("periodo_cod").cast("int").alias("ano"),
            F.col("valor_txt").cast("long").alias("populacao_estimada"),
        )
        .join(F.broadcast(dim_uf.select("cod_uf")), "cod_uf", "left_semi")
    )


def build_fato_ipca_mensal(ipca_raw: DataFrame) -> DataFrame:
    """Grão: mês, Brasil (fonte nacional). PK: competencia. Variação mensal em %."""
    return ipca_raw.select(
        F.col("periodo_cod").cast("int").alias("competencia"),
        F.col("valor_txt").cast(T.DecimalType(8, 2)).alias("ipca_variacao_mensal_pct"),
    )
