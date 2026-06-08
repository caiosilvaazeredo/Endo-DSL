"""Servidor web da Endo-DSL (apenas biblioteca padrão).

Expõe a jornada do usuário como aplicação web: estúdio de design (Fases 1–6),
biblioteca de componentes, fila de curadoria e relatórios. Usa ``http.server``
em modo single-thread (uma conexão SQLite, sequencial e segura para uso local).

Não há dependências externas — coerente com a filosofia do projeto.
"""

from __future__ import annotations

import json
import mimetypes
import re
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from endo_dsl.compiler.compiler import CompileError
from endo_dsl.library.models import SearchFilters
from endo_dsl.platform import Platform
from endo_dsl.web import views

_STATIC = Path(__file__).parent / "static"

# Tipo de um handler: recebe (platform, match, query, body) -> Response
Response = Tuple[int, str, bytes]


def _html(body: str, status: int = 200) -> Response:
    return status, "text/html; charset=utf-8", body.encode("utf-8")


def _json(data: Any, status: int = 200) -> Response:
    return status, "application/json; charset=utf-8", json.dumps(
        data, ensure_ascii=False).encode("utf-8")


class Router:
    def __init__(self) -> None:
        self.routes: List[Tuple[str, re.Pattern, Callable]] = []

    def add(self, method: str, pattern: str, handler: Callable) -> None:
        regex = re.compile("^" + re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern) + "$")
        self.routes.append((method, regex, handler))

    def match(self, method: str, path: str):
        for m, regex, handler in self.routes:
            if m != method:
                continue
            mo = regex.match(path)
            if mo:
                return handler, mo.groupdict()
        return None, None


router = Router()


def route(method: str, pattern: str):
    def deco(fn: Callable) -> Callable:
        router.add(method, pattern, fn)
        return fn
    return deco


# --------------------------------------------------------------------------- #
# Páginas (HTML)
# --------------------------------------------------------------------------- #
@route("GET", "/")
def home(p: Platform, m, q, body) -> Response:
    stats = {
        "components": len(p.search_components()),
        "canonical": len(p.search_components(SearchFilters(status="canonical"))),
        "prototypes": len(p.list_prototypes()),
        "backend": p.backend.name,
    }
    return _html(views.home_page(stats))


@route("GET", "/studio")
def studio(p: Platform, m, q, body) -> Response:
    return _html(views.studio_page())


@route("GET", "/library")
def library(p: Platform, m, q, body) -> Response:
    filters = SearchFilters(
        text=_first(q, "text"), bloom_level=_first(q, "bloom"),
        mechanic_type=_first(q, "type"), domain=_first(q, "domain"),
        status=_first(q, "status"),
    )
    comps = p.search_components(filters)
    return _html(views.library_page(comps, q))


@route("GET", "/component/<key>")
def component_detail(p: Platform, m, q, body) -> Response:
    comp = p.get_component(m["key"])
    if not comp:
        return _html(views.not_found("Componente não encontrado"), 404)
    versions = p.repo.versions(comp.id)
    history = p.repo.curation_history(comp.id)
    return _html(views.component_page(comp, versions, history))


@route("GET", "/curator")
def curator(p: Platform, m, q, body) -> Response:
    return _html(views.curator_page(p.curation_queue()))


@route("GET", "/report")
def report(p: Platform, m, q, body) -> Response:
    return _html(views.report_page(p.comparison_report()))


@route("GET", "/docs")
def docs(p: Platform, m, q, body) -> Response:
    from endo_dsl.dsl import limits
    grammar = (Path(__file__).parent.parent / "dsl" / "grammar.ebnf").read_text(encoding="utf-8")
    return _html(views.docs_page(grammar, limits.as_dict()))


@route("GET", "/evaluate/<pid>")
def evaluate_page(p: Platform, m, q, body) -> Response:
    proto = p.get_prototype(int(m["pid"]))
    if not proto:
        return _html(views.not_found("Protótipo não encontrado"), 404)
    return _html(views.evaluate_page(proto))


@route("GET", "/prototype/<pid>")
def serve_prototype(p: Platform, m, q, body) -> Response:
    html = p.prototype_html(int(m["pid"]))
    if html is None:
        return _html(views.not_found("Protótipo não encontrado"), 404)
    return _html(html)


@route("GET", "/prototype/<pid>/traceability")
def serve_traceability(p: Platform, m, q, body) -> Response:
    proto = p.get_prototype(int(m["pid"]))
    if not proto:
        return _html(views.not_found("Protótipo não encontrado"), 404)
    from endo_dsl.dsl.parser import parse
    spec_row = p.db.query_one("SELECT dsl_source FROM specifications WHERE id = ?",
                              (proto["spec_id"],))
    if spec_row:
        from endo_dsl.compiler import traceability as trace
        return _html(trace.as_html(parse(spec_row["dsl_source"])))
    return _json(proto["traceability"])


# --------------------------------------------------------------------------- #
# API (JSON)
# --------------------------------------------------------------------------- #
@route("POST", "/api/session")
def api_session(p: Platform, m, q, body) -> Response:
    sid = p.create_session(body.get("name", "Sessão sem nome"), body)
    return _json({"session_id": sid})


@route("POST", "/api/retrieve")
def api_retrieve(p: Platform, m, q, body) -> Response:
    from endo_dsl.agents.context import DesignContext
    ctx = DesignContext.from_dict(body)
    retrieved = p.retrieve(ctx, top_k=int(body.get("top_k", 6)))
    return _json({"components": [rc.to_dict() for rc in retrieved]})


@route("POST", "/api/generate")
def api_generate(p: Platform, m, q, body) -> Response:
    sid = body.get("session_id")
    if sid is None:
        sid = p.create_session(body.get("name", "Sessão"), body)
    keys = body.get("selected_keys")
    res = p.generate(int(sid), selected_keys=keys,
                     from_scratch=bool(body.get("from_scratch")))
    out = res.to_dict()
    out["session_id"] = sid
    out["metrics"] = p.generation_metrics(int(sid))
    return _json(out)


@route("POST", "/api/validate")
def api_validate(p: Platform, m, q, body) -> Response:
    return _json(p.validate(body.get("dsl", "")))


@route("POST", "/api/compile")
def api_compile(p: Platform, m, q, body) -> Response:
    try:
        result = p.compile(body.get("dsl", ""), session_id=body.get("session_id"),
                           origin=body.get("origin", "auto"))
    except CompileError as exc:
        return _json({"ok": False, "errors": exc.messages}, 400)
    result.pop("html", None)  # não precisa devolver o HTML inteiro ao cliente
    result["ok"] = True
    return _json(result)


@route("POST", "/api/reparametrize")
def api_reparametrize(p: Platform, m, q, body) -> Response:
    res = p.reparametrize(int(body["prototype_id"]), domain=body.get("domain"),
                          topic=body.get("topic"))
    res.pop("html", None)
    return _json(res)


@route("POST", "/api/curate")
def api_curate(p: Platform, m, q, body) -> Response:
    action = body.get("action")
    cid = int(body["component_id"])
    if action == "approve":
        p.approve_component(cid, curator=body.get("curator"), justification=body.get("note", ""))
    elif action == "reject":
        p.reject_component(cid, curator=body.get("curator"), justification=body.get("note", ""))
    elif action == "request_changes":
        p.request_component_changes(cid, curator=body.get("curator"),
                                    justification=body.get("note", ""))
    else:
        return _json({"ok": False, "error": "ação inválida"}, 400)
    return _json({"ok": True})


@route("POST", "/api/contribute")
def api_contribute(p: Platform, m, q, body) -> Response:
    try:
        cid = p.contribute_component(
            name=body["name"], dsl_signature=body["dsl_signature"],
            bloom_level=body["bloom_level"], mechanic_type=body["mechanic_type"],
            description=body["description"], params=body.get("params", {}),
            domain=body.get("domain"), context=body.get("context"),
            age_range=body.get("age_range"), modality=body.get("modality"),
            author=body.get("author"))
    except (KeyError, ValueError) as exc:
        return _json({"ok": False, "error": str(exc)}, 400)
    return _json({"ok": True, "component_id": cid})


@route("POST", "/api/evaluate")
def api_evaluate(p: Platform, m, q, body) -> Response:
    try:
        eid = p.evaluate(
            scores={k: float(v) for k, v in body.get("scores", {}).items()},
            origin=body.get("origin", "auto"),
            prototype_id=body.get("prototype_id"),
            evaluator=body.get("evaluator"),
            bloom_level=body.get("bloom_level"),
            domain=body.get("domain"),
            components_used=body.get("components_used"),
            comments=body.get("comments", ""))
    except ValueError as exc:
        return _json({"ok": False, "error": str(exc)}, 400)
    return _json({"ok": True, "evaluation_id": eid})


@route("GET", "/api/report")
def api_report(p: Platform, m, q, body) -> Response:
    if _first(q, "format") == "csv":
        return (200, "text/csv; charset=utf-8", p.evaluations.export_csv().encode("utf-8"))
    return _json(p.comparison_report())


# --------------------------------------------------------------------------- #
def _first(q: Dict[str, List[str]], key: str) -> Optional[str]:
    vals = q.get(key)
    return vals[0] if vals else None


class Handler(BaseHTTPRequestHandler):
    platform: Optional[Platform] = None
    server_version = "EndoDSL/1.0"

    def log_message(self, fmt, *args):  # silencia logs ruidosos
        pass

    def _send(self, resp: Response) -> None:
        status, ctype, body = resp
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path: str) -> bool:
        rel = path[len("/static/"):]
        fpath = (_STATIC / rel).resolve()
        if not str(fpath).startswith(str(_STATIC.resolve())) or not fpath.is_file():
            return False
        ctype = mimetypes.guess_type(str(fpath))[0] or "application/octet-stream"
        self._send((200, ctype, fpath.read_bytes()))
        return True

    def _handle(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if method == "GET" and path.startswith("/static/"):
            if not self._static(path):
                self._send(_html(views.not_found("Arquivo não encontrado"), 404))
            return
        body: Dict[str, Any] = {}
        if method == "POST":
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            if raw:
                try:
                    body = json.loads(raw.decode("utf-8"))
                except ValueError:
                    body = {k: v[0] for k, v in parse_qs(raw.decode("utf-8")).items()}
        handler, params = router.match(method, path)
        if handler is None:
            self._send(_html(views.not_found(f"Rota não encontrada: {path}"), 404))
            return
        try:
            query = parse_qs(parsed.query)
            self._send(handler(self.platform, params, query, body))
        except Exception as exc:  # erro inesperado -> 500 com traço (uso local)
            tb = traceback.format_exc()
            if path.startswith("/api/"):
                self._send(_json({"ok": False, "error": str(exc), "trace": tb}, 500))
            else:
                self._send(_html(views.error_page(str(exc), tb), 500))

    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")


def make_server(host: str = "127.0.0.1", port: int = 8000,
                db_path: Optional[str] = None) -> HTTPServer:
    Handler.platform = Platform(db_path)
    return HTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8000,
          db_path: Optional[str] = None) -> None:
    httpd = make_server(host, port, db_path)
    print(f"Endo-DSL — interface web em http://{host}:{port}")
    print(f"  backend LLM: {Handler.platform.backend.name}  ·  "
          f"banco: {Handler.platform.db.path}")
    print("  Ctrl+C para encerrar.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando…")
        httpd.server_close()
