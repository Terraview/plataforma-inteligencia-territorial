import shutil
import tempfile
from pathlib import Path

from pyspark.sql import SparkSession
from src.prata.column_normalizer import normalizar_colunas
from pyspark.sql.functions import col
from src.prata.cbo_ti import CBO_TI
from pyspark.sql.functions import lit


def main():
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

    root_dir = Path(__file__).resolve().parents[2]
    output_dir = root_dir / "Data_Silver" / "caged_2019"
    with tempfile.TemporaryDirectory(prefix="caged_2019_") as temporary_dir:
        temporary_output = Path(temporary_dir) / "caged_2019"
        df.write.mode("overwrite").parquet(str(temporary_output))

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for parquet_file in temporary_output.rglob("*"):
            relative_path = parquet_file.relative_to(temporary_output)
            destination = output_dir / relative_path
            if parquet_file.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            elif parquet_file.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(parquet_file, destination)

    print("Número de linhas salvas:", df.count())
    df.show(10, truncate=False)
    df.printSchema()

if __name__ == "__main__":
    main()