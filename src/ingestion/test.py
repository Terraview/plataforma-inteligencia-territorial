from url_builder import construir_url
from extract import extrair_dados


def executar():

    url = construir_url(
        tabela="7060",
        nivel="n1",
        localidade="all",
        variavel="63",
        periodo="202201 - 202212"
    )

    extrair_dados(
        url=url,
        pasta_destino="data/bronze",
        nome_arquivo="ipca_2022.json"
)


if __name__ == "__main__":
    executar()

