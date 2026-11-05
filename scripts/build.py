#!/usr/bin/env python3
"""Genera el hero y las tarjetas de proyecto del perfil de GitHub (versión oscura y clara).

Uso: python3 scripts/build.py   → escribe los SVG en profile/
Solo librería estándar. Colores tomados de los tokens de Quobit (styles/tokens.css).
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "profile"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(
        bg="#070d20", bg2="#0c1530", fg="#eceff7", muted="#a3adc6", dim="#7c88a8",
        accent="#2f5bea", ink="#8fb0ff", cyan="#3cc6f5", hand="#f2d58a", ok="#5dd3a0",
        line="#ffffff", line_op="0.07", chip="#111c3d", chip_line="#ffffff", chip_op="0.10",
        glow_op="0.55", term="#0a1229", term_line="#ffffff", term_op="0.10",
    ),
    "light": dict(
        bg="#f5f7fc", bg2="#ffffff", fg="#0b1430", muted="#45507a", dim="#6b7596",
        accent="#2f5bea", ink="#2f5bea", cyan="#0f9fd6", hand="#d9a21b", ok="#1f9d6b",
        line="#0b1430", line_op="0.06", chip="#ffffff", chip_line="#0b1430", chip_op="0.12",
        glow_op="0.22", term="#0a1229", term_line="#0b1430", term_op="0.0",
    ),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
CH = 0.602  # ancho medio de carácter monoespaciado (em)

REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def chips(items, x, y, t, size=14, gap=10, padx=12, h=30):
    out, cx = [], x
    for it in items:
        w = len(it) * size * CH + padx * 2
        out.append(
            f'<g class="fade" style="animation-delay:{0.9 + 0.08 * len(out):.2f}s">'
            f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{t["chip"]}" '
            f'stroke="{t["chip_line"]}" stroke-opacity="{t["chip_op"]}"/>'
            f'<text x="{cx + w/2:.1f}" y="{y + h/2 + size*0.36:.1f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="{size}" fill="{t["muted"]}">{escape(it)}</text></g>'
        )
        cx += w + gap
    return "".join(out)


def terminal(t, x, y, w, h):
    """Tarjeta tipo terminal con líneas que se 'escriben' en secuencia."""
    size, lh, padx = 15, 25, 22
    lines = [
        ("cmd", "whoami"),
        ("out", [("mauro", "#eceff7"), (" · full-stack @ ", "#a3adc6"), ("quobit.es", "#8fb0ff")]),
        ("cmd", "ls proyectos/"),
        ("out", [("trainpicker/  cardeo/  planabc/  reel-gallery/", "#3cc6f5")]),
        ("cmd", "cat trainpicker/README"),
        ("out", [("Avisa cuando se libera plaza en un", "#a3adc6")]),
        ("out", [("AVE completo. En producción, gratis.", "#a3adc6")]),
        ("cmd", "./contactar --proyecto"),
        ("out", [("✓ ", "#5dd3a0"), ("info@quobit.es", "#eceff7"), (" · respuesta en 1–2 días", "#a3adc6")]),
    ]
    parts = [
        f'<g class="rise">'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{t["term"]}" '
        f'stroke="{t["term_line"]}" stroke-opacity="{t["term_op"] or 0}"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="url(#termGlow)"/>'
        f'<path d="M{x} {y+44}H{x+w}" stroke="#ffffff" stroke-opacity="0.07"/>'
    ]
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        parts.append(f'<circle cx="{x + 24 + i*20}" cy="{y + 22}" r="6" fill="{c}" opacity="0.9"/>')
    parts.append(
        f'<text x="{x + w/2}" y="{y + 27}" text-anchor="middle" font-family="{MONO}" font-size="13" '
        f'fill="#7c88a8">mauro@quobit — zsh</text>'
    )
    defs = []
    delay = 1.2
    ty = y + 44 + 34
    for i, (kind, content) in enumerate(lines):
        if kind == "cmd":
            text = content
            tw = (2 + len(text)) * size * CH + 4
            dur = 0.035 * len(text) + 0.15
            cid = f"type{i}"
            defs.append(
                f'<clipPath id="{cid}"><rect class="type" x="{x + padx + 2*size*CH:.1f}" y="{ty - 18}" '
                f'width="{tw:.1f}" height="{lh}" style="animation-delay:{delay:.2f}s;animation-duration:{dur:.2f}s"/></clipPath>'
            )
            parts.append(
                f'<g class="fade" style="animation-delay:{delay - 0.15:.2f}s">'
                f'<text x="{x + padx}" y="{ty}" font-family="{MONO}" font-size="{size}" fill="#5dd3a0">❯</text></g>'
                f'<text x="{x + padx + 2*size*CH:.1f}" y="{ty}" font-family="{MONO}" font-size="{size}" '
                f'fill="#eceff7" clip-path="url(#{cid})">{escape(text)}</text>'
            )
            delay += dur + 0.25
        else:
            spans = "".join(f'<tspan fill="{col}">{escape(s)}</tspan>' for s, col in content)
            parts.append(
                f'<g class="fade" style="animation-delay:{delay:.2f}s">'
                f'<text x="{x + padx}" y="{ty}" font-family="{MONO}" font-size="{size}">{spans}</text></g>'
            )
            delay += 0.18
            # deja un respiro tras cada bloque de salida
            if i + 1 < len(lines) and lines[i + 1][0] == "cmd":
                delay += 0.25
                ty += 8
        ty += lh
    # prompt final con cursor parpadeante
    parts.append(
        f'<g class="fade" style="animation-delay:{delay:.2f}s">'
        f'<text x="{x + padx}" y="{ty + 8}" font-family="{MONO}" font-size="{size}" fill="#5dd3a0">❯</text>'
        f'<rect class="cursor" x="{x + padx + 2*size*CH:.1f}" y="{ty + 8 - 14}" width="9" height="18" rx="1.5" fill="#8fb0ff"/></g>'
    )
    parts.append("</g>")
    return "".join(defs), "".join(parts)


def hero(name, t):
    W, H = 1200, 440
    tdefs, term = terminal(t, 680, 52, 468, 336)
    hand_y = 300
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Mauro Serrano — Full-stack developer, cofundador de Quobit</title>
<desc id="desc">Desarrollador full-stack en Sevilla. Webs, apps, automatizaciones e IA aplicada. Autor de TrainPicker y reel-gallery.</desc>
<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0H0V40" fill="none" stroke="{t["line"]}" stroke-opacity="{t["line_op"]}"/>
  </pattern>
  <radialGradient id="glowA" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow_op"]}"/>
    <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowB" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{t["cyan"]}" stop-opacity="{float(t["glow_op"]) * 0.6:.2f}"/>
    <stop offset="1" stop-color="{t["cyan"]}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="termGlow" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#2f5bea" stop-opacity="0.16"/>
    <stop offset="0.6" stop-color="#2f5bea" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fadeGrid" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0.25"/>
  </linearGradient>
  <mask id="gridMask"><rect width="{W}" height="{H}" fill="url(#fadeGrid)"/></mask>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  {tdefs}
</defs>
<style>
  .fade {{ animation: fade .5s ease-out both; }}
  .rise {{ animation: rise .9s cubic-bezier(.22,1,.36,1) both; }}
  .type {{ transform-box: fill-box; transform-origin: left center; animation-name: type; animation-timing-function: steps(18, end); animation-fill-mode: both; }}
  .cursor {{ animation: blink 1.1s steps(1, end) infinite; }}
  .pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-out infinite; }}
  .drift {{ animation: drift 14s ease-in-out infinite alternate; }}
  .hand {{ stroke-dasharray: 340; stroke-dashoffset: 0; animation: draw 1s .9s cubic-bezier(.22,1,.36,1) both; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes type {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @keyframes pulse {{ 0% {{ transform: scale(1); opacity: .55; }} 100% {{ transform: scale(2.6); opacity: 0; }} }}
  @keyframes drift {{ from {{ transform: translate(0,0); }} to {{ transform: translate(-60px, 30px); }} }}
  @keyframes draw {{ from {{ stroke-dashoffset: 340; }} to {{ stroke-dashoffset: 0; }} }}
  {REDUCED}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{t["bg"]}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridMask)"/>
  <g class="drift"><ellipse cx="980" cy="60" rx="420" ry="300" fill="url(#glowA)"/></g>
  <ellipse cx="120" cy="460" rx="380" ry="220" fill="url(#glowB)"/>

  <!-- etiqueta -->
  <g class="fade" style="animation-delay:.1s">
    <rect x="64" y="56" width="352" height="34" rx="17" fill="{t["chip"]}" stroke="{t["chip_line"]}" stroke-opacity="{t["chip_op"]}"/>
    <circle class="pulse" cx="86" cy="73" r="5" fill="{t["ok"]}"/>
    <circle cx="86" cy="73" r="5" fill="{t["ok"]}"/>
    <text x="102" y="78" font-family="{MONO}" font-size="14" fill="{t["muted"]}">Disponible para proyectos · Sevilla</text>
  </g>

  <!-- nombre y rol -->
  <g class="fade" style="animation-delay:.2s">
    <text x="62" y="170" font-family="{SANS}" font-size="74" font-weight="700" letter-spacing="-2" fill="{t["fg"]}">Mauro Serrano</text>
  </g>
  <g class="fade" style="animation-delay:.35s">
    <text x="64" y="218" font-family="{SANS}" font-size="26" font-weight="500" fill="{t["fg"]}" fill-opacity="0.92">Full-stack developer · cofundador de <tspan fill="{t["ink"]}" font-weight="700">Quobit</tspan></text>
  </g>

  <!-- frase -->
  <g class="fade" style="animation-delay:.5s">
    <text font-family="{SANS}" font-size="20" fill="{t["muted"]}">
      <tspan x="64" y="268">Cojo ideas a medio cocer y las convierto en software</tspan>
      <tspan x="64" y="{hand_y - 4 + 2}">que alguien abre <tspan fill="{t["fg"]}" font-weight="600">cada mañana</tspan>.</tspan>
    </text>
  </g>
  <path class="hand" d="M219 {hand_y + 8} C 250 {hand_y + 3}, 300 {hand_y + 2}, 340 {hand_y + 6}" fill="none" stroke="{t["hand"]}" stroke-width="3.2" stroke-linecap="round"/>

  {chips(["TypeScript", "Next.js", "Python", "Java", "Flutter", "IA"], 64, 340, t)}

  {term}
</g>
</svg>
'''
    (OUT / f"hero-{name}.svg").write_text(svg, encoding="utf-8")


# ---------- tarjetas de proyecto ----------

Q_PATH = ("M49.5 121Q39.3 121 31.2 115.9Q23.1 110.8 18.4 102Q13.7 93.3 13.7 82.3Q13.7 71.1 18.4 62.4Q23.1 53.6 31.2 48.4"
          "Q39.3 43.3 49.5 43.3Q57.6 43.3 63.9 46.6Q70.2 49.9 74.1 55.6Q77.9 61.4 78.2 68.7V95.6Q77.9 102.9 74.1 108.7"
          "Q70.3 114.4 64 117.7Q57.6 121 49.5 121ZM53.3 102.3Q61.8 102.3 67 96.7Q72.2 91 72.2 82.2Q72.2 76.2 69.9 71.7"
          "Q67.5 67.1 63.3 64.6Q59 62 53.3 62Q47.8 62 43.5 64.6Q39.3 67.1 36.8 71.7Q34.4 76.2 34.4 82.2Q34.4 88.1 36.8 92.6"
          "Q39.3 97.2 43.5 99.7Q47.8 102.3 53.3 102.3ZM71.2 148V100.7L74.4 82.6L71.2 64.5V44.8H91.3V148Z")


def logo_trainpicker(x, y, s):
    k = s / 64
    return (f'<g transform="translate({x} {y}) scale({k})"><rect width="64" height="64" rx="14" fill="#6b1f7a"/>'
            '<path d="M32 9 C22.6 9 15 16.6 15 26 C15 38.5 32 55 32 55 C32 55 49 38.5 49 26 C49 16.6 41.4 9 32 9 Z" fill="#fff"/>'
            '<rect x="24" y="17" width="16" height="17" rx="5" fill="#6b1f7a"/><rect x="27" y="20" width="10" height="6" rx="1.5" fill="#fff"/>'
            '<circle cx="28.5" cy="30" r="1.6" fill="#ffd34d"/><circle cx="35.5" cy="30" r="1.6" fill="#ffd34d"/></g>')


def logo_reel(x, y, s):
    k = s / 64
    tiles = [(10, 10, 20, 26, "#3cc6f5"), (34, 10, 20, 16, "#8fb0ff"), (10, 40, 20, 14, "#cfe0ff"), (34, 30, 20, 24, "#2f5bea")]
    r = "".join(f'<rect x="{a}" y="{b}" width="{c}" height="{d}" rx="3.5" fill="{f}"/>' for a, b, c, d, f in tiles)
    return f'<g transform="translate({x} {y}) scale({k})"><rect width="64" height="64" rx="14" fill="#0c1530"/>{r}</g>'


def logo_quobit(x, y, s):
    k = s / 64
    return (f'<g transform="translate({x} {y}) scale({k})"><rect width="64" height="64" rx="14" fill="#2f5bea"/>'
            f'<path d="{Q_PATH}" fill="#ffffff" transform="translate(11 -16) scale(0.5)"/></g>')


def logo_cardeo(x, y, s):
    # favicon de cardeo.quobit.es (azulejo andaluz)
    k = s / 52
    return (f'<g transform="translate({x} {y}) scale({k})"><rect width="52" height="52" rx="12" fill="#1B4B7A"/>'
            '<polygon points="26,7 31,17 42,14 38,25 48,26 38,27 42,38 31,35 26,45 21,35 10,38 14,27 4,26 14,25 10,14 21,17" fill="#F7F2E9"/>'
            '<circle cx="26" cy="26" r="5" fill="#B44F27"/></g>')


def logo_planabc(x, y, s):
    # fichas A (hecha), B (libre), C (planeada) del logotipo de PlanABC
    k = s / 64
    f = f"font-family=\"{SANS}\" font-size=\"15\" font-weight=\"900\" text-anchor=\"middle\""
    return (f'<g transform="translate({x} {y}) scale({k})"><rect width="64" height="64" rx="14" fill="#172030"/>'
            f'<rect x="2.5" y="21.5" width="19" height="19" rx="4.5" fill="#2fd38f"/><text x="12" y="36.5" {f} fill="#0b3d2b">A</text>'
            f'<g transform="rotate(-6 32 31)"><rect x="23.3" y="22.3" width="17.4" height="17.4" rx="4" fill="#172030" stroke="#fff" stroke-width="1.6"/>'
            f'<text x="32" y="36.5" {f} fill="#fff">B</text></g>'
            f'<g transform="rotate(6 52 31)"><rect x="42.5" y="21.5" width="19" height="19" rx="4.5" fill="#4c7bff"/><text x="52" y="36.5" {f} fill="#fff">C</text></g></g>')


PROJECTS = [
    dict(slug="trainpicker", logo=logo_trainpicker, title="TrainPicker", kicker="Bot de Telegram · en producción",
         desc=["Vigila trenes completos de Renfe y Ouigo y te avisa", "en cuanto se libera una plaza, con la compra rellenada."],
         tags=["Python", "Telegram", "Docker"], link="trainpicker.quobit.es"),
    dict(slug="cardeo", logo=logo_cardeo, title="Cardeo", kicker="Juego multijugador · en producción",
         desc=["Cartas online para jugar con la peña que tienes delante:", "salas en tiempo real y cinco modos de juego."],
         tags=["React", "Socket.IO", "Node.js"], link="cardeo.quobit.es"),
    dict(slug="planabc", logo=logo_planabc, title="PlanABC", kicker="App para parejas (PWA) · en producción",
         desc=["27 planes en pareja, uno por cada letra del abecedario,", "en el orden que os apetezca."],
         tags=["Next.js", "Spring Boot", "PostgreSQL"], link="planabc.quobit.es"),
    dict(slug="reel-gallery", logo=logo_reel, title="reel-gallery", kicker="Paquete npm · open source",
         desc=["Galería mosaico animada con scroll para fotos, vídeos", "y Live Photos, con visor 3D opcional."],
         tags=["TypeScript", "three.js", "React · Vue"], link="ver demo"),
]


def card(p, name, t):
    W, H = 480, 218
    tags = chips(p["tags"], 24, 170, t, size=12, gap=8, padx=10, h=24).replace('class="fade"', 'class="x"')
    desc = "".join(f'<tspan x="24" y="{124 + i*22}">{escape(l)}</tspan>' for i, l in enumerate(p["desc"]))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(p["title"])}: {escape(" ".join(p["desc"]))}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{0.14 if name == "dark" else 0.06}"/><stop offset=".55" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="{t["bg2"] if name == "light" else t["bg"]}" stroke="{t["chip_line"]}" stroke-opacity="{t["chip_op"]}"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="url(#g)"/>
{p["logo"](24, 24, 48)}
<text x="86" y="45" font-family="{SANS}" font-size="21" font-weight="700" fill="{t["fg"]}">{escape(p["title"])}</text>
<text x="86" y="66" font-family="{MONO}" font-size="12" fill="{t["dim"]}">{escape(p["kicker"])}</text>
<text font-family="{SANS}" font-size="15" fill="{t["muted"]}">{desc}</text>
{tags}
<text x="{W-24}" y="187" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["ink"]}">{escape(p["link"])} ↗</text>
</svg>
'''
    (OUT / f"card-{p['slug']}-{name}.svg").write_text(svg, encoding="utf-8")


for name, t in THEMES.items():
    hero(name, t)
    for p in PROJECTS:
        card(p, name, t)
print("ok →", OUT)
