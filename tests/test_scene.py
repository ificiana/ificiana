import re
import xml.etree.ElementTree as ET

import pytest

from metrics.scene import LANTERNS, SCENE_H, SCENE_STYLE, scene

DOTS = [
    {"seed": 11, "language": "Python", "size": 400},
    {"seed": 5000, "language": "Python", "size": 40},
    {"seed": 90000, "language": "Go", "size": 100},
    {"seed": 123456, "language": None, "size": 0},
    {"seed": 777777, "language": "Obscure", "size": 5},
]
STATS = {"followers": 3, "repos": 5, "stars": 7}


def build(login="u", dots=DOTS, stats=STATS):
    return scene(login, dots, stats)


def test_scene_is_valid_xml():
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{build()}</svg>')


def test_scene_height_is_positive():
    assert SCENE_H > 300


def test_each_repo_lights_exactly_one_window():
    assert build().count('class="win"') == len(DOTS)
    assert build(dots=[]).count('class="win"') == 0


def test_scene_has_festival_elements():
    s = build()
    assert "petal" not in s
    assert s.count('class="lantern"') == LANTERNS
    assert 'class="neon"' not in s
    assert "torii" not in s and "mascot" not in s


def test_scene_has_japanese_text_and_stats():
    s = build()
    for text in ("フォロワー 3", "リポジトリ 5", "★ 7"):
        assert text in s
    for banner in ("酒", "湯", "夜桜祭り", "東京", "TOKYO", "FESTIVAL", "こんにちは"):
        assert banner not in s


def test_scene_is_deterministic_and_login_dependent():
    assert build() == build()
    assert build("other") != build()


def test_scene_ids_are_unique_and_prefixed():
    ids = re.findall(r'id="([^"]+)"', build())
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("name", ["win", "drift", "sway"])
def test_scene_style_defines_animations(name):
    assert f"@keyframes {name}" in SCENE_STYLE
