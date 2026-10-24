"""Sols et clotures : cours et surfaces dures (lues sur l'orthophoto), parkings et leurs places (OSM),
jardins prives fermes par des haies et des murets (cadastre).
"""

import json
import math

import monde
import voirie
from carrefour import dalle
from geo import M, REF, obb
from materiaux import MAT

HAUT = {"asphalte": 4, "dalle_claire": 5, "terre": 2}


def construire(q):
    q.jardins_poly = []
    jardins(q)
    surfaces(q)
    parkings(q)


def _sur_batiment(q, x, y):
    return any(e[0] < x < e[2] and e[1] < y < e[3] for e in q.emprises)


def surfaces(q):
    """Rectangles de sol dur ou de terre (reference/ign/sols_couloir.json), poses sur le terrain."""
    from quartier import dans_poly, prisme_triangle
    for x0, y0, x1, y1, cle in json.loads((REF / "ign" / "sols_couloir.json").read_text()):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if monde.ancre((cx, cy))[0] > monde.R0 - 400 or _sur_batiment(q, cx, cy):
            continue
        if any(bb[0] < cx < bb[2] and bb[1] < cy < bb[3] and dans_poly(cx, cy, pts) for pts, bb in q.jardins_poly):
            continue          # dans un jardin : pelouse
        h = HAUT[cle]
        c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        # cote : terrain au coin et au centre, pour ne pas etre perce au milieu de la dalle
        zc = q.z(cx, cy)
        p3 = [(x, y, max(q.z(x, y), zc - 6) + h) for x, y in c]
        zb = min(p[2] for p in p3) - 20
        q.ajoute("sols", prisme_triangle(p3[0], p3[1], p3[2], zb, MAT[cle]))
        q.ajoute("sols", prisme_triangle(p3[0], p3[2], p3[3], zb, MAT[cle]))


def parkings(q):
    """Tous les parkings OSM visibles : enrobe, lignes des places, places pour les voitures."""
    d = json.loads((REF / "osm" / "corridor.json").read_text(encoding="utf-8"))
    n = 0
    for e in d["elements"]:
        t = e.get("tags", {})
        if t.get("amenity") != "parking" or t.get("parking") in ("underground", "multi-storey"):
            continue
        pts = [q.site.proj(nd["lat"], nd["lon"]) for nd in e["geometry"]][:-1]
        if len(pts) < 3:
            continue
        cx, cy, l, w, a = obb(pts)
        if monde.ancre((cx, cy))[0] > monde.R0 - 400:
            continue
        dalle(q, pts, MAT["asphalte"], 7, "parkings")
        n += 1
        if not monde.jouable(cx, cy) or w < 300:
            continue
        # places en batailles le long des deux grands cotes (une seule rangee si le parking est etroit)
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        rangees = (1, -1) if w >= 560 else (1,)
        nb = int((l - 60) // 123)
        for sens in rangees:
            base = w / 2 - 20
            for k in range(nb + 1):
                s = -l / 2 + 30 + k * 123 + (l - 60 - nb * 123) / 2
                x = cx + ux * s + vx * sens * (base - 115)
                y = cy + uy * s + vy * sens * (base - 115)
                voirie.boite_orientee(q, "marquages", x, y, 4, 230, 3, math.degrees(a), MAT["marquage"], dz=7.5)
                if k < nb and (k * 7 + n) % 20 < 11:
                    xc = cx + ux * (s + 61) + vx * sens * (base - 115)
                    yc = cy + uy * (s + 61) + vy * sens * (base - 115)
                    if not q.interdit(xc, yc, 90):
                        q.slots.append((xc, yc, (math.degrees(a) + 90) % 360))
    q.nb_parkings_osm = n


def jardins(q):
    """Parcelles de maisons dans la zone jouable : haie sur les limites, muret et grille cote rue, portillon."""
    parcelles = json.loads((REF / "ign" / "parcelles_couloir.json").read_text())
    from quartier import dans_poly
    maisons = [(p["cx"], p["cy"]) for p in q.maisons if p.get("aire", 0) < 400]
    vus = set()
    rues = [pts for hw, nom, pts, acces, ow in q.osm_routes if hw in voirie.VEHICULE and hw != "service"]
    n = 0
    for pc in parcelles:
        pts = [tuple(p) for p in pc["pts"]]
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        if not monde.jouable(cx, cy, 300) or monde.dans_cadre(cx, cy) and abs(cx) < 3500 and abs(cy) < 4500:
            continue      # le coeur du quartier HLM reste ouvert
        aire = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2 / M / M
        if aire > 2500 or not any(dans_poly(x, y, pts) for x, y in maisons):
            continue
        n += 1
        q.jardins_poly.append((pts, (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            cle = tuple(sorted(((round(a[0] / 16), round(a[1] / 16)), (round(b[0] / 16), round(b[1] / 16)))))
            if cle in vus:
                continue
            vus.add(cle)
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 40:
                continue
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            cote_rue = any(monde.dist_chemin((mx, my), r)[0] < 420 for r in rues)
            if cote_rue:
                # muret + grille, interrompus par un portillon de 64 au milieu
                for s0, s1 in ((0, L / 2 - 32), (L / 2 + 32, L)):
                    if s1 - s0 < 20:
                        continue
                    sm = (s0 + s1) / 2
                    x = a[0] + (b[0] - a[0]) * sm / L
                    y = a[1] + (b[1] - a[1]) * sm / L
                    voirie.boite_orientee(q, "clotures", x, y, s1 - s0, 12, 30, ang, MAT["muret"], dz=-8)
                    voirie.boite_orientee(q, "clotures", x, y, s1 - s0, 3, 34, ang, MAT["rail_clair"], dz=22)
            else:
                voirie.boite_orientee(q, "clotures", mx, my, L, 40, 100, ang, MAT["feuillage"], dz=-8)
    q.nb_jardins = n
