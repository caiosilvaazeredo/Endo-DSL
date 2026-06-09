/* UI global: tema claro/escuro, overlay de ajuda, atalhos. */
const ENDOUI = {
  toggleTheme() {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    try { localStorage.setItem("endo-theme", next); } catch (e) {}
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = next === "dark" ? "☀" : "◐";
  },
  help() {
    const o = document.getElementById("help-overlay");
    if (o) o.classList.toggle("show");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const t = document.documentElement.getAttribute("data-theme");
  const btn = document.getElementById("theme-toggle");
  if (btn && t === "dark") btn.textContent = "☀";
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    const o = document.getElementById("help-overlay");
    if (o && o.classList.contains("show")) o.classList.remove("show");
  }
  // "?" sem foco em campo de texto
  if (e.key === "?" && !/^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ""))) {
    e.preventDefault();
    ENDOUI.help();
  }
});
