from __future__ import annotations

import base64
import binascii
import re
import unicodedata
from dataclasses import dataclass

_LEET = str.maketrans({"1": "i", "0": "o", "@": "a", "3": "e", "$": "s"})
_INVISIBLE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_B64_TOKEN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")


def normalize(text: str) -> str:
    """Forma canónica para el matching: sin acentos, minúsculas, leetspeak básico y espacios colapsados."""
    text = _INVISIBLE.sub("", text or "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("'", "").replace("\u2019", "")
    text = text.translate(_LEET)
    return re.sub(r"\s+", " ", text).strip()


_VERB_IGNORE = r"(ignore|disregard|forget|override|ignora|ignorar|olvida|olvidate de|omite|descarta|desestima)"
_PREV = r"(previous|prior|above|earlier|preceding|anteriores|previas|previos|de arriba)"
_INSTR = r"(instructions?|rules|prompts?|directions|guidelines|instrucciones|reglas|ordenes|indicaciones|directrices)"
_REVEAL = r"(reveal|show|print|display|repeat|dump|leak|tell me|give me|muestra|muestrame|revela|imprime|dime|dame|repite|filtra)"
_SECRET_PROMPT = (
    r"(system prompt|hidden prompt|initial prompt|prompt (de|del) sistema|prompt oculto|"
    r"(hidden|secret|internal|initial) (configuration|instructions|rules|prompt)|"
    r"(configuracion|instrucciones|reglas) (oculta|ocultas|internas|del sistema))"
)
_ASSISTANT_CUE = (
    r"(answer|respond|reply|act|behave|operate|mode|assistant|you are|youre|"
    r"responde|contesta|actua|comportate|modo|asistente|eres)"
)
_NO_LIMITS = (
    r"(no|without|sin)\s+(any |ninguna )?"
    r"(restrictions|restriction|filters|censorship|restricciones|filtros|censura)"
)

RULES = [
    (
        "ignore_previous",
        re.compile(
            rf"{_VERB_IGNORE} (all |any |every |todas |todos )?(of )?(the |your |tus |las |los |mis )?"
            rf"{_PREV} {_INSTR}"
            rf"|{_VERB_IGNORE} (everything|all|anything) (that )?(you|i) ?(were|was|have been|had been|ve been|been) "
            r"(told|instructed|given|said)"
            rf"|{_VERB_IGNORE} (todas |todos |todo )?(las |los |tus |mis )?{_INSTR} {_PREV}"
            r"|(ignora|olvida|descarta) todo lo que te (dijeron|han dicho|dije)",
        ),
    ),
    (
        "system_override",
        re.compile(
            r"\b(dan|developer|god|modo dios|modo desarrollador|desarrollador) mode\b|\bmodo (dios|dan|desarrollador)\b|"
            r"\bdo anything now\b|"
            r"\byou are now (dan|an? (unrestricted|unfiltered|uncensored|jailbroken|evil)|no longer|free from|"
            r"in (dan|developer|god) mode)|"
            r"\bact as (an? |the )?(unrestricted|unfiltered|uncensored|jailbroken|evil|dan)\b|"
            r"\bact as if you (have|had|are) (no|without) (rules|restrictions|limits|filters)|"
            r"\bahora eres (dan|un asistente sin|libre de)|\bactua como (dan|un asistente sin|si no tuvieras)",
        ),
    ),
    (
        "reveal_system",
        re.compile(
            rf"{_REVEAL}.{{0,40}}{_SECRET_PROMPT}"
            rf"|(reveal|print|dump|output|revela|imprime|muestra) (your|tu|tus) (full |entire |complete |todo el |todas )?"
            r"(configuration|config|instructions|initial prompt|configuracion|instrucciones)"
            rf"|{_VERB_IGNORE} (the |your |el |tu )?(system prompt|prompt (de|del) sistema)",
        ),
    ),
    (
        "jailbreak",
        re.compile(
            r"bypass (the |all |any )?(safety|content|security|guardrails|filters)"
            r"|(evade|omite|salta|saltate) (los |las |el |la )?(filtros|restricciones|seguridad|guardrails)"
            r"|\bjailbreak (this|the|you|your|yourself|it|me)\b|\bjailbreak and\b|\bjailbreak (mode|prompt) (on|enabled|activated)\b"
            r"|\bhaz(lo)? jailbreak\b|\bjailbreakea\w*"
            rf"|{_ASSISTANT_CUE}.{{0,40}}{_NO_LIMITS}",
        ),
    ),
    (
        "exfil",
        re.compile(
            r"exfiltrat|\bexfiltra\b|leak (the |all |your )?(secrets|credentials)|filtra (los |las |tus )?(secretos|credenciales)"
            r"|(print|reveal|dump|leak|revela|imprime|filtra).{0,30}(api[_ ]?keys?|secret keys?|private keys?|credentials|credenciales)"
            r"|(show|give|tell|muestra|dame|dime) (me )?(your|tu|tus) .{0,15}(api[_ ]?keys?|secret keys?|password|clave|credenciales)",
        ),
    ),
    (
        "role_swap",
        re.compile(
            r"forget (you are|your role|your rules|everything you know)|do not follow your rules|dont follow your rules"
            r"|olvida (tu rol|quien eres|tus reglas)|no sigas tus reglas|ignora tu rol"
            r"|pretend (that )?(the |your |all )?(rules|restrictions|guidelines|limits) (do not|dont|no longer) apply"
            r"|(finge|pretende|simula) que (no tienes|las reglas no|no hay) (reglas|restricciones|aplican|limites)",
        ),
    ),
]


@dataclass
class Verdict:
    allowed: bool
    score: float
    matched: list[str]
    reason: str


def _decode_base64_payloads(text: str) -> list[str]:
    decoded = []
    for token in _B64_TOKEN.findall(text):
        padded = token + "=" * (-len(token) % 4)
        try:
            raw = base64.b64decode(padded, validate=True)
            candidate = raw.decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
        if candidate and all(c.isprintable() or c.isspace() for c in candidate):
            decoded.append(candidate)
    return decoded


def _match(text: str) -> list[str]:
    norm = normalize(text)
    return [name for name, pattern in RULES if pattern.search(norm)]


def inspect(text: str) -> Verdict:
    text = text or ""
    matched = _match(text)
    for payload in _decode_base64_payloads(text):
        inner = _match(payload)
        if inner:
            matched += [r for r in inner if r not in matched]
            if "encoded_payload" not in matched:
                matched.append("encoded_payload")
    if not matched:
        return Verdict(True, 1.0, [], "ok")
    score = max(0.0, 1.0 - 0.25 * len(matched))
    return Verdict(False, round(score, 2), matched, "blocked_by_rules")
