import pandas as pd
import wos_geo


def test_analyze_articles_batch_output_format():
    articles = ["article one", "article two"]
    df = wos_geo.analyze_articles_batch(articles)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["article", "summary"]
    assert df.shape[0] == len(articles)


def test_geocode_locations_cache(monkeypatch):
    calls = []

    def fake_geocode(loc):
        calls.append(loc)
        return {"lat": 1.0, "lng": 2.0}

    monkeypatch.setattr(wos_geo, "_geocode_location", fake_geocode)
    wos_geo._GEOCODE_CACHE.clear()

    df = wos_geo.geocode_locations(["Paris", "Paris"])
    assert df.shape[0] == 2
    assert len(calls) == 1


def test_analyze_articles_to_excel(tmp_path):
    articles = ["foo", "bar"]
    out_file = tmp_path / "out.xlsx"
    path = wos_geo.analyze_articles_to_excel(articles, str(out_file))
    assert path == str(out_file)
    assert out_file.exists()

