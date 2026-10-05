import math
import random
from html import escape

from metrics.scene import SCENE_H, SCENE_STYLE, scene

W, SKY_H = 800, 440
H = SKY_H + SCENE_H
SKY = (40, 150, 720, 170)
PALETTE = ["#3572A5", "#f1e05a", "#e34c26", "#a371f7", "#56d364", "#f0883e", "#00ADD8", "#ff7eb6"]
KNOWN = {"Python": "#4b8bbe", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Go": "#00ADD8",
         "Rust": "#dea584", "C": "#9aa0a6", "C++": "#f34b7d", "Java": "#b07219", "Shell": "#89e051",
         "HTML": "#e34c26", "CSS": "#a371f7", "Jupyter Notebook": "#f37726", "Kotlin": "#A97BFF"}
STYLE = """
text{font-family:-apple-system,'Segoe UI','Noto Sans JP','Hiragino Sans','Yu Gothic',Helvetica,Arial,sans-serif;fill:#e6edf3}
.t{font-size:28px;font-weight:700;letter-spacing:.5px}.s{font-size:13px;fill:#8b9bb4}
.n{font-size:14px;fill:#c3cde0}.l{font-size:12px;fill:#c3cde0}.h{font-size:11px;fill:#6f7f9c;letter-spacing:3px}
.bg{animation:twinkle 4s ease-in-out infinite}
.repo{animation:twinkle 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
.link{stroke-width:1;stroke-dasharray:3 4;opacity:.45}
.shoot{animation:shoot 9s linear infinite}
@keyframes twinkle{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.8)}}
@keyframes shoot{0%{transform:translate(-120px,0);opacity:0}4%{opacity:1}14%{transform:translate(520px,140px);opacity:0}100%{transform:translate(520px,140px);opacity:0}}
"""


def _color(language):
    if language is None:
        return "#8b9bb4"
    return KNOWN.get(language) or PALETTE[sum(map(ord, language)) % len(PALETTE)]


def _pos(seed):
    x, y, w, h = SKY
    return x + (seed % 7200) / 7200 * w, y + (seed // 7200 % 1000) / 1000 * h


def _t(x, y, cls, text, extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}"{extra}>{escape(str(text))}</text>'


def _background(login):
    rng = random.Random(login)
    return [
        f'<circle class="bg" cx="{rng.uniform(0, W):.1f}" cy="{rng.uniform(0, SKY_H):.1f}" r="{rng.choice((.5, .8, 1.1)):.1f}" '
        f'fill="#fff" opacity="{rng.uniform(.2, .8):.2f}" style="animation-delay:{rng.uniform(0, 4):.1f}s"/>'
        for _ in range(90)
    ]


def _constellations(dots):
    placed = [(*_pos(d["seed"]), d) for d in dots]
    groups = {}
    for x, y, d in placed:
        if d["language"]:
            groups.setdefault(d["language"], []).append((x, y))
    lines = []
    for language, pts in groups.items():
        pts.sort()
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            lines.append(f'<line class="link" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{_color(language)}"/>')
    biggest = max([d["size"] for d in dots], default=0) or 1
    stars = []
    for x, y, d in placed:
        r = 2 + 5 * math.sqrt(d["size"] / biggest)
        c = _color(d["language"])
        stars.append(
            f'<circle class="repo" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" filter="url(#glow)" '
            f'style="animation-delay:{d["seed"] % 30 / 10:.1f}s"/>'
        )
    return lines + stars


def _languages(languages, y):
    total = sum(b for _, b in languages)
    top = languages[:8]
    out = [_t(30, y, "h", "LANGUAGES")]
    x = 30.0
    for name, size in top:
        w = (W - 60) * size / total
        out.append(f'<rect x="{x:.1f}" y="{y + 12}" width="{max(w - 3, 1):.1f}" height="8" rx="4" fill="{_color(name)}" filter="url(#glow)"/>')
        x += w
    for i, (name, size) in enumerate(top):
        cx, cy = 30 + (i % 4) * 190, y + 46 + (i // 4) * 22
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="4" fill="{_color(name)}" filter="url(#glow)"/>')
        out.append(_t(cx + 16, cy, "l", f"{name} {100 * size / total:.1f}%"))
    return out


def render(p):
    parts = _background(p["login"])
    parts += _constellations(p["dots"])
    parts.append(scene(p["login"], p["dots"], p))
    parts.append('<g class="shoot"><line x1="0" y1="20" x2="-70" y2="-6" stroke="url(#tail)" stroke-width="2"/><circle cx="0" cy="20" r="2" fill="#fff"/></g>')
    parts += [_t(30, 52, "t", p["name"]), _t(30, 74, "s", f"@{p['login']}")]
    if p["bio"]:
        parts.append(_t(30, 100, "n", p["bio"]))
    parts.append(_t(30, 124, "s", f"{p['followers']} followers · {p['following']} following · {p['repos']} repos · ★ {p['stars']}"))
    if p["languages"]:
        parts += _languages(p["languages"], 358)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f"<style>{STYLE}{SCENE_STYLE}</style>"
        '<defs><radialGradient id="sky" cx="30%" cy="20%" r="90%"><stop offset="0" stop-color="#1b2550"/>'
        '<stop offset=".55" stop-color="#0d1330"/><stop offset="1" stop-color="#05070f"/></radialGradient>'
        '<linearGradient id="tail" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>'
        f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="#05070f"/><rect width="{W}" height="{SKY_H}" fill="url(#sky)"/>'
        + "".join(parts)
        + "</g></svg>\n"
    )
