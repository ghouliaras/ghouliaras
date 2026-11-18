"""Render the custom profile header (dark + light) as SVG."""
import sys

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

T = {
    "dark": dict(bg1="#0B1120", bg2="#0F1E45", grid="#1E293B", name="#F8FAFC", role="#93C5FD", text="#94A3B8",
                 chip_bg="#111C33", chip_bd="#1E3A8A", chip_tx="#BFDBFE", card="#0B1222", card_bd="#1E293B",
                 kw="#C084FC", var="#93C5FD", fn="#FDE68A", str="#86EFAC", pun="#64748B", accent="#2563EB", glow="#2563EB"),
    "light": dict(bg1="#FFFFFF", bg2="#EAF1FF", grid="#E2E8F0", name="#0F172A", role="#1D4ED8", text="#475569",
                  chip_bg="#FFFFFF", chip_bd="#BFDBFE", chip_tx="#1E40AF", card="#0F172A", card_bd="#1E293B",
                  kw="#C084FC", var="#93C5FD", fn="#FDE68A", str="#86EFAC", pun="#64748B", accent="#2563EB", glow="#93C5FD"),
}


def chip(x, y, label, c):
    w = 30 + len(label) * 7.4
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="15" fill="{c["chip_bg"]}" stroke="{c["chip_bd"]}"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 20}" text-anchor="middle" font-family="{SANS}" font-size="13" '
            f'font-weight="600" fill="{c["chip_tx"]}">{label}</text>'), w


def header(theme):
    c = T[theme]
    W, H = 1200, 340
    chips, x = [], 72
    for label in ["WordPress", "WooCommerce", "Laravel", "AI Automation"]:
        s, w = chip(x, 236, label, c)
        chips.append(s)
        x += w + 10

    code = [
        [("$george", c["var"]), (" = ", c["pun"]), ("new", c["kw"]), (" Developer", c["fn"]), ("(", c["pun"]),
         ("'Patras, GR'", c["str"]), (");", c["pun"])],
        [],
        [("$george", c["var"]), ("->", c["pun"]), ("stack", c["fn"]), ("([", c["pun"])],
        [("    'WordPress'", c["str"]), (", ", c["pun"]), ("'WooCommerce'", c["str"]), (",", c["pun"])],
        [("    'Laravel'", c["str"]), (", ", c["pun"]), ("'AI'", c["str"]), (",", c["pun"])],
        [("]);", c["pun"])],
        [],
        [("$george", c["var"]), ("->", c["pun"]), ("ship", c["fn"]), ("(", c["pun"]), ("secure", c["var"]),
         (": ", c["pun"]), ("true", c["kw"]), (", ", c["pun"]), ("fast", c["var"]), (": ", c["pun"]),
         ("true", c["kw"]), (");", c["pun"])],
    ]
    cx, cy = 742, 70
    lines = []
    for i, toks in enumerate(code):
        spans = "".join(f'<tspan fill="{col}">{txt.replace("&", "&amp;").replace(">", "&gt;")}</tspan>' for txt, col in toks)
        lines.append(f'<text x="{cx + 24}" y="{cy + 64 + i * 22}" font-family="{MONO}" font-size="14" xml:space="preserve">{spans}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="George Chouliaras — Full Stack Developer">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c["bg1"]}"/><stop offset="1" stop-color="{c["bg2"]}"/>
  </linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
    <path d="M32 0H0V32" fill="none" stroke="{c["grid"]}" stroke-width="1"/>
  </pattern>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{c["glow"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="0.55" stop-color="#fff" stop-opacity="0.15"/><stop offset="1" stop-color="#fff" stop-opacity="0.5"/>
  </linearGradient>
  <mask id="gm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <clipPath id="r"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gm)" opacity="0.6"/>
  <circle cx="930" cy="170" r="260" fill="url(#glow)"/>
  <rect x="0" y="{H - 4}" width="{W}" height="4" fill="{c["accent"]}"/>
</g>

<rect x="72" y="62" width="44" height="44" rx="10" fill="{c["accent"]}"/>
<text x="94" y="91" text-anchor="middle" font-family="{SANS}" font-size="18" font-weight="700" fill="#FFFFFF">GC</text>
<text x="130" y="90" font-family="{SANS}" font-size="15" font-weight="600" fill="{c["text"]}" letter-spacing="2">FULL STACK DEVELOPER</text>

<text x="70" y="168" font-family="{SANS}" font-size="56" font-weight="700" fill="{c["name"]}">George Chouliaras</text>
<text x="72" y="208" font-family="{SANS}" font-size="20" fill="{c["text"]}">Fast, secure &amp; maintainable web products — <tspan fill="{c["role"]}" font-weight="600">built to last.</tspan></text>
{"".join(chips)}

<g>
  <rect x="{cx}" y="{cy}" width="390" height="230" rx="12" fill="{c["card"]}" stroke="{c["card_bd"]}"/>
  <circle cx="{cx + 22}" cy="{cy + 22}" r="5" fill="#F87171"/>
  <circle cx="{cx + 40}" cy="{cy + 22}" r="5" fill="#FBBF24"/>
  <circle cx="{cx + 58}" cy="{cy + 22}" r="5" fill="#34D399"/>
  <text x="{cx + 370}" y="{cy + 26}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#64748B">george.php</text>
  <line x1="{cx}" y1="{cy + 40}" x2="{cx + 390}" y2="{cy + 40}" stroke="{c["card_bd"]}"/>
  {"".join(lines)}
</g>
</svg>
'''


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for t in T:
        with open(f"{out}/header-{t}.svg", "w", encoding="utf-8") as f:
            f.write(header(t))
