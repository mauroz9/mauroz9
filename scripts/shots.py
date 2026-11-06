#!/usr/bin/env python3
"""Compone las capturas de producto de las fichas (assets/shots/*.jpg, 1120×700) a partir de
pantallas reales de cada app, no de su landing.

Uso: python3 scripts/shots.py <carpeta con las capturas originales>   (requiere Pillow)

Origen de cada captura (repos de mauroz9):
  tp-chat.png                      trainpicker            docs/img/chat.png (textos reales del bot)
  cd-app-menu/sala/partida.webp    cardeo-web             sitio/img/app-*.webp
  pa-planes-ancho.png, pa-plan-movil.png
                                   planabc-front          public/icons/screenshots/
  pwa-*.jpg                        pwa-install-assistant  docs/support/*.jpg (simulador iOS y emulador Android)

Después: python3 scripts/build.py para regenerar las fichas.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "shots"
W, H = 1120, 700


def rounded(im: Image.Image, r: int) -> Image.Image:
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def paste_shadowed(canvas: Image.Image, im: Image.Image, x: int, y: int, r: int, border=None):
    """Pega una pantalla con esquinas redondeadas, sombra suave y borde fino opcional."""
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x, y + 10, x + im.width, y + im.height + 10), r,
                                             fill=(0, 0, 0, 110))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))
    canvas.alpha_composite(rounded(im, r), (x, y))
    if border:
        ImageDraw.Draw(canvas).rounded_rectangle((x, y, x + im.width - 1, y + im.height - 1), r,
                                                 outline=border, width=2)


def fit_h(im: Image.Image, h: int) -> Image.Image:
    return im.convert("RGB").resize((round(im.width * h / im.height), h), Image.LANCZOS)


def phones_row(src: Path, files: list[str], bg: str, h: int, gap: int, border=None) -> Image.Image:
    canvas = Image.new("RGBA", (W, H), bg)
    ims = [fit_h(Image.open(src / f), h) for f in files]
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    x, y = (W - total) // 2, (H - h) // 2 - 4
    for im in ims:
        paste_shadowed(canvas, im, x, y, 26, border)
        x += im.width + gap
    return canvas


def trainpicker(src: Path) -> Image.Image:
    im = Image.open(src / "tp-chat.png").convert("RGB")
    # fuera el marco redondeado exterior y el pie de la maqueta: queda el chat
    im = im.crop((45, 45, im.width - 45, 925))
    canvas = Image.new("RGBA", (W, H), "#efe9f1")
    k = min((W - 40) / im.width, (H - 40) / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return canvas


def cardeo(src: Path) -> Image.Image:
    return phones_row(src, ["cd-app-menu.webp", "cd-app-sala.webp", "cd-app-partida.webp"],
                      "#1a4c79", 640, 34)


def planabc(src: Path) -> Image.Image:
    canvas = Image.new("RGBA", (W, H), "#161f30")
    desk = Image.open(src / "pa-planes-ancho.png").convert("RGB")
    desk = desk.resize((860, round(desk.height * 860 / desk.width)), Image.LANCZOS)
    paste_shadowed(canvas, desk, 44, (H - desk.height) // 2 - 30, 14)
    phone = fit_h(Image.open(src / "pa-plan-movil.png"), 600)
    paste_shadowed(canvas, phone, W - phone.width - 44, (H - 600) // 2, 30, "#2b3750")
    return canvas


def pwa(src: Path) -> Image.Image:
    return phones_row(src, ["pwa-ios-iphone-bottom-arrow.jpg", "pwa-android-native-dialog.jpg",
                            "pwa-android-assistant.jpg"], "#0d1324", 630, 30, "#2a3350")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    src = Path(sys.argv[1])
    for name, fn in (("trainpicker", trainpicker), ("cardeo", cardeo), ("planabc", planabc), ("pwa", pwa)):
        fn(src).convert("RGB").save(OUT / f"{name}.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        print("ok ->", OUT / f"{name}.jpg")


if __name__ == "__main__":
    main()
