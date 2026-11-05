#!/usr/bin/env python3
"""Genera las piezas visuales del perfil de GitHub en profile/: hero, fichas de proyecto y botones.

Uso: python3 scripts/build.py      (requiere fonttools y brotli: scripts/requirements.txt)

Dirección de diseño: la marca Quobit (repo quobit: styles/tokens.css, components/Hero,
components/Button y el prototipo v10 de docs/prototype).
Lectura: cabecera de perfil para posibles clientes y desarrolladores, en el lenguaje
visual de quobit.es; ENERGY 2 / RHYTHM 2 / MOTION 1 (imágenes estáticas).

Decisiones y su porqué (anti-slop R-31):
- Solo tema oscuro: Quobit no tiene tema claro (tokens.css define uno), y el azul marino
  es su identidad; en el modo claro de GitHub se ven como piezas de la marca.
- Hero calcado de la estructura del de quobit.es: etiqueta con chincheta, titular en Outfit
  con el subrayado a mano en azul de la marca, entradilla y la Q 3D con su halo azul.
  El halo y el leve degradado del fondo son los de Hero.module.css: marca, no decoración.
- Sin botones dentro del hero: en una imagen no se pueden pulsar. Los botones de verdad
  van justo debajo, como enlaces.
- Fichas de proyecto como las de «Lo que ya funciona» del prototipo: captura en un marco de
  ventana, línea de estado y etiqueta a mano. Las capturas son las webs reales a 1280×800,
  enteras, sin recortar.
- Ritmo variado: ficha ancha, dos medias y otra ancha invertida, en vez de cuatro iguales.
- Iconos Phosphor: los que usa quobit.es (sprite del prototipo).
- Verde de estado (--ok) solo en el punto «en producción»: es un estado real comprobado.
"""
from __future__ import annotations

import base64

from svgkit import (ROOT, check_contrast, esc, family, font_css, icon_path, text_width,
                    wrap)

OUT = ROOT / "profile"
ASSETS = ROOT / "assets"
OUT.mkdir(exist_ok=True)

SANS_FB = "'Helvetica Neue', Helvetica, Arial, sans-serif"
HAND_FB = "'Bradley Hand', 'Segoe Print', cursive"
F_TITLE, F_BODY, F_MED, F_HAND = (family("OutfitSemi", SANS_FB), family("Geist", SANS_FB),
                                  family("GeistMedium", SANS_FB), family("Caveat", HAND_FB))

# tokens.css de Quobit
T = dict(bg="#070d20", surface="#0c1530", surface2="#111c3d", fg="#eceff7", muted="#a3adc6",
         dim="#7c88a8", accent="#2f5bea", ink="#8fb0ff", cyan="#3cc6f5", pale="#cfe0ff",
         ok="#5dd3a0", word="#cde8fe")


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def word_path() -> str:
    import re
    return re.search(r' d="([^"]+)"', (ASSETS / "brand" / "quobit-word.svg").read_text()).group(1)


def icon(name, x, y, size, color):
    k = size / 256
    return f'<path d="{icon_path(name)}" fill="{color}" transform="translate({x:.1f} {y:.1f}) scale({k:.4f})"/>'


def hand_underline(x, baseline, w, color, stroke=5):
    """El subrayado a mano del hero de quobit.es (M3 13c38-7 92-10 140-6 22 2 38 4 54 7), a escala."""
    k = w / 194
    y = baseline + 12
    return (f'<path d="M{x:.1f} {y:.1f} c{38 * k:.1f} -7 {92 * k:.1f} -10 {140 * k:.1f} -6 '
            f'{22 * k:.1f} 2 {38 * k:.1f} 4 {54 * k:.1f} 7" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round"/>')


def svg_doc(w, h, title, desc, css, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d">\n<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n'
            f'<defs><style>{css}</style>{defs}</defs>\n{body}\n</svg>\n')


# ---------------------------------------------------------------- hero

def hero():
    W, H, x0 = 1200, 500, 72
    kicker = "Full-stack developer en Sevilla"
    l1, l2a, l2b = "Mauro Serrano,", "cofundador de ", "Quobit."
    lede = "Cojo ideas a medio cocer y las convierto en algo que alguien abre cada mañana."
    size = 64
    # el titular no debe invadir el logo
    size = min(size, 600 / (text_width("OutfitSemi", l2a + l2b, 1)))
    lede_lines = wrap("Geist", lede, 21, 520)

    ux = x0 + text_width("OutfitSemi", l2a, size)
    uw = text_width("OutfitSemi", l2b[:-1], size)
    b1, b2 = 240, 240 + size * 1.08
    ly = b2 + 66

    css = font_css({"OutfitSemi": l1 + l2a + l2b, "GeistMedium": kicker, "Geist": lede})
    defs = (f'<radialGradient id="halo" cx="925" cy="245" r="400" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{T["accent"]}" stop-opacity="0.30"/>'
            f'<stop offset="0.72" stop-color="{T["accent"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="bgfade" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#081027"/><stop offset="0.85" stop-color="{T["bg"]}"/></linearGradient>'
            f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#bgfade)"/>
<rect width="{W}" height="{H}" fill="url(#halo)"/>
<path d="{word_path()}" fill="{T["word"]}" transform="translate({x0 - 3} 46) scale(0.19)"/>
{icon("map-pin", x0, 138, 22, T["ink"])}
<text x="{x0 + 30}" y="156" font-family="{F_MED}" font-size="19" fill="{T["muted"]}">{esc(kicker)}</text>
<text font-family="{F_TITLE}" font-size="{size:.1f}" letter-spacing="-0.5" fill="{T["fg"]}">
  <tspan x="{x0 - 3}" y="{b1}">{esc(l1)}</tspan>
  <tspan x="{x0 - 3}" y="{b2:.1f}">{esc(l2a + l2b)}</tspan>
</text>
{hand_underline(ux - 3, b2, uw + 6, T["accent"])}
<text font-family="{F_BODY}" font-size="21" fill="{T["muted"]}">{"".join(f'<tspan x="{x0}" y="{ly + i * 31:.1f}">{esc(l)}</tspan>' for i, l in enumerate(lede_lines))}</text>
<image href="{b64(ASSETS / "brand" / "q-3d.webp", "image/webp")}" x="705" y="25" width="450" height="450"/>
</g>'''
    desc = f"{kicker}. {l1} {l2a}{l2b} {lede} A la derecha, el logotipo 3D de Quobit."
    (OUT / "hero.svg").write_text(svg_doc(W, H, f"{l1} {l2a}{l2b}", desc, css, body, defs), encoding="utf-8")


# ---------------------------------------------------------------- fichas de proyecto

PROJECTS = {
    "trainpicker": dict(
        title="TrainPicker", kind="Bot de Telegram", status="En producción",
        desc="Vigila trenes completos de Renfe y Ouigo cada pocos segundos y te escribe en cuanto "
             "alguien anula su billete, con un botón que abre la compra ya rellenada.",
        stack="Python · API de Telegram · Docker", host="trainpicker.quobit.es",
        sticker="gratis, pruébalo"),
    "cardeo": dict(
        title="Cardeo", kind="Juego multijugador", status="En producción",
        desc="Cartas online para jugar con la peña que tienes delante: cada uno desde su móvil, "
             "con salas en tiempo real y cinco modos de juego.",
        stack="React · Socket.IO · Node.js", host="cardeo.quobit.es"),
    "planabc": dict(
        title="PlanABC", kind="App para parejas", status="En producción",
        desc="27 planes, uno por cada letra del abecedario, en el orden que os apetezca. "
             "Se instala en el móvil como una app.",
        stack="Next.js · Spring Boot · PostgreSQL", host="planabc.quobit.es"),
    "reel": dict(
        title="reel-gallery", kind="Paquete npm", status="Publicado en npm",
        desc="Galería mosaico que se anima con el scroll, para fotos, vídeos y Live Photos, "
             "con un visor 3D opcional. Para React, Vue, Svelte, Angular o como Web Component.",
        stack="TypeScript · three.js", host="Ver la demo",
        sticker="código abierto"),
}


def window_frame(x, y, w, shot, cid):
    bar = 30
    ih = w * 0.625
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{bar + ih:.1f}" rx="14" fill="{T["surface"]}" '
            f'stroke="#ffffff" stroke-opacity="0.09"/>'
            + "".join(f'<circle cx="{x + 18 + i * 14}" cy="{y + bar / 2}" r="4" fill="{T["dim"]}" opacity="0.55"/>' for i in range(3))
            + f'<clipPath id="{cid}"><path d="M{x} {y + bar}H{x + w}V{y + bar + ih - 14:.1f}'
              f'a14 14 0 0 1 -14 14H{x + 14}a14 14 0 0 1 -14 -14Z"/></clipPath>'
              f'<image href="{b64(ASSETS / "shots" / f"{shot}.jpg", "image/jpeg")}" x="{x}" y="{y + bar}" '
              f'width="{w}" height="{ih:.1f}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>'), bar + ih


def sticker(x, y, text, rot):
    w = text_width("Caveat", text, 26) + 28
    return (f'<g transform="rotate({rot} {x + w / 2:.1f} {y + 19})"><rect x="{x}" y="{y}" width="{w:.1f}" height="38" rx="6" '
            f'fill="{T["surface2"]}" stroke="{T["pale"]}" stroke-opacity="0.55"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + 27}" text-anchor="middle" font-family="{F_HAND}" font-size="26" fill="{T["pale"]}">{esc(text)}</text></g>'), w


def text_block(p, x, y, maxw, title_size, desc_size, lh):
    """Línea de estado, título, descripción, stack y destino. Devuelve (svg, alto, textos)."""
    parts, used = [], {"Geist": "", "GeistMedium": "", "OutfitSemi": ""}
    # estado: tipo · ● estado
    kind_w = text_width("Geist", p["kind"], 16)
    parts.append(f'<text x="{x}" y="{y}" font-family="{F_BODY}" font-size="16" fill="{T["muted"]}">{esc(p["kind"])}</text>'
                 f'<circle cx="{x + kind_w + 18:.1f}" cy="{y - 5.5}" r="4" fill="{T["ok"]}"/>'
                 f'<text x="{x + kind_w + 28:.1f}" y="{y}" font-family="{F_BODY}" font-size="16" fill="{T["muted"]}">{esc(p["status"])}</text>')
    used["Geist"] += p["kind"] + p["status"]
    ty = y + title_size + 14
    parts.append(f'<text x="{x - 1}" y="{ty}" font-family="{F_TITLE}" font-size="{title_size}" letter-spacing="-0.3" fill="{T["fg"]}">{esc(p["title"])}</text>')
    used["OutfitSemi"] += p["title"]
    lines = wrap("Geist", p["desc"], desc_size, maxw)
    dy = ty + desc_size + 18
    parts.append(f'<text font-family="{F_BODY}" font-size="{desc_size}" fill="{T["muted"]}">'
                 + "".join(f'<tspan x="{x}" y="{dy + i * lh}">{esc(l)}</tspan>' for i, l in enumerate(lines)) + "</text>")
    used["Geist"] += p["desc"]
    sy = dy + (len(lines) - 1) * lh + 34
    parts.append(f'<text x="{x}" y="{sy}" font-family="{F_BODY}" font-size="16" fill="{T["dim"]}">{esc(p["stack"])}</text>')
    used["Geist"] += p["stack"]
    hy = sy + 40
    parts.append(f'<text x="{x}" y="{hy}" font-family="{F_MED}" font-size="18" fill="{T["ink"]}">{esc(p["host"])}</text>'
                 + icon("arrow-right", x + text_width("GeistMedium", p["host"], 18) + 8, hy - 15, 18, T["ink"]))
    used["GeistMedium"] += p["host"]
    return "".join(parts), hy - y, used


def merge(a, b):
    return {k: a.get(k, "") + b.get(k, "") for k in set(a) | set(b)}


def card_wide(slug, mirrored=False):
    p = PROJECTS[slug]
    W, pad, fw = 1200, 28, 660
    fx = W - pad - fw if mirrored else pad
    frame, fh = window_frame(fx, pad, fw, slug, "shot")
    H = int(pad * 2 + fh)
    tx = 40 if mirrored else fx + fw + 40
    maxw = (fx - 40 - 40) if mirrored else (W - tx - 40)
    # el bloque de texto, centrado en vertical junto a la captura
    probe, th, used = text_block(p, tx, 0, maxw, 46, 20, 30)
    ty = (H - th) / 2 + 6
    block, th, used = text_block(p, tx, ty, maxw, 46, 20, 30)
    extra = ""
    if p.get("sticker"):
        s, sw = sticker(0, 0, p["sticker"], 0)
        sx = fx + fw - sw - 18 if not mirrored else fx + 18
        extra, _ = sticker(sx, pad - 12, p["sticker"], -4 if not mirrored else 3)
        used["Caveat"] = p["sticker"]
    body = (f'<rect width="{W}" height="{H}" rx="20" fill="{T["bg"]}"/>' + frame + block + extra)
    desc = f'{p["title"]}. {p["kind"]}, {p["status"].lower()}. {p["desc"]} {p["stack"]}.'
    (OUT / f"card-{slug}.svg").write_text(svg_doc(W, H, p["title"], desc, font_css(used), body), encoding="utf-8")


def card_half_pair(a, b):
    W, pad = 590, 22
    fw = W - 2 * pad
    blocks = {}
    for slug in (a, b):
        _, th, _ = text_block(PROJECTS[slug], pad, 0, fw - 4, 34, 18, 27)
        blocks[slug] = th
    th_max = max(blocks.values())
    for slug in (a, b):
        p = PROJECTS[slug]
        frame, fh = window_frame(pad, pad, fw, slug, "shot")
        ty = pad + fh + 42
        block, th, used = text_block(p, pad + 2, ty, fw - 4, 34, 18, 27)
        H = int(ty + th_max + pad + 4)
        body = f'<rect width="{W}" height="{H}" rx="20" fill="{T["bg"]}"/>' + frame + block
        desc = f'{p["title"]}. {p["kind"]}, {p["status"].lower()}. {p["desc"]} {p["stack"]}.'
        (OUT / f"card-{slug}.svg").write_text(svg_doc(W, H, p["title"], desc, font_css(used), body), encoding="utf-8")


# ---------------------------------------------------------------- botones

BUTTONS = [  # (fichero, texto, icono, primario)
    ("btn-proyecto", "Cuéntame tu proyecto", "arrow-right", True),
    ("btn-linkedin", "LinkedIn", "linkedin-logo", False),
    ("btn-x", "@mauroserranoo_", "x-logo", False),
    ("btn-telegram", "Prueba TrainPicker", "telegram-logo", False),
]


def button(fname, label, ic, primary):
    """Botones de quobit.es (Button.module.css): píldora, Geist 500, primario azul con flecha
    a la derecha; secundarios en azul marino con borde fino y el icono de la red delante."""
    h, padx, fs, isz, gap = 44, 18, 16, 18, 8  # 44 px: alto mínimo de Button.module.css
    tw = text_width("GeistMedium", label, fs)
    w = padx * 2 + tw + gap + isz
    bg, fg, ic_col = (T["accent"], "#ffffff", "#ffffff") if primary else (T["surface"], T["fg"], T["ink"])
    ring = "" if primary else ' stroke="#ffffff" stroke-opacity="0.16"'
    if primary:
        tx, ix = padx, padx + tw + gap
    else:
        ix, tx = padx, padx + isz + gap
    body = (f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{h - 1}" rx="{(h - 1) / 2}" fill="{bg}"{ring}/>'
            f'<text x="{tx:.1f}" y="{h / 2 + fs * 0.35:.1f}" font-family="{F_MED}" font-size="{fs}" fill="{fg}">{esc(label)}</text>'
            + icon(ic, ix, (h - isz) / 2, isz, ic_col))
    (OUT / f"{fname}.svg").write_text(svg_doc(round(w), h, label, label, font_css({"GeistMedium": label}), body), encoding="utf-8")


def main():
    print("\n".join(check_contrast([
        ("titular", T["fg"], T["bg"], True),
        ("texto secundario", T["muted"], T["bg"], False),
        ("stack de cada ficha (16 px)", T["dim"], T["bg"], False),
        ("enlace de cada ficha", T["ink"], T["bg"], False),
        ("botón principal", "#ffffff", T["accent"], False),
        ("botones secundarios", T["fg"], T["surface"], False),
        ("etiqueta a mano", T["pale"], T["surface2"], True),
    ])))
    hero()
    card_wide("trainpicker")
    card_half_pair("cardeo", "planabc")
    card_wide("reel", mirrored=True)
    for b in BUTTONS:
        button(*b)
    print("ok ->", OUT)


if __name__ == "__main__":
    main()
