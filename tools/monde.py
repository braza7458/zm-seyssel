"""Le monde de la map : quartier (cadre) + couloir jusqu'au Carrefour, et terrain a mailles variables.

Le chemin (reference/osm/spine.json) suit les vraies routes de la rue des Pres Dombet au Carrefour
(route de Geneve). La zone jouable est le cadre du quartier plus une bande de demi-largeur WP autour du
chemin. Le terrain est un quadtree : mailles de 256 dans le cadre, 512 dans la bande, puis de plus en plus
grosses. Au-dela de R0 de la zone jouable, la terre est comprimee (loi de grille.py) a partir du point le
plus proche du chemin : les montagnes gardent leur taille apparente.
"""

import json
import math

import grille
from geo import M, REF

X0, X1, Y0, Y1 = grille.X0, grille.X1, grille.Y0, grille.Y1
R0, BORD = grille.R0, grille.BORD
WP = 3600                       # demi-largeur jouable du couloir
PAS_RASTER = 10 * M             # altitude IGN echantillonnee tous les 10 m

SPINE = [tuple(p) for p in json.loads((REF / "osm" / "spine.json").read_text())]
SQUELETTE = [(0.0, 0.0)] + SPINE


def _seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1.0
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    q = (a[0] + t * dx, a[1] + t * dy)
    return math.hypot(p[0] - q[0], p[1] - q[1]), q


def dist_chemin(p, ligne=SPINE):
    """(distance, point le plus proche) au chemin."""
    best = (1e18, None)
    for a, b in zip(ligne, ligne[1:]):
        d, q = _seg(p, a, b)
        if d < best[0]:
            best = (d, q)
    return best


def dist_cadre(p):
    """(distance, point le plus proche) au cadre du quartier ; 0 a l'interieur."""
    qx = min(max(p[0], X0), X1)
    qy = min(max(p[1], Y0), Y1)
    return math.hypot(p[0] - qx, p[1] - qy), (qx, qy)


def dans_cadre(x, y):
    return X0 <= x <= X1 and Y0 <= y <= Y1


def jouable(x, y, marge=0):
    """Dans le cadre ou dans la bande autour du chemin, a marge pres vers l'interieur."""
    if X0 + marge <= x <= X1 - marge and Y0 + marge <= y <= Y1 - marge:
        return True
    return dist_chemin((x, y))[0] <= WP - marge


def ancre(p):
    """(distance, point d'ancrage) : le point le plus proche de la zone jouable elargie (cadre + chemin)."""
    d1, q1 = dist_cadre(p)
    if d1 == 0:
        return 0.0, p
    d2, q2 = dist_chemin(p)
    return (d1, q1) if d1 <= d2 else (d2, q2)


def position_vraie(x, y):
    """(x_vrai, y_vrai, facteur d'echelle des hauteurs) du point de jeu (x, y)."""
    r, q = ancre((x, y))
    if r <= R0:
        return x, y, 1.0
    rc = min(r, 13400.0)
    d = grille.distance_vraie(rc)
    ux, uy = (x - q[0]) / r, (y - q[1]) / r
    return q[0] + ux * d, q[1] + uy * d, rc / d


def dist_jouable(x, y):
    """Distance a la zone jouable (0 dedans)."""
    d1, _ = dist_cadre((x, y))
    d2 = max(0.0, dist_chemin((x, y))[0] - WP)
    return min(d1, d2)


def loi_taille(d):
    """Taille de maille voulue a la distance d de la zone jouable."""
    if d <= 1500:
        return 512
    if d <= 4500:
        return 1024
    if d <= R0:
        return 2048
    if d <= 15000:
        return 4096
    return 8192


def boite():
    xs = [p[0] for p in SQUELETTE] + [X0, X1]
    ys = [p[1] for p in SQUELETTE] + [Y0, Y1]
    return min(xs) - BORD, min(ys) - BORD, max(xs) + BORD, max(ys) + BORD


def feuilles():
    """Mailles du terrain : liste de (x0, y0, taille), alignees sur la grille de 256."""
    bx0, by0, bx1, by1 = boite()
    racine = 8192
    out = []

    def tester(x0, y0, t):
        cx, cy = x0 + t / 2, y0 + t / 2
        demi = t * 0.7072
        # trop loin du squelette : on n'y met rien
        r = min(dist_cadre((cx, cy))[0], dist_chemin((cx, cy), SQUELETTE)[0]) - demi
        if r > BORD:
            return
        chev = not (x0 >= X1 or x0 + t <= X0 or y0 >= Y1 or y0 + t <= Y0)
        dedans = X0 <= x0 and x0 + t <= X1 and Y0 <= y0 and y0 + t <= Y1
        if dedans and t == 256:
            out.append((x0, y0, t))
            return
        if chev:
            cible = 256
        else:
            cible = loi_taille(max(0.0, dist_jouable(cx, cy) - demi))
        if t <= cible:
            out.append((x0, y0, t))
            return
        h = t // 2
        for dx in (0, h):
            for dy in (0, h):
                tester(x0 + dx, y0 + dy, h)

    ix0, iy0 = math.floor(bx0 / racine), math.floor(by0 / racine)
    ix1, iy1 = math.ceil(bx1 / racine), math.ceil(by1 / racine)
    for ix in range(ix0, ix1):
        for iy in range(iy0, iy1):
            tester(ix * racine, iy * racine, racine)
    return out


def sommets(fs):
    """Sommets (x, y) de toutes les mailles."""
    s = set()
    for x, y, t in fs:
        for dx in (0, t):
            for dy in (0, t):
                s.add((x + dx, y + dy))
    return s


# --- raster d'altitude (zone a l'echelle reelle) -------------------------------------

def noeuds_raster(marge=1200):
    """Noeuds (i, j) du raster de 10 m a moins de R0 + marge de la zone jouable."""
    bx0, by0, bx1, by1 = boite()
    out = []
    for i in range(int(bx0 // PAS_RASTER) - 1, int(bx1 // PAS_RASTER) + 2):
        for j in range(int(by0 // PAS_RASTER) - 1, int(by1 // PAS_RASTER) + 2):
            p = (i * PAS_RASTER, j * PAS_RASTER)
            if ancre(p)[0] <= R0 + marge:
                out.append((i, j))
    return out


class Relief:
    """Altitude (unites de jeu) en tout point : cadre (IGN 4 m), raster de 10 m, puis terre comprimee."""

    def __init__(self, site):
        self.site = site
        data = json.loads((REF / "ign" / "relief_monde.json").read_text())
        self.raster = {tuple(map(int, k.split(","))): v for k, v in data["raster"].items()}
        self.lointain = {tuple(map(int, k.split(","))): v for k, v in data["lointain"].items()}

    def _raster(self, x, y):
        fx, fy = x / PAS_RASTER, y / PAS_RASTER
        i, j = math.floor(fx), math.floor(fy)
        tx, ty = fx - i, fy - j
        try:
            a, b = self.raster[(i, j)], self.raster[(i + 1, j)]
            c, d = self.raster[(i, j + 1)], self.raster[(i + 1, j + 1)]
        except KeyError:
            return None
        alt = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
        return (alt - self.site.alt_ref) * M

    def h0(self, x, y):
        """Hauteur du terrain naturel, a l'echelle reelle (sert aux maisons et aux routes)."""
        if dans_cadre(x, y):
            return self.site.z(x, y)
        h = self._raster(x, y)
        if h is not None:
            return h
        return self.sommet(x, y)

    def sommet(self, x, y):
        """Hauteur d'un sommet de maille (avec compression au-dela de R0)."""
        if dans_cadre(x, y):
            return self.site.z(x, y)
        r, _ = ancre((x, y))
        if r <= R0:
            h = self._raster(x, y)
            if h is not None:
                return h
        a = self.lointain.get((int(x), int(y)))
        if a is None:
            raise KeyError(f"altitude manquante en ({x}, {y}) : relancer tools/corridor_donnees.py")
        f = position_vraie(x, y)[2]
        return (a - self.site.alt_ref) * M * f
