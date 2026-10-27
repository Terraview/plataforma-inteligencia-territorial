from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from column_normalizer import normalizar_colunas
from cbo_ti import CBO_TI

spark = (
    SparkSession.builder
    .appName("silver_caged_2020_2023" )
    .getOrCreate()
)

df = spark.read.csv(
    "Data_Bronze/Caged_extracted/CAGEDMOV*.txt",
    sep=";",
    header=True,
    encoding="utf-8"
)

df = normalizar_colunas(df)

df = (
    df.withColumnRenamed(
        "competenciadec",
        "competencia"
    )
    
    .withColumnRenamed(
    "cbo2002ocupacao",
    "cbo"
)

    .withColumnRenamed(
        "graudeinstrucao",
        "escolaridade"
    )

    .withColumnRenamed(
        "tipomovimentacao",
        "movimento"
    )

)


df = df.select(
    "competencia",
    "municipio",
    "uf",
    "cbo",
    "sexo",
    "idade",
    "escolaridade",
    "salario",
    "movimento"
)

df = df.filter(
    col("cbo")
    .cast("int")
    .isin(CBO_TI)
)

# print(
#     "Total registros TI:",    (total de 1.661.864)
#     df.count()
# )
df.show(
    10,
    truncate=False
)

df.printSchema()