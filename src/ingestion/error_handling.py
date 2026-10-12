import requests
import json

def status_handling(response):

#O código 404 significa que a URL aponta para algo que não existe (tabela, rota ou parâmetro errado). Imprime a mensagem e retorna False

    if response.status_code == 404:  
        print(" Erro 404: recurso não encontrado.")
        return False

#O código 500 indica falha no servidor da API. O problema não é seu, e muitas vezes tentar de novo mais tarde resolve.
 
    elif response.status_code == 500:
        print(" Erro 500: erro interno do servidor.")
        return False

#Captura qualquer outro código diferente de 200.
 
    elif response.status_code != 200:
        print(f" Erro HTTP {response.status_code}: "
    f"{response.reason}"
)                   
        return False

    return True #Se nenhum if anterior foi acionado, o status é 200 (OK) e a função retorna True


def exception_handling(erro):

    if isinstance(erro, requests.exceptions.Timeout):
        print(" Timeout: a API demorou para responder.") #Acontece quando a API não respondeu dentro do timeout=30 que você definiu no requests.get.

    elif isinstance(erro, requests.exceptions.ConnectionError):
        print(" Erro de conexão com a API.") #Falha de rede: sem internet, DNS não resolveu, servidor fora do ar ou conexão recusada.

    elif isinstance(erro, requests.exceptions.RequestException):
        print(f" Erro na requisição: {erro}") #RequestException é a classe-mãe de todos os erros do requests. Aqui ela serve como "rede de segurança" para qualquer erro do requests que não seja Timeout nem ConnectionError (URL inválida, redirecionamentos demais etc.).

    elif isinstance(erro, json.JSONDecodeError):
        print(" Erro ao interpretar o JSON retornado.") #Ocorre no response.json() quando a resposta não é um JSON válido (por exemplo, a API devolveu HTML ou texto de erro).

    else:
        print(f" Erro inesperado: {erro}") #Qualquer outro erro que não caiu nos casos anteriores (permissão ao gravar arquivo, bug no código etc.).
        