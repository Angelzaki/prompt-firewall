from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from prompt_firewall.rules import inspect


def load_rows(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def run_batch(rows: list[dict]) -> dict:
    """Evalúa cada fila y devuelve métricas agregadas y detalle por muestra."""
    detail = []
    rules = Counter()
    tp = fp = fn = tn = 0
    for row in rows:
        v = inspect(row["text"])
        expected = bool(row.get("expect_block", False))
        blocked = not v.allowed
        if blocked and expected:
            tp += 1
        elif blocked and not expected:
            fp += 1
        elif not blocked and expected:
            fn += 1
        else:
            tn += 1
        rules.update(v.matched)
        detail.append(
            {
                "id": row["id"],
                "category": row.get("category", "-"),
                "expect_block": expected,
                "blocked": blocked,
                "ok": blocked == expected,
                "matched": v.matched,
                "score": v.score,
            }
        )
    total = len(rows)
    blocked_total = tp + fp
    precision = tp / blocked_total if blocked_total else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "total": total,
        "allowed": total - blocked_total,
        "blocked": blocked_total,
        "allow_rate": round((total - blocked_total) / total, 4) if total else 0.0,
        "block_rate": round(blocked_total / total, 4) if total else 0.0,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "accuracy": round((tp + tn) / total, 4) if total else 0.0,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "top_rules": rules.most_common(),
        "detail": detail,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Reporte batch · prompt-firewall",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        f"| Muestras | {report['total']} |",
        f"| Permitidas | {report['allowed']} ({report['allow_rate']:.1%}) |",
        f"| Bloqueadas | {report['blocked']} ({report['block_rate']:.1%}) |",
        f"| Accuracy | {report['accuracy']:.1%} |",
        f"| Precision | {report['precision']:.1%} |",
        f"| Recall | {report['recall']:.1%} |",
        f"| TP / FP / FN / TN | {report['tp']} / {report['fp']} / {report['fn']} / {report['tn']} |",
        "",
        "## Reglas más disparadas",
        "",
        "| Regla | Disparos |",
        "|---|---:|",
    ]
    for name, n in report["top_rules"]:
        lines.append(f"| `{name}` | {n} |")
    lines += ["", "## Discrepancias", "", "| id | categoría | esperado | resultado | reglas |", "|---|---|---|---|---|"]
    for d in report["detail"]:
        if not d["ok"]:
            exp = "block" if d["expect_block"] else "allow"
            got = "block" if d["blocked"] else "allow"
            lines.append(f"| {d['id']} | {d['category']} | {exp} | {got} | {', '.join(d['matched']) or '-'} |")
    return "\n".join(lines) + "\n"


def save_report(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "batch_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "batch_report.md").write_text(render_markdown(report), encoding="utf-8")
