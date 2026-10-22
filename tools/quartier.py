"""Le quartier des Pres Dombet : terrain IGN, routes, parkings, immeubles, vegetation, decor.

Tout est en unites de jeu dans le repere de geo.py. Renvoie des brushes
(listes de plans (normale, point, materiau)) et des entites (dicts).
"""

import math
import random

from geo import ANNEXE, BAT1, BAT2, BAT3, GARAGES, M, Site, obb
from immeuble import H, Immeuble, bloc
from make_blockout import convex_hull

# --- materiaux ---------------------------------------------------------------
MAT = {
    # terrain et voirie
    "herbe": "core_grass_med", "herbe_sombre": "core_grass_dark", "terre": "core_dirt_med",
    "asphalte": "t7_asphalt_dirty_dark_desert", "trottoir": "t7_concrete_sidewalk_02",
    "bordure": "t7_street_concrete_curb_01a", "montagne": "core_grass_dark", "ciel": "sky",
    "clip": "clip_player",
    # immeubles
    "facade_beige": "t7_plaster_smooth_light_01", "facade_blanche": "t7_concrete_worn_painted_white",
    "socle": "t7_brick_worn_heavy_grout_brown_wet", "panneau": "t7_wood_panel_01_stain_brown_drk",
    "loggia": "t7_drywall_painted_brown_01", "fenetre": "core_window_opaque", "vitre": "core_glass_plain_trans",
    "appui": "t7_concrete_trim_beveled_03", "volet": "t7_drywall_painted_beige_01",
    "garage": "core_door_metal_light", "porte": "core_door_wood_dark", "porte_asc": "t7_metal_bare_stainless_steel_brushed",
    "garde_corps": "t7_metal_worn_iron_dark", "dalle_balcon": "t7_concrete_floor_sealed_01",
    "balcon": "t7_concrete_worn_painted_white", "toit": "core_roof_dark", "rive": "t7_wood_trim_dark_brown",
    "cheminee": "t7_plaster_smooth_light_01", "auvent": "t7_metal_paint_worn_grey_dk",
    # halls (creme, comme dans la realite)
    "hall_sol": "t7_stone_travertine", "hall_mur": "t7_drywall_base_cream", "plafond": "t7_drywall_painted_white_01",
    "rampe": "t7_metal_bare_stainless_steel_brushed", "boites": "t7_metal_painted_clean_white",
    "dalle": "t7_concrete_floor_sealed_01",
    # ascenseur
    "gaine": "t7_concrete_floor_sealed_01", "cabine": "t7_metal_bare_stainless_steel_brushed",
    "cabine_sol": "t7_metal_floor_square_pattern_01",
    # appartements
    "appart_mur": "t7_drywall_painted_white_01", "sol_entree": "core_tile_light", "sol_cuisine": "t7_ceramic_tiles_16x16",
    "sol_sdb": "t7_ceramic_tile_shower_white", "sol_chambre": "t7_wood_veneer_sugarpine_matte",
    "faience": "t7_ceramic_tile_large_white", "meuble": "t7_wood_panel_01_stain_brown_drk",
    # annexe, garages, voisins, vegetation
    "annexe": "t7_concrete_poured_bunker_paint_01_grey_lt", "gravier": "t7_stone_pebbles_01",
    "garages": "t7_concrete_worn_painted_white", "voisin": "t7_plaster_rough_worn_01", "voisin_toit": "core_roof_med",
    "ecole": "t7_concrete_wall_weathered_01_wet", "ecorce": "t7_wood_beam_worn_oak",
    "feuillage": "core_grass_dark", "feuillage_clair": "core_grass_med", "conteneur": "t7_metal_paint_worn_grey_dk",
    "metal": "t7_metal_bare_graphite_matte",
}


def mats_immeuble(style):
    m = dict(MAT)
    m["facade"] = MAT["facade_beige"] if style == "beige" else MAT["facade_blanche"]
    return m


# --- geometrie generique -------------------------------------------------------

def pave(x0, y0, z0, x1, y1, z1, mat, faces=None):
    """Pave monde, faces = {'x-':..., 'z+':...}."""
    f = {k.replace("x", "u").replace("y", "v"): v for k, v in (faces or {}).items()}
    return bloc(x0, y0, z0, x1, y1, z1, mat, f)


def tourne(planes, angle, cx, cy, dz=0.0):
    c, s = math.cos(angle), math.sin(angle)
    out = []
    for n, p, mat in planes:
        out.append(((n[0] * c - n[1] * s, n[0] * s + n[1] * c, n[2]),
                    (p[0] * c - p[1] * s + cx, p[0] * s + p[1] * c + cy, p[2] + dz), mat))
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
    X0, X1, Y0, Y1 = -4608, 5888, -4608, 5888
    PAS = 256

    # zones dessinees d'apres les photos (unites, calees sur la grille du terrain)
    PARKING_BAS = (256, -1536, 768, 1536)       # le long de la facade est du batiment 1
    PARKING_HAUT = (1792, -768, 3072, 1024)     # 2,5 m plus haut, d'ou est prise la photo 1
    ALLEE_GARAGES = (1536, 1536, 1792, 3072)

    def __init__(self):
        self.site = Site()
        self.brushes = []        # [(planes)]
        self.entites = []
        self.immeubles = []
        self.emprises = []       # rectangles a garder libres (x0, y0, x1, y1, z_sol)
        self.aplanir = []        # rectangles ou le terrain est mis au niveau du rez-de-chaussee
        random.seed(74910)

    # --- relief ------------------------------------------------------------
    def hauteurs(self):
        s = self.site
        nx = (self.X1 - self.X0) // self.PAS + 1
        ny = (self.Y1 - self.Y0) // self.PAS + 1
        self.hz = {}
        for j in range(ny):
            for i in range(nx):
                x, y = self.X0 + i * self.PAS, self.Y0 + j * self.PAS
                z = s.z(x, y)
                for x0, y0, x1, y1, zs in self.aplanir:
                    if x0 - 128 <= x <= x1 + 128 and y0 - 128 <= y <= y1 + 128:
                        z = zs - 2
                self.hz[(i, j)] = round(z)
        self.nx, self.ny = nx, ny

    def z(self, x, y):
        """Hauteur exacte du terrain triangule en (x, y)."""
        fx = min(max((x - self.X0) / self.PAS, 0), self.nx - 1.0001)
        fy = min(max((y - self.Y0) / self.PAS, 0), self.ny - 1.0001)
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        h = self.hz
        if tx + ty <= 1:
            return h[(i, j)] + (h[(i + 1, j)] - h[(i, j)]) * tx + (h[(i, j + 1)] - h[(i, j)]) * ty
        return h[(i + 1, j + 1)] + (h[(i, j + 1)] - h[(i + 1, j + 1)]) * (1 - tx) + (h[(i + 1, j)] - h[(i + 1, j + 1)]) * (1 - ty)

    def terrain(self):
        P = self.PAS
        sols = [(self.PARKING_BAS, "asphalte"), (self.PARKING_HAUT, "asphalte"), (self.ALLEE_GARAGES, "asphalte")]
        for j in range(self.ny - 1):
            for i in range(self.nx - 1):
                x, y = self.X0 + i * P, self.Y0 + j * P
                a = (x, y, self.hz[(i, j)])
                b = (x + P, y, self.hz[(i + 1, j)])
                c = (x, y + P, self.hz[(i, j + 1)])
                d = (x + P, y + P, self.hz[(i + 1, j + 1)])
                mat = MAT["herbe"]
                cx, cy = x + P / 2, y + P / 2
                for (x0, y0, x1, y1), m in sols:
                    if x0 <= cx <= x1 and y0 <= cy <= y1:
                        mat = MAT[m]
                if mat == MAT["herbe"] and (i * 7 + j * 3) % 11 == 0:
                    mat = MAT["herbe_sombre"]
                zb = min(a[2], b[2], c[2], d[2]) - 96
                self.brushes.append(prisme_triangle(a, b, c, zb, mat))
                self.brushes.append(prisme_triangle(b, d, c, zb, mat))

    def bordures(self):
        """Bordures de trottoir autour des parkings."""
        for x0, y0, x1, y1 in (self.PARKING_BAS, self.PARKING_HAUT):
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
                    if any(e[0] - 8 < (lx0 + lx1) / 2 < e[2] + 8 and e[1] - 8 < (ly0 + ly1) / 2 < e[3] + 8 for e in self.emprises):
                        continue
                    self.brushes.append(pave(lx0, ly0, zz - 24, lx1, ly1, zz + 6, MAT["bordure"]))

    def routes(self):
        s = self.site
        for wid, w in s.ways.items():
            hw = w.get("tags", {}).get("highway")
            if not hw or hw in ("steps",):
                continue
            larg = {"secondary": 300, "tertiary": 280, "residential": 260, "service": 200}.get(hw, 80)
            mat = MAT["trottoir"] if larg == 80 else MAT["asphalte"]
            pts = s.poly(wid)
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                L = math.dist((ax, ay), (bx, by))
                if L < 1:
                    continue
                n = max(1, int(L // 128))
                nx_, ny_ = -(by - ay) / L * larg / 2, (bx - ax) / L * larg / 2
                for k in range(n):
                    p0 = (ax + (bx - ax) * k / n, ay + (by - ay) * k / n)
                    p1 = (ax + (bx - ax) * (k + 1) / n, ay + (by - ay) * (k + 1) / n)
                    quad = [(p0[0] - nx_, p0[1] - ny_), (p1[0] - nx_, p1[1] - ny_), (p1[0] + nx_, p1[1] + ny_), (p0[0] + nx_, p0[1] + ny_)]
                    if not all(self.X0 + 64 < x < self.X1 - 64 and self.Y0 + 64 < y < self.Y1 - 64 for x, y in quad):
                        continue
                    if any(e[0] < x < e[2] and e[1] < y < e[3] for x, y in quad for e in self.emprises):
                        continue
                    q3 = [(x, y, self.z(x, y) + 5) for x, y in quad]
                    zb = min(p[2] for p in q3) - 24
                    self.brushes.append(prisme_triangle(q3[0], q3[1], q3[2], zb, mat))
                    self.brushes.append(prisme_triangle(q3[0], q3[2], q3[3], zb, mat))

    # --- immeubles -----------------------------------------------------------
    def immeubles_hlm(self):
        s = self.site
        specs = [
            # nom, way, halls, niveaux, style, appartement (hall, etage, cote), ascenseur, facade des halls
            ("batiment_1", BAT1, 3, 5, "beige", (1, 4, 1), 1, "+x"),
            ("batiment_2", BAT2, 2, 5, "blanc", (0, 3, -1), None, "+y"),
            ("batiment_3", BAT3, 3, 6, "blanc", (0, 5, -1), None, "+y"),
        ]
        for nom, wid, halls, niv, style, appart, asc, cote_halls in specs:
            cx, cy, l, w, a = obb(s.poly(wid)[:-1])
            L = round(l / halls / 32) * 32 * halls          # sections multiples de 32
            D = round(w * 1.28 / 16) * 16                    # elargi comme demande (x1,6 au total)
            if cote_halls == "+x":
                # batiment 1 : la facade des halls (est) reste en place, on elargit vers l'ouest
                x_halls = cx + w / 2
                origine, eu, ev = (x_halls, cy - L / 2), (0, 1), (-1, 0)
                rect = (x_halls - D, cy - L / 2, x_halls, cy + L / 2)
                z0 = 0
                pied = (x_halls + 120, cy)
            else:
                y_halls = cy + D / 2
                origine, eu, ev = (cx - L / 2, y_halls), (1, 0), (0, -1)
                rect = (cx - L / 2, y_halls - D, cx + L / 2, y_halls)
                pied = (cx, y_halls + 120)
                z0 = round(s.z(*pied) / 8) * 8
            zmin = min(s.z(x, y) for x in (rect[0], rect[2]) for y in (rect[1], rect[3]))
            imm = Immeuble(nom, origine, eu, ev, L, D, halls, niv, z0, style, appart, asc, z_sol_min=min(zmin, z0))
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
        self.brushes.append(pave(x0, y0, zs - 160, x1, y1, zs + haut, MAT["annexe"], {"z+": MAT["gravier"]}))
        for (a0, b0, a1, b1) in ((x0 - 8, y0 - 8, x1 + 8, y0), (x0 - 8, y1, x1 + 8, y1 + 8),
                                 (x0 - 8, y0, x0, y1), (x1, y0, x1 + 8, y1)):
            self.brushes.append(pave(a0, b0, zs + haut - 8, a1, b1, zs + haut + 16, MAT["annexe"]))
        n = int((y1 - y0) // 160)
        for k in range(n):
            g = y0 + (y1 - y0 - n * 160) / 2 + k * 160 + 16
            self.brushes.append(pave(x0 - 4, g, zs, x0, g + 128, zs + 112, MAT["garage"]))

        # rangee de garages blancs le long de l'allee (photo 3)
        gx0, gy0, gx1, gy1 = boite_obb(*obb(s.poly(GARAGES)[:-1]))
        cy = (gy0 + gy1) / 2
        zg = round(s.z(gx0 - 128, cy) / 8) * 8
        self.emprises.append((gx0, gy0, gx1, gy1, zg))
        self.brushes.append(pave(gx0, gy0, zg - 96, gx1, gy1, zg + 152, MAT["garages"]))
        self.brushes.append(pave(gx0 - 24, gy0 - 24, zg + 152, gx1 + 24, gy1 + 24, zg + 164, MAT["garages"], {"z+": MAT["gravier"]}))
        n = int((gy1 - gy0) // 136)
        for k in range(n):
            g = gy0 + (gy1 - gy0 - n * 136) / 2 + k * 136 + 12
            self.brushes.append(pave(gx0 - 4, g, zg, gx0, g + 112, zg + 104, MAT["garage"]))

    def voisins(self):
        s = self.site
        ignorer = {BAT1, BAT2, BAT3, ANNEXE, GARAGES}
        for wid, w in s.ways.items():
            tags = w.get("tags", {})
            if "building" not in tags or wid in ignorer:
                continue
            poly = s.poly(wid)[:-1]
            if len(poly) < 3 or not all(self.X0 + 128 < x < self.X1 - 128 and self.Y0 + 128 < y < self.Y1 - 128 for x, y in poly):
                continue
            cx, cy, l, wd, a = obb(poly)
            if l < 120 or wd < 120:
                continue
            aire = l * wd / M / M
            zb = min(self.z(x, y) for x, y in poly)
            zt = max(self.z(x, y) for x, y in poly)
            if aire > 400:      # ecole, maison de pays : grands volumes a toit plat
                h, mur, toit = 230, MAT["ecole"], None
            else:               # pavillons : R+1 sous toit a deux pans
                h, mur, toit = 300, MAT["voisin"], MAT["voisin_toit"]
            base = bloc(-l / 2, -wd / 2, zb - zt - 64, l / 2, wd / 2, h, mur)
            self.brushes.append(tourne(base, a, cx, cy, zt))
            if toit:
                d = 28
                pente = math.tan(math.radians(32)) * (wd / 2 + d)
                planes = [((0, 0, -1), (0, 0, h), toit), ((-1, 0, 0), (-l / 2 - d, 0, 0), toit),
                          ((1, 0, 0), (l / 2 + d, 0, 0), toit),
                          ((0, -pente, wd / 2 + d), (0, -wd / 2 - d, h), toit),
                          ((0, pente, wd / 2 + d), (0, wd / 2 + d, h), toit)]
                self.brushes.append(tourne(planes, a, cx, cy, zt))
                self.brushes.append(tourne(bloc(l * 0.2, -16, h + pente * 0.4, l * 0.2 + 36, 16, h + pente + 40, MAT["voisin"]), a, cx, cy, zt))

    # --- vegetation --------------------------------------------------------------
    def libre(self, x, y, marge=96):
        return all(not (e[0] - marge < x < e[2] + marge and e[1] - marge < y < e[3] + marge) for e in self.emprises) \
            and self.X0 + 200 < x < self.X1 - 200 and self.Y0 + 200 < y < self.Y1 - 200

    def sapin(self, x, y, hauteur=900, rayon=230):
        z = self.z(x, y)
        self.brushes.append(pave(x - 14, y - 14, z - 32, x + 14, y + 14, z + hauteur * 0.25, MAT["ecorce"]))
        etages = [(0.12, 1.0), (0.38, 0.78), (0.6, 0.55), (0.8, 0.32)]
        for k, (h0, r) in enumerate(etages):
            zb = z + hauteur * h0
            zt = z + hauteur * (etages[k + 1][0] + 0.06 if k + 1 < len(etages) else 1.0)
            rt = rayon * (etages[k + 1][1] * 0.75 if k + 1 < len(etages) else 0.06)
            self.brushes.append(tronc_cone(x, y, zb, rayon * r, zt, rt, MAT["feuillage"]))

    def peuplier(self, x, y, hauteur=950):
        z = self.z(x, y)
        self.brushes.append(pave(x - 10, y - 10, z - 32, x + 10, y + 10, z + 160, MAT["ecorce"]))
        self.brushes.append(tronc_cone(x, y, z + 140, 70, z + hauteur * 0.55, 92, MAT["feuillage_clair"]))
        self.brushes.append(tronc_cone(x, y, z + hauteur * 0.55, 92, z + hauteur, 10, MAT["feuillage_clair"]))

    def modele(self, nom, x, y, angle=0.0, echelle=1.0, dz=0.0):
        self.entites.append({"classname": "misc_model", "model": nom,
                             "origin": f"{x:.1f} {y:.1f} {self.z(x, y) + dz:.1f}",
                             "angles": f"0 {angle:.1f} 0", "modelscale": f"{echelle:g}"})

    def vegetation(self):
        s = self.site
        # rangees d'arbres OSM : peupliers tous les 10 m
        for wid, w in s.ways.items():
            if w.get("tags", {}).get("natural") != "tree_row":
                continue
            pts = s.poly(wid)
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                n = max(1, int(math.dist((ax, ay), (bx, by)) // 400))
                for k in range(n + 1):
                    x, y = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
                    if self.libre(x, y):
                        self.peuplier(x, y, random.uniform(850, 1050))
        # peupliers le long de l'avenue Borcier (ouest du batiment 1)
        for wid, w in s.ways.items():
            if w.get("tags", {}).get("highway") != "secondary":
                continue
            pts = s.poly(wid)
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                L = math.dist((ax, ay), (bx, by))
                if L < 1:
                    continue
                n = int(L // 420)
                ox, oy = -(by - ay) / L * 260, (bx - ax) / L * 260
                if ox < 0:
                    ox, oy = -ox, -oy  # cote est de l'avenue, vers les immeubles
                for k in range(n):
                    x, y = ax + (bx - ax) * (k + 0.5) / max(n, 1) + ox, ay + (by - ay) * (k + 0.5) / max(n, 1) + oy
                    if -3600 < y < 2600 and x < -900 and self.libre(x, y):
                        self.peuplier(x, y, random.uniform(900, 1100))
        # grands sujets reperes sur les photos
        for x, y, f in ((1430, 2950, self.sapin), (2350, 3480, self.sapin), (-3057, 5114, self.sapin)):
            if self.libre(x, y, 32):
                f(x, y, 1050, 260)
        for x, y in ((-700, 2300), (-1050, -900), (-950, 950), (-1150, -2300), (900, 3500), (3900, 2900), (-2300, 3300)):
            if self.libre(x, y, 32):
                self.modele("p7_foliage_tree_albizia_tall_full", x, y, random.uniform(0, 360), random.uniform(0.9, 1.2))
        for x, y in ((700, 2700), (820, 2760), (520, 2620), (2000, 3300), (-400, 2650)):
            if self.libre(x, y, 16):
                self.modele("p7_foliage_hedge_round_48_48_36_vibrant", x, y, random.uniform(0, 360), 1.6)
        # touffes d'herbe sur les pelouses
        n = 0
        while n < 220:
            x = random.uniform(self.X0 + 300, self.X1 - 300)
            y = random.uniform(self.Y0 + 300, self.Y1 - 300)
            if not self.libre(x, y, 64):
                continue
            if any(z0 <= x <= z1 and w0 <= y <= w1 for z0, w0, z1, w1 in (self.PARKING_BAS, self.PARKING_HAUT, self.ALLEE_GARAGES)):
                continue
            self.modele(random.choice(["p7_foliage_grass_tussock_green_1", "p7_foliage_grass_tussock_green_2",
                                       "p7_foliage_grass_tussock_green_3", "p7_foliage_grass_flowers"]),
                        x, y, random.uniform(0, 360), random.uniform(0.8, 1.3))
            n += 1

    # --- mobilier et voitures --------------------------------------------------------
    def decor(self):
        # voitures garees en epi devant le batiment 1 (photos 1 et 4)
        couleurs = ["grey", "blue", "black", "green"]
        b1 = self.immeubles[0]
        halls_y = [b1.monde(b1.section(k)[1] + (b1.section(k)[2] - b1.section(k)[1]) / 2, 0, 0)[1] for k in range(b1.halls)]
        y = -1380
        while y < 1400:
            if all(abs(y - hy) > 200 for hy in halls_y):
                self.modele(f"veh_t7_civ_car_compact_{random.choice(couleurs)}", 560, y, random.choice((0, 180)))
            y += 230
        for x, y in ((1660, 1700), (1660, 2100), (-300, 2550), (1200, 3900)):
            self.modele(f"veh_t7_civ_car_compact_{random.choice(couleurs)}", x, y, random.choice((90, 270)))
        # conteneurs a dechets semi-enterres au bord du parking du haut
        for k in range(3):
            x, y = 1900 + k * 96, 1150
            z = self.z(x, y)
            self.brushes.append(pave(x - 36, y - 36, z - 32, x + 36, y + 36, z + 72, MAT["conteneur"]))
            self.brushes.append(pave(x - 40, y - 40, z + 72, x + 40, y + 40, z + 80, MAT["metal"]))
        # lampadaires le long de la rue des Pres Dombet
        for x, y in ((900, -1700), (900, -500), (900, 700), (1450, 1600), (1450, 2700), (2200, 3200)):
            if not self.libre(x, y, 24):
                continue
            z = self.z(x, y)
            self.brushes.append(pave(x - 5, y - 5, z - 16, x + 5, y + 5, z + 380, MAT["metal"]))
            self.brushes.append(pave(x - 40, y - 12, z + 380, x + 12, y + 12, z + 392, MAT["metal"]))
        # bancs sur les pelouses
        for x, y, a in ((-500, 1900, 0), (1000, 3000, 90), (-600, -1900, 0)):
            if self.libre(x, y, 16):
                self.modele("p7_bench_modern_01", x, y, a)

    # --- decor lointain et limites ---------------------------------------------------
    def montagnes(self):
        """Couronne de montagnes boisees (Grand Colombier a l'ouest, collines a l'est)."""
        cx, cy = (self.X0 + self.X1) / 2, (self.Y0 + self.Y1) / 2
        r0, r1 = 7600, 10200
        n = 36

        def h(t):
            ouest = max(0.0, math.cos(t - math.radians(165)))
            return 900 + 2100 * ouest ** 1.5 + 260 * math.sin(3 * t + 1) + 180 * math.sin(7 * t)

        for k in range(n):
            t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            p0 = (cx + r0 * math.cos(t0), cy + r0 * math.sin(t0), -64)
            p1 = (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1), -64)
            q0 = (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0), h(t0))
            q1 = (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1), h(t1))
            self.brushes.append(prisme_triangle(p0, p1, q1, -512, MAT["montagne"]))
            self.brushes.append(prisme_triangle(p0, q1, q0, -512, MAT["montagne"]))
        # plaine entre le quartier et les montagnes
        for (x0, y0, x1, y1) in ((-r1 + cx, -r1 + cy, self.X0, r1 + cy), (self.X1, -r1 + cy, r1 + cx, r1 + cy),
                                 (self.X0, -r1 + cy, self.X1, self.Y0), (self.X0, self.Y1, self.X1, r1 + cy)):
            self.brushes.append(pave(x0, y0, -512, x1, y1, -64, MAT["herbe_sombre"]))
        # murs invisibles autour de la zone jouable
        e = 64
        for (x0, y0, x1, y1) in ((self.X0 - e, self.Y0 - e, self.X1 + e, self.Y0), (self.X0 - e, self.Y1, self.X1 + e, self.Y1 + e),
                                 (self.X0 - e, self.Y0, self.X0, self.Y1), (self.X1, self.Y0, self.X1 + e, self.Y1)):
            self.brushes.append(pave(x0, y0, -256, x1, y1, 2400, MAT["clip"]))

    def construire(self):
        self.immeubles_hlm()
        self.annexe_et_garages()
        self.hauteurs()
        self.terrain()
        self.bordures()
        self.routes()
        for imm in self.immeubles:
            imm.construire(mats_immeuble(imm.style))
            self.entites += imm.entites
        self.voisins()
        self.vegetation()
        self.decor()
        self.montagnes()
        return self
