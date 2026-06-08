/* Studio — Endo-DSL phases 1-6 */
const ENDO = {
  _state: { session_id: null, phase: 1, retrieved: [], dsl: "", prototype_id: null },
  _debounce: null,

  go(phase) {
    document.querySelectorAll(".phase-panel").forEach(p => p.style.display = "none");
    const panel = document.getElementById("phase-" + phase);
    if (panel) panel.style.display = "block";
    document.querySelectorAll(".phase-step").forEach(s => {
      const n = parseInt(s.dataset.phase);
      s.classList.toggle("active", n === phase);
      s.classList.toggle("done", n < phase);
    });
    this._state.phase = phase;
  },

  async createSession() {
    const form = document.getElementById("ctx-form");
    if (!form) return null;
    const data = {};
    new FormData(form).forEach((v, k) => { data[k] = v; });
    const res = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    this._state.session_id = json.session_id;
    this._state.ctx = data;
    return json.session_id;
  },

  async retrieve() {
    if (!this._state.session_id) await this.createSession();
    const ctx = this._state.ctx || {};
    const body = { ...ctx, top_k: 6 };
    const res = await fetch("/api/retrieve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const json = await res.json();
    this._state.retrieved = json.components || [];
    this._renderRetrieved();
    this.go(2);
  },

  _renderRetrieved() {
    const list = document.getElementById("retrieved-list");
    if (!list) return;
    if (!this._state.retrieved.length) {
      list.innerHTML = "<p>Nenhum componente recuperado.</p>";
      return;
    }
    list.innerHTML = this._state.retrieved.map(rc => `
      <div class="component-card">
        <label>
          <input type="checkbox" name="selected_keys" value="${rc.key}" checked>
          <strong>${rc.key}</strong>
          <span class="bloom-badge bloom-${(rc.bloom_level||"").toLowerCase()}">${rc.bloom_level||""}</span>
          <span class="badge badge-secondary">${rc.mechanic_type||""}</span>
          <span class="score">${(rc.score||0).toFixed(2)}</span>
        </label>
        <p>${rc.description||""}</p>
      </div>`).join("");
  },

  skipToGenerate() {
    this._state.retrieved = [];
    this.go(3);
    this.generate();
  },

  async generate() {
    if (!this._state.session_id) await this.createSession();
    const checkboxes = document.querySelectorAll("input[name=selected_keys]:checked");
    const selected_keys = checkboxes.length
      ? Array.from(checkboxes).map(c => c.value)
      : null;
    const btn = document.getElementById("btn-generate");
    if (btn) { btn.disabled = true; btn.textContent = "Gerando…"; }
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this._state.session_id, selected_keys })
      });
      const json = await res.json();
      this._state.dsl = json.dsl || "";
      this._state.session_id = json.session_id || this._state.session_id;
      const editor = document.getElementById("dsl-editor");
      if (editor) editor.value = this._state.dsl;
      this._renderMetrics(json.metrics);
      this.go(4);
      this.onEdit();
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = "Gerar DSL"; }
    }
  },

  _renderMetrics(metrics) {
    const box = document.getElementById("metrics-box");
    if (!box || !metrics) return;
    box.innerHTML = `
      <div class="metric-box"><span>${metrics.attempts||0}</span><label>tentativas</label></div>
      <div class="metric-box"><span>${metrics.success ? "✓" : "✗"}</span><label>sucesso</label></div>
      <div class="metric-box"><span>${(metrics.elapsed_ms||0).toFixed(0)}ms</span><label>tempo</label></div>`;
  },

  onEdit() {
    clearTimeout(this._debounce);
    this._debounce = setTimeout(() => this._validate(), 400);
  },

  async _validate() {
    const editor = document.getElementById("dsl-editor");
    if (!editor) return;
    const dsl = editor.value;
    this._state.dsl = dsl;
    const res = await fetch("/api/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dsl })
    });
    const json = await res.json();
    this._renderValidation(json);
  },

  _renderValidation(v) {
    const panel = document.getElementById("validation-panel");
    if (!panel) return;
    const errors = v.errors || [];
    const warnings = v.warnings || [];
    let html = "";
    if (v.syntactic_ok && v.semantic_ok && !warnings.length) {
      html = '<div class="alert alert-success">✓ DSL válida</div>';
    } else {
      errors.forEach(e => { html += `<div class="alert alert-danger">✗ ${e}</div>`; });
      warnings.forEach(w => { html += `<div class="alert alert-warning">⚠ ${w}</div>`; });
    }
    panel.innerHTML = html;
  },

  async compile() {
    const editor = document.getElementById("dsl-editor");
    const dsl = editor ? editor.value : this._state.dsl;
    const btn = document.getElementById("btn-compile");
    if (btn) { btn.disabled = true; btn.textContent = "Compilando…"; }
    try {
      const res = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dsl, session_id: this._state.session_id, origin: "manual" })
      });
      const json = await res.json();
      if (!json.ok) {
        const result = document.getElementById("compile-result");
        if (result) result.innerHTML = (json.errors||[]).map(e =>
          `<div class="alert alert-danger">${e}</div>`).join("");
        return;
      }
      this._state.prototype_id = json.prototype_id;
      const result = document.getElementById("compile-result");
      if (result) result.innerHTML = `
        <div class="alert alert-success">Protótipo #${json.prototype_id} compilado!</div>
        <a href="/prototype/${json.prototype_id}" target="_blank" class="btn btn-primary">Abrir protótipo</a>
        <a href="/prototype/${json.prototype_id}/traceability" target="_blank" class="btn btn-sm">Rastreabilidade</a>
        <a href="/evaluate/${json.prototype_id}" class="btn btn-sm btn-success">Avaliar</a>`;
      this.go(5);
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = "Compilar"; }
    }
  },

  async reparametrize(pid, domain, topic) {
    const res = await fetch("/api/reparametrize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prototype_id: pid, domain, topic })
    });
    const json = await res.json();
    if (json.prototype_id) {
      window.open("/prototype/" + json.prototype_id, "_blank");
    }
  },

  evaluate(pid) {
    window.location.href = "/evaluate/" + pid;
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const editor = document.getElementById("dsl-editor");
  if (editor) editor.addEventListener("input", () => ENDO.onEdit());
  ENDO.go(1);
});
