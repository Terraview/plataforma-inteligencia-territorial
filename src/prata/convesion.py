import shutil
import tempfile
from pathlib import Path

import py7zr

# FUNÇÃO PARA CONVERSÃO DOS DADOS CAGED
# QUE ESTÃO EM FORMATO 7Z PARA TXT

def extract_7z():
    # Encontra a raiz do projeto dinamicamente (subindo 2 níveis a partir de src/prata/convesion.py)
    base_dir = Path(__file__).resolve().parents[2]
    
    # Define caminhos possíveis (local no WSL vs container Docker do Airflow)
    local_path = base_dir / "caged"
    docker_path = Path("/opt/airflow/caged")

    # Escolhe automaticamente o caminho que existe no ambiente atual
    if local_path.exists():
        origin_path = local_path
    elif docker_path.exists():
        origin_path = docker_path
    else:
        origin_path = local_path  # Fallback padrão

    destination_path = base_dir / "Data_Bronze" / "Caged_extracted"

    destination_path.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"Procurando ficheiros .7z em: {origin_path.absolute()}")
    files = list(origin_path.glob("*.7z"))
    
    if not files:
        raise FileNotFoundError(f"Nenhum ficheiro .7z encontrado em {origin_path.absolute()}")

    for file_7z in files:
        try:
            print(f"Extraindo {file_7z.name}...")
            with tempfile.TemporaryDirectory(prefix="caged_extract_") as temporary_dir:
                temporary_path = Path(temporary_dir)
                with py7zr.SevenZipFile(file_7z, mode="r") as archive:
                    archive.extractall(path=temporary_path)

                for extracted_path in temporary_path.rglob("*"):
                    relative_path = extracted_path.relative_to(temporary_path)
                    output_path = destination_path / relative_path
                    if extracted_path.is_dir():
                        output_path.mkdir(parents=True, exist_ok=True)
                    elif extracted_path.is_file():
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(extracted_path, output_path)
            print(f"{file_7z.name} OK.")
        except Exception as erro:
            print(f"Erro ao extrair {file_7z.name}: {erro}")
            raise  # Propaga o erro para o Airflow capturar a falha corretamente

if __name__ == "__main__":
    extract_7z()