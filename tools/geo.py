"""Geographie du quartier : projection en unites BO3, relief IGN, donnees OSM.

Repere de jeu :
    - origine au centre du batiment 1 (HLM rue des Pres Dombet)
    - axe Y le long du batiment 1 (vers le nord-nord-ouest), axe X vers l'est-nord-est
    - z = 0 au pied de la facade est du batiment 1
    - ECHELLE agrandit tout le quartier : a 1, 1 m reel = 39,4 unites ; le jeu
      parait petit a l'echelle exacte, les maps officielles sont plus genereuses
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "reference"

ECHELLE = 1.25
M = 39.37 * ECHELLE  # unites par metre reel

BAT1, BAT2, BAT3 = 131537388, 131537277, 131537354
ANNEXE, GARAGES = 131540438, 131539162


def _lire(nom):
    return json.loads((REF / nom).read_text(encoding="utf-8"))


class Site:
    def __init__(self):
        self.ways = {}
        for nom in ("osm/site_pres_dombet.json", "osm/batiment2_2018.json", "osm/amenagements.json"):
            data = _lire(nom)
            for e in data["elements"] if isinstance(data, dict) else data:
                if e["type"] == "way":
                    self.ways[e["id"]] = e
        self.nodes = [e for e in _lire("osm/amenagements.json")["elements"] if e["type"] == "node"]

        ref = self.ways[BAT1]["geometry"]
        self.lat0 = sum(n["lat"] for n in ref) / len(ref)
        self.lon0 = sum(n["lon"] for n in ref) / len(ref)
        self.kx = 111320 * math.cos(math.radians(self.lat0))
        self.ky = 110540

        # Rotation : le plus long mur du batiment 1 devient l'axe Y
        pts = [self._metres(n["lat"], n["lon"]) for n in ref]
        (ax, ay), (bx, by) = max(zip(pts, pts[1:]), key=lambda s: math.dist(*s))
        rot = math.pi / 2 - math.atan2(by - ay, bx - ax)
        self.rot = (rot + math.pi / 2) % math.pi - math.pi / 2
        self.cos, self.sin = math.cos(self.rot), math.sin(self.rot)

        rp = [self._tourner(*p) for p in pts]
        self.ox = (min(p[0] for p in rp) + max(p[0] for p in rp)) / 2
        self.oy = (min(p[1] for p in rp) + max(p[1] for p in rp)) / 2

        relief = _lire("ign/relief_pres_dombet.json")
        self.ign = relief
        self.ign_lat0, self.ign_lon0 = relief["centre"]
        self.alt_ref = None
        self.alt_ref = self.altitude_reelle(*self.vers_latlon(self.boite(BAT1)[2], 0))

    # --- projection --------------------------------------------------------
    def _metres(self, lat, lon):
        return (lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky

    def _tourner(self, x, y):
        return x * self.cos - y * self.sin, x * self.sin + y * self.cos

    def proj(self, lat, lon):
        """lat/lon -> unites de jeu (x, y)."""
        x, y = self._tourner(*self._metres(lat, lon))
        return (x - self.ox) * M, (y - self.oy) * M

    def vers_latlon(self, x, y):
        rx, ry = x / M + self.ox, y / M + self.oy
        mx = rx * self.cos + ry * self.sin
        my = -rx * self.sin + ry * self.cos
        return self.lat0 + my / self.ky, self.lon0 + mx / self.kx

    def poly(self, way_id):
        return [self.proj(n["lat"], n["lon"]) for n in self.ways[way_id]["geometry"]]

    def boite(self, way_id):
        """Boite englobante (x0, y0, x1, y1) d'un batiment, en unites."""
        p = self.poly(way_id)
        return min(x for x, _ in p), min(y for _, y in p), max(x for x, _ in p), max(y for _, y in p)

    # --- relief ------------------------------------------------------------
    def altitude_reelle(self, lat, lon):
        """Altitude IGN (m) interpolee."""
        r = self.ign
        x = (lon - self.ign_lon0) * 111320 * math.cos(math.radians(self.ign_lat0))
        y = (lat - self.ign_lat0) * 110540
        n, pas, half = r["n"], r["pas_m"], r["demi_cote_m"]
        fx = min(max((x + half) / pas, 0), n - 1.001)
        fy = min(max((y + half) / pas, 0), n - 1.001)
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        a = r["altitudes"]
        z00, z10 = a[j * n + i], a[j * n + i + 1]
        z01, z11 = a[(j + 1) * n + i], a[(j + 1) * n + i + 1]
        return (z00 * (1 - tx) + z10 * tx) * (1 - ty) + (z01 * (1 - tx) + z11 * tx) * ty

    def z(self, x, y):
        """Hauteur du terrain naturel en unites de jeu."""
        return (self.altitude_reelle(*self.vers_latlon(x, y)) - self.alt_ref) * M


def obb(points):
    """Rectangle d'emprise minimal : (cx, cy, longueur, largeur, angle de la longueur)."""
    from make_blockout import convex_hull
    hull = convex_hull(points)
    best = None
    for (ax, ay), (bx, by) in zip(hull, hull[1:] + hull[:1]):
        a = math.atan2(by - ay, bx - ax)
        c, s = math.cos(a), math.sin(a)
        us = [x * c + y * s for x, y in hull]
        vs = [-x * s + y * c for x, y in hull]
        area = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or area < best[0]:
            u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
            cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
            best = (area, cu * c - cv * s, cu * s + cv * c, u1 - u0, v1 - v0, a)
    _, cx, cy, l, w, a = best
    if w > l:
        l, w, a = w, l, a + math.pi / 2
    return cx, cy, l, w, a
