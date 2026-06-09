"""Renderização das páginas HTML da interface web (v2 — Overleaf-like IDE)."""

from __future__ import annotations

import html
import json
from typing import Any, Dict, List

from endo_dsl.dsl.bloom import Bloom, parse_bloom
from endo_dsl.dsl.semantic import MECHANIC_TYPES
from endo_dsl.evaluation.instrument import DIMENSIONS

NAV = [
    ("/",         "Início"),
    ("/studio",   "Estúdio"),
    ("/library",  "Biblioteca"),
    ("/curator",  "Curadoria"),
    ("/report",   "Relatórios"),
    ("/docs",     "Gramática"),
]


def esc(text: Any) -> str:
    return html.escape(str(text if text is not None else ""))


def bloom_badge(name: str) -> str:
    level = parse_bloom(name) if name else None
    n = int(level) if level else 0
    return f'<span class="badge bloom-{n}">{esc(level.pt if level else name)}</span>'


def status_badge(status: str) -> str:
    cls   = {"canonical": "ok", "experimental": "warn", "rejected": "bad"}.get(status, "")
    label = {"canonical": "canônico ★", "experimental": "experimental",
             "rejected": "rejeitado"}.get(status, status)
    return f'<span class="pill {cls}">{esc(label)}</span>'


# --------------------------------------------------------------------------- #
# Layout base
# --------------------------------------------------------------------------- #
def layout(title: str, body: str, active: str = "/", *,
           full: bool = False, extra_body_class: str = "") -> str:
    nav = "".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label in NAV
    )
    main_cls = "" if full else "wrap"
    body_cls = ("studio-body " + extra_body_class).strip() if full else extra_body_class
    foot = "" if full else (
        '<footer class="foot">Endo-DSL &middot; jogos educacionais endógenos &middot; '
        'PESC/COPPE/UFRJ</footer>')
    return f"""<!doctype html><html lang="pt-br"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} &middot; Endo-DSL</title>
<link rel="stylesheet" href="/static/app.css">
<script>(function(){{try{{var t=localStorage.getItem('endo-theme');
if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head><body{(' class="' + body_cls + '"') if body_cls else ''}>
<header class="app-header topbar">
  <a class="brand" href="/">Endo<span>-DSL</span></a>
  <nav>{nav}</nav>
  <div class="tools">
    <button class="icon-btn" id="theme-toggle" title="Alternar tema"
            aria-label="Alternar tema" onclick="ENDOUI.toggleTheme()">◐</button>
    <button class="icon-btn" title="Atalhos de teclado" aria-label="Ajuda"
            onclick="ENDOUI.help()">?</button>
  </div>
</header>
<main class="{main_cls}">{body}</main>
{foot}
<!-- Shortcuts overlay -->
<div class="shortcuts-overlay" id="shortcuts-overlay" hidden>
  <div class="shortcuts-modal" role="dialog" aria-label="Atalhos de teclado">
    <h2>Atalhos de teclado</h2>
    <table>
      <tr><td><kbd>Ctrl</kbd>+<kbd>Enter</kbd></td><td>Compilar protótipo</td></tr>
      <tr><td><kbd>Ctrl</kbd>+<kbd>S</kbd></td><td>Baixar spec (.endo)</td></tr>
      <tr><td><kbd>?</kbd></td><td>Abrir / fechar esta ajuda</td></tr>
      <tr><td><kbd>Esc</kbd></td><td>Fechar overlays</td></tr>
    </table>
    <div class="actions"><button class="btn ghost" onclick="ENDOUI.help()">Fechar</button></div>
  </div>
</div>
<!-- Legacy overlay alias -->
<div class="overlay" id="help-overlay" onclick="if(event.target===this)ENDOUI.help()">
  <div class="modal" role="dialog">
    <h2>Atalhos de teclado</h2>
    <table>
      <tr><td><kbd>Ctrl</kbd>+<kbd>Enter</kbd></td><td>Compilar</td></tr>
      <tr><td><kbd>Ctrl</kbd>+<kbd>S</kbd></td><td>Baixar spec (.endo)</td></tr>
      <tr><td><kbd>?</kbd></td><td>Abrir / fechar ajuda</td></tr>
    </table>
    <div class="actions"><button class="btn ghost" onclick="ENDOUI.help()">Fechar</button></div>
  </div>
</div>
<script>
// Minimal ENDOUI shim — overridden by studio.js when on the studio page
if(typeof ENDOUI==='undefined'){{
  var ENDOUI={{
    toggleTheme:function(){{
      var themes=['endo','dark','light'];
      var cur=document.documentElement.getAttribute('data-theme')||'endo';
      var idx=themes.indexOf(cur);
      var next=themes[(idx+1)%themes.length];
      document.documentElement.setAttribute('data-theme',next);
      try{{localStorage.setItem('endo-theme',next);}}catch(e){{}}
    }},
    help:function(){{
      var el=document.getElementById('shortcuts-overlay');
      if(!el)return;
      if(el.hidden){{el.hidden=false;requestAnimationFrame(function(){{el.classList.add('show');}});}}
      else{{el.classList.remove('show');setTimeout(function(){{el.hidden=true;}},200);}}
    }}
  }};
}}
</script>
</body></html>"""


# --------------------------------------------------------------------------- #
# Home
# --------------------------------------------------------------------------- #
def home_page(stats: Dict[str, Any]) -> str:
    body = f"""
<section class="hero">
  <h1>Design e geração automática de jogos educacionais endógenos</h1>
  <p>Uma DSL formal com a Taxonomia de Bloom como construto de primeira classe,
     uma biblioteca de componentes reutilizáveis, um pipeline multi-agente e um
     compilador para protótipos HTML5 jogáveis.</p>
  <div class="cta">
    <a class="btn lg" href="/studio">&#9654; Abrir o Estúdio de Design</a>
    <a class="btn ghost" href="/library">Explorar a Biblioteca</a>
  </div>
</section>
<section class="grid4">
  <div class="stat"><b>{stats['components']}</b><span>componentes</span></div>
  <div class="stat"><b>{stats['canonical']}</b><span>canônicos</span></div>
  <div class="stat"><b>{stats['prototypes']}</b><span>protótipos</span></div>
  <div class="stat"><b>{esc(stats['backend'])}</b><span>backend LLM</span></div>
</section>
<div class="card" style="margin-bottom:1rem">
  <h3>Início rápido</h3>
  <p>Defina um objetivo de aprendizagem, recupere componentes da biblioteca,
     gere uma especificação DSL com IA e compile o protótipo — tudo no Estúdio.</p>
  <a class="btn" href="/studio">Abrir o Estúdio &#8594;</a>
</div>
<section class="cards">
  <div class="card"><h3>1 &middot; Motor da DSL</h3><p>Gramática formal, parser com erros
     descritivos (RF03) e validação de coerência cognitiva (RF04).</p></div>
  <div class="card"><h3>2 &middot; Biblioteca</h3><p>Componentes versionados, com métricas,
     busca multifacetada (RF09) e curadoria canônico/experimental (RF12).</p></div>
  <div class="card"><h3>3 &middot; Pipeline multi-agente</h3><p>Recuperação, geração e
     validação encadeadas, com refinamento iterativo (RF14–RF18).</p></div>
  <div class="card"><h3>4 &middot; Compilador</h3><p>DSL &rarr; protótipo HTML5 jogável,
     Bloom rastreável (RF21) e reparametrização de domínio (RF22).</p></div>
</section>"""
    return layout("Início", body, "/")


# --------------------------------------------------------------------------- #
# Studio (Overleaf-like IDE)
# --------------------------------------------------------------------------- #
def studio_page() -> str:
    bloom_opts = "".join(f'<option value="{b.pt}">{b.pt}</option>' for b in Bloom)
    dom_opts   = "".join(
        f'<option value="{esc(d)}">{esc(d)}</option>'
        for d in ["Matemática","Português","Ciências","História",
                  "Geografia","Física","Química","Biologia"])
    steps = [
        (1, "Contexto educacional"), (2, "Recuperar componentes"),
        (3, "Gerar especificação"),  (4, "Revisar &amp; validar"),
        (5, "Compilar protótipo"),   (6, "Avaliar"),
    ]
    stepper = "".join(
        f'<li data-step="{n}" class="{"active" if n==1 else ""}" '
        f'onclick="ENDO.go({n})"><span class="num">{n}</span>{lbl}</li>'
        for n, lbl in steps)

    body = f"""
<div class="studio-layout" id="studio-layout">

  <!-- ── Sidebar ── -->
  <aside class="studio-sidebar" id="sidebar">
    <div class="sidebar-content" id="sidebar-content">

      <h2>Jornada (6 fases)</h2>
      <ol class="stepper" id="stepper">{stepper}</ol>

      <h2>Contexto educacional <span class="rf">RF13</span></h2>
      <form id="ctx-form" class="ctx-form" onsubmit="return false">
        <label>Objetivo de aprendizagem
          <textarea name="learning_objective" id="objective"
            placeholder="ex.: comparar frações com denominadores diferentes"
            rows="3"></textarea></label>
        <label>Área / domínio
          <input name="domain" id="domain" placeholder="ex.: Matemática"></label>
        <label>Tópico específico
          <input name="topic" id="topic" placeholder="ex.: frações"></label>
        <label>Nível de Bloom
          <select name="bloom_target" id="bloom">
            {bloom_opts}
          </select></label>
        <div class="row">
          <label style="flex:1">Faixa etária<input name="age_range" placeholder="10-11"></label>
          <label style="flex:1">Duração (min)<input name="duration_minutes" type="number" placeholder="15"></label>
        </div>
        <label class="check"><input type="checkbox" name="no_extensive_reading" value="1">
          Sem leitura extensiva</label>
      </form>

      <div class="actions" style="flex-direction:column;gap:.4rem">
        <button class="btn block" onclick="ENDO.retrieve()">
          &#8984; Recuperar componentes</button>
        <button class="btn ghost block" onclick="ENDO.skipToGenerate()">
          &#10024; Gerar do zero (IA)</button>
      </div>

      <!-- Retrieved components -->
      <div id="retrieved-wrap" hidden>
        <h2>Componentes recuperados <span class="rf">RF14</span></h2>
        <div id="retrieved-list" class="complist compact"></div>
        <div class="actions">
          <button class="btn block" id="btn-generate" onclick="ENDO.generate()">
            Gerar especificação &rarr;</button>
        </div>
      </div>

      <!-- Generation metrics -->
      <div id="metrics-wrap" hidden>
        <h2>Métricas de geração</h2>
        <div id="metrics-box" class="metrics-mini"></div>
      </div>

    </div><!-- /sidebar-content -->
    <div class="sidebar-footer">
      <button class="collapse-btn" id="sidebar-collapse-btn"
              onclick="ENDO.toggleSidebar()" title="Recolher painel">
        &#8249; Recolher
      </button>
    </div>
  </aside><!-- /studio-sidebar -->

  <!-- ── Editor pane ── -->
  <main class="studio-editor-pane" id="editor-pane">

    <!-- Toolbar -->
    <div class="editor-toolbar" role="toolbar" aria-label="Ações do editor">
      <button class="icon-btn" id="sidebar-toggle"
              onclick="ENDO.toggleSidebar()" title="Painel lateral"
              style="background:var(--surface2);color:var(--fg-muted);width:30px;height:30px;font-size:.9rem">&#9776;</button>
      <span class="sep"></span>
      <button class="btn sm ghost" onclick="ENDO.retrieve()" title="Recuperar componentes da biblioteca">
        &#8984; Recuperar</button>
      <button class="btn sm ghost" onclick="ENDO.skipToGenerate()" title="Gerar especificação com IA">
        &#10024; Gerar com IA</button>
      <span class="sep"></span>
      <button class="btn sm" id="btn-compile" onclick="ENDO.compile()" title="Ctrl+Enter">
        &#9654; Compilar</button>
      <button class="btn sm ghost" onclick="ENDO.reparametrize()" title="Reparametrizar domínio">
        &#8635; Reparametrizar</button>
      <select id="reparam-domain" aria-label="Domínio para reparametrização"
              style="width:auto;margin:0;padding:.3rem .5rem;font-size:.8rem;height:auto">
        <option value="">Domínio…</option>{dom_opts}
      </select>
      <span class="sep"></span>
      <button class="btn sm ghost" id="btn-download" onclick="ENDO.download()" title="Ctrl+S">
        &#8595; Baixar</button>
      <button class="btn sm ghost" onclick="ENDO.evaluate()" title="Avaliar protótipo">
        &#9733; Avaliar</button>
      <span class="spacer"></span>
      <!-- Validation badge -->
      <div class="val-badge" id="val-badge" title="Estado da validação">
        <span class="dot"></span> &mdash;
      </div>
    </div><!-- /editor-toolbar -->

    <!-- Code editor -->
    <div class="editor-container" id="editor-container">
      <div class="editor-gutter" id="line-numbers" aria-hidden="true">1</div>
      <div class="editor-highlight" id="highlight-layer" aria-hidden="true"></div>
      <textarea id="dsl-editor" class="dsl-editor" spellcheck="false"
        autocomplete="off" autocapitalize="off" autocorrect="off"
        aria-label="Editor da especificação DSL"
        placeholder="// Preencha o contexto e clique em Gerar com IA, ou escreva sua DSL aqui.
game &quot;Meu Jogo&quot; {{ ... }}"></textarea>
    </div>

    <!-- Error panel -->
    <div class="error-panel" id="error-panel"></div>

    <!-- Status bar -->
    <div class="editor-statusbar" id="statusbar">
      <span class="st"><span class="dot" id="st-syn"></span>sintaxe</span>
      <span class="st"><span class="dot" id="st-sem"></span>semântica</span>
      <span class="st"><span class="dot" id="st-warn"></span>
        <span id="st-warn-n">0</span> avisos</span>
      <span class="st" id="st-msg"></span>
      <span class="spacer"></span>
      <span class="st" id="st-cursor">Ln 1, Col 1</span>
    </div>

  </main><!-- /studio-editor-pane -->

  <!-- ── Resize divider ── -->
  <div class="studio-divider" id="divider" title="Arrastar para redimensionar"></div>

  <!-- ── Preview pane ── -->
  <aside class="studio-preview-pane" id="preview-pane">
    <div class="preview-header">
      <span class="title">Pré-visualização</span>
      <span class="spacer"></span>
      <label class="autocompile-toggle" title="Compilar automaticamente ao editar">
        <input type="checkbox" id="autocompile-toggle">
        auto-compilar
      </label>
      <button class="icon-btn" onclick="ENDO.openPrototype()" title="Abrir em nova aba"
              aria-label="Abrir protótipo em nova aba">&#10138;</button>
    </div>

    <div class="preview-empty" id="preview-empty">
      <div class="big">&#127918;</div>
      <p>Compile uma especificação para ver o protótipo jogável aqui.</p>
      <p class="small muted">A pré-visualização é atualizada após cada compilação.</p>
    </div>
    <iframe id="preview-iframe" class="preview-iframe"
            sandbox="allow-scripts allow-same-origin"
            title="Protótipo compilado"></iframe>

    <div class="compile-metrics" id="compile-metrics" style="display:none"></div>
  </aside><!-- /studio-preview-pane -->

</div><!-- /studio-layout -->

<script src="/static/studio.js"></script>"""

    return layout("Estúdio", body, "/studio", full=True)


# --------------------------------------------------------------------------- #
# Library
# --------------------------------------------------------------------------- #
def library_page(comps: List[Any], query: Dict[str, List[str]]) -> str:
    def val(k):
        return esc(query.get(k, [""])[0])

    bloom_opts = '<option value="">Bloom (todos)</option>' + "".join(
        f'<option value="{b.pt}">{b.pt}</option>' for b in Bloom)
    type_opts  = '<option value="">Mecânica (todas)</option>' + "".join(
        f'<option value="{k}">{esc(k)}</option>' for k in sorted(MECHANIC_TYPES))
    cur_bloom  = val("bloom")

    # Bloom filter chips
    chips = '<a class="chip {on}" href="?">Todos</a>'.format(
        on="on" if not cur_bloom else "")
    for b in Bloom:
        color = f"var(--bloom-{int(b)})"
        on    = "on" if cur_bloom == b.pt else ""
        chips += (
            f'<a class="chip {on}" href="?bloom={b.pt}" '
            f'style="background:{"" if not on else color};border-color:{color};'
            f'color:{"#fff" if on else color}">'
            f'<span class="badge bloom-{int(b)}">{b.pt}</span></a>')

    cards = ""
    for c in comps:
        rating = f'{c.metrics.avg_rating:.1f}&#9733;' if c.metrics.avg_rating else "—"
        cards += f"""
<div class="comp-card" onclick="location.href='/component/{esc(c.key)}'" role="button"
     tabindex="0" onkeydown="if(event.key==='Enter')location.href='/component/{esc(c.key)}'">
  <div class="cc-head">
    <div><div class="cc-name">{esc(c.name)}</div>
      <div class="cc-key">{esc(c.key)}</div></div>
    {status_badge(c.status)}
  </div>
  <div class="cc-badges">{bloom_badge(c.bloom_level)}
    <span class="pill">{esc(c.mechanic_type)}</span>
    <span class="pill">{esc(c.domain or 'genérico')}</span></div>
  <div class="cc-desc">{esc((c.description or '')[:120])}</div>
  <div class="cc-metrics">
    <span><b>{c.metrics.instantiations}</b> usos</span>
    <span><b>{rating}</b> ({c.metrics.rating_count})</span>
  </div>
</div>"""

    body = f"""
<h1>Biblioteca de componentes <span class="rf">RF07–RF12</span></h1>
<p class="muted">{len(comps)} componente(s). Clique para ver detalhes, versões e curadoria.</p>
<div class="chips">{chips}</div>
<form class="filters" method="get">
  <label style="margin:0">Busca
    <input name="text" placeholder="Buscar nome, descrição…" value="{val('text')}"></label>
  <label style="margin:0">Bloom
    <select name="bloom">{_selected(bloom_opts, val('bloom'))}</select></label>
  <label style="margin:0">Mecânica
    <select name="type">{_selected(type_opts, val('type'))}</select></label>
  <label style="margin:0">Domínio
    <input name="domain" placeholder="ex.: Matemática" value="{val('domain')}"></label>
  <label style="margin:0">Status
    <select name="status">{_selected(
        '<option value="">Todos</option>'
        '<option value="canonical">canônico</option>'
        '<option value="experimental">experimental</option>',
        val('status'))}</select></label>
  <button class="btn" type="submit">Filtrar</button>
</form>
<div class="complist">
  {cards or '<p class="muted">Nenhum componente encontrado para os filtros atuais.</p>'}
</div>"""
    return layout("Biblioteca", body, "/library")


# --------------------------------------------------------------------------- #
# Component detail
# --------------------------------------------------------------------------- #
def component_page(comp: Any, versions: List[Dict], history: List[Dict]) -> str:
    params = "".join(f"<li><b>{esc(k)}</b>: {esc(v)}</li>" for k, v in comp.params.items())
    vrows  = "".join(
        f"<tr><td>v{v['version']}</td><td>{esc(v['change_note'])}</td>"
        f"<td class='muted small'>{esc(v['created_at'])}</td></tr>" for v in versions)
    hrows  = "".join(
        f"<tr><td>{esc(h['action'])}</td><td>{esc(h['curator'] or '—')}</td>"
        f"<td>{esc(h['justification'] or '')}</td></tr>" for h in history)
    refs   = "".join(f"<li>{esc(r)}</li>" for r in comp.references) or "<li class='muted'>—</li>"
    m = comp.metrics
    body = f"""
<a href="/library" class="muted">&larr; Biblioteca</a>
<h1>{esc(comp.name)} {status_badge(comp.status)}</h1>
<p class="muted">{esc(comp.key)} &middot; v{comp.current_version} &middot; autor: {esc(comp.author or '—')}</p>
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
    <p>{bloom_badge(comp.bloom_level)} &middot; {esc(comp.mechanic_type)}</p>
    <p class="muted small">Domínio: {esc(comp.domain or '—')}<br>
       Contexto: {esc(comp.context or '—')} &middot; {esc(comp.age_range or '—')}</p>
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


# --------------------------------------------------------------------------- #
# Curator
# --------------------------------------------------------------------------- #
def curator_page(queue: List[Any]) -> str:
    cards = ""
    for c in queue:
        cards += f"""
<div class="card curate" data-id="{c.id}">
  <div class="row" style="align-items:flex-start">
    <div style="flex:1">
      <b>{esc(c.name)}</b> {bloom_badge(c.bloom_level)}
      <span class="pill muted small">{esc(c.mechanic_type)}</span>
    </div>
    <span class="muted small" style="white-space:nowrap">
      instâncias: {c.metrics.instantiations} &middot;
      aval.: {f'{c.metrics.avg_rating:.1f}' if c.metrics.avg_rating else '—'}
    </span>
  </div>
  <pre class="code small" style="margin:.6rem 0">{esc(c.dsl_signature)}</pre>
  <p class="muted small">{esc(c.description)}</p>
  <div class="actions">
    <button class="btn ok sm" onclick="CUR.act({c.id},'approve')">
      &#10003; Aprovar (&#8594; canônico)</button>
    <button class="btn ghost sm" onclick="CUR.act({c.id},'request_changes')">
      &#9998; Solicitar revisão</button>
    <button class="btn bad sm" onclick="CUR.act({c.id},'reject')">
      &#10007; Rejeitar</button>
  </div>
</div>"""
    body = f"""
<h1>Fila de curadoria <span class="rf">RF12</span></h1>
<p class="muted">Componentes experimentais aguardando revisão. Aprovar promove a
   canônico (priorizado pelo Agente de Recuperação).</p>
{cards or '<p class="muted">Fila vazia — nenhum componente experimental pendente.</p>'}
<script src="/static/curator.js"></script>"""
    return layout("Curadoria", body, "/curator")


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def report_page(report: Dict[str, Any]) -> str:
    s        = report["summary"]
    dim_rows = ""
    chart    = ""
    has_data = False

    for d in report["by_dimension"]:
        dim_rows += (
            f"<tr><td>{esc(d['label'])}</td>"
            f"<td>{_barcell(d['auto'])}</td>"
            f"<td>{_barcell(d['manual'])}</td>"
            f"<td>{_delta(d['delta'])}</td></tr>")
        if d.get("auto") is not None or d.get("manual") is not None:
            has_data = True
        chart += (
            f'<div class="bc-row"><span>{esc(d["label"])}</span>'
            f'<div class="bc-track">'
            f'{_bar("bc-auto", d.get("auto"))}'
            f'{_bar("bc-manual", d.get("manual"))}'
            f'</div></div>')

    chart_block = ("" if not has_data else f"""
<h3>Comparativo por dimensão (automático &times; manual)</h3>
<div class="legend">
  <span><i style="background:var(--primary)"></i>Automático</span>
  <span><i style="background:var(--bloom-2)"></i>Manual</span>
</div>
<div class="barchart">{chart}</div>""")

    bloom_rows  = "".join(
        f"<tr><td>{bloom_badge(k)}</td>"
        f"<td>{_fmt(v['auto_mean'])} ({v['n_auto']})</td>"
        f"<td>{_fmt(v['manual_mean'])} ({v['n_manual']})</td></tr>"
        for k, v in report["by_bloom"].items())
    domain_rows = "".join(
        f"<tr><td>{esc(k)}</td>"
        f"<td>{_fmt(v['auto_mean'])} ({v['n_auto']})</td>"
        f"<td>{_fmt(v['manual_mean'])} ({v['n_manual']})</td></tr>"
        for k, v in report["by_domain"].items())

    body = f"""
<h1>Relatório comparativo <span class="rf">RF24–RF26</span></h1>
<div class="grid4">
  <div class="stat"><b>{_fmt(s['auto']['overall_mean'])}</b>
    <span>auto (n={s['auto']['n']})</span></div>
  <div class="stat"><b>{_fmt(s['manual']['overall_mean'])}</b>
    <span>manual (n={s['manual']['n']})</span></div>
  <div class="stat"><b>{_delta(s['overall_delta'])}</b><span>diferença</span></div>
  <div class="stat"><a class="btn ghost" href="/api/report?format=csv">&#8595; CSV (RF25)</a></div>
</div>
<p class="callout">{esc(report['interpretation'])}</p>
{chart_block}
<h3>Por dimensão pedagógica</h3>
<table class="grid">
  <tr><th>Dimensão</th><th>Automático</th><th>Manual</th><th>&#916;</th></tr>
  {dim_rows}
</table>
<div class="row2">
  <div><h3>Por nível de Bloom</h3>
    <table class="grid"><tr><th>Bloom</th><th>Auto</th><th>Manual</th></tr>
    {bloom_rows or '<tr><td colspan=3 class=muted>—</td></tr>'}</table></div>
  <div><h3>Por domínio</h3>
    <table class="grid"><tr><th>Domínio</th><th>Auto</th><th>Manual</th></tr>
    {domain_rows or '<tr><td colspan=3 class=muted>—</td></tr>'}</table></div>
</div>"""
    return layout("Relatórios", body, "/report")


# --------------------------------------------------------------------------- #
# Docs
# --------------------------------------------------------------------------- #
def docs_page(grammar: str, limits: Dict[str, Any]) -> str:
    def group(title, items, cls):
        rows = "".join(
            f"<li><b>{esc(i['name'])}</b> — {esc(i['rationale'])}</li>"
            for i in items)
        return f'<div class="card {cls}"><h3>{esc(title)}</h3><ul>{rows}</ul></div>'

    mechs = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(v.label)}</td>"
        f"<td>{', '.join(sorted(b.pt for b in v.bloom_affinity))}</td></tr>"
        for k, v in sorted(MECHANIC_TYPES.items()))

    body = f"""
<h1>Gramática &amp; limites <span class="rf">RF01 &middot; RF02 &middot; RF06</span></h1>
<h3>Gramática formal (EBNF)</h3>
<pre class="code">{esc(grammar)}</pre>
<h3>Tipos de mecânica e afinidade cognitiva (RF04)</h3>
<table class="grid">
  <tr><th>Tipo</th><th>Rótulo</th><th>Níveis de Bloom afins</th></tr>
  {mechs}
</table>
<h3>Limites da formalização (RF06)</h3>
<div class="cards">
  {group('Formalizados', limits['formalized'], 'ok')}
  {group('Parcialmente formalizados', limits['partial'], 'warn')}
  {group('Controle humano deliberado', limits['human'], 'bad')}
</div>"""
    return layout("Gramática", body, "/docs")


# --------------------------------------------------------------------------- #
# Evaluate
# --------------------------------------------------------------------------- #
def evaluate_page(proto: Dict[str, Any]) -> str:
    dims = "".join(f"""
<div class="dimrow">
  <label>{esc(d.label)}<br>
    <span class="muted small">{esc(d.question)}</span></label>
  <div class="likert" data-dim="{d.key}">
    {''.join(f'<button type="button" onclick="EV.set(this,{n})">{n}</button>' for n in range(1,6))}
  </div>
</div>""" for d in DIMENSIONS)

    body = f"""
<a href="/prototype/{proto['id']}" class="muted">&larr; Protótipo</a>
<h1>Avaliar protótipo #{proto['id']} <span class="rf">RF24 &middot; RF25</span></h1>
<p class="muted">{esc(proto.get('title',''))} &middot; origem: {esc(proto.get('origin'))}</p>
<form id="evalform" data-pid="{proto['id']}" data-origin="{esc(proto.get('origin','auto'))}">
  {dims}
  <label>Avaliador<input id="evaluator" placeholder="seu nome"></label>
  <label>Comentários<textarea id="comments"></textarea></label>
  <div class="actions">
    <button class="btn" type="button" onclick="EV.submit()">Registrar avaliação</button>
    <span id="evstatus" class="muted"></span>
  </div>
</form>
<script src="/static/evaluate.js"></script>"""
    return layout("Avaliação", body, "/report")


# --------------------------------------------------------------------------- #
# Error / 404
# --------------------------------------------------------------------------- #
def not_found(msg: str) -> str:
    return layout("Não encontrado",
                  f'<div class="card"><h1>404</h1><p>{esc(msg)}</p>'
                  '<a class="btn" href="/">Início</a></div>')


def error_page(msg: str, tb: str) -> str:
    return layout("Erro",
                  f'<div class="card bad"><h1>Erro</h1><p>{esc(msg)}</p>'
                  f'<pre class="code small">{esc(tb)}</pre></div>')


# --------------------------------------------------------------------------- #
# Helpers
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


def _bar(cls: str, v) -> str:
    if v is None:
        return ""
    pct = max(0, min(100, int(round(v / 5 * 100))))
    return f'<div class="bc-fill {cls}" style="width:{pct}%">{v:.1f}</div>'


def _barcell(v) -> str:
    if v is None:
        return '<span class="muted">—</span>'
    pct = int(round(v / 5 * 100))
    return (f'<div class="minibar"><i style="width:{pct}%"></i></div>'
            f'<span class="small">{v:.2f}</span>')
