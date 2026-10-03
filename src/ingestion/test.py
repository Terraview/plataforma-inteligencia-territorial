from url_builder import construir_url
from extract import extrair_dados
from extract import extrair_caged_ftp


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
        pasta_destino="data/bronze/ibge",
        nome_arquivo="ipca_2022.json"
)

# 2. Ingestão do CAGED (Baixa o ano de 2022 inteiro via FTP)
print("🚀 Extraindo pasta do CAGED (2022)...")

extrair_caged_ftp(
    pasta_servidor="pdet/microdados/NOVO CAGED",
    pasta_destino="data/bronze/caged",
    ano="2022"
)

if __name__ == "__main__":
    executar()

