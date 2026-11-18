from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn
from rich.console import Console

from prompt_firewall.batch import load_rows, run_batch, save_report
from prompt_firewall.rules import inspect

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prompt-firewall")
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check")
    check.add_argument("text")
    batch = sub.add_parser("batch")
    batch.add_argument("--file", default="samples/attacks.jsonl")
    batch.add_argument("--out", default="results")
    batch.add_argument("--fail-under", type=float, default=0.95, help="accuracy mínima para salir con código 0")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8011)
    args = parser.parse_args(argv)

    if args.cmd == "check":
        v = inspect(args.text)
        print(json.dumps(v.__dict__, ensure_ascii=False, indent=2))
        return 0 if v.allowed else 1

    if args.cmd == "batch":
        report = run_batch(load_rows(Path(args.file)))
        for d in report["detail"]:
            console.print(f"{d['id']}: {'PASS' if d['ok'] else 'FAIL'} matched={d['matched']}", markup=False)
        save_report(report, Path(args.out))
        console.print(
            f"total={report['total']} allow={report['allowed']} block={report['blocked']} "
            f"accuracy={report['accuracy']:.1%} precision={report['precision']:.1%} recall={report['recall']:.1%}",
            markup=False,
        )
        console.print("top_rules=" + ", ".join(f"{n}:{c}" for n, c in report["top_rules"]), markup=False)
        return 0 if report["accuracy"] >= args.fail_under else 1

    if args.cmd == "serve":
        uvicorn.run("prompt_firewall.app:app", host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
