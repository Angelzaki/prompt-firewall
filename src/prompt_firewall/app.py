from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from prompt_firewall.rules import inspect

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))
app = FastAPI(title="prompt-firewall")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return TEMPLATES.TemplateResponse("index.html", {"request": request, "verdict": None, "text": ""})


@app.post("/check", response_class=HTMLResponse)
def check(request: Request, text: str = Form(...)):
    verdict = inspect(text)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "verdict": verdict, "text": text},
    )


@app.post("/api/check")
def api_check(payload: dict):
    verdict = inspect(payload.get("text", ""))
    return {
        "allowed": verdict.allowed,
        "score": verdict.score,
        "matched": verdict.matched,
        "reason": verdict.reason,
    }
