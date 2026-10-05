import re

from metrics.render import render

DOTS = [
    {"seed": 11, "language": "Python", "size": 400},
    {"seed": 5000, "language": "Python", "size": 40},
    {"seed": 90000, "language": "Go", "size": 100},
    {"seed": 123456, "language": None, "size": 0},
    {"seed": 777777, "language": "Obscure", "size": 5},
]
PROFILE = {
    "login": "u", "name": "A & B", "bio": "<bio>", "followers": 3, "following": 1,
    "repos": 5, "stars": 7,
    "languages": [("Python", 150), ("Shell", 50)],
    "dots": DOTS,
}


def test_render_is_escaped_svg():
    svg = render(PROFILE)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert "A &amp; B" in svg and "&lt;bio&gt;" in svg
    assert "<bio>" not in svg


def test_render_shows_language_percentages_and_stats():
    svg = render(PROFILE)
    assert "75.0%" in svg and "25.0%" in svg and "Python" in svg
    assert "3 followers" in svg and "5 repos" in svg and "★ 7" in svg


def test_render_draws_one_star_per_repo_and_is_animated():
    svg = render(PROFILE)
    assert svg.count('class="repo"') == len(DOTS)
    assert "@keyframes twinkle" in svg and "@keyframes shoot" in svg


def test_render_connects_same_language_repos_only():
    svg = render(PROFILE)
    assert svg.count('class="link"') == 1


def test_render_is_deterministic_and_seed_dependent():
    assert render(PROFILE) == render(PROFILE)
    assert render({**PROFILE, "login": "other"}) != render(PROFILE)


def test_render_is_a_valid_xml_tree():
    import xml.etree.ElementTree as ET
    ET.fromstring(render(PROFILE))


def test_render_without_languages_dots_or_bio():
    svg = render({**PROFILE, "languages": [], "dots": [], "bio": ""})
    assert "<svg" in svg and 'class="repo"' not in svg


def test_render_wraps_many_languages_in_legend():
    langs = [(f"L{i}", 10) for i in range(9)]
    svg = render({**PROFILE, "languages": langs})
    assert len(re.findall(r"L\d \d+\.\d%", svg)) == 8


def test_render_includes_scene_and_grows_canvas():
    svg = render(PROFILE)
    assert 'height="840"' in svg and "TOKYO" not in svg and "@keyframes win" in svg


def test_render_ids_are_unique():
    ids = re.findall(r'id="([^"]+)"', render(PROFILE))
    assert len(ids) == len(set(ids))
