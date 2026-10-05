import random

W = 800
SCENE_H = 400
GROUND = 335
LANTERNS = 11
COLORS = ["#3572A5", "#f1e05a", "#e34c26", "#a371f7", "#56d364", "#f0883e", "#00ADD8", "#ff7eb6"]
KNOWN = {"Python": "#4b8bbe", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Go": "#00ADD8",
         "Rust": "#dea584", "C": "#9aa0a6", "C++": "#f34b7d", "Java": "#b07219", "Shell": "#89e051",
         "HTML": "#e34c26", "CSS": "#a371f7", "Jupyter Notebook": "#f37726", "Kotlin": "#A97BFF"}

SCENE_STYLE = """
.cloud{animation:drift 80s linear infinite}
.lantern{animation:sway 3.5s ease-in-out infinite;transform-box:fill-box;transform-origin:50% 0}
.win{animation:win 3.2s ease-in-out infinite}
.jp{font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic',Meiryo,'Noto Sans CJK JP',sans-serif}
@keyframes drift{from{transform:translateX(-260px)}to{transform:translateX(1060px)}}
@keyframes sway{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}}
@keyframes win{0%,100%{opacity:1}50%{opacity:.55}}
"""

DEFS = (
    "<defs>"
    '<linearGradient id="scSky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#0d1330" stop-opacity="0"/><stop offset=".1" stop-color="#241552"/>'
    '<stop offset=".42" stop-color="#7a2a78"/><stop offset=".68" stop-color="#e8546a"/>'
    '<stop offset=".86" stop-color="#ff9a5c"/><stop offset="1" stop-color="#ffc47a"/></linearGradient>'
    '<radialGradient id="scSun"><stop offset="0" stop-color="#fff6b0"/><stop offset=".6" stop-color="#ffb347"/>'
    '<stop offset="1" stop-color="#ff5e6c"/></radialGradient>'
    '<radialGradient id="scHalo"><stop offset="0" stop-color="#ffb36b" stop-opacity=".6"/>'
    '<stop offset="1" stop-color="#ffb36b" stop-opacity="0"/></radialGradient>'
    '<radialGradient id="scLamp"><stop offset="0" stop-color="#ffd27a"/><stop offset=".5" stop-color="#ff5a4a"/>'
    '<stop offset="1" stop-color="#b5121b"/></radialGradient>'
    '<filter id="scGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    "</defs>"
)


def _color(language):
    if language is None:
        return "#8b9bb4"
    return KNOWN.get(language) or COLORS[sum(map(ord, language)) % len(COLORS)]


def _buildings(rng, narrow, wide, top_min, top_max):
    out, x = [], -10
    while x < W:
        w = rng.randint(narrow, wide)
        out.append((x, w, rng.randint(top_min, top_max)))
        x += w + rng.randint(0, 4)
    return out


def _sky(rng):
    clouds = "".join(
        f'<g transform="translate(0,{y})"><g class="cloud" style="animation-delay:-{rng.uniform(0, 80):.0f}s">'
        f'<ellipse cx="0" cy="0" rx="70" ry="9"/><ellipse cx="-25" cy="-6" rx="38" ry="9"/>'
        f'<ellipse cx="30" cy="-4" rx="30" ry="8"/></g></g>'
        for y in (120, 175, 225)
    )
    return (
        f'<rect y="-40" width="{W}" height="{SCENE_H + 40}" fill="url(#scSky)"/>'
        '<circle cx="560" cy="250" r="150" fill="url(#scHalo)"/>'
        '<circle cx="560" cy="250" r="62" fill="url(#scSun)"/>'
        f'<g fill="#ff9ac1" opacity=".35">{clouds}</g>'
    )


def _far(rng):
    out = []
    for x, w, top in _buildings(rng, 30, 56, 150, 240):
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{GROUND - top}" fill="#4a2670" opacity=".85"/>')
        out.append(f'<rect x="{x + w // 2}" y="{top - 16}" width="2" height="16" fill="#4a2670" opacity=".85"/>')
    return "".join(out)


def _near(rng, dots):
    blds = _buildings(rng, 34, 64, 200, 275)
    grids = []
    out = []
    for x, w, top in blds:
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{GROUND - top}" fill="#170c30"/>')
        cols, rows = max(1, (w - 8) // 9), (GROUND - top - 14) // 11
        grids.append((x, top, cols, rows))
        for c in range(cols):
            for r in range(rows):
                if rng.random() < 0.22:
                    out.append(f'<rect class="dim" x="{x + 4 + c * 9}" y="{top + 12 + r * 11}" width="5" height="6" fill="#ffd27a" opacity=".35"/>')
    for d in dots:
        x, top, cols, rows = grids[d["seed"] % len(grids)]
        cell = d["seed"] // len(grids) % (cols * rows)
        out.append(
            f'<rect class="win" x="{x + 4 + cell % cols * 9}" y="{top + 12 + cell // cols * 11}" width="5" height="6" '
            f'fill="{_color(d["language"])}" filter="url(#scGlow)" style="animation-delay:-{d["seed"] % 30 / 10:.1f}s"/>'
        )
    return "".join(out)


def _ground():
    return (
        f'<rect y="{GROUND}" width="{W}" height="{SCENE_H - GROUND}" fill="#0b0616"/>'
        f'<rect y="{GROUND}" width="{W}" height="2" fill="#ff4fa3" opacity=".55" filter="url(#scGlow)"/>'
    )


def _lanterns():
    out = ['<path d="M-10,36 Q400,112 810,48" fill="none" stroke="#2a1233" stroke-width="1.5"/>']
    for i in range(LANTERNS):
        t = (i + .5) / LANTERNS
        x = 2 * (1 - t) * t * 400 + (1 - t) ** 2 * -10 + t * t * 810
        y = 2 * (1 - t) * t * 112 + (1 - t) ** 2 * 36 + t * t * 48
        c = "#ffd27a" if i % 2 else "#ff9a5c"
        out.append(
            f'<g transform="translate({x:.1f},{y:.1f})"><g class="lantern" style="animation-delay:-{i * .3:.1f}s">'
            f'<circle cy="12" r="17" fill="{c}" opacity=".3"/>'
            '<rect x="-4" y="0" width="8" height="3" fill="#2a1233"/>'
            '<ellipse cy="12" rx="8" ry="10" fill="url(#scLamp)"/>'
            '<rect x="-4" y="21" width="8" height="3" fill="#2a1233"/></g></g>'
        )
    return "".join(out)


def scene(login, dots, stats):
    rng = random.Random(login + "-city")
    stats_line = f"フォロワー {stats['followers']} ・ リポジトリ {stats['repos']} ・ ★ {stats['stars']}"
    return (
        f'<g transform="translate(0,440)">{DEFS}{_sky(rng)}{_far(rng)}{_near(rng, dots)}{_ground()}'
        f'{_lanterns()}'
        f'<text class="jp" x="290" y="378" font-size="12" style="fill:#c3cde0">{stats_line}</text>'
        '</g>'
    )
