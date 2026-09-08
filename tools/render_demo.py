"""Render a compact, deterministic portfolio walkthrough from the demo dataset."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scoring import score_tender


ROOT = Path(__file__).parents[1]
OUT = ROOT / "assets" / "demo"
SIZE = (1280, 720)
NAVY, BLUE, MINT = "#0b1739", "#3267e3", "#33d1a0"
INK, MUTED, LINE, BG = "#15213b", "#697386", "#e4e9f2", "#f5f8ff"


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)


def base(step: str, title: str, subtitle: str):
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    rounded(draw, (52, 34, 104, 86), 14, BLUE)
    draw.text((68, 49), "TR", font=font(18, True), fill="white")
    draw.text((120, 47), "TENDER RADAR", font=font(22, True), fill=NAVY)
    draw.text((1075, 52), step, font=font(15, True), fill=BLUE)
    draw.text((52, 119), title, font=font(43, True), fill=NAVY)
    draw.text((54, 176), subtitle, font=font(19), fill=MUTED)
    return image, draw


def metric(draw, x, label, value):
    rounded(draw, (x, 228, x + 255, 324), 18, "white", LINE)
    draw.text((x + 20, 247), label.upper(), font=font(13, True), fill=MUTED)
    draw.text((x + 20, 276), str(value), font=font(28, True), fill=INK)


def card(draw, y, item, compact=False):
    rounded(draw, (52, y, 1228, y + (104 if compact else 144)), 18, "white", LINE)
    color = {"PASSEND": MINT, "MANUELL_PRUEFEN": "#f5b942", "NICHT_AKTIV": "#8a93a4", "NICHT_PASSEND": "#e76872"}[item["classification"]]
    rounded(draw, (73, y + 22, 87, y + 82), 7, color)
    draw.text((106, y + 20), item["category"].upper(), font=font(12, True), fill=BLUE)
    draw.text((106, y + 44), item["title"], font=font(22, True), fill=INK)
    draw.text((106, y + 78), f"{item['organization']}  ·  {item.get('location') or '—'}  ·  Frist {item.get('deadline') or '—'}", font=font(14), fill=MUTED)
    draw.text((1090, y + 25), f"{item['score']} Pkt.", font=font(21, True), fill=INK)
    if not compact:
        reason = item["reasons"][0]
        draw.text((106, y + 108), f"Bewertung: {reason}", font=font(14), fill=color)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = json.loads((ROOT / "data" / "demo_tenders.json").read_text(encoding="utf-8"))
    items = sorted((score_tender(x) for x in raw), key=lambda x: x["score"], reverse=True)
    scenes = []

    image, draw = base("01 / 04", "Aus Daten werden Entscheidungen.", "Öffentliche IT-Ausschreibungen strukturiert bewerten und schneller priorisieren.")
    for x, label, value in zip((52, 344, 636, 928), ("Analysiert", "Passend", "Zu prüfen", "Ø Score"), (8, 2, 3, 9)):
        metric(draw, x, label, value)
    draw.text((52, 382), "Ein fokussiertes Dashboard statt manueller Tabellenarbeit.", font=font(25, True), fill=NAVY)
    card(draw, 438, items[0], compact=True)
    card(draw, 558, items[1], compact=True)
    scenes.append(image)

    image, draw = base("02 / 04", "Chancen auf einen Blick.", "Statusfilter und Relevanzscore bringen die stärksten Treffer nach oben.")
    rounded(draw, (52, 225, 1228, 288), 16, "white", LINE)
    draw.text((76, 247), "Status:  Passend", font=font(16, True), fill=INK)
    draw.text((420, 247), "Sortierung:  Score absteigend", font=font(16), fill=MUTED)
    draw.text((960, 247), "2 Ergebnisse", font=font(16, True), fill=BLUE)
    card(draw, 318, items[0])
    card(draw, 482, items[1])
    scenes.append(image)

    python_item = next(x for x in items if x["title"].startswith("Automatisierte"))
    image, draw = base("03 / 04", "Suchen ohne Umwege.", "Titel, Auftraggeber, Ort und Technologien werden gemeinsam durchsucht.")
    rounded(draw, (52, 226, 1228, 298), 18, "white", BLUE, 2)
    draw.text((78, 249), "Python", font=font(19), fill=INK)
    draw.text((1120, 247), "SUCHEN", font=font(14, True), fill=BLUE)
    draw.text((54, 326), "1 von 8 Ergebnissen", font=font(15), fill=MUTED)
    card(draw, 366, python_item)
    rounded(draw, (52, 552, 1228, 655), 18, "#eaf1ff")
    draw.text((78, 573), "Warum dieser Treffer?", font=font(17, True), fill=NAVY)
    draw.text((78, 606), "  •  " + "   •  ".join(python_item["reasons"]), font=font(15), fill=BLUE)
    scenes.append(image)

    image, draw = base("04 / 04", "Nachvollziehbar und getestet.", "Jede Entscheidung bleibt erklärbar – vom Keyword bis zur finalen Klassifikation.")
    checks = ["Regelbasiertes Scoring", "Inaktive Verfahren erkannt", "Fehlende Werte sauber ausgeblendet", "Echte Nullwerte erhalten", "Suche und Filter getestet", "8 automatisierte Tests bestanden"]
    for i, text in enumerate(checks):
        x = 52 + (i % 2) * 590
        y = 235 + (i // 2) * 112
        rounded(draw, (x, y, x + 548, y + 84), 16, "white", LINE)
        rounded(draw, (x + 22, y + 23, x + 60, y + 61), 19, MINT)
        draw.text((x + 34, y + 29), "✓", font=font(18, True), fill="white")
        draw.text((x + 78, y + 29), text, font=font(17, True), fill=INK)
    rounded(draw, (52, 594, 1228, 670), 18, NAVY)
    draw.text((82, 618), "PYTHON  ·  STREAMLIT  ·  JSON  ·  PYTEST  ·  GITHUB ACTIONS", font=font(19, True), fill="white")
    scenes.append(image)

    for index, scene in enumerate(scenes, 1):
        scene.save(OUT / f"scene-{index}.png", optimize=True)


if __name__ == "__main__":
    render()
