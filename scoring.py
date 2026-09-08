from __future__ import annotations

import re
import unicodedata


POSITIVE = {
    "Game-/Serious-Game-Entwicklung": (20, ("game", "spielentwicklung", "serious game", "unity", "godot")),
    "AR/VR/XR": (20, ("virtual reality", "augmented reality", " vr ", " xr ")),
    "Python und Automatisierung": (14, ("python", "automatisierung", "web scraping", "datenanalyse")),
    "Web und APIs": (10, ("webanwendung", "api", "schnittstelle", "dashboard")),
}
NEGATIVE = {
    "Hardware-/Lieferleistung": (-18, ("hardwarelieferung", "drucker", "toner", "arbeitsplatz-pc")),
    "Reiner Betrieb/Hosting": (-12, ("reiner betrieb", "rechenzentrumsbetrieb", "hosting only")),
}
INACTIVE = ("vergeben", "aufgehoben", "abgeschlossen")


def normalize(value: object) -> str:
    # Replace punctuation before ASCII folding so characters such as an en dash
    # remain word boundaries instead of joining two terms.
    text = re.sub(r"[^\w]+", " ", str(value or ""), flags=re.UNICODE)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return " " + re.sub(r"[^a-z0-9]+", " ", text).strip() + " "


def score_tender(tender: dict) -> dict:
    result = tender.copy()
    text = normalize(" ".join(str(result.get(key, "")) for key in ("title", "description", "category", "organization", "status")))
    score = 0
    reasons: list[str] = []
    positive_hits = 0

    for name, (weight, variants) in POSITIVE.items():
        if any(normalize(variant).strip() in text for variant in variants):
            score += weight
            positive_hits += 1
            reasons.append(f"+{weight}: {name}")
    for name, (weight, variants) in NEGATIVE.items():
        if any(normalize(variant).strip() in text for variant in variants):
            score += weight
            reasons.append(f"{weight}: {name}")

    if any(marker in text for marker in INACTIVE):
        classification = "NICHT_AKTIV"
        reasons.insert(0, "Status: nicht mehr aktiv")
    elif score >= 28 and positive_hits >= 2:
        classification = "PASSEND"
    elif score >= 10:
        classification = "MANUELL_PRUEFEN"
    else:
        classification = "NICHT_PASSEND"

    result.update(score=score, classification=classification, reasons=reasons or ["Keine relevanten Kriterien erkannt"])
    return result
