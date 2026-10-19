from ftplib import FTP
from pathlib import Path
from bronze.caged_mapper import build_path_caged, gerar_competencias



def download_caged_ftp():
    parta_destino = "caged"

    Path(parta_destino).mkdir(
        parents=True,
        exist_ok=True
    )

    ftp = FTP('ftp.mtps.gov.br')
    ftp.login()

    for competencia in gerar_competencias():
        caminho_remoto = build_path_caged(competencia)
        nome_arquivo = caminho_remoto.split("/")[-1]
        caminho_local = Path(parta_destino) / nome_arquivo

        try:
            with open(caminho_local, 'wb') as arquivo:
                ftp.retrbinary(
                    f"RETR /pdet/microdados/{caminho_remoto}",
                    arquivo.write
                )
            print(f'Arquivo {nome_arquivo} baixado com sucesso em {parta_destino}.')

        except Exception as e:
            print(f'Erro ao baixar o arquivo {nome_arquivo}: {e}')

    ftp.quit()
