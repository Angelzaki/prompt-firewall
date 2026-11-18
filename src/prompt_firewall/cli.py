from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn
from rich.console import Console

from prompt_firewall.rules import inspect

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prompt-firewall")
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check")
    check.add_argument("text")
    batch = sub.add_parser("batch")
    batch.add_argument("--file", default="samples/attacks.jsonl")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8011)
    args = parser.parse_args(argv)

    if args.cmd == "check":
        v = inspect(args.text)
        print(json.dumps(v.__dict__, ensure_ascii=False, indent=2))
        return 0 if v.allowed else 1

    if args.cmd == "batch":
        path = Path(args.file)
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        ok = 0
        for row in rows:
            v = inspect(row["text"])
            expected_block = row.get("expect_block", False)
            hit = (not v.allowed) == expected_block
            ok += int(hit)
            console.print(f"{row['id']}: {'PASS' if hit else 'FAIL'} matched={v.matched}")
        console.print(f"score={ok}/{len(rows)}")
        return 0 if ok == len(rows) else 1

    if args.cmd == "serve":
        uvicorn.run("prompt_firewall.app:app", host="127.0.0.1", port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
