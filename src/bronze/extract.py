from bronze.error_handling import (
status_handling,
exception_handling
)
import json
import requests
from pathlib import Path



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

 