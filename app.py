from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from scoring import score_tender


ROOT = Path(__file__).parent

st.set_page_config(page_title="Tender Radar", page_icon="📡", layout="wide")


def load_demo_data() -> list[dict]:
    with (ROOT / "data" / "demo_tenders.json").open(encoding="utf-8") as handle:
        return [score_tender(item) for item in json.load(handle)]


def show_value(label: str, value: object) -> None:
    # Missing data is omitted; a real zero remains visible.
    if value is not None and value != "" and value != []:
        st.markdown(f"<span class='field-label'>{label}</span><br>{value}", unsafe_allow_html=True)


def render_card(tender: dict) -> None:
    status = tender["classification"]
    status_label = {
        "PASSEND": "Passend",
        "MANUELL_PRUEFEN": "Manuell prüfen",
        "NICHT_AKTIV": "Nicht aktiv",
        "NICHT_PASSEND": "Nicht passend",
    }[status]
    with st.container(border=True):
        title_col, score_col = st.columns([5, 1])
        with title_col:
            st.markdown(f"<div class='eyebrow'>{tender['category']}</div>", unsafe_allow_html=True)
            st.subheader(tender["title"])
            st.markdown(f"<span class='status status-{status.lower()}'>{status_label}</span>", unsafe_allow_html=True)
        with score_col:
            st.metric("Relevanz", f"{tender['score']} Pkt.")

        first, second, third = st.columns(3)
        with first:
            show_value("Auftraggeber", tender.get("organization"))
        with second:
            show_value("Ort", tender.get("location"))
        with third:
            show_value("Frist", tender.get("deadline"))

        st.write(tender["description"])
        with st.expander("Bewertung nachvollziehen"):
            for reason in tender["reasons"]:
                st.write(f"• {reason}")
        if tender.get("url"):
            st.link_button("Ausschreibung öffnen", tender["url"], use_container_width=True)


def main() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#0b1739; --blue:#3267e3; --mint:#33d1a0; --muted:#697386; }
        .stApp { background:linear-gradient(180deg,#f5f8ff 0,#ffffff 26rem); }
        .block-container { max-width:1220px; padding-top:2.2rem; }
        .brand { display:flex; align-items:center; gap:.8rem; color:var(--navy); font-weight:800; letter-spacing:-.03em; font-size:1.15rem; }
        .brand-mark { display:grid; place-items:center; width:2.4rem; height:2.4rem; border-radius:.8rem; color:white; background:linear-gradient(135deg,var(--blue),#7654db); box-shadow:0 8px 24px #3267e342; }
        .hero { padding:3.3rem 0 2.2rem; }
        .hero h1 { color:var(--navy); font-size:clamp(2.5rem,6vw,4.8rem); line-height:.98; max-width:850px; letter-spacing:-.055em; margin:.45rem 0 1rem; }
        .hero p { max-width:720px; color:var(--muted); font-size:1.1rem; line-height:1.65; }
        .kicker,.eyebrow { color:var(--blue); text-transform:uppercase; letter-spacing:.12em; font-size:.74rem; font-weight:800; }
        .status { display:inline-block; margin:.1rem 0 1rem; padding:.28rem .65rem; border-radius:2rem; font-size:.78rem; font-weight:750; }
        .status-passend { color:#087255; background:#d9f8ec; }
        .status-manuell_pruefen { color:#8a5500; background:#fff1cd; }
        .status-nicht_aktiv { color:#576071; background:#e8ebf0; }
        .status-nicht_passend { color:#a52a35; background:#ffe3e6; }
        .field-label { color:var(--muted); font-size:.76rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
        [data-testid='stMetric'] { background:white; border:1px solid #e5eaf3; padding:1rem; border-radius:1rem; box-shadow:0 8px 30px #1627550a; }
        [data-testid='stVerticalBlockBorderWrapper'] { background:#fff; border-color:#e4e9f2!important; border-radius:1.2rem!important; box-shadow:0 12px 36px #10204a0a; }
        </style>
        <div class='brand'><span class='brand-mark'>TR</span>Tender Radar</div>
        <section class='hero'>
          <div class='kicker'>Ausschreibungen. Klar priorisiert.</div>
          <h1>Aus Daten werden Entscheidungen.</h1>
          <p>Eine Python-Anwendung, die öffentliche IT-Ausschreibungen strukturiert,
          transparent bewertet und die wichtigsten Chancen in einem fokussierten Dashboard bündelt.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    tenders = load_demo_data()
    total = len(tenders)
    matching = sum(t["classification"] == "PASSEND" for t in tenders)
    manual = sum(t["classification"] == "MANUELL_PRUEFEN" for t in tenders)
    avg_score = round(sum(t["score"] for t in tenders) / total)
    metrics = st.columns(4)
    for column, label, value in zip(metrics, ["Analysiert", "Passend", "Zu prüfen", "Ø Score"], [total, matching, manual, avg_score]):
        column.metric(label, value)

    st.markdown("### Ausschreibungsübersicht")
    filter_col, search_col, sort_col = st.columns([1.2, 2.2, 1.2])
    with filter_col:
        selected = st.selectbox("Status", ["Alle", "Passend", "Manuell prüfen", "Nicht aktiv", "Nicht passend"])
    with search_col:
        query = st.text_input("Suche", placeholder="Titel, Auftraggeber oder Technologie …")
    with sort_col:
        sort_order = st.selectbox("Sortierung", ["Score absteigend", "Frist", "Titel A–Z"])

    status_map = {"Passend": "PASSEND", "Manuell prüfen": "MANUELL_PRUEFEN", "Nicht aktiv": "NICHT_AKTIV", "Nicht passend": "NICHT_PASSEND"}
    filtered = [t for t in tenders if selected == "Alle" or t["classification"] == status_map[selected]]
    if query.strip():
        needle = query.casefold().strip()
        filtered = [t for t in filtered if needle in " ".join(str(t.get(k, "")) for k in ("title", "organization", "description", "category", "location")).casefold()]
    if sort_order == "Score absteigend":
        filtered.sort(key=lambda item: item["score"], reverse=True)
    elif sort_order == "Titel A–Z":
        filtered.sort(key=lambda item: item["title"].casefold())
    else:
        filtered.sort(key=lambda item: item.get("deadline") or "9999")

    st.caption(f"{len(filtered)} von {total} Ergebnissen")
    if not filtered:
        st.info("Keine Ausschreibungen entsprechen den gewählten Filtern.")
    for tender in filtered:
        render_card(tender)

    st.markdown("---")
    st.caption("Portfolio-Demo · Python · Streamlit · regelbasiertes Scoring · synthetische Beispieldaten")


if __name__ == "__main__":
    main()
