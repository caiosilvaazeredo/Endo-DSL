/* Evaluation form */
const EV = {
  scores: {},

  set(dim, val) {
    this.scores[dim] = val;
    document.querySelectorAll(`[data-dim="${dim}"] .star`).forEach((s, i) => {
      s.classList.toggle("active", i < val);
    });
  },

  submit(pid) {
    const comments = (document.getElementById("comments") || {}).value || "";
    const evaluator = (document.getElementById("evaluator") || {}).value || "anônimo";
    fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prototype_id: pid,
        scores: this.scores,
        comments,
        evaluator,
        origin: "manual"
      })
    }).then(r => r.json()).then(d => {
      const box = document.getElementById("eval-result");
      if (d.ok) {
        if (box) box.innerHTML = `<div class="alert alert-success">Avaliação registrada! ID: ${d.evaluation_id}</div>`;
      } else {
        alert("Erro: " + d.error);
      }
    });
  }
};
