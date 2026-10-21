import os
from dotenv import load_dotenv
load_dotenv()

from bronze.url_builder import construir_url
from bronze.extract import extrair_dados

SIDRA_POPULATION = os.getenv("SIDRA_POPULATION")

def execut_populacao():

    url = SIDRA_POPULATION

    dados = extrair_dados(
        url=url,
        pasta_destino="ibge",
        nome_arquivo="populacao_2019_2021.json"
    )

    print(type(dados))
    print(len(dados))

    