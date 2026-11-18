import pytest

from pipeline import linkgist


@pytest.fixture(autouse=True)
def no_live_gist(tmp_path, monkeypatch):
    monkeypatch.setattr(linkgist, "TOKENFILE", tmp_path / "no_gist_token.json")
    monkeypatch.setattr(linkgist, "STATE", tmp_path / "gist_state.json")
