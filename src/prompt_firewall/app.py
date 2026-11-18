from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from prompt_firewall.batch import load_rows
from prompt_firewall.rules import RULES, inspect
from prompt_firewall.stats import Stats

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "samples" / "attacks.jsonl"
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))
app = FastAPI(title="prompt-firewall")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
STATS = Stats()


def _render(request: Request, verdict=None, text: str = ""):
    ctx = {
        "request": request,
        "verdict": verdict,
        "text": text,
        "stats": STATS.snapshot(),
        "rule_count": len(RULES),
    }
    return TEMPLATES.TemplateResponse(request, "index.html", ctx)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _render(request)


@app.post("/check", response_class=HTMLResponse)
def check(request: Request, text: str = Form(...)):
    verdict = inspect(text)
    STATS.record(text, verdict)
    return _render(request, verdict, text)


@app.post("/samples")
def run_samples():
    for row in load_rows(SAMPLES):
        STATS.record(row["text"], inspect(row["text"]))
    return RedirectResponse("/", status_code=303)


@app.post("/reset")
def reset():
    STATS.reset()
    return RedirectResponse("/", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def api_stats():
    return STATS.snapshot()


@app.post("/api/check")
def api_check(payload: dict):
    text = payload.get("text", "")
    verdict = inspect(text)
    STATS.record(text, verdict)
    return {
        "allowed": verdict.allowed,
        "score": verdict.score,
        "matched": verdict.matched,
        "reason": verdict.reason,
    }
