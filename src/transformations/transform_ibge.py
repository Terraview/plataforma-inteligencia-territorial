import json
import pandas as pd
from pathlib import Path


def processar_ibge():
    pasta_bronze = Path("data/bronze/ibge")
    pasta_silver = Path("data/silver/ibge")

    pasta_silver.mkdir(parents=True, exist_ok=True)

    arquivos_json = list(pasta_bronze.glob("*.json"))

    if not arquivos_json:
        print("Nenhum arquivo JSON do IBGE encontrado em data/bronze/ibge/")
        return

    for arquivo in arquivos_json:
        print(f"Processando IBGE: {arquivo.name}...")

        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            df = pd.DataFrame(dados)

            nome_parquet = arquivo.stem + ".parquet"
            caminho_parquet = pasta_silver / nome_parquet

            df.to_parquet(caminho_parquet, index=False)

            print(f"Salvo na Prata em: {caminho_parquet}")

        except Exception as erro:
            print(f"Erro ao processar {arquivo.name}: {erro}")


if __name__ == "__main__":
    processar_ibge()