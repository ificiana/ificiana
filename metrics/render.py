from html import escape

WIDTH = 800
COLORS = ["#3572A5", "#f1e05a", "#e34c26", "#563d7c", "#89e051", "#b07219", "#00ADD8", "#c6538c"]
STYLE = (
    "text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#c9d1d9}"
    ".t{font-size:24px;font-weight:600}.s{font-size:14px;fill:#8b949e}"
    ".h{font-size:16px;font-weight:600}.n{font-size:14px}"
)


def _t(x, y, cls, text):
    return f'<text x="{x}" y="{y}" class="{cls}">{escape(str(text))}</text>'


def _languages(languages, y):
    total = sum(b for _, b in languages)
    out = [_t(30, y, "h", "Top languages")]
    x, bar_y = 30.0, y + 14
    for i, (name, size) in enumerate(languages):
        w = (WIDTH - 60) * size / total
        out.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="10" fill="{COLORS[i % len(COLORS)]}"/>')
        x += w
    for i, (name, size) in enumerate(languages):
        cx, cy = 30 + (i % 4) * 190, bar_y + 34 + (i // 4) * 22
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 5}" r="5" fill="{COLORS[i % len(COLORS)]}"/>')
        out.append(_t(cx + 16, cy, "n", f"{name} {100 * size / total:.1f}%"))
    return out, bar_y + 34 + ((len(languages) - 1) // 4 + 1) * 22


def render(p):
    parts = [_t(30, 45, "t", p["name"]), _t(30, 68, "s", f"@{p['login']}")]
    if p["bio"]:
        parts.append(_t(30, 92, "n", p["bio"]))
    stats = f"{p['followers']} followers · {p['following']} following · {p['repos']} repos · ★ {p['stars']}"
    parts.append(_t(30, 118, "s", stats))
    y = 150
    if p["languages"]:
        lang, y = _languages(p["languages"], y)
        parts += lang
    if p["recent"]:
        parts.append(_t(30, y + 20, "h", "Recent activity"))
        y += 44
        for r in p["recent"]:
            meta = " · ".join(x for x in (r["language"], f"★ {r['stars']}") if x)
            parts.append(_t(30, y, "n", r["name"]))
            parts.append(_t(WIDTH - 30, y, "s", meta).replace("<text ", '<text text-anchor="end" '))
            if r["description"]:
                parts.append(_t(30, y + 18, "s", r["description"]))
                y += 18
            y += 32
    height = y + 10
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">'
        f"<style>{STYLE}</style>"
        f'<rect width="{WIDTH}" height="{height}" rx="10" fill="#0d1117"/>'
        + "".join(parts)
        + "</svg>\n"
    )
