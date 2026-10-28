from src.bronze.ibge_ipca import execut_ipca
from src.bronze.ibge_pib import execut_pib
from src.bronze.ibge_population import execut_populacao
from src.bronze.caged import download_caged_ftp


if __name__ == "__main__":
    execut_ipca()
    execut_pib()
    execut_populacao()
    download_caged_ftp()
        

        