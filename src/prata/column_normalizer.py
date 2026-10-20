
import re
import unicodedata


def normalizar_nome_coluna(nome):

    nome = (
        unicodedata
        .normalize("NFKD", nome)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

    nome = nome.lower()

    nome = re.sub(
        r"[^a-z0-9]+",
        "_",
        nome
    )

    return nome.strip("_")


def normalizar_colunas(df):

    for coluna in df.columns:

        df = df.withColumnRenamed(
            coluna,
            normalizar_nome_coluna(coluna)
        )

    return df

