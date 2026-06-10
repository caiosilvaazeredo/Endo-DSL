"""Demonstração ponta-a-ponta da plataforma Endo-DSL.

Percorre a jornada completa (Fases 1–7 + curadoria) com dados de exemplo e
imprime um resumo de cada requisito exercitado. Útil para validação manual e
para apresentar a plataforma.
"""

from __future__ import annotations

from typing import Optional

from endo_dsl.evaluation.instrument import dimension_keys
from endo_dsl.platform import Platform


def run_demo(db_path: Optional[str] = None) -> None:
    p = Platform(db_path or ":memory:")
    line = "─" * 64

    print(line)
    print(" DEMONSTRAÇÃO Endo-DSL — jornada completa do Designer/Educador")
    print(line)
    print(f" Backend LLM: {p.backend.name}  |  componentes na biblioteca: "
          f"{len(p.search_components())}")

    # Fase 1 — contexto
    print("\n[Fase 1] Definição do contexto educacional (RF13)")
    sid = p.create_session("Demo — Frações", {
        "learning_objective": "comparar frações com denominadores diferentes",
        "domain": "Matemática", "topic": "frações", "bloom_target": "Analisar",
        "age_range": "10-11", "education_level": "5º ano", "learner_context": "formal",
        "duration": 15, "platform": "web", "no_extensive_reading": True,
    })
    ctx = p.session_context(sid)
    print(f"  sessão #{sid}: {ctx.learning_objective} (Bloom alvo: {ctx.bloom_target.pt})")

    # Fase 2 — recuperação
    print("\n[Fase 2] Recuperação de componentes (RF14)")
    retrieved = p.retrieve(ctx, top_k=4)
    for rc in retrieved:
        print(f"  {rc.score:.2f}  {rc.component.key} ({rc.component.status}) — "
              f"{'; '.join(rc.reasons[:2])}")

    # Fase 3 — geração
    print("\n[Fase 3] Geração da especificação DSL (RF15/RF16)")
    keys = [retrieved[0].component.key] if retrieved else None
    res = p.generate(sid, selected_keys=keys)
    print(f"  {'válida' if res.success else 'inválida'} em {len(res.attempts)} tentativa(s) — "
          f"{res.report.summary()}")

    # Fase 4 — revisão/validação
    print("\n[Fase 4] Revisão e validação em tempo real (RF03/RF04/RF05)")
    val = p.validate(res.dsl)
    print(f"  sintaxe={'ok' if val['syntactic_ok'] else 'erro'}, "
          f"semântica={'ok' if val['semantic_ok'] else 'erro'}, "
          f"avisos={len(val['warnings'])}")

    # Fase 5 — compilação
    print("\n[Fase 5] Compilação e geração do protótipo (RF19-RF23)")
    comp = p.compile(res.dsl, session_id=sid, origin="auto")
    print(f"  protótipo #{comp['prototype_id']}: {comp['paths']['html']}")
    print(f"  rastreabilidade: {comp['traceability']['coverage']}")
    rep = p.reparametrize(comp["prototype_id"], domain="educação ambiental")
    print(f"  reparametrizado (RF22) -> {rep['path']}")

    # Fase 6 — avaliação
    print("\n[Fase 6] Avaliação pedagógica (RF24-RF26)")
    auto_scores = {k: v for k, v in zip(dimension_keys(), [4, 5, 4, 4, 4, 3, 5])}
    manual_scores = {k: v for k, v in zip(dimension_keys(), [5, 4, 4, 5, 5, 5, 3])}
    p.evaluate(prototype_id=comp["prototype_id"], origin="auto", evaluator="ana",
               scores=auto_scores)
    p.evaluate(origin="manual", evaluator="joão", bloom_level="Analisar",
               domain="Matemática", scores=manual_scores)
    report = p.comparison_report()
    print(f"  {report['interpretation']}")

    # Fase 7 — contribuição + curadoria
    print("\n[Fase 7] Contribuição e curadoria (RF07/RF12)")
    new_id = p.contribute_component(
        name="Roleta de Revisão",
        dsl_signature='mechanic roleta { type: quiz bloom: Lembrar }',
        bloom_level="Lembrar", mechanic_type="quiz",
        description="Roleta sorteia perguntas de revisão para fixação.", author="caio")
    print(f"  componente experimental #{new_id} submetido; fila: {len(p.curation_queue())}")
    p.approve_component(new_id, curator="curador", justification="qualidade adequada")
    print(f"  curador aprovou -> agora canônico; fila: {len(p.curation_queue())}")

    print("\n[Métricas] Geração (RF18):", p.generation_metrics(sid))
    print(line)
    print(" Demonstração concluída. Use 'endo-dsl serve' para a interface web.")
    print(line)
    p.close()
