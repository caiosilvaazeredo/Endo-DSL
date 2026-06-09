"""Endo-DSL — plataforma de design e geração automática de jogos educacionais endógenos.

Quatro subsistemas integrados:

* ``endo_dsl.dsl``        — Motor da DSL (gramática formal, parser e validadores).
* ``endo_dsl.library``    — Biblioteca de componentes reutilizáveis (SQLite).
* ``endo_dsl.agents``     — Pipeline multi-agente LLM (recuperação, geração, validação).
* ``endo_dsl.compiler``   — Compilador DSL -> protótipo HTML5 jogável.
* ``endo_dsl.evaluation`` — Instrumento de avaliação e relatórios comparativos.

Proposta de pesquisa — Doutorado PESC/COPPE/UFRJ.
Caio Azeredo | Orientador: Prof. Geraldo Bonorino Xexéo.
"""

__version__ = "1.1.0"
__all__ = ["__version__"]
