from __future__ import annotations

from collections import Counter, deque
from threading import Lock

from prompt_firewall.rules import Verdict


class Stats:
    """Contadores en memoria de las revisiones hechas por el proceso."""

    def __init__(self, history: int = 8) -> None:
        self._lock = Lock()
        self._allowed = 0
        self._blocked = 0
        self._rules: Counter[str] = Counter()
        self._recent: deque[dict] = deque(maxlen=history)

    def record(self, text: str, verdict: Verdict) -> None:
        with self._lock:
            if verdict.allowed:
                self._allowed += 1
            else:
                self._blocked += 1
                self._rules.update(verdict.matched)
            self._recent.appendleft(
                {
                    "allowed": verdict.allowed,
                    "score": verdict.score,
                    "matched": list(verdict.matched),
                    "preview": text.strip().replace("\n", " ")[:80],
                }
            )

    def reset(self) -> None:
        with self._lock:
            self._allowed = 0
            self._blocked = 0
            self._rules.clear()
            self._recent.clear()

    def snapshot(self) -> dict:
        with self._lock:
            total = self._allowed + self._blocked
            top = self._rules.most_common(6)
            peak = top[0][1] if top else 0
            return {
                "total": total,
                "allowed": self._allowed,
                "blocked": self._blocked,
                "allow_rate": round(self._allowed / total, 4) if total else 0.0,
                "block_rate": round(self._blocked / total, 4) if total else 0.0,
                "top_rules": [{"name": n, "count": c, "pct": round(100 * c / peak)} for n, c in top],
                "recent": list(self._recent),
            }
