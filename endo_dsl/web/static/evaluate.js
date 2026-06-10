/* Avaliação pedagógica (instrumento Likert 1–5) */
const EV = {
  scores: {},

  set(btn, val) {
    const group = btn.closest(".likert");
    const dim = group.dataset.dim;
    this.scores[dim] = val;
    group.querySelectorAll("button").forEach((b, i) => b.classList.toggle("on", i < val));
  },

  submit() {
    const form = document.getElementById("evalform");
    const pid = form ? parseInt(form.dataset.pid) : null;
    const origin = (form && form.dataset.origin) || "manual";
    const comments = (document.getElementById("comments") || {}).value || "";
    const evaluator = (document.getElementById("evaluator") || {}).value || "anônimo";
    const status = document.getElementById("evstatus");
    if (Object.keys(this.scores).length === 0) {
      if (status) status.textContent = "Pontue ao menos uma dimensão antes de registrar.";
      return;
    }
    fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prototype_id: pid, scores: this.scores, comments, evaluator, origin })
    }).then(r => r.json()).then(d => {
      if (status) status.textContent = d.ok
        ? `✓ Avaliação registrada (ID ${d.evaluation_id}).`
        : "Erro: " + (d.error || "desconhecido");
    });
  }
};
