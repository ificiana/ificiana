from metrics.render import render

PROFILE = {
    "login": "u", "name": "A & B", "bio": "<bio>", "followers": 3, "following": 1,
    "repos": 2, "stars": 7,
    "languages": [("Python", 150), ("Shell", 50)],
    "recent": [{"name": "a", "description": "da", "language": "Python", "stars": 5},
               {"name": "b", "description": "", "language": None, "stars": 0}],
}


def test_render_is_escaped_svg():
    svg = render(PROFILE)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert "A &amp; B" in svg and "&lt;bio&gt;" in svg
    assert "<bio>" not in svg


def test_render_shows_language_percentages_and_repos():
    svg = render(PROFILE)
    assert "Python" in svg and "75.0%" in svg and "25.0%" in svg
    assert ">a<" in svg and "da" in svg and "★ 5" in svg


def test_render_without_languages_or_repos():
    svg = render({**PROFILE, "languages": [], "recent": [], "bio": ""})
    assert "<svg" in svg
