import os
from dotenv import load_dotenv

load_dotenv()

SIDRA_BASE_URL = os.getenv("SIDRA_BASE_URL")
def construir_url(
        tabela,
        nivel,
        localidade,
        variavel,
        periodo
):
    return(
        f"{SIDRA_BASE_URL}"
        f"/values/t/{tabela}"
        f"/{nivel}/{localidade}"
        f"/v/{variavel}"
        f"/p/{periodo}"
    )





