from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("silver-pib")
    .getOrCreate()
)

# leitura do json da bronze
df = spark.read.json(
    "ibge/pib_municipal_2019_2023.json"
)

# manter apenas dados úteis
df = df.select(
    "Municipio",
    "Ano",
    "Valor"
)

# renomear colunas
df = (
    df.withColumnRenamed(
        "Municipio",
        "municipio"
    )
    .withColumnRenamed(
        "Ano",
        "ano"
    )
    .withColumnRenamed(
        "Valor",
        "pib"
    )
)

df.write.mode(
    "overwrite"
).parquet(
    "silver/pib"
)