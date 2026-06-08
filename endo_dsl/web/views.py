"""Renderização das páginas HTML da interface web."""

from __future__ import annotations

import html
import json
from typing import Any, Dict, List

from endo_dsl.dsl.bloom import Bloom, parse_bloom
from endo_dsl.dsl.semantic import MECHANIC_TYPES
from endo_dsl.evaluation.instrument import DIMENSIONS

NAV = [
    ("/", "Início"),
    ("/studio", "Estúdio"),
    ("/library", "Biblioteca"),
    ("/curator", "Curadoria"),
    ("/report", "Relatórios"),
    ("/docs", "Gramática"),
]


def esc(text: Any) -> str:
    return html.escape(str(text if text is not None else ""))


def bloom_badge(name: str) -> str:
    level = parse_bloom(name) if name else None
    n = int(level) if level else 0
    return f'<span class="badge bloom-{n}">{esc(level.pt if level else name)}</span>'


def status_badge(status: str) -> str:
    cls = {"canonical": "ok", "experimental": "warn", "rejected": "bad"}.get(status, "")
    label = {"canonical": "canônico ★", "experimental": "experimental",
             "rejected": "rejeitado"}.get(status, status)
    return f'<span class="pill {cls}">{esc(label)}</span>'


def layout(title: str, body: str, active: str = "/") -> str:
    nav = "".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label in NAV
    )
    return f"""<!doctype html><html lang="pt-br"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Endo-DSL</title>
<link rel="stylesheet" href="/static/app.css">
</head><body>
<header class="topbar">
  <a class="brand" href="/">Endo<span>-DSL</span></a>
  <nav>{nav}</nav>
</header>
<main>{body}</main>
<footer class="foot">Endo-DSL · jogos educacionais endógenos · PESC/COPPE/UFRJ</footer>
</body></html>"""


# --------------------------------------------------------------------------- #
def home_page(stats: Dict[str, Any]) -> str:
    body = f"""
<section class="hero">
  <h1>Design e geração automática de jogos educacionais endógenos</h1>
  <p>Uma DSL formal com a Taxonomia de Bloom como construto de primeira classe,
     uma biblioteca de componentes reutilizáveis, um pipeline multi-agente e um
     compilador para protótipos HTML5 jogáveis.</p>
  <div class="cta">
    <a class="btn" href="/studio">▶ Abrir o Estúdio de Design</a>
    <a class="btn ghost" href="/library">Explorar a Biblioteca</a>
  </div>
</section>
<section class="grid4">
  <div class="stat"><b>{stats['components']}</b><span>componentes</span></div>
  <div class="stat"><b>{stats['canonical']}</b><span>canônicos</span></div>
  <div class="stat"><b>{stats['prototypes']}</b><span>protótipos</span></div>
  <div class="stat"><b>{esc(stats['backend'])}</b><span>backend LLM</span></div>
</section>
<section class="cards">
  <div class="card"><h3>1 · Motor da DSL</h3><p>Gramática formal, parser com erros
     descritivos (RF03) e validação de coerência cognitiva (RF04).</p></div>
  <div class="card"><h3>2 · Biblioteca</h3><p>Componentes versionados, com métricas,
     busca multifacetada (RF09) e curadoria canônico/experimental (RF12).</p></div>
  <div class="card"><h3>3 · Pipeline multi-agente</h3><p>Recuperação, geração e
     validação encadeadas, com refinamento iterativo (RF14–RF18).</p></div>
  <div class="card"><h3>4 · Compilador</h3><p>DSL → protótipo HTML5 jogável, Bloom
     rastreável (RF21) e reparametrização de domínio (RF22).</p></div>
</section>"""
    return layout("Início", body, "/")


def studio_page() -> str:
    bloom_opts = "".join(f'<option value="{b.pt}">{b.pt}</option>' for b in Bloom)
    body = f"""
<div class="studio">
  <aside class="steps">
    <h2>Jornada</h2>
    <ol id="steps">
      <li data-step="1" class="active">Contexto educacional</li>
      <li data-step="2">Recuperar componentes</li>
      <li data-step="3">Gerar especificação</li>
      <li data-step="4">Revisar &amp; validar</li>
      <li data-step="5">Compilar protótipo</li>
      <li data-step="6">Avaliar</li>
    </ol>
  </aside>
  <section class="panel">
    <!-- Fase 1 -->
    <div class="phase" data-phase="1">
      <h2>Fase 1 — Contexto educacional <span class="rf">RF13</span></h2>
      <label>Tema / área de conhecimento
        <input id="domain" placeholder="ex.: Matemática (frações)"></label>
      <label>Tópico específico
        <input id="topic" placeholder="ex.: frações"></label>
      <label>Objetivo de aprendizagem
        <textarea id="objective" placeholder="ex.: comparar frações com denominadores diferentes"></textarea></label>
      <div class="row">
        <label>Nível de Bloom desejado<select id="bloom">{bloom_opts}</select></label>
        <label>Faixa etária<input id="age" placeholder="ex.: 10-11"></label>
      </div>
      <div class="row">
        <label>Escolaridade<input id="level" placeholder="ex.: 5º ano"></label>
        <label>Duração (min)<input id="duration" type="number" placeholder="15"></label>
      </div>
      <label class="check"><input type="checkbox" id="noreading"> Sem leitura extensiva</label>
      <div class="actions">
        <button class="btn" onclick="ENDO.retrieve()">Recuperar componentes →</button>
        <button class="btn ghost" onclick="ENDO.skipToGenerate()">Gerar do zero</button>
      </div>
    </div>
    <!-- Fase 2 -->
    <div class="phase" data-phase="2" hidden>
      <h2>Fase 2 — Componentes recuperados <span class="rf">RF14</span></h2>
      <p class="muted">Selecione os componentes que servirão de ponto de partida.</p>
      <div id="retrieved" class="complist"></div>
      <div class="actions">
        <button class="btn ghost" onclick="ENDO.go(1)">← Voltar</button>
        <button class="btn" onclick="ENDO.generate()">Gerar especificação →</button>
      </div>
    </div>
    <!-- Fase 3/4 -->
    <div class="phase" data-phase="3" hidden>
      <h2>Fases 3–4 — Especificação DSL <span class="rf">RF15 · RF16 · RF05</span></h2>
      <div id="genmeta" class="muted"></div>
      <div class="editor-wrap">
        <pre id="highlight" class="highlight" aria-hidden="true"></pre>
        <textarea id="dsl" spellcheck="false" oninput="ENDO.onEdit()"></textarea>
      </div>
      <div id="diagnostics" class="diagnostics"></div>
      <div class="actions">
        <button class="btn ghost" onclick="ENDO.go(2)">← Componentes</button>
        <button class="btn" onclick="ENDO.compile()">Compilar protótipo →</button>
      </div>
    </div>
    <!-- Fase 5 -->
    <div class="phase" data-phase="5" hidden>
      <h2>Fase 5 — Protótipo compilado <span class="rf">RF19 · RF22 · RF23</span></h2>
      <div id="compiled"></div>
    </div>
    <!-- Fase 6 -->
    <div class="phase" data-phase="6" hidden>
      <h2>Fase 6 — Avaliação pedagógica <span class="rf">RF24 · RF25</span></h2>
      <div id="evalform"></div>
    </div>
  </section>
</div>
<script src="/static/studio.js"></script>"""
    return layout("Estúdio", body, "/studio")


def library_page(comps: List[Any], query: Dict[str, List[str]]) -> str:
    def val(k):
        return esc(query.get(k, [""])[0])

    bloom_opts = '<option value="">Bloom</option>' + "".join(
        f'<option value="{b.pt}">{b.pt}</option>' for b in Bloom)
    type_opts = '<option value="">Mecânica</option>' + "".join(
        f'<option value="{k}">{esc(k)}</option>' for k in sorted(MECHANIC_TYPES))
    rows = ""
    for c in comps:
        rating = f'⟨{c.metrics.avg_rating:.1f}⟩' if c.metrics.avg_rating else "—"
        rows += f"""
<tr onclick="location.href='/component/{esc(c.key)}'">
  <td>{status_badge(c.status)}</td>
  <td><b>{esc(c.name)}</b><br><span class="muted small">{esc(c.key)}</span></td>
  <td>{bloom_badge(c.bloom_level)}</td>
  <td>{esc(c.mechanic_type)}</td>
  <td>{esc(c.domain or '—')}</td>
  <td>{c.metrics.instantiations}</td>
  <td>{rating}</td>
</tr>"""
    body = f"""
<h1>Biblioteca de componentes <span class="rf">RF07–RF12</span></h1>
<form class="filters" method="get">
  <input name="text" placeholder="Buscar…" value="{val('text')}">
  <select name="bloom">{_selected(bloom_opts, val('bloom'))}</select>
  <select name="type">{_selected(type_opts, val('type'))}</select>
  <input name="domain" placeholder="Domínio" value="{val('domain')}">
  <select name="status">{_selected('<option value="">Status</option>'
        '<option value="canonical">canônico</option>'
        '<option value="experimental">experimental</option>', val('status'))}</select>
  <button class="btn" type="submit">Filtrar</button>
</form>
<table class="grid">
  <tr><th>Status</th><th>Componente</th><th>Bloom</th><th>Mecânica</th>
      <th>Domínio</th><th>Usos</th><th>Aval.</th></tr>
  {rows or '<tr><td colspan="7" class="muted">Nenhum componente encontrado.</td></tr>'}
</table>"""
    return layout("Biblioteca", body, "/library")


def component_page(comp: Any, versions: List[Dict], history: List[Dict]) -> str:
    params = "".join(f"<li><b>{esc(k)}</b>: {esc(v)}</li>" for k, v in comp.params.items())
    vrows = "".join(
        f"<tr><td>v{v['version']}</td><td>{esc(v['change_note'])}</td>"
        f"<td class='muted small'>{esc(v['created_at'])}</td></tr>" for v in versions)
    hrows = "".join(
        f"<tr><td>{esc(h['action'])}</td><td>{esc(h['curator'] or '—')}</td>"
        f"<td>{esc(h['justification'] or '')}</td></tr>" for h in history)
    refs = "".join(f"<li>{esc(r)}</li>" for r in comp.references) or "<li class='muted'>—</li>"
    m = comp.metrics
    body = f"""
<a href="/library" class="muted">← Biblioteca</a>
<h1>{esc(comp.name)} {status_badge(comp.status)}</h1>
<p class="muted">{esc(comp.key)} · v{comp.current_version} · autor: {esc(comp.author or '—')}</p>
<div class="row2">
  <div>
    <h3>Assinatura DSL</h3>
    <pre class="code">{esc(comp.dsl_signature)}</pre>
    <h3>Descrição</h3><p>{esc(comp.description)}</p>
    <h3>Parâmetros configuráveis</h3><ul>{params or '<li class=muted>—</li>'}</ul>
    <h3>Referências (RF08)</h3><ul>{refs}</ul>
  </div>
  <aside class="sidecard">
    <h3>Classificação</h3>
    <p>{bloom_badge(comp.bloom_level)} · {esc(comp.mechanic_type)}</p>
    <p class="muted small">Domínio: {esc(comp.domain or '—')}<br>
       Contexto: {esc(comp.context or '—')} · {esc(comp.age_range or '—')}</p>
    <h3>Métricas (RF11)</h3>
    <ul class="metrics">
      <li>Instanciações: <b>{m.instantiations}</b></li>
      <li>Avaliação média: <b>{f'{m.avg_rating:.2f}' if m.avg_rating else '—'}</b>
          ({m.rating_count})</li>
      <li>Sucesso de compilação: <b>{f'{m.compile_success_rate*100:.0f}%'
          if m.compile_success_rate is not None else '—'}</b></li>
    </ul>
  </aside>
</div>
<h3>Histórico de versões (RF10)</h3>
<table class="grid"><tr><th>Versão</th><th>Nota</th><th>Data</th></tr>{vrows}</table>
<h3>Trilha de curadoria (RF12)</h3>
<table class="grid"><tr><th>Ação</th><th>Curador</th><th>Justificativa</th></tr>
{hrows or '<tr><td colspan=3 class=muted>—</td></tr>'}</table>"""
    return layout(comp.name, body, "/library")


def curator_page(queue: List[Any]) -> str:
    cards = ""
    for c in queue:
        cards += f"""
<div class="card curate" data-id="{c.id}">
  <div class="row">
    <div><b>{esc(c.name)}</b> {bloom_badge(c.bloom_level)}
         <span class="muted small">{esc(c.mechanic_type)}</span></div>
    <span class="muted small">instâncias: {c.metrics.instantiations} ·
         aval.: {f'{c.metrics.avg_rating:.1f}' if c.metrics.avg_rating else '—'}</span>
  </div>
  <pre class="code small">{esc(c.dsl_signature)}</pre>
  <p class="muted">{esc(c.description)}</p>
  <div class="actions">
    <button class="btn ok" onclick="CUR.act({c.id},'approve')">Aprovar (→ canônico)</button>
    <button class="btn ghost" onclick="CUR.act({c.id},'request_changes')">Solicitar revisão</button>
    <button class="btn bad" onclick="CUR.act({c.id},'reject')">Rejeitar</button>
  </div>
</div>"""
    body = f"""
<h1>Fila de curadoria <span class="rf">jornada do curador · RF12</span></h1>
<p class="muted">Componentes experimentais aguardando revisão. Aprovar promove a
   canônico (priorizado pelo Agente de Recuperação).</p>
{cards or '<p class="muted">Fila vazia — nenhum componente experimental pendente.</p>'}
<script src="/static/curator.js"></script>"""
    return layout("Curadoria", body, "/curator")


def report_page(report: Dict[str, Any]) -> str:
    s = report["summary"]
    dim_rows = ""
    for d in report["by_dimension"]:
        dim_rows += f"""
<tr><td>{esc(d['label'])}</td>
    <td>{_barcell(d['auto'])}</td>
    <td>{_barcell(d['manual'])}</td>
    <td>{_delta(d['delta'])}</td></tr>"""
    bloom_rows = "".join(
        f"<tr><td>{bloom_badge(k)}</td><td>{_fmt(v['auto_mean'])} ({v['n_auto']})</td>"
        f"<td>{_fmt(v['manual_mean'])} ({v['n_manual']})</td></tr>"
        for k, v in report["by_bloom"].items())
    domain_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{_fmt(v['auto_mean'])} ({v['n_auto']})</td>"
        f"<td>{_fmt(v['manual_mean'])} ({v['n_manual']})</td></tr>"
        for k, v in report["by_domain"].items())
    body = f"""
<h1>Relatório comparativo <span class="rf">RF24–RF26</span></h1>
<div class="grid4">
  <div class="stat"><b>{_fmt(s['auto']['overall_mean'])}</b><span>auto (n={s['auto']['n']})</span></div>
  <div class="stat"><b>{_fmt(s['manual']['overall_mean'])}</b><span>manual (n={s['manual']['n']})</span></div>
  <div class="stat"><b>{_delta(s['overall_delta'])}</b><span>diferença</span></div>
  <div class="stat"><a class="btn ghost" href="/api/report?format=csv">⬇ CSV (RF25)</a></div>
</div>
<p class="callout">{esc(report['interpretation'])}</p>
<h3>Por dimensão pedagógica</h3>
<table class="grid"><tr><th>Dimensão</th><th>Automático</th><th>Manual</th><th>Δ</th></tr>
{dim_rows}</table>
<div class="row2">
  <div><h3>Por nível de Bloom</h3>
    <table class="grid"><tr><th>Bloom</th><th>Auto</th><th>Manual</th></tr>
    {bloom_rows or '<tr><td colspan=3 class=muted>—</td></tr>'}</table></div>
  <div><h3>Por domínio</h3>
    <table class="grid"><tr><th>Domínio</th><th>Auto</th><th>Manual</th></tr>
    {domain_rows or '<tr><td colspan=3 class=muted>—</td></tr>'}</table></div>
</div>"""
    return layout("Relatórios", body, "/report")


def docs_page(grammar: str, limits: Dict[str, Any]) -> str:
    def group(title, items, cls):
        rows = "".join(f"<li><b>{esc(i['name'])}</b> — {esc(i['rationale'])}</li>" for i in items)
        return f'<div class="card {cls}"><h3>{esc(title)}</h3><ul>{rows}</ul></div>'

    mechs = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(v.label)}</td>"
        f"<td>{', '.join(sorted(b.pt for b in v.bloom_affinity))}</td></tr>"
        for k, v in sorted(MECHANIC_TYPES.items()))
    body = f"""
<h1>Gramática &amp; limites <span class="rf">RF01 · RF02 · RF06</span></h1>
<h3>Gramática formal (EBNF)</h3>
<pre class="code">{esc(grammar)}</pre>
<h3>Tipos de mecânica e afinidade cognitiva (RF04)</h3>
<table class="grid"><tr><th>Tipo</th><th>Rótulo</th><th>Níveis de Bloom afins</th></tr>{mechs}</table>
<h3>Limites da formalização (RF06)</h3>
<div class="cards">
  {group('Formalizados', limits['formalized'], 'ok')}
  {group('Parcialmente formalizados', limits['partial'], 'warn')}
  {group('Controle humano deliberado', limits['human'], 'bad')}
</div>"""
    return layout("Gramática", body, "/docs")


def evaluate_page(proto: Dict[str, Any]) -> str:
    dims = "".join(f"""
<div class="dimrow"><label>{esc(d.label)}<br><span class="muted small">{esc(d.question)}</span></label>
  <div class="likert" data-dim="{d.key}">
    {''.join(f'<button type=button onclick="EV.set(this,{n})">{n}</button>' for n in range(1,6))}
  </div></div>""" for d in DIMENSIONS)
    body = f"""
<a href="/prototype/{proto['id']}" class="muted">← Protótipo</a>
<h1>Avaliar protótipo #{proto['id']} <span class="rf">RF24 · RF25</span></h1>
<p class="muted">{esc(proto.get('title',''))} · origem: {esc(proto.get('origin'))}</p>
<form id="evalform" data-pid="{proto['id']}" data-origin="{esc(proto.get('origin','auto'))}">
  {dims}
  <label>Avaliador<input id="evaluator" placeholder="seu nome"></label>
  <label>Comentários<textarea id="comments"></textarea></label>
  <button class="btn" type="button" onclick="EV.submit()">Registrar avaliação</button>
  <span id="evstatus" class="muted"></span>
</form>
<script src="/static/evaluate.js"></script>"""
    return layout("Avaliação", body, "/report")


# --------------------------------------------------------------------------- #
def not_found(msg: str) -> str:
    return layout("Não encontrado", f'<div class="card"><h1>404</h1><p>{esc(msg)}</p>'
                  '<a class="btn" href="/">Início</a></div>')


def error_page(msg: str, tb: str) -> str:
    return layout("Erro", f'<div class="card bad"><h1>Erro</h1><p>{esc(msg)}</p>'
                  f'<pre class="code small">{esc(tb)}</pre></div>')


# --------------------------------------------------------------------------- #
def _selected(options_html: str, value: str) -> str:
    if not value:
        return options_html
    return options_html.replace(f'value="{value}"', f'value="{value}" selected')


def _fmt(v) -> str:
    return f"{v:.2f}" if v is not None else "—"


def _delta(v) -> str:
    if v is None:
        return "—"
    cls = "up" if v > 0 else ("down" if v < 0 else "")
    return f'<span class="delta {cls}">{v:+.2f}</span>'


def _barcell(v) -> str:
    if v is None:
        return '<span class="muted">—</span>'
    pct = int(round(v / 5 * 100))
    return (f'<div class="minibar"><i style="width:{pct}%"></i></div>'
            f'<span class="small">{v:.2f}</span>')
