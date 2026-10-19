from bronze.ibge_ipca import execut_ipca
from bronze.ibge_pib import execut_pib
from bronze.ibge_population import execut_populacao
from bronze.caged import download_caged_ftp


if __name__ == "__main__":
    execut_ipca()
    execut_pib()
    execut_populacao()
    download_caged_ftp()
        