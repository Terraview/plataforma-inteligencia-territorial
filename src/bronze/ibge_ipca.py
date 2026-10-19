from bronze.url_builder import construir_url
from bronze.extract import extrair_dados



def execut_ipca():

    url = construir_url(
        tabela="1737",
        nivel="n1",
        localidade="all",
        variavel="63",
        periodo="201901 - 202312"
    )

    extrair_dados(
        url=url,
        pasta_destino="ibge",
        nome_arquivo="ipca_2019_2023.json"
)

if __name__ == "__main__":
    execut_ipca()

