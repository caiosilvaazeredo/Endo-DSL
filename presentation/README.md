# Slide deck — Exame de qualificação (Endo-DSL)

Gera `Endo-DSL-Qualificacao.pptx`: um deck de 36 slides em português para o
exame de qualificação de doutorado no PESC/COPPE/UFRJ.

## Conteúdo

- `build_deck.py` — script Python (usa `python-pptx`) que monta o deck inteiro
  programaticamente: tema visual consistente (barras de título *slate* `#1E293B`,
  acentos índigo `#4F46E5`, conteúdo branco, fontes Calibri), numeração de slides,
  rodapé institucional e diagramas montados com formas pptx (arquitetura de 5
  módulos, fluxo do pipeline, pirâmide de Bloom colorida, stepper da jornada,
  matriz de afinidade, Gantt).
- `Endo-DSL-Qualificacao.pptx` — artefato gerado (36 slides, 16:9 widescreen).

## Pré-requisitos

```bash
pip install python-pptx        # já instalado no ambiente do projeto
```

## Como reconstruir o `.pptx`

A partir da raiz do repositório (`Endo-DSL/`):

```bash
python presentation/build_deck.py
```

Saída esperada:

```
OK: .../presentation/Endo-DSL-Qualificacao.pptx gerado com 36 slides.
```

## Gerar uma prévia em PDF (opcional)

Requer LibreOffice (`soffice`):

```bash
soffice --headless --convert-to pdf \
  --outdir presentation presentation/Endo-DSL-Qualificacao.pptx
```

> Nota: em alguns ambientes headless o filtro de importação do LibreOffice pode
> recusar arquivos `.pptx` (erro "source file could not be loaded"), inclusive
> para arquivos triviais — é uma limitação do ambiente, não do deck. O `.pptx`
> abre normalmente no PowerPoint / Google Slides / LibreOffice Impress GUI.
> Se a conversão falhar, abra o `.pptx` no Impress e exporte via
> *Arquivo → Exportar como → PDF*.

## Estrutura do deck (36 slides)

1. Capa · 2. Agenda · 3. Contexto e motivação · 4. Problema de pesquisa ·
5. Questões (QP1–QP4) · 6. Hipóteses · 7. Objetivos · 8. DSLs ·
9. Taxonomia de Bloom · 10. Game design endógeno · 11. RAG + LLM multi-agente ·
12. Trabalhos relacionados · 13. Lacuna · 14. Visão geral · 15. Arquitetura ·
16. Módulo 1 (DSL/EBNF) · 17. Bloom 1ª classe · 18. Validação + matriz ·
19. Módulo 2 (Biblioteca) · 20. Módulo 3 (Pipeline) · 21. Módulo 4 (Compilador) ·
22. Módulo 5 (Avaliação 7-D) · 23. Jornada do usuário · 24. Interface tipo-Overleaf ·
25. Estudo de caso (Frações) · 26. Design Science Research · 27. Protocolo experimental ·
28. Métricas · 29. Resultados preliminares · 30. Contribuições · 31. Ameaças à validade ·
32. Cronograma (Gantt) · 33. Plano da tese · 34. Conclusão · 35. Referências ·
36. Agradecimento/perguntas.

## Personalização

- Orientador(a): substituir o placeholder `[Prof(a). Orientador(a)]` na função
  `slide_capa()` em `build_deck.py`.
- Cores/tema: constantes no topo de `build_deck.py` (`SLATE`, `INDIGO`, `BLOOM`, …).
- Rodapé: constante `FOOTER`.
