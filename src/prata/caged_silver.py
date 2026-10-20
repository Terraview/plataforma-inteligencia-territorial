from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
from column_normalizer import normalizar_colunas
from cbo_ti import CBO_TI

# CRIA SESSÃO SPARK
spark = (
    SparkSession.builder
    .appName("silver-caged")
    .getOrCreate()
)

# leitura dos arquivos processados da bronze
df = spark.read.csv(
    "caged/extracted/*.txt",
    sep=";",
    header=True,
    encoding='ISO-8859-1'
)

# NORMALIZA O NOME DAS COLUNAS
df = normalizar_colunas(df)
print(df.columns) #pra conferir se as colunas foram normalizadas corretamente

# filtra apenas profissionais de TI
df = df.filter(
    col("cbo_2002_ocupacao")
    .cast("int")
    .isin(CBO_TI)
)

# seleciona apenas colunas relevantes
df = df.select(
    "competencia_declarada",
    "ano_declarado",
    "municipio",
    "uf",
    "cbo_2002_ocupacao",
    "sexo",
    "idade",
    "grau_instrucao",
    "salario_mensal",
    "admitidos_desligados"
)

# RENOMEIA PARA O PADRÃO FINAL DA SILVER
df = (
    df.withColumnRenamed(
        "competencia_declarada",
        "competencia_declarada"
    )
    .withColumnRenamed(
        "ano_declarado",
        "ano"
    )
    .withColumnRenamed(
        "municipio",
        "municipio"
    )
    .withColumnRenamed(
        "cbo_2002_ocupacao",
        "cbo"
    )
    .withColumnRenamed(
        "grau_instrucao",
        "grau_instrucao"
    )
    .withColumnRenamed(
        "salario_mensal",
        "salario_mensal"
    )
)


# cria classificação do período
df = df.withColumn(
    "periodo",
    when(
        col("ano") == "2019",
        "pre_pandemia"
    )
    .when(
        col("ano").isin(
            "2020",
            "2021"
        ),
        "pandemia"
    )
    .otherwise(
        "pos_pandemia"
    )
)

# salva silver
df.write.mode("overwrite").parquet(
    "silver/caged_ti"
)