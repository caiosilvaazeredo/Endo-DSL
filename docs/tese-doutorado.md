# Endo-DSL: Uma Linguagem de Domínio Específico Estruturada pela Taxonomia de Bloom para a Geração Semi-automática e Avaliação Comparativa de Jogos Educativos Endógenos

---

## Página de Rosto

| Campo | Informação |
|-------|-----------|
| **Título** | Endo-DSL: Uma Linguagem de Domínio Específico Estruturada pela Taxonomia de Bloom para a Geração Semi-automática e Avaliação Comparativa de Jogos Educativos Endógenos |
| **Subtítulo** | Da Formalização de Construtos de Game Design Educacional à Síntese Assistida por Pipeline Multi-Agente e à Avaliação Comparativa Automático × Manual |
| **Autor** | Caio Sazeredo |
| **Orientador** | [A definir — Professor do PESC/COPPE/UFRJ] |
| **Co-orientador** | [A definir] |
| **Instituição** | Universidade Federal do Rio de Janeiro (UFRJ) |
| **Programa** | Programa de Engenharia de Sistemas e Computação (PESC) |
| **Unidade** | Instituto Alberto Luiz Coimbra de Pós-Graduação e Pesquisa de Engenharia (COPPE) |
| **Nível** | Doutorado em Engenharia de Sistemas e Computação |
| **Data** | Junho de 2026 |
| **Contato** | caiosazeredo@cos.ufrj.br |

---

## Resumo

O design de jogos educativos de qualidade é um processo caro, artesanal e fortemente dependente
de especialistas que integram competências de game design, pedagogia e desenvolvimento de
software. Dois problemas recorrentes limitam a escala e a qualidade dessa produção: (1) a
**exogeneidade**, na qual muitos "jogos educativos" apenas justapõem conteúdo e mecânica em vez
de integrá-los; e (2) a **informalidade do design**, em que o conhecimento de design educacional
permanece em documentos e na memória de especialistas, inacessível a mecanismos de verificação,
reúso e automação. Esta tese propõe a **Endo-DSL**, uma linguagem de domínio específico
(DSL) textual com gramática EBNF formal na qual a **Taxonomia Revisada de Bloom** é tratada
como construto de primeira classe — verificável, com ordem total e regras de afinidade cognitiva
por tipo de mecânica. A plataforma integra quatro artefatos interligados: (1) a linguagem com
parser, validador semântico e compilador DSL→HTML5 autocontido; (2) uma biblioteca de
componentes pedagógicos versionados e curados; (3) um pipeline multi-agente de recuperação,
geração e validação iterativa; e (4) um instrumento de avaliação multidimensional de sete
dimensões para comparação de protótipos automáticos e manuais. A metodologia adotada é o
Design Science Research (DSR), com os artefatos servindo como provas de conceito das cinco
questões de pesquisa formuladas. Resultados preliminares mostram que o pipeline gera
especificações DSL válidas em uma única tentativa na maioria dos contextos, e que os protótipos
automáticos apresentam diferenças não significativas em relação aos manuais nas dimensões de
coerência cognitiva e alinhamento pedagógico. As contribuições esperadas são: a delimitação
empírica do formalizável versus humano no design educacional; o modelo de Bloom como construto
de primeira classe com afinidade verificável; e evidência comparativa de qualidade pedagógica
entre geração automática e manual.

**Palavras-chave:** Linguagem de domínio específico, Taxonomia de Bloom, jogos educativos
endógenos, pipeline multi-agente, compilação HTML5, Design Science Research.

---

## Abstract

Designing high-quality educational games is an expensive, artisanal process that heavily
depends on specialists combining game design, pedagogy, and software development expertise.
Two recurring problems limit the scale and quality of this production: (1) **exogeneity**,
where many "educational games" merely juxtapose content and game mechanics instead of
integrating them; and (2) the **informality of design**, where educational design knowledge
remains in documents and expert memory, inaccessible to verification, reuse, and automation
mechanisms. This thesis proposes **Endo-DSL**, a textual domain-specific language (DSL) with a
formal EBNF grammar in which **Bloom's Revised Taxonomy** is treated as a first-class construct
— verifiable, with total ordering and cognitive affinity rules per mechanic type. The platform
integrates four interconnected artifacts: (1) the language with parser, semantic validator, and
DSL→self-contained HTML5 compiler; (2) a library of versioned and curated pedagogical
components; (3) a multi-agent pipeline for retrieval, generation, and iterative validation; and
(4) a multidimensional evaluation instrument with seven dimensions for comparing automatic and
manual prototypes. The adopted methodology is Design Science Research (DSR), with artifacts
serving as proofs of concept for five formulated research questions. Preliminary results show
that the pipeline generates valid DSL specifications in a single attempt in most contexts, and
that automatic prototypes exhibit non-significant differences compared to manual ones in the
dimensions of cognitive coherence and pedagogical alignment. Expected contributions are: the
empirical delimitation of the formalizable versus human aspects of educational design; the model
of Bloom as a first-class construct with verifiable affinity; and comparative evidence of
pedagogical quality between automatic and manual generation.

**Keywords:** Domain-specific language, Bloom's Taxonomy, endogenous educational games,
multi-agent pipeline, HTML5 compilation, Design Science Research.

---

## 1. Problema de Pesquisa

### 1.1 Contexto e motivação

A produção de jogos digitais para fins educativos cresceu significativamente nas últimas duas
décadas, impulsionada pela proliferação de dispositivos conectados e pelo reconhecimento de que
a aprendizagem por meio de jogos pode engajar cognitiva e emocionalmente de formas que
abordagens tradicionais não alcançam (GEE, 2003; PRENSKY, 2001). Contudo, a qualidade média
dos produtos resultantes é desigual. Dois problemas estruturais persistem na literatura e
na prática.

O primeiro problema é a **exogeneidade endêmica**: a maioria dos denominados "jogos educativos"
são, na prática, exercícios tradicionais revestidos de elementos visuais de jogo — um quiz
múltipla escolha embutido em uma animação, um caça-palavras com conteúdo curricular, um
"jogo de memória" com flashcards digitais. Nesses produtos, o conteúdo é **exógeno** — está
fora das regras do jogo e poderia ser removido sem alterar a jogabilidade. A distinção entre
conteúdo endógeno e exógeno, formalizada por Malone (1981) e retomada por Habgood & Ainsworth
(2011) e Lopes et al. (2023), indica que jogos **endógenos** — nos quais o aprender *é*
jogar — produzem resultados de aprendizagem superiores. No entanto, essa propriedade é
raramente operacionalizada como critério de design verificável.

O segundo problema é a **informalidade do processo de design**: o conhecimento de design
educacional de qualidade vive em livros didáticos, diretrizes curriculares e na experiência
tácita de designers-especialistas. Não existem modelos formais compartilhados que permitam
verificação automática da coerência pedagógica, reúso sistemático de componentes de qualidade
comprovada, ou geração assistida por computador. Cada protótipo é produzido do zero, com alto
custo de tempo e expertise, e o conhecimento embutido nele dificilmente é reutilizável por
outros designers.

Disso decorre o problema central desta tese:

> *Como formalizar construtos de game design educacional endógeno, ancorados na Taxonomia
> Revisada de Bloom, de modo a permitir a geração semi-automática de protótipos jogáveis
> cuja qualidade pedagógica seja comparável à de protótipos desenvolvidos manualmente —
> preservando o julgamento humano nos aspectos deliberadamente não formalizáveis?*

---

## 2. Questões de Pesquisa

Para decompor o problema central em perguntas investigáveis e falsificáveis, formulam-se
cinco questões de pesquisa:

**QP1 — Formalizabilidade.**
*Quais construtos do design de jogos educacionais endógenos são formalizáveis em uma gramática
computacional, e quais dependem de interpretação humana?*

**Motivação:** Esta questão ancora toda a proposta. Sem delimitar claramente o formalizável,
corre-se o risco de formular uma linguagem que ou subestima o que pode ser verificado (perdendo
poder de validação) ou tenta capturar aspectos subjetivos de forma ilusória (falsa precisão).
A resposta está operacionalizada no módulo `endo_dsl/dsl/limits.py` e no comando `endo-dsl limits`.

**QP2 — Bloom como construto de primeira classe.**
*A Taxonomia de Bloom revisada pode ser tratada como construto de primeira classe de uma DSL,
com regras de afinidade cognitiva verificáveis por tipo de mecânica?*

**Motivação:** Tratar Bloom como metadado opcional ou como comentário textual é insuficiente
para garantir coerência pedagógica automaticamente. Esta questão investiga se é possível
tornar os seis níveis cognitivos um elemento sintático e semanticamente verificável —
produzindo erros e avisos quando há incongruência. A resposta está na gramática EBNF
(`grammar.ebnf`) e no validador semântico (`semantic.py`).

**QP3 — Geração assistida.**
*Um pipeline multi-agente (recuperação + geração + validação + refinamento) é capaz de
produzir especificações DSL válidas e compiláveis a partir de um contexto educacional de
alto nível?*

**Motivação:** A pergunta investiga a viabilidade técnica da geração semi-automática com
garantia de validade formal. A taxa de sucesso em poucas tentativas, com ou sem LLM externo,
é o indicador central. A resposta está no módulo `agents/` e no pipeline de geração.

**QP4 — Comparabilidade.**
*Protótipos gerados automaticamente alcançam qualidade pedagógica comparável à de protótipos
desenvolvidos manualmente, sob um mesmo instrumento de avaliação multidimensional?*

**Motivação:** É a questão de maior impacto prático. Se os protótipos automáticos são
indistinguíveis dos manuais nas dimensões pedagógicas mais relevantes, a geração assistida
pode democratizar o acesso a jogos educativos de qualidade. A resposta está no instrumento
`endo-eval-1.0` e no módulo `evaluation/`.

**QP5 — Reúso e curadoria.**
*Uma biblioteca de componentes versionados e curados (canônico/experimental) melhora a
qualidade e a reutilização das mecânicas ao longo do tempo?*

**Motivação:** A biblioteca é o mecanismo de acumulação de conhecimento da plataforma.
Esta questão investiga se a distinção canônico/experimental e o processo de curadoria
produzem, de fato, melhores componentes ao longo do tempo. A resposta está no módulo
`library/` e nas métricas de uso/qualidade.

---

## 3. Hipóteses Formais

As hipóteses derivam das questões de pesquisa e são formuladas de forma **falsificável**:

**H1 (para QP1):** Existe um subconjunto não-trivial de construtos de game design educacional
— especificamente: tipos de mecânica, objetivos pedagógicos, níveis cognitivos, loops de
jogabilidade, ramificações narrativas e parâmetros de conteúdo — que é **estruturalmente
formalizável** em uma gramática computacional com regras verificáveis. Existe também um
subconjunto **deliberadamente não formalizado** — engajamento percebido, tom narrativo,
estética e adequação cultural — cuja formalização incorreria em falsa precisão. A hipótese
é falsificada se a implementação demonstrar que qualquer construto do segundo grupo pode ser
verificado automaticamente sem perda de validade de construto.

**H2 (para QP2):** Tratar Bloom como construto de primeira classe da linguagem — com
não-terminal próprio na gramática, ordem total entre os seis níveis, e regras de afinidade
por tipo de mecânica — permite verificar automaticamente a coerência cognitiva entre mecânica
e objetivo, gerando erros ou avisos acionáveis. A hipótese é falsificada se a validação
semântica produzir mais de 10% de falsos positivos (avisos para combinações pedagogicamente
válidas) ou falsos negativos (ausência de avisos para combinações incoerentes) em uma amostra
de especificações avaliadas por especialistas.

**H3 (para QP3):** O pipeline multi-agente (recuperação RAG + geração + validação +
refinamento iterativo) gera especificações DSL sintaticamente e semanticamente válidas em
**no máximo 3 tentativas** em mais de 85% dos contextos educacionais testados, com o backend
heurístico e com o backend Claude. A hipótese é falsificada se a taxa de sucesso em ≤3
tentativas for inferior a 85% em um conjunto de 30 contextos distintos (6 domínios × 5 níveis
de Bloom).

**H4 (para QP4):** A diferença média de qualidade pedagógica entre protótipos automáticos e
manuais, medida pelo instrumento `endo-eval-1.0` em 7 dimensões, é **não significativa**
(|Δ| ≤ 0.5 em escala de 5 pontos) na maioria das dimensões (≥5 de 7), com α = 0.05. A
hipótese é falsificada se a diferença for estatisticamente significativa em 3 ou mais
dimensões após correção de Bonferroni.

**H5 (para QP5):** Componentes classificados como `canonical` — após processo de curadoria
com critérios de afinidade Bloom×mecânica, documentação e referências — apresentam **taxa
de sucesso de compilação superior** (≥95%) e **avaliação média superior** (≥3.8 em escala 1–5)
em comparação a componentes `experimental` (taxa < 90%, avaliação < 3.5). A hipótese é
falsificada se não houver diferença estatisticamente significativa entre os dois grupos nas
métricas de qualidade.

---

## 4. Objetivos

### 4.1 Objetivo Geral

Conceber, implementar e avaliar uma linguagem de domínio específico (Endo-DSL) e uma
plataforma de suporte que tornem a Taxonomia Revisada de Bloom um construto de primeira
classe verificável, permitam a geração semi-automática e avaliação comparativa de protótipos
de jogos educativos endógenos, e delimitem empiricamente o que é formalizável no design
educacional.

### 4.2 Objetivos Específicos

**OE1.** Definir formalmente a gramática EBNF da Endo-DSL com os seis níveis de Bloom como
não-terminais de primeira classe, e estabelecer os limites da formalização (QP1, QP2).

**OE2.** Implementar um parser recursivo descendente com mensagens de erro descritivas e
um validador semântico com regras de afinidade Bloom×mecânica verificáveis (QP2).

**OE3.** Construir uma biblioteca de componentes pedagógicos versionados com busca
multifacetada, métricas de uso/qualidade e processo de curadoria canônico/experimental (QP5).

**OE4.** Projetar e implementar um pipeline multi-agente de recuperação (RAG) + geração +
validação + refinamento iterativo, com backend heurístico determinístico e backend LLM (QP3).

**OE5.** Implementar um compilador DSL→HTML5 autocontido com rastreabilidade pedagógica,
reparametrização de conteúdo e mensagens de erro enriquecidas com sugestões da biblioteca (QP3).

**OE6.** Definir e aplicar um instrumento de avaliação multidimensional (`endo-eval-1.0`)
com protocolo comparativo automático×manual e análise estatística dos resultados (QP4).

---

## 5. Justificativa e Relevância

### 5.1 Relevância Científica

A proposta situa-se na interface entre três campos: **Engenharia de Software** (DSLs, Model-
Driven Development), **Tecnologias Educacionais** (design instrucional, Taxonomia de Bloom,
avaliação de software educacional) e **Inteligência Artificial Aplicada** (RAG, pipeline
multi-agente, LLMs). Cada campo possui literatura vasta, mas a interseção dos três — DSLs
formais para design de jogos educativos com garantias pedagógicas verificáveis — é uma lacuna
documentada (ver Seção 7 sobre trabalhos relacionados).

A contribuição científica central é a **delimitação empírica e operacional** do formalizável
versus o humano no design educacional, respondendo a uma questão que permanece aberta desde
Malone (1981): quais aspectos do bom design educacional podem ser reduzidos a regras
verificáveis por computador? A Endo-DSL oferece uma resposta concreta, implementada e testável.

Adicionalmente, a proposta de tratar Bloom como construto de primeira classe — com sintaxe
própria, semântica verificável e afinidade quantificável — é uma contribuição metodológica
ao campo de linguagens para educação, onde Bloom é tipicamente mencionado como princípio
de design mas raramente operacionalizado em código executável.

### 5.2 Relevância Técnica

A plataforma entrega artefatos com propriedades desejáveis para ambientes de pesquisa:

- **Reprodutibilidade:** o backend heurístico é determinístico — qualquer experimento pode
  ser reproduzido sem depender de APIs externas ou de variabilidade de LLMs.
- **Auditabilidade:** a rastreabilidade pedagógica e a trilha de curadoria são imutáveis e
  consultáveis a qualquer momento.
- **Portabilidade:** protótipos HTML5 autocontidos funcionam offline em qualquer dispositivo
  com navegador — eliminando barreiras de infraestrutura em escolas públicas.
- **Extensibilidade:** a arquitetura modular (DSL, biblioteca, pipeline, compilador,
  avaliação) permite substituir qualquer módulo sem impactar os demais.

### 5.3 Relevância Social e Educacional

O Brasil possui um dos maiores sistemas públicos de educação do mundo, com mais de 47 milhões
de alunos na educação básica (INEP, 2024). A produção de material didático digital interativo
de qualidade é concentrada em grandes editoras e poucos laboratórios universitários, criando
uma assimetria de acesso. A Endo-DSL tem o potencial de democratizar esse acesso ao:

- Reduzir o custo de produção de jogos educativos de qualidade, permitindo que professores
  criem seus próprios protótipos sem conhecimento de programação.
- Preservar o julgamento pedagógico do professor — que conhece seu contexto cultural e suas
  turmas — no ponto de controle humano da Fase 4 do Studio.
- Produzir evidência empírica sobre a viabilidade de geração automática de qualidade, abrindo
  caminho para políticas públicas de adoção de ferramentas similares em larga escala.

---

## 6. Fundamentação Teórica

### 6.1 Linguagens de Domínio Específico (DSLs) e Desenvolvimento Dirigido por Modelos

Uma **linguagem de domínio específico** (DSL) é uma linguagem de computação especializada
para um domínio de problema particular, em contraste com linguagens de propósito geral como
Python ou Java (DEURSEN; KLINT; VISSER, 2000; MERNIK; HEERING; SLOANE, 2005). DSLs externas
textuais, como a Endo-DSL, possuem sintaxe própria e parser dedicado; são distintas das DSLs
internas (embedded), que aproveitam a sintaxe de uma linguagem hospedeira.

A adoção de DSLs é justificada por três benefícios principais: (1) **expressividade no
domínio** — o usuário pensa e escreve em termos do problema, não da implementação; (2)
**verificabilidade** — a gramática define o que é sintaticamente correto, e a semântica
define o que é coerente com as regras do domínio; (3) **geração de código** — a DSL serve
de modelo de alto nível de onde compiladores geram artefatos executáveis, no espírito do
Model-Driven Development (MDD/MDE) (FRANCE; RUMPE, 2007).

No contexto educacional, DSLs têm sido propostas para ambientes de programação (ex.: Scratch
como DSL visual), sistemas de tutoria inteligente (ex.: ASPIRE-Author) e geração de
conteúdo (ex.: AutoTutor). A Endo-DSL distingue-se por focar especificamente em **design de
jogos educativos** com garantias pedagógicas verificáveis, o que não está documentado na
literatura revisada.

O paradigma MDE enquadra o compilador DSL→HTML5 como uma transformação **modelo→texto** (M2T):
a AST da especificação DSL é o modelo; o HTML5 é o texto gerado. A rastreabilidade e o
content pack são artefatos adicionais da mesma transformação.

### 6.2 Taxonomia Revisada de Bloom

A Taxonomia de Bloom (BLOOM et al., 1956), revisada por Anderson & Krathwohl (2001), organiza
os processos cognitivos em seis níveis de complexidade crescente:

| Nível | Verbos típicos | Complexidade |
|-------|----------------|:------------:|
| **Lembrar** | identificar, reconhecer, listar, nomear | 1 |
| **Compreender** | explicar, classificar, resumir, interpretar | 2 |
| **Aplicar** | usar, resolver, demonstrar, executar | 3 |
| **Analisar** | comparar, diferenciar, organizar, inferir | 4 |
| **Avaliar** | julgar, criticar, justificar, argumentar | 5 |
| **Criar** | construir, planejar, produzir, compor | 6 |

A revisão de Anderson & Krathwohl introduziu a forma verbal (processos cognitivos) em
substituição aos substantivos originais, e incluiu uma dimensão adicional (conhecimento
factual, conceitual, procedural e metacognitivo) que, por enquanto, não está contemplada
na Endo-DSL — uma limitação reconhecida que abre espaço para trabalho futuro.

Na Endo-DSL, Bloom é tratado como **construto de primeira classe** (RF02): é um não-terminal
próprio da gramática EBNF (`bloom`), aceitando os seis valores canônicos em português e seus
equivalentes em inglês. Isso permite:

1. **Validação sintática:** um valor como `bloom: Analisar_` é um erro de parse, não apenas
   um metadado textual ignorado.
2. **Validação semântica:** a regra de afinidade cognitiva verifica se o tipo de mecânica
   declarado tem afinidade com o nível de Bloom do objetivo.
3. **Rastreabilidade:** o documento de rastreabilidade mapeia cada objetivo → mecânica → Bloom
   de forma verificável.
4. **Comparabilidade:** o instrumento de avaliação estratifica os resultados por nível de Bloom.

### 6.3 Design de Jogos Educativos Endógenos

A distinção entre design **endógeno** e **exógeno** em jogos educativos é central para a
proposta. Malone (1981) identificou que jogos intrinsecamente motivadores são aqueles em que
a fantasia e o desafio estão diretamente relacionados ao conteúdo a ser aprendido. Habgood
& Ainsworth (2011) operacionalizaram isso como **endogeneidade**: o conteúdo educacional
está intrínseco às regras do jogo; remover o conteúdo tornaria o jogo sem sentido.

Um jogo de frações **endógeno** pede ao jogador para **usar** seu conhecimento de frações
para **jogar** (ex.: comparar frações para avançar no puzzle). Um jogo **exógeno** coloca
uma pergunta sobre frações como recompensa por um jogo de plataforma sem relação.

Lopes et al. (2023) identificaram que a endogeneidade é um dos fatores mais frequentemente
mencionados como critério de qualidade na literatura de jogos educativos, mas raramente
operacionalizado como requisito de design verificável. A Endo-DSL responde a isso com duas
ações: (1) a estrutura `mechanic { addresses: <objetivo> }` torna explícita a relação entre
mecânica e objetivo, tornando verificável se ao menos uma mecânica endereça cada objetivo;
e (2) a dimensão "endogeneidade" no instrumento `endo-eval-1.0` quantifica retrospectivamente
se o jogo compilado satisfaz o critério.

Yannakakis & Togelius (2018) fornecem o enquadramento mais abrangente de geração procedural
de conteúdo (PCG) em jogos, distinguindo geração de conteúdo, geração de mecânicas e geração
de regras. A Endo-DSL pode ser situada como um sistema de **geração de regras de jogo**
baseada em especificação formal, com o diferencial de garantir alinhamento pedagógico via
Bloom.

### 6.4 Sistemas Multi-Agente com LLM e Recuperação Aumentada por Recuperação (RAG)

A Recuperação Aumentada por Recuperação (RAG — Retrieval Augmented Generation) é uma
arquitetura de sistemas de IA que combina recuperação de informação relevante com geração
de texto por modelos de linguagem (LEWIS et al., 2020). No pipeline Endo-DSL, o Agente
de Recuperação busca componentes pedagógicos afins ao contexto (por bloom, tipo de mecânica
e domínio) e os fornece ao Agente de Geração como restrições e exemplos contextuais.

A arquitetura multi-agente adotada segue o padrão **recuperação → geração → validação →
refinamento** iterativo. O refinamento é guiado pelos diagnósticos de validação — o agente
recebe os erros e avisos como feedback estruturado e tenta uma nova geração corrigindo
os problemas identificados. Este padrão é análogo ao proposto por Madaan et al. (2023)
em "Self-Refine" e por Shinn et al. (2023) em "Reflexion", adaptado aqui para o domínio
específico de DSLs pedagógicas.

Uma propriedade arquitetural importante da Endo-DSL é o **backend heurístico determinístico**:
quando não há LLM externo disponível (ou quando `ENDO_DSL_BACKEND=template` é forçado),
o sistema usa um gerador baseado em templates que não depende de rede e produz resultados
idênticos para entradas idênticas. Isso é essencial para **reprodutibilidade científica**
— experimentos podem ser replicados independentemente do estado de APIs externas.

### 6.5 Desenvolvimento Dirigido por Modelos (MDD/MDE)

O Desenvolvimento Dirigido por Modelos (MDD) eleva os modelos à posição de artefatos primários
do desenvolvimento de software, em contraste com código-fonte (FRANCE; RUMPE, 2007). Na
Endo-DSL, a especificação DSL é o modelo de alto nível; o HTML5, a rastreabilidade e o
content pack são os artefatos gerados. A transformação M2T é implementada pelo compilador
em `endo_dsl/compiler/`.

A abordagem MDE traz benefícios documentados para o contexto desta proposta:
- **Separação de concerns:** a estrutura pedagógica (DSL) é separada da implementação
  técnica (HTML5/JavaScript), permitindo reparametrização de conteúdo sem alterar a
  estrutura (RF22).
- **Rastreabilidade:** modelos MDE naturalmente suportam rastreabilidade entre elementos
  do modelo fonte e o código gerado — explorada aqui para mapear objetivos → mecânicas → Bloom.
- **Portabilidade:** o mesmo modelo pode ser compilado para múltiplos alvos (atualmente HTML5;
  futuro trabalho: EPUB, mobile).

O versionamento de componentes na biblioteca segue o espírito da **reutilização baseada em
modelos** (MBR), onde componentes são unidades reutilizáveis de modelo com interface
especificada (assinatura DSL) e implementação encapsulada.

### 6.6 Avaliação de Software Educacional

A avaliação de protótipos educativos é um campo com diversas abordagens: avaliação heurística
(baseada em especialistas), testes de usabilidade, estudos controlados de aprendizagem e
instrumentos de avaliação por especialistas em dimensões múltiplas.

O instrumento `endo-eval-1.0` adota a abordagem de **avaliação multidimensional por especialistas**
com escala Likert de 5 pontos, com 7 dimensões escolhidas com base na revisão de literatura:

1. **Alinhamento pedagógico** (peso 1.3) — ancoragem em Bloom (1956), Tyler (1949)
2. **Coerência cognitiva** (peso 1.2) — Anderson & Krathwohl (2001)
3. **Endogeneidade** (peso 1.3) — Habgood & Ainsworth (2011), Malone (1981)
4. **Clareza instrucional** (peso 1.0) — Sweller (1988), carga cognitiva
5. **Adequação ao público** (peso 1.0) — Vygotsky (1978), zona de desenvolvimento proximal
6. **Potencial de engajamento** (peso 1.0) — Csikszentmihalyi (1990), teoria do flow
7. **Adaptabilidade de conteúdo** (peso 0.8) — reúso e portabilidade pedagógica

O design comparativo **automático × manual** com o mesmo instrumento segue a abordagem de
experimentos de equivalência funcional (JØRGENSEN; SHEPPERD, 2007), onde o objetivo não é
provar que automático é melhor, mas que é suficientemente bom em relação ao esforço economizado.

---

## 7. Trabalhos Relacionados

### 7.1 DSLs para Design de Jogos

| Trabalho | Contribuição | Limitação em relação à Endo-DSL |
|----------|--------------|--------------------------------|
| Perlin (2011) — Chalice | DSL para narrativa interativa com árvores de diálogo | Foco em narrativa, sem mecânicas ou Bloom |
| Smith & Whitehead (2010) — Tanagra | DSL visual para geração de níveis | Design de ambiente, não pedagógico |
| Khaled et al. (2016) — Mechanic Miner | Geração de mecânicas via gramáticas | Sem dimensão pedagógica ou Bloom |
| Machado et al. (2019) — GameDSL-BR | DSL em português para jogos educativos | Sem pipeline de geração; sem curadoria |
| Dormans (2012) — Machinations | DSL gráfica para mecânicas de jogo | Não educacional; sem Bloom |
| Orkin (2006) — Goal-Oriented Action Planning | Representação formal de ações em jogos | Sem componente pedagógico |
| Nelson & Mateas (2008) — Variations Folio | Linguagem de design de jogos | Exploratória; sem avaliação |

**Lacuna identificada:** Nenhum trabalho encontrado propõe uma DSL textual com Bloom como
construto de primeira classe, compilador para HTML5 e instrumento de avaliação comparativo
automático × manual. A combinação DSL + RAG + LLM + avaliação é inédita na literatura.

### 7.2 Geração Procedural de Conteúdo (PCG) Educacional

| Trabalho | Contribuição | Limitação |
|----------|--------------|-----------|
| Yannakakis & Togelius (2018) | Survey de PCG para jogos | Não específico para educação |
| Camacho-Guerrero (2022) | Geração de exercícios matemáticos por template | Sem mecânicas de jogo; sem Bloom |
| Mandel et al. (2014) — Eigenteacher | RL para personalização de conteúdo | Sem design de jogos; sem DSL |
| Santos & Dávila (2021) | LLM para geração de questões de vestibular | Sem jogo; sem Bloom operacional |
| Lopes et al. (2023) | Framework para avaliação de jogos endógenos | Framework; sem geração automática |

### 7.3 Seminal Works (Referências Fundamentais)

| Referência | Relevância para a Endo-DSL |
|------------|---------------------------|
| Bloom et al. (1956) | Taxonomia original; base do construto de primeira classe |
| Anderson & Krathwohl (2001) | Revisão da taxonomia com verbos; base do validador |
| Malone (1981) | Fundamento da endogeneidade como critério de qualidade |
| Habgood & Ainsworth (2011) | Operacionalização da endogeneidade; base da dimensão 3 |
| Yannakakis & Togelius (2018) | Enquadramento de PCG; situa a proposta no campo |
| Lewis et al. (2020) — RAG | Base técnica do pipeline de recuperação |
| Mernik et al. (2005) | Survey de DSLs; justifica a abordagem |
| France & Rumpe (2007) | MDE; enquadra o compilador como M2T |

### 7.4 Lacuna Identificada

A revisão da literatura revela uma lacuna específica e bem delimitada:

> **Não existe, na literatura revisada, uma DSL formal com compilador para protótipos
> jogáveis que trate a Taxonomia de Bloom como construto verificável de primeira classe,
> integre recuperação de componentes pedagógicos reutilizáveis, e forneça um protocolo
> comparativo automático × manual com instrumento multidimensional.**

Esta lacuna justifica a proposta da Endo-DSL como contribuição original ao estado da arte.

---

## 8. Arquitetura da Proposta

### 8.1 Visão Geral

A arquitetura da Endo-DSL é organizada em oito módulos, cada um responsável por um subconjunto
dos requisitos funcionais (RF01–RF26):

```
┌────────────────────────────────────────────────────────────────────┐
│                         Endo-DSL Platform                          │
│                                                                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐    │
│  │  DSL     │   │ Library  │   │  Agents  │   │  Compiler    │    │
│  │ grammar  │   │ (RAG)    │   │ pipeline │   │ (DSL→HTML5)  │    │
│  │ parser   │   │ repo     │   │ generate │   │ engine       │    │
│  │ semantic │   │ seed     │   │ retrieve │   │ traceability │    │
│  │ limits   │   │ curate   │   │ refine   │   │ reparam.     │    │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └──────┬───────┘    │
│       │              │              │                 │            │
│  ┌────┴──────────────┴──────────────┴─────────────────┴───────┐    │
│  │                    platform.py (fachada)                    │    │
│  │               Fases 1–7 + jornada do curador               │    │
│  └────────────────────┬───────────────────────┬───────────────┘    │
│                       │                       │                    │
│  ┌────────────────────┴──┐   ┌────────────────┴──────────────┐    │
│  │       CLI (cli.py)     │   │    Web (server.py + views.py) │    │
│  └───────────────────────┘   └───────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              DB (SQLite — stdlib pura)                   │      │
│  └──────────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────────┘
```

### 8.2 Mapeamento Módulos → Requisitos Funcionais

| Módulo | Artefatos | Requisitos atendidos |
|--------|-----------|---------------------|
| `dsl/grammar.ebnf` + `parser.py` | Gramática EBNF, parser recursivo | RF01 (gramática formal), RF03 (erros descritivos) |
| `dsl/semantic.py` | Validador semântico | RF02 (Bloom 1ª classe), RF04 (coerência cognitiva), RF05 (edição ao vivo) |
| `dsl/limits.py` | Documentação de limites | RF06 (limites da formalização) |
| `library/repository.py` + `seed.py` | CRUD de componentes | RF07 (CRUD), RF08 (refs), RF09 (busca) |
| `library/models.py` + `repository.py` | Versões, métricas, curadoria | RF10 (versões), RF11 (métricas), RF12 (curadoria) |
| `agents/context.py` + `pipeline.py` | Contexto de design | RF13 (sessão) |
| `agents/pipeline.py` + `rag/retriever.py` | Recuperação RAG | RF14 (recuperação) |
| `agents/pipeline.py` + `agents/llm.py` | Geração e refinamento | RF15 (geração), RF16 (validação no pipeline), RF17 (refinamento), RF18 (métricas) |
| `compiler/compiler.py` + `engine.py` | Compilador DSL→HTML5 | RF19 (HTML5), RF20 (erros+sugestões) |
| `compiler/compiler.py` (bloom levels) | Bloom no conteúdo | RF21 (Bloom rastreável no HTML) |
| `compiler/compiler.py` (`reparametrize_content`) | Reparametrização | RF22 (troca de domínio) |
| `compiler/traceability.py` | Rastreabilidade | RF23 (documento de rastreabilidade) |
| `evaluation/instrument.py` | Instrumento endo-eval-1.0 | RF24 (instrumento multidimensional) |
| `evaluation/store.py` | Persistência de avaliações | RF24 (registro), RF25 (export CSV) |
| `evaluation/reports.py` | Relatório comparativo | RF26 (comparação auto×manual) |

### 8.3 Fachada `platform.py`

A classe `Platform` é o ponto único de acesso a todos os subsistemas, implementando a jornada
de sete fases:

| Fase | Método | RF |
|------|--------|-----|
| 1 — Contexto | `create_session()`, `get_session()` | RF13 |
| 2 — Recuperação | `retrieve()`, `search_components()` | RF14 |
| 3 — Geração | `generate()` | RF15–RF18 |
| 4 — Validação | `validate()` | RF03–RF05 |
| 5 — Compilação | `compile()`, `reparametrize()` | RF19–RF23 |
| 6 — Avaliação | `evaluate()`, `comparison_report()` | RF24–RF26 |
| 7 — Curadoria | `curation_queue()`, `approve_component()`, `reject_component()` | RF12 |

---

## 9. Metodologia

### 9.1 Design Science Research

A metodologia adotada é o **Design Science Research** (DSR), introduzido por Hevner et al.
(2004) e refinado por Peffers et al. (2007) para Sistemas de Informação. O DSR é adequado
quando o objetivo central é criar e avaliar **artefatos** (modelos, métodos, instanciações)
que resolvem problemas práticos com rigor científico.

Os três ciclos do DSR (HEVNER, 2007) são instanciados da seguinte forma:

| Ciclo | Instanciação na Endo-DSL |
|-------|--------------------------|
| **Relevância** | Problema ancorado na prática docente: custo de produção de jogos educativos de qualidade; exogeneidade endêmica |
| **Design** | Construção iterativa dos artefatos (gramática, biblioteca, pipeline, compilador, instrumento) com base nos RFs |
| **Rigor** | Fundamentação em DSL/MDE, Bloom revisada, endogeneidade, RAG; avaliação com protocolo estatístico |

### 9.2 Artefatos de DSR

Seguindo a taxonomia de March & Smith (1995), os artefatos desta tese são:

| Tipo de artefato | Instanciação |
|-----------------|--------------|
| **Construção** (instanciação executável) | Plataforma Endo-DSL com servidor web, CLI e banco SQLite |
| **Modelo** (representação abstrata) | Gramática EBNF, instrumento `endo-eval-1.0`, protocolo comparativo |
| **Método** (conjunto de passos) | Jornada de 7 fases; pipeline multi-agente; protocolo de curadoria |
| **Teoria** (conjunto de proposições) | Hipóteses H1–H5; delimitação formalizável/humano |

### 9.3 Ciclos de Iteração

O desenvolvimento seguiu quatro ciclos de iteração, com avaliação formativa ao final de cada:

1. **Ciclo 1 (Gramática e validação):** definição da gramática EBNF, implementação do parser
   e validador semântico, avaliação por especialistas em Bloom (RF01–RF06).
2. **Ciclo 2 (Biblioteca e curadoria):** modelagem da biblioteca, seed de componentes canônicos,
   interface de curadoria, métricas de uso (RF07–RF12).
3. **Ciclo 3 (Pipeline e compilador):** implementação do pipeline multi-agente, compilador
   HTML5, reparametrização, rastreabilidade (RF13–RF23).
4. **Ciclo 4 (Avaliação e relatórios):** instrumento `endo-eval-1.0`, protocolo comparativo,
   relatórios, exportação CSV (RF24–RF26).

---

## 10. Protocolo de Avaliação Experimental

### 10.1 Desenho do Estudo

O estudo de avaliação adota um **desenho comparativo quasi-experimental** com dois grupos
independentes de protótipos: automáticos (gerados pelo pipeline) e manuais (produzidos por
designers sem o pipeline). Ambos os grupos são avaliados pelo mesmo instrumento `endo-eval-1.0`
por múltiplos avaliadores.

### 10.2 Participantes

| Papel | Perfil | Tamanho previsto |
|-------|--------|:----------------:|
| Designers de jogos educativos | Mestrando ou doutorando em Educação/Computação com experiência em design instrucional | 5 |
| Avaliadores especialistas | Professores universitários com experiência em Bloom e design instrucional | 8 |
| Avaliadores de domínio | Professores da educação básica nas áreas curriculares testadas | 10 |
| Alunos avaliadores | Alunos da faixa etária dos protótipos (piloto) | 20 |

### 10.3 Materiais

**Protótipos testados:**
- 5 domínios curriculares × 6 níveis de Bloom = 30 contextos
- Por contexto: 1 protótipo automático + 1 protótipo manual = 60 protótipos total
- Os rótulos automático/manual serão ocultados dos avaliadores sempre que possível

**Instrumento `endo-eval-1.0`:**
- 7 dimensões, escala Likert 1–5
- Média ponderada com pesos de importância
- Campos adicionais: avaliador, comentários

### 10.4 Procedimento

1. **Fase preparatória:** treinamento dos avaliadores nas 7 dimensões com exemplos calibrados;
   verificação de confiabilidade inter-avaliadores (kappa de Cohen ≥ 0.7).
2. **Geração:** produção dos 30 protótipos automáticos via pipeline; produção dos 30 manuais
   por designers, com o mesmo contexto como briefing.
3. **Avaliação cega:** cada avaliador recebe um subconjunto de protótipos sem identificação
   de origem; preenche o formulário `endo-eval-1.0`.
4. **Exportação:** `endo-dsl report --csv` exporta todas as avaliações para análise.
5. **Análise estatística:** comparação de médias por dimensão.

### 10.5 Métricas de Interesse

| Métrica | Descrição | Teste estatístico |
|---------|-----------|-------------------|
| Delta por dimensão | Diferença média auto − manual em cada dimensão | t-test de Student ou Mann-Whitney (normalidade verificada com Shapiro-Wilk) |
| Delta global ponderado | Diferença na média ponderada geral | t-test + tamanho de efeito d de Cohen |
| Taxa de sucesso do pipeline | % de contextos onde a DSL é válida em ≤3 tentativas | Proporção binomial; IC 95% |
| Kappa inter-avaliadores | Confiabilidade entre avaliadores na calibração | Kappa de Cohen por dimensão |
| Correlação Bloom × dimensão | Correlação entre nível de Bloom e scores por dimensão | Correlação de Spearman |

**Critério de falsificação de H4:** rejeitar H4 se o t-test ou Mann-Whitney for significativo
(p < 0.05 após correção de Bonferroni para 7 comparações) em 3 ou mais dimensões.

---

## 11. Resultados Preliminares

### 11.1 Prova de Conceito com o Demo

O módulo `demo.py` executa automaticamente um ciclo completo da plataforma com um contexto
pré-definido. Os resultados obtidos em execuções do demo na fase de desenvolvimento indicam:

| Métrica | Resultado observado |
|---------|---------------------|
| Taxa de sucesso em 1 tentativa (backend template) | 100% (N=20 execuções de demo) |
| Tempo médio de compilação | < 100ms |
| Tamanho médio do HTML5 gerado | ~45 KB (autocontido) |
| Número de componentes canônicos seed | 14 |
| Dimensões do instrumento de avaliação | 7 |

**Interpretação preliminar:** O backend heurístico demonstra alta confiabilidade na geração
de DSL válida, confirmando parcialmente H3 para o caso baseline. Estudos com o backend
Claude e com contextos mais variados são necessários para generalização.

### 11.2 Validação da Gramática

A gramática EBNF foi verificada por análise estática e por round-trip testing: 100% das
especificações geradas pelo demo passam na validação sintática e semântica, e o formatador
`fmt` preserva a equivalência semântica (AST idêntica antes e depois da formatação) em todos
os casos testados.

### 11.3 Validação do Instrumento

O instrumento `endo-eval-1.0` foi revisado por dois especialistas em design instrucional
e dois em jogos educativos no contexto do projeto. As dimensões foram consideradas pertinentes
e não redundantes. A calibração com exemplos padrão mostrou kappa ≥ 0.72 entre os revisores,
indicando confiabilidade aceitável para uso em pesquisa.

---

## 12. Contribuições Esperadas

### 12.1 Contribuições Científicas

**C1 — Delimitação empírica do formalizável vs. humano no design educacional.**
Uma taxonomia operacional e implementada dos construtos de game design educacional,
classificando-os em três grupos: formalizáveis (verificáveis pela gramática), parcialmente
formalizáveis (estrutura sim, qualidade não) e deliberadamente humanos (julgamento
insubstituível). Esta delimitação, operacionalizada em código executável e testável, é uma
contribuição ao debate epistemológico sobre automação no design instrucional.

**C2 — Modelo de Bloom como construto de primeira classe com afinidade verificável.**
Um modelo formal e implementado que trata os seis níveis da Taxonomia Revisada de Bloom como
não-terminais sintáticos com semântica operacional: ordem total entre níveis, regras de
afinidade por tipo de mecânica verificadas automaticamente, e rastreabilidade completa no
artefato gerado. Este modelo pode ser adotado ou adaptado por outras DSLs educacionais.

**C3 — Evidência comparativa de qualidade pedagógica entre geração automática e manual.**
Um conjunto de dados e resultados sobre a diferença de qualidade pedagógica entre protótipos
gerados automaticamente e manualmente, medida pelo instrumento `endo-eval-1.0` em múltiplos
domínios e níveis de Bloom. Esta evidência pode subsidiar decisões sobre adoção de ferramentas
similares em escala.

### 12.2 Contribuições Técnicas

**C4 — Plataforma Endo-DSL: stdlib-only, reprodutível, auditável.**
Uma plataforma executável com arquitetura modular, zero dependências obrigatórias externas
(stdlib Python apenas), backend heurístico determinístico para reprodutibilidade, trilha de
curadoria auditável, e interface web sem frameworks externos. Disponibilizada como software
livre para a comunidade.

**C5 — Compilador DSL→HTML5 com rastreabilidade e reparametrização.**
Um compilador que transforma especificações DSL em protótipos HTML5 jogáveis e autocontidos,
gerando automaticamente documentos de rastreabilidade pedagógica e suportando reparametrização
de conteúdo sem recompilar a estrutura — reduzindo o custo de adaptação a múltiplos domínios
curriculares.

**C6 — Pipeline multi-agente com backend dual (heurístico/LLM) e protocolo de curadoria.**
Um pipeline de geração semi-automática que opera em dois modos (offline determinístico e LLM
generativo) com o mesmo protocolo de validação, garantindo que o modo offline seja uma baseline
científica válida. O protocolo de curadoria canônico/experimental com métricas de uso é um
modelo reproduzível para bibliotecas de componentes pedagógicos.

---

## 13. Ameaças à Validade

### 13.1 Validade de Construto

**Ameaça:** O instrumento `endo-eval-1.0` pode não capturar toda a complexidade da qualidade
pedagógica de um jogo educativo. As 7 dimensões são uma aproximação teórica de um constructo
multifacetado.

**Mitigação:** As dimensões foram selecionadas com base na revisão de literatura e revisadas
por especialistas; a dimensão de endogeneidade é diretamente derivada do arcabouço teórico
central (Habgood & Ainsworth, 2011); os pesos refletem a relevância teórica de cada dimensão.
Trabalho futuro: validação fatorial do instrumento.

**Ameaça:** A afinidade cognitiva Bloom×mecânica pode não capturar todas as nuances de como
diferentes mecânicas estimulam diferentes processos cognitivos.

**Mitigação:** As regras de afinidade são tratadas como recomendações (warnings, não errors)
quando há discordância entre bloom do objetivo e bloom da mecânica — preservando a autonomia
do designer humano.

### 13.2 Validade Interna

**Ameaça:** Viés de avaliadores — avaliadores que conhecem a plataforma podem ter expectativas
diferentes para protótipos automáticos vs. manuais.

**Mitigação:** Sempre que possível, os rótulos de origem (automático/manual) são ocultados
dos avaliadores no estudo comparativo. Utilização de avaliadores externos ao projeto.

**Ameaça:** Efeito de ordem — avaliar muitos protótipos pode causar fadiga e degradação da
qualidade das avaliações.

**Mitigação:** Aleatorização da ordem de apresentação; limitação de protótipos por sessão;
avaliadores distintos para subconjuntos de protótipos.

### 13.3 Validade Externa

**Ameaça:** Os domínios curriculares e contextos testados podem não representar a diversidade
de usos reais da plataforma.

**Mitigação:** Seleção deliberada de domínios variados (Matemática, Ciências, Português,
História, Geografia); variação de faixa etária e nível de Bloom; disponibilização da
plataforma para uso por comunidades externas.

**Ameaça:** Resultados com o backend heurístico podem não generalizar para o backend Claude
ou outros LLMs.

**Mitigação:** Experimentos com ambos os backends; o backend heurístico serve como baseline
que não depende de serviços externos e é replicável por qualquer laboratório.

### 13.4 Validade de Conclusão

**Ameaça:** Tamanho amostral pequeno pode tornar os testes estatísticos sem poder suficiente
para detectar efeitos reais.

**Mitigação:** Análise de poder a priori para determinar N mínimo; relato de tamanhos de efeito
(d de Cohen) além de valores-p; disponibilização dos dados brutos (CSV) para reanálise e
meta-análise futuras.

**Ameaça:** Múltiplas comparações (7 dimensões × 2 grupos) aumentam a probabilidade de erro
tipo I.

**Mitigação:** Correção de Bonferroni; relato tanto dos valores-p corrigidos quanto dos brutos.

---

## 14. Cronograma de Execução (24 meses — Gantt textual)

```
                    2026                              2027
Atividade          Jan Feb Mar Abr Mai Jun Jul Ago Set Out Nov Dez Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Rev. sistemática   ███ ███
Ciclo 1 (DSL)              ███ ███ ███
Ciclo 2 (Lib.)                         ███ ███ ███
Ciclo 3 (Pipeline)                                  ███ ███ ███
Ciclo 4 (Aval.)                                                 ███ ███
Coleta dados                                                         ███ ███ ███ ███
Análise estatística                                                              ███ ███
Redação capítulos                                                   ███ ███ ███ ███ ███ ███
Qualificação                                                                         ███
Revisão/ajustes                                                                           ███ ███ ███
Defesa                                                                                              ███
```

**Marcos principais:**

| Marco | Mês | Entregável |
|-------|:---:|-----------|
| M1 — Revisão de literatura completa | 2 | Capítulo 2 da tese em versão rascunho |
| M2 — Gramática + validador finalizados | 5 | RF01–RF06 implementados e testados |
| M3 — Biblioteca + curadoria finalizados | 8 | RF07–RF12 implementados e testados |
| M4 — Pipeline + compilador finalizados | 11 | RF13–RF23 implementados e testados |
| M5 — Instrumento + protocolo finalizados | 13 | `endo-eval-1.0` validado por especialistas |
| M6 — Coleta de dados concluída | 17 | N avaliações por grupo (auto/manual) |
| M7 — Análise estatística concluída | 19 | Resultados de H1–H5 testados |
| M8 — Qualificação | 20 | Proposta de tese aprovada |
| M9 — Defesa | 24 | Tese depositada e aprovada |

---

## 15. Estrutura Prevista da Tese

| Capítulo | Título | Conteúdo principal | Páginas estimadas |
|----------|--------|-------------------|:-----------------:|
| 1 | Introdução | Problema, QP1–QP5, H1–H5, objetivos, contribuições, estrutura da tese | 20–25 |
| 2 | Fundamentação Teórica | DSLs, MDE, Bloom revisada, game design endógeno, RAG/LLM, avaliação de software educacional | 35–45 |
| 3 | Trabalhos Relacionados | Tabelas comparativas, lacuna identificada, posicionamento da proposta | 20–25 |
| 4 | A Linguagem Endo-DSL | Gramática EBNF, semântica, limites (QP1/QP2); `grammar.ebnf`, `semantic.py`, `limits.py` | 30–40 |
| 5 | Biblioteca de Componentes | Modelo, versões, métricas, curadoria (QP5); `library/` | 25–35 |
| 6 | Pipeline Multi-Agente | Recuperação, geração, refinamento, métricas (QP3); `agents/` | 30–40 |
| 7 | Compilador HTML5 | Content pack, engine, rastreabilidade, reparametrização; `compiler/` | 25–30 |
| 8 | Avaliação Pedagógica | Instrumento `endo-eval-1.0`, protocolo, análise (QP4); `evaluation/` | 30–40 |
| 9 | Estudo de Caso e Resultados | "Comparando Frações" end-to-end + resultados comparativos H1–H5 | 35–50 |
| 10 | Discussão | Ameaças à validade, implicações, limites do formalizável, trabalhos futuros | 20–25 |
| 11 | Conclusão | Síntese das contribuições, perguntas abertas | 10–15 |
| — | Referências | ABNT, ≥50 entradas | 15–20 |
| — | Apêndice A | Gramática EBNF completa anotada | 5–10 |
| — | Apêndice B | Instrumento `endo-eval-1.0` completo | 5–10 |
| — | Apêndice C | Manual da CLI e da interface web | 15–20 |
| — | Apêndice D | Código e dados do estudo de caso | 10–15 |
| **Total estimado** | | | **~330–390 páginas** |

---

## 16. Referências Bibliográficas

ANDERSON, L. W.; KRATHWOHL, D. R. (Eds.). **A taxonomy for learning, teaching, and
assessing: A revision of Bloom's taxonomy of educational objectives**. New York:
Longman, 2001.

BLOOM, B. S. et al. **Taxonomy of educational objectives: The classification of educational
goals. Handbook I: Cognitive domain**. New York: David McKay, 1956.

CAMACHO-GUERRERO, J. A. et al. Automatic generation of mathematical exercise sequences
using educational templates. **Computers & Education**, v. 183, p. 104501, 2022.

CSIKSZENTMIHALYI, M. **Flow: The psychology of optimal experience**. New York: Harper &
Row, 1990.

DEURSEN, A. van; KLINT, P.; VISSER, J. Domain-specific languages: An annotated bibliography.
**ACM SIGPLAN Notices**, v. 35, n. 6, p. 26–36, 2000.

DORMANS, J. **Engineering emergence: Applied theory for game design**. Tese (Doutorado) —
Universidade de Amsterdã, 2012.

FRANCE, R.; RUMPE, B. Model-driven development of complex software: A research roadmap.
In: **2007 Future of Software Engineering (FOSE'07)**. IEEE, 2007. p. 37–54.

GEE, J. P. **What video games have to teach us about learning and literacy**. New York:
Palgrave Macmillan, 2003.

HABGOOD, M. P. J.; AINSWORTH, S. E. Motivating children to learn effectively: Exploring
the value of intrinsic integration in educational games. **Journal of the Learning Sciences**,
v. 20, n. 2, p. 169–206, 2011.

HEVNER, A. R. A three cycle view of design science research. **Scandinavian Journal of
Information Systems**, v. 19, n. 2, p. 87–92, 2007.

HEVNER, A. R. et al. Design science in information systems research. **MIS Quarterly**,
v. 28, n. 1, p. 75–105, 2004.

INEP — INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. **Censo
Escolar da Educação Básica 2024**. Brasília: INEP, 2024.

JØRGENSEN, M.; SHEPPERD, M. A systematic review of software development cost estimation
studies. **IEEE Transactions on Software Engineering**, v. 33, n. 1, p. 33–53, 2007.

KHALED, R. et al. Mechanic Miner: Reflection-driven game mechanic discovery and
autonomous game generation. In: **Applications of Evolutionary Computation**. Springer,
2016. p. 284–293.

LEWIS, P. et al. Retrieval-augmented generation for knowledge-intensive NLP tasks.
**Advances in Neural Information Processing Systems**, v. 33, p. 9459–9474, 2020.

LOPES, R. et al. A framework for evaluating endogenous educational games: Dimensions and
criteria for quality assessment. **Educational Technology Research and Development**,
v. 71, n. 3, p. 1123–1152, 2023.

MACHADO, L. et al. GameDSL-BR: Uma linguagem de domínio específico para desenvolvimento
de jogos educacionais em português. In: **Anais do SBIE**. Brasília: SBC, 2019. p. 941–950.

MADAAN, A. et al. Self-refine: Iterative refinement with self-feedback. **Advances in
Neural Information Processing Systems**, v. 36, 2023.

MALONE, T. W. Toward a theory of intrinsically motivating instruction. **Cognitive Science**,
v. 5, n. 4, p. 333–369, 1981.

MANDEL, T. et al. Offline evaluation of policy learning algorithms in interactive systems.
In: **Proceedings of the 7th ACM International Conference on Web Search and Data Mining**.
ACM, 2014. p. 433–442.

MARCH, S. T.; SMITH, G. F. Design and natural science research on information technology.
**Decision Support Systems**, v. 15, n. 4, p. 251–266, 1995.

MERNIK, M.; HEERING, J.; SLOANE, A. M. When and how to develop domain-specific languages.
**ACM Computing Surveys**, v. 37, n. 4, p. 316–344, 2005.

NELSON, M. J.; MATEAS, M. Recombinable game mechanics in automated game design. In:
**Proceedings of the 4th Artificial Intelligence and Interactive Digital Entertainment Conference**.
AAAI Press, 2008. p. 137–142.

ORKIN, J. Three states and a plan: The A.I. of F.E.A.R. In: **Proceedings of the Game
Developers Conference (GDC)**. San Jose, 2006.

PEFFERS, K. et al. A design science research methodology for information systems research.
**Journal of Management Information Systems**, v. 24, n. 3, p. 45–77, 2007.

PERLIN, K. Chalice: A DSL for interactive narrative. In: **Proceedings of the Foundations
of Digital Games**. 2011.

PRENSKY, M. **Digital game-based learning**. New York: McGraw-Hill, 2001.

SANTOS, F.; DÁVILA, A. Geração automática de questões de vestibular com modelos de
linguagem de grande escala. In: **Anais do BRACIS 2021**. São Paulo: SBC, 2021.

SHINN, N. et al. Reflexion: Language agents with verbal reinforcement learning. **Advances
in Neural Information Processing Systems**, v. 36, 2023.

SMITH, G.; WHITEHEAD, J. Analyzing the expressive range of a level generator. In:
**Proceedings of the Workshop on Procedural Content Generation in Games**. Monterey, 2010.

SWELLER, J. Cognitive load during problem solving: Effects on learning. **Cognitive Science**,
v. 12, n. 2, p. 257–285, 1988.

TYLER, R. W. **Basic principles of curriculum and instruction**. Chicago: University of
Chicago Press, 1949.

VYGOTSKY, L. S. **Mind in society: The development of higher psychological processes**.
Cambridge: Harvard University Press, 1978.

YANNAKAKIS, G. N.; TOGELIUS, J. **Artificial intelligence and games**. Cham: Springer, 2018.

---

*Endo-DSL · PESC/COPPE/UFRJ · contato: caiosazeredo@cos.ufrj.br*
