import py7zr
from pathlib import Path

# FUNÇÃO PARA CONVERSÃO DOS DADOS CAGED
# QUE ESTÃO EM FORMATO 7Z PARA TXT

def extract_7z():

    origin_path = Path("caged")
    destination_path = Path("Data_Bronze/Caged_extracted/")

    destination_path.mkdir(
        parents=True,
        exist_ok=True
    )

    files = origin_path.glob("*.7z")

    for file_7z in files:

        try:
            print(f"Extraindo {file_7z.name}...")

            with py7zr.SevenZipFile(

                file_7z,
                mode="r"

            ) as file:
                file.extractall(path=destination_path)

            print(f"{file_7z.name} OK.")

        except Exception as erro:

            print(f"Erro ao extrair {file_7z.name}: {erro}")

extract_7z()            