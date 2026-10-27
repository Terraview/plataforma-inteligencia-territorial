"""Localização dos arquivos de entrada (caminhos relativos ou absolutos)."""
from __future__ import annotations

from pathlib import Path

from .config import CAGED_PATTERNS, IPCA_PATTERNS, PIB_PATTERNS, POPULACAO_PATTERNS


def _find(directory: Path, patterns: list[str]) -> list[Path]:
    found: dict[str, Path] = {}
    for pat in patterns:
        for p in directory.glob(pat):
            if p.is_file():
                found[str(p.resolve())] = p.resolve()
    return sorted(found.values())


def _find_one(directory: Path, patterns: list[str], label: str) -> Path:
    matches = _find(directory, patterns)
    if len(matches) != 1:
        raise FileNotFoundError(
            f"[{label}] esperado exatamente 1 arquivo em {directory} "
            f"com padrões {patterns}; encontrados: {[m.name for m in matches]}"
        )
    return matches[0]


def resolve_inputs(root: Path, caged_dir: str, ibge_dir: str) -> dict:
    """Caminhos relativos são resolvidos a partir de `root`; absolutos são mantidos."""
    def _dir(d: str) -> Path:
        p = Path(d)
        return p if p.is_absolute() else (root / p)

    cdir, idir = _dir(caged_dir), _dir(ibge_dir)
    for d in (cdir, idir):
        if not d.is_dir():
            raise FileNotFoundError(f"Diretório não encontrado: {d}")
    caged = _find(cdir, CAGED_PATTERNS)
    if not caged:
        raise FileNotFoundError(f"Nenhum arquivo CAGED em {cdir} ({CAGED_PATTERNS})")
    return {
        "caged": [p.as_posix() for p in caged],
        "populacao": _find_one(idir, POPULACAO_PATTERNS, "populacao").as_posix(),
        "pib": _find_one(idir, PIB_PATTERNS, "pib").as_posix(),
        "ipca": _find_one(idir, IPCA_PATTERNS, "ipca").as_posix(),
    }
