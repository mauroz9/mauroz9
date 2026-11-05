"""Utilidades compartidas por los generadores de SVG del perfil.

- Fuentes de la marca Quobit (Outfit, Geist, Caveat; licencia OFL en assets/fonts/OFL.txt),
  fijadas a un peso y recortadas a los caracteres que usa cada SVG, incrustadas en woff2.
  Un SVG servido como <img> no puede cargar fuentes externas: sin esto GitHub pintaría
  la tipografía del sistema de cada visitante.
- Medición de texto con las métricas reales de la fuente, para colocar subrayados y
  separaciones sin adivinar.
- Comprobación de contraste WCAG (AA) de cada pareja texto/fondo antes de escribir nada.

Requiere fonttools y brotli (pip install fonttools brotli).
"""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"

# familia → (fichero, peso fijado)
FACES = {
    "Outfit": ("outfit-latin.woff2", 700),
    "Geist": ("geist-latin.woff2", 400),
    "GeistMedium": ("geist-latin.woff2", 500),
    "Caveat": ("caveat-latin.woff2", 600),
}


@lru_cache(maxsize=None)
def _instance(face: str) -> TTFont:
    fichero, peso = FACES[face]
    font = TTFont(FONTS / fichero)
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": peso})
    return font


def text_width(face: str, text: str, size: float, tracking: float = 0) -> float:
    font = _instance(face)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    total = sum(hmtx[cmap.get(ord(ch), cmap.get(ord("?")))][0] for ch in text)
    return total * size / upm + tracking * max(len(text) - 1, 0)


def font_css(usage: dict[str, str]) -> str:
    """usage: familia → texto que se pinta con ella. Devuelve las reglas @font-face."""
    reglas = []
    for face, text in usage.items():
        if not text:
            continue
        # copia de la instancia: el recorte la modifica y la caché debe quedar intacta
        buf = io.BytesIO()
        _instance(face).save(buf)
        buf.seek(0)
        font = TTFont(buf)
        opts = Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "calt"]
        opts.name_IDs = []
        sub = Subsetter(opts)
        sub.populate(text=text + " ")
        sub.subset(font)
        out = io.BytesIO()
        font.flavor = "woff2"
        font.save(out)
        b64 = base64.b64encode(out.getvalue()).decode()
        reglas.append(
            f"@font-face{{font-family:'Q{face}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(reglas)


def family(face: str, fallback: str) -> str:
    return f"'Q{face}', {fallback}"


# ---------- contraste ----------

def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_contrast(pairs: list[tuple[str, str, str, bool]]) -> list[str]:
    """pairs: (nombre, texto, fondo, es_grande). Lanza si alguna no llega a AA."""
    informe, fallos = [], []
    for nombre, fg, bg, grande in pairs:
        ratio = contrast(fg, bg)
        minimo = 3.0 if grande else 4.5
        linea = f"{nombre}: {ratio:.2f}:1 (mínimo {minimo})"
        informe.append(linea)
        if ratio < minimo:
            fallos.append(linea)
    if fallos:
        raise SystemExit("Contraste insuficiente:\n  " + "\n  ".join(fallos))
    return informe


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
