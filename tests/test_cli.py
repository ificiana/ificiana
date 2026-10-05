from metrics.cli import main


def test_main_writes_svg(tmp_path):
    out = tmp_path / "m.svg"
    profile = {"login": "u", "name": "n", "bio": "", "followers": 0, "following": 0,
               "repos": 0, "stars": 0, "languages": [], "dots": []}
    main(["u", str(out)], get=lambda p: None, collector=lambda user, get, authed: profile)
    assert out.read_text().startswith("<svg")


def test_main_passes_authed_flag_from_env(tmp_path, monkeypatch):
    seen = []
    profile = {"login": "u", "name": "n", "bio": "", "followers": 0, "following": 0,
               "repos": 0, "stars": 0, "languages": [], "dots": []}
    for token in ("t", None):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        if token:
            monkeypatch.setenv("GITHUB_TOKEN", token)
        main(["u", str(tmp_path / "m.svg")], get=lambda p: None,
             collector=lambda user, get, authed: seen.append(authed) or profile)
    assert seen == [True, False]
