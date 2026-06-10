/* ════════════════════════════════════════════════════════════════════════
   ENDO-GDC — Game Design Canvas interactive editor
   ════════════════════════════════════════════════════════════════════════ */
'use strict';

const GDC = {

  /* ── state ──────────────────────────────────────────────────────────── */
  state: {
    title: 'Meu Jogo',
    version: '1.0',
    date: new Date().toISOString().slice(0, 10),
    game_type: 'trilha',
    player_count: 2,
    duration: 30,
    bloom_levels: [],
    domain: '',
    topic: '',
    bullets: {
      situation: [''],
      player: [''],
      objectives: [''],
      narrative: [''],
      process: [''],
      mda_a: [''],
      mda_d: [''],
      mda_m: [''],
      game_objectives: [''],
      inspirations: [''],
      restrictions: [''],
    },
    selected_mechanics: [],
  },

  mechanicsCatalog: [],

  /* ── MDA hints per game type ─────────────────────────────────────────── */
  mdaHints: {
    trilha: {
      a: 'Progressão, conquista, superação de obstáculos',
      d: 'Avançar casas, enfrentar desafios nas casas especiais',
      m: 'Dados, cartas de desafio, casas especiais, peões',
    },
    quiz_battle: {
      a: 'Competição, conhecimento, rivalidade saudável',
      d: 'Responder perguntas para avançar ou marcar pontos',
      m: 'Banco de questões, pontuação, timer, placar',
    },
    memoria: {
      a: 'Descoberta, correspondência, concentração',
      d: 'Virar pares de cartas, memorizar posições',
      m: 'Baralho com pares, turnos alternados, pontuação por pares',
    },
    xadrez: {
      a: 'Estratégia, antecipação, controle do tabuleiro',
      d: 'Mover peças para controlar o tabuleiro e capturar o rei adversário',
      m: 'Peças com movimentos únicos, tabuleiro 8×8, xeque/xeque-mate',
    },
    cartas: {
      a: 'Sorte, estratégia, blefe',
      d: 'Jogar cartas da mão, construir combos ou coletar sets',
      m: 'Baralho, mão de cartas, pilhas de descarte, poderes especiais',
    },
    livre: {
      a: 'Definir estética personalizada para o jogo',
      d: 'Definir dinâmicas personalizadas',
      m: 'Definir mecânicas personalizadas',
    },
  },

  /* ── init ────────────────────────────────────────────────────────────── */
  init() {
    this._loadFromStorage();
    this._renderAll();
    this._wireGlobalInputs();
    this.loadMechanics();

    // auto-save on any change
    document.getElementById('gdc-canvas-root').addEventListener('input', () => {
      this._saveToStorage();
    });
  },

  /* ── persistence ─────────────────────────────────────────────────────── */
  _saveToStorage() {
    try {
      const s = this.toDict();
      localStorage.setItem('endo-gdc-state', JSON.stringify(s));
    } catch (e) { /* ignore */ }
  },

  _loadFromStorage() {
    try {
      const raw = localStorage.getItem('endo-gdc-state');
      if (!raw) return;
      const s = JSON.parse(raw);
      if (s.title)      this.state.title      = s.title;
      if (s.version)    this.state.version    = s.version;
      if (s.date)       this.state.date       = s.date;
      if (s.game_type)  this.state.game_type  = s.game_type;
      if (s.player_count) this.state.player_count = s.player_count;
      if (s.duration)   this.state.duration   = s.duration;
      if (Array.isArray(s.bloom_levels)) this.state.bloom_levels = s.bloom_levels;
      if (s.domain)     this.state.domain     = s.domain;
      if (s.topic)      this.state.topic      = s.topic;
      if (s.bullets && typeof s.bullets === 'object') {
        Object.assign(this.state.bullets, s.bullets);
      }
      if (Array.isArray(s.selected_mechanics)) {
        this.state.selected_mechanics = s.selected_mechanics;
      }
    } catch (e) { /* ignore bad storage */ }
  },

  /* ── render all sections ─────────────────────────────────────────────── */
  _renderAll() {
    document.getElementById('gdc-title-input').value       = this.state.title;
    document.getElementById('gdc-version-input').value     = this.state.version;
    document.getElementById('gdc-date-input').value        = this.state.date;
    document.getElementById('gdc-domain-input').value      = this.state.domain;
    document.getElementById('gdc-topic-input').value       = this.state.topic;
    document.getElementById('gdc-player-slider').value     = this.state.player_count;
    document.getElementById('gdc-player-label').textContent = this.state.player_count;
    this._renderGameType();
    this._renderBloomChips();
    this._renderDurationBtns();
    this._renderAllBullets();
    this._renderSelectedMechanics();
  },

  _renderGameType() {
    document.querySelectorAll('.game-type-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.type === this.state.game_type);
    });
    const hint = this.mdaHints[this.state.game_type] || this.mdaHints.livre;
    const setHint = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = 'Dica: ' + text;
    };
    setHint('mda-hint-a', hint.a);
    setHint('mda-hint-d', hint.d);
    setHint('mda-hint-m', hint.m);
  },

  _renderBloomChips() {
    document.querySelectorAll('.bloom-chip').forEach(chip => {
      chip.classList.toggle('active', this.state.bloom_levels.includes(chip.dataset.level));
    });
  },

  _renderDurationBtns() {
    document.querySelectorAll('.duration-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.dur) === this.state.duration);
    });
  },

  _renderAllBullets() {
    Object.keys(this.state.bullets).forEach(section => this._renderBullets(section));
  },

  _renderBullets(section) {
    const container = document.getElementById(`bullets-${section}`);
    if (!container) return;
    const bullets = this.state.bullets[section];
    container.innerHTML = '';
    bullets.forEach((text, idx) => {
      const li = document.createElement('li');
      li.className = 'gdc-bullet-item';
      li.innerHTML = `<textarea class="gdc-bullet-text" rows="1"
          data-section="${section}" data-idx="${idx}"
          placeholder="Escreva aqui…">${this._esc(text)}</textarea>
        <button class="gdc-bullet-remove" title="Remover" onclick="GDC.removeBullet('${section}',${idx})">✕</button>`;
      container.appendChild(li);
    });
    // auto-resize textareas
    container.querySelectorAll('.gdc-bullet-text').forEach(ta => {
      ta.addEventListener('input', e => {
        const s = e.target.dataset.section;
        const i = parseInt(e.target.dataset.idx);
        GDC.state.bullets[s][i] = e.target.value;
        GDC._autoResize(e.target);
        GDC._saveToStorage();
        if (s === 'objectives') GDC.autoSuggestBloom();
      });
      this._autoResize(ta);
    });
  },

  _autoResize(ta) {
    ta.style.height = 'auto';
    ta.style.height = ta.scrollHeight + 'px';
  },

  _renderSelectedMechanics() {
    const container = document.getElementById('selected-mechanics');
    if (!container) return;
    container.innerHTML = this.state.selected_mechanics.map((m, i) =>
      `<span class="mechanic-tag">${this._esc(m)}
        <button onclick="GDC.removeMechanic(${i})" title="Remover">✕</button>
       </span>`
    ).join('');
  },

  /* ── wire global inputs ──────────────────────────────────────────────── */
  _wireGlobalInputs() {
    const bind = (id, key) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('input', () => {
        this.state[key] = el.value;
        this._saveToStorage();
      });
    };
    bind('gdc-title-input',   'title');
    bind('gdc-version-input', 'version');
    bind('gdc-date-input',    'date');
    bind('gdc-domain-input',  'domain');
    bind('gdc-topic-input',   'topic');

    const slider = document.getElementById('gdc-player-slider');
    if (slider) {
      slider.addEventListener('input', () => {
        this.state.player_count = parseInt(slider.value);
        document.getElementById('gdc-player-label').textContent = slider.value;
        this._saveToStorage();
      });
    }
  },

  /* ── public API ──────────────────────────────────────────────────────── */
  setGameType(type) {
    this.state.game_type = type;
    this._renderGameType();
    this._saveToStorage();
  },

  toggleBloom(level) {
    const idx = this.state.bloom_levels.indexOf(level);
    if (idx >= 0) this.state.bloom_levels.splice(idx, 1);
    else          this.state.bloom_levels.push(level);
    this._renderBloomChips();
    this._saveToStorage();
  },

  setDuration(dur) {
    this.state.duration = dur;
    this._renderDurationBtns();
    this._saveToStorage();
  },

  addBullet(section) {
    this.state.bullets[section].push('');
    this._renderBullets(section);
    // focus new textarea
    const container = document.getElementById(`bullets-${section}`);
    if (container) {
      const tas = container.querySelectorAll('.gdc-bullet-text');
      if (tas.length) tas[tas.length - 1].focus();
    }
  },

  removeBullet(section, idx) {
    if (this.state.bullets[section].length <= 1) return; // keep at least 1
    this.state.bullets[section].splice(idx, 1);
    this._renderBullets(section);
    this._saveToStorage();
  },

  removeMechanic(idx) {
    this.state.selected_mechanics.splice(idx, 1);
    this._renderSelectedMechanics();
    this._saveToStorage();
  },

  /* ── toDict ──────────────────────────────────────────────────────────── */
  toDict() {
    return {
      title:              this.state.title,
      version:            this.state.version,
      date:               this.state.date,
      game_type:          this.state.game_type,
      player_count:       this.state.player_count,
      duration:           this.state.duration,
      bloom_levels:       [...this.state.bloom_levels],
      domain:             this.state.domain,
      topic:              this.state.topic,
      situation:          [...this.state.bullets.situation],
      players_desc:       [...this.state.bullets.player],
      learning_objectives:[...this.state.bullets.objectives],
      narrative:          [...this.state.bullets.narrative],
      learning_process:   [...this.state.bullets.process],
      mda_aesthetics:     [...this.state.bullets.mda_a],
      mda_dynamics:       [...this.state.bullets.mda_d],
      mda_mechanics:      [...this.state.bullets.mda_m],
      game_objectives:    [...this.state.bullets.game_objectives],
      inspirations:       [...this.state.bullets.inspirations],
      restrictions:       [...this.state.bullets.restrictions],
      selected_mechanics: [...this.state.selected_mechanics],
      bullets:            JSON.parse(JSON.stringify(this.state.bullets)),
    };
  },

  /* ── generate prototype ──────────────────────────────────────────────── */
  async generatePrototype() {
    const btn = document.getElementById('btn-generate-proto');
    btn.classList.add('btn-loading');
    try {
      const resp = await fetch('/api/boardgame/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          gdc: this.toDict(),
          players: this.state.player_count,
          domain:  this.state.domain,
          topic:   this.state.topic,
          title:   this.state.title,
          game_type: this.state.game_type,
        }),
      });
      const data = await resp.json();
      if (data.ok && data.html_url) {
        window.open(data.html_url, '_blank');
      } else {
        alert('Erro ao gerar protótipo: ' + (data.error || JSON.stringify(data)));
      }
    } catch (e) {
      alert('Falha na requisição: ' + e.message);
    } finally {
      btn.classList.remove('btn-loading');
    }
  },

  /* ── generate DSL ────────────────────────────────────────────────────── */
  async generateDSL() {
    const btn = document.getElementById('btn-gen-dsl');
    btn.classList.add('btn-loading');
    try {
      const resp = await fetch('/api/boardgame/gdc-to-dsl', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ gdc: this.toDict() }),
      });
      const data = await resp.json();
      const pre = document.getElementById('dsl-modal-content');
      pre.textContent = data.dsl || '(sem conteúdo)';
      document.getElementById('dsl-modal').classList.remove('hidden');
    } catch (e) {
      alert('Falha: ' + e.message);
    } finally {
      btn.classList.remove('btn-loading');
    }
  },

  closeDSLModal() {
    document.getElementById('dsl-modal').classList.add('hidden');
  },

  copyDSL() {
    const text = document.getElementById('dsl-modal-content').textContent;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById('btn-copy-dsl');
      btn.textContent = '✓ Copiado!';
      setTimeout(() => { btn.textContent = 'Copiar'; }, 2000);
    });
  },

  /* ── save / load JSON ────────────────────────────────────────────────── */
  saveJSON() {
    const dict = this.toDict();
    const blob = new Blob([JSON.stringify(dict, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (this.state.title || 'gdc').replace(/\s+/g, '_') + '.gdc.json';
    a.click();
    URL.revokeObjectURL(url);
  },

  loadJSON(input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const data = JSON.parse(e.target.result);
        // apply to state
        if (data.title)    this.state.title    = data.title;
        if (data.version)  this.state.version  = data.version;
        if (data.date)     this.state.date     = data.date;
        if (data.game_type) this.state.game_type = data.game_type;
        if (data.player_count) this.state.player_count = data.player_count;
        if (data.duration) this.state.duration = data.duration;
        if (Array.isArray(data.bloom_levels)) this.state.bloom_levels = data.bloom_levels;
        if (data.domain)   this.state.domain   = data.domain;
        if (data.topic)    this.state.topic    = data.topic;
        if (data.bullets)  Object.assign(this.state.bullets, data.bullets);
        if (Array.isArray(data.selected_mechanics)) {
          this.state.selected_mechanics = data.selected_mechanics;
        }
        this._renderAll();
        this._saveToStorage();
      } catch (err) {
        alert('Erro ao carregar JSON: ' + err.message);
      }
    };
    reader.readAsText(file);
  },

  /* ── export HTML ─────────────────────────────────────────────────────── */
  exportHTML() {
    const s = this.toDict();
    const bl = (list) => list.filter(b => b.trim())
      .map(b => `<p>• ${this._esc(b)}</p>`).join('\n');

    const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ENDO-GDC: ${this._esc(s.title)}</title>
<style>
body { font-family: 'Comic Sans MS', 'Chalkboard SE', cursive; margin:0; padding:20px; background:white; }
.container { max-width:1200px; margin:0 auto; display:grid; grid-template-columns:repeat(4,1fr); grid-template-rows:auto auto auto auto auto; gap:10px; }
.header-cell { border:1px solid #000; padding:10px; background:white; }
.situation,.player { background:#FBD7B4; border:2px solid #E67E22; border-radius:5px; padding:15px; }
.situation { grid-column:1/span 2; grid-row:2; }
.player    { grid-column:3/span 2; grid-row:2; }
.learning-objectives { grid-column:1/span 2; grid-row:3; background:#D5F5E3; border:2px solid #27AE60; border-radius:5px; padding:15px; }
.narrative { grid-column:3/span 2; grid-row:3; background:#D6EAF8; border:2px solid #3498DB; border-radius:5px; padding:15px; }
.learning-process { grid-column:1; grid-row:4; background:#D5F5E3; border:2px solid #27AE60; border-radius:5px; padding:15px; }
.game { grid-column:2/span 2; grid-row:4; background:#FCF3CF; border:2px solid #F1C40F; border-radius:5px; padding:15px; }
.game-objectives { grid-column:4; grid-row:4; background:#D6EAF8; border:2px solid #3498DB; border-radius:5px; padding:15px; }
.inspirations { grid-column:1/span 2; grid-row:5; background:#FCF3CF; border:2px solid #F1C40F; border-radius:5px; padding:15px; }
.restrictions { grid-column:3/span 2; grid-row:5; background:#FADBD8; border:2px solid #E74C3C; border-radius:5px; padding:15px; }
.footer { grid-column:1/span 4; grid-row:6; font-size:.8em; padding:10px 0; }
.section-title { font-weight:bold; margin-bottom:10px; }
.section-content p { margin:5px 0; }
.amd-section { margin-top:10px; padding-top:5px; border-top:1px dashed #bbb; }
.amd-title { font-weight:bold; color:#666; }
</style>
</head>
<body>
<div class="container">
  <div class="header-cell" style="grid-column:1/span 2"><strong>Jogo:</strong> ${this._esc(s.title)}</div>
  <div class="header-cell"><strong>Versão:</strong> ${this._esc(s.version)}</div>
  <div class="header-cell"><strong>Data:</strong> ${this._esc(s.date)}</div>
  <div class="situation">
    <div class="section-title">🏠 Situação</div>
    <div class="section-content">${bl(s.situation)}</div>
  </div>
  <div class="player">
    <div class="section-title">😊 Jogador/Aluno</div>
    <div class="section-content">${bl(s.players_desc)}</div>
  </div>
  <div class="learning-objectives">
    <div class="section-title">📚 Objetivos de Aprendizado</div>
    <div class="section-content">${bl(s.learning_objectives)}</div>
  </div>
  <div class="narrative">
    <div class="section-title">📖 Narrativa</div>
    <div class="section-content">${bl(s.narrative)}</div>
  </div>
  <div class="learning-process">
    <div class="section-title">📝 Processo Lúdico de Aprendizado</div>
    <div class="section-content">${bl(s.learning_process)}</div>
  </div>
  <div class="game">
    <div class="section-title">🎮 Jogo (MDA, Interface, exemplos)</div>
    <div class="section-content">
      <div class="amd-section"><div class="amd-title">A</div>${bl(s.mda_aesthetics)}</div>
      <div class="amd-section"><div class="amd-title">D</div>${bl(s.mda_dynamics)}</div>
      <div class="amd-section"><div class="amd-title">M</div>${bl(s.mda_mechanics)}</div>
    </div>
  </div>
  <div class="game-objectives">
    <div class="section-title">🎯 Objetivos do Jogo</div>
    <div class="section-content">${bl(s.game_objectives)}</div>
  </div>
  <div class="inspirations">
    <div class="section-title">💡 Inspirações</div>
    <div class="section-content">${bl(s.inspirations)}</div>
  </div>
  <div class="restrictions">
    <div class="section-title">⚠️ Restrições</div>
    <div class="section-content">${bl(s.restrictions)}</div>
  </div>
  <div class="footer">ENDO-GDC &middot; PESC/COPPE/UFRJ &middot; ${this._esc(s.date)}</div>
</div>
</body></html>`;

    const blob = new Blob([html], {type: 'text/html'});
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = (s.title || 'gdc').replace(/\s+/g, '_') + '_GDC.html';
    a.click();
    URL.revokeObjectURL(url);
  },

  /* ── auto-suggest Bloom ──────────────────────────────────────────────── */
  autoSuggestBloom() {
    const text = this.state.bullets.objectives.join(' ').toLowerCase();
    const keywords = {
      criar:       ['criar', 'compor', 'projetar', 'elaborar', 'inventar', 'produzir'],
      avaliar:     ['avaliar', 'julgar', 'defender', 'argumentar', 'criticar'],
      analisar:    ['analisar', 'comparar', 'diferenciar', 'examinar', 'investigar'],
      aplicar:     ['aplicar', 'usar', 'executar', 'resolver', 'calcular', 'praticar'],
      compreender: ['explicar', 'descrever', 'resumir', 'interpretar', 'classificar', 'entender'],
      lembrar:     ['lembrar', 'listar', 'identificar', 'nomear', 'reconhecer', 'recordar'],
    };
    let bestLevel = null;
    const order = ['criar','avaliar','analisar','aplicar','compreender','lembrar'];
    for (const level of order) {
      if (keywords[level].some(kw => text.includes(kw))) {
        bestLevel = level;
        break;
      }
    }
    const el = document.getElementById('bloom-suggest-text');
    if (el) {
      if (bestLevel) {
        el.textContent = `Nível de Bloom sugerido: ${bestLevel.charAt(0).toUpperCase() + bestLevel.slice(1)}`;
      } else {
        el.textContent = '';
      }
    }
  },

  /* ── mechanics loader ────────────────────────────────────────────────── */
  async loadMechanics() {
    try {
      const resp = await fetch('/api/boardgame/mechanics');
      const data = await resp.json();
      if (Array.isArray(data)) this.mechanicsCatalog = data;
      else if (data.mechanics) this.mechanicsCatalog = data.mechanics;
    } catch (e) {
      // fallback sample
      this.mechanicsCatalog = [
        {id:'dice_roll',name:'Rolagem de Dados'},
        {id:'card_draw',name:'Compra de Cartas'},
        {id:'worker_placement',name:'Colocação de Trabalhadores'},
        {id:'area_control',name:'Controle de Área'},
        {id:'deck_building',name:'Construção de Baralho'},
        {id:'cooperative',name:'Jogo Cooperativo'},
        {id:'push_your_luck',name:'Empurrar a Sorte'},
        {id:'trivia',name:'Trivia/Quiz'},
        {id:'memory',name:'Memória'},
        {id:'movement_track',name:'Trilha de Movimento'},
      ];
    }
    this._populateMechanicsDropdown('');
  },

  _populateMechanicsDropdown(filter) {
    const dropdown = document.getElementById('mechanics-dropdown');
    if (!dropdown) return;
    const lower = filter.toLowerCase();
    const items = this.mechanicsCatalog.filter(m =>
      !filter || m.name.toLowerCase().includes(lower) || m.id.toLowerCase().includes(lower)
    );
    dropdown.innerHTML = items.map(m =>
      `<div class="mechanic-option${this.state.selected_mechanics.includes(m.name) ? ' selected' : ''}"
           onclick="GDC.selectMechanic('${this._esc(m.name)}')">${this._esc(m.name)}</div>`
    ).join('') || '<div class="mechanic-option" style="color:#999">Nenhuma encontrada</div>';
  },

  selectMechanic(name) {
    if (!this.state.selected_mechanics.includes(name)) {
      this.state.selected_mechanics.push(name);
      this._renderSelectedMechanics();
      this._saveToStorage();
    }
    // also add to mda_m bullets
    const last = this.state.bullets.mda_m;
    if (!last.includes(name)) {
      if (last.length === 1 && last[0] === '') last[0] = name;
      else last.push(name);
      this._renderBullets('mda_m');
    }
    this._populateMechanicsDropdown(document.getElementById('mechanics-search').value);
  },

  toggleMechanicsDropdown() {
    const dd = document.getElementById('mechanics-dropdown');
    if (dd) dd.classList.toggle('open');
  },

  filterMechanics(value) {
    const dd = document.getElementById('mechanics-dropdown');
    if (dd) { dd.classList.add('open'); this._populateMechanicsDropdown(value); }
  },

  /* ── utility ─────────────────────────────────────────────────────────── */
  _esc(str) {
    return String(str || '')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;');
  },
};

document.addEventListener('DOMContentLoaded', () => GDC.init());

// close mechanics dropdown when clicking outside
document.addEventListener('click', e => {
  const dd = document.getElementById('mechanics-dropdown');
  if (!dd) return;
  if (!e.target.closest('.mechanics-selector')) dd.classList.remove('open');
});
