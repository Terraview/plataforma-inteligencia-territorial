def construir_url(
        tabela,
        nivel,
        localidade,
        variavel,
        periodo
):
    return(
        f"http://apisidra.ibge.gov.br"
        f"/values/t/{tabela}"
        f"/{nivel}/{localidade}"
        f"/v/{variavel}"
        f"/p/{periodo}"
    )



