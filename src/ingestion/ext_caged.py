from extract import extrair_caged_ftp, extrair_dados
from url_builder import construir_url


# =========================================================
#  CONFIGURAÇÕES (Altere aqui quando quiser)
# =========================================================
ANOS = ["2022"]

# Exemplo futuro com mais anos: ["2019", "2020", "2021", "2022", "2023"]
MESES = ["202201"]  # Mude para None quando quiser baixar todos os 12 meses do ano


# =========================================================
#  FUNÇÃO PRINCIPAL DE INGESTÃO
# =========================================================
def executar_ingestao():
    print(f" Iniciando extração do CAGED para os anos: {ANOS}...")

    for ano in ANOS:
        extrair_caged_ftp(
            pasta_servidor="pdet/microdados/NOVO CAGED",
            pasta_destino="data/bronze/caged",
            ano=ano,
            meses_filtro=MESES,
        )

    print(" Ingestão concluída com sucesso!")


if __name__ == "__main__":
    executar_ingestao()
