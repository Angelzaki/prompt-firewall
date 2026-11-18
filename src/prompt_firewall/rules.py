from __future__ import annotations

import re
from dataclasses import dataclass

RULES = [
    ("ignore_previous", re.compile(r"ignore (all |any )?(previous|prior|above) instructions", re.I)),
    ("system_override", re.compile(r"(you are now|act as|dan mode|developer mode)", re.I)),
    ("reveal_system", re.compile(r"(reveal|show|print).*(system prompt|hidden prompt)", re.I)),
    ("jailbreak", re.compile(r"(jailbreak|bypass (the )?safety|no restrictions)", re.I)),
    ("exfil", re.compile(r"(exfiltrat|leak secrets|api[_ ]?key)", re.I)),
    ("role_swap", re.compile(r"forget (you are|your role)|do not follow your rules", re.I)),
]


@dataclass
class Verdict:
    allowed: bool
    score: float
    matched: list[str]
    reason: str


def inspect(text: str) -> Verdict:
    matched = [name for name, pattern in RULES if pattern.search(text or "")]
    if not matched:
        return Verdict(True, 1.0, [], "ok")
    score = max(0.0, 1.0 - 0.25 * len(matched))
    return Verdict(False, round(score, 2), matched, "blocked_by_rules")
