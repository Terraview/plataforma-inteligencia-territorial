from pyspark.sql import SparkSession
from column_normalizer import normalizar_colunas
from pyspark.sql.functions import col
from cbo_ti import CBO_TI
from pyspark.sql.functions import lit

spark = (
    SparkSession.builder
    .appName("silver-caged-2019")
    .getOrCreate()
)

df = spark.read.csv(
    "Data_Bronze/Caged_extracted/CAGEDEST_*.txt",
    sep=";",
    header=True,
    encoding="latin1"
)

df = normalizar_colunas(df)

# trocando os nomes das colunas para o padrão do projeto
df = (
    df.withColumnRenamed(
        "competencia_declarada",
        "competencia"
    )
    .withColumnRenamed(
        "ano_declarado",
        "ano"
    )
    .withColumnRenamed(
        "cbo_2002_ocupacao",
        "cbo"
    )
    .withColumnRenamed(
        "grau_instrucao",
        "escolaridade"
    )
    .withColumnRenamed(
        "salario_mensal",
        "salario"
    )
    .withColumnRenamed(
        "admitidos_desligados",
        "movimento"
    )
)


#utilizando a lista contida em cbo_ti.py para filtrar os registros do dataframe
df = df.filter(
    col("cbo")
    .cast("int")
    .isin(CBO_TI)
)
print("Número de registros após o filtro: ", df.count())

#Incluindo uma coluna com o período de pandemia para facilitar a análise dos dados
df = df.withColumn(
    "periodo",
    lit("pre_pandemia") 
)
#mostra o dataframe final com as colunas de ano e período
# df.select(
#     "ano",
#     "periodo"
# ).show(truncate=False)

df = df.select(
    "competencia",
    "ano",
    "municipio",
    "uf",
    "cbo",
    "sexo",
    "idade",
    "escolaridade",
    "salario",
    "movimento",
    "periodo"
)

# Salva o dataframe em formato parquet na pasta silver/caged_2019, sobrescrevendo caso já exista
df.write.mode(
    "overwrite"
).parquet(
    "Data_Silver/caged_2019"
)
# mostra quantas linhas foram salvas no dataframe final
print(df.count())

# mostra as primeiras 10 linhas do dataframe final
df.show(
    10,
    truncate=False
)

df.printSchema()