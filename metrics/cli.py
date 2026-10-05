import json
import os
from urllib.request import Request, urlopen

from metrics.data import collect
from metrics.render import render


def make_get(token):
    def get(path):
        req = Request("https://api.github.com" + path, headers={"Accept": "application/vnd.github+json"})
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        return json.load(urlopen(req))

    return get


def main(argv, get=None, collector=collect):
    login, out = argv
    token = os.environ.get("GITHUB_TOKEN")
    get = get or make_get(token)
    with open(out, "w") as f:
        f.write(render(collector(login, get, authed=bool(token))))
