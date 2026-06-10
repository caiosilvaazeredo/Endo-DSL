"""Engine HTML5 para protótipos de board game gerados pela Endo-DSL.

Suporta 4 tipos de jogo:
  - track       : trilha serpentina numerada (estilo jogo da cobrinha educacional)
  - grid        : grade estratégica (xadrez/damas/jogo da velha)
  - cards_only  : jogo de cartas puro
  - quiz_battle : duelo de quiz (estilo Perguntados)

O HTML gerado é completamente autocontido (sem dependências externas).
"""

from __future__ import annotations

import json
from typing import Any, Dict

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_BOARD_CSS = """
:root {
  --bg: #0f172a; --panel: #1e293b; --panel2: #334155; --ink: #f1f5f9;
  --muted: #94a3b8; --accent: #6366f1; --good: #22c55e; --bad: #ef4444;
  --warn: #eab308; --border: #334155;
  --bloom-1: #3b82f6; --bloom-2: #14b8a6; --bloom-3: #22c55e;
  --bloom-4: #eab308; --bloom-5: #f97316; --bloom-6: #ef4444;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: var(--bg); color: var(--ink);
  min-height: 100vh; min-width: 800px;
}
#game-wrap { max-width: 1100px; margin: 0 auto; padding: 16px; }
#game-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; background: var(--panel); border-radius: 14px;
  margin-bottom: 14px; border: 1px solid var(--border); flex-wrap: wrap; gap: 8px;
}
#game-header h1 { font-size: 1.3rem; letter-spacing: .2px; }
#header-controls { display: flex; gap: 10px; align-items: center; }
.btn {
  background: var(--accent); color: #fff; border: none; border-radius: 10px;
  padding: 9px 18px; font: inherit; font-weight: 600; cursor: pointer;
  transition: filter .12s, transform .1s;
}
.btn:hover { filter: brightness(1.12); transform: translateY(-1px); }
.btn.ghost { background: transparent; border: 1px solid var(--border); color: var(--ink); }
.btn.sm { padding: 6px 13px; font-size: .88rem; }
.btn.danger { background: var(--bad); }

/* SCOREBOARD */
#scoreboard {
  display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px;
}
.player-card {
  flex: 1; min-width: 140px; background: var(--panel);
  border: 2px solid var(--border); border-radius: 12px;
  padding: 10px 14px; transition: border-color .2s;
}
.player-card.active { border-color: var(--accent); }
.player-card .player-name { font-weight: 700; font-size: .95rem; display: flex; align-items: center; gap: 6px; }
.player-card .player-score { font-size: 1.6rem; font-weight: 800; margin-top: 2px; }
.player-card .player-pos { font-size: .78rem; color: var(--muted); margin-top: 2px; }

/* MAIN GAME AREA */
#game-area { display: flex; gap: 14px; flex-wrap: wrap; }
#board-container {
  flex: 2; min-width: 500px; background: var(--panel);
  border: 1px solid var(--border); border-radius: 16px; padding: 16px;
  position: relative;
}
#side-panel {
  flex: 1; min-width: 220px; display: flex; flex-direction: column; gap: 12px;
}

/* TRACK BOARD */
#track-grid {
  display: grid; gap: 4px; margin: 0 auto;
}
.track-cell {
  aspect-ratio: 1; border-radius: 8px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; font-size: .75rem; font-weight: 600;
  border: 2px solid rgba(255,255,255,.08); cursor: default; position: relative;
  transition: transform .15s;
  min-width: 0;
}
.track-cell.normal { background: var(--panel2); }
.track-cell.quiz { background: #1e3a5f; border-color: var(--bloom-1); }
.track-cell.bonus { background: #14451a; border-color: var(--good); }
.track-cell.penalty { background: #450e0e; border-color: var(--bad); }
.track-cell.special { background: #3d2a00; border-color: var(--warn); }
.track-cell.start { background: #1a3a1a; border-color: var(--good); }
.track-cell.end { background: #3a1a3a; border-color: #a855f7; }
.track-cell .cell-num { font-size: .65rem; color: var(--muted); position: absolute; top: 2px; left: 4px; }
.track-cell .cell-icon { font-size: 1.1rem; }
.track-cell .tokens { display: flex; flex-wrap: wrap; justify-content: center; gap: 1px; position: absolute; bottom: 2px; }
.token { font-size: .95rem; line-height: 1; }

/* DICE */
#dice-area {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; padding: 14px; text-align: center;
}
#dice-face {
  font-size: 3.5rem; display: block; margin: 6px auto;
  transition: transform .1s;
  user-select: none;
}
#dice-face.rolling { animation: rollDice .4s ease; }
@keyframes rollDice {
  0%  { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(90deg) scale(.8); }
  50% { transform: rotate(180deg) scale(1.2); }
  75% { transform: rotate(270deg) scale(.9); }
  100%{ transform: rotate(360deg) scale(1); }
}
#dice-result { font-size: 1.1rem; font-weight: 700; margin: 4px 0; }

/* QUIZ MODAL */
#quiz-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.75);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 20px;
}
#quiz-overlay.hidden { display: none; }
#quiz-modal {
  background: var(--panel); border: 2px solid var(--accent);
  border-radius: 18px; padding: 24px; max-width: 560px; width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,.5);
}
#quiz-modal h2 { font-size: 1.1rem; color: var(--muted); margin-bottom: 8px; }
#quiz-question { font-size: 1.15rem; line-height: 1.5; margin-bottom: 18px; font-weight: 600; }
.quiz-options { display: grid; gap: 10px; }
.quiz-opt {
  background: var(--panel2); border: 2px solid var(--border);
  border-radius: 11px; padding: 12px 16px; cursor: pointer;
  font: inherit; color: var(--ink); text-align: left;
  transition: background .12s, border-color .12s, transform .1s;
}
.quiz-opt:hover:not(:disabled) { background: #3a4a6a; transform: translateY(-1px); }
.quiz-opt.correct { background: rgba(34,197,94,.2); border-color: var(--good); }
.quiz-opt.wrong { background: rgba(239,68,68,.18); border-color: var(--bad); }
.quiz-opt:disabled { cursor: default; }
#quiz-feedback {
  margin-top: 14px; padding: 10px 14px; border-radius: 10px;
  font-weight: 600; display: none;
}
#quiz-feedback.show { display: block; }
#quiz-feedback.ok { background: rgba(34,197,94,.15); border: 1px solid var(--good); color: var(--good); }
#quiz-feedback.no { background: rgba(239,68,68,.13); border: 1px solid var(--bad); color: var(--bad); }
#quiz-continue {
  margin-top: 14px; width: 100%; padding: 11px;
  background: var(--accent); color: #fff; border: none; border-radius: 10px;
  font: inherit; font-weight: 700; cursor: pointer; display: none;
}
#quiz-continue.show { display: block; }

/* BLOOM BADGE */
.bloom-badge {
  display: inline-block; padding: 2px 9px; border-radius: 999px;
  font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .3px;
}
.b1 { background: var(--bloom-1); }
.b2 { background: var(--bloom-2); }
.b3 { background: var(--bloom-3); color: #0a1a0a; }
.b4 { background: var(--bloom-4); color: #1a1200; }
.b5 { background: var(--bloom-5); }
.b6 { background: var(--bloom-6); }

/* GRID GAME */
#grid-board {
  display: grid; margin: 0 auto; gap: 3px;
}
.grid-cell {
  aspect-ratio: 1; border-radius: 6px; display: flex; align-items: center;
  justify-content: center; font-size: 1.6rem; cursor: pointer;
  border: 2px solid rgba(255,255,255,.08);
  transition: background .15s, border-color .15s, transform .1s;
  min-width: 0;
}
.grid-cell.light { background: #2d3a52; }
.grid-cell.dark  { background: #1e2a3e; }
.grid-cell.selected { border-color: var(--accent); background: rgba(99,102,241,.3); }
.grid-cell.valid-move { border-color: var(--good); background: rgba(34,197,94,.15); cursor: pointer; }
.grid-cell.valid-move:hover { background: rgba(34,197,94,.28); }
.grid-cell:hover:not(.valid-move) { transform: scale(1.04); }
.grid-cell.ttt-x { background: rgba(99,102,241,.2); border-color: var(--bloom-1); }
.grid-cell.ttt-o { background: rgba(239,68,68,.2); border-color: var(--bad); }

/* CARDS GAME */
#cards-area { display: flex; flex-direction: column; gap: 12px; }
#piles-row { display: flex; gap: 14px; justify-content: center; align-items: center; }
.card-pile {
  width: 90px; height: 130px; border-radius: 12px; border: 2px dashed var(--border);
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; gap: 4px; cursor: pointer; font-size: .8rem;
  color: var(--muted); transition: border-color .15s; position: relative;
}
.card-pile:hover { border-color: var(--accent); }
.card-pile .pile-count { font-size: 1.4rem; font-weight: 800; color: var(--ink); }
.card-back {
  width: 90px; height: 130px; border-radius: 12px;
  background: linear-gradient(135deg, #1e3a5f, #3a1e5f);
  border: 2px solid var(--accent); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,.3);
  transition: transform .12s;
}
.card-back:hover { transform: translateY(-3px); }
#hand-area { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.game-card {
  width: 100px; height: 140px; border-radius: 12px; background: var(--panel);
  border: 2px solid var(--border); display: flex; flex-direction: column;
  align-items: center; justify-content: space-between; padding: 8px 6px;
  cursor: pointer; transition: transform .15s, border-color .15s, box-shadow .15s;
  font-size: .78rem; text-align: center; position: relative;
}
.game-card:hover { transform: translateY(-6px); border-color: var(--accent); box-shadow: 0 8px 24px rgba(0,0,0,.4); }
.game-card.selected { border-color: var(--warn); box-shadow: 0 0 0 3px rgba(234,179,8,.3); }
.game-card .card-icon { font-size: 1.8rem; }
.game-card .card-text { font-size: .7rem; line-height: 1.3; color: var(--muted); }
.game-card .card-type-badge { font-size: .62rem; font-weight: 700; padding: 2px 6px; border-radius: 6px; }
.card-type-quiz { background: rgba(99,102,241,.3); color: #a5b4fc; }
.card-type-action { background: rgba(34,197,94,.2); color: #86efac; }
.card-type-bonus { background: rgba(234,179,8,.2); color: #fde68a; }
.card-type-penalty { background: rgba(239,68,68,.2); color: #fca5a5; }
#discard-top { min-height: 130px; }

/* QUIZ BATTLE */
#qb-area { display: flex; flex-direction: column; gap: 14px; }
#qb-question-box {
  background: var(--panel); border: 2px solid var(--accent); border-radius: 16px;
  padding: 22px; text-align: center;
}
#qb-question { font-size: 1.2rem; font-weight: 700; margin-bottom: 6px; }
#qb-timer { font-size: 2rem; font-weight: 800; color: var(--warn); }
#qb-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
.qb-opt {
  background: var(--panel2); border: 2px solid var(--border);
  border-radius: 11px; padding: 13px 16px; cursor: pointer;
  font: inherit; color: var(--ink); font-size: .95rem; font-weight: 600;
  transition: all .12s;
}
.qb-opt:hover:not(:disabled) { background: #3a4a6a; border-color: var(--accent); transform: scale(1.02); }
.qb-opt.correct { background: rgba(34,197,94,.25); border-color: var(--good); }
.qb-opt.wrong   { background: rgba(239,68,68,.2); border-color: var(--bad); }
.qb-opt:disabled { cursor: default; }
#qb-bloom-bars { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 14px; }
#qb-bloom-bars h3 { font-size: .88rem; color: var(--muted); margin-bottom: 10px; }
.bloom-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.bloom-row .bloom-label { width: 100px; font-size: .78rem; }
.bloom-bar-bg { flex: 1; height: 10px; background: var(--panel2); border-radius: 999px; overflow: hidden; }
.bloom-bar-fill { height: 100%; border-radius: 999px; transition: width .3s; width: 0; }
.bloom-row .bloom-pts { font-size: .78rem; color: var(--muted); min-width: 30px; text-align: right; }
#qb-round-info { text-align: center; color: var(--muted); font-size: .9rem; }

/* GAME LOG */
#game-log {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 12px; padding: 12px; max-height: 180px; overflow-y: auto;
}
#game-log h3 { font-size: .82rem; color: var(--muted); margin-bottom: 8px; }
.log-entry { font-size: .8rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.log-entry:last-child { border: none; }

/* WIN SCREEN */
#win-screen {
  position: fixed; inset: 0; background: rgba(0,0,0,.85);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 20px;
}
#win-screen.hidden { display: none; }
#win-box {
  background: var(--panel); border: 3px solid var(--good);
  border-radius: 20px; padding: 36px; text-align: center;
  max-width: 420px; width: 100%;
  box-shadow: 0 0 60px rgba(34,197,94,.3);
}
#win-box h1 { font-size: 2.2rem; margin-bottom: 8px; }
#win-box .win-trophy { font-size: 4rem; display: block; margin: 10px 0; }
#win-box .win-winner { font-size: 1.3rem; font-weight: 700; color: var(--good); margin-bottom: 6px; }
#win-box .win-detail { color: var(--muted); margin-bottom: 20px; }

/* SETUP SCREEN */
#setup-screen {
  max-width: 540px; margin: 40px auto; background: var(--panel);
  border: 1px solid var(--border); border-radius: 18px; padding: 28px;
}
#setup-screen h1 { font-size: 1.5rem; margin-bottom: 6px; }
#setup-screen .sub { color: var(--muted); margin-bottom: 20px; font-size: .95rem; }
.setup-row { margin-bottom: 16px; }
.setup-row label { display: block; font-size: .85rem; color: var(--muted); margin-bottom: 5px; font-weight: 600; }
.setup-row input {
  width: 100%; background: var(--panel2); border: 1px solid var(--border);
  border-radius: 9px; padding: 9px 12px; color: var(--ink); font: inherit;
  font-size: .95rem;
}
.setup-row input:focus { outline: 2px solid var(--accent); }
#player-name-inputs { display: flex; flex-direction: column; gap: 8px; }
.msg { padding: 10px 14px; border-radius: 10px; font-weight: 600; margin-top: 10px; display: none; }
.msg.show { display: block; }
.msg.info { background: rgba(99,102,241,.2); border: 1px solid var(--accent); color: #a5b4fc; }
"""

# ---------------------------------------------------------------------------
# JS — Game Engine
# ---------------------------------------------------------------------------
_BOARD_JS = r"""
(function() {
'use strict';

// ─── Content Pack ───────────────────────────────────────────────────────────
const CP = JSON.parse(document.getElementById('endo-board-content').textContent);

// ─── Helpers ────────────────────────────────────────────────────────────────
function el(tag, cls, txt) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (txt != null) e.textContent = txt;
  return e;
}
function shuffle(arr) {
  arr = arr.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
function pickRandom(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function logMsg(msg) {
  const log = document.getElementById('game-log-entries');
  if (!log) return;
  const div = el('div', 'log-entry', msg);
  log.prepend(div);
  if (log.children.length > 30) log.removeChild(log.lastChild);
}

// ─── Player tokens ──────────────────────────────────────────────────────────
const TOKENS = ['🔴','🔵','🟢','🟡'];
const COLORS = ['#ef4444','#3b82f6','#22c55e','#eab308'];
const BLOOM_NAMES = ['Lembrar','Compreender','Aplicar','Analisar','Avaliar','Criar'];
const BLOOM_COLORS = ['#3b82f6','#14b8a6','#22c55e','#eab308','#f97316','#ef4444'];

// ─── Game State ─────────────────────────────────────────────────────────────
let state = {};

// ─── Quiz System ─────────────────────────────────────────────────────────────
const questions = CP.questions || [];
let usedQIdx = [];

function getQuestion() {
  if (!questions.length) return null;
  if (usedQIdx.length >= questions.length) usedQIdx = [];
  const avail = questions.map((_,i)=>i).filter(i=>!usedQIdx.includes(i));
  const idx = pickRandom(avail);
  usedQIdx.push(idx);
  return { ...questions[idx], _idx: idx };
}

function showQuiz(opts) {
  // opts: { onCorrect, onWrong, title }
  const q = getQuestion();
  if (!q) { opts.onCorrect && opts.onCorrect(); return; }
  const overlay = document.getElementById('quiz-overlay');
  overlay.classList.remove('hidden');
  document.getElementById('quiz-modal-title').textContent = opts.title || '❓ Pergunta';
  document.getElementById('quiz-question').textContent = q.q;
  const bloom = q.bloom || 0;
  const badgeEl = document.getElementById('quiz-bloom-badge');
  if (bloom > 0) {
    badgeEl.textContent = BLOOM_NAMES[bloom-1] || '';
    badgeEl.className = 'bloom-badge b' + bloom;
    badgeEl.style.display = '';
  } else {
    badgeEl.style.display = 'none';
  }
  const optsCont = document.getElementById('quiz-options');
  optsCont.innerHTML = '';
  const shuffled = shuffle(q.options.map((o,i)=>({text:o, idx:i})));
  let answered = false;
  shuffled.forEach(opt => {
    const btn = el('button', 'quiz-opt', opt.text);
    btn.onclick = () => {
      if (answered) return;
      answered = true;
      Array.from(optsCont.children).forEach(b => b.disabled = true);
      const correct = opt.idx === q.answer;
      btn.classList.add(correct ? 'correct' : 'wrong');
      if (!correct) {
        const corrBtn = optsCont.children[shuffled.findIndex(s=>s.idx===q.answer)];
        if (corrBtn) corrBtn.classList.add('correct');
      }
      const fb = document.getElementById('quiz-feedback');
      fb.className = 'show ' + (correct ? 'ok' : 'no');
      fb.textContent = correct ? '✓ Correto!' : '✗ Resposta errada!';
      const cont = document.getElementById('quiz-continue');
      cont.className = 'show';
      cont.onclick = () => {
        overlay.classList.add('hidden');
        if (correct) { opts.onCorrect && opts.onCorrect(); }
        else         { opts.onWrong && opts.onWrong(); }
      };
    };
    optsCont.appendChild(btn);
  });
  document.getElementById('quiz-feedback').className = '';
  document.getElementById('quiz-continue').className = '';
}

// ─── Scoreboard ─────────────────────────────────────────────────────────────
function renderScoreboard() {
  const sb = document.getElementById('scoreboard');
  if (!sb) return;
  sb.innerHTML = '';
  state.players.forEach((p, i) => {
    const card = el('div', 'player-card' + (i === state.currentPlayer ? ' active' : ''));
    const nameDiv = el('div', 'player-name');
    nameDiv.innerHTML = TOKENS[i] + ' ' + p.name;
    card.appendChild(nameDiv);
    card.appendChild(el('div', 'player-score', p.score + ' pts'));
    card.appendChild(el('div', 'player-pos', p.posLabel || ''));
    sb.appendChild(card);
  });
}

function addScore(playerIdx, pts) {
  state.players[playerIdx].score += pts;
  renderScoreboard();
}

// ─── Win Screen ─────────────────────────────────────────────────────────────
function showWin(winner, detail) {
  document.getElementById('win-screen').classList.remove('hidden');
  document.getElementById('win-winner').textContent = TOKENS[winner] + ' ' + state.players[winner].name;
  document.getElementById('win-detail').textContent = detail || 'Parabéns!';
}

// ─── Log helper ─────────────────────────────────────────────────────────────
function sideLog() {
  const panel = document.getElementById('side-panel');
  if (!panel) return;
  const logDiv = el('div', 'card' /* reuse look */);
  logDiv.id = 'game-log';
  const h3 = el('h3', null, '📋 Log');
  const entries = el('div'); entries.id = 'game-log-entries';
  logDiv.appendChild(h3); logDiv.appendChild(entries);
  panel.appendChild(logDiv);
}

// ═══════════════════════════════════════════════════════════════════════════
// TRACK GAME
// ═══════════════════════════════════════════════════════════════════════════
function initTrack() {
  const config = CP.config || {};
  const totalSpaces = CP.spaces_count || config.spaces || 36;
  const spaces = CP.spaces || buildDefaultSpaces(totalSpaces);

  state = {
    type: 'track',
    players: state.players,
    currentPlayer: 0,
    positions: state.players.map(() => 0),
    spaces,
    totalSpaces,
    rolling: false,
    waitingForQuiz: false,
    finished: false,
  };
  state.players.forEach((p, i) => { p.score = 0; p.posLabel = 'Casa 0'; });

  // Layout
  document.getElementById('board-container').innerHTML = '';
  const trackEl = el('div'); trackEl.id = 'track-grid';
  document.getElementById('board-container').appendChild(trackEl);

  const cols = Math.ceil(Math.sqrt(totalSpaces * 1.4));
  trackEl.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

  renderTrack();
  renderScoreboard();

  // Side panel
  const side = document.getElementById('side-panel');
  side.innerHTML = '';

  // Dice
  const diceDiv = el('div'); diceDiv.id = 'dice-area';
  diceDiv.innerHTML = `
    <div style="font-size:.85rem;color:var(--muted);margin-bottom:4px">Vez de:</div>
    <div id="dice-whose-turn" style="font-weight:700;font-size:1rem"></div>
    <div id="dice-face" style="font-size:3.5rem;text-align:center;margin:8px 0">🎲</div>
    <div id="dice-result" style="text-align:center;color:var(--muted);font-size:.9rem"></div>
    <button class="btn" id="roll-btn" style="width:100%;margin-top:10px">🎲 Jogar Dado</button>
  `;
  side.appendChild(diceDiv);
  document.getElementById('roll-btn').onclick = rollDice;
  sideLog();
  updateDiceUI();
}

function buildDefaultSpaces(n) {
  const types = ['normal','quiz','bonus','penalty','special'];
  const weights = [0.5, 0.25, 0.1, 0.1, 0.05];
  return Array.from({length: n}, (_, i) => {
    if (i === 0) return {type:'start', icon:'🏁'};
    if (i === n-1) return {type:'end', icon:'🏆'};
    const r = Math.random();
    let cum = 0, type = 'normal';
    for (let j = 0; j < types.length; j++) {
      cum += weights[j];
      if (r < cum) { type = types[j]; break; }
    }
    const icons = {normal:'', quiz:'❓', bonus:'⭐', penalty:'💀', special:'🎁'};
    return {type, icon: icons[type] || ''};
  });
}

const DICE_FACES = ['⚀','⚁','⚂','⚃','⚄','⚅'];

function updateDiceUI() {
  const whose = document.getElementById('dice-whose-turn');
  if (whose) whose.textContent = TOKENS[state.currentPlayer] + ' ' + state.players[state.currentPlayer].name;
}

function rollDice() {
  if (state.rolling || state.finished) return;
  state.rolling = true;
  const btn = document.getElementById('roll-btn');
  btn.disabled = true;
  const face = document.getElementById('dice-face');
  face.classList.add('rolling');
  let ticks = 0;
  const interval = setInterval(() => {
    face.textContent = DICE_FACES[Math.floor(Math.random()*6)];
    ticks++;
    if (ticks >= 8) {
      clearInterval(interval);
      const val = Math.floor(Math.random()*6) + 1;
      face.textContent = DICE_FACES[val-1];
      face.classList.remove('rolling');
      document.getElementById('dice-result').textContent = 'Tirou ' + val;
      state.rolling = false;
      movePlayer(state.currentPlayer, val);
    }
  }, 70);
}

function movePlayer(playerIdx, steps) {
  const oldPos = state.positions[playerIdx];
  const newPos = Math.min(oldPos + steps, state.totalSpaces - 1);
  state.positions[playerIdx] = newPos;
  state.players[playerIdx].posLabel = 'Casa ' + newPos;
  logMsg(TOKENS[playerIdx] + ' ' + state.players[playerIdx].name + ' avançou ' + steps + ' → casa ' + newPos);
  renderTrack();
  renderScoreboard();

  if (newPos >= state.totalSpaces - 1) {
    addScore(playerIdx, 20);
    logMsg('🏆 ' + state.players[playerIdx].name + ' chegou ao fim!');
    state.finished = true;
    setTimeout(() => showWin(playerIdx, 'Chegou à casa final com ' + state.players[playerIdx].score + ' pontos!'), 400);
    return;
  }

  const space = state.spaces[newPos];
  setTimeout(() => landOnSpace(playerIdx, space, newPos), 350);
}

function landOnSpace(playerIdx, space, pos) {
  const btn = document.getElementById('roll-btn');
  switch (space.type) {
    case 'quiz':
      logMsg('❓ Pergunta para ' + state.players[playerIdx].name + '!');
      showQuiz({
        title: '❓ Pergunta — acerte para ganhar 5 pts!',
        onCorrect: () => {
          addScore(playerIdx, 5);
          logMsg('✓ Correto! +5 pts');
          nextTurn();
        },
        onWrong: () => {
          state.positions[playerIdx] = Math.max(0, pos - 2);
          state.players[playerIdx].posLabel = 'Casa ' + state.positions[playerIdx];
          logMsg('✗ Errou! Voltou 2 casas.');
          renderTrack(); renderScoreboard();
          nextTurn();
        }
      });
      return;
    case 'bonus':
      addScore(playerIdx, 3);
      logMsg('⭐ Bônus! +3 pts e avança 2 casas');
      movePlayer(playerIdx, 2);
      return;
    case 'penalty':
      logMsg('💀 Penalidade! -2 pts e volta 1 casa');
      addScore(playerIdx, -2);
      state.positions[playerIdx] = Math.max(0, pos - 1);
      state.players[playerIdx].posLabel = 'Casa ' + state.positions[playerIdx];
      renderTrack(); renderScoreboard();
      nextTurn();
      return;
    case 'special':
      addScore(playerIdx, 2);
      logMsg('🎁 Especial! +2 pts');
      nextTurn();
      return;
    default:
      nextTurn();
  }
}

function nextTurn() {
  const btn = document.getElementById('roll-btn');
  state.currentPlayer = (state.currentPlayer + 1) % state.players.length;
  updateDiceUI();
  renderScoreboard();
  if (btn) btn.disabled = false;
}

function renderTrack() {
  const grid = document.getElementById('track-grid');
  if (!grid) return;
  grid.innerHTML = '';
  state.spaces.forEach((sp, idx) => {
    const cell = el('div', 'track-cell ' + (sp.type || 'normal'));
    const numEl = el('span', 'cell-num', idx);
    cell.appendChild(numEl);
    if (sp.icon) cell.appendChild(el('span', 'cell-icon', sp.icon));
    // tokens
    const tokensHere = state.positions.map((p,i)=>i).filter(i=>state.positions[i]===idx);
    if (tokensHere.length) {
      const tDiv = el('div', 'tokens');
      tokensHere.forEach(i => tDiv.appendChild(el('span', 'token', TOKENS[i])));
      cell.appendChild(tDiv);
    }
    grid.appendChild(cell);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// GRID GAME (tic-tac-toe default, extensible)
// ═══════════════════════════════════════════════════════════════════════════
function initGrid() {
  const config = CP.config || {};
  const size = config.grid_size || 3;
  const mode = config.grid_mode || 'ttt'; // ttt | checkers

  state = {
    type: 'grid',
    players: state.players,
    currentPlayer: 0,
    size,
    mode,
    board: Array.from({length: size}, () => Array(size).fill(null)),
    selected: null,
    finished: false,
  };
  state.players.forEach(p => { p.score = 0; p.posLabel = ''; });

  document.getElementById('board-container').innerHTML = '';
  const gridEl = el('div'); gridEl.id = 'grid-board';
  gridEl.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
  gridEl.style.maxWidth = `${Math.min(500, size * 100)}px`;
  document.getElementById('board-container').appendChild(gridEl);

  if (mode === 'ttt') initTTT(gridEl);
  else initCheckers(gridEl);

  renderScoreboard();
  const side = document.getElementById('side-panel');
  side.innerHTML = '';
  const info = el('div');
  info.style.cssText = 'background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px';
  info.innerHTML = '<div style="font-size:.85rem;color:var(--muted);margin-bottom:6px">Modo</div>' +
    '<div style="font-weight:700">' + (mode==='ttt'?'Jogo da Velha':'Damas') + '</div>';
  side.appendChild(info);
  sideLog();
}

function initTTT(gridEl) {
  state.board = Array.from({length:3}, ()=>Array(3).fill(null));
  renderTTT(gridEl);
}

function renderTTT(gridEl) {
  if (!gridEl) gridEl = document.getElementById('grid-board');
  if (!gridEl) return;
  gridEl.innerHTML = '';
  const symbols = ['✕','○'];
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const val = state.board[r][c];
      const cell = el('div', 'grid-cell ' + ((r+c)%2===0?'light':'dark') + (val===0?' ttt-x':val===1?' ttt-o':''));
      cell.textContent = val !== null ? symbols[val] : '';
      if (val === null && !state.finished) {
        cell.onclick = () => playTTT(r, c);
      }
      gridEl.appendChild(cell);
    }
  }
}

function playTTT(r, c) {
  if (state.board[r][c] !== null || state.finished) return;
  const p = state.currentPlayer;
  state.board[r][c] = p;
  logMsg(TOKENS[p] + ' ' + state.players[p].name + ' jogou em ' + r + ',' + c);
  renderTTT();

  const winner = checkTTTWin();
  if (winner !== null) {
    state.finished = true;
    if (winner === -1) {
      logMsg('🤝 Empate!');
      setTimeout(() => showWin(0, 'Empate! Nenhum vencedor.'), 300);
    } else {
      addScore(winner, 10);
      logMsg('🏆 ' + state.players[winner].name + ' venceu!');
      setTimeout(() => showWin(winner, 'Venceu o jogo da velha com 10 pts!'), 300);
    }
    return;
  }

  // Quiz on capture: only if board nearly full (simulate via random chance)
  if (Math.random() < 0.3 && questions.length) {
    showQuiz({
      title: '❓ Bônus — responda para ganhar 3 pts!',
      onCorrect: () => { addScore(p, 3); nextGridTurn(); },
      onWrong:   () => { nextGridTurn(); }
    });
  } else {
    nextGridTurn();
  }
}

function nextGridTurn() {
  state.currentPlayer = (state.currentPlayer + 1) % state.players.length;
  renderScoreboard();
}

function checkTTTWin() {
  const b = state.board;
  const lines = [
    [[0,0],[0,1],[0,2]], [[1,0],[1,1],[1,2]], [[2,0],[2,1],[2,2]],
    [[0,0],[1,0],[2,0]], [[0,1],[1,1],[2,1]], [[0,2],[1,2],[2,2]],
    [[0,0],[1,1],[2,2]], [[0,2],[1,1],[2,0]],
  ];
  for (const line of lines) {
    const [a,b2,c] = line.map(([r,cc])=>state.board[r][cc]);
    if (a !== null && a === b2 && b2 === c) return a;
  }
  if (b.every(row=>row.every(v=>v!==null))) return -1;
  return null;
}

function initCheckers(gridEl) {
  const n = state.size;
  state.board = Array.from({length:n}, (_, r) =>
    Array.from({length:n}, (__, c) => {
      if (r < Math.floor(n/2)-1 && (r+c)%2===1) return {player:1, king:false};
      if (r > Math.floor(n/2) && (r+c)%2===1) return {player:0, king:false};
      return null;
    })
  );
  state.selected = null;
  renderCheckers(gridEl);
}

function renderCheckers(gridEl) {
  if (!gridEl) gridEl = document.getElementById('grid-board');
  if (!gridEl) return;
  gridEl.innerHTML = '';
  const n = state.size;
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const piece = state.board[r][c];
      const isLight = (r+c)%2===0;
      let cls = 'grid-cell ' + (isLight?'light':'dark');
      const isSelected = state.selected && state.selected[0]===r && state.selected[1]===c;
      const isValidMove = state.validMoves && state.validMoves.some(m=>m[0]===r&&m[1]===c);
      if (isSelected) cls += ' selected';
      if (isValidMove) cls += ' valid-move';
      const cell = el('div', cls);
      if (piece) {
        cell.textContent = piece.king
          ? (piece.player===0?'♛':'♚')
          : (piece.player===0?'⬤':'◯');
        cell.style.color = COLORS[piece.player];
        cell.style.fontSize = '1.5rem';
      }
      cell.onclick = () => clickCheckers(r, c);
      gridEl.appendChild(cell);
    }
  }
}

function clickCheckers(r, c) {
  if (state.finished) return;
  const piece = state.board[r][c];
  const p = state.currentPlayer;

  if (state.selected) {
    const isValid = state.validMoves && state.validMoves.some(m=>m[0]===r&&m[1]===c);
    if (isValid) {
      const [sr,sc] = state.selected;
      const midR = (sr+r)/2, midC = (sc+c)/2;
      const captured = Number.isInteger(midR) && state.board[midR][midC] !== null;
      state.board[r][c] = state.board[sr][sc];
      state.board[sr][sc] = null;
      if (captured) {
        state.board[midR][midC] = null;
        logMsg(TOKENS[p]+' capturou uma peça!');
        addScore(p, 2);
        if (questions.length) {
          state.selected = null; state.validMoves = null;
          renderCheckers();
          showQuiz({
            title:'❓ Captura — responda para +5 pts!',
            onCorrect: ()=>{addScore(p,5); finishCheckersMove();},
            onWrong:   ()=>{ finishCheckersMove(); }
          });
          return;
        }
      }
      if ((p===0&&r===0)||(p===1&&r===state.size-1)) state.board[r][c].king=true;
      state.selected = null; state.validMoves = null;
      renderCheckers();
      if (checkCheckersWin()) return;
      nextGridTurn();
    } else if (piece && piece.player === p) {
      selectCheckersPiece(r, c);
    } else {
      state.selected = null; state.validMoves = null;
      renderCheckers();
    }
  } else {
    if (piece && piece.player === p) selectCheckersPiece(r, c);
  }
}

function selectCheckersPiece(r, c) {
  state.selected = [r,c];
  state.validMoves = getCheckersMovesFor(r, c);
  renderCheckers();
}

function finishCheckersMove() {
  state.selected = null; state.validMoves = null;
  if (!checkCheckersWin()) nextGridTurn();
}

function getCheckersMovesFor(r, c) {
  const piece = state.board[r][c];
  if (!piece) return [];
  const dirs = piece.king ? [[-1,-1],[-1,1],[1,-1],[1,1]] :
    piece.player===0 ? [[-1,-1],[-1,1]] : [[1,-1],[1,1]];
  const moves = [];
  const n = state.size;
  dirs.forEach(([dr,dc]) => {
    const nr=r+dr, nc=c+dc;
    if (nr>=0&&nr<n&&nc>=0&&nc<n) {
      if (!state.board[nr][nc]) moves.push([nr,nc]);
      else if (state.board[nr][nc].player!==piece.player) {
        const jr=r+2*dr,jc=c+2*dc;
        if (jr>=0&&jr<n&&jc>=0&&jc<n&&!state.board[jr][jc]) moves.push([jr,jc]);
      }
    }
  });
  return moves;
}

function checkCheckersWin() {
  const counts = [0,0];
  for (let r=0;r<state.size;r++) for (let c=0;c<state.size;c++) {
    if (state.board[r][c]) counts[state.board[r][c].player]++;
  }
  for (let p=0;p<2;p++) {
    if (counts[p]===0) {
      const winner = 1-p;
      state.finished=true;
      addScore(winner,15);
      logMsg('🏆 '+state.players[winner].name+' venceu as damas!');
      setTimeout(()=>showWin(winner,'Eliminou todas as peças adversárias!'),300);
      return true;
    }
  }
  return false;
}

// ═══════════════════════════════════════════════════════════════════════════
// CARDS ONLY
// ═══════════════════════════════════════════════════════════════════════════
function initCards() {
  const config = CP.config || {};
  const handSize = config.hand_size || 5;
  const winScore = config.win_score || 20;

  const deck = buildCardDeck();
  state = {
    type: 'cards',
    players: state.players,
    currentPlayer: 0,
    deck: shuffle(deck),
    discard: [],
    hands: state.players.map(() => []),
    handSize,
    winScore,
    selectedCard: null,
    finished: false,
  };
  state.players.forEach(p => { p.score = 0; p.posLabel = ''; });

  // Deal initial hands
  state.players.forEach((_, pi) => {
    for (let i=0;i<handSize;i++) {
      if (state.deck.length) state.hands[pi].push(state.deck.pop());
    }
  });

  renderCardsUI();
  renderScoreboard();
  sideLog();
}

function buildCardDeck() {
  const types = ['quiz','action','bonus','penalty'];
  const icons = {quiz:'❓', action:'⚡', bonus:'⭐', penalty:'💀'};
  const cards = [];
  for (let i=0; i<40; i++) {
    const type = types[i % types.length];
    const bloom = Math.floor(Math.random()*6)+1;
    cards.push({
      id: i, type, icon: icons[type],
      text: type==='quiz'?'Pergunta Bloom '+(BLOOM_NAMES[bloom-1]||''):
            type==='action'?'Ação especial':
            type==='bonus'?'Bônus +3 pts':'Penalidade -1 pt',
      bloom, pts: type==='bonus'?3:type==='penalty'?-1:5,
    });
  }
  return cards;
}

function renderCardsUI() {
  const bc = document.getElementById('board-container');
  bc.innerHTML = '';
  const area = el('div'); area.id = 'cards-area';

  // Piles row
  const pilesRow = el('div'); pilesRow.id = 'piles-row';
  const deckPile = el('div', 'card-back');
  deckPile.innerHTML = '🂠';
  deckPile.title = 'Comprar carta';
  deckPile.onclick = drawCard;

  const deckInfo = el('div');
  deckInfo.innerHTML = `<div style="text-align:center;margin-bottom:6px">
    <div style="font-size:.8rem;color:var(--muted)">Baralho</div>
    <div style="font-weight:700">${state.deck.length} cartas</div>
  </div>`;

  const discardPile = el('div', 'card-pile');
  discardPile.id = 'discard-top';
  const topCard = state.discard[state.discard.length-1];
  if (topCard) {
    discardPile.innerHTML = `<div style="font-size:2rem">${topCard.icon}</div><div style="font-size:.7rem">${topCard.type}</div>`;
  } else {
    discardPile.innerHTML = '<div style="font-size:.8rem;color:var(--muted)">Descarte</div>';
  }

  pilesRow.appendChild(deckInfo);
  pilesRow.appendChild(deckPile);
  pilesRow.appendChild(discardPile);
  area.appendChild(pilesRow);

  // Turn info
  const turnInfo = el('div');
  turnInfo.style.cssText = 'text-align:center;padding:6px;font-size:.9rem;color:var(--muted)';
  const cp = state.players[state.currentPlayer];
  turnInfo.textContent = 'Vez de: ' + TOKENS[state.currentPlayer] + ' ' + cp.name;
  area.appendChild(turnInfo);

  // Hand
  const handLabel = el('div');
  handLabel.style.cssText = 'font-size:.82rem;color:var(--muted);margin:8px 0 4px';
  handLabel.textContent = 'Mão — clique para selecionar, depois Jogar ou Descartar';
  area.appendChild(handLabel);

  const handArea = el('div'); handArea.id = 'hand-area';
  const hand = state.hands[state.currentPlayer];
  hand.forEach((card, idx) => {
    const cardEl = el('div', 'game-card' + (state.selectedCard===idx?' selected':''));
    cardEl.innerHTML = `
      <span class="card-type-badge card-type-${card.type}">${card.type}</span>
      <span class="card-icon">${card.icon}</span>
      <span class="card-text">${card.text}</span>
      <span class="bloom-badge b${card.bloom}" style="font-size:.6rem">${BLOOM_NAMES[card.bloom-1]||''}</span>
    `;
    cardEl.onclick = () => { state.selectedCard = state.selectedCard===idx?null:idx; renderCardsUI(); };
    handArea.appendChild(cardEl);
  });
  area.appendChild(handArea);

  // Action buttons
  const actRow = el('div');
  actRow.style.cssText = 'display:flex;gap:10px;justify-content:center;margin-top:12px';
  const playBtn = el('button', 'btn', '▶ Jogar');
  playBtn.onclick = playCard;
  const discBtn = el('button', 'btn ghost', '🗑 Descartar');
  discBtn.onclick = discardCard;
  const drawBtn = el('button', 'btn ghost sm', '+ Comprar');
  drawBtn.onclick = drawCard;
  actRow.appendChild(playBtn); actRow.appendChild(discBtn); actRow.appendChild(drawBtn);
  area.appendChild(actRow);

  bc.appendChild(area);
}

function drawCard() {
  if (!state.deck.length) { logMsg('Baralho vazio!'); return; }
  const card = state.deck.pop();
  state.hands[state.currentPlayer].push(card);
  logMsg(TOKENS[state.currentPlayer]+' comprou uma carta');
  renderCardsUI(); renderScoreboard();
}

function playCard() {
  if (state.selectedCard === null) { logMsg('Selecione uma carta primeiro'); return; }
  const p = state.currentPlayer;
  const hand = state.hands[p];
  const card = hand[state.selectedCard];
  hand.splice(state.selectedCard, 1);
  state.selectedCard = null;
  state.discard.push(card);

  if (card.type === 'quiz') {
    logMsg(TOKENS[p]+' jogou carta de quiz');
    showQuiz({
      title: '❓ Carta de Quiz — ' + BLOOM_NAMES[card.bloom-1],
      onCorrect: () => { addScore(p, card.pts); logMsg('✓ Correto! +'+card.pts+' pts'); finishCardTurn(); },
      onWrong:   () => { logMsg('✗ Errou!'); finishCardTurn(); }
    });
  } else if (card.type === 'bonus') {
    addScore(p, card.pts);
    logMsg(TOKENS[p]+' usou bônus: +'+card.pts+' pts');
    finishCardTurn();
  } else if (card.type === 'penalty') {
    const target = (p+1) % state.players.length;
    addScore(target, card.pts);
    logMsg(TOKENS[p]+' aplicou penalidade em '+state.players[target].name);
    finishCardTurn();
  } else {
    addScore(p, 1);
    logMsg(TOKENS[p]+' jogou ação: +1 pt');
    finishCardTurn();
  }
}

function discardCard() {
  if (state.selectedCard === null) { logMsg('Selecione uma carta para descartar'); return; }
  const p = state.currentPlayer;
  const card = state.hands[p].splice(state.selectedCard, 1)[0];
  state.selectedCard = null;
  state.discard.push(card);
  logMsg(TOKENS[p]+' descartou uma carta');
  finishCardTurn();
}

function finishCardTurn() {
  const p = state.currentPlayer;
  if (state.players[p].score >= state.winScore) {
    state.finished = true;
    showWin(p, 'Atingiu '+state.winScore+' pontos primeiro!');
    return;
  }
  if (!state.deck.length && state.hands.every(h=>!h.length)) {
    // Game over: most points wins
    let best=0, bestScore=-Infinity;
    state.players.forEach((pl,i)=>{ if(pl.score>bestScore){bestScore=pl.score;best=i;} });
    state.finished=true;
    showWin(best,'Baralho esgotado! Maior pontuação: '+bestScore+' pts');
    return;
  }
  state.currentPlayer = (state.currentPlayer+1) % state.players.length;
  renderCardsUI(); renderScoreboard();
}

// ═══════════════════════════════════════════════════════════════════════════
// QUIZ BATTLE
// ═══════════════════════════════════════════════════════════════════════════
function initQuizBattle() {
  const config = CP.config || {};
  const winScore = config.win_score || 10;
  const timeLimit = config.time_limit || 20;
  const totalRounds = config.rounds || 15;

  state = {
    type: 'quiz_battle',
    players: state.players,
    currentPlayer: 0,
    scores: state.players.map(()=>0),
    bloomPts: state.players.map(()=>Array(6).fill(0)),
    winScore,
    timeLimit,
    totalRounds,
    round: 0,
    answered: false,
    finished: false,
    timerHandle: null,
    timeLeft: timeLimit,
  };
  state.players.forEach((p,i)=>{ p.score=0; p.posLabel=''; });

  renderQBUI();
  renderScoreboard();
  startQBRound();
}

function renderQBUI() {
  const bc = document.getElementById('board-container');
  bc.innerHTML = '';
  const area = el('div'); area.id = 'qb-area';

  const roundInfo = el('div'); roundInfo.id = 'qb-round-info';
  area.appendChild(roundInfo);

  const qBox = el('div'); qBox.id = 'qb-question-box';
  qBox.innerHTML = `
    <div id="qb-bloom-badge" style="margin-bottom:8px"></div>
    <div id="qb-question">Carregando...</div>
    <div id="qb-timer" style="margin:10px 0">—</div>
    <div id="qb-options" class="qb-options" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"></div>
    <div id="qb-feedback" style="margin-top:12px;font-weight:600;display:none"></div>
    <button id="qb-next" style="margin-top:12px;width:100%;padding:10px;background:var(--accent);color:#fff;border:none;border-radius:10px;font:inherit;font-weight:700;cursor:pointer;display:none">Próxima →</button>
  `;
  area.appendChild(qBox);
  bc.appendChild(area);

  // Side panel: bloom bars
  const side = document.getElementById('side-panel');
  side.innerHTML = '';
  const barsDiv = el('div'); barsDiv.id = 'qb-bloom-bars';
  barsDiv.innerHTML = '<h3>Pontos por Bloom</h3>';
  BLOOM_NAMES.forEach((name, bi) => {
    const row = el('div', 'bloom-row');
    const label = el('div', 'bloom-label', name);
    const bgDiv = el('div', 'bloom-bar-bg');
    const fill = el('div', 'bloom-bar-fill');
    fill.id = 'bloom-fill-' + bi;
    fill.style.background = BLOOM_COLORS[bi];
    bgDiv.appendChild(fill);
    const pts = el('div', 'bloom-pts', '0');
    pts.id = 'bloom-pts-' + bi;
    row.appendChild(label); row.appendChild(bgDiv); row.appendChild(pts);
    barsDiv.appendChild(row);
  });
  side.appendChild(barsDiv);
  sideLog();
}

let qbTimerInterval = null;

function startQBRound() {
  if (state.finished) return;
  state.round++;
  state.answered = false;

  document.getElementById('qb-round-info').textContent =
    'Rodada ' + state.round + ' / ' + state.totalRounds + ' — Objetivo: ' + state.winScore + ' pts';

  const q = getQuestion();
  if (!q) return;

  const bloomIdx = (q.bloom||1) - 1;
  const badgeEl = document.getElementById('qb-bloom-badge');
  badgeEl.innerHTML = '<span class="bloom-badge b'+(q.bloom||1)+'">'+BLOOM_NAMES[bloomIdx]+'</span>';

  document.getElementById('qb-question').textContent = q.q;
  document.getElementById('qb-feedback').style.display = 'none';
  document.getElementById('qb-next').style.display = 'none';

  const optsCont = document.getElementById('qb-options');
  optsCont.innerHTML = '';
  const shuffled = shuffle(q.options.map((o,i)=>({text:o,idx:i})));
  shuffled.forEach(opt => {
    const btn = el('button', 'qb-opt', opt.text);
    btn.onclick = () => answerQB(opt.idx, q.answer, bloomIdx, shuffled, q);
    optsCont.appendChild(btn);
  });

  // Timer
  state.timeLeft = state.timeLimit;
  updateQBTimer();
  if (qbTimerInterval) clearInterval(qbTimerInterval);
  qbTimerInterval = setInterval(() => {
    state.timeLeft--;
    updateQBTimer();
    if (state.timeLeft <= 0) {
      clearInterval(qbTimerInterval);
      if (!state.answered) {
        document.getElementById('qb-feedback').textContent = '⏰ Tempo esgotado!';
        document.getElementById('qb-feedback').style.display='block';
        Array.from(optsCont.children).forEach(b=>b.disabled=true);
        state.answered = true;
        scheduleNextQB();
      }
    }
  }, 1000);
}

function updateQBTimer() {
  const t = document.getElementById('qb-timer');
  if (t) t.textContent = '⏱ ' + state.timeLeft + 's';
}

function answerQB(chosen, correct, bloomIdx, shuffled, q) {
  if (state.answered) return;
  state.answered = true;
  clearInterval(qbTimerInterval);

  const p = state.currentPlayer; // first to click wins
  const isCorrect = chosen === correct;
  const optsCont = document.getElementById('qb-options');
  Array.from(optsCont.children).forEach((b,i) => {
    b.disabled = true;
    if (shuffled[i].idx === correct) b.classList.add('correct');
    else if (shuffled[i].idx === chosen && !isCorrect) b.classList.add('wrong');
  });

  const fb = document.getElementById('qb-feedback');
  fb.style.display = 'block';
  if (isCorrect) {
    const pts = q.bloom || 1;
    addScore(p, pts);
    state.bloomPts[p][bloomIdx] = (state.bloomPts[p][bloomIdx]||0) + pts;
    updateBloomBars();
    fb.style.color = 'var(--good)';
    fb.textContent = '✓ ' + state.players[p].name + ' acertou! +' + pts + ' pts';
    logMsg('✓ '+TOKENS[p]+' '+state.players[p].name+' acertou +'+pts+' pts');
  } else {
    fb.style.color = 'var(--bad)';
    fb.textContent = '✗ Errou!';
  }

  // Alternate who answers next
  state.currentPlayer = (state.currentPlayer + 1) % state.players.length;
  renderScoreboard();

  if (isCorrect && state.players[p].score >= state.winScore) {
    clearInterval(qbTimerInterval);
    state.finished = true;
    setTimeout(()=>showWin(p, 'Primeiro a atingir '+state.winScore+' pontos!'), 500);
    return;
  }

  scheduleNextQB();
}

function scheduleNextQB() {
  const nextBtn = document.getElementById('qb-next');
  if (!nextBtn) return;
  nextBtn.style.display = 'block';
  nextBtn.onclick = () => {
    if (state.round >= state.totalRounds) {
      // Most points wins
      let best=0, bestScore=-Infinity;
      state.players.forEach((p,i)=>{ if(p.score>bestScore){bestScore=p.score;best=i;} });
      state.finished=true;
      showWin(best,'Fim das '+state.totalRounds+' rodadas! Maior pontuação: '+bestScore+' pts');
    } else {
      startQBRound();
    }
  };
}

function updateBloomBars() {
  const maxPts = Math.max(10, ...state.players.flatMap((_,pi)=>state.bloomPts[pi]));
  BLOOM_NAMES.forEach((_, bi) => {
    const total = state.players.reduce((sum,_,pi)=>sum+(state.bloomPts[pi][bi]||0),0);
    const fill = document.getElementById('bloom-fill-'+bi);
    const pts = document.getElementById('bloom-pts-'+bi);
    if (fill) fill.style.width = Math.round(100*total/Math.max(1,maxPts))+'%';
    if (pts) pts.textContent = total;
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SETUP SCREEN
// ═══════════════════════════════════════════════════════════════════════════
function showSetup() {
  document.getElementById('game-wrap').innerHTML = `
    <div id="setup-screen">
      <h1>🎲 ${CP.title || 'Board Game'}</h1>
      <div class="sub">${CP.board_type ? CP.board_type.toUpperCase() + ' · ' : ''}Jogo educacional Endo-DSL</div>
      <div class="setup-row">
        <label>Número de jogadores (2–4)</label>
        <input type="number" id="num-players" min="2" max="4" value="${CP.players||2}">
      </div>
      <div id="player-name-inputs"></div>
      <button class="btn" id="start-btn" style="width:100%;margin-top:18px;padding:14px;font-size:1.05rem">▶ Iniciar Jogo</button>
    </div>
  `;
  updateNameInputs();
  document.getElementById('num-players').oninput = updateNameInputs;
  document.getElementById('start-btn').onclick = startGame;
}

function updateNameInputs() {
  const n = parseInt(document.getElementById('num-players').value) || 2;
  const cont = document.getElementById('player-name-inputs');
  cont.innerHTML = '';
  for (let i=0; i<n; i++) {
    const row = el('div', 'setup-row');
    row.innerHTML = `<label>${TOKENS[i]} Jogador ${i+1}</label>
      <input type="text" id="pname-${i}" value="Jogador ${i+1}" placeholder="Nome do jogador">`;
    cont.appendChild(row);
  }
}

function startGame() {
  const n = parseInt(document.getElementById('num-players').value) || 2;
  const players = [];
  for (let i=0;i<n;i++) {
    const inp = document.getElementById('pname-'+i);
    players.push({name: inp ? inp.value.trim() || ('Jogador '+(i+1)) : ('Jogador '+(i+1)), score:0, posLabel:''});
  }

  // Build full layout
  document.getElementById('game-wrap').innerHTML = `
    <div id="game-header">
      <h1>🎲 ${CP.title||'Board Game'}</h1>
      <div id="header-controls">
        <button class="btn ghost sm" id="new-game-btn">↻ Novo Jogo</button>
      </div>
    </div>
    <div id="scoreboard"></div>
    <div id="game-area">
      <div id="board-container"></div>
      <div id="side-panel"></div>
    </div>
    <div id="quiz-overlay" class="hidden">
      <div id="quiz-modal">
        <h2 id="quiz-modal-title">❓ Pergunta</h2>
        <div id="quiz-bloom-badge" style="margin-bottom:8px"></div>
        <div id="quiz-question"></div>
        <div id="quiz-options" class="quiz-options"></div>
        <div id="quiz-feedback"></div>
        <button id="quiz-continue">Continuar →</button>
      </div>
    </div>
    <div id="win-screen" class="hidden">
      <div id="win-box">
        <span class="win-trophy">🏆</span>
        <div class="win-winner" id="win-winner"></div>
        <div class="win-detail" id="win-detail"></div>
        <h1 style="margin-bottom:16px">Vitória!</h1>
        <button class="btn" id="win-new-game" style="width:100%">↻ Jogar Novamente</button>
      </div>
    </div>
  `;
  document.getElementById('new-game-btn').onclick = showSetup;
  document.getElementById('win-new-game').onclick = showSetup;

  state.players = players;

  const boardType = CP.board_type || 'track';
  if (boardType === 'track' || boardType === 'trilha') initTrack();
  else if (boardType === 'grid') initGrid();
  else if (boardType === 'cards_only' || boardType === 'cards') initCards();
  else if (boardType === 'quiz_battle' || boardType === 'quiz') initQuizBattle();
  else initTrack();
}

// ─── BOOT ───────────────────────────────────────────────────────────────────
showSetup();

})();
"""

_HTML_SHELL = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="Endo-DSL Board Game Compiler v__VERSION__">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<div id="game-wrap"></div>
<!-- ENDO-DSL BOARD GAME CONTENT PACK -->
<script id="endo-board-content" type="application/json">__CONTENT_PACK__</script>
<script>__JS__</script>
</body>
</html>
"""


def render_board_game(spec_dict: dict, version: str = "1.0.0") -> str:
    """Render a complete self-contained HTML5 board game from a spec dict."""
    pack_json = json.dumps(spec_dict, ensure_ascii=False)
    pack_json = pack_json.replace("</", "<\\/")

    html = _HTML_SHELL
    html = html.replace("__CSS__", _BOARD_CSS)
    html = html.replace("__JS__", _BOARD_JS)
    html = html.replace("__TITLE__", _escape(spec_dict.get("title", "Board Game")))
    html = html.replace("__CONTENT_PACK__", pack_json)
    html = html.replace("__VERSION__", version)
    return html


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
