#!/usr/bin/env python3
"""Genera el hero del perfil de GitHub (versión oscura y clara) en profile/.

Uso: python3 scripts/build.py      (requiere fonttools y brotli)

Dirección de diseño: la marca Quobit (styles/tokens.css del repo quobit).
Lectura: cabecera de perfil para posibles clientes y desarrolladores, en el lenguaje
visual de Quobit; ENERGY 2 / RHYTHM 2 / MOTION 1 (imagen estática).

Decisiones y su porqué (anti-slop R-31):
- Fondo azul marino liso #070d20: es el fondo de quobit.es; liso, porque la profundidad
  la dan las polaroids, no un degradado ni una rejilla.
- Polaroids con nombre a mano: motivo propio de Quobit (sección Equipo de quobit.es).
  Aquí enseñan capturas reales de los productos, no maquetas.
- Sombra solo en las polaroids: son papel sobre una mesa; es la única elevación.
- Ámbar a mano (#f2d58a, «hand» en tokens.css): el único acento. Subraya la frase clave
  y escribe la nota sobre los productos.
- Outfit para el nombre, Geist para el texto y Caveat para lo escrito a mano: las tres
  tipografías de quobit.es.
- Estático: una imagen de perfil se mira en dos segundos; el movimiento no aportaba nada.
"""
from __future__ import annotations

import base64

from svgkit import ROOT, check_contrast, esc, family, font_css, text_width

OUT = ROOT / "profile"
SHOTS = ROOT / "assets" / "shots"
OUT.mkdir(exist_ok=True)

SANS_FB = "'Helvetica Neue', Helvetica, Arial, sans-serif"
HAND_FB = "'Bradley Hand', 'Segoe Print', cursive"

THEMES = {
    "dark": dict(
        bg="#070d20", fg="#eceff7", muted="#a3adc6", ink="#8fb0ff", hand="#f2d58a",
        word="#cde8fe", paper="#e8ebf2", paper_ink="#1c2a55", shadow="#000000", shadow_op=0.55,
    ),
    "light": dict(
        bg="#f1f3f8", fg="#0b1430", muted="#45507a", ink="#1f45c4", hand="#9a6b00",
        word="#1c2a55", paper="#ffffff", paper_ink="#1c2a55", shadow="#1c2a55", shadow_op=0.22,
    ),
}

NAME = "Mauro Serrano"
ROLE = "Full-stack developer, cofundador de Quobit"
LINE1 = "Cojo ideas a medio cocer y las convierto"
LINE2_A = "en algo que alguien abre "
LINE2_B = "cada mañana"
LINE2_C = "."
CTA_A = "Escríbeme: "
CTA_B = "info@quobit.es"
NOTE = ["ya están funcionando,", "pruébalos"]

POLAROIDS = [  # (captura, pie a mano, centro x, centro y, giro)
    ("trainpicker", "TrainPicker", 800, 132, -5),
    ("cardeo", "Cardeo", 1022, 124, 4),
    ("planabc", "PlanABC", 858, 362, 3),
    ("reel", "reel-gallery", 1076, 352, -3),
]
PW, PH, PAD, PHOTO_H = 184, 218, 9, 156

# Logotipo de Quobit (public/marca/quobit-word.svg del repo quobit), viewBox 460×160.
QUOBIT_WORD = ("M49.5 121Q39.3 121 31.2 115.9Q23.1 110.8 18.4 102Q13.7 93.3 13.7 82.3Q13.7 71.1 18.4 62.4Q23.1 53.6 31.2 48.4Q39.3 43.3 49.5 43.3Q57.6 43.3 63.9 46.6Q70.2 49.9 74.1 55.6Q77.9 61.4 78.2 68.7V95.6Q77.9 102.9 74.1 108.7Q70.3 114.4 64 117.7Q57.6 121 49.5 121ZM53.3 102.3Q61.8 102.3 67 96.7Q72.2 91 72.2 82.2Q72.2 76.2 69.9 71.7Q67.5 67.1 63.3 64.6Q59 62 53.3 62Q47.8 62 43.5 64.6Q39.3 67.1 36.8 71.7Q34.4 76.2 34.4 82.2Q34.4 88.1 36.8 92.6Q39.3 97.2 43.5 99.7Q47.8 102.3 53.3 102.3ZM71.2 148V100.7L74.4 82.6L71.2 64.5V44.8H91.3V148ZM139.1 121Q131.2 121 123.6 117.4Q115.9 113.7 110.8 106.5Q105.7 99.2 105.7 88.3V45H125.2V87.6Q125.2 94.3 129.1 98.7Q133.1 103.1 139.1 103.1Q147 103.1 151.4 98.6Q155.8 94.1 155.8 87.6V45H175.3V119.5H155.8V112.3Q153.8 116.7 149.2 118.8Q144.7 121 139.1 121ZM226 121.1Q214.7 121.1 205.7 115.9Q196.6 110.7 191.3 101.8Q186 93 186 82Q186 71 191.3 62.3Q196.6 53.6 205.6 48.4Q214.7 43.2 225.9 43.2Q237.3 43.2 246.3 48.3Q255.4 53.5 260.7 62.2Q266 71 266 82Q266 93 260.7 101.8Q255.4 110.7 246.4 115.9Q237.3 121.1 226 121.1ZM225.9 102.2Q231.7 102.2 236 99.6Q240.4 97.1 242.8 92.5Q245.2 87.9 245.2 82Q245.2 76.2 242.7 71.7Q240.2 67.2 235.9 64.7Q231.7 62.1 225.9 62.1Q220.4 62.1 216 64.7Q211.7 67.3 209.2 71.7Q206.8 76.2 206.8 82.1Q206.8 87.9 209.2 92.5Q211.7 97.1 216 99.6Q220.4 102.2 225.9 102.2ZM318.7 121Q310.6 121 304.1 117.6Q297.6 114.2 293.7 108.4Q289.9 102.5 289.5 95.2V68.7Q289.9 61.4 293.8 55.6Q297.7 49.9 304.2 46.6Q310.7 43.3 318.7 43.3Q329 43.3 337.2 48.4Q345.4 53.6 350.1 62.4Q354.8 71.1 354.8 82.3Q354.8 93.3 350.1 102Q345.4 110.8 337.2 115.9Q329 121 318.7 121ZM277.2 119.5V14.9H297.5V63.2L294.1 81.2L297.3 99.4V119.5ZM315.2 102.3Q320.8 102.3 325 99.7Q329.2 97.2 331.7 92.6Q334.1 88.1 334.1 82.2Q334.1 76.2 331.7 71.7Q329.2 67.1 325 64.6Q320.7 62 315.2 62Q309.6 62 305.3 64.6Q301 67.1 298.6 71.7Q296.3 76.2 296.3 82.2Q296.3 88.1 298.6 92.7Q301 97.2 305.3 99.8Q309.6 102.3 315.2 102.3ZM366.8 119.5V44.8H387.2V119.5ZM377 32.9Q372.1 32.9 368.9 29.5Q365.6 26.2 365.6 21.3Q365.6 16.4 368.9 13Q372.1 9.7 377 9.7Q382.1 9.7 385.2 13Q388.4 16.4 388.4 21.3Q388.4 26.2 385.2 29.5Q382.1 32.9 377 32.9ZM408.9 29.9 429 24.9V45.9H447V62.9H429V97.1Q429 101.4 433.6 101.4H447V119.5H427.6Q419.1 119.5 414 113.8Q408.9 108.2 408.9 97.8V62.9H397V45.9H408.9Z")


def photo_b64(name: str) -> str:
    return base64.b64encode((SHOTS / f"{name}.jpg").read_bytes()).decode()


def polaroid(i, shot, caption, cx, cy, rot, t, hand):
    x, y = cx - PW / 2, cy - PH / 2
    pw = PW - 2 * PAD
    return f'''
  <g transform="rotate({rot} {cx} {cy})" filter="url(#lift)">
    <rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="3" fill="{t["paper"]}"/>
    <clipPath id="ph{i}"><rect x="{x + PAD}" y="{y + PAD}" width="{pw}" height="{PHOTO_H}" rx="1.5"/></clipPath>
    <image href="data:image/jpeg;base64,{photo_b64(shot)}" x="{x + PAD}" y="{y + PAD}" width="{pw}" height="{PHOTO_H}" preserveAspectRatio="xMidYMid slice" clip-path="url(#ph{i})"/>
    <text x="{cx}" y="{y + PH - 17}" text-anchor="middle" font-family="{hand}" font-size="29" fill="{t["paper_ink"]}">{esc(caption)}</text>
  </g>'''


def hero(name: str, t: dict) -> None:
    W, H = 1200, 490
    outfit, geist, geistm, hand = (family("Outfit", SANS_FB), family("Geist", SANS_FB),
                                   family("GeistMedium", SANS_FB), family("Caveat", HAND_FB))
    x0 = 72

    # medidas reales para el subrayado a mano
    s_line = 23
    ux0 = x0 + text_width("Geist", LINE2_A, s_line)
    ux1 = ux0 + text_width("GeistMedium", LINE2_B, s_line)
    uy = 332

    css = font_css({
        "Outfit": NAME,
        "Geist": ROLE + LINE1 + LINE2_A + LINE2_C + CTA_A + CTA_B,
        "GeistMedium": LINE2_B,
        "Caveat": "".join(NOTE) + "".join(p[1] for p in POLAROIDS),
    })

    pols = "".join(polaroid(i, *p, t, hand) for i, p in enumerate(POLAROIDS))

    # nota a mano con flecha hacia las polaroids
    nx, ny = 486, 428
    note = (f'<g transform="rotate(-4 {nx} {ny})" font-family="{hand}" font-size="30" fill="{t["hand"]}">'
            f'<text x="{nx}" y="{ny}">{esc(NOTE[0])}</text><text x="{nx + 34}" y="{ny + 30}">{esc(NOTE[1])}</text></g>')
    arrow = (f'<path d="M654 436 C 692 430, 724 414, 748 388" fill="none" stroke="{t["hand"]}" stroke-width="2.6" stroke-linecap="round"/>'
             f'<path d="M734 389 L 749 386 L 747 402" fill="none" stroke="{t["hand"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    underline = (f'<path d="M{ux0 - 3:.1f} {uy + 10} C {ux0 + (ux1 - ux0) * 0.3:.1f} {uy + 5}, {ux0 + (ux1 - ux0) * 0.7:.1f} {uy + 4}, {ux1 + 4:.1f} {uy + 8}" '
                 f'fill="none" stroke="{t["hand"]}" stroke-width="3.4" stroke-linecap="round"/>')

    alt = (f"{NAME}. {ROLE}. {LINE1} {LINE2_A}{LINE2_B}. Polaroids con capturas de TrainPicker, Cardeo, "
           f"PlanABC y reel-gallery, con la nota a mano: {' '.join(NOTE)}.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">{esc(NAME)}, {esc(ROLE)}</title>
<desc id="d">{esc(alt)}</desc>
<defs>
  <style>{css}</style>
  <filter id="lift" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="{t["shadow"]}" flood-opacity="{t["shadow_op"]}"/>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{t["bg"]}"/>
  <path d="{QUOBIT_WORD}" fill="{t["word"]}" transform="translate({x0 - 4} 64) scale(0.2)"/>
  <text x="{x0 - 3}" y="174" font-family="{outfit}" font-size="76" letter-spacing="-1.5" fill="{t["fg"]}">{esc(NAME)}</text>
  <text x="{x0}" y="224" font-family="{geist}" font-size="25" fill="{t["fg"]}">{esc(ROLE)}</text>
  <text font-family="{geist}" font-size="{s_line}" fill="{t["muted"]}">
    <tspan x="{x0}" y="298">{esc(LINE1)}</tspan>
    <tspan x="{x0}" y="{uy}">{esc(LINE2_A)}<tspan font-family="{geistm}" fill="{t["fg"]}">{esc(LINE2_B)}</tspan>{esc(LINE2_C)}</tspan>
  </text>
  {underline}
  <text x="{x0}" y="394" font-family="{geist}" font-size="21" fill="{t["muted"]}">{esc(CTA_A)}<tspan fill="{t["ink"]}">{esc(CTA_B)}</tspan></text>
  {pols}
  {note}
  {arrow}
</g>
</svg>
'''
    (OUT / f"hero-{name}.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    informe = []
    for name, t in THEMES.items():
        informe += check_contrast([
            (f"{name} nombre", t["fg"], t["bg"], True),
            (f"{name} texto", t["muted"], t["bg"], False),
            (f"{name} correo", t["ink"], t["bg"], False),
            (f"{name} nota a mano (30 px)", t["hand"], t["bg"], True),
            (f"{name} pie de polaroid", t["paper_ink"], t["paper"], True),
        ])
        hero(name, t)
    print("\n".join(informe))
    print("ok ->", OUT)


if __name__ == "__main__":
    main()
