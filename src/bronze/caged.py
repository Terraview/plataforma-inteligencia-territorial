from ftplib import FTP
from pathlib import Path
import tempfile

from src.bronze.caged_mapper import build_path_caged, gerar_competencias


def download_caged_ftp():
    parta_destino = "caged"
    competencias = gerar_competencias()
    destino = Path(parta_destino)

    destino.mkdir(parents=True, exist_ok=True)

    with FTP("ftp.mtps.gov.br") as ftp:
        ftp.login()
        for competencia in competencias:
            caminho_remoto = build_path_caged(competencia)
            arquivo_local = destino / caminho_remoto.split("/")[-1]
            nome_arquivo = arquivo_local.name
            with tempfile.NamedTemporaryFile(
                dir=destino,
                prefix=f".{nome_arquivo}.",
                suffix=".part",
                delete=False,
            ) as arquivo_temporario:
                caminho_temporario = Path(arquivo_temporario.name)

            try:
                with caminho_temporario.open("wb") as arquivo:
                    ftp.retrbinary(
                        f"RETR /pdet/microdados/{caminho_remoto}",
                        arquivo.write,
                    )

                caminho_temporario.replace(arquivo_local)
                print(f"Arquivo {nome_arquivo} baixado e substituído em {destino}.")
            except Exception as error:
                caminho_temporario.unlink(missing_ok=True)
                print(f"Erro ao baixar {nome_arquivo}: {error}")
                raise