"""Genere le blockout (greybox) du quartier en prefab Radiant BO3.

Contenu du prefab, a l'echelle reelle, HLM centre sur (0,0) :
    - le sol (dalle de 16 unites sous z=0) et les routes
    - le HLM decoupe en blocs droits d'apres le cadastre, 5 niveaux de 128
    - son toit a deux pans et sa rangee de cheminees
    - l'annexe a toit plat et les batiments voisins en volumes simples

Usage :
    python tools/make_blockout.py

Sortie :
    game/map_source/_prefabs/zm_seyssel/site_blockout.map
Dans Radiant : clic droit dans la vue 2D > Misc > Prefab..., puis choisir ce fichier.
"""

import math
import uuid
from pathlib import Path

from osm_to_plan import REF_WAY, ROOT, load_site

OUT = ROOT / "game" / "map_source" / "_prefabs" / "zm_seyssel" / "site_blockout.map"

# Materiaux BO3 releves dans les sources des maps officielles (map_source des Mod Tools)
MAT = {
    "sol": "t7_stone_pebbles_01",
    "route": "t7_asphalt_dirty_dark_desert",
    "mur": "t7_plaster_smooth_light_01",
    "toit": "t7_brick_worn_dirty_red_wet",
    "cheminee": "t7_brick_worn_heavy_grout_red",
    "annexe": "t7_concrete_poured_bunker_paint_01_grey_lt",
    "voisin": "t7_concrete_wall_weathered_01_wet",
}

ETAGE = 128
NIVEAUX = 5  # rez-de-chaussee + 4 etages
PENTE_TOIT = math.radians(30)
DEBORD_TOIT = 16
RAYON = 4096  # on garde les batiments a moins de ~100 m du HLM
ANNEXE = 131540438

# Hauteur des voisins selon le type de batiment OSM
HAUTEURS = {"apartments": 512, "civic": 192, "yes": 256, "house": 256}


# --- geometrie -------------------------------------------------------------

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def scale(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def norm(a):
    return scale(a, 1 / math.sqrt(dot(a, a)))


def plane_points(n, p):
    """Trois points du plan, ordonnes comme Radiant : (p3-p1) x (p2-p1) = normale sortante."""
    n = norm(n)
    a = cross(n, (0, 0, 1)) if abs(n[2]) < 0.9 else cross(n, (1, 0, 0))
    a = scale(norm(a), 256)
    b = cross(n, a)
    return p, add(p, b), add(p, a)


def box(x0, y0, z0, x1, y1, z1):
    return [
        ((-1, 0, 0), (x0, 0, 0)), ((1, 0, 0), (x1, 0, 0)),
        ((0, -1, 0), (0, y0, 0)), ((0, 1, 0), (0, y1, 0)),
        ((0, 0, -1), (0, 0, z0)), ((0, 0, 1), (0, 0, z1)),
    ]


def prism(poly, z0, z1):
    """Brush vertical a partir d'un polygone convexe tourne dans le sens direct."""
    planes = [((0, 0, -1), (0, 0, z0)), ((0, 0, 1), (0, 0, z1))]
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        planes.append(((by - ay, -(bx - ax), 0), (ax, ay, z0)))
    return planes


def roof(x0, y0, x1, y1, z_egout):
    """Toit a deux pans, faitage le long de Y."""
    xm = (x0 + x1) / 2
    z_faitage = z_egout + (xm - x0) * math.tan(PENTE_TOIT)
    h = z_faitage - z_egout
    return [
        ((0, 0, -1), (0, 0, z_egout)),
        ((0, -1, 0), (0, y0, 0)), ((0, 1, 0), (0, y1, 0)),
        ((-h, 0, xm - x0), (x0, 0, z_egout)),
        ((h, 0, x1 - xm), (x1, 0, z_egout)),
    ], z_faitage


def convex_hull(points):
    pts = sorted(set((round(x), round(y)) for x, y in points))
    if len(pts) < 3:
        return pts

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h

    hull = half(pts)[:-1] + half(reversed(pts))[:-1]
    # Supprime les aretes trop courtes, qui donnent des faces invalides dans Radiant
    clean = []
    for p in hull:
        if not clean or math.dist(p, clean[-1]) >= 8:
            clean.append(p)
    if len(clean) > 2 and math.dist(clean[0], clean[-1]) < 8:
        clean.pop()
    return clean


def is_orthogonal(poly, tolerance=6):
    """Vrai si tous les murs de plus de 1 m sont alignes sur les axes (a quelques degres pres)."""
    for (ax, ay), (bx, by) in zip(poly, poly[1:]):
        if math.dist((ax, ay), (bx, by)) < 40:
            continue
        angle = math.degrees(math.atan2(by - ay, bx - ax)) % 90
        if tolerance < angle < 90 - tolerance:
            return False
    return True


def rectangles(poly, grid=8):
    """Decoupe un polygone presque orthogonal en rectangles alignes sur la grille."""
    pts = [(round(x / grid) * grid, round(y / grid) * grid) for x, y in poly]
    ys = sorted(set(y for _, y in pts))
    bands = []
    for y0, y1 in zip(ys, ys[1:]):
        ym = (y0 + y1) / 2
        xs = []
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            if (ay <= ym) != (by <= ym):
                xs.append(round((ax + (ym - ay) * (bx - ax) / (by - ay)) / grid) * grid)
        xs.sort()
        bands.append((y0, y1, list(zip(xs[::2], xs[1::2]))))
    # Fusionne les bandes voisines qui ont les memes largeurs
    merged = []
    for y0, y1, spans in bands:
        if merged and merged[-1][2] == spans and merged[-1][1] == y0:
            merged[-1] = (merged[-1][0], y1, spans)
        else:
            merged.append((y0, y1, spans))
    return [(x0, y0, x1, y1) for y0, y1, spans in merged for x0, x1 in spans if x1 > x0]


def road_quads(line, width):
    quads = []
    for (ax, ay), (bx, by) in zip(line, line[1:]):
        length = math.dist((ax, ay), (bx, by))
        if length < 1:
            continue
        nx, ny = -(by - ay) / length * width / 2, (bx - ax) / length * width / 2
        quads.append([(ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny), (ax + nx, ay + ny)])
    return quads


# --- ecriture du .map ------------------------------------------------------

def fmt(v):
    return f"{round(v, 3):g}"


_guids = {"graine": "", "n": 0}


def reset_guids(graine):
    """Identifiants stables : la meme generation redonne les memes GUID (eclairage et diffs git)."""
    _guids.update(graine=graine, n=0)


def new_guid():
    _guids["n"] += 1
    return f'{{{str(uuid.uuid5(uuid.NAMESPACE_URL, f"zm_seyssel/{_guids["graine"]}/{_guids["n"]}")).upper()}}}'


def brush_lines(brushes, first=0):
    """Lignes .map des brushes ; chaque brush est (categorie de MAT ou nom de materiau, plans)."""
    lines = []
    for i, (cat, planes) in enumerate(brushes, first):
        mat = MAT.get(cat, cat)
        lines += [f"// brush {i}", "{", f" guid \"{new_guid()}\""]
        for n, p in planes:
            p1, p2, p3 = plane_points(n, p)
            pts = " ".join("( " + " ".join(fmt(c) for c in q) + " )" for q in (p1, p2, p3))
            lines.append(f" {pts} {mat} 256 256 0 0 0 0 lightmap_gray 16384 16384 0 0 0 0")
        lines.append("}")
    return lines


def write_map(brushes, path):
    reset_guids(path.name)
    lines = ["iwmap 4", "// entity 0", "{", f'guid "{new_guid()}"', '"classname" "worldspawn"']
    lines += brush_lines(brushes)
    lines.append("}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\r\n")


def check_brush(planes):
    """Verifie qu'un brush est un volume ferme : chaque face doit porter au moins 3 sommets."""
    planes = [(norm(n), dot(norm(n), p)) for n, p in planes]
    verts = []
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            for k in range(j + 1, len(planes)):
                (a, da), (b, db), (c, dc) = planes[i], planes[j], planes[k]
                det = dot(a, cross(b, c))
                if abs(det) < 1e-9:
                    continue
                v = scale(add(add(scale(cross(b, c), da), scale(cross(c, a), db)), scale(cross(a, b), dc)), 1 / det)
                if all(dot(n, v) <= d + 0.01 for n, d in planes):
                    verts.append(v)
    return all(sum(1 for v in verts if abs(dot(n, v) - d) < 0.01) >= 3 for n, d in planes)


def build_site():
    """Brushes du quartier : liste de (categorie, plans), la categorie donne le materiau via MAT."""
    ways, project = load_site(ROOT / "reference" / "osm" / "site_pres_dombet.json")
    brushes = []

    # Sol
    brushes.append(("sol", box(-RAYON, -RAYON, -16, RAYON, RAYON, 0)))

    # Routes : bandes de 2 unites d'epaisseur posees sur le sol
    for w in ways.values():
        hw = w.get("tags", {}).get("highway")
        if not hw:
            continue
        line = [project(n) for n in w["geometry"]]
        if not any(abs(x) < RAYON and abs(y) < RAYON for x, y in line):
            continue
        width = 240 if hw in ("secondary", "tertiary", "residential") else 120 if hw == "service" else 60
        for quad in road_quads(line, width):
            if all(abs(c) < RAYON for p in quad for c in p):
                brushes.append(("route", prism(quad, 0, 2)))

    # HLM : volumes droits + toit + cheminees
    hlm = [project(n) for n in ways[REF_WAY]["geometry"]][:-1]
    rects = rectangles(hlm)
    for x0, y0, x1, y1 in rects:
        brushes.append(("mur", box(x0, y0, 0, x1, y1, ETAGE * NIVEAUX)))
    bx0 = min(r[0] for r in rects) - DEBORD_TOIT
    bx1 = max(r[2] for r in rects) + DEBORD_TOIT
    by0 = min(r[1] for r in rects) - DEBORD_TOIT
    by1 = max(r[3] for r in rects) + DEBORD_TOIT
    toit, z_faitage = roof(bx0, by0, bx1, by1, ETAGE * NIVEAUX)
    brushes.append(("toit", toit))
    xm = (bx0 + bx1) / 2
    for i in range(10):
        y = by0 + (by1 - by0) * (i + 0.5) / 10
        brushes.append(("cheminee", box(xm - 24, y - 16, z_faitage - 32, xm + 24, y + 16, z_faitage + 64)))

    # Voisins
    for wid, w in ways.items():
        tags = w.get("tags", {})
        if "building" not in tags or wid == REF_WAY:
            continue
        poly = [project(n) for n in w["geometry"]]
        if not all(abs(x) < RAYON and abs(y) < RAYON for x, y in poly):
            continue
        h = 128 if wid == ANNEXE else HAUTEURS.get(tags["building"], 256)
        cat = "annexe" if wid == ANNEXE else "voisin"
        if is_orthogonal(poly):
            for x0, y0, x1, y1 in rectangles(poly[:-1]):
                brushes.append((cat, box(x0, y0, 0, x1, y1, h)))
            continue
        hull = convex_hull(poly)
        if len(hull) >= 3:
            brushes.append((cat, prism(hull, 0, h)))

    bad = [i for i, (_, planes) in enumerate(brushes) if not check_brush(planes)]
    if bad:
        raise SystemExit(f"Brushes invalides : {bad}")
    return brushes, rects, z_faitage


def main():
    brushes, rects, z_faitage = build_site()
    write_map(brushes, OUT)
    print(f"{len(brushes)} brushes ecrits dans {OUT.relative_to(ROOT)}")
    print(f"HLM : {len(rects)} blocs, egout a z={ETAGE * NIVEAUX}, faitage a z={round(z_faitage)}")


if __name__ == "__main__":
    main()
