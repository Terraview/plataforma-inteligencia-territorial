import requests
import json

def status_handling(response):

    if response.status_code == 404:
        print(" Erro 404: recurso não encontrado.")
        return False

    elif response.status_code == 500:
        print(" Erro 500: erro interno do servidor.")
        return False

    elif response.status_code != 200:
        print(f" Erro HTTP {response.status_code}: "
    f"{response.reason}"
)                   
        return False

    return True


def exception_handling(erro):

    if isinstance(erro, requests.exceptions.Timeout):
        print(" Timeout: a API demorou para responder.")

    elif isinstance(erro, requests.exceptions.ConnectionError):
        print(" Erro de conexão com a API.")

    elif isinstance(erro, requests.exceptions.RequestException):
        print(f" Erro na requisição: {erro}")

    elif isinstance(erro, json.JSONDecodeError):
        print(" Erro ao interpretar o JSON retornado.")

    else:
        print(f" Erro inesperado: {erro}")