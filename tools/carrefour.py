"""Le Carrefour Market, sa station-service et les parkings du couloir.

Positions et formes : OpenStreetMap (station : way 315532199, magasin : way 821364046, parkings) et
BD TOPO (batiments 00837282 et 00837211). Les volumes simples sont faits par maisons.py ; ici on ajoute
les details : bandeau bleu, facade vitree, auvent, marquise de la station, pompes, totem de prix.
"""

import json
import math

import monde
from geo import REF, obb
from immeuble import bloc
from materiaux import MAT


def triangulation(pts):
    """Ear clipping d'un polygone simple : liste de triangles (indices)."""
    n = len(pts)
    idx = list(range(n))
    aire = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    if aire < 0:
        idx.reverse()

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def dedans(p, a, b, c):
        return cross(a, b, p) >= 0 and cross(b, c, p) >= 0 and cross(c, a, p) >= 0

    out = []
    garde = 0
    while len(idx) > 3 and garde < 10 * n:
        garde += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if cross(a, b, c) <= 0:
                continue
            if any(dedans(pts[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            out.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            break
    if len(idx) == 3:
        out.append(tuple(idx))
    return out


def dalle(q, pts, mat, haut=6, groupe="parkings"):
    """Dalle plate (enrobe) sur un polygone, collee au terrain."""
    from quartier import prisme_triangle
    for i0, i1, i2 in triangulation(pts):
        tri = [(pts[i][0], pts[i][1], q.z(*pts[i]) + haut) for i in (i0, i1, i2)]
        q.ajoute(groupe, prisme_triangle(tri[0], tri[1], tri[2], min(t[2] for t in tri) - 30, mat))


def construire(q):
    d = json.loads((REF / "osm" / "corridor.json").read_text(encoding="utf-8"))
    parkings, station = [], None
    for e in d["elements"]:
        t = e.get("tags", {})
        pts = [q.site.proj(n["lat"], n["lon"]) for n in e["geometry"]][:-1]
        if len(pts) < 3:
            continue
        c = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        if t.get("amenity") == "parking" and not monde.dans_cadre(*c) and t.get("access") not in ("private", "no"):
            if sum(1 for p in pts if monde.jouable(p[0], p[1], 60)) == len(pts):
                parkings.append(pts)
        if e["id"] == 315532199:
            station = pts
    # les parkings eux-memes sont faits par sols.parkings()
    if station:
        _station(q, station)
    for p in q.maisons:
        if p["id"] == "00837282" and p.get("principal"):
            _magasin(q, p)
    q.nb_parkings = len(parkings)


def _orientee(q, cx, cy, ang, zref, brushes, groupe):
    from quartier import tourne
    for b in brushes:
        q.ajoute(groupe, tourne(b, math.radians(ang), cx, cy, zref))


def _magasin(q, p):
    """Facade du Carrefour Market tournee vers le parking : bandeau bleu, baie vitree, auvent."""
    l, w, h = p["l"], p["w"], int(p["h"] * 49.2)
    cible = (17338, 38942)
    a = math.radians(p["ang"])
    best = None
    for axe, sens in (("v", 1), ("v", -1), ("u", 1), ("u", -1)):
        nx, ny = (-math.sin(a), math.cos(a)) if axe == "v" else (math.cos(a), math.sin(a))
        nx, ny = nx * sens, ny * sens
        sc = (cible[0] - p["cx"]) * nx + (cible[1] - p["cy"]) * ny
        if best is None or sc > best[0]:
            best = (sc, axe, sens)
    _, axe, sens = best
    L = l if axe == "v" else w
    face = sens * (w / 2 if axe == "v" else l / 2)
    out = []

    def coller(a0, a1, z0, z1, mat, ep, proj=None):
        if axe == "v":
            v0, v1 = (face, face + ep) if sens > 0 else (face - ep, face)
            out.append(bloc(a0, v0, z0, a1, v1, z1, mat, proj=proj))
        else:
            u0, u1 = (face, face + ep) if sens > 0 else (face - ep, face)
            out.append(bloc(u0, a0, z0, u1, a1, z1, mat, proj=proj))

    coller(-L / 2, L / 2, h - 220, h - 40, MAT["volet_bleu"], 10)                  # bandeau bleu
    coller(-L / 2 + 60, -L / 2 + 700, h - 190, h - 70, MAT["marquage"], 12)        # enseigne
    coller(-420, 420, 0, 250, MAT["vitre"], 8, (840, 250))                          # entree vitree
    for u in (-420, 412):
        coller(u, u + 8, 0, 250, MAT["cadre"], 14)
    coller(-420, 420, 250, 262, MAT["cadre"], 14)
    # auvent en saillie, sur deux poteaux
    ep = 260
    if axe == "v":
        v0, v1 = (face, face + ep) if sens > 0 else (face - ep, face)
        out.append(bloc(-560, v0, 280, 560, v1, 296, MAT["auvent"]))
        for u in (-540, 524):
            vp = v1 - 20 if sens > 0 else v0
            out.append(bloc(u, vp, 0, u + 16, vp + 20, 280, MAT["metal"]))
    else:
        u0, u1 = (face, face + ep) if sens > 0 else (face - ep, face)
        out.append(bloc(u0, -560, 280, u1, 560, 296, MAT["auvent"]))
        for v in (-540, 524):
            up = u1 - 20 if sens > 0 else u0
            out.append(bloc(up, v, 0, up + 20, v + 16, 280, MAT["metal"]))
    _orientee(q, p["cx"], p["cy"], p["ang"], p["zref"], out, "maisons")


def _station(q, pts):
    """Marquise sur piliers, ilots de pompes, kiosque et totem de prix."""
    cx, cy, l, w, a = obb(pts)
    ang = math.degrees(a)
    z = round(q.z(cx, cy) / 8) * 8
    out = []
    # sol : enrobe sous la marquise
    out.append(bloc(-l / 2 - 120, -w / 2 - 120, -24, l / 2 + 120, w / 2 + 120, 4, MAT["asphalte"]))
    # marquise
    haut = 290
    out.append(bloc(-l / 2, -w / 2, haut, l / 2, w / 2, haut + 24, MAT["cadre"]))
    out.append(bloc(-l / 2 - 6, -w / 2 - 6, haut + 16, l / 2 + 6, w / 2 + 6, haut + 40, MAT["volet_bleu"]))
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx * (l / 2 - 50), sy * (w / 2 - 50)
            out.append(bloc(px - 12, py - 12, 0, px + 12, py + 12, haut, MAT["facade_blanche"]))
    # ilots et pompes
    for sy in (-0.3, 0.3):
        out.append(bloc(-l * 0.3, w * sy - 30, 0, l * 0.3, w * sy + 30, 8, MAT["bordure"]))
        for sx in (-0.2, 0.2):
            out.append(bloc(l * sx - 16, w * sy - 12, 8, l * sx + 16, w * sy + 12, 120, MAT["conteneur"]))
            out.append(bloc(l * sx - 12, w * sy - 14, 70, l * sx + 12, w * sy + 14, 100, MAT["fenetre"], proj=(24, 30)))
    # kiosque
    out.append(bloc(-l / 2 - 20, w / 2 + 40, 0, -l / 2 + 150, w / 2 + 160, 130, MAT["facade_blanche"]))
    out.append(bloc(-l / 2 - 24, w / 2 + 36, 130, -l / 2 + 154, w / 2 + 164, 142, MAT["volet_bleu"]))
    out.append(bloc(-l / 2 + 30, w / 2 + 38, 24, -l / 2 + 130, w / 2 + 40, 100, MAT["vitre"]))
    # totem des prix
    out.append(bloc(l / 2 + 150, -6, 0, l / 2 + 162, 6, 560, MAT["metal"]))
    out.append(bloc(l / 2 + 110, -12, 560, l / 2 + 202, 12, 700, MAT["cadre"]))
    out.append(bloc(l / 2 + 110, -14, 640, l / 2 + 202, -12, 700, MAT["volet_bleu"]))
    _orientee(q, cx, cy, ang, z, out, "maisons")
    q.station = (cx, cy)
