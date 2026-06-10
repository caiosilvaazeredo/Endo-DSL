/* Curator page */
const CUR = {
  act(cid, action, note) {
    if (!note) note = prompt(`Justificativa para "${action}":`);
    if (note === null) return;
    fetch("/api/curate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ component_id: cid, action, note, curator: "curador" })
    }).then(r => r.json()).then(d => {
      if (d.ok) location.reload();
      else alert("Erro: " + d.error);
    });
  }
};
