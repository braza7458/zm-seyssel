"""Convertit un export OpenStreetMap (JSON Overpass) en plan pour Radiant.

Le plan est en unites BO3 (1 unite = 1 pouce = 2,54 cm), centre sur le
batiment de reference et tourne pour que son grand cote soit aligne sur
l'axe Y de Radiant : on peut ainsi construire avec des brushes droits.

Usage :
    python tools/osm_to_plan.py reference/osm/site_pres_dombet.json

Sorties :
    docs/plans/site-pres-dombet.svg      vue de dessus avec grille
    docs/plans/coordonnees-radiant.md    sommets des batiments en unites
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Batiment de depart : HLM rue des Pres Dombet (way OSM 131537388)
REF_WAY = 131537388
NAMED = {
    131537388: "HLM Pres Dombet (batiment 01)",
    131540438: "Annexe toit plat (garages)",
    131537354: "Barre nord (Chemin de la Fontaine)",
    131537380: "Ecole maternelle",
    131537365: "Maison de Pays",
}

M_PER_UNIT = 0.0254
GRID = 512  # une ligne de grille tous les 512 unites (~13 m)


def to_local_m(lat, lon, lat0, lon0):
    x = (lon - lon0) * 111320 * math.cos(math.radians(lat0))
    y = (lat - lat0) * 110540
    return x, y


def load_site(src):
    """Renvoie (ways, project) : les ways OSM par id et la projection en unites BO3."""
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    ways = {e["id"]: e for e in data["elements"] if e["type"] == "way"}
    ref = ways[REF_WAY]["geometry"]
    lat0 = sum(n["lat"] for n in ref) / len(ref)
    lon0 = sum(n["lon"] for n in ref) / len(ref)

    # Angle du plus long cote du batiment de reference
    pts = [to_local_m(n["lat"], n["lon"], lat0, lon0) for n in ref]
    longest = max(
        zip(pts, pts[1:]),
        key=lambda s: math.dist(s[0], s[1]),
    )
    (ax, ay), (bx, by) = longest
    rot = math.pi / 2 - math.atan2(by - ay, bx - ax)
    # Garder le nord vers le haut (rotation entre -90 et +90 degres)
    rot = (rot + math.pi / 2) % math.pi - math.pi / 2

    def rotate(n):
        x, y = to_local_m(n["lat"], n["lon"], lat0, lon0)
        rx = x * math.cos(rot) - y * math.sin(rot)
        ry = x * math.sin(rot) + y * math.cos(rot)
        return rx / M_PER_UNIT, ry / M_PER_UNIT

    # Origine = centre de la boite englobante du HLM
    ref_pts = [rotate(n) for n in ref]
    ox = (min(p[0] for p in ref_pts) + max(p[0] for p in ref_pts)) / 2
    oy = (min(p[1] for p in ref_pts) + max(p[1] for p in ref_pts)) / 2

    def project(n):
        x, y = rotate(n)
        return x - ox, y - oy

    project.rotation_deg = math.degrees(rot)
    return ways, project


def main(src):
    ways, project = load_site(src)

    shapes = []
    for wid, w in ways.items():
        tags = w.get("tags", {})
        poly = [project(n) for n in w["geometry"]]
        if "building" in tags:
            shapes.append(("building", wid, tags, poly))
        elif "highway" in tags:
            shapes.append(("road", wid, tags, poly))

    half = 6144  # rayon affiche, ~156 m
    size = 1000
    scale = size / (2 * half)

    def sx(x):
        return (x + half) * scale

    def sy(y):
        return (half - y) * scale

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size + 60}" '
        'font-family="Segoe UI, Arial, sans-serif">',
        f'<rect width="{size}" height="{size + 60}" fill="#f4f1ea"/>',
    ]
    for g in range(-half, half + 1, GRID):
        color = "#9a8f7a" if g == 0 else "#ddd6c6"
        out.append(f'<line x1="{sx(g):.1f}" y1="0" x2="{sx(g):.1f}" y2="{size}" stroke="{color}" stroke-width="1"/>')
        out.append(f'<line x1="0" y1="{sy(g):.1f}" x2="{size}" y2="{sy(g):.1f}" stroke="{color}" stroke-width="1"/>')
    for kind, wid, tags, poly in shapes:
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in poly)
        if kind == "road":
            width = 7 if tags["highway"] in ("secondary", "tertiary", "residential") else 3
            out.append(f'<polyline points="{d}" fill="none" stroke="#b9b2a3" stroke-width="{width}" stroke-linejoin="round"/>')
    for kind, wid, tags, poly in shapes:
        if kind != "building":
            continue
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in poly)
        fill = "#c0392b" if wid == REF_WAY else ("#7d6e57" if wid in NAMED else "#a99d88")
        out.append(f'<polygon points="{d}" fill="{fill}" stroke="#3b3326" stroke-width="1"/>')
    for wid, label in NAMED.items():
        if wid not in ways:
            continue
        poly = [project(n) for n in ways[wid]["geometry"]]
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        # Le HLM est etiquete a gauche pour ne pas chevaucher l'annexe
        tx, anchor = (sx(min(p[0] for p in poly)) - 8, "end") if wid == REF_WAY else (sx(cx) + 8, "start")
        out.append(
            f'<text x="{tx:.1f}" y="{sy(cy):.1f}" text-anchor="{anchor}" font-size="13" fill="#1d1a14" '
            f'stroke="#f4f1ea" stroke-width="3" paint-order="stroke">{label}</text>'
        )
    out.append(
        f'<text x="12" y="{size + 25}" font-size="14" fill="#1d1a14">'
        f"Grille : {GRID} unites BO3 (~{GRID * M_PER_UNIT:.1f} m). Origine (0,0) = centre du HLM. "
        "Axe Y = grand cote du HLM.</text>"
    )
    out.append(
        f'<text x="12" y="{size + 48}" font-size="12" fill="#5c5446">'
        "Donnees : (c) contributeurs OpenStreetMap, licence ODbL (cadastre DGFiP).</text>"
    )
    out.append("</svg>")

    plans = ROOT / "docs" / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / "site-pres-dombet.svg").write_text("\n".join(out), encoding="utf-8")

    lines = [
        "# Coordonnees Radiant (unites BO3)",
        "",
        "Genere par `tools/osm_to_plan.py`. Origine (0,0) = centre du HLM, axe Y = grand cote du HLM.",
        "Arrondi a 8 unites pres (grille Radiant conseillee : 8).",
        "",
    ]
    for wid, label in NAMED.items():
        if wid not in ways:
            continue
        poly = [project(n) for n in ways[wid]["geometry"]]
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        lines += [
            f"## {label} (OSM way {wid})",
            "",
            f"Boite englobante : X {round(min(xs) / 8) * 8} a {round(max(xs) / 8) * 8}, "
            f"Y {round(min(ys) / 8) * 8} a {round(max(ys) / 8) * 8} "
            f"(~{(max(xs) - min(xs)) * M_PER_UNIT:.1f} m x {(max(ys) - min(ys)) * M_PER_UNIT:.1f} m)",
            "",
            "| # | X | Y |",
            "|---|---|---|",
        ]
        for i, (x, y) in enumerate(poly[:-1], 1):
            lines.append(f"| {i} | {round(x / 8) * 8} | {round(y / 8) * 8} |")
        lines.append("")
    (plans / "coordonnees-radiant.md").write_text("\n".join(lines), encoding="utf-8")
    print("Rotation appliquee :", round(project.rotation_deg, 1), "degres")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "reference" / "osm" / "site_pres_dombet.json")
