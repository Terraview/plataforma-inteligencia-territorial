from bronze.url_builder import construir_url
from bronze.extract import extrair_dados


def execut_populacao():

    url = (
        "http://apisidra.ibge.gov.br/values"
        "/t/6579"
        "/n3/all"
        "/v/9324"
        "/p/2019-2021"
    )

    dados = extrair_dados(
        url=url,
        pasta_destino="ibge",
        nome_arquivo="populacao_2019_2021.json"
    )

    print(type(dados))
    print(len(dados))

    