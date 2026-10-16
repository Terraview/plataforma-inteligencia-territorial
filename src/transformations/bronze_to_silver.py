from transform_ibge import processar_ibge
from transform_caged import processar_caged


def executar_pipeline_prata():
    print("Executando Pipeline da Camada Prata...")
    processar_ibge()
    processar_caged()
    print("Camada Prata gerada com sucesso!")


if __name__ == "__main__":
    executar_pipeline_prata()