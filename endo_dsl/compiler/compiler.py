"""Compilador Endo-DSL -> protótipo HTML5 jogável (RF19–RF23).

Fluxo:
    fonte DSL --parse--> AST --valida--> content pack --render--> HTML autocontido

Garante:
* RF19 — saída HTML5 executável no navegador sem dependências externas;
* RF20 — erros de compilação descritivos, com sugestões referenciando a biblioteca;
* RF21 — níveis de Bloom preservados (no content pack e em ``data-bloom``);
* RF22 — reparametrização de conteúdo sem recompilar a estrutura;
* RF23 — documento de rastreabilidade gerado automaticamente.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from endo_dsl import __version__
from endo_dsl.compiler import content as content_mod
from endo_dsl.compiler import engine, traceability
from endo_dsl.dsl.ast import GameSpec
from endo_dsl.dsl.parser import ParseError, parse
from endo_dsl.dsl.semantic import MECHANIC_TYPES, validate_semantics


class CompileError(Exception):
    """Erro de compilação com mensagens descritivas e sugestões (RF20)."""

    def __init__(self, messages: List[Dict[str, Any]]):
        self.messages = messages
        super().__init__("; ".join(m.get("message", "") for m in messages))

    def to_dict(self) -> Dict[str, Any]:
        return {"errors": self.messages}


@dataclass
class CompileResult:
    """Resultado bem-sucedido da compilação."""

    html: str
    content_pack: Dict[str, Any]
    traceability: Dict[str, Any]
    bloom_levels: List[str] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    spec: Optional[GameSpec] = None

    def write(self, out_dir: str | Path, *, basename: str = "prototype") -> Dict[str, str]:
        """Escreve protótipo, rastreabilidade e content pack em ``out_dir``.

        Retorna os caminhos gerados.
        """
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        html_path = out / f"{basename}.html"
        trace_path = out / f"{basename}.traceability.html"
        trace_json = out / f"{basename}.traceability.json"
        content_path = out / f"{basename}.content.json"

        html_path.write_text(self.html, encoding="utf-8")
        if self.spec is not None:
            trace_path.write_text(traceability.as_html(self.spec), encoding="utf-8")
        trace_json.write_text(
            json.dumps(self.traceability, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        content_path.write_text(
            json.dumps(self.content_pack, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return {
            "html": str(html_path),
            "traceability_html": str(trace_path),
            "traceability_json": str(trace_json),
            "content_pack": str(content_path),
        }


def _suggest_from_library(mech_type: str) -> Optional[str]:
    """RF20 — sugere construtos equivalentes na biblioteca (catálogo de mecânicas)."""
    import difflib
    match = difflib.get_close_matches(mech_type, list(MECHANIC_TYPES), n=1, cutoff=0.4)
    if match:
        m = MECHANIC_TYPES[match[0]]
        return (f"a biblioteca oferece a mecânica '{match[0]}' ({m.label}); "
                f"considere usá-la.")
    return f"tipos de mecânica disponíveis na biblioteca: {', '.join(sorted(MECHANIC_TYPES))}"


def compile_spec(spec: GameSpec, *,
                 content_overrides: Optional[Dict[str, Any]] = None,
                 strict: bool = True) -> CompileResult:
    """Compila uma AST já validada em protótipo HTML5 (RF19).

    Se ``strict`` (padrão), erros semânticos abortam a compilação com mensagens
    descritivas (RF20). Warnings nunca abortam, mas são retornados.
    """
    issues = validate_semantics(spec)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i.to_dict() for i in issues if i.severity == "warning"]

    if errors and strict:
        messages = []
        for e in errors:
            d = e.to_dict()
            # Enriquecimento de sugestão referenciando a biblioteca (RF20).
            if e.code in ("E_BAD_TYPE", "E_NO_TYPE"):
                mech_type = _extract_type_token(e.message)
                lib = _suggest_from_library(mech_type)
                if lib:
                    d["suggestion"] = (d.get("suggestion") or "") + " " + lib
            messages.append(d)
        raise CompileError(messages)

    pack = content_mod.build_content_pack(spec, content_overrides=content_overrides)
    html = engine.render_html(pack, version=__version__)
    trace = traceability.build(spec)
    bloom_levels = [b.pt for b in spec.bloom_levels]
    return CompileResult(
        html=html,
        content_pack=pack,
        traceability=trace,
        bloom_levels=bloom_levels,
        warnings=warnings,
        spec=spec,
    )


def _extract_type_token(message: str) -> str:
    m = re.search(r"'([^']+)'", message)
    return m.group(1) if m else ""


def compile_source(source: str, *,
                   content_overrides: Optional[Dict[str, Any]] = None,
                   strict: bool = True) -> CompileResult:
    """Compila a partir do texto-fonte DSL (parse + semântica + render).

    Erros de sintaxe (RF03) e de compilação (RF20) são levantados como
    :class:`CompileError` com mensagens estruturadas.
    """
    try:
        spec = parse(source)
    except ParseError as exc:
        raise CompileError([exc.to_dict()]) from exc
    return compile_spec(spec, content_overrides=content_overrides, strict=strict)


# --------------------------------------------------------------------------- #
# RF22 — Reparametrização de conteúdo independente de estrutura.
# --------------------------------------------------------------------------- #
def reparametrize_content(html: str, *,
                          domain: Optional[str] = None,
                          topic: Optional[str] = None,
                          content_pack: Optional[Dict[str, Any]] = None) -> str:
    """Troca o domínio/conteúdo de um protótipo JÁ compilado **sem recompilar** (RF22).

    A estrutura (mecânicas, interações, níveis de Bloom) é preservada; apenas o
    conteúdo embutido é substituído. Pode-se passar um ``content_pack`` pronto ou
    pedir a re-resolução do banco por ``domain``/``topic``.
    """
    current = _extract_content_pack(html)
    if current is None:
        raise ValueError("HTML não contém um content pack Endo-DSL válido.")

    if content_pack is not None:
        new_pack = content_pack
    else:
        bank = content_mod.resolve_bank(domain, topic)
        new_pack = dict(current)
        new_pack["domain"] = domain or current.get("domain")
        # Reescreve o conteúdo de cada estágio preservando a estrutura.
        new_stages = []
        for stage in current["stages"]:
            st = dict(stage)
            interaction = st.get("interaction", "choose")
            if interaction == "choose":
                st["content"] = {"items": [dict(i) for i in bank.get("choose", [])]} or st["content"]
            elif interaction in bank:
                st["content"] = dict(bank[interaction])
            new_stages.append(st)
        new_pack["stages"] = new_stages

    pack_json = json.dumps(new_pack, ensure_ascii=False).replace("</", "<\\/")
    return re.sub(
        r'(<script id="endo-content" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + pack_json + m.group(2),
        html,
        count=1,
        flags=re.DOTALL,
    )


def _extract_content_pack(html: str) -> Optional[Dict[str, Any]]:
    m = re.search(
        r'<script id="endo-content" type="application/json">(.*?)</script>',
        html, flags=re.DOTALL,
    )
    if not m:
        return None
    raw = m.group(1).replace("<\\/", "</")
    try:
        return json.loads(raw)
    except ValueError:
        return None
