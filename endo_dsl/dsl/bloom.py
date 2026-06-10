"""Taxonomia de Bloom como construto de primeira classe (RF02).

Os seis níveis cognitivos são modelados como um ``IntEnum`` ordenado, de forma que
operações de comparação (``<``, ``>=``) expressem progressão cognitiva diretamente.

Os nomes canônicos são em português (conforme a proposta), mas o parser aceita
aliases em inglês para interoperabilidade.
"""

from __future__ import annotations

import difflib
from enum import IntEnum
from typing import List, Optional


class Bloom(IntEnum):
    """Os seis níveis da Taxonomia de Bloom (revisada), ordenados por demanda cognitiva."""

    LEMBRAR = 1
    COMPREENDER = 2
    APLICAR = 3
    ANALISAR = 4
    AVALIAR = 5
    CRIAR = 6

    @property
    def pt(self) -> str:
        """Nome canônico em português."""
        return _PT_NAMES[self]

    @property
    def en(self) -> str:
        """Nome em inglês."""
        return _EN_NAMES[self]

    @property
    def slug(self) -> str:
        """Identificador estável para uso em código/JSON/HTML (ex.: ``analisar``)."""
        return self.name.lower()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.pt


BLOOM_ORDER: List[Bloom] = list(Bloom)

_PT_NAMES = {
    Bloom.LEMBRAR: "Lembrar",
    Bloom.COMPREENDER: "Compreender",
    Bloom.APLICAR: "Aplicar",
    Bloom.ANALISAR: "Analisar",
    Bloom.AVALIAR: "Avaliar",
    Bloom.CRIAR: "Criar",
}

_EN_NAMES = {
    Bloom.LEMBRAR: "Remember",
    Bloom.COMPREENDER: "Understand",
    Bloom.APLICAR: "Apply",
    Bloom.ANALISAR: "Analyze",
    Bloom.AVALIAR: "Evaluate",
    Bloom.CRIAR: "Create",
}

# Mapa de aliases aceitos pelo parser -> nível. Inclui português, inglês e
# variações ortográficas comuns (com/sem acento, grafia britânica).
_ALIASES = {}
for _level in Bloom:
    for _name in (_level.pt, _level.en, _level.name):
        _ALIASES[_name.lower()] = _level
_ALIASES.update(
    {
        "analyse": Bloom.ANALISAR,  # grafia britânica
        "remember": Bloom.LEMBRAR,
        "lembrar": Bloom.LEMBRAR,
        "compreender": Bloom.COMPREENDER,
        "entender": Bloom.COMPREENDER,
        "aplicar": Bloom.APLICAR,
        "analisar": Bloom.ANALISAR,
        "avaliar": Bloom.AVALIAR,
        "criar": Bloom.CRIAR,
    }
)


def parse_bloom(token: str) -> Optional[Bloom]:
    """Resolve um token textual para um nível de Bloom, ou ``None`` se inválido."""
    if token is None:
        return None
    return _ALIASES.get(token.strip().lower())


def suggest_bloom(token: str, n: int = 1) -> List[str]:
    """Sugere nomes de níveis próximos a um token inválido (para mensagens de erro)."""
    canonical = [level.pt for level in Bloom] + [level.en for level in Bloom]
    return difflib.get_close_matches(token, canonical, n=n, cutoff=0.4)


def all_names() -> List[str]:
    """Lista de nomes canônicos (pt) para autocompletar/documentação."""
    return [level.pt for level in Bloom]
