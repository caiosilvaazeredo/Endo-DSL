"""Engine HTML5/JS dos protótipos gerados (RF19, RF21, RF22).

O protótipo é um único arquivo HTML autocontido (CSS + JS embutidos, sem
dependências externas — RF19). A jogabilidade é dirigida por um *content pack*
(JSON embutido em ``window.ENDO_GAME``), de modo que a **estrutura** (mecânicas,
níveis de Bloom, interações) fica separada do **conteúdo** (itens jogáveis),
permitindo reparametrização de domínio sem recompilar (RF22).

Os níveis de Bloom de cada mecânica são preservados no content pack e expostos
como atributos ``data-bloom`` no DOM (RF21).
"""

from __future__ import annotations

import json
from typing import Any, Dict

# --------------------------------------------------------------------------- #
# CSS — tema escuro sóbrio, responsivo, sem dependências.
# --------------------------------------------------------------------------- #
_CSS = """
:root{
  --bg:#0f1320; --panel:#1a2034; --panel2:#222a44; --ink:#e8ecf6; --muted:#9aa6c4;
  --accent:#5b8cff; --good:#37c98b; --bad:#ff6b6b; --warn:#ffc857;
  --b1:#7b61ff;--b2:#3aa0ff;--b3:#23c4a8;--b4:#ffb020;--b5:#ff7a59;--b6:#ff5d8f;
}
*{box-sizing:border-box}
body{margin:0;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  background:linear-gradient(160deg,#0c1020,#141a2e);color:var(--ink);min-height:100vh}
.wrap{max-width:820px;margin:0 auto;padding:24px}
header.game{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
h1{margin:0;font-size:1.7rem;letter-spacing:.3px}
.sub{color:var(--muted);font-size:.95rem}
.card{background:var(--panel);border:1px solid #2a3354;border-radius:16px;
  padding:22px;box-shadow:0 10px 30px rgba(0,0,0,.25);margin-bottom:18px}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
.badge{font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:999px;
  text-transform:uppercase;letter-spacing:.4px;color:#0b0f1c}
.bloom-1{background:var(--b1);color:#fff}.bloom-2{background:var(--b2);color:#fff}
.bloom-3{background:var(--b3)}.bloom-4{background:var(--b4)}
.bloom-5{background:var(--b5)}.bloom-6{background:var(--b6);color:#fff}
.tag{background:var(--panel2);color:var(--muted);font-size:.72rem;padding:4px 10px;
  border-radius:999px;border:1px solid #313b60}
.prompt{font-size:1.15rem;margin:6px 0 16px;line-height:1.45}
.options{display:grid;gap:10px}
button.opt,button.chip{font:inherit;text-align:left;background:var(--panel2);color:var(--ink);
  border:1px solid #38426c;border-radius:12px;padding:13px 16px;cursor:pointer;
  transition:.12s transform,.12s background}
button.opt:hover,button.chip:hover{background:#2c365a;transform:translateY(-1px)}
button.opt.correct{background:rgba(55,201,139,.22);border-color:var(--good)}
button.opt.wrong{background:rgba(255,107,107,.18);border-color:var(--bad)}
button.opt:disabled,button.chip:disabled{cursor:default;opacity:.85}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.col h4{margin:.2rem 0 .6rem;color:var(--muted);font-weight:600;font-size:.85rem}
.chip.sel{outline:2px solid var(--accent);background:#33406e}
.chip.done{opacity:.45}
.buckets{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px}
.bucket{background:var(--panel2);border:1px dashed #46517e;border-radius:12px;padding:12px;min-height:70px}
.bucket h4{margin:0 0 8px;font-size:.85rem;color:var(--muted)}
.bucket .item{background:#33406e;border-radius:8px;padding:6px 10px;margin:4px 0;font-size:.9rem}
.seq{display:flex;flex-direction:column;gap:8px}
.slot{display:flex;gap:8px;align-items:center}
.slot .n{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem}
.bar{height:8px;background:#222a44;border-radius:999px;overflow:hidden;margin:14px 0}
.bar > i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--b3));width:0;transition:.4s}
.feedback{margin-top:14px;padding:12px 14px;border-radius:12px;font-size:.95rem;display:none}
.feedback.show{display:block}
.feedback.ok{background:rgba(55,201,139,.15);border:1px solid var(--good)}
.feedback.no{background:rgba(255,107,107,.13);border:1px solid var(--bad)}
.row{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.btn{background:var(--accent);color:#fff;border:none;border-radius:12px;padding:12px 22px;
  font:inherit;font-weight:700;cursor:pointer}
.btn:hover{filter:brightness(1.08)}
.btn.ghost{background:transparent;border:1px solid #3a456e;color:var(--ink)}
.muted{color:var(--muted)}
.kv{display:flex;gap:8px;flex-wrap:wrap;font-size:.85rem;color:var(--muted)}
.kv b{color:var(--ink);font-weight:600}
.score{font-size:2.4rem;font-weight:800}
table.trace{width:100%;border-collapse:collapse;font-size:.9rem}
table.trace th,table.trace td{border-bottom:1px solid #2a3354;padding:8px;text-align:left;vertical-align:top}
table.trace th{color:var(--muted);font-weight:600}
footer{color:var(--muted);font-size:.78rem;text-align:center;margin:24px 0}
"""

# --------------------------------------------------------------------------- #
# JS — engine de jogabilidade. Lê window.ENDO_GAME e renderiza estágios.
# Sem dependências externas. Interações: choose, order, match, classify, info.
# --------------------------------------------------------------------------- #
_JS = r"""
(function(){
  const G = window.ENDO_GAME;
  const app = document.getElementById('app');
  let stageIdx = 0, totalScore = 0, maxScore = 0;
  const bloomVisited = new Set();

  const el = (t,c,txt)=>{const e=document.createElement(t); if(c)e.className=c; if(txt!=null)e.textContent=txt; return e;};
  const bloomBadge = (b)=>{ if(!b) return null; const e=el('span','badge bloom-'+b.level, b.name); e.setAttribute('data-bloom', b.name); return e; };

  function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}

  function header(){
    const h = el('header','game');
    h.appendChild(el('h1', G.title));
    const sub = el('div','sub', (G.meta.domain? G.meta.domain+' · ':'') + (G.meta.audience||''));
    h.appendChild(sub);
    return h;
  }

  function progress(){
    const bar = el('div','bar'); const i = el('i'); bar.appendChild(i);
    requestAnimationFrame(()=>{ i.style.width = Math.round(100*stageIdx/G.stages.length)+'%'; });
    return bar;
  }

  function start(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    c.appendChild(el('div','muted','Protótipo educacional endógeno gerado pela Endo-DSL'));
    const badges = el('div','badges');
    (G.bloom_levels||[]).forEach(b=>{const x=bloomBadge(b); if(x)badges.appendChild(x);});
    c.appendChild(badges);
    const ul = el('div','kv');
    ul.innerHTML = '<span><b>Objetivos:</b> '+G.objectives.length+'</span>'+
                   '<span><b>Mecânicas:</b> '+G.stages.length+'</span>'+
                   '<span><b>Duração estimada:</b> '+(G.meta.duration||'—')+' min</span>';
    c.appendChild(ul);
    if(G.objectives.length){
      const list = el('ul'); list.style.color='var(--muted)';
      G.objectives.forEach(o=>{const li=el('li'); li.innerHTML='<b style="color:var(--ink)">'+o.bloom_name+':</b> '+o.description; list.appendChild(li);});
      c.appendChild(list);
    }
    const btn = el('button','btn','▶ Começar'); btn.onclick=()=>{stageIdx=0;totalScore=0;maxScore=0;bloomVisited.clear();renderStage();};
    const row = el('div','row'); row.appendChild(btn);
    const tbtn = el('button','btn ghost','Ver rastreabilidade'); tbtn.onclick=showTrace; row.appendChild(tbtn);
    c.appendChild(row);
    app.appendChild(c);
  }

  function renderStage(){
    if(stageIdx>=G.stages.length){ return finish(); }
    const s = G.stages[stageIdx];
    if(s.bloom) bloomVisited.add(s.bloom.name);
    app.innerHTML=''; app.appendChild(header()); app.appendChild(progress());
    const c = el('div','card'); c.setAttribute('data-mechanic', s.mechanic);
    if(s.bloom) c.setAttribute('data-bloom', s.bloom.name);
    const top = el('div','row');
    const tags = el('div','badges');
    const bb = bloomBadge(s.bloom); if(bb) tags.appendChild(bb);
    tags.appendChild(el('span','tag', s.type_label||s.mechanic));
    top.appendChild(tags);
    top.appendChild(el('span','muted','Etapa '+(stageIdx+1)+'/'+G.stages.length));
    c.appendChild(top);
    if(s.description){ const d=el('div','muted'); d.style.margin='6px 0 4px'; d.textContent=s.description; c.appendChild(d); }
    app.appendChild(c);
    const host = el('div'); c.appendChild(host);
    const render = INTERACTIONS[s.interaction] || INTERACTIONS.info;
    render(host, s, (gained, max)=>{ totalScore+=gained; maxScore+=max; });
  }

  function nextButton(host, label){
    const row = el('div','row'); row.style.marginTop='14px';
    const b = el('button','btn', label||'Continuar →');
    b.onclick=()=>{ stageIdx++; renderStage(); };
    row.appendChild(b); host.appendChild(row); return b;
  }

  // ---- Interações ----
  const INTERACTIONS = {
    info: function(host, s, score){
      const p = el('div','prompt', (s.content && s.content.text) || 'Reflita sobre o desafio proposto.');
      host.appendChild(p);
      score(1,1);
      nextButton(host);
    },

    choose: function(host, s, score){
      const items = s.content.items||[]; let idx=0; let gained=0;
      const promptEl = el('div','prompt'); host.appendChild(promptEl);
      const opts = el('div','options'); host.appendChild(opts);
      const fb = el('div','feedback'); host.appendChild(fb);
      function step(){
        if(idx>=items.length){ score(gained, items.length); return nextButton(host); }
        const it = items[idx];
        promptEl.textContent = it.prompt;
        opts.innerHTML=''; fb.className='feedback';
        const order = it.shuffle===false? it.options.map((o,i)=>i) : shuffle(it.options.map((o,i)=>i));
        order.forEach(oi=>{
          const b = el('button','opt', it.options[oi]);
          b.onclick=()=>{
            Array.from(opts.children).forEach(x=>x.disabled=true);
            const correct = oi===it.correct;
            if(correct){ b.classList.add('correct'); gained++; }
            else { b.classList.add('wrong'); const cb=opts.children[order.indexOf(it.correct)]; if(cb)cb.classList.add('correct'); }
            fb.className='feedback show '+(correct?'ok':'no');
            fb.textContent = (correct?'✓ ':'✗ ') + (it.explanation || (correct?'Correto!':'Resposta correta destacada.'));
            const nb = el('button','btn', idx+1>=items.length?'Concluir etapa →':'Próximo →');
            nb.style.marginTop='12px'; nb.onclick=()=>{idx++; step();}; fb.appendChild(document.createElement('br')); fb.appendChild(nb);
          };
          opts.appendChild(b);
        });
      }
      step();
    },

    order: function(host, s, score){
      const correct = s.content.items||[]; const pool = shuffle(correct.map((t,i)=>({t,i})));
      host.appendChild(el('div','prompt', s.content.prompt||'Coloque os itens na ordem correta:'));
      const chips = el('div','options'); host.appendChild(chips);
      const seq = el('div','seq'); seq.style.marginTop='12px'; host.appendChild(seq);
      const fb = el('div','feedback'); host.appendChild(fb);
      const chosen=[];
      function redraw(){
        seq.innerHTML='';
        chosen.forEach((c,n)=>{const slot=el('div','slot'); slot.appendChild(el('span','n', (n+1))); slot.appendChild(el('span',null,c.t)); seq.appendChild(slot);});
      }
      pool.forEach(p=>{
        const b=el('button','chip', p.t);
        b.onclick=()=>{ if(b.classList.contains('done'))return; b.classList.add('done'); b.disabled=true; chosen.push(p); redraw();
          if(chosen.length===correct.length){ check(); } };
        chips.appendChild(b);
      });
      function check(){
        let ok=0; chosen.forEach((c,n)=>{ if(c.i===n) ok++; });
        const perfect = ok===correct.length;
        fb.className='feedback show '+(perfect?'ok':'no');
        fb.textContent=(perfect?'✓ Ordem correta!':'✗ '+ok+'/'+correct.length+' nas posições certas. Ordem correta: '+correct.join(' → '));
        score(ok, correct.length); nextButton(host);
      }
    },

    match: function(host, s, score){
      const pairs = s.content.pairs||[];
      host.appendChild(el('div','prompt', s.content.prompt||'Associe os pares correspondentes:'));
      const cols = el('div','cols'); host.appendChild(cols);
      const left = el('div','col'); left.appendChild(el('h4','Coluna A'));
      const right = el('div','col'); right.appendChild(el('h4','Coluna B'));
      cols.appendChild(left); cols.appendChild(right);
      const fb = el('div','feedback'); host.appendChild(fb);
      let sel=null, matched=0, errors=0;
      pairs.forEach((p,i)=>{ const b=el('button','chip',p.a); b.dataset.k=i; b.onclick=()=>{ if(b.disabled)return; clearSel(); sel=b; b.classList.add('sel'); }; left.appendChild(b); });
      shuffle(pairs.map((p,i)=>({t:p.b,k:i}))).forEach(r=>{ const b=el('button','chip',r.t); b.dataset.k=r.k;
        b.onclick=()=>{ if(!sel||b.disabled)return; if(b.dataset.k===sel.dataset.k){ b.disabled=sel.disabled=true; b.classList.add('done'); sel.classList.remove('sel'); sel.classList.add('done'); matched++; if(matched===pairs.length)done(); }
          else { errors++; flash(b); flash(sel); } clearSel(); };
        right.appendChild(b); });
      function clearSel(){ if(sel){sel.classList.remove('sel'); sel=null;} }
      function flash(b){ b.classList.add('wrong'); setTimeout(()=>b.classList.remove('wrong'),300); }
      function done(){ fb.className='feedback show ok'; fb.textContent='✓ Todos os pares associados ('+errors+' tentativas erradas).'; score(Math.max(0,pairs.length-errors), pairs.length); nextButton(host); }
    },

    classify: function(host, s, score){
      const cats = s.content.categories||[]; const items = shuffle((s.content.items||[]).slice());
      host.appendChild(el('div','prompt', s.content.prompt||'Classifique cada item na categoria correta:'));
      const itemRow = el('div','options'); host.appendChild(itemRow);
      const buckets = el('div','buckets'); host.appendChild(buckets);
      const fb = el('div','feedback'); host.appendChild(fb);
      let sel=null, placed=0, correct=0;
      const bucketEls={};
      cats.forEach(cat=>{ const bk=el('div','bucket'); bk.appendChild(el('h4',cat)); bk.onclick=()=>{ if(!sel)return; const it=sel.__item;
          const ok = it.category===cat; placed++; if(ok)correct++;
          const tag=el('div','item', it.text + (ok?' ✓':' ✗ ('+it.category+')')); bk.appendChild(tag);
          sel.disabled=true; sel.classList.add('done'); sel=null;
          if(placed===items.length){ fb.className='feedback show '+(correct===items.length?'ok':'no'); fb.textContent=(correct===items.length?'✓ ':'✗ ')+correct+'/'+items.length+' classificados corretamente.'; score(correct, items.length); nextButton(host);} };
        bucketEls[cat]=bk; buckets.appendChild(bk); });
      items.forEach(it=>{ const b=el('button','chip', it.text); b.__item=it; b.onclick=()=>{ if(b.disabled)return; if(sel)sel.classList.remove('sel'); sel=b; b.classList.add('sel'); }; itemRow.appendChild(b); });
    }
  };

  function finish(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    const pct = maxScore? Math.round(100*totalScore/maxScore):0;
    c.appendChild(el('div','muted','Protótipo concluído'));
    c.appendChild(el('div','score', pct+'%'));
    c.appendChild(el('div',null,'Pontuação: '+totalScore+' de '+maxScore));
    const badges = el('div','badges'); badges.style.marginTop='12px';
    badges.appendChild(el('span','muted','Níveis de Bloom exercitados: '));
    (G.bloom_levels||[]).forEach(b=>{ if(bloomVisited.has(b.name)){ const x=bloomBadge(b); if(x)badges.appendChild(x);} });
    c.appendChild(badges);
    const row=el('div','row'); row.style.marginTop='10px';
    const again=el('button','btn','↻ Jogar de novo'); again.onclick=()=>{stageIdx=0;totalScore=0;maxScore=0;bloomVisited.clear();renderStage();};
    const tb=el('button','btn ghost','Ver rastreabilidade'); tb.onclick=showTrace;
    row.appendChild(again); row.appendChild(tb); c.appendChild(row);
    app.appendChild(c);
  }

  function showTrace(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    c.appendChild(el('h1','Rastreabilidade pedagógica'));
    c.appendChild(el('div','muted','Vínculo entre objetivos de aprendizagem e mecânicas (RF23).'));
    const t = el('table','trace');
    t.innerHTML='<tr><th>Objetivo</th><th>Bloom</th><th>Mecânicas que o endereçam</th></tr>';
    (G.traceability.links||[]).forEach(L=>{
      const tr=el('tr');
      tr.innerHTML='<td>'+L.objective_description+'</td><td>'+L.bloom+'</td><td>'+
        (L.mechanics.map(m=>m.name+' <span class="muted">('+m.type+', '+m.bloom+')</span>').join('<br>')||'<span class="muted">— nenhuma —</span>')+'</td>';
      t.appendChild(tr);
    });
    c.appendChild(t);
    const back=el('button','btn ghost','← Voltar'); back.style.marginTop='14px'; back.onclick=start; c.appendChild(back);
    app.appendChild(c);
  }

  start();
})();
"""

_HTML_SHELL = """<!doctype html>
<html lang="pt-br" data-endo-dsl="1" data-bloom-levels="__BLOOM_DATA__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="Endo-DSL Compiler v__VERSION__">
<meta name="endo-dsl:bloom-levels" content="__BLOOM_META__">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap"><div id="app"></div>
<footer>Gerado por <b>Endo-DSL</b> · protótipo educacional endógeno · níveis de Bloom rastreáveis (data-bloom)</footer>
</div>
<!-- ENDO-DSL CONTENT PACK: estrutura (mecânicas/Bloom) separada do conteúdo, permitindo reparametrização (RF22) -->
<script id="endo-content" type="application/json">__CONTENT_PACK__</script>
<script>window.ENDO_GAME = JSON.parse(document.getElementById('endo-content').textContent);</script>
<script>__JS__</script>
</body>
</html>
"""


def render_html(content_pack: Dict[str, Any], version: str = "1.0.0") -> str:
    """Monta o arquivo HTML autocontido a partir do *content pack*."""
    bloom_names = [b["name"] for b in content_pack.get("bloom_levels", [])]
    pack_json = json.dumps(content_pack, ensure_ascii=False)
    # Evita que '</script>' no conteúdo quebre o documento.
    pack_json = pack_json.replace("</", "<\\/")
    html = _HTML_SHELL
    html = html.replace("__CSS__", _CSS)
    html = html.replace("__JS__", _JS)
    html = html.replace("__TITLE__", _escape(content_pack.get("title", "Protótipo Endo-DSL")))
    html = html.replace("__CONTENT_PACK__", pack_json)
    html = html.replace("__VERSION__", version)
    html = html.replace("__BLOOM_META__", _escape(", ".join(bloom_names)))
    html = html.replace("__BLOOM_DATA__", _escape(json.dumps(bloom_names, ensure_ascii=False)))
    return html


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
