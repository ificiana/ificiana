from collections import Counter

MAX_LANGUAGE_REPOS = 30
RECENT_COUNT = 5


def aggregate_languages(per_repo):
    total = Counter()
    for langs in per_repo:
        total.update(langs)
    return sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))


def collect(login, get):
    user = get(f"/users/{login}")
    repos = get(f"/users/{login}/repos?per_page=100&type=owner&sort=pushed")
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
        "repos": user["public_repos"],
        "stars": sum(r["stargazers_count"] for r in own),
        "languages": languages,
        "recent": [
            {
                "name": r["name"],
                "description": r["description"] or "",
                "language": r["language"],
                "stars": r["stargazers_count"],
            }
            for r in own[:RECENT_COUNT]
        ],
    }
