from bronze.extract import extrair_dados

def execut_pib():
   
    url = (
    "http://apisidra.ibge.gov.br/values"
    "/t/5938"
    "/n6/all"
    "/v/37"
    "/p/2019-2023"
)
    print(url)
    
    extrair_dados(
    
        url=url,
        pasta_destino="ibge",
        nome_arquivo="pib_municipal_2019_2023.json"
    )

if __name__ == "__main__":
    execut_pib()