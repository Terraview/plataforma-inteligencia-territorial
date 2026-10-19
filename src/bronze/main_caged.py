from caged_path_builder import build_path_caged, gerar_competencias
from caged import download_caged_ftp

competencias = [
    "201901",
    "202001"
]

for competencia in competencias:

    caminho = build_path_caged(
        competencia
    )

    nome_arquivo = caminho.split("/")[-1]

    download_caged_ftp(
        caminho_remoto=caminho,
        pasta_destino="data/bronze/caged",
        nome_arquivo=nome_arquivo
    )