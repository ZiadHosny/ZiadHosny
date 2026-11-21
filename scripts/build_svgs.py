"""Build every SVG used by the profile README.

Usage: python scripts/build_svgs.py

Rules for all output:
- system fonts only (no web fonts, no embedded fonts)
- no scripts
- animation is CSS @keyframes inside the SVG only (no SMIL)
- text is static, so it stays readable even if animation never runs
"""
import base64, os, re, urllib.request, xml.dom.minidom
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
ICONS = os.path.join(ASSETS, "icons")
SI = "https://cdn.jsdelivr.net/npm/simple-icons@{}/icons/{}.svg"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"
PURPLE, CYAN, BLUE, TEXT, MUTED = "#bd93f9", "#8be9fd", "#6272a4", "#f8f8f2", "#a9abc3"

# ------------------------------------------------------------------ content
NAME = "Ziad Hosny"
TITLE = "Full-Stack Software Engineer"
TYPING_LINES = [
    "Full-Stack Software Engineer",
    "Node.js · NestJS · PostgreSQL",
    "React · Next.js · TypeScript",
    "System Design in Arabic",
]
BUTTONS = [
    ("website", "Website", "globe", PURPLE),
    ("youtube", "YouTube", ("16.38.0", "youtube"), "#FF0000"),
    ("linkedin", "LinkedIn", ("9.21.0", "linkedin"), "#0A66C2"),
    ("email", "Email", ("16.38.0", "gmail"), "#EA4335"),
    ("system-design-in-arabic", "System Design in Arabic", ("16.38.0", "youtube"), "#FF0000"),
]
TECH = [
    ("BACKEND", [
        ("JavaScript", "javascript-original.svg"), ("TypeScript", "typescript-original.svg"),
        ("Python", "python-original.svg"), ("PHP", "php-original.svg"),
        ("Node.js", "nodejs-original.svg"), ("NestJS", "nestjs-original.svg"),
        ("Express", "express-white.svg"), ("Strapi", "strapi-4945FF.svg"),
        ("Prisma", "prisma-white.svg"), ("Sequelize", "sequelize-original.svg"),
        ("Mongoose", "mongoose-white.svg"), ("JWT", "jsonwebtokens-D63AFF.svg"),
    ]),
    ("FRONTEND", [
        ("React", "react-original.svg"), ("Next.js", "nextjs-original.svg"),
        ("Angular", "angular-original.svg"), ("Redux", "redux-original.svg"),
        ("Material UI", "materialui-original.svg"), ("Tailwind CSS", "tailwindcss-original.svg"),
    ]),
    ("DATABASES", [
        ("PostgreSQL", "postgresql-original.svg"), ("MongoDB", "mongodb-original.svg"),
        ("Microsoft SQL Server", "microsoftsqlserver-original.svg"), ("Firebase", "firebase-original.svg"),
    ]),
    ("TOOLS", [
        ("Docker", "docker-original.svg"), ("Git", "git-original.svg"),
        ("GitHub", "github-white.svg"), ("GitHub Actions", "githubactions-original.svg"),
        ("GitLab", "gitlab-original.svg"), ("Postman", "postman-original.svg"),
        ("Sentry", "sentry-white.svg"), ("npm", "npm-original.svg"), ("Figma", "figma-original.svg"),
    ]),
    ("AI", [
        ("Claude", "claude-original.svg"), ("ChatGPT", "openai-white.svg"),
        ("GitHub Copilot", "githubcopilot-white.svg"),
    ]),
]

# ------------------------------------------------------------------ helpers
_paths = {}


def si_path(version, slug):
    if (version, slug) not in _paths:
        svg = urllib.request.urlopen(SI.format(version, slug), timeout=60).read().decode()
        _paths[(version, slug)] = re.search(r' d="([^"]+)"', svg).group(1)
    return _paths[(version, slug)]


def icon(spec, x, y, size, color):
    s = size / 24
    if spec == "globe":
        return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.3f})" fill="none" stroke="{color}" stroke-width="2">'
                '<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.5" ry="10"/>'
                '<path d="M2 12h20M4 6.5h16M4 17.5h16"/></g>')
    return f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.3f})" fill="{color}" d="{si_path(*spec)}"/>'


def text_width(s, size):
    return len(s) * size * 0.56


BG_CSS = f"""
    .s1 {{ animation: s1 10s ease-in-out infinite; }}
    .s2 {{ animation: s2 10s ease-in-out infinite; }}
    @keyframes s1 {{ 50% {{ stop-color: #10121b; }} }}
    @keyframes s2 {{ 50% {{ stop-color: #181430; }} }}
    .grid {{ animation: grid 8s linear infinite; }}
    @keyframes grid {{ to {{ transform: translate(40px, 40px); }} }}
    .b1 {{ animation: b1 16s ease-in-out infinite; }}
    .b2 {{ animation: b2 18s ease-in-out infinite; }}
    .b3 {{ animation: b3 20s ease-in-out infinite; }}
    @keyframes b1 {{ 50% {{ transform: translate(120px, 40px); }} }}
    @keyframes b2 {{ 50% {{ transform: translate(-120px, -30px); }} }}
    @keyframes b3 {{ 50% {{ transform: translate(0, 60px); }} }}
    .tw {{ animation: tw 4s ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: .15; }} 50% {{ opacity: .9; }} }}
    .fl {{ animation: fl 6s ease-in-out infinite; transform-box: fill-box; }}
    @keyframes fl {{ 50% {{ transform: translateY(-10px); }} }}
"""


def background(w, h, seed=0, glow=0.25):
    pts = [(0.15, 0.3), (0.85, 0.7), (0.5, 0.1)]
    pts = pts[seed % 3:] + pts[:seed % 3]
    (ax, ay), (bx, by), (cx, cy) = [(px * w, py * h) for px, py in pts]
    r = max(80, min(h, 240) * 0.6)
    stars = [(0.05, 0.2, 0), (0.95, 0.3, 1.2), (0.9, 0.85, 2.1), (0.08, 0.8, 0.6),
             (0.35, 0.9, 1.7), (0.7, 0.12, 2.6)]
    star_svg = "".join(
        f'<circle class="tw" cx="{x * w:.0f}" cy="{y * h:.0f}" r="1.6" style="animation-delay:-{d}s"/>'
        for x, y, d in stars)
    defs = f'''
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop class="s1" offset="0" stop-color="#0b0d13"/>
      <stop class="s2" offset="1" stop-color="#141626"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{PURPLE}"/><stop offset="0.5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PURPLE}"/>
    </linearGradient>
    <pattern id="gridp" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{TEXT}" stroke-opacity="0.045"/>
    </pattern>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="45"/></filter>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="20"/></clipPath>'''
    layers = f'''
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <g filter="url(#blur)" opacity="{glow}">
      <circle class="b1" cx="{ax:.0f}" cy="{ay:.0f}" r="{r:.0f}" fill="{PURPLE}"/>
      <circle class="b2" cx="{bx:.0f}" cy="{by:.0f}" r="{r:.0f}" fill="{BLUE}"/>
      <circle class="b3" cx="{cx:.0f}" cy="{cy:.0f}" r="{r * 0.7:.0f}" fill="{CYAN}" opacity="0.5"/>
    </g>
    <rect class="grid" x="-40" y="-40" width="{w + 80}" height="{h + 80}" fill="url(#gridp)"/>
    <g fill="{TEXT}">{star_svg}</g>
    <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="{PURPLE}" stroke-opacity="0.18"/>'''
    return defs, layers


def card(w, h, label, body, seed=0, glow=0.25, extra_css=""):
    defs, layers = background(w, h, seed, glow)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}">\n  <title>{escape(label)}</title>\n'
            f'  <style>{BG_CSS}{extra_css}  </style>\n  <defs>{defs}\n  </defs>\n'
            f'  <g clip-path="url(#card)">{layers}\n{body}\n  </g>\n</svg>\n')


def write(rel, svg):
    xml.dom.minidom.parseString(svg.encode())
    assert "<script" not in svg and "@import" not in svg and "@font-face" not in svg
    assert not re.search(r"<animate|<set\b", svg), "SMIL found"
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(svg)
    print(f"assets/{rel}  {len(svg) // 1024}KB")


# ------------------------------------------------------------------ builders
def header():
    w, h = 1200, 320
    symbols = [("( )", 150, 80, 28, 0), ("{ }", 1040, 90, 40, 2), ("&lt;/&gt;", 90, 250, 44, 1), ("=&gt;", 980, 285, 28, 3)]
    sym = "".join(
        f'<text class="fl" x="{x}" y="{y}" font-size="{s}" style="animation-delay:-{d}s">{t}</text>'
        for t, x, y, s, d in symbols)
    body = f'''
    <g font-family="{MONO}" font-weight="700" fill="{TEXT}" opacity="0.08">{sym}</g>
    <g font-family="{SANS}" text-anchor="middle">
      <text x="{w / 2}" y="160" font-size="76" font-weight="800" fill="url(#shine)">{escape(NAME)}</text>
      <text x="{w / 2}" y="212" font-size="26" font-weight="500" fill="{TEXT}" fill-opacity="0.9" letter-spacing="2">{escape(TITLE)}</text>
    </g>
    <rect x="{w / 2 - 80}" y="234" width="160" height="4" rx="2" fill="url(#shine)"/>'''
    write("header.svg", card(w, h, f"{NAME} - {TITLE}", body, seed=0, glow=0.3))


def typing():
    w, h, size = 600, 50, 22
    cycle, n = 16, len(TYPING_LINES)
    slot = 100 / n
    css, groups, masks = [], [], []
    for i, line in enumerate(TYPING_LINES):
        tw = len(line) * size * 0.6
        x0 = (w - tw) / 2
        steps = len(line)
        delay = -((cycle - i * cycle / n) % cycle)
        t_end, hold_end, erase_end, off = slot * 0.4, slot * 0.8, slot * 0.96, slot * 0.999
        css.append(f'''
    .v{i} {{ animation: v{i} {cycle}s infinite; animation-delay: {delay}s; }}
    @keyframes v{i} {{ 0%, {off:.2f}% {{ opacity: 1; }} {slot:.2f}%, 100% {{ opacity: 0; }} }}
    .m{i} {{ transform-box: fill-box; transform-origin: left center; animation: m{i} {cycle}s infinite; animation-delay: {delay}s; }}
    @keyframes m{i} {{
      0% {{ transform: scaleX(0); animation-timing-function: steps({steps}, end); }}
      {t_end:.2f}% {{ transform: scaleX(1); }}
      {hold_end:.2f}% {{ transform: scaleX(1); animation-timing-function: steps({steps}, end); }}
      {erase_end:.2f}%, 100% {{ transform: scaleX(0); }}
    }}
    .c{i} {{ animation: c{i} {cycle}s infinite; animation-delay: {delay}s; }}
    @keyframes c{i} {{
      0% {{ transform: translateX(0); animation-timing-function: steps({steps}, end); }}
      {t_end:.2f}% {{ transform: translateX({tw:.1f}px); }}
      {hold_end:.2f}% {{ transform: translateX({tw:.1f}px); animation-timing-function: steps({steps}, end); }}
      {erase_end:.2f}%, 100% {{ transform: translateX(0); }}
    }}''')
        masks.append(f'<mask id="k{i}"><rect class="m{i}" x="{x0:.1f}" y="0" width="{tw:.1f}" height="{h}" fill="#fff"/></mask>')
        groups.append(
            f'<g class="v{i}">'
            f'<text x="{x0:.1f}" y="{h / 2 + 8}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" mask="url(#k{i})">{escape(line)}</text>'
            f'<rect class="c{i}" x="{x0 + 2:.1f}" y="{h / 2 - 13}" width="3" height="27" fill="{PURPLE}"/></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="{escape(", ".join(TYPING_LINES))}">\n  <title>{escape(TITLE)}</title>\n'
           f'  <style>{"".join(css)}\n  </style>\n  <defs>{"".join(masks)}</defs>\n'
           f'  <g font-family="{MONO}" font-size="{size}" font-weight="500" fill="{PURPLE}">{"".join(groups)}</g>\n</svg>\n')
    write("typing.svg", svg)


def button(name, label, spec, color):
    isz, fs = 22, 18
    tw = text_width(label, fs)
    w, h = max(200, int(isz + 12 + tw + 64)), 56
    x0 = (w - (isz + 12 + tw)) / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
           f'<title>{escape(label)}</title>'
           f'<style>.o {{ animation: o 4s ease-in-out infinite; }} @keyframes o {{ 50% {{ stroke-opacity: .65; }} }}</style>'
           f'<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d13"/><stop offset="1" stop-color="#181a2e"/></linearGradient></defs>'
           f'<rect class="o" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#b)" stroke="{PURPLE}" stroke-opacity="0.3"/>'
           + icon(spec, x0, (h - isz) / 2, isz, color)
           + f'<text x="{x0 + isz + 12:.1f}" y="{h / 2 + 6.5}" font-family="{SANS}" font-size="{fs}" font-weight="600" fill="{TEXT}">{escape(label)}</text>'
           f'</svg>\n')
    write(f"buttons/{name}.svg", svg)


def ensure_white(slug, version="16.38.0"):
    path = os.path.join(ICONS, f"{slug}-white.svg")
    if not os.path.exists(path):
        svg = urllib.request.urlopen(SI.format(version, slug), timeout=60).read().decode()
        open(path, "w", encoding="utf-8").write(svg.replace("<svg ", '<svg fill="#ffffff" ', 1))


def tech_stack():
    ensure_white("mongoose")
    ensure_white("openai", "12.0.0")  # removed from newer simple-icons releases
    W, TILE, GAP, ICON = 1000, 64, 14, 40
    parts, y, n = [], 112, 0
    for title, icons in TECH:
        parts.append(f'<text x="{W / 2}" y="{y}" text-anchor="middle" font-family="{SANS}" font-size="15" '
                     f'font-weight="600" letter-spacing="4" fill="{PURPLE}">{title}</text>')
        x = (W - (len(icons) * TILE + (len(icons) - 1) * GAP)) / 2
        ty = y + 20
        for label, file in icons:
            raw = open(os.path.join(ICONS, file), "rb").read()
            uri = "data:image/svg+xml;base64," + base64.b64encode(raw).decode()
            pad = (TILE - ICON) / 2
            parts.append(
                f'<g class="bob" style="animation-delay:-{n * 0.15:.2f}s"><title>{escape(label)}</title>'
                f'<rect x="{x}" y="{ty}" width="{TILE}" height="{TILE}" rx="14" fill="{TEXT}" fill-opacity="0.05" '
                f'stroke="{PURPLE}" stroke-opacity="0.25"/>'
                f'<image x="{x + pad}" y="{ty + pad}" width="{ICON}" height="{ICON}" href="{uri}"/></g>')
            x += TILE + GAP
            n += 1
        y = ty + TILE + 44
    H = int(y - 44 + 40)
    body = (f'<text x="{W / 2}" y="62" text-anchor="middle" font-family="{SANS}" font-size="34" '
            f'font-weight="800" fill="url(#shine)">Tech Stack</text>' + "".join(parts))
    css = """    .bob { animation: bob 4s ease-in-out infinite; }
    @keyframes bob { 50% { transform: translateY(-4px); } }
"""
    write("tech-stack.svg", card(W, H, "Tech Stack", body, seed=0, glow=0.22, extra_css=css))


def footer():
    w, h = 1000, 110
    body = (f'<text x="{w / 2}" y="{h / 2 + 10}" text-anchor="middle" font-family="{SANS}" font-size="26" '
            f'font-weight="700" fill="url(#shine)">Thanks for stopping by</text>')
    write("footer.svg", card(w, h, "Thanks for stopping by", body, seed=2))


if __name__ == "__main__":
    header()
    typing()
    for b in BUTTONS:
        button(*b)
    tech_stack()
    footer()
