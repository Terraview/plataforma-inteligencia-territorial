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
        response = requests.get( #Envia um GET para a API e guarda a resposta em response. O timeout=30 diz: "se a API não responder em 30 segundos, desista e lance um Timeout". Sem isso, o programa poderia ficar travado indefinidamente.

            url,
            timeout=30
)

        if not status_handling(response): #Se o status não for 200, ela imprime o erro e devolve False. O not inverte isso, então a função encerra aqui com None
            return None

        dados = response.json() #Transforma o texto da resposta em estruturas Python (lista de dicionários, no caso do SIDRA). Se a resposta não for um JSON válido, estoura um JSONDecodeError, que cai no except.

        Path(pasta_destino).mkdir(
            
            parents=True, #cria também as pastas intermediárias (data e depois data/bronze)
            exist_ok=True #se a pasta já existir, não dá erro.
        )

        caminho = (
            Path(pasta_destino) #O operador / do pathlib junta as partes, resultando em data/bronze/ipca_2022.json. Funciona em qualquer sistema operacional, sem se preocupar com / ou \
            / nome_arquivo
        )

        with open(
            caminho,
            "w", #abre para escrita (sobrescreve se já existir).
            encoding="utf-8" #garante que acentos sejam gravados corretamente.
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False, #mantém caracteres como "ã" e "ç" legíveis, em vez de \u00e3.
                indent=4 #deixa o JSON formatado e fácil de ler.
        )

        print(f" Arquivo salvo em: {caminho}")

        return dados

    except Exception as erro: #Se qualquer coisa estourar no try (timeout, falta de conexão, JSON inválido, erro ao gravar), o erro é capturado, enviado para o exception_handling (que imprime a mensagem adequada) e a função devolve None.
        exception_handling(erro)
        return None



# CAGED - Conexão FTP com o MTE (Ministério do Trabalho e Emprego)

def extrair_caged_ftp(
    pasta_servidor="pdet/microdados/NOVO CAGED",
    pasta_destino="data/bronze/caged",
    ano="2022",
    meses_filtro=["202201"]
):
    try:
        Path(pasta_destino).mkdir(parents=True, exist_ok=True)

        print("🔌 Conectando ao servidor FTP do MTE (ftp.mtps.gov.br)...")

        ftp = FTP("ftp.mtps.gov.br")
        ftp.login()  # Login anônimo

        # Se você passar meses_filtro (ex: ["202201"]), baixa só esses.
        # Senão, gera de 01 a 12.
        if meses_filtro:
            meses = meses_filtro
        else:
            meses = [f"{ano}{mes:02d}" for mes in range(1, 13)]

        for mes in meses:
            caminho_mes = f"/{pasta_servidor}/{ano}/{mes}"

            try:
                ftp.cwd(caminho_mes)
                arquivos = ftp.nlst()

                arquivos_7z = [
                    f for f in arquivos if f.upper().endswith(".7Z")
                ]

                for item in arquivos_7z:
                    nome_arquivo = Path(item).name
                    caminho_local = Path(pasta_destino) / nome_arquivo

                    # 1. PULA O DOWNLOAD SE O ARQUIVO JÁ EXISTE LOCALMENTE
                    if (
                        caminho_local.exists()
                        and caminho_local.stat().st_size > 0
                    ):
                        print(
                            f"⏩ {nome_arquivo} já baixado em "
                            f"{pasta_destino}. Pulando..."
                        )
                        continue

                    print(f"⬇️ Baixando {nome_arquivo} (Pasta {mes})...")

                    # 2. USAMOS blocksize DE 1MB (MUITO MAIS RÁPIDO QUE O PADRÃO DE 8KB)
                    with open(caminho_local, "wb") as f:
                        ftp.retrbinary(
                            f"RETR {nome_arquivo}",
                            f.write,
                            blocksize=1024 * 1024
                        )

                    print(f"✅ Salvo em: {caminho_local}")

            except Exception as erro_mes:
                print(
                    f"⚠️ Não foi possível acessar ou baixar o mês "
                    f"{mes}: {erro_mes}"
                )

        ftp.quit()
        print("🎉 Download do CAGED concluído!")

    except Exception as erro:
        print(f"❌ Erro na conexão FTP com o CAGED: {erro}")