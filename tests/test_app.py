from streamlit.testing.v1 import AppTest
from pathlib import Path


APP_PATH = Path(__file__).parents[1] / "app.py"


def load_app() -> AppTest:
    app = AppTest.from_file(APP_PATH)
    return app.run(timeout=20)


def test_dashboard_renders_without_exceptions():
    app = load_app()
    assert not app.exception
    assert [metric.value for metric in app.metric[:4]] == ["8", "2", "3", "9"]
    assert len(app.subheader) == 8


def test_status_filter_reduces_result_cards():
    app = load_app()
    app.selectbox[0].set_value("Passend").run(timeout=20)
    assert not app.exception
    assert len(app.subheader) == 2


def test_search_finds_python_tender():
    app = load_app()
    app.text_input[0].set_value("Python").run(timeout=20)
    assert not app.exception
    titles = [heading.value for heading in app.subheader]
    assert "Automatisierte Analyse öffentlicher Daten" in titles
