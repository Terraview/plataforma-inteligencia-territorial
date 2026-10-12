from url_builder import construir_url
from extract import extrair_dados

url = (
    "http://apisidra.ibge.gov.br/values"
    "/t/6579"
    "/n3/all"
    "/v/9324"
    "/p/2019-2021"
)

dados = extrair_dados(
    url=url,
    pasta_destino="data/bronze/ibge",
    nome_arquivo="populacao_2019_2021.json"
)

print(type(dados))
print(len(dados))

    