"""Builds the profile README panels in assets/.

Every panel is drawn in one shared 840px-wide coordinate space, so the frame,
grid and cards line up when README.md stacks the images with align="top".
Half and third width cards are the same drawing cropped with viewBox.

Edit the data below, then run:  python3 tools/build.py
"""

import base64
import html
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "src"
OUT = ROOT / "assets"

W = 840
FRAME_L, FRAME_R = 10, 830
GRID = 20  # every panel height is a multiple of this so the grid runs across seams

MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG = "#05080F"
PANEL = "#08101C"
GRID_LINE = "#0C1726"
EDGE = "#123A48"
CYAN = "#00E5FF"
MAGENTA = "#FF2E88"
GREEN = "#3DFFA2"
TEXT = "#E6F1FF"
DIM = "#8DA2B8"
FAINT = "#4B6074"

# ----------------------------------------------------------------------------
# content

PROJECTS = [
    {
        "slug": "g923-claude",
        "title": "g923-claude",
        "chip": "v0.6.1 · pypi",
        "thumb": ("image", "g923-claude.jpg"),
        "desc": "Drive Claude Code with a racing wheel. Brake interrupts, gas sends, the "
                "shifter switches models, and force feedback buzzes when Claude needs you. "
                "Ships with a floating HUD and a type-with-the-wheel mode.",
        "tags": ["python", "evdev", "uinput", "pypi"],
    },
    {
        "slug": "ares",
        "title": "ares",
        "chip": "100% local",
        "thumb": ("diagram", "ares"),
        "desc": "A fully local multi-agent system. An orchestrator routes over A2A HTTP to "
                "coder, thinker, runner and Serena agents on Ollama models, with on-disk "
                "mem0 memory, Langfuse tracing, and routing it learns from your ratings.",
        "tags": ["python", "ollama", "a2a", "mem0", "langfuse"],
    },
    {
        "slug": "verisim",
        "title": "verisim",
        "chip": "msc dissertation",
        "thumb": ("image", "verisim.jpg"),
        "desc": "A clinical training sim where the patient, a relative and a nurse are each "
                "an AI agent with its own persona. Tests are gated on patient consent, so "
                "the learner has to de-escalate before they can act. Runs offline.",
        "tags": ["typescript", "convex", "ollama", "agents"],
    },
    {
        "slug": "devdesk",
        "title": "devdesk",
        "chip": "google adk",
        "thumb": ("diagram", "devdesk"),
        "desc": "Multi-agent RAG. A router delegates by explicit tool call to per-project "
                "specialist agents, each grounded in that project's docs through Chroma, "
                "and a deterministic eval with a holdout split keeps routing honest.",
        "tags": ["python", "adk", "gemini", "chroma", "rag"],
    },
]

EXPERIENCE = [
    {
        "role": "BACKEND & FULL-STACK ENGINEER",
        "org": "FUNDEDIN",
        "when": "JUN 2026 - PRESENT",
        "meta": "freelance · remote",
        "desc": "Shipped KYC identity verification gating trader payouts, a brokerage fee "
                "engine handling partial-fill capping and settlement, and AWS SQS outbox "
                "dispatch for order events, in a Dockerised CI/CD codebase with 13+ test modules.",
    },
    {
        "role": "CLINICAL AI / EMR TOOLING",
        "org": "SACOM",
        "when": "PRIVATE · NDA",
        "meta": "ophthalmology",
        "desc": "Ophthalmology workflow modules involving computer vision and voice-assisted "
                "documentation. The code and client data aren't public because of the NDA "
                "and healthcare privacy constraints.",
    },
]

AI_TOOLING = "ollama · google adk · mem0 · langfuse · chroma · hugging face"

# ----------------------------------------------------------------------------
# svg helpers

def esc(s):
    return html.escape(s, quote=True)


def text(x, y, s, size=13, fill=TEXT, weight=None, anchor=None, spacing=None, extra=""):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if extra:
        attrs.append(extra)
    return f'<text {" ".join(attrs)}>{esc(s)}</text>'


def defs():
    return f"""<defs>
  <pattern id="cp-grid" width="{GRID}" height="{GRID}" patternUnits="userSpaceOnUse">
    <path d="M{GRID} 0H0V{GRID}" fill="none" stroke="{GRID_LINE}" stroke-width="1"/>
  </pattern>
  <pattern id="cp-scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="2" fill="#000" fill-opacity="0.22"/>
  </pattern>
  <filter id="cp-glow" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1000" height="1000">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="cp-soft" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1000" height="1000">
    <feGaussianBlur stdDeviation="1.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""


def body(h, top=0, bottom=None):
    """Panel background and the left/right frame between y=top and y=bottom."""
    bottom = h if bottom is None else bottom
    return (
        f'<rect x="{FRAME_L}" y="{top}" width="{FRAME_R - FRAME_L}" height="{bottom - top}" fill="{BG}"/>'
        f'<rect x="{FRAME_L}" y="{top}" width="{FRAME_R - FRAME_L}" height="{bottom - top}" fill="url(#cp-grid)"/>'
        f'<path d="M{FRAME_L} {top}V{bottom}M{FRAME_R} {top}V{bottom}" stroke="{EDGE}" stroke-width="1.5"/>'
    )


def svg(content, h, x0=0, w=W, label=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="{x0} 0 {w} {h}" role="img" aria-label="{esc(label)}" font-family="{MONO}">\n'
        f"{defs()}\n{content}\n</svg>\n"
    )


def write(name, data):
    (OUT / name).write_text(data)
    print(f"{name:28} {len(data.encode()) / 1024:6.1f} KB")


def chamfer(x, y, w, h, c=12):
    """Box with the top-left and bottom-right corners cut."""
    return f"M{x + c} {y}H{x + w}V{y + h - c}L{x + w - c} {y + h}H{x}V{y + c}Z"


def corner_accents(x, y, w, h, c=12, color=CYAN):
    return (
        f'<path d="M{x} {y + c + 14}V{y + c}L{x + c} {y}H{x + c + 14}" fill="none" stroke="{color}" stroke-width="2" filter="url(#cp-soft)"/>'
        f'<path d="M{x + w} {y + h - c - 14}V{y + h - c}L{x + w - c} {y + h}H{x + w - c - 14}" fill="none" stroke="{color}" stroke-width="2" filter="url(#cp-soft)"/>'
    )


def brackets(top=True, h=0):
    """HUD brackets in the margin outside the frame."""
    s = 22
    if top:
        return (
            f'<path d="M2 {s}V2H{s}M{W - s} 2H{W - 2}V{s}" fill="none" stroke="{CYAN}" stroke-width="2.5" filter="url(#cp-soft)"/>'
        )
    return (
        f'<path d="M2 {h - s}V{h - 2}H{s}M{W - s} {h - 2}H{W - 2}V{h - s}" fill="none" stroke="{CYAN}" stroke-width="2.5" filter="url(#cp-soft)"/>'
    )


def prompt(x, y, cmd, size=13):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}">'
        f'<tspan fill="{GREEN}">arjun@agents</tspan><tspan fill="{FAINT}">:</tspan>'
        f'<tspan fill="{CYAN}">~</tspan><tspan fill="{FAINT}">$ </tspan>'
        f'<tspan fill="{DIM}">{esc(cmd)}</tspan></text>'
    )


def fade(begin, end=0.92, out=0.95, dur=8):
    return (
        f'<animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="0;{begin};{min(begin + 0.03, end):.2f};{end};{out}" dur="{dur}s" repeatCount="indefinite"/>'
    )


# ----------------------------------------------------------------------------
# panels

def header():
    h = 340
    graph_paths = [
        "M680 128 C680 170 594 170 594 214",
        "M680 128 C680 170 658 170 658 214",
        "M680 128 C680 170 722 170 722 214",
        "M680 128 C680 170 786 170 786 214",
    ]
    children = [("rag", 594), ("tools", 658), ("memory", 722), ("eval", 786)]
    name_attrs = 'font-size="52" font-weight="800" letter-spacing="5"'
    jitter = (
        '<animateTransform attributeName="transform" type="translate" '
        'values="0 0;0 0;{a} 0;{b} 1;0 0;0 0" keyTimes="0;0.90;0.92;0.94;0.96;1" '
        'dur="7s" repeatCount="indefinite"/>'
    )

    c = [brackets(top=True), body(h, top=10)]
    c.append(f'<path d="M{FRAME_L} 10H{FRAME_R}" stroke="{EDGE}" stroke-width="1.5"/>')
    # status bar
    c.append(f'<rect x="{FRAME_L + 1}" y="11" width="{FRAME_R - FRAME_L - 2}" height="34" fill="{PANEL}"/>')
    c.append(f'<path d="M{FRAME_L} 45H{FRAME_R}" stroke="{EDGE}"/>')
    c.append(f'<text x="30" y="33" font-size="11" letter-spacing="2">'
             f'<tspan fill="{CYAN}">SYS://ARJUN-ASHAD</tspan><tspan fill="{FAINT}"> // NODE:AGENTS</tspan></text>')
    status = "ONLINE · AGENTS 5/5"
    dot_x = 810 - len(status) * (11 * 0.6 + 2) - 12
    c.append(f'<circle cx="{dot_x:.0f}" cy="29" r="4" fill="{GREEN}" filter="url(#cp-soft)">'
             '<animate attributeName="opacity" values="1;0.35;1" dur="2s" repeatCount="indefinite"/></circle>')
    c.append(text(810, 33, status, 11, DIM, anchor="end", spacing=2))

    # identity
    c.append(prompt(40, 92, "whoami"))
    # magenta and cyan copies offset by 2px give a chromatic edge; they jolt apart briefly every 7s
    c.append(f'<g {name_attrs}>'
             f'<text x="38" y="156" fill="{MAGENTA}" fill-opacity="0.75">ARJUN ASHAD{jitter.format(a=-4, b=3)}</text>'
             f'<text x="42" y="156" fill="{CYAN}" fill-opacity="0.75">ARJUN ASHAD{jitter.format(a=4, b=-3)}</text>'
             f'<text x="40" y="156" fill="{TEXT}" filter="url(#cp-soft)">ARJUN ASHAD</text>'
             '</g>')
    lines = [
        "agentic AI · multi-agent systems · applied ML",
        "msc applied ai @ university of warwick",
        "backend engineer @ fundedin",
    ]
    for i, s in enumerate(lines):
        y = 196 + i * 24
        c.append(f'<text x="40" y="{y}" font-size="14"><tspan fill="{CYAN}">&gt;&gt; </tspan>'
                 f'<tspan fill="{TEXT if i == 0 else DIM}">{esc(s)}</tspan></text>')

    # boot log, the old terminal header in one line
    boot = (f'<text x="40" y="306" font-size="12">'
            f'<tspan fill="{GREEN}">[ok]</tspan><tspan fill="{DIM}"> ollama   </tspan>'
            f'<tspan fill="{GREEN}">[ok]</tspan><tspan fill="{DIM}"> langfuse   </tspan>'
            f'<tspan fill="{GREEN}">[ok]</tspan><tspan fill="{DIM}"> agents 5/5   </tspan>'
            f'<tspan fill="{CYAN}">&gt; system ready</tspan>'
            f'<tspan fill="{CYAN}">_<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></tspan>'
            '</text>')
    c.append(f'<path d="M30 280H810" stroke="{EDGE}" stroke-dasharray="2 4"/>')
    c.append(boot)

    # agent graph
    g = [f'<g font-size="11" text-anchor="middle">']
    g.append(f'<circle cx="680" cy="150" r="88" fill="{CYAN}" fill-opacity="0.045"/>')
    g.append(f'<g><path d="{chamfer(616, 94, 128, 34, 8)}" fill="#04222B" stroke="{CYAN}" stroke-width="1.5" filter="url(#cp-soft)"/>'
             f'{text(680, 116, "orchestrator", 12, TEXT)}{fade(0.03)}</g>')
    g.append(f'<g stroke="{CYAN}" stroke-opacity="0.55" stroke-width="1.3" fill="none">'
             + "".join(f'<path d="{p}"/>' for p in graph_paths) + f"{fade(0.20, out=0.95)}</g>")
    for i, (label, cx) in enumerate(children):
        g.append(f'<g><path d="{chamfer(cx - 29, 214, 58, 28, 6)}" fill="{PANEL}" stroke="{EDGE}" stroke-width="1.2"/>'
                 f'{text(cx, 232, label, 11, DIM)}{fade(0.20 + i * 0.04)}</g>')
    pulses = "".join(
        f'<circle r="2.6"><animateMotion dur="1.8s" begin="{i * 0.45:.2f}s" repeatCount="indefinite" path="{p}"/></circle>'
        for i, p in enumerate(graph_paths)
    )
    g.append(f'<g fill="{MAGENTA}" filter="url(#cp-soft)">{pulses}{fade(0.40)}</g>')
    g.append("</g>")
    c.extend(g)
    c.append(text(680, 262, "// agent mesh", 10, FAINT, anchor="middle", spacing=1))

    write("header.svg", svg("\n".join(c), h,
          label="Arjun Ashad. Agentic AI, multi-agent systems, applied ML. MSc Applied AI at the University of Warwick. Backend engineer at FundedIn."))


def link_row():
    h = 100
    boxes = [(30, 246), (297, 246), (564, 246)]
    cards = [
        ("link-linkedin.svg", "LINKEDIN", "in/arjun-ashad-z", "linkedin"),
        ("link-warwick.svg", "MSC APPLIED AI", "university of warwick", "cap"),
        ("link-location.svg", "BASED IN", "coventry, uk", "pin"),
    ]
    for (name, title, sub, icon), (bx, bw), x0 in zip(cards, boxes, (0, 280, 560)):
        by, bh = 20, 64
        c = [body(h)]
        c.append(f'<path d="{chamfer(bx, by, bw, bh, 10)}" fill="{PANEL}" stroke="{EDGE}" stroke-width="1.2"/>')
        c.append(corner_accents(bx, by, bw, bh, 10))
        ix, iy = bx + 30, by + bh / 2
        if icon == "linkedin":
            c.append(f'<rect x="{ix - 12}" y="{iy - 12}" width="24" height="24" rx="4" fill="none" stroke="{CYAN}" stroke-width="1.6" filter="url(#cp-soft)"/>')
            c.append(text(ix, iy + 5, "in", 13, CYAN, weight="700", anchor="middle"))
        elif icon == "cap":
            c.append(f'<g fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-linejoin="round" filter="url(#cp-soft)">'
                     f'<path d="M{ix - 13} {iy - 3}L{ix} {iy - 9}L{ix + 13} {iy - 3}L{ix} {iy + 3}Z"/>'
                     f'<path d="M{ix - 7} {iy}V{iy + 6}C{ix - 7} {iy + 9} {ix + 7} {iy + 9} {ix + 7} {iy + 6}V{iy}"/>'
                     f'<path d="M{ix + 13} {iy - 3}V{iy + 5}"/></g>')
        else:
            c.append(f'<g fill="none" stroke="{CYAN}" stroke-width="1.6" filter="url(#cp-soft)">'
                     f'<path d="M{ix} {iy + 12}C{ix} {iy + 12} {ix - 9} {iy + 2} {ix - 9} {iy - 3}A9 9 0 0 1 {ix + 9} {iy - 3}C{ix + 9} {iy + 2} {ix} {iy + 12} {ix} {iy + 12}Z"/>'
                     f'<circle cx="{ix}" cy="{iy - 3}" r="3"/></g>')
        c.append(text(bx + 56, by + 28, title, 12, CYAN, weight="700", spacing=1.5))
        c.append(text(bx + 56, by + 46, sub, 12, DIM))
        write(name, svg("\n".join(c), h, x0=x0, w=280, label=f"{title.title()}: {sub}"))


def section(slug, index, title, cmd):
    h = 100
    c = [body(h)]
    c.append(f'<text x="40" y="46" font-size="20" font-weight="800" letter-spacing="4">'
             f'<tspan fill="{MAGENTA}">//</tspan><tspan fill="{CYAN}" filter="url(#cp-soft)"> {esc(title)}</tspan></text>')
    c.append(text(800, 46, f"{index:02d}", 12, FAINT, anchor="end", spacing=2))
    c.append(f'<path d="M40 60H800" stroke="{EDGE}"/>')
    end = 40 + len(f"// {title}") * (20 * 0.6 + 4)
    c.append(f'<path d="M40 60H{end:.0f}" stroke="{CYAN}" stroke-width="2" filter="url(#cp-soft)"/>')
    c.append(f'<path d="M{end + 6:.0f} 60h10m6 0h6" stroke="{MAGENTA}" stroke-width="2"/>')
    c.append(prompt(40, 88, cmd, 12))
    write(f"section-{slug}.svg", svg("\n".join(c), h, label=title.title()))


def diagram(kind):
    """800x400 drawing scaled into a card thumbnail."""
    node = f'fill="#04222B" stroke="{CYAN}" stroke-width="2.5" filter="url(#cp-soft)"'
    leaf = f'fill="{PANEL}" stroke="{EDGE}" stroke-width="2"'
    edge = f'stroke="{CYAN}" stroke-opacity="0.65" stroke-width="2.6" fill="none"'
    d = [f'<rect width="800" height="400" fill="{BG}"/><rect width="800" height="400" fill="url(#cp-grid)"/>']
    if kind == "ares":
        rows = [("coder", ":8101"), ("thinker", ":8102"), ("runner", ":8103"), ("serena", ":8104")]
        ys = [52, 128, 204, 280]
        d.append(f'<g {edge}>' + "".join(
            f'<path d="M300 196C365 196 365 {y + 28} 430 {y + 28}"/>' for y in ys) + "</g>")
        d.append(f'<path d="{chamfer(40, 146, 260, 100, 14)}" {node}/>')
        d.append(text(170, 194, "orchestrator", 28, TEXT, anchor="middle"))
        d.append(text(170, 228, "A2A :8100", 22, CYAN, anchor="middle"))
        for (name, port), y in zip(rows, ys):
            d.append(f'<path d="{chamfer(436, y, 324, 56, 10)}" {leaf}/>')
            d.append(text(458, y + 37, name, 26, TEXT))
            d.append(text(740, y + 36, port, 22, FAINT, anchor="end"))
        d.append(text(40, 378, "ollama · mem0 · langfuse", 22, MAGENTA, spacing=1))
    else:
        rows = [("verisim_agent", False), ("ares_agent", False), ("search_all", True)]
        ys = [64, 162, 260]
        d.append(f'<g {edge}>' + "".join(
            f'<path d="M260 196C305 196 305 {y + 28} 344 {y + 28}"/>' for y in ys) + "</g>")
        d.append(f'<g stroke="{MAGENTA}" stroke-opacity="0.7" stroke-width="2.2" fill="none" stroke-dasharray="7 6">'
                 + "".join(f'<path d="M616 {y + 28}C650 {y + 28} 650 200 672 200"/>' for y in ys) + "</g>")
        d.append(f'<path d="{chamfer(40, 146, 220, 100, 14)}" {node}/>')
        d.append(text(150, 194, "router", 28, TEXT, anchor="middle"))
        d.append(text(150, 228, "ADK agent", 22, CYAN, anchor="middle"))
        for (name, dashed), y in zip(rows, ys):
            dash = ' stroke-dasharray="6 5"' if dashed else ""
            d.append(f'<path d="{chamfer(350, y, 266, 56, 10)}" {leaf}{dash}/>')
            d.append(text(372, y + 37, name, 25, DIM if dashed else TEXT))
        d.append(f'<g fill="#1A0714" stroke="{MAGENTA}" stroke-width="2.5" filter="url(#cp-soft)">'
                 '<path d="M680 160V240C680 256 768 256 768 240V160"/><ellipse cx="724" cy="160" rx="44" ry="13"/></g>')
        d.append(f'<path d="M680 186C680 200 768 200 768 186M680 212C680 226 768 226 768 212" fill="none" stroke="{MAGENTA}" stroke-opacity="0.5" stroke-width="2"/>')
        d.append(text(724, 290, "chroma", 22, MAGENTA, anchor="middle"))
        d.append(text(40, 378, "google adk · gemini · chroma", 22, MAGENTA, spacing=1))
    return "".join(d)


def project_cards():
    h = 440
    boxes = [(30, 380), (430, 380)]
    for row in (PROJECTS[0:2], PROJECTS[2:4]):
        for p, (bx, bw), x0 in zip(row, boxes, (0, 420)):
            by, bh = 10, 420
            c = [body(h)]
            c.append(f'<path d="{chamfer(bx, by, bw, bh, 14)}" fill="{PANEL}" stroke="{EDGE}" stroke-width="1.2"/>')
            c.append(corner_accents(bx, by, bw, bh, 14))

            tx, ty, tw, th = bx + 14, by + 14, bw - 28, (bw - 28) // 2
            kind, ref = p["thumb"]
            if kind == "image":
                b64 = base64.b64encode((SRC / ref).read_bytes()).decode()
                inner = f'<image href="data:image/jpeg;base64,{b64}" x="{tx}" y="{ty}" width="{tw}" height="{th}" preserveAspectRatio="xMidYMid slice"/>'
            else:
                inner = f'<svg x="{tx}" y="{ty}" width="{tw}" height="{th}" viewBox="0 0 800 400">{diagram(ref)}</svg>'
            c.append(inner)
            c.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="url(#cp-scan)"/>')
            c.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="none" stroke="{CYAN}" stroke-opacity="0.45"/>')

            y = ty + th + 34
            c.append(f'<text x="{tx}" y="{y}" font-size="18" font-weight="800" letter-spacing="1">'
                     f'<tspan fill="{CYAN}" filter="url(#cp-soft)">{esc(p["title"])}</tspan>'
                     f'<tspan fill="{MAGENTA}" font-size="15"> ↗</tspan></text>')
            chip_w = len(p["chip"]) * 6.6 + 18
            cx = tx + tw - chip_w
            c.append(f'<rect x="{cx}" y="{y - 15}" width="{chip_w}" height="20" fill="#1A0714" stroke="{MAGENTA}" stroke-opacity="0.7"/>')
            c.append(text(cx + chip_w / 2, y - 1, p["chip"], 11, MAGENTA, anchor="middle"))

            for i, line in enumerate(textwrap.wrap(p["desc"], 46)):
                c.append(text(tx, y + 28 + i * 19, line, 12.5, DIM))

            ty2 = by + bh - 26
            x = tx
            for tag in p["tags"]:
                tw2 = len(tag) * 6.6 + 16
                c.append(f'<rect x="{x}" y="{ty2 - 14}" width="{tw2}" height="20" fill="none" stroke="{EDGE}"/>')
                c.append(text(x + tw2 / 2, ty2, tag, 11, CYAN, anchor="middle"))
                x += tw2 + 8

            label = f'{p["title"]}: {p["desc"]}'
            write(f'card-{p["slug"]}.svg', svg("\n".join(c), h, x0=x0, w=420, label=label))


def experience():
    blocks = []
    y = 20
    for e in EXPERIENCE:
        lines = textwrap.wrap(e["desc"], 92)
        top = y
        blocks.append(f'<text x="56" y="{y + 18}" font-size="14" font-weight="800" letter-spacing="1">'
                      f'<tspan fill="{CYAN}">{esc(e["role"])}</tspan>'
                      f'<tspan fill="{MAGENTA}">  @ {esc(e["org"])}</tspan></text>')
        blocks.append(text(800, y + 18, e["when"], 11, DIM, anchor="end", spacing=1.5))
        blocks.append(text(56, y + 40, e["meta"], 12, FAINT))
        for i, line in enumerate(lines):
            blocks.append(text(56, y + 66 + i * 20, line, 13, DIM))
        y = y + 66 + (len(lines) - 1) * 20 + 30
        blocks.append(f'<path d="M40 {top + 4}V{y - 24}" stroke="{CYAN}" stroke-width="2" filter="url(#cp-soft)"/>')
        blocks.append(f'<rect x="36" y="{top + 4}" width="8" height="8" fill="{MAGENTA}"/>')
    h = -(-y // GRID) * GRID
    write("experience.svg", svg(body(h) + "\n" + "\n".join(blocks), h,
          label="Experience. " + " ".join(f'{e["role"].title()} at {e["org"].title()}, {e["when"].lower()}: {e["desc"]}' for e in EXPERIENCE)))


def stack():
    h = 160
    icons = (SRC / "skillicons.svg").read_text()
    inner = icons[icons.index(">", icons.index("<svg")) + 1: icons.rindex("</svg>")]
    iw = 723
    ix = (W - iw) / 2
    c = [body(h)]
    c.append(f'<svg x="{ix}" y="22" width="{iw}" height="48" viewBox="0 0 3856 256">{inner}</svg>')
    c.append(f'<path d="M40 98H800" stroke="{EDGE}" stroke-dasharray="2 4"/>')
    c.append(f'<text x="420" y="132" font-size="13" text-anchor="middle">'
             f'<tspan fill="{MAGENTA}" font-weight="800" letter-spacing="2">AI TOOLING  </tspan>'
             f'<tspan fill="{DIM}">{esc(AI_TOOLING)}</tspan></text>')
    write("stack.svg", svg("\n".join(c), h,
          label="Stack: Python, TypeScript, FastAPI, Flask, PostgreSQL, Docker, AWS, Azure, Linux, PyTorch, TensorFlow, React, Unity. AI tooling: " + AI_TOOLING))


def footer():
    h = 80
    c = [body(h, bottom=50)]
    c.append(f'<path d="M{FRAME_L} 50H{FRAME_R}" stroke="{EDGE}" stroke-width="1.5"/>')
    c.append(brackets(top=False, h=h))
    c.append(prompt(40, 32, "exit", 12))
    c.append(f'<text x="800" y="32" font-size="11" text-anchor="end" letter-spacing="2">'
             f'<tspan fill="{FAINT}">SESSION CLOSED · </tspan><tspan fill="{CYAN}">AGENTS IDLE</tspan>'
             f'<tspan fill="{CYAN}">_<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
    write("footer.svg", svg("\n".join(c), h, label="Session closed."))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    header()
    link_row()
    section("projects", 1, "PROJECTS", "ls ~/projects")
    project_cards()
    section("experience", 2, "EXPERIENCE", "cat ~/experience.log")
    experience()
    section("stack", 3, "STACK", "which --all")
    stack()
    footer()
