import hashlib
from collections import Counter

MAX_LANGUAGE_REPOS = 30


def aggregate_languages(per_repo):
    total = Counter()
    for langs in per_repo:
        total.update(langs)
    return sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))


def collect(login, get, authed=False):
    user = get(f"/users/{login}")
    path = "/user/repos?affiliation=owner&visibility=all" if authed else f"/users/{login}/repos?type=owner"
    repos = get(f"{path}&per_page=100&sort=pushed")
    own = sorted((r for r in repos if not r["fork"]), key=lambda r: r["pushed_at"], reverse=True)
    languages = aggregate_languages(
        get(f"/repos/{login}/{r['name']}/languages") for r in own[:MAX_LANGUAGE_REPOS]
    )
    return {
        "login": login,
        "name": user["name"] or login,
        "bio": user["bio"] or "",
        "followers": user["followers"],
        "following": user["following"],
        "repos": len(repos),
        "stars": sum(r["stargazers_count"] for r in own),
        "languages": languages,
        "dots": [
            {"seed": int(hashlib.sha1(r["name"].encode()).hexdigest()[:8], 16), "language": r["language"], "size": r["size"]}
            for r in sorted(own, key=lambda r: r["name"])
        ],
    }
