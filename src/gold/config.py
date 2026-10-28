"""Constantes e esquemas de leitura. Para mudar anos, regiões ou nomes de arquivo, edite aqui."""
from pyspark.sql import types as T

ANOS = list(range(2019, 2024))                 # 2019..2023
REGIOES_ALVO = ("Sudeste", "Sul")

# Padrões (glob) para localizar os arquivos dentro das pastas de entrada.
CAGED_PATTERNS = ["CAGED*.json", "caged*.json"]
POPULACAO_PATTERNS = ["populacao*.json"]
PIB_PATTERNS = ["pib*.json"]
IPCA_PATTERNS = ["ipca*.json"]

# Esquemas explícitos (contrato de leitura). Tudo string: preserva zeros à
# esquerda ("01", "004441,00") e evita inferência divergente entre as variantes.
CAGED_SCHEMA = T.StructType(
    [T.StructField(c, T.StringType(), True) for c in (
        "competencia", "ano", "municipio", "uf", "cbo", "sexo",
        "idade", "escolaridade", "salario", "movimento", "periodo",
    )]
)
SIDRA_SCHEMA = T.StructType(
    [T.StructField(c, T.StringType(), True) for c in (
        "NC", "NN", "MC", "MN", "V", "D1C", "D1N", "D2C", "D2N", "D3C", "D3N",
    )]
)
