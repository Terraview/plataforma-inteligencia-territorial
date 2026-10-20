from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("silver-ipca")
    .getOrCreate()
)

df = spark.read.json(
    "ibge/ipca_2019_2023.json"
)

df = df.select(
    "D3C",
    "D3N",
    "V"
)

df = (
    df.withColumnRenamed(
        "D3C",
        "ano"
    )
    .withColumnRenamed(
        "D3N",
        "mes"
    )
    .withColumnRenamed(
        "V",
        "ipca"
    )
)

df.write.mode(
    "overwrite"
).parquet(
    "silver/ipca"
)