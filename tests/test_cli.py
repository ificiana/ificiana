from metrics.cli import main


def test_main_writes_svg(tmp_path):
    out = tmp_path / "m.svg"
    profile = {"login": "u", "name": "n", "bio": "", "followers": 0, "following": 0,
               "repos": 0, "stars": 0, "languages": [], "recent": []}
    main(["u", str(out)], get=lambda p: None, collector=lambda user, get: profile)
    assert out.read_text().startswith("<svg")
