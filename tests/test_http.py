import io, json
from unittest.mock import patch
from metrics.cli import make_get


def test_make_get_sends_token_and_parses_json():
    seen = {}

    def fake_urlopen(req):
        seen["url"] = req.full_url
        seen["auth"] = req.get_header("Authorization")
        return io.BytesIO(json.dumps({"ok": 1}).encode())

    with patch("metrics.cli.urlopen", fake_urlopen):
        assert make_get("tok")("/x") == {"ok": 1}
    assert seen == {"url": "https://api.github.com/x", "auth": "Bearer tok"}


def test_make_get_without_token_has_no_auth():
    seen = {}

    def fake_urlopen(req):
        seen["auth"] = req.get_header("Authorization")
        return io.BytesIO(b"[]")

    with patch("metrics.cli.urlopen", fake_urlopen):
        make_get(None)("/x")
    assert seen["auth"] is None
