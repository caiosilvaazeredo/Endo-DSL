/* Construtor de Blocos MDA — /builder
 *
 * Três painéis de blocos (mecânicas, dinâmicas, estéticas) carregados de
 * /api/builder/catalogs, mais um editor de fluxo estilo BPMN em SVG.
 * Gera a DSL boardgame{} via /api/builder/dsl e o jogo via /api/builder/generate.
 */
const BLD = {
  catalogs: null,
  sel: { mechanics: {}, dynamics: new Set(), aesthetics: new Set() },
  flow: { nodes: [], edges: [] },
  _nodeSeq: 1,
  _selectedNode: null,
  _connectFrom: null,
  _connecting: false,
  _drag: null,

  /* ── init ─────────────────────────────────────────────────────────── */
  async init() {
    try {
      const resp = await fetch('/api/builder/catalogs');
      this.catalogs = await resp.json();
    } catch (e) {
      alert('Não foi possível carregar os catálogos: ' + e.message);
      return;
    }
    this.renderGrid('mechanics');
    this.renderGrid('dynamics');
    this.renderGrid('aesthetics');
    this.renderFlowPalette();
    this.bindFlowCanvas();
    this.restore();
  },

  /* ── painéis de blocos ───────────────────────────────────────────── */
  renderGrid(kind) {
    const grid = document.getElementById('grid-' + kind);
    const cat = this.catalogs[kind];
    grid.innerHTML = '';
    for (const [id, b] of Object.entries(cat)) {
      const div = document.createElement('div');
      div.className = 'bld-block';
      div.dataset.id = id;
      div.dataset.kind = kind;
      div.dataset.text = (b.name + ' ' + b.desc + ' ' + (b.inspired_by || '') +
                          ' ' + (b.category || '')).toLowerCase();
      let extra = '';
      if (kind === 'aesthetics' && b.theme) {
        extra = '<span class="bld-swatch">' +
          ['primary', 'secondary', 'bg', 'surface'].map(k =>
            `<i style="background:${b.theme[k]}"></i>`).join('') + '</span>';
      }
      let params = '';
      if (kind === 'mechanics' && b.params && Object.keys(b.params).length) {
        params = '<div class="bld-params" onclick="event.stopPropagation()">' +
          Object.entries(b.params).map(([k, v]) => {
            const t = (typeof v === 'number') ? 'number' : 'text';
            const val = (typeof v === 'boolean') ? String(v) : v;
            return `<label>${k}<input type="${t}" value="${val}" data-param="${k}"
                     onchange="BLD.setParam('${id}','${k}',this.value)"></label>`;
          }).join('') + '</div>';
      }
      div.innerHTML = `
        <span class="bld-cat">${b.category || ''}</span>
        <h4><input type="checkbox" class="bld-check" tabindex="-1">${b.name}</h4>
        <p>${b.desc}</p>
        ${b.inspired_by ? `<span class="bld-insp">inspirado em: ${b.inspired_by}</span>` : ''}
        ${extra}${params}`;
      div.addEventListener('click', () => this.toggle(kind, id, div));
      grid.appendChild(div);
    }
  },

  toggle(kind, id, div) {
    if (kind === 'mechanics') {
      if (this.sel.mechanics[id]) delete this.sel.mechanics[id];
      else this.sel.mechanics[id] = { id, params: {} };
    } else {
      const s = this.sel[kind];
      s.has(id) ? s.delete(id) : s.add(id);
    }
    const on = kind === 'mechanics' ? !!this.sel.mechanics[id] : this.sel[kind].has(id);
    div.classList.toggle('selected', on);
    div.querySelector('.bld-check').checked = on;
    this.updateCounts();
    this.persist();
  },

  setParam(mechId, key, value) {
    if (!this.sel.mechanics[mechId]) return;
    const n = Number(value);
    this.sel.mechanics[mechId].params[key] =
      value === 'true' ? true : value === 'false' ? false : (isNaN(n) || value === '' ? value : n);
    this.persist();
  },

  updateCounts() {
    document.getElementById('cnt-mechanics').textContent =
      Object.keys(this.sel.mechanics).length;
    document.getElementById('cnt-dynamics').textContent = this.sel.dynamics.size;
    document.getElementById('cnt-aesthetics').textContent = this.sel.aesthetics.size;
  },

  setTab(tab) {
    document.querySelectorAll('.bld-tab').forEach(b =>
      b.classList.toggle('active', b.dataset.tab === tab));
    ['mechanics', 'dynamics', 'aesthetics', 'flow'].forEach(t =>
      document.getElementById('panel-' + t).classList.toggle('hidden', t !== tab));
  },

  filter(q) {
    q = q.trim().toLowerCase();
    document.querySelectorAll('.bld-block').forEach(b =>
      b.classList.toggle('hidden-by-filter', q && !b.dataset.text.includes(q)));
  },

  /* ── editor de fluxo BPMN ────────────────────────────────────────── */
  renderFlowPalette() {
    const pal = document.getElementById('bld-flow-palette');
    pal.innerHTML = '';
    for (const [type, t] of Object.entries(this.catalogs.flow_node_types)) {
      const btn = document.createElement('button');
      btn.className = 'bld-node-add';
      btn.textContent = '+ ' + t.name;
      btn.title = t.desc;
      btn.addEventListener('click', () => this.flowAddNode(type, t.name));
      pal.appendChild(btn);
    }
  },

  flowAddNode(type, label) {
    const id = 'n' + (this._nodeSeq++);
    const n = this.flow.nodes.length;
    this.flow.nodes.push({
      id, type, label,
      x: 90 + (n % 5) * 170, y: 70 + Math.floor(n / 5) * 110,
    });
    this.drawFlow();
    this.persist();
  },

  bindFlowCanvas() {
    const svg = document.getElementById('bld-flow-canvas');
    svg.addEventListener('mousemove', ev => {
      if (!this._drag) return;
      const pt = this._svgPoint(svg, ev);
      this._drag.node.x = pt.x - this._drag.dx;
      this._drag.node.y = pt.y - this._drag.dy;
      this.drawFlow();
    });
    svg.addEventListener('mouseup', () => {
      if (this._drag) { this._drag = null; this.persist(); }
    });
    svg.addEventListener('mouseleave', () => { this._drag = null; });
  },

  _svgPoint(svg, ev) {
    const r = svg.getBoundingClientRect();
    return { x: ev.clientX - r.left, y: ev.clientY - r.top };
  },

  drawFlow() {
    const gN = document.getElementById('bld-flow-nodes');
    const gE = document.getElementById('bld-flow-edges');
    const NS = 'http://www.w3.org/2000/svg';
    gN.innerHTML = ''; gE.innerHTML = '';
    const byId = {};
    this.flow.nodes.forEach(n => { byId[n.id] = n; });

    for (const e of this.flow.edges) {
      const a = byId[e.from], b = byId[e.to];
      if (!a || !b) continue;
      const p = document.createElementNS(NS, 'path');
      const mx = (a.x + b.x) / 2;
      p.setAttribute('d', `M ${a.x} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x} ${b.y}`);
      p.setAttribute('class', 'bld-fedge');
      gE.appendChild(p);
    }

    for (const n of this.flow.nodes) {
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'bld-fnode' + (this._selectedNode === n.id ? ' selected' : ''));
      g.setAttribute('transform', `translate(${n.x},${n.y})`);
      let shape;
      if (n.type === 'start' || n.type === 'end' || n.type === 'event' || n.type === 'timer') {
        shape = document.createElementNS(NS, 'circle');
        shape.setAttribute('r', 24);
        if (n.type === 'end') shape.setAttribute('stroke-width', '4');
      } else if (n.type === 'gateway' || n.type === 'parallel') {
        shape = document.createElementNS(NS, 'rect');
        shape.setAttribute('x', -26); shape.setAttribute('y', -26);
        shape.setAttribute('width', 52); shape.setAttribute('height', 52);
        shape.setAttribute('transform', 'rotate(45)');
        shape.setAttribute('rx', 6);
      } else {
        shape = document.createElementNS(NS, 'rect');
        shape.setAttribute('x', -62); shape.setAttribute('y', -26);
        shape.setAttribute('width', 124); shape.setAttribute('height', 52);
        shape.setAttribute('rx', 10);
      }
      shape.setAttribute('class', 'bld-fnode-shape');
      g.appendChild(shape);

      const label = document.createElementNS(NS, 'text');
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('y', n.type.match(/start|end|event|timer|gateway|parallel/) ? 42 : 4);
      label.textContent = n.label.length > 20 ? n.label.slice(0, 19) + '…' : n.label;
      g.appendChild(label);

      g.addEventListener('mousedown', ev => {
        ev.preventDefault();
        if (this._connecting) return;
        const svg = document.getElementById('bld-flow-canvas');
        const pt = this._svgPoint(svg, ev);
        this._drag = { node: n, dx: pt.x - n.x, dy: pt.y - n.y };
        this._selectedNode = n.id;
        this.drawFlow();
      });
      g.addEventListener('click', ev => {
        ev.stopPropagation();
        if (this._connecting) {
          if (!this._connectFrom) { this._connectFrom = n.id; return; }
          if (this._connectFrom !== n.id) {
            this.flow.edges.push({ from: this._connectFrom, to: n.id });
          }
          this._connectFrom = null;
          this._connecting = false;
          document.getElementById('bld-flow-canvas').classList.remove('connecting');
          document.getElementById('bld-btn-connect').classList.remove('primary');
          this.drawFlow();
          this.persist();
        }
      });
      g.addEventListener('dblclick', () => {
        const novo = prompt('Rótulo do nó:', n.label);
        if (novo !== null && novo.trim()) { n.label = novo.trim(); this.drawFlow(); this.persist(); }
      });
      gN.appendChild(g);
    }
  },

  flowConnectMode() {
    this._connecting = !this._connecting;
    this._connectFrom = null;
    document.getElementById('bld-flow-canvas').classList.toggle('connecting', this._connecting);
    document.getElementById('bld-btn-connect').classList.toggle('primary', this._connecting);
  },

  flowDeleteSelected() {
    if (!this._selectedNode) return;
    const id = this._selectedNode;
    this.flow.nodes = this.flow.nodes.filter(n => n.id !== id);
    this.flow.edges = this.flow.edges.filter(e => e.from !== id && e.to !== id);
    this._selectedNode = null;
    this.drawFlow();
    this.persist();
  },

  flowClear() {
    if (!confirm('Limpar todo o fluxo?')) return;
    this.flow = { nodes: [], edges: [] };
    this.drawFlow();
    this.persist();
  },

  /* ── config ──────────────────────────────────────────────────────── */
  config() {
    const v = id => document.getElementById(id).value;
    return {
      title: v('bld-title') || 'Jogo de Blocos',
      domain: v('bld-domain') || 'Geral',
      topic: v('bld-topic') || '',
      bloom: v('bld-bloom'),
      players: parseInt(v('bld-players') || '2', 10),
      duration: parseInt(v('bld-duration') || '30', 10),
      objective: v('bld-objective') || '',
      mechanics: Object.values(this.sel.mechanics),
      dynamics: [...this.sel.dynamics],
      aesthetics: [...this.sel.aesthetics],
      flow: this.flow,
    };
  },

  /* ── DSL / geração ───────────────────────────────────────────────── */
  async showDSL() {
    try {
      const resp = await fetch('/api/builder/dsl', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: this.config() }),
      });
      const data = await resp.json();
      document.getElementById('bld-dsl-content').textContent =
        data.dsl || data.error || '(vazio)';
      document.getElementById('bld-dsl-modal').classList.remove('hidden');
    } catch (e) { alert('Falha: ' + e.message); }
  },

  closeDSL() { document.getElementById('bld-dsl-modal').classList.add('hidden'); },

  copyDSL() {
    navigator.clipboard.writeText(
      document.getElementById('bld-dsl-content').textContent);
  },

  async generate() {
    const cfg = this.config();
    if (!cfg.mechanics.length) {
      alert('Selecione ao menos um bloco de mecânica.');
      this.setTab('mechanics');
      return;
    }
    const btn = document.getElementById('bld-btn-generate');
    btn.disabled = true; btn.textContent = 'Gerando…';
    try {
      const resp = await fetch('/api/builder/generate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: cfg }),
      });
      const data = await resp.json();
      if (data.ok && data.html_url) {
        const dl = document.getElementById('bld-btn-download');
        dl.href = data.html_url + '/download';
        dl.classList.remove('hidden');
        window.open(data.html_url, '_blank');
      }
      else alert('Erro: ' + (data.error || JSON.stringify(data)));
    } catch (e) { alert('Falha: ' + e.message); }
    finally { btn.disabled = false; btn.textContent = '▶ Gerar Jogo'; }
  },

  /* ── persistência local ──────────────────────────────────────────── */
  persist() {
    try {
      localStorage.setItem('endo-builder', JSON.stringify({
        config: this.config(), nodeSeq: this._nodeSeq,
      }));
    } catch (e) { /* quota */ }
  },

  restore() {
    let saved;
    try { saved = JSON.parse(localStorage.getItem('endo-builder')); } catch (e) {}
    if (!saved || !saved.config) return;
    this.applyConfig(saved.config);
    this._nodeSeq = saved.nodeSeq || (this.flow.nodes.length + 1);
  },

  applyConfig(cfg) {
    const set = (id, val) => { const el = document.getElementById(id);
      if (el && val !== undefined && val !== null) el.value = val; };
    set('bld-title', cfg.title); set('bld-domain', cfg.domain);
    set('bld-topic', cfg.topic); set('bld-bloom', cfg.bloom);
    set('bld-players', cfg.players); set('bld-duration', cfg.duration);
    set('bld-objective', cfg.objective);
    this.sel.mechanics = {};
    (cfg.mechanics || []).forEach(m => {
      const o = typeof m === 'string' ? { id: m, params: {} } : m;
      this.sel.mechanics[o.id] = o;
    });
    this.sel.dynamics = new Set(cfg.dynamics || []);
    this.sel.aesthetics = new Set(cfg.aesthetics || []);
    this.flow = cfg.flow && cfg.flow.nodes ? cfg.flow : { nodes: [], edges: [] };
    document.querySelectorAll('.bld-block').forEach(div => {
      const on = div.dataset.kind === 'mechanics'
        ? !!this.sel.mechanics[div.dataset.id]
        : this.sel[div.dataset.kind].has(div.dataset.id);
      div.classList.toggle('selected', on);
      div.querySelector('.bld-check').checked = on;
      if (on && div.dataset.kind === 'mechanics') {
        const saved = this.sel.mechanics[div.dataset.id].params || {};
        div.querySelectorAll('[data-param]').forEach(inp => {
          if (saved[inp.dataset.param] !== undefined) inp.value = saved[inp.dataset.param];
        });
      }
    });
    this.updateCounts();
    this.drawFlow();
  },

  saveJSON() {
    const blob = new Blob([JSON.stringify(this.config(), null, 2)],
                          { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (this.config().title || 'jogo').replace(/\s+/g, '_') + '.builder.json';
    a.click();
  },

  loadJSON() {
    const inp = document.createElement('input');
    inp.type = 'file'; inp.accept = '.json,application/json';
    inp.onchange = () => {
      const f = inp.files[0];
      if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try { this.applyConfig(JSON.parse(r.result)); this.persist(); }
        catch (e) { alert('JSON inválido: ' + e.message); }
      };
      r.readAsText(f);
    };
    inp.click();
  },
};

document.addEventListener('DOMContentLoaded', () => BLD.init());
