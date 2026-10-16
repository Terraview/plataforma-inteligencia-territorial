import py7zr
import pandas as pd
from pathlib import Path


def processar_caged():
    pasta_bronze = Path("data/bronze/caged")
    pasta_silver = Path("data/silver/caged")
    pasta_silver.mkdir(parents=True, exist_ok=True)

    # 1. Localiza os arquivos .7z baixados
    arquivos_7z = list(pasta_bronze.glob("*.7z"))

    if not arquivos_7z:
        print("Nenhum arquivo .7z do CAGED encontrado em data/bronze/caged/")
        return

    # 2. Descompacta cada arquivo .7z na pasta bronze
    for arquivo_7z in arquivos_7z:
        print(f"Descompactando {arquivo_7z.name}...")

        try:
            with py7zr.SevenZipFile(arquivo_7z, mode='r') as archive:
                archive.extractall(path=pasta_bronze)
        except Exception as erro:
            print(f"Erro ao descompactar {arquivo_7z.name}: {erro}")

    # 3. Lê os arquivos descompactados (.txt ou .csv)
    arquivos_texto = list(pasta_bronze.glob("*.txt")) + list(pasta_bronze.glob("*.csv"))
    dfs = []

    for arquivo in arquivos_texto:
        print(f"Processando CSV do CAGED: {arquivo.name}...")

        try:
            df = pd.read_csv(arquivo, sep=";", dtype=str)

            colunas_chaves = [
                "competênciamov",
                "região",
                "uf",
                "município",
                "seção",
                "subclasse",
                "saldomovimentação",
                "cbo2002ocupação",
                "graudeinstrução",
                "idade",
                "sexo",
                "salário"
            ]

            cols_existentes = [c for c in colunas_chaves if c in df.columns]
            df = df[cols_existentes]
            dfs.append(df)

        except Exception as erro:
            print(f"Erro ao ler {arquivo.name}: {erro}")

    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)

        if "saldomovimentação" in df_final.columns:
            df_final["saldomovimentação"] = pd.to_numeric(
                df_final["saldomovimentação"],
                errors="coerce"
            )

        caminho_parquet = pasta_silver / "caged_2022.parquet"
        df_final.to_parquet(caminho_parquet, index=False)

        print(f"CAGED consolidado e salvo em: {caminho_parquet}")


if __name__ == "__main__":
    processar_caged()