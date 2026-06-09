# Endo-DSL como Tese de Doutorado

> Documento de fundamentação que articula a plataforma **Endo-DSL** como um
> programa de pesquisa de doutorado no Programa de Engenharia de Sistemas e
> Computação (PESC), COPPE/UFRJ. Estruturado como esboço de tese, referencia os
> artefatos reais do repositório.

---

## Título proposto

**"Endo-DSL: uma linguagem de domínio específico estruturada pela Taxonomia de
Bloom para a geração semi-automática e avaliação de jogos educativos endógenos."**

Subtítulo de trabalho: *Da formalização de construtos de game design educacional à
síntese assistida por pipeline multi-agente e à avaliação comparativa
auto × manual.*

---

## 1. Problema de pesquisa

O design de jogos educativos de qualidade é caro, artesanal e fortemente
dependente de especialistas que combinem competências de **game design**,
**pedagogia** e **desenvolvimento de software**. Duas patologias recorrentes
limitam a escala e a qualidade:

1. **Exogeneidade.** Muitos "jogos educativos" justapõem conteúdo e mecânica — um
   quiz envolto em uma fantasia visual — em vez de integrar o aprender ao jogar.
   Falta um arcabouço que torne a **endogeneidade** um requisito verificável.
2. **Informalidade do design.** O conhecimento de design educacional vive em
   documentos e na cabeça de especialistas, não em **modelos formais** que
   permitam verificação, reúso e automação.

Disso decorre o problema central:

> *Como formalizar construtos de game design educacional endógeno, ancorados em
> uma taxonomia cognitiva, de modo a permitir a geração semi-automática de
> protótipos jogáveis cuja qualidade pedagógica seja comparável à de protótipos
> desenvolvidos manualmente — preservando o julgamento humano nos aspectos não
> formalizáveis?*

---

## 2. Questões de pesquisa

- **QP1 — Formalizabilidade.** Quais construtos do design de jogos educacionais
  endógenos são **formalizáveis** em uma gramática computacional, e quais
  dependem de interpretação humana? *(operacionalizada em `endo_dsl/dsl/limits.py`
  e exposta em `endo-dsl limits`.)*
- **QP2 — Bloom como construto de primeira classe.** A Taxonomia de Bloom revisada
  pode ser tratada como **construto de primeira classe** da linguagem, com regras
  de afinidade cognitiva verificáveis por tipo de mecânica? *(grammar.ebnf,
  `MECHANIC_TYPES`, validação semântica RF04.)*
- **QP3 — Geração assistida.** Um **pipeline multi-agente** (recuperação +
  geração + validação + refinamento) é capaz de produzir especificações válidas e
  compiláveis a partir de um contexto educacional? *(módulo `agents/`,
  `endo-dsl generate`.)*
- **QP4 — Comparabilidade.** Protótipos **gerados automaticamente** alcançam
  qualidade pedagógica **comparável** à de protótipos **manuais**, sob um mesmo
  instrumento de avaliação? *(módulo `evaluation/`, `endo-dsl report`.)*
- **QP5 — Reúso e curadoria.** Uma biblioteca de componentes **versionados e
  curados** (canônico/experimental) melhora a qualidade e a reutilização das
  mecânicas ao longo do tempo? *(módulo `library/`, jornada do curador.)*

---

## 3. Hipóteses

- **H1.** Existe um subconjunto não trivial de construtos de game design
  educacional **estruturalmente formalizável** (mecânicas, objetivos, loops,
  ramificações, níveis cognitivos), distinto de um subconjunto **deliberadamente
  humano** (engajamento percebido, tom, estética, adequação cultural).
- **H2.** Tratar Bloom como construto de primeira classe permite **verificar
  automaticamente** a coerência cognitiva entre mecânica e objetivo (afinidade
  Bloom×mecânica).
- **H3.** O pipeline multi-agente gera especificações válidas em **poucas
  tentativas** na maioria dos contextos, com refinamento guiado pelos diagnósticos.
- **H4.** A diferença média de qualidade pedagógica entre protótipos automáticos e
  manuais é **pequena e não significativa** na maioria das dimensões, com a
  endogeneidade preservada.
- **H5.** A curadoria canônico/experimental eleva a **qualidade média** e a taxa de
  sucesso de compilação dos componentes mais utilizados.

---

## 4. Objetivos

**Objetivo geral.** Conceber, implementar e avaliar uma DSL e uma plataforma de
suporte que tornem a Taxonomia de Bloom um construto de primeira classe e
permitam a geração semi-automática e a avaliação comparativa de jogos educativos
endógenos.

**Objetivos específicos.**
1. Definir formalmente a gramática (EBNF) da Endo-DSL e seus limites (QP1).
2. Implementar parser com erros descritivos e validação semântica de coerência
   cognitiva (QP2).
3. Construir uma biblioteca de componentes versionados, com busca multifacetada e
   curadoria (QP5).
4. Projetar um pipeline multi-agente de recuperação–geração–validação–refinamento
   (QP3).
5. Implementar um compilador DSL→HTML5 autocontido, com rastreabilidade e
   reparametrização (QP3).
6. Definir e aplicar um instrumento de avaliação multidimensional e um protocolo
   comparativo auto × manual (QP4).

---

## 5. Justificativa

A relevância é tripla. **Científica:** contribui para a interface entre
Engenharia de Software (DSLs, MDE) e Tecnologias Educacionais ao delimitar
empiricamente o que é formalizável no design educacional. **Técnica:** entrega
uma plataforma stdlib-only, reprodutível e auditável, com compilação para HTML5
sem dependências em runtime — baixando a barreira de adoção em escolas. **Social:**
amplia o acesso a jogos educativos de qualidade ao reduzir o custo de produção,
mantendo o professor no controle das decisões pedagógicas sensíveis.

---

## 6. Fundamentação teórica

### 6.1 Linguagens de domínio específico (DSLs) e MDE
DSLs trocam generalidade por **expressividade no domínio**, elevando o nível de
abstração e habilitando verificação e geração de código. A Endo-DSL é uma DSL
**externa textual** com gramática EBNF (`grammar.ebnf`), parser recursivo
descendente, validação semântica e um compilador (transformação modelo→texto), no
espírito da Engenharia Dirigida por Modelos (MDE).

### 6.2 Taxonomia de Bloom revisada
A taxonomia revisada (Anderson & Krathwohl) organiza processos cognitivos em seis
níveis — Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar. Na Endo-DSL,
esses níveis são **construtos de primeira classe** (não-terminal `bloom`),
exigíveis em qualquer elemento, com **ordem total** e **afinidade** por tipo de
mecânica (verificável em `validate_semantics`).

### 6.3 Game design endógeno
A distinção entre conteúdo **endógeno** (intrínseco às regras) e **exógeno**
(decorativo) é central. A Endo-DSL incorpora a endogeneidade como **dimensão
avaliável** do instrumento (`evaluation/instrument.py`), explicitando-a como
critério de qualidade.

### 6.4 RAG e sistemas multi-agente com LLM
O pipeline combina **recuperação** de componentes (RAG) e **geração** por agentes,
com **refinamento iterativo** guiado por validação. O backend de geração é
opcional: na ausência de chave/LLM, um backend **heurístico determinístico**
mantém a reprodutibilidade — propriedade desejável para experimentação científica.
Quando um provedor LLM é usado, a arquitetura prevê o Claude (Anthropic) via a
variável `ANTHROPIC_API_KEY`/`ENDO_DSL_BACKEND`.

### 6.5 Engenharia de Software baseada em modelos
Rastreabilidade (objetivo→mecânica→Bloom), versionamento de componentes, métricas
de uso e compilação verificável situam o trabalho na tradição de **engenharia
baseada em modelos**, com ênfase em auditabilidade e reprodutibilidade.

---

## 7. Metodologia — Design Science Research (DSR)

Adota-se **Design Science Research**, adequada à criação e avaliação de
**artefatos**. Os ciclos:

- **Relevância.** Problema ancorado na prática docente e na produção de jogos.
- **Design.** Construção dos artefatos: a DSL, a biblioteca, o pipeline, o
  compilador e o instrumento de avaliação.
- **Rigor.** Fundamentação em DSL/MDE, Bloom e game design endógeno.
- **Avaliação.** Estudo comparativo auto × manual com instrumento estruturado e
  análise estatística.

Artefatos como saídas de DSR: a **linguagem** (gramática + semântica), o
**método** (jornada de 7 fases), a **instanciação** (plataforma executável) e o
**instrumento** de avaliação.

---

## 8. Arquitetura da solução e mapeamento aos requisitos (RF01–RF26)

A plataforma divide-se nos módulos `dsl`, `library`, `agents`, `compiler`,
`evaluation`, `platform`, `web` e `cli`. O mapeamento requisito→artefato:

| RF | Requisito | Artefato |
|----|-----------|----------|
| RF01–RF02 | Gramática formal; Bloom 1ª classe | `dsl/grammar.ebnf` |
| RF03–RF05 | Parser com erros; validação; edição ao vivo | `dsl/parser.py`, `dsl/semantic.py`, Estúdio |
| RF06 | Limites da formalização | `dsl/limits.py`, `endo-dsl limits` |
| RF07–RF12 | Biblioteca: criação, refs, versões, métricas, curadoria | `library/` |
| RF13–RF18 | Pipeline: contexto, recuperação, geração, refinamento | `agents/`, `endo-dsl generate` |
| RF19–RF23 | Compilação HTML5; Bloom rastreável; reparametrização; traceability | `compiler/` |
| RF24–RF26 | Instrumento; export CSV; relatório comparativo | `evaluation/`, `endo-dsl report` |

A fachada `endo_dsl/platform.py` materializa a jornada (Fases 1–7) numa API de
alto nível, reaproveitada por CLI e web.

---

## 9. Protocolo de avaliação experimental

**Desenho.** Estudo comparativo **auto × manual** intra-instrumento.

- **Unidades.** Protótipos compilados, rotulados por `origin` (`auto`/`manual`).
- **Instrumento.** `endo-eval-1.0`, **7 dimensões** em Likert 1–5 (atende ao
  espírito de um instrumento Likert detalhado, com 7 dimensões ponderadas):
  alinhamento pedagógico (peso 1.3), coerência cognitiva (1.2), endogeneidade
  (1.3), clareza instrucional (1.0), adequação ao público (1.0), potencial de
  engajamento (1.0), adaptabilidade de conteúdo (0.8).
- **Métricas.** Média ponderada geral; médias por dimensão, por nível de Bloom e
  por domínio; **delta** auto−manual; nº de tentativas de geração; taxa de sucesso
  de compilação por componente (RF11).
- **Procedimento.** (1) Definir contextos-alvo; (2) gerar protótipos automáticos e
  produzir manuais equivalentes; (3) avaliar ambos por múltiplos avaliadores; (4)
  exportar CSV (`report --csv`); (5) testar diferenças por dimensão.
- **Análise.** Comparação de médias por dimensão; relato de deltas e da
  interpretação agregada (módulo `evaluation/reports.py`).

> **Nota sobre a escala.** O instrumento usa Likert 1–5 por **item**, com **7
> dimensões** ponderadas. Caso o comitê requeira escala de **7 pontos**, a
> constante `LIKERT_MAX` em `instrument.py` é o único ponto de ajuste, sem
> alterar o protocolo.

---

## 10. Contribuições esperadas

**Científicas.**
- C1. Delimitação empírica do **formalizável vs. humano** no design educacional (QP1).
- C2. Modelo de **Bloom como construto de primeira classe** com afinidade
  verificável (QP2).
- C3. Evidência comparativa **auto × manual** de qualidade pedagógica (QP4).

**Técnicas.**
- C4. Plataforma **stdlib-only**, reprodutível e auditável.
- C5. Compilador DSL→**HTML5 autocontido** com rastreabilidade e reparametrização.
- C6. Pipeline multi-agente com **backend heurístico determinístico** para
  experimentação reprodutível.

---

## 11. Ameaças à validade

- **Construto.** O instrumento pode não capturar toda a qualidade pedagógica —
  mitigado por dimensões ancoradas (incl. endogeneidade) e por revisão de
  especialistas.
- **Interna.** Viés de avaliador — mitigado por múltiplos avaliadores e rótulos
  cegos sempre que possível.
- **Externa.** Generalização limitada por domínios/contextos amostrados — mitigada
  por variação de domínio e reparametrização.
- **Conclusão.** Tamanho amostral — endereçado por replicação e exportação CSV
  para reanálise.
- **Reprodutibilidade do LLM.** Variabilidade de geração — mitigada pelo backend
  heurístico determinístico como linha de base.

---

## 12. Cronograma (Gantt textual)

```
Ano 1  | T1 | T2 | T3 | T4 |
Lit/QP | ██ | ██ |    |    |
Gram.  |    | ██ | ██ |    |   (RF01–RF06)
Libr.  |    |    | ██ | ██ |   (RF07–RF12)
Ano 2  | T1 | T2 | T3 | T4 |
Pipe.  | ██ | ██ |    |    |   (RF13–RF18)
Comp.  |    | ██ | ██ |    |   (RF19–RF23)
Aval.  |    |    | ██ | ██ |   (RF24–RF26)
Ano 3  | T1 | T2 | T3 | T4 |
Estudo | ██ | ██ |    |    |
Análise|    | ██ | ██ |    |
Escrita|    |    | ██ | ██ |
Defesa |    |    |    | ██ |
```

---

## 13. Mapeamento capítulo-a-capítulo da tese

1. **Introdução.** Problema, QP1–QP5, hipóteses, objetivos, contribuições.
2. **Fundamentação.** DSL/MDE, Bloom revisada, game design endógeno, RAG/LLM
   multi-agente, ESW baseada em modelos.
3. **A linguagem Endo-DSL.** Gramática EBNF, semântica, limites (QP1, QP2) —
   `grammar.ebnf`, `semantic.py`, `limits.py`.
4. **Biblioteca de componentes.** Modelo, versões, métricas, curadoria (QP5) —
   `library/`.
5. **Pipeline multi-agente.** Recuperação, geração, refinamento (QP3) — `agents/`.
6. **Compilação para HTML5.** Content pack, rastreabilidade, reparametrização —
   `compiler/`.
7. **Avaliação pedagógica.** Instrumento, protocolo, relatórios (QP4) —
   `evaluation/`.
8. **Estudo de caso e resultados.** "Comparando Frações" e a análise comparativa.
9. **Discussão.** Ameaças à validade, implicações, limites do formalizável.
10. **Conclusão e trabalhos futuros.** Generalização a outros domínios e níveis.

---

## 14. Síntese

A Endo-DSL articula uma resposta verificável ao problema do design educacional
informal: formaliza o que é formalizável, preserva o julgamento humano onde ele é
insubstituível e fecha o ciclo com avaliação comparativa. O repositório fornece os
artefatos concretos — gramática, biblioteca, pipeline, compilador e instrumento —
que sustentam empiricamente cada questão de pesquisa, qualificando o trabalho como
um programa de doutorado coeso no PESC/COPPE/UFRJ.

---

*Endo-DSL · PESC/COPPE/UFRJ · contato: caiosazeredo@cos.ufrj.br*
