"""Tabelas dimensionais do esquema estrela."""
from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .config import ANOS, REGIOES_ALVO


def _regiao_expr(cod_uf: str):
    """Região a partir do 1º dígito do código oficial da UF (convenção IBGE)."""
    d = F.substring(F.col(cod_uf).cast("string"), 1, 1)
    return (
        F.when(d == "1", "Norte").when(d == "2", "Nordeste")
        .when(d == "3", "Sudeste").when(d == "4", "Sul")
        .when(d == "5", "Centro-Oeste")
    )


def _periodo_analise_expr(ano_col: str):
    """Rótulo descritivo definido no escopo do projeto. NÃO implica causalidade."""
    a = F.col(ano_col)
    return F.when(a == 2019, "pre_pandemia").when(a.isin(2020, 2021), "pandemia").otherwise("pos_pandemia")


def build_dim_uf(pop_raw: DataFrame, pib_raw: DataFrame) -> DataFrame:
    """Grão: 1 linha por UF das regiões-alvo. PK: cod_uf."""
    nomes = pop_raw.select(
        F.col("territorio_cod").cast("int").alias("cod_uf"),
        F.col("territorio_nome").alias("nome_uf"),
    ).distinct()
    siglas = pib_raw.select(
        F.substring("territorio_cod", 1, 2).cast("int").alias("cod_uf"),
        F.regexp_extract("territorio_nome", r"^.* - ([A-Z]{2})$", 1).alias("sigla_uf"),
    ).distinct()
    return (
        nomes.join(siglas, "cod_uf", "inner")
        .withColumn("regiao", _regiao_expr("cod_uf"))
        .filter(F.col("regiao").isin(*REGIOES_ALVO))
        .select("cod_uf", "sigla_uf", "nome_uf", "regiao")
    )


def build_dim_municipio(pib_raw: DataFrame, dim_uf: DataFrame) -> DataFrame:
    """Grão: 1 linha por município das UFs-alvo. PK: cod_municipio (7 dígitos).
    `cod_municipio_6` (sem dígito verificador) é a ponte para o CAGED."""
    base = pib_raw.select(
        F.col("territorio_cod").cast("int").alias("cod_municipio"),
        F.substring("territorio_cod", 1, 6).cast("int").alias("cod_municipio_6"),
        F.regexp_extract("territorio_nome", r"^(.*) - [A-Z]{2}$", 1).alias("nome_municipio"),
        F.substring("territorio_cod", 1, 2).cast("int").alias("cod_uf"),
    ).distinct()
    return base.join(dim_uf, "cod_uf", "inner").select(
        "cod_municipio", "cod_municipio_6", "nome_municipio",
        "cod_uf", "sigla_uf", "nome_uf", "regiao",
    )


def build_dim_ano(spark: SparkSession) -> DataFrame:
    schema = T.StructType([T.StructField("ano", T.IntegerType(), False)])
    return (
        spark.createDataFrame([(a,) for a in ANOS], schema)
        .withColumn("periodo_analise", _periodo_analise_expr("ano"))
    )


def build_dim_tempo(spark: SparkSession) -> DataFrame:
    """Grão: 1 linha por mês. PK: competencia (AAAAMM, int)."""
    rows = [(a * 100 + m, a, m, (m - 1) // 3 + 1) for a in ANOS for m in range(1, 13)]
    schema = T.StructType([
        T.StructField("competencia", T.IntegerType(), False),
        T.StructField("ano", T.IntegerType(), False),
        T.StructField("mes", T.IntegerType(), False),
        T.StructField("trimestre", T.IntegerType(), False),
    ])
    return spark.createDataFrame(rows, schema)


def build_dim_cbo(caged_raw: DataFrame) -> DataFrame:
    """Grão: 1 linha por código CBO presente no CAGED. PK: cod_cbo.
    Descrição e classificação de TI NÃO existem nos arquivos -> não são criadas."""
    return (
        caged_raw.select(F.col("cbo").alias("cod_cbo"))
        .filter(F.col("cod_cbo").isNotNull() & (F.length("cod_cbo") > 0))
        .distinct()
    )
