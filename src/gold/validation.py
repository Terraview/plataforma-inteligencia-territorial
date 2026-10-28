"""Validações de contagem, duplicidade e integridade referencial."""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .config import ANOS


def _dup_keys(df: DataFrame, cols: list[str]) -> int:
    return df.groupBy(*cols).count().filter(F.col("count") > 1).count()


def _orphans(child: DataFrame, col: str, parent: DataFrame, pcol: str | None = None) -> int:
    pcol = pcol or col
    p = parent.select(F.col(pcol).alias("_k")).distinct()
    c = child.select(F.col(col).alias("_k"))
    return c.join(F.broadcast(p), "_k", "left_anti").count()


def validate_star_schema(t: dict[str, DataFrame]) -> list[tuple[str, bool, str]]:
    res: list[tuple[str, bool, str]] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        res.append((name, bool(ok), detail))

    n = {k: v.count() for k, v in t.items()}

    # --- Dimensões ---------------------------------------------------------
    chk("dim_uf: 7 UFs (CO+Sul)", n["dim_uf"] == 7, f"{n['dim_uf']}")
    chk("dim_uf: PK única", _dup_keys(t["dim_uf"], ["cod_uf"]) == 0)
    chk("dim_municipio: PK única", _dup_keys(t["dim_municipio"], ["cod_municipio"]) == 0)
    chk("dim_municipio: cod_municipio_6 único (ponte CAGED sem N:N)",
        _dup_keys(t["dim_municipio"], ["cod_municipio_6"]) == 0)
    chk("dim_municipio: sem nulos em nome/UF",
        t["dim_municipio"].filter(F.col("nome_municipio").isNull() | (F.col("nome_municipio") == "")
                                  | F.col("sigla_uf").isNull()).count() == 0)
    chk("dim_municipio -> dim_uf (FK)", _orphans(t["dim_municipio"], "cod_uf", t["dim_uf"]) == 0)
    chk("dim_tempo: 60 competências, PK única",
        n["dim_tempo"] == 60 and _dup_keys(t["dim_tempo"], ["competencia"]) == 0)
    chk("dim_ano: 5 anos, PK única", n["dim_ano"] == 5 and _dup_keys(t["dim_ano"], ["ano"]) == 0)
    chk("dim_cbo: PK única", _dup_keys(t["dim_cbo"], ["cod_cbo"]) == 0, f"{n['dim_cbo']} códigos")

    # --- Contagens contra a origem (detecta perda ou multiplicação) -------
    esperado_caged = (
        t["_raw_caged"].withColumn("cod_uf", F.col("uf").cast("int"))
        .join(F.broadcast(t["dim_uf"].select("cod_uf")), "cod_uf", "left_semi").count()
    )
    chk("fato_caged: contagem = origem filtrada por UF", n["fato_caged"] == esperado_caged,
        f"fato={n['fato_caged']} origem={esperado_caged}")
    chk("fato_pib: contagem = municípios x anos",
        n["fato_pib"] == n["dim_municipio"] * len(ANOS), f"{n['fato_pib']}")
    chk("fato_populacao_uf: contagem = UFs x 3 anos (2019-2021)",
        n["fato_populacao_uf"] == n["dim_uf"] * 3, f"{n['fato_populacao_uf']}")
    chk("fato_ipca_mensal: 60 meses", n["fato_ipca_mensal"] == 60, f"{n['fato_ipca_mensal']}")

    # --- Unicidade do grão (fatos com chave natural) ----------------------
    chk("fato_pib: grão único (município, ano)", _dup_keys(t["fato_pib"], ["cod_municipio", "ano"]) == 0)
    chk("fato_populacao_uf: grão único (UF, ano)", _dup_keys(t["fato_populacao_uf"], ["cod_uf", "ano"]) == 0)
    chk("fato_ipca_mensal: grão único (competência)", _dup_keys(t["fato_ipca_mensal"], ["competencia"]) == 0)

    # --- Integridade referencial -----------------------------------------
    fc = t["fato_caged"]
    chk("fato_caged: cod_municipio sem órfãos/nulos",
        fc.filter(F.col("cod_municipio").isNull()).count() == 0)
    chk("fato_caged -> dim_municipio (FK)", _orphans(fc, "cod_municipio", t["dim_municipio"]) == 0)
    chk("fato_caged -> dim_tempo (FK)", _orphans(fc, "competencia", t["dim_tempo"]) == 0)
    chk("fato_caged -> dim_cbo (FK)", _orphans(fc, "cod_cbo", t["dim_cbo"]) == 0)
    chk("fato_pib -> dim_municipio (FK)", _orphans(t["fato_pib"], "cod_municipio", t["dim_municipio"]) == 0)
    chk("fato_pib -> dim_ano (FK)", _orphans(t["fato_pib"], "ano", t["dim_ano"]) == 0)
    chk("fato_populacao_uf -> dim_uf (FK)", _orphans(t["fato_populacao_uf"], "cod_uf", t["dim_uf"]) == 0)
    chk("fato_populacao_uf -> dim_ano (FK)", _orphans(t["fato_populacao_uf"], "ano", t["dim_ano"]) == 0)
    chk("fato_ipca_mensal -> dim_tempo (FK)", _orphans(t["fato_ipca_mensal"], "competencia", t["dim_tempo"]) == 0)

    # --- Qualidade dos casts (NULL gerado por valor não numérico) --------
    chk("fato_pib: sem PIB nulo", t["fato_pib"].filter(F.col("pib_correntes_mil_reais").isNull()).count() == 0)
    chk("fato_populacao_uf: sem população nula",
        t["fato_populacao_uf"].filter(F.col("populacao_estimada").isNull()).count() == 0)
    chk("fato_ipca_mensal: sem IPCA nulo",
        t["fato_ipca_mensal"].filter(F.col("ipca_variacao_mensal_pct").isNull()).count() == 0)
    chk("fato_caged: sem competência nula", fc.filter(F.col("competencia").isNull()).count() == 0)

    # --- Informativos (não reprovam) ---------------------------------------
    sal_nulo = fc.filter(F.col("salario_nominal").isNull()).count()
    idade_nula = fc.filter(F.col("idade").isNull()).count()
    dup_exatas = n["fato_caged"] - fc.distinct().count()
    chk("[info] fato_caged: salário nulo (campo ausente/não numérico)", True, f"{sal_nulo}")
    chk("[info] fato_caged: idade nula", True, f"{idade_nula}")
    chk("[info] fato_caged: linhas idênticas preservadas (NÃO removidas)", True, f"{dup_exatas}")
    return res
