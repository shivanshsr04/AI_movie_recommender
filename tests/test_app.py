from pathlib import Path
import tomllib
from streamlit.testing.v1 import AppTest
from train_models import train

ROOT = Path(__file__).resolve().parents[1]


def test_guest_recommendations_search_and_analytics(tmp_path, monkeypatch):
    monkeypatch.setenv('MOVIE_MODEL_DIR', str(tmp_path))
    app = AppTest.from_file(str(ROOT / 'streamlit_app.py'), default_timeout=20).run()
    assert not app.exception
    assert 'Demo mode' in app.info[0].value
    app.button[0].click().run()
    assert not app.exception
    assert any('The Last Starship' in block.value for block in app.markdown)
    app.sidebar.radio[0].set_value('Search').run()
    app.text_input[0].set_value('[').run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 0
    app.sidebar.radio[0].set_value('Analytics').run()
    assert not app.exception
    app.sidebar.radio[0].set_value('About').run()
    assert not app.exception
    tomllib.loads((ROOT / '.streamlit/config.toml').read_text())


def test_trained_catalog_loads_in_app(tmp_path, monkeypatch):
    train(demo=True, output_dir=tmp_path)
    monkeypatch.setenv('MOVIE_MODEL_DIR', str(tmp_path))
    app = AppTest.from_file(str(ROOT / 'streamlit_app.py'), default_timeout=20).run()
    app.button[0].click().run()
    assert not app.exception
    assert any('Cosine similarity' in block.value for block in app.markdown)
