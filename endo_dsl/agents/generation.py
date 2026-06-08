"""Agente de Geração (RF15).

Produz uma especificação DSL a partir do contexto educacional e dos componentes
recuperados, adaptando-os ao domínio fornecido. Opera em dois modos:

* **LLM** (Claude) — quando há backend disponível, monta um prompt com a gramática
  e os componentes e solicita uma especificação DSL completa.
* **Template** — compositor determinístico (offline) que monta a DSL combinando os
  componentes selecionados; é válida por construção, servindo de fallback e baseline.
"""

from __future__ import annotations

import re
from typing import List, Optional

from endo_dsl.agents.context import DesignContext
from endo_dsl.agents.llm import LLMBackend, TemplateBackend, get_backend
from endo_dsl.agents.retrieval import RetrievedComponent
from endo_dsl.dsl.bloom import Bloom
from endo_dsl.dsl.semantic import MECHANIC_TYPES, mechanic_bloom_affinity

# Tipo de mecânica padrão por nível de Bloom (geração from scratch). Cada escolha
# tem o nível-alvo em sua afinidade, evitando incoerência semântica (RF04).
DEFAULT_TYPE_BY_BLOOM = {
    Bloom.LEMBRAR: "recall",
    Bloom.COMPREENDER: "classification",
    Bloom.APLICAR: "simulation",
    Bloom.ANALISAR: "comparison",
    Bloom.AVALIAR: "critique",
    Bloom.CRIAR: "design",
}


def _esc(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def _bloom_for_type(mech_type: str, target: Bloom) -> Bloom:
    """Nível de Bloom da afinidade do tipo mais próximo do alvo (sem incoerência)."""
    affinity = mechanic_bloom_affinity(mech_type)
    if not affinity:
        return target
    if target in affinity:
        return target
    return min(affinity, key=lambda b: abs(int(b) - int(target)))


def _ident(name: str, fallback: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s).strip("_")
    return s or fallback


class GenerationAgent:
    """Gera especificações DSL (RF15)."""

    def __init__(self, backend: Optional[LLMBackend] = None):
        self.backend = backend or get_backend()

    @property
    def backend_name(self) -> str:
        return self.backend.name

    def generate(self, context: DesignContext,
                 components: Optional[List[RetrievedComponent]] = None,
                 *, feedback: Optional[str] = None) -> str:
        components = components or []
        if isinstance(self.backend, TemplateBackend) or not self.backend.available:
            return self._compose_template(context, components, feedback)
        try:
            return self._compose_llm(context, components, feedback)
        except Exception:
            # Falha de rede/credencial -> degrada para o compositor determinístico.
            return self._compose_template(context, components, feedback)

    # ------------------------------------------------------------------ #
    # Modo determinístico (offline)
    # ------------------------------------------------------------------ #
    def _compose_template(self, ctx: DesignContext,
                          components: List[RetrievedComponent],
                          feedback: Optional[str]) -> str:
        title = ctx.title or f"Jogo: {ctx.learning_objective[:48]}" or "Protótipo Endo-DSL"
        topic = ctx.topic or ctx.domain or "o conteúdo"
        difficulty = str(ctx.extra.get("difficulty", "medium"))

        lines: List[str] = [f'game "{_esc(title)}" {{']
        # metadata
        lines.append("  metadata {")
        lines.append(f'    domain: "{_esc(ctx.domain)}"')
        audience = ctx.education_level or ctx.age_range or "geral"
        lines.append(f'    audience: "{_esc(audience)}"')
        ar = _parse_age_range(ctx.age_range)
        if ar:
            lines.append(f"    age_range: {ar[0]}..{ar[1]}")
        lines.append(f'    context: "{_esc(ctx.learner_context or "formal")}"')
        if ctx.duration_minutes:
            lines.append(f"    duration: {int(ctx.duration_minutes)}")
        lines.append(f'    platform: "{_esc(ctx.platform)}"')
        lines.append(f'    bloom_target: "{ctx.bloom_target.pt}"')
        if ctx.no_extensive_reading:
            lines.append("    no_extensive_reading: true")
        lines.append("  }")

        # objetivo
        lines.append("  objective OBJ_principal {")
        lines.append(f'    description: "{_esc(ctx.learning_objective)}"')
        lines.append(f"    bloom: {ctx.bloom_target.pt}")
        lines.append("  }")

        # mecânicas
        mechs = self._select_mechanics(ctx, components)
        for i, (mech_type, bloom, desc, source_key) in enumerate(mechs, start=1):
            name = _ident(source_key or mech_type, f"mecanica_{i}") + ("" if i == 1 else f"_{i}")
            lines.append(f"  mechanic {name} {{")
            lines.append(f"    type: {mech_type}")
            lines.append(f"    bloom: {bloom.pt}")
            lines.append("    addresses: OBJ_principal")
            if source_key:
                lines.append(f'    source_component: "{_esc(source_key)}"')
            lines.append("    params {")
            lines.append(f'      content: "{_esc(topic)}"')
            lines.append(f'      difficulty: "{_esc(difficulty)}"')
            lines.append(f'      domain: "{_esc(ctx.domain)}"')
            lines.append("    }")
            lines.append(f'    description: "{_esc(desc)}"')
            lines.append("  }")

        # loop de jogabilidade
        lines.append("  loop principal {")
        lines.append("    bloom: Aplicar")
        lines.append("    steps {")
        lines.append("      apresenta -> desafia")
        lines.append("      desafia -> avalia")
        lines.append("      avalia -> apresenta")
        lines.append("    }")
        lines.append("  }")

        lines.append("}")
        return "\n".join(lines)

    def _select_mechanics(self, ctx: DesignContext,
                          components: List[RetrievedComponent]):
        """Retorna lista de (type, bloom, description, source_key)."""
        result = []
        for rc in components[:3]:
            comp = rc.component
            mtype = comp.mechanic_type if comp.mechanic_type in MECHANIC_TYPES else \
                DEFAULT_TYPE_BY_BLOOM[ctx.bloom_target]
            bloom = _bloom_for_type(mtype, ctx.bloom_target)
            result.append((mtype, bloom, comp.description, comp.key))
        if not result:
            # from scratch: uma mecânica central no nível alvo + uma de apoio
            mtype = DEFAULT_TYPE_BY_BLOOM[ctx.bloom_target]
            label = MECHANIC_TYPES[mtype].label
            result.append((mtype, ctx.bloom_target,
                           f"Mecânica de {label.lower()} sobre {ctx.topic or ctx.domain}.", None))
            if ctx.bloom_target > Bloom.COMPREENDER:
                support_type = DEFAULT_TYPE_BY_BLOOM[Bloom.COMPREENDER]
                result.append((support_type, Bloom.COMPREENDER,
                               f"Mecânica de apoio para compreender {ctx.topic or ctx.domain}.",
                               None))
        return result

    # ------------------------------------------------------------------ #
    # Modo LLM (Claude)
    # ------------------------------------------------------------------ #
    def _compose_llm(self, ctx: DesignContext,
                     components: List[RetrievedComponent],
                     feedback: Optional[str]) -> str:
        system = _SYSTEM_PROMPT
        comp_block = "\n\n".join(
            f"// componente '{rc.component.key}' "
            f"(Bloom: {rc.component.bloom_level}, tipo: {rc.component.mechanic_type})\n"
            f"{rc.component.dsl_signature}"
            for rc in components
        ) or "// (nenhum componente selecionado — gere do zero)"
        user = (
            f"Contexto educacional:\n"
            f"- Objetivo de aprendizagem: {ctx.learning_objective}\n"
            f"- Área de conhecimento: {ctx.domain}\n"
            f"- Tema: {ctx.topic or ctx.domain}\n"
            f"- Nível de Bloom desejado: {ctx.bloom_target.pt}\n"
            f"- Perfil do aprendiz: {ctx.age_range or '—'}, {ctx.education_level or '—'}, "
            f"contexto {ctx.learner_context or 'formal'}\n"
            f"- Restrições: duração {ctx.duration_minutes or '—'} min, plataforma {ctx.platform}, "
            f"sem leitura extensiva: {ctx.no_extensive_reading}\n\n"
            f"Componentes recuperados da biblioteca (use-os como ponto de partida):\n"
            f"{comp_block}\n\n"
        )
        if feedback:
            user += (f"A tentativa anterior foi rejeitada pela validação. Corrija estes "
                     f"problemas:\n{feedback}\n\n")
        user += ("Gere UMA especificação Endo-DSL completa e válida, começando por "
                 '`game "..." { ... }`. Responda apenas com o código DSL.')

        result = self.backend.complete(system, user, max_tokens=2048)
        return _extract_dsl(result.text)


def _parse_age_range(text: Optional[str]):
    if not text:
        return None
    nums = re.findall(r"\d+", str(text))
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    return None


def _extract_dsl(text: str) -> str:
    """Extrai o bloco DSL da resposta do LLM (remove cercas de código e ruído)."""
    if "```" in text:
        fences = re.findall(r"```(?:[a-zA-Z]+)?\n(.*?)```", text, re.DOTALL)
        if fences:
            text = fences[0]
    m = re.search(r"(game\s+\"[^\"]*\"\s*\{.*\})", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


_SYSTEM_PROMPT = """Você é o Agente de Geração da plataforma Endo-DSL, especialista em \
design de jogos educacionais endógenos. Você escreve especificações na Endo-DSL, cuja \
gramática é:

game "Título" {
  metadata { domain: "..." audience: "..." age_range: 10..11 context: "formal" \
duration: 15 platform: "web" }
  objective ID { description: "..." bloom: Analisar }
  mechanic ID { type: <tipo> bloom: <nível> addresses: ID_objetivo \
params { content: "..." difficulty: "medium" domain: "..." } description: "..." }
  loop ID { bloom: Aplicar steps { a -> b  b -> c  c -> a } }
  narrative ID { branch ID { text: "..." choice "..." -> outro_ramo } }
}

Níveis de Bloom (use exatamente): Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar.
Tipos de mecânica válidos: recall, flashcard, matching, labeling, quiz, classification, \
sequencing, comparison, simulation, puzzle, construction, strategy, role_play, decision, \
critique, debate, design, storytelling, exploration.

Regra de coerência: o nível de Bloom de uma mecânica deve ser compatível com seu tipo \
(ex.: 'recall' exercita 'Lembrar', não 'Criar'). Toda mecânica deve endereçar um objetivo. \
Responda APENAS com o código DSL, sem explicações."""
