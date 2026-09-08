from scoring import normalize, score_tender


def test_strong_relevant_tender_is_matching():
    result = score_tender({"title": "Python Serious Game", "description": "Unity Webanwendung mit API", "status": "aktiv"})
    assert result["classification"] == "PASSEND"
    assert result["score"] >= 28


def test_inactive_status_overrides_positive_score():
    result = score_tender({"title": "Python VR Serious Game", "description": "Unity API", "status": "bereits vergeben"})
    assert result["classification"] == "NICHT_AKTIV"


def test_hardware_false_positive_is_reduced():
    result = score_tender({"title": "Lieferung Hardware", "description": "Hardwarelieferung von Arbeitsplatz-PC und Drucker", "status": "aktiv"})
    assert result["classification"] == "NICHT_PASSEND"
    assert result["score"] < 0


def test_normalization_handles_umlauts_and_punctuation():
    assert normalize("ÜBER–Prüfung!") == " uber prufung "


def test_real_zero_is_preserved_in_result():
    result = score_tender({"title": "Unbekannt", "description": "", "budget": 0})
    assert result["budget"] == 0
