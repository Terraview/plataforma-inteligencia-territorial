# from pyspark.sql import SparkSession

# spark = (
#     SparkSession.builder
#     .appName("teste-caged")
#     .getOrCreate()
# )

# df = spark.read.csv(
#     "ibge/ipca_municipal_2019_2023.json",
#     sep=";",
#     header=True,
#     encoding="latin1"
# )

# df.printSchema()

# df. select(
#      "Competência Declarada",
#     "Ano Declarado",
#     "Município",
#     "CBO 2002 Ocupação",
#     "Grau Instrução",
#     "Idade",
#     "Salário Mensal",
#     "Sexo",
#     "UF"
# ).show(5, truncate=False)

