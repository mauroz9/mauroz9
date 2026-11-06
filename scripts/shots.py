#!/usr/bin/env python3
"""Compone las capturas de producto de las fichas (assets/shots/*.jpg, 1120×700) a partir de
pantallas reales de cada app, no de su landing.

Uso: python3 scripts/shots.py <carpeta con las capturas originales>
     (requiere Pillow y Google Chrome, que renderiza las maquetas HTML)

Maquetas HTML (assets/shots/src/, cada una explica de dónde salen sus textos y colores):
  trainpicker.html   el bot en Telegram simulado, con los mensajes y botones reales del bot
  cardeo.html        miniatura que explica el juego: la peña en la mesa, cada uno con su móvil

Capturas originales (repos de mauroz9), en la carpeta que se pasa como argumento:
  pa-planes-ancho.png, pa-plan-movil.png
                                   planabc-front          public/icons/screenshots/
  pwa-*.jpg                        pwa-install-assistant  docs/support/*.jpg (simulador iOS y emulador Android)

Después: python3 scripts/build.py para regenerar las fichas.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
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


CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def render_html(name: str) -> Image.Image:
    """Captura assets/shots/src/<name>.html con Chrome sin ventana, a 2x y reducida a 1120×700."""
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "shot.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={W},{H}",
                        "--virtual-time-budget=3000", f"--screenshot={png}",
                        (OUT / "src" / f"{name}.html").as_uri()],
                       check=True, capture_output=True)
        return Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)


def trainpicker(src: Path) -> Image.Image:
    return render_html("trainpicker")


def cardeo(src: Path) -> Image.Image:
    return render_html("cardeo")


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
