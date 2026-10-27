import os
from dotenv import load_dotenv
load_dotenv()

from src.bronze.extract import extrair_dados

SINDRA_PIB_URL=os.getenv("SINDRA_PIB_URL")

def execut_pib():
   
    url = SINDRA_PIB_URL
    
    
    extrair_dados(
    
        url=url,
        pasta_destino="ibge",
        nome_arquivo="pib_municipal_2019_2023.json"
    )

if __name__ == "__main__":
    execut_pib()