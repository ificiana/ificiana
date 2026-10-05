from metrics.data import collect, aggregate_languages

USER = {"login": "u", "name": "U Ser", "bio": "hi", "followers": 3, "following": 1, "public_repos": 2}
REPOS = [
    {"name": "a", "fork": False, "stargazers_count": 5, "pushed_at": "2026-01-02T00:00:00Z", "description": "da", "language": "Python", "size": 400},
    {"name": "f", "fork": True, "stargazers_count": 99, "pushed_at": "2026-01-03T00:00:00Z", "description": None, "language": "C", "size": 10},
    {"name": "b", "fork": False, "stargazers_count": 2, "pushed_at": "2026-01-01T00:00:00Z", "description": None, "language": None, "size": 100},
    {"name": "p", "fork": False, "private": True, "stargazers_count": 1, "pushed_at": "2026-01-04T00:00:00Z", "description": "secret", "language": "Go", "size": 50},
]
LANGS = {"a": {"Python": 100, "Shell": 20}, "b": {"Python": 50}, "p": {"Go": 30}}


def fake_get(path):
    if path.startswith("/search/commits"):
        return {"total_count": 2317}
    if path.startswith("/search/issues"):
        return {"total_count": 203}
    if path == "/users/u":
        return USER
    if path.startswith(("/users/u/repos", "/user/repos")):
        return REPOS
    return LANGS[path.split("/")[3]]


def test_aggregate_languages_sums_and_sorts():
    assert aggregate_languages([{"X": 1, "Y": 5}, {"X": 6}]) == [("X", 7), ("Y", 5)]


def test_collect_filters_forks_and_builds_profile():
    p = collect("u", fake_get)
    assert p["name"] == "U Ser"
    assert "recent" not in p
    assert p["stars"] == 8
    assert p["languages"] == [("Python", 150), ("Go", 30), ("Shell", 20)]
    assert p["followers"] == 3 and p["repos"] == 4 and p["bio"] == "hi"


def test_collect_builds_anonymous_dots_for_own_repos():
    dots = collect("u", fake_get)["dots"]
    assert [d["language"] for d in dots] == ["Python", None, "Go"]
    assert [d["size"] for d in dots] == [400, 100, 50]
    assert all(set(d) == {"seed", "language", "size"} for d in dots)
    assert len({d["seed"] for d in dots}) == 3
    assert all(isinstance(d["seed"], int) for d in dots)
    assert "secret" not in str(dots) and "'p'" not in str(dots)


def test_collect_counts_commits_and_prs_from_search():
    paths = []
    p = collect("u", lambda path: paths.append(path) or fake_get(path))
    assert p["commits"] == 2317 and p["prs"] == 203
    assert any(x.startswith("/search/commits?q=author:u") for x in paths)
    assert any(x.startswith("/search/issues?q=author:u+type:pr") for x in paths)


def test_collect_uses_authenticated_endpoint_when_asked():
    paths = []
    collect("u", lambda path: paths.append(path) or fake_get(path), authed=True)
    assert any(x.startswith("/user/repos") and "affiliation=owner" in x for x in paths)



def test_collect_falls_back_to_login_and_empty_bio():
    user = {**USER, "name": None, "bio": None}
    get = lambda path: user if path == "/users/u" else fake_get(path)
    p = collect("u", get)
    assert p["name"] == "u" and p["bio"] == ""
