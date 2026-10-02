import json
import requests
from pathlib import Path
from error_handling import (
status_handling,
exception_handling
)


def extrair_dados(url, pasta_destino, nome_arquivo):

    try:

        response = requests.get(
        url,
        timeout=30
)

        if not status_handling(response):
            return None

        dados = response.json()

        Path(pasta_destino).mkdir(
            parents=True,
            exist_ok=True
        )

        caminho = (
            Path(pasta_destino)
            / nome_arquivo
        )

        with open(
            caminho,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

        print(f"✅ Arquivo salvo em: {caminho}")

        return dados

    except Exception as erro:
        exception_handling(erro)
        return None