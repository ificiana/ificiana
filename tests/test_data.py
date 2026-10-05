from metrics.data import collect, aggregate_languages

USER = {"login": "u", "name": "U Ser", "bio": "hi", "followers": 3, "following": 1, "public_repos": 2}
REPOS = [
    {"name": "a", "fork": False, "stargazers_count": 5, "pushed_at": "2026-01-02T00:00:00Z", "description": "da", "language": "Python"},
    {"name": "f", "fork": True, "stargazers_count": 99, "pushed_at": "2026-01-03T00:00:00Z", "description": None, "language": "C"},
    {"name": "b", "fork": False, "stargazers_count": 2, "pushed_at": "2026-01-01T00:00:00Z", "description": None, "language": None},
]
LANGS = {"a": {"Python": 100, "Shell": 20}, "b": {"Python": 50}}


def fake_get(path):
    if path == "/users/u":
        return USER
    if path.startswith("/users/u/repos"):
        return REPOS
    return LANGS[path.split("/")[3]]


def test_aggregate_languages_sums_and_sorts():
    assert aggregate_languages([{"X": 1, "Y": 5}, {"X": 6}]) == [("X", 7), ("Y", 5)]


def test_collect_filters_forks_and_builds_profile():
    p = collect("u", fake_get)
    assert p["name"] == "U Ser"
    assert [r["name"] for r in p["recent"]] == ["a", "b"]
    assert p["stars"] == 7
    assert p["languages"] == [("Python", 150), ("Shell", 20)]
    assert p["followers"] == 3 and p["repos"] == 2 and p["bio"] == "hi"


def test_collect_falls_back_to_login_and_empty_bio():
    user = {**USER, "name": None, "bio": None}
    get = lambda path: user if path == "/users/u" else fake_get(path)
    p = collect("u", get)
    assert p["name"] == "u" and p["bio"] == ""
