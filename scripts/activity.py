#!/usr/bin/env python3
"""Tarjeta de actividad del perfil (profile/activity.svg).

Datos: API GraphQL de GitHub con el token de GH_TOKEN (o GITHUB_TOKEN). Con un token del
propio usuario incluye la actividad en repos privados, sin enseñar nada de su código.
Si la API falla, sale con error y no toca los SVG existentes: el perfil sigue mostrando
la última versión buena en vez de una tarjeta vacía o rota.

Uso: GH_TOKEN=... python3 scripts/activity.py [usuario]

Decisiones (anti-slop R-31):
- Calendario en una sola gama de azules de Quobit: la intensidad es lo único que se lee,
  así que un solo tono lo cuenta sin ruido.
- Lenguajes en tonos del mismo azul, con nombre y porcentaje escritos: identificar por
  color obligaría a una leyenda de seis colores ajenos a la marca.
- Las cifras son las que da la API, sin redondeos a «+»; si no hay datos, se dice.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

from svgkit import ROOT, check_contrast, esc, family, font_css, text_width

USER = sys.argv[1] if len(sys.argv) > 1 else "mauroz9"
OUT = ROOT / "profile"
SANS_FB = "'Helvetica Neue', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(bg="#070d20", fg="#eceff7", muted="#a3adc6", line="#1b2647",
                 scale=["#111c3d", "#1d3a8f", "#2f5bea", "#6f93ff", "#cfe0ff"],
                 langs=["#cfe0ff", "#8fb0ff", "#4c7bff", "#2546b8", "#1a2f75"], other="#3a4562"),
    "light": dict(bg="#f1f3f8", fg="#0b1430", muted="#45507a", line="#d5dbe8",
                  scale=["#dde3ef", "#a9c0f5", "#5f86f2", "#2f5bea", "#13308f"],
                  langs=["#13308f", "#2f5bea", "#6f93ff", "#a9c0f5", "#cfdcf8"], other="#b9c0cf"),
}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""


def fetch() -> dict:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Falta GH_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-activity-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not data.get("data", {}).get("user"):
        raise SystemExit(f"Error de la API: {data.get('errors')}")
    return data["data"]["user"]


def stats(user: dict) -> dict:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    counts = [d["contributionCount"] for d in days]
    # racha actual: si hoy aún no hay nada, se cuenta desde ayer
    i = len(counts) - 1
    if counts and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    langs: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return dict(weeks=cal["weeks"], total=cal["totalContributions"], active=sum(1 for c in counts if c),
                current=current, longest=longest, langs=langs)


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def card(name: str, t: dict, s: dict, today: dt.date) -> str:
    W, H = 1200, 500
    x0 = 56
    outfit, geist, geistm = family("Outfit", SANS_FB), family("Geist", SANS_FB), family("GeistMedium", SANS_FB)
    title = "Actividad en GitHub"
    sub = "Últimos 12 meses, repos públicos y privados"
    figures = [(fmt(s["total"]), "contribuciones"), (fmt(s["active"]), "días con actividad"),
               (f'{s["current"]} {"día" if s["current"] == 1 else "días"}', "racha actual"),
               (f'{s["longest"]} días', "racha más larga")]
    foot = f"Actualizado el {today.day} {MESES[today.month - 1]} {today.year}"

    parts, used_geist, used_outfit, used_med = [], title + sub + foot, "", ""

    # cifras
    fx = x0
    for value, label in figures:
        parts.append(f'<text x="{fx}" y="146" font-family="{outfit}" font-size="40" fill="{t["fg"]}">{esc(value)}</text>'
                     f'<text x="{fx}" y="174" font-family="{geist}" font-size="17" fill="{t["muted"]}">{esc(label)}</text>')
        used_outfit += value
        used_geist += label
        fx += 272

    # calendario
    weeks = s["weeks"]
    cell, gap = 16, 4
    gx, gy = x0 + 40, 230
    maxc = max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] + [1])

    def level(c: int) -> int:
        if c == 0:
            return 0
        return min(4, 1 + int(3 * (c - 1) / max(maxc - 1, 1) + 0.5)) if maxc > 1 else 4

    last_month = None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            date = dt.date.fromisoformat(d["date"])
            wd = date.weekday()  # lunes = 0
            x, y = gx + wi * (cell + gap), gy + wd * (cell + gap)
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3.5" fill="{t["scale"][level(d["contributionCount"])]}">'
                         f'<title>{d["contributionCount"]} el {date.day} {MESES[date.month - 1]}</title></rect>')
        first = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month != last_month and first.day <= 7 and wi < len(weeks) - 2:
            m = MESES[first.month - 1]
            parts.append(f'<text x="{gx + wi * (cell + gap)}" y="{gy - 12}" font-family="{geist}" font-size="14" fill="{t["muted"]}">{m}</text>')
            used_geist += m
        last_month = first.month
    for wd, lab in ((0, "lun"), (2, "mié"), (4, "vie")):
        parts.append(f'<text x="{x0}" y="{gy + wd * (cell + gap) + 13}" font-family="{geist}" font-size="13" fill="{t["muted"]}">{lab}</text>')
        used_geist += lab
    if s["total"] == 0:
        msg = "Sin actividad registrada en los últimos 12 meses"
        parts.append(f'<text x="{W / 2}" y="{gy + 76}" text-anchor="middle" font-family="{geist}" font-size="18" fill="{t["muted"]}">{msg}</text>')
        used_geist += msg

    # leyenda del calendario
    lx = gx + len(weeks) * (cell + gap) - 5 * (cell + gap) - 92
    ly = gy + 7 * (cell + gap) + 18
    parts.append(f'<text x="{lx}" y="{ly + 13}" font-family="{geist}" font-size="13" fill="{t["muted"]}">menos</text>')
    for k, col in enumerate(t["scale"]):
        parts.append(f'<rect x="{lx + 44 + k * (cell + gap)}" y="{ly}" width="{cell}" height="{cell}" rx="3.5" fill="{col}"/>')
    parts.append(f'<text x="{lx + 44 + 5 * (cell + gap) + 4}" y="{ly + 13}" font-family="{geist}" font-size="13" fill="{t["muted"]}">más</text>')
    used_geist += "menosmás"

    # lenguajes: barra apilada, del más usado (azul más intenso) al resto
    total_b = sum(s["langs"].values())
    top = sorted(s["langs"].items(), key=lambda kv: -kv[1])[:5]
    rest = total_b - sum(v for _, v in top)
    if rest > 0:
        top.append(("Otros", rest))
    by = 462
    bar_w = W - 2 * x0
    shades = t["langs"][: len(top) - (1 if rest > 0 else 0)] + ([t["other"]] if rest > 0 else [])
    bx = x0
    legend_x = x0
    if total_b:
        parts.append(f'<clipPath id="bar"><rect x="{x0}" y="{by - 26}" width="{bar_w}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
        for k, (lang, size) in enumerate(top):
            w = bar_w * size / total_b
            parts.append(f'<rect x="{bx:.1f}" y="{by - 26}" width="{w + 0.5:.1f}" height="10" fill="{shades[k]}"/>')
            bx += w
        parts.append("</g>")
        for k, (lang, size) in enumerate(top):
            label = f"{lang} {size * 100 / total_b:.1f} %".replace(".", ",")
            parts.append(f'<rect x="{legend_x}" y="{by + 2}" width="10" height="10" rx="2" fill="{shades[k]}"/>'
                         f'<text x="{legend_x + 16}" y="{by + 12}" font-family="{geist}" font-size="15" fill="{t["fg"]}">{esc(label)}</text>')
            used_geist += label
            legend_x += 16 + text_width("Geist", label, 15) + 26

    css = font_css({"Outfit": used_outfit, "Geist": used_geist, "GeistMedium": title})
    desc = (f"{s['total']} contribuciones en los últimos 12 meses, {s['active']} días con actividad, "
            f"racha actual de {s['current']} días y racha más larga de {s['longest']} días.")
    if total_b:
        desc += " Lenguajes: " + ", ".join(f"{l} {v * 100 / total_b:.0f} %" for l, v in top) + "."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">{title} de {USER}</title>
<desc id="d">{esc(desc)}</desc>
<defs><style>{css}</style></defs>
<rect width="{W}" height="{H}" rx="20" fill="{t["bg"]}"/>
<text x="{x0}" y="62" font-family="{geistm}" font-size="22" fill="{t["fg"]}">{title}</text>
<text x="{x0}" y="88" font-family="{geist}" font-size="16" fill="{t["muted"]}">{sub}</text>
<path d="M{x0} 202H{W - x0}" stroke="{t["line"]}"/>
{"".join(parts)}
<text x="{W - x0}" y="62" text-anchor="end" font-family="{geist}" font-size="14" fill="{t["muted"]}">{esc(foot)}</text>
</svg>
'''


def main() -> None:
    s = stats(fetch())
    today = dt.datetime.now(dt.timezone.utc).date()
    # solo tema oscuro, como el resto de piezas de la marca (ver build.py)
    t = THEMES["dark"]
    check_contrast([("texto", t["muted"], t["bg"], False), ("cifras", t["fg"], t["bg"], True)])
    (OUT / "activity.svg").write_text(card("dark", t, s, today), encoding="utf-8")
    print(f"ok: {s['total']} contribuciones, racha {s['current']}/{s['longest']}, {len(s['langs'])} lenguajes")


if __name__ == "__main__":
    main()
