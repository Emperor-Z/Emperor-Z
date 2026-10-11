"""Builds the profile images in assets/: the hero card and the project cards.

Everything else on the profile is plain text in README.md.
Run:  python3 tools/build.py
"""

import base64
import html
import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "src"
OUT = ROOT / "assets"

# Palette: Arjun's VS Code theme, "Activate SCARLET protocol" (max-ss.cyberpunk)
BG = "#0A0B0E"          # sideBar.background
PANEL = "#101116"       # editor.background
SCARLET = "#FF0055"     # editor.foreground, tab.activeBorder
SCARLET_FILL = "#140009"  # titleBar.activeBackground
AQUA = "#00FFC8"        # editorCursor, textLink
GREEN = "#00FF9C"       # buttons, classes
TEXT = "#EEFFFF"        # variables
MUTED = "#A9B1D6"
COMMENT = "#6766B3"     # comments
HAIRLINE = "#FFFFFF1A"

MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Inter,'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"


def esc(s):
    return html.escape(s, quote=True)


def write(name, data):
    (OUT / name).write_text(data)
    print(f"{name:24} {len(data.encode()) / 1024:6.1f} KB")


def curve(x1, y1, x2, y2, horizontal=True):
    if horizontal:
        mx = (x1 + x2) / 2
        return f"M{x1} {y1}C{mx} {y1} {mx} {y2} {x2} {y2}"
    my = (y1 + y2) / 2
    return f"M{x1} {y1}C{x1} {my} {x2} {my} {x2} {y2}"


def pill(x, y, w, h, label, size, accent=False):
    stroke, fill, sw = (SCARLET, SCARLET_FILL, 1.6) if accent else (HAIRLINE, PANEL, 1.2)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.36:.1f}" font-size="{size}" fill="{TEXT}" text-anchor="middle">{esc(label)}</text>')


# ----------------------------------------------------------------------------
# hero

def hero():
    w, h = 840, 280
    kids = [("rag", 572), ("tools", 638), ("memory", 704), ("eval", 770)]
    paths = [curve(671, 116, cx, 184, horizontal=False) for _, cx in kids]
    edges = "".join(f'<path d="{p}"/>' for p in paths)
    nodes = "".join(pill(cx - 30, 184, 60, 26, label, 11) for label, cx in kids)
    pulses = "".join(
        f'<circle r="2.4" fill="{AQUA}"><animateMotion dur="2.4s" begin="-{i * 0.6:.1f}s" '
        f'repeatCount="indefinite" path="{p}"/></circle>' for i, p in enumerate(paths))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Arjun Ashad. Agentic AI, multi-agent systems, applied ML.">
<defs>
  <radialGradient id="glow" cx="0.8" cy="0.48" r="0.4">
    <stop offset="0" stop-color="{SCARLET}" stop-opacity="0.15"/>
    <stop offset="1" stop-color="{SCARLET}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="16" fill="url(#glow)"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{HAIRLINE}"/>

<text x="56" y="76" font-family="{MONO}" font-size="13"><tspan fill="{GREEN}">arjun@agents</tspan><tspan fill="{COMMENT}">:~$ </tspan><tspan fill="{MUTED}">whoami </tspan><tspan fill="{SCARLET}">_<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></tspan></text>
<text x="54" y="134" font-family="{SANS}" font-size="46" font-weight="600" letter-spacing="-0.5" fill="{TEXT}">Arjun Ashad</text>
<text x="56" y="170" font-family="{SANS}" font-size="17" fill="{MUTED}">Agentic AI · Multi-agent systems · Applied ML</text>
<rect x="56" y="192" width="36" height="2" rx="1" fill="{SCARLET}"/>
<text x="56" y="226" font-family="{MONO}" font-size="12" letter-spacing="0.5" fill="{COMMENT}">MSc Applied AI, Warwick  ·  Backend engineer, FundedIn</text>

<g font-family="{MONO}">
  <g stroke="{SCARLET}" stroke-opacity="0.5" stroke-width="1.3" fill="none">{edges}</g>
  {pill(603, 78, 136, 38, "orchestrator", 13, accent=True)}
  {nodes}
  {pulses}
</g>
</svg>
"""
    write("hero.svg", svg)


# ----------------------------------------------------------------------------
# project cards: one dark card per project, two per row
#
# Each card SVG is 420 wide with the card body inset 8px on the inner side, so two
# cards side by side leave a 16px gutter and their outer edges line up with the hero.

PROJECTS = [
    {
        "slug": "g923-claude",
        "kicker": "DEVELOPER TOOL · PYPI",
        "title": "g923-claude",
        "desc": "Drive Claude Code with a racing wheel. Brake interrupts, gas sends, "
                "gears switch models, and the wheel buzzes when Claude needs you.",
        "tags": ["python", "evdev", "uinput"],
        "thumb": "g923-claude.jpg",
    },
    {
        "slug": "ares",
        "kicker": "LOCAL MULTI-AGENT SYSTEM",
        "title": "Ares",
        "desc": "An orchestrator routes coder, thinker, runner and Serena agents over "
                "A2A on Ollama models, with mem0 memory and Langfuse tracing.",
        "tags": ["python", "ollama", "mem0", "langfuse"],
        "thumb": "ares",
    },
    {
        "slug": "verisim",
        "kicker": "MSC DISSERTATION",
        "title": "VeriSim",
        "desc": "A clinical training sim where every character is an AI agent, and "
                "tests are gated on the patient's consent. Runs offline.",
        "tags": ["typescript", "convex", "ollama"],
        "thumb": "verisim.jpg",
    },
    {
        "slug": "devdesk",
        "kicker": "MULTI-AGENT RAG",
        "title": "DevDesk",
        "desc": "A router built on Google ADK hands each question to a per-project "
                "specialist agent, checked by a deterministic eval.",
        "tags": ["python", "google adk", "gemini", "chroma"],
        "thumb": "devdesk",
    },
]

CARD_W, CARD_H, GUTTER = 420, 420, 16
THUMB_H = (CARD_W - GUTTER // 2) // 2   # 2:1 thumbnail, full bleed
WRAP = 47                               # chars per line at 14px, safe for wide fallback fonts


def node(x, y, w, title, sub):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="80" rx="16" fill="{SCARLET_FILL}" stroke="{SCARLET}" stroke-width="2.5"/>'
            f'<text x="{x + w / 2}" y="{y + 36}" font-size="24" fill="{TEXT}" text-anchor="middle">{esc(title)}</text>'
            f'<text x="{x + w / 2}" y="{y + 62}" font-size="17" fill="{SCARLET}" text-anchor="middle">{esc(sub)}</text>')


def leaf(x, y, w, label, port=None, dashed=False):
    dash = ' stroke-dasharray="6 6"' if dashed else ""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="50" rx="25" fill="{PANEL}" stroke="{HAIRLINE}" stroke-width="2"{dash}/>'
           f'<text x="{x + 30}" y="{y + 33}" font-size="21" fill="{MUTED if dashed else TEXT}">{esc(label)}</text>')
    if port:
        out += f'<text x="{x + w - 28}" y="{y + 32}" font-size="18" fill="{COMMENT}" text-anchor="end">{esc(port)}</text>'
    return out


def ares_drawing():
    rows = [("coder", ":8101"), ("thinker", ":8102"), ("runner", ":8103"), ("serena", ":8104")]
    ys = [70, 140, 210, 280]
    edges = "".join(f'<path d="{curve(300, 200, 470, y + 25)}"/>' for y in ys)
    return f"""<rect width="800" height="400" fill="url(#glow)"/>
<g font-family="{MONO}">
<g stroke="{SCARLET}" stroke-opacity="0.55" stroke-width="2.2" fill="none">{edges}</g>
{node(60, 160, 240, "orchestrator", "a2a :8100")}
{"".join(leaf(470, y, 270, n, p) for (n, p), y in zip(rows, ys))}
</g>"""


def devdesk_drawing():
    rows = ["verisim_agent", "ares_agent", "search_all"]
    ys = [95, 175, 255]
    edges = "".join(f'<path d="{curve(280, 200, 360, y + 25)}"/>' for y in ys)
    reads = "".join(f'<path d="{curve(620, y + 25, 680, 200)}"/>' for y in ys)
    return f"""<rect width="800" height="400" fill="url(#glow)"/>
<g font-family="{MONO}">
<g stroke="{SCARLET}" stroke-opacity="0.55" stroke-width="2.2" fill="none">{edges}</g>
<g stroke="{AQUA}" stroke-opacity="0.45" stroke-width="2" fill="none" stroke-dasharray="5 6">{reads}</g>
{node(60, 160, 220, "router", "adk agent")}
{"".join(leaf(360, y, 260, n, dashed=(n == "search_all")) for n, y in zip(rows, ys))}
<g fill="none" stroke="{AQUA}" stroke-width="2.2" stroke-opacity="0.85">
  <path d="M684 168V232C684 246 756 246 756 232V168"/><ellipse cx="720" cy="168" rx="36" ry="11"/>
  <path d="M684 190C684 202 756 202 756 190M684 212C684 224 756 224 756 212" stroke-opacity="0.4"/>
</g>
<text x="720" y="280" font-size="17" fill="{AQUA}" fill-opacity="0.85" text-anchor="middle">chroma</text>
</g>"""


DRAWINGS = {"ares": ares_drawing, "devdesk": devdesk_drawing}


def thumbnail(ref):
    if ref in DRAWINGS:
        return DRAWINGS[ref]()
    b64 = base64.b64encode((SRC / ref).read_bytes()).decode()
    return f'<image href="data:image/jpeg;base64,{b64}" width="800" height="400" preserveAspectRatio="xMidYMid slice"/>'


def card(p, side):
    bx = 0 if side == "left" else GUTTER // 2
    bw = CARD_W - GUTTER // 2
    pad = 24
    lines = textwrap.wrap(p["desc"], WRAP)
    assert len(lines) <= 3, f'{p["slug"]}: description runs to {len(lines)} lines'

    y_kicker = THUMB_H + 36
    y_title = y_kicker + 28
    y_desc = y_title + 30
    y_rule = CARD_H - 48
    y_tags = CARD_H - 21
    ax, ay = bx + bw - pad, y_title - 6   # link arrow, top-right of the title line

    desc = "".join(f'<text x="{bx + pad}" y="{y_desc + i * 22}">{esc(line)}</text>' for i, line in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="{esc(p["title"])}: {esc(p["desc"])}">
<defs>
  <clipPath id="card"><rect x="{bx}" width="{bw}" height="{CARD_H}" rx="14"/></clipPath>
  <radialGradient id="glow" cx="0.28" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{SCARLET}" stop-opacity="0.14"/>
    <stop offset="1" stop-color="{SCARLET}" stop-opacity="0"/>
  </radialGradient>
</defs>
<g clip-path="url(#card)">
  <rect x="{bx}" width="{bw}" height="{CARD_H}" fill="{BG}"/>
  <svg x="{bx}" y="0" width="{bw}" height="{THUMB_H}" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid slice">{thumbnail(p["thumb"])}</svg>
  <rect x="{bx}" y="{THUMB_H}" width="{bw}" height="1" fill="{HAIRLINE}"/>
</g>
<rect x="{bx + 0.5}" y="0.5" width="{bw - 1}" height="{CARD_H - 1}" rx="13.5" fill="none" stroke="{HAIRLINE}"/>

<text x="{bx + pad}" y="{y_kicker}" font-family="{MONO}" font-size="10.5" letter-spacing="1.6" fill="{SCARLET}">{esc(p["kicker"])}</text>
<text x="{bx + pad}" y="{y_title}" font-family="{SANS}" font-size="20" font-weight="600" fill="{TEXT}">{esc(p["title"])}</text>
<path d="M{ax - 9} {ay + 9}L{ax} {ay}M{ax - 7} {ay}H{ax}V{ay + 7}" fill="none" stroke="{COMMENT}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
<g font-family="{SANS}" font-size="14" fill="{MUTED}">{desc}</g>

<rect x="{bx + pad}" y="{y_rule}" width="{bw - 2 * pad}" height="1" fill="{HAIRLINE}"/>
<text x="{bx + pad}" y="{y_tags}" font-family="{MONO}" font-size="11" letter-spacing="0.4" fill="{COMMENT}">{esc("  ·  ".join(p["tags"]))}</text>
</svg>
"""


if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    hero()
    for i, p in enumerate(PROJECTS):
        write(f'card-{p["slug"]}.svg', card(p, "left" if i % 2 == 0 else "right"))
    shutil.copy(SRC / "skillicons.svg", OUT / "stack.svg")
