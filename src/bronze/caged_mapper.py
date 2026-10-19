
######### MAPEAMENTO DOS ARQUIVOS CAGED #########

def gerar_competencias():
    competencias = []
   
    for ano in range(2019,2024):
        for mes in range(1, 13):
            competencias.append(f"{ano}{mes:02d}")
    
    return competencias


def build_path_caged(competencia):
    ano = competencia[:4]
    mes = competencia[4:]

    if ano == "2019":
        return (
            f'CAGED/'
            f'{ano}/'
            f'CAGEDEST_{mes}{ano}.7z'
        )

    return (
        f'NOVO CAGED/'
        f'{ano}/'
        f'{competencia}/'
        f'CAGEDMOV{competencia}.7z'
    )

