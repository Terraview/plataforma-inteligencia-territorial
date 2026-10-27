import shutil
import tempfile
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from column_normalizer import normalizar_colunas
from cbo_ti import CBO_TI


def main():
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

    root_dir = Path(__file__).resolve().parents[2]
    output_dir = root_dir / "Data_Silver" / "caged_2020_2023"
    with tempfile.TemporaryDirectory(prefix="caged_2020_2023_") as temporary_dir:
        temporary_output = Path(temporary_dir) / "caged_2020_2023"
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

    print(df.count())

    df.show(
        10,
        truncate=False
    )

    df.printSchema()
if __name__ == "__main__":
    main()    