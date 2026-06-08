"""Backend de linguagem plugável para o pipeline multi-agente.

Abstrai a geração de texto por LLM. Há duas implementações:

* :class:`ClaudeBackend` — usa a API da Claude (pacote ``anthropic``), ativada
  automaticamente quando o SDK está instalado e ``ANTHROPIC_API_KEY`` definido.
  Modelo padrão: ``claude-sonnet-4-5`` (sobreponível por ``ENDO_DSL_LLM_MODEL``).
* :class:`TemplateBackend` — backend determinístico, sem rede, que serve de
  fallback para que o pipeline seja sempre executável e testável offline. A
  composição real da DSL nesse modo fica em :mod:`endo_dsl.agents.generation`.

A seleção é feita por :func:`get_backend`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_MODEL = os.environ.get("ENDO_DSL_LLM_MODEL", "claude-sonnet-4-5")


@dataclass
class LLMResult:
    text: str
    backend: str
    model: Optional[str] = None


class LLMBackend:
    """Interface comum dos backends de linguagem."""

    name = "base"
    available = False

    def complete(self, system: str, user: str, *, max_tokens: int = 2048) -> LLMResult:
        raise NotImplementedError


class TemplateBackend(LLMBackend):
    """Backend determinístico (fallback offline).

    Não realiza completude livre de texto; sinaliza ao agente de geração que a
    composição determinística por templates deve ser usada.
    """

    name = "template"
    available = True

    def complete(self, system: str, user: str, *, max_tokens: int = 2048) -> LLMResult:
        # O agente de geração detecta este backend e compõe a DSL por templates,
        # sem chamar este método. Mantido por completude da interface.
        raise RuntimeError(
            "TemplateBackend não gera texto livre; use a composição determinística."
        )


class ClaudeBackend(LLMBackend):
    """Backend baseado na API da Claude (Anthropic)."""

    name = "claude"

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._client = None
        try:
            import anthropic  # type: ignore

            self._client = anthropic.Anthropic()
            self.available = True
        except Exception:  # SDK ausente ou sem credenciais
            self.available = False

    def complete(self, system: str, user: str, *, max_tokens: int = 2048) -> LLMResult:
        if not self.available or self._client is None:
            raise RuntimeError("ClaudeBackend indisponível (SDK ou chave ausente).")
        message = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
        return LLMResult(text=text, backend=self.name, model=self.model)


def get_backend(prefer: Optional[str] = None) -> LLMBackend:
    """Retorna o backend ativo.

    Por padrão usa Claude se disponível; caso contrário, o backend de template.
    ``prefer='template'`` força o modo offline determinístico.
    """
    if prefer == "template":
        return TemplateBackend()
    if prefer in (None, "claude") and os.environ.get("ANTHROPIC_API_KEY"):
        claude = ClaudeBackend()
        if claude.available:
            return claude
    return TemplateBackend()
