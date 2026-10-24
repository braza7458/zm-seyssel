"""Le quartier des Pres Dombet : terrain IGN, routes, parkings, immeubles, maisons, vegetation, decor.

Tout est en unites de jeu dans le repere de geo.py. Renvoie des brushes
(listes de plans (normale, point, materiau [, projection])) et des entites (dicts).
Les brushes sont ranges par groupe (terrain, voirie, maisons...) : un prefab par groupe.
"""

import json
import math
import random

import bisect

import carrefour
import grille
import maisons
import monde
import sols
import voirie
from geo import ANNEXE, GARAGES, M, REF, Site, obb
from immeuble import H, Immeuble, bloc, mur_perce
from materiaux import MAT


def mats_immeuble():
    m = dict(MAT)
    m["facade"] = MAT["facade_beige"]
    return m


# --- geometrie generique -------------------------------------------------------

def pave(x0, y0, z0, x1, y1, z1, mat, faces=None):
    """Pave monde, faces = {'x-':..., 'z+':...}."""
    f = {k.replace("x", "u").replace("y", "v"): v for k, v in (faces or {}).items()}
    return bloc(x0, y0, z0, x1, y1, z1, mat, f)


def tourne(planes, angle, cx, cy, dz=0.0):
    c, s = math.cos(angle), math.sin(angle)
    out = []
    for pl in planes:
        n, p, mat = pl[:3]
        out.append(((n[0] * c - n[1] * s, n[0] * s + n[1] * c, n[2]),
                    (p[0] * c - p[1] * s + cx, p[0] * s + p[1] * c + cy, p[2] + dz), mat) + tuple(pl[3:]))
    return out


def prisme_triangle(a, b, c, z_bas, mat, mat_cotes=None):
    """Prisme vertical sous un triangle 3D (a, b, c) : terrain, routes."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = a, b, c
    # sens direct
    if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0:
        b, c = c, b
        (bx, by, bz), (cx, cy, cz) = b, c
    u = (bx - ax, by - ay, bz - az)
    v = (cx - ax, cy - ay, cz - az)
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    mc = mat_cotes or mat
    planes = [(n, a, mat), ((0, 0, -1), (ax, ay, z_bas), mc)]
    for (px, py, _), (qx, qy, _) in ((a, b), (b, c), (c, a)):
        planes.append(((qy - py, -(qx - px), 0), (px, py, z_bas), mc))
    return planes


def tronc_cone(cx, cy, zb, rb, zt, rt, mat, cotes=8):
    """Tronc de cone a 8 pans (houppiers des sapins et des peupliers)."""
    k = math.cos(math.pi / cotes)
    planes = [((0, 0, -1), (cx, cy, zb), mat), ((0, 0, 1), (cx, cy, zt), mat)]
    for j in range(cotes):
        t = 2 * math.pi * (j + 0.5) / cotes
        ab, at = rb * k, rt * k
        planes.append(((math.cos(t) * (zt - zb), math.sin(t) * (zt - zb), ab - at),
                       (cx + ab * math.cos(t), cy + ab * math.sin(t), zb), mat))
    return planes


def boite_obb(cx, cy, l, w, a):
    """Boite alignee sur les axes d'un rectangle presque aligne (0 ou 90 degres)."""
    if abs(math.cos(a)) > 0.7:
        return cx - l / 2, cy - w / 2, cx + l / 2, cy + w / 2
    return cx - w / 2, cy - l / 2, cx + w / 2, cy + l / 2


def dans_poly(x, y, poly):
    dedans = False
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            dedans = not dedans
    return dedans


# --- le quartier ---------------------------------------------------------------

class Quartier:
    X0, X1, Y0, Y1 = grille.X0, grille.X1, grille.Y0, grille.Y1   # cadre jouable
    PAS = grille.PAS
    VIS = (-7000, 8300)      # ce qui est modelise (maisons, routes, arbres) au-dela du cadre jouable

    # zones d'enrobe (unites, calees sur la grille du terrain)
    PARKING_BAS = (512, -1024, 1792, 2048)
    PARKING_HAUT = (1792, -768, 3072, 1024)     # 2,5 m plus haut, d'ou est prise la photo 1
    ALLEE_GARAGES = (1536, 1536, 1792, 3072)
    PARKING_NORD = (0, 3840, 1536, 4864)
    COUR_ECOLE = (1024, -4864, 3072, -1792)

    # le gameplay (docs/gameplay/zone-01-hlm.md) : rien de solide dans ces zones
    ZONES_GAMEPLAY = [
        ("disque", 2935, -12, 450), ("rect", 1950, 360, 2150, 840), ("disque", 2058, -398, 200),
        ("disque", 2292, 924, 250), ("disque", 2447, 941, 200), ("disque", 2456, -458, 150),
        ("disque", 3300, -200, 300),
    ]

    # immeubles : un seul gabarit, parametres releves sur la BD TOPO (docs/conception-v0.3.md, A.1)
    ELARGISSEMENT = 1.28   # profondeur des corps, comme demande pour l'espace de jeu
    HLM = [
        # nom, origine du nu de la facade, eu, ev, longueur, profondeur cadastrale, halls, genouillere, appartement, ascenseur, lucarnes
        ("batiment_1", (217, -1444), (0, 1), (-1, 0), 2944, 552, [520, 1424, 2416], 48, (1, 4, -1), 1, []),
        ("batiment_2", (-668, 3464), (1, 0), (0, -1), 1912, 456, [480, 1432], 0, (1, 3, -1), None, [268, 692, 1220, 1644]),
        ("batiment_3", (1763, 4432), (1, 0), (0, -1), 2896, 480, [496, 1456, 2408], 48, (1, 4, -1), None,
         [284, 708, 1244, 1668, 2196, 2620]),
    ]

    def __init__(self):
        self.site = Site()
        self.groupes = {}        # nom de groupe -> [brushes]
        self.entites = []
        self.immeubles = []
        self.emprises = []       # rectangles a garder libres (x0, y0, x1, y1, z_sol)
        self.aplanir = []        # rectangles ou le terrain est mis au niveau du rez-de-chaussee
        self.slots = []          # places de stationnement : (x, y, angle)
        self.maisons = []
        self.vegetation_bd = json.loads((REF / "ign" / "bdtopo_vegetation_couloir.json").read_text(encoding="utf-8"))
        random.seed(74910)

    # --- sorties -------------------------------------------------------------
    def ajoute(self, groupe, planes):
        self.groupes.setdefault(groupe, []).append(planes)

    @property
    def brushes(self):
        return [b for g in self.groupes.values() for b in g]

    def interdit(self, x, y, marge=0):
        for z in self.ZONES_GAMEPLAY:
            if z[0] == "disque" and math.hypot(x - z[1], y - z[2]) < z[3] + marge:
                return True
            if z[0] == "rect" and z[1] - marge < x < z[3] + marge and z[2] - marge < y < z[4] + marge:
                return True
        return False

    # --- relief ------------------------------------------------------------
    def hauteurs(self):
        """Hauteurs des sommets du quadtree : IGN 4 m dans le cadre, raster de 10 m, puis terre comprimee."""
        s = self.site
        self.relief = monde.Relief(s)
        self.leaves = monde.feuilles()
        self.index = {(t, x // t, y // t): (x, y, t) for x, y, t in self.leaves}
        self.hz, self.alt = {}, {}
        # rectangles aplanis, ranges par case de 4096 pour ne pas tout parcourir
        cases = {}
        for r in self.aplanir:
            for cx in range(int((r[0] - 128) // 4096), int((r[2] + 128) // 4096) + 1):
                for cy in range(int((r[1] - 128) // 4096), int((r[3] + 128) // 4096) + 1):
                    cases.setdefault((cx, cy), []).append(r)
        for (x, y) in monde.sommets(self.leaves):
            z = self.relief.sommet(x, y)
            f = monde.position_vraie(x, y)[2] if not monde.dans_cadre(x, y) else 1.0
            self.alt[(x, y)] = z / (M * f) + s.alt_ref
            for x0, y0, x1, y1, zs in cases.get((int(x // 4096), int(y // 4096)), ()):
                if x0 - 128 <= x <= x1 + 128 and y0 - 128 <= y <= y1 + 128:
                    z = zs - 2
            self.hz[(x, y)] = round(z)

    def feuille(self, x, y):
        for t in (256, 512, 1024, 2048, 4096, 8192):
            f = self.index.get((t, math.floor(x / t), math.floor(y / t)))
            if f:
                return f
        return None

    def z(self, x, y):
        """Hauteur exacte du terrain triangule en (x, y)."""
        f = self.feuille(x, y)
        if f is None:
            return self.relief.h0(x, y)
        x0, y0, t = f
        tx = min(max((x - x0) / t, 0), 1)
        ty = min(max((y - y0) / t, 0), 1)
        h = self.hz
        a, b, c, d = h[(x0, y0)], h[(x0 + t, y0)], h[(x0, y0 + t)], h[(x0 + t, y0 + t)]
        if (x0 // t + y0 // t) % 2 == 0:       # diagonale b-c
            if tx + ty <= 1:
                return a + (b - a) * tx + (c - a) * ty
            return d + (c - d) * (1 - tx) + (b - d) * (1 - ty)
        if tx >= ty:                            # diagonale a-d : triangle (a, b, d)
            return a + (b - a) * tx + (d - b) * ty
        return a + (d - c) * tx + (c - a) * ty

    def terrain(self):
        sols = [(self.PARKING_BAS, "asphalte"), (self.PARKING_HAUT, "asphalte"), (self.ALLEE_GARAGES, "asphalte"),
                (self.PARKING_NORD, "asphalte"), (self.COUR_ECOLE, "asphalte")]
        bois = [o["pts"] for o in self.vegetation_bd if "Bois" in o["nature"] or "For" in o["nature"]]
        for x, y, t in self.leaves:
            x1, y1 = x + t, y + t
            a = (x, y, self.hz[(x, y)])
            b = (x1, y, self.hz[(x1, y)])
            c = (x, y1, self.hz[(x, y1)])
            d = (x1, y1, self.hz[(x1, y1)])
            cx, cy = x + t / 2, y + t / 2
            mat = MAT["herbe"]
            i, j = x // t, y // t
            if monde.dans_cadre(cx, cy):
                for (r0, r1, r2, r3), m in sols:
                    if r0 <= cx <= r2 and r1 <= cy <= r3:
                        mat = MAT[m]
                if mat == MAT["herbe"] and (i * 7 + j * 3) % 11 == 0:
                    mat = MAT["herbe_sombre"]
            else:
                alt = sum(self.alt[k] for k in ((x, y), (x1, y), (x, y1), (x1, y1))) / 4 - self.site.alt_ref
                pente = max(abs(a[2] - d[2]), abs(b[2] - c[2])) / (t * 1.414)
                r = monde.ancre((cx, cy))[0]
                if r > monde.R0 and (alt > 420 or pente > 0.75):
                    mat = MAT["roche"]
                elif r > monde.R0 and (alt > 60 or pente > 0.3):
                    mat = MAT["foret"]
                elif any(dans_poly(cx, cy, pts) for pts in bois):
                    mat = MAT["foret"]
                elif (i * 7 + j * 3) % 11 == 0:
                    mat = MAT["herbe_sombre"]
            zb = min(-160, min(a[2], b[2], c[2], d[2]) - 96)
            if (i + j) % 2 == 0:
                self.ajoute("terrain", prisme_triangle(a, b, c, zb, mat))
                self.ajoute("terrain", prisme_triangle(b, d, c, zb, mat))
            else:
                self.ajoute("terrain", prisme_triangle(a, b, d, zb, mat))
                self.ajoute("terrain", prisme_triangle(a, d, c, zb, mat))

    def bordures(self):
        """Bordures de trottoir autour des parkings."""
        for x0, y0, x1, y1 in (self.PARKING_BAS, self.PARKING_HAUT, self.PARKING_NORD):
            for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x0, y1, x1, y1), (x0, y0, x0, y1)):
                n = max(1, int(math.dist((ax, ay), (bx, by)) // 128))
                for k in range(n):
                    px0, py0 = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
                    px1, py1 = ax + (bx - ax) * (k + 1) / n, ay + (by - ay) * (k + 1) / n
                    zz = (self.z(px0, py0) + self.z(px1, py1)) / 2
                    lx0, lx1 = sorted((px0, px1))
                    ly0, ly1 = sorted((py0, py1))
                    if ax == bx:
                        lx0, lx1 = ax - 6, ax + 6
                    else:
                        ly0, ly1 = ay - 6, ay + 6
                    mx, my = (lx0 + lx1) / 2, (ly0 + ly1) / 2
                    if any(e[0] - 8 < mx < e[2] + 8 and e[1] - 8 < my < e[3] + 8 for e in self.emprises):
                        continue
                    if self.interdit(mx, my) or self.dans_route(mx, my):
                        continue
                    self.ajoute("bordures", pave(lx0, ly0, zz - 24, lx1, ly1, zz + 6, MAT["bordure"]))

    def dans_route(self, x, y):
        return maisons._dist_route(self.routes_axes, x, y)[0] < 170

    # --- immeubles -----------------------------------------------------------
    def immeubles_hlm(self):
        s = self.site
        for nom, o, eu, ev, L, Dcad, halls, gen, appart, asc, lucarnes in self.HLM:
            D = round(Dcad * self.ELARGISSEMENT / 16) * 16
            imm = Immeuble(nom, o, eu, ev, L, D, halls, 5, 0, appart, asc, gen, lucarnes)
            pied = imm.monde(L / 2, -200, 0)
            z0 = 0 if nom == "batiment_1" else round(s.z(pied[0], pied[1]) / 8) * 8
            imm.z0 = z0
            rect = imm.emprise
            zmin = min(s.z(x, y) for x in (rect[0], rect[2]) for y in (rect[1], rect[3]))
            imm.z_fond = min(zmin, z0) - 192
            self.immeubles.append(imm)
            self.emprises.append(rect + (z0,))
            self.aplanir.append(rect + (z0,))

    def annexe_et_garages(self):
        s = self.site
        # annexe a toit plat, a moitie enterree dans le talus du parking du haut
        x0, y0, x1, y1 = boite_obb(*obb(s.poly(ANNEXE)[:-1]))
        cy = (y0 + y1) / 2
        zs = round(s.z(x0 - 64, cy) / 8) * 8
        self.annexe_boite = (x0, y0, x1, y1, zs)
        self.emprises.append((x0, y0, x1, y1, zs))
        haut = 184
        self.ajoute("annexes", pave(x0, y0, zs - 160, x1, y1, zs + haut, MAT["annexe"], {"z+": MAT["gravier_clair"]}))
        for (a0, b0, a1, b1) in ((x0 - 8, y0 - 8, x1 + 8, y0), (x0 - 8, y1, x1 + 8, y1 + 8),
                                 (x0 - 8, y0, x0, y1), (x1, y0, x1 + 8, y1)):
            self.ajoute("annexes", pave(a0, b0, zs + haut - 8, a1, b1, zs + haut + 16, MAT["annexe"]))
        self.facade_garages(x0, y0, y1, zs, 160, 120, 112, "annexes")

        # rangee de garages blancs le long de l'allee (photo 3)
        gx0, gy0, gx1, gy1 = boite_obb(*obb(s.poly(GARAGES)[:-1]))
        cy = (gy0 + gy1) / 2
        zg = round(s.z(gx0 - 128, cy) / 8) * 8
        self.emprises.append((gx0, gy0, gx1, gy1, zg))
        self.ajoute("annexes", pave(gx0, gy0, zg - 96, gx1, gy1, zg + 152, MAT["garages"]))
        self.ajoute("annexes", pave(gx0 - 24, gy0 - 24, zg + 152, gx1 + 24, gy1 + 24, zg + 164, MAT["garages"],
                                    {"z+": MAT["toit_plat"]}))
        self.facade_garages(gx0, gy0, gy1, zg, 136, 112, 104, "annexes")

    def facade_garages(self, x, y0, y1, zs, pas, larg, haut, groupe):
        """Facade de garages cote -x : porte basculante en retrait dans une baie, linteau, pilastres, descente d'eau.

        Le mur plein de l'annexe est deja pose ; on le double d'une peau de 10 u percee des baies."""
        n = int((y1 - y0) // pas)
        marge = (y1 - y0 - n * pas) / 2
        baies = []
        for k in range(n):
            g = y0 + marge + k * pas + (pas - larg) / 2
            baies.append((g, g + larg, zs, zs + haut))
        for br in mur_perce("v", y0, y1, x - 10, x, zs, zs + 152, baies, MAT["garages"]):
            self.ajoute(groupe, br)
        for g0, g1, za, zb in baies:
            # vantail basculant, en retrait de 4 u, avec son cadre blanc
            self.ajoute(groupe, pave(x - 4, g0 + 4, zs, x - 2, g1 - 4, zs + haut - 4, MAT["garage"]))
            for ya, yb in ((g0, g0 + 4), (g1 - 4, g1)):
                self.ajoute(groupe, pave(x - 12, ya, zs, x - 8, yb, zs + haut, MAT["cadre"]))
            self.ajoute(groupe, pave(x - 12, g0, zs + haut, x - 8, g1, zs + haut + 6, MAT["cadre"]))
            self.ajoute(groupe, pave(x - 14, g0 - 6, zs - 6, x - 6, g1 + 6, zs, MAT["dalle_balcon"]))   # seuil
        # pilastres entre les portes et descente d'eau aux extremites
        for k in range(n + 1):
            g = y0 + marge + k * pas
            self.ajoute(groupe, pave(x - 14, g - 6, zs, x - 10, g + 6, zs + 152, MAT["garages"]))
        self.ajoute(groupe, pave(x - 16, y0 + 6, zs, x - 12, y0 + 12, zs + 164, MAT["garde_corps"]))
        # bandeau de rive et gouttiere sous le toit
        self.ajoute(groupe, pave(x - 20, y0 - 4, zs + 150, x - 6, y1 + 4, zs + 170, MAT["rive"]))

    # --- chemins OSM ---------------------------------------------------------------
    def chemins(self):
        """Allees et sentiers d'OpenStreetMap qui ne sont pas deja dans la BD TOPO."""
        s = self.site
        for wid, w in s.ways.items():
            hw = w.get("tags", {}).get("highway")
            if hw not in ("service", "footway", "path", "pedestrian", "track"):
                continue
            pts = s.poly(wid)
            mid = pts[len(pts) // 2]
            if maisons._dist_route(self.routes_axes, *mid)[0] < 260:
                continue
            larg = 220 if hw in ("service", "track") else 90
            mat = MAT["asphalte"] if hw in ("service", "track") else MAT["gravier"]
            voirie.ruban(self, pts, larg, mat, 4, groupe="voirie")

    # --- vegetation --------------------------------------------------------------
    def libre(self, x, y, marge=96, visible=False):
        if visible:
            dans = monde.ancre((x, y))[0] <= monde.R0
        else:
            dans = monde.jouable(x, y, 200)
        return dans and all(not (e[0] - marge < x < e[2] + marge and e[1] - marge < y < e[3] + marge) for e in self.emprises)

    def sapin(self, x, y, hauteur=900, rayon=230):
        z = self.z(x, y)
        self.ajoute("vegetation", pave(x - 14, y - 14, z - 32, x + 14, y + 14, z + hauteur * 0.25, MAT["ecorce"]))
        etages = [(0.12, 1.0), (0.38, 0.78), (0.6, 0.55), (0.8, 0.32)]
        for k, (h0, r) in enumerate(etages):
            zb = z + hauteur * h0
            zt = z + hauteur * (etages[k + 1][0] + 0.06 if k + 1 < len(etages) else 1.0)
            rt = rayon * (etages[k + 1][1] * 0.75 if k + 1 < len(etages) else 0.06)
            self.ajoute("vegetation", tronc_cone(x, y, zb, rayon * r, zt, rt, MAT["feuillage"]))

    def peuplier(self, x, y, hauteur=590):
        z = self.z(x, y)
        self.ajoute("vegetation", pave(x - 10, y - 10, z - 32, x + 10, y + 10, z + 120, MAT["ecorce"]))
        self.ajoute("vegetation", tronc_cone(x, y, z + 100, 56, z + hauteur * 0.55, 74, MAT["feuillage_clair"]))
        self.ajoute("vegetation", tronc_cone(x, y, z + hauteur * 0.55, 74, z + hauteur, 8, MAT["feuillage_clair"]))

    def feuillu(self, x, y, hauteur, rayon):
        z = self.z(x, y)
        self.ajoute("vegetation", pave(x - 12, y - 12, z - 32, x + 12, y + 12, z + hauteur * 0.4, MAT["ecorce"]))
        self.ajoute("vegetation", tronc_cone(x, y, z + hauteur * 0.3, rayon * 0.6, z + hauteur * 0.65, rayon, MAT["feuillage_clair"]))
        self.ajoute("vegetation", tronc_cone(x, y, z + hauteur * 0.65, rayon, z + hauteur, rayon * 0.2, MAT["feuillage_clair"]))

    def modele(self, nom, x, y, angle=0.0, echelle=1.0, dz=0.0):
        self.entites.append({"classname": "misc_model", "model": nom,
                             "origin": f"{x:.1f} {y:.1f} {self.z(x, y) + dz:.1f}",
                             "angles": f"0 {angle:.1f} 0", "modelscale": f"{echelle:g}"})

    def vegetation(self):
        arbres = json.loads((REF / "ign" / "lidar_quartier.json").read_text(encoding="utf-8"))["arbres"]
        ligne = lambda y: 0.1303 * y - 1650  # noqa: E731  rangee de peupliers a l'est de l'avenue Borcier
        # rangee de peupliers de l'avenue, tous les 5,1 m, 12 m de haut
        y = -3358
        while y <= 4977:
            x = ligne(y)
            if self.libre(x, y, 64) and not self.interdit(x, y, 40) and not self.dans_route(x, y):
                self.peuplier(x, y, 590 * random.uniform(0.92, 1.08))
            y += 251
        for t in arbres:
            x, y, h, r, el = t["x"], t["y"], t["h_m"], t["rayon_m"], t["elancement"]
            if abs(x - ligne(y)) < 320 and -3500 < y < 5100:
                continue                      # deja dans la rangee de peupliers
            if (x, y) == (57, 2387) or not self.libre(x, y, 48, visible=True) or self.interdit(x, y, 60) or self.dans_route(x, y):
                continue
            proche = math.hypot(x - 2000, y - 500) < 4500
            if h >= 15 and el >= 2.2:
                self.sapin(x, y, h * 49.2, max(r, 4) * 49.2 * 0.9)
            elif proche and el < 2.2 and h >= 6:
                self.modele("p7_foliage_tree_albizia_tall_full", x, y, random.uniform(0, 360),
                            max(0.35, min(1.0, h * 0.0644)))
            elif proche and h < 6:
                self.modele(random.choice(["p7_foliage_tree_olive_small", "p7_foliage_tree_acacia_bush"]), x, y,
                            random.uniform(0, 360), 1.5)
            else:
                self.feuillu(x, y, h * 49.2, max(r, 2.5) * 49.2)
        self.vegetation_couloir()
        # haies
        for x, y in ((700, 2700), (820, 2760), (520, 2620), (2000, 3300), (-400, 2650)):
            if self.libre(x, y, 16) and not self.interdit(x, y, 40):
                self.modele("p7_foliage_hedge_round_48_48_36_vibrant", x, y, random.uniform(0, 360), 1.6)
        # touffes d'herbe sur les pelouses du coeur
        n = 0
        while n < 150:
            x = random.uniform(-1500, 4500)
            y = random.uniform(-2500, 3500)
            if not self.libre(x, y, 64) or self.interdit(x, y, 40) or self.dans_route(x, y):
                continue
            if any(z0 <= x <= z1 and w0 <= y <= w1 for z0, w0, z1, w1 in
                   (self.PARKING_BAS, self.PARKING_HAUT, self.ALLEE_GARAGES, self.PARKING_NORD)):
                continue
            self.modele(random.choice(["p7_foliage_grass_tussock_green_1", "p7_foliage_grass_tussock_green_2",
                                       "p7_foliage_grass_tussock_green_3", "p7_foliage_grass_flowers"]),
                        x, y, random.uniform(0, 360), random.uniform(0.8, 1.3))
            n += 1

    def vegetation_couloir(self):
        """Bois, haies et arbres du couloir d'apres la BD TOPO (zones de vegetation) et OpenStreetMap."""
        rnd = random.Random(7491)
        nb_arbres = 0
        for o in self.vegetation_bd:
            nat, pts = o["nature"], o["pts"]
            if all(monde.ancre(p)[0] > monde.R0 for p in pts):
                continue
            if "Haie" in nat:
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    L = math.hypot(b[0] - a[0], b[1] - a[1])
                    n = int(L // 150)
                    for k in range(n):
                        x, y = a[0] + (b[0] - a[0]) * (k + 0.5) / n, a[1] + (b[1] - a[1]) * (k + 0.5) / n
                        if self.libre(x, y, 30, visible=True) and not self.dans_route(x, y):
                            z = self.z(x, y)
                            self.ajoute("vegetation", pave(x - 50, y - 50, z - 12, x + 50, y + 50, z + 95, MAT["feuillage"]))
                continue
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            pas = 700
            x = min(xs)
            while x < max(xs) and nb_arbres < 420:
                y = min(ys)
                while y < max(ys):
                    px, py = x + rnd.uniform(-220, 220), y + rnd.uniform(-220, 220)
                    if dans_poly(px, py, [tuple(p) for p in pts]) and self.libre(px, py, 60, visible=True) \
                            and not self.dans_route(px, py) and not self.interdit(px, py, 60):
                        h = rnd.uniform(9, 17) * 49.2
                        if rnd.random() < 0.25:
                            self.sapin(px, py, h, rnd.uniform(3.2, 4.5) * 49.2)
                        else:
                            self.feuillu(px, py, h, rnd.uniform(3.5, 5.5) * 49.2)
                        nb_arbres += 1
                    y += pas
                x += pas
        # arbres isoles et rangees d'OpenStreetMap
        osm = json.loads((REF / "osm" / "arbres_couloir.json").read_text())
        for x, y in osm["arbres"]:
            if self.libre(x, y, 40, visible=True) and not self.dans_route(x, y):
                self.feuillu(x, y, rnd.uniform(7, 14) * 49.2, rnd.uniform(3, 4.5) * 49.2)
        for rang in osm["rangees"]:
            for a, b in zip(rang, rang[1:]):
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                n = max(1, int(L // 330))
                for k in range(n + 1):
                    x, y = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
                    if self.libre(x, y, 40, visible=True) and not self.dans_route(x, y):
                        self.feuillu(x, y, rnd.uniform(8, 13) * 49.2, 3.5 * 49.2)

    # --- mobilier et voitures --------------------------------------------------------
    def decor(self):
        couleurs = ["grey", "blue", "black", "green"]
        # voitures sur les places marquees (55 % occupees), a l'echelle 1,25
        for i, (x, y, ang) in enumerate(self.slots):
            if (i * 7 + int(abs(x)) // 13) % 20 >= 11:
                continue
            if not self.libre(x, y, 20) or self.interdit(x, y, 90) or self.dans_route(x, y):
                continue
            self.modele(f"veh_t7_civ_car_compact_{couleurs[(i * 5) % 4]}", x, y, ang, 1.25)
        # rangee en epi devant le batiment 1, d'apres les photos de l'utilisateur
        b1 = self.immeubles[0]
        halls_y = [b1.monde((b1.section(k)[1] + b1.section(k)[2]) / 2, 0, 0)[1] for k in range(b1.halls)]
        y = -1380
        while y < 1400:
            if all(abs(y - hy) > 220 for hy in halls_y) and self.libre(560, y, 20) and not self.interdit(560, y, 90):
                self.modele(f"veh_t7_civ_car_compact_{random.choice(couleurs)}", 560, y, random.choice((0, 180)), 1.25)
            y += 260
        # grands bacs a dechets gris pres de la facade
        for x, y in ((2300, 150), (2300, 330)):
            z = self.z(x, y)
            self.ajoute("mobilier", pave(x - 62, y - 62, z, x + 62, y + 62, z + 98, MAT["conteneur"]))
            self.ajoute("mobilier", pave(x - 66, y - 66, z + 98, x + 66, y + 66, z + 106, MAT["metal"]))
        # lampadaires le long des voies principales
        for tr, nom in self.routes_noms:
            pts = voirie.reechantillonne(tr, 40)
            dist = 0
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                dist += math.hypot(bx - ax, by - ay)
                if dist < 1800:
                    continue
                dist = 0
                L = math.hypot(bx - ax, by - ay) or 1
                nx, ny = -(by - ay) / L, (bx - ax) / L
                dec = voirie.NOMS.get(nom, 300) / 2 + 110
                x, y = bx + nx * dec, by + ny * dec
                if self.libre(x, y, 24) and not self.interdit(x, y, 40):
                    z = self.z(x, y)
                    self.ajoute("mobilier", pave(x - 4, y - 4, z - 16, x + 4, y + 4, z + 270, MAT["metal"]))
                    xa, xb = sorted((x - 4, x + 56 * (1 if nx < 0 else -1)))
                    self.ajoute("mobilier", pave(xa, y - 4, z + 262, xb, y + 4, z + 270, MAT["metal"]))
        # bancs sur les pelouses
        for x, y, a in ((-500, 1900, 0), (1000, 3000, 90), (-600, -1900, 0)):
            if self.libre(x, y, 16):
                self.modele("p7_bench_modern_01", x, y, a, 1.25)

    # --- zone de test (debut de partie) -------------------------------------------
    ARMES_MUR = ["pistol_burst", "pistol_fullauto", "smg_standard", "smg_fastfire", "smg_versatile", "shotgun_pump",
                 "ar_standard", "ar_cqb", "ar_longburst", "ar_marksman", "frag_grenade", "bouncingbetty", "bowie"]
    ATOUTS_PLUS = ["vending_additionalprimaryweapon_struct", "vending_deadshot_struct", "vending_marathon_struct"]

    def zone_test(self):
        """Mur d'armes au bord sud du parking du haut, machine a points, rangee d'atouts supplementaires.

        Les entites (prefabs d'armes et d'atouts, declencheur) sont posees par build_map.py a partir de
        self.test ; ici seulement les brushes."""
        x0, x1, y = 2120, 3060, -716
        self.test = {"armes": [], "atouts": [], "argent": None}
        n = len(self.ARMES_MUR)
        pas = (x1 - x0) / n
        for k in range(n):
            xa, xb = x0 + k * pas, x0 + (k + 1) * pas
            z = min(self.z(xa, y), self.z(xb, y), self.z(xa, y + 16), self.z(xb, y + 16))
            # trois paves empiles, sans saillie : socle, mur, chaperon
            self.ajoute("test", pave(xa, y - 16, z - 40, xb, y, z + 12, MAT["socle"]))
            self.ajoute("test", pave(xa, y - 16, z + 12, xb, y, z + 170, MAT["facade_blanche"]))
            self.ajoute("test", pave(xa, y - 16, z + 170, xb, y, z + 182, MAT["appui"]))
            xc = (xa + xb) / 2
            self.test["armes"].append((self.ARMES_MUR[k], xc, y + 1, self.z(xc, y + 40)))
        # machine a points : borne grise avec un panneau rouge, pres du spawn
        mx, my = 2700, -560
        z = self.z(mx, my)
        self.ajoute("test", pave(mx - 28, my - 20, z - 8, mx + 28, my + 20, z + 120, MAT["conteneur"], {"y+": MAT["volet_vert"]}))
        self.ajoute("test", pave(mx - 28, my - 20, z + 120, mx + 28, my + 20, z + 128, MAT["metal"]))
        self.test["argent"] = (mx, my + 20, z)
        # atouts supplementaires : deuxieme rangee, face aux premiers
        for k, nom in enumerate(self.ATOUTS_PLUS):
            ax, ay = 2300, 404 + k * 128
            self.test["atouts"].append((nom, ax, ay, self.z(ax, ay)))

    # --- decor lointain et limites ---------------------------------------------------
    def montagnes(self):
        """Murs invisibles tout autour de la zone jouable (cadre + couloir)."""
        from voirie import boite_orientee
        pas = 160
        X0, X1, Y0, Y1 = self.X0, self.X1, self.Y0, self.Y1
        # bord du cadre, interrompu la ou le couloir s'y raccorde
        for (ax, ay, bx, by) in ((X0, Y0, X1, Y0), (X1, Y0, X1, Y1), (X1, Y1, X0, Y1), (X0, Y1, X0, Y0)):
            n = int(math.hypot(bx - ax, by - ay) // pas)
            for k in range(n):
                px, py = ax + (bx - ax) * (k + 0.5) / n, ay + (by - ay) * (k + 0.5) / n
                if monde.dist_chemin((px, py))[0] < monde.WP + 60:
                    continue
                self._mur(px, py, math.degrees(math.atan2(by - ay, bx - ax)), math.hypot(bx - ax, by - ay) / n + 8)
        # cotes du couloir et bout
        sp = monde.SPINE
        pts = voirie.reechantillonne(sp, 120)
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            for sens in (1, -1):
                px, py = (a[0] + b[0]) / 2 + nx * monde.WP * sens, (a[1] + b[1]) / 2 + ny * monde.WP * sens
                if monde.dans_cadre(px, py) or monde.dist_chemin((px, py))[0] < monde.WP - 40:
                    continue
                self._mur(px, py, ang, L + 8)
        # bouchon au bout du couloir
        a, b = pts[-2], pts[-1]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        n = int(2 * monde.WP // pas)
        for k in range(n):
            off = -monde.WP + (k + 0.5) * 2 * monde.WP / n
            self._mur(b[0] + tx * monde.WP * 0.5 - ty * off, b[1] + ty * monde.WP * 0.5 + tx * off,
                      math.degrees(math.atan2(ty, tx)) + 90, pas + 8)

    def eau(self):
        """Plan d'eau au niveau du Rhone (252,3 m) : visible seulement la ou le terrain est plus bas."""
        niveau = (252.3 - self.site.alt_ref) * M
        x0, y0, x1, y1 = monde.boite()
        self.ajoute("eau", pave(x0, y0, niveau - 8, x1, y1, niveau, MAT["eau"]))

    def _mur(self, x, y, ang, longueur):
        from voirie import boite_orientee
        boite_orientee(self, "murs", x, y, longueur, 32, 2600, ang, MAT["clip"], dz=-300)

    def construire(self):
        bd = json.loads((REF / "ign" / "bdtopo_quartier.json").read_text(encoding="utf-8"))
        self.relief = monde.Relief(self.site)
        self.osm_routes = voirie.routes_osm(self)
        self.routes_axes = [pts for hw, nom, pts, acces, oneway in self.osm_routes if hw in voirie.VEHICULE]
        self.routes_noms = [(pts, nom) for hw, nom, pts, acces, oneway in self.osm_routes if hw in voirie.TROTTOIRS and nom]
        self.immeubles_hlm()
        self.annexe_et_garages()
        self.nb_fixes = len(self.emprises)
        maisons.preparer(self)
        self.hauteurs()
        self.terrain()
        voirie.construire(self)
        voirie.barrages(self)
        self.bordures()
        for imm in self.immeubles:
            imm.construire(mats_immeuble())
            self.entites += imm.entites
        maisons.construire(self)
        carrefour.construire(self)
        sols.construire(self)
        self.vegetation()
        self.zone_test()
        self.decor()
        self.montagnes()
        self.eau()
        return self
