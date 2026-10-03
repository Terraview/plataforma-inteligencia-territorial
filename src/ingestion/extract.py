import json
import requests
from ftplib import FTP
from pathlib import Path
from error_handling import (
status_handling,
exception_handling
)


def extrair_dados(url, pasta_destino, nome_arquivo):

    try:

        response = requests.get(
        url,
        timeout=30
)

        if not status_handling(response):
            return None

        dados = response.json()

        Path(pasta_destino).mkdir(
            parents=True,
            exist_ok=True
        )

        caminho = (
            Path(pasta_destino)
            / nome_arquivo
        )

        with open(
            caminho,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

        print(f"✅ Arquivo salvo em: {caminho}")

        return dados

    except Exception as erro:
        exception_handling(erro)
        return None



# 2. FUNÇÃO DO CAGED (Acessa as subpastas 202201 até 202212)

def extrair_caged_ftp(pasta_servidor="pdet/microdados/NOVO CAGED", pasta_destino="data/bronze/caged", ano="2022"):
    try:
        Path(pasta_destino).mkdir(parents=True, exist_ok=True)
        print("🔌 Conectando ao servidor FTP do MTE (ftp.mtps.gov.br)...")
        
        ftp = FTP("ftp.mtps.gov.br")
        ftp.login()  # Login anônimo
        
        # Gera a lista das subpastas mensais: ['202201', '202202', ..., '202212']
        meses = [f"{ano}{mes:02d}" for mes in range(1, 13)]
        
        for mes in meses:
            caminho_mes = f"/{pasta_servidor}/{ano}/{mes}"
            try:
                # Entra na subpasta do mês (ex: /pdet/microdados/NOVO CAGED/2022/202201)
                ftp.cwd(caminho_mes)
                arquivos = ftp.nlst()
                
                # Encontra os arquivos .7z dentro da pasta do mês
                arquivos_7z = [f for f in arquivos if f.upper().endswith(".7Z")]
                
                for item in arquivos_7z:
                    nome_arquivo = Path(item).name
                    caminho_local = Path(pasta_destino) / nome_arquivo
                    print(f"⬇ Baixando {nome_arquivo} (Pasta {mes})...")
                    
                    with open(caminho_local, "wb") as f:
                        ftp.retrbinary(f"RETR {nome_arquivo}", f.write)
                        
                    print(f"✅ Salvo em: {caminho_local}")
                    
            except Exception as erro_mes:
                print(f"⚠️ Não foi possível acessar ou baixar o mês {mes}: {erro_mes}")
                
        ftp.quit()
        print("🎉 Download de todos os meses do CAGED concluído!")
        
    except Exception as erro:
        print(f"❌ Erro na conexão FTP com o CAGED: {erro}")