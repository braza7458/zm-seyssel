"""Rendu PNG rapide (z-buffer, ombrage lambertien) de fichiers .map Radiant.

Remplace le painter SVG lent de preview_blockout.py : les brushes sont lus avec
read_brushes/faces/COULEURS de preview_blockout.py, triangules, projetes puis
rasterises par numpy avec un vrai z-buffer. Le quartier entier (~40 000 faces)
se rend en 5 a 12 s en 1600x1000, anticrenelage compris (surechantillonnage 2x2), dont
2 a 3 s de lecture des .map. Memoire : environ 200 Mo de pic en 1600x1000 avec --ss 2
(le traitement de l'image se fait par bandes de lignes) ; --ss 1 ou --res plus petit
si la machine manque de memoire.

Ce qui est dessine :
    - les brushes (couleur par famille de materiau, ombrage par normale) ;
    - des PLACEHOLDERS pour les misc_model (voitures, arbres, haies, bancs...) : ce sont
      des boites/cones approximatifs, PAS les vrais modeles du jeu (tailles estimees) ;
    - avec --reperes, des boites pour les prefabs zm_core de la map principale
      (atouts, Mystery Box, Pack-a-Punch, courant) et les points d'apparition.
Ce n'est pas le rendu du moteur : ni textures, ni lumieres, ni ombres portees. Les couleurs
sont celles de preview_blockout.COULEURS (par sous-chaine du nom de materiau), corrigees pour
quelques collisions (voir COULEURS_PRIORITE) ; un materiau inconnu est gris-beige.

Usage :
    python tools/preview_png.py [fichier.map ...] -o sortie.png [options]

Sans fichier .map, charge quartier.map, batiment_1..3.map et zm_seyssel.map.

Cadrage (au choix) :
    --vue AZIMUT ELEVATION             vue orthographique. Azimut 0 = camera au sud regardant
                                       le nord, 90 = camera a l'est (voit la facade est),
                                       180 = au nord, 270 = a l'ouest. Elevation 90 = plan.
    --camera EX EY EZ CX CY CZ         perspective de l'oeil E vers la cible C (unites de jeu)
    --cible NOM --face F               raccourci : camera devant une facade d'un immeuble.
                                       NOM = batiment_1, batiment_2, batiment_3 (prefabs).
                                       F = est|ouest|nord|sud (axes du JEU : X = est, Y = nord)
        --portion A B                  tranche de la facade, de 0 (gauche vu de la camera) a 1
        --niveaux N0 N1                tranche verticale en etages (0 = sol du rez, 5 = haut). Le sol du
                                       rez est la face +z la plus basse en travertin du prefab.
        --yaw DEG --pitch DEG          decalage de la camera autour de la cible (def. 20 et 8)
        --distance D                   distance camera-facade en unites (sinon calculee)
    --fov DEG                          champ vertical de la perspective (def. 55)
    --res L H                          taille de l'image (def. 1600 1000)
    --ss N                             surechantillonnage (def. 2 ; 1 = rapide et crenele)

Filtres :
    --boite X0 Y0 Z0 X1 Y1 Z1          ne garde que les faces entierement dans la boite
    --centre                           ... ou dont le centre est dans la boite
    --sans mot,mot                     exclut les materiaux contenant ces mots (noms de GDT, ex. bunker,roof)
    --sans-vegetation                  retire arbres, haies et touffes (brushes de feuillage + placeholders)
    --seulement mot,mot                ne garde que ces materiaux
    --sans-modeles                     n'affiche pas les placeholders de misc_model
    --reperes                          affiche atouts/box/Pack-a-Punch/spawns de la map principale
    --ciel                             affiche la boite de ciel (masquee par defaut)

Diagnostic :
    --zfight                           colore en magenta les faces coplanaires de meme sens, de materiaux
                                       differents, qui se recouvrent sans etre enterrees dans un autre
                                       brush (= scintillement en jeu) ; liste les 15 plus grosses
    --brume D                          brume de distance (unites), perspective seulement
    --sans-aretes                      pas de contours aux discontinuites de profondeur
    --etiquette "texte"                ecrit un texte en bas a gauche de l'image
    --info                             affiche les boites englobantes et quitte

Exemples :
    python tools/preview_png.py -o _build/renders/vue.png --vue 35 38
    python tools/preview_png.py -o _build/renders/est.png --cible batiment_1 --face est --sans-vegetation
    python tools/preview_png.py -o _build/renders/balcons.png --cible batiment_1 --face ouest --portion 0 0.4 --niveaux 1 4
    python tools/preview_png.py -o _build/renders/hall.png --camera 700 0 60 200 0 90 --fov 70

Axes du jeu : X vers l'est-nord-est, Y vers le nord-nord-ouest (le long du batiment 1),
voir geo.py. Les mots "est/ouest/nord/sud" de ce script suivent ces axes, pas la boussole.
"""

import argparse
import gc
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from preview_blockout import COULEURS, faces, read_brushes

RACINE = Path(__file__).resolve().parent.parent
PREFABS = RACINE / "game" / "map_source" / "_prefabs" / "zm_seyssel"
MAP_PRINCIPALE = RACINE / "game" / "map_source" / "zm" / "zm_seyssel.map"
DEFAUT = sorted(p for p in PREFABS.glob("*.map") if p.stem != "decor") + [PREFABS.parent.parent / "zm" / "zm_seyssel.map"]

try:  # hauteur d'etage du generateur ; 144 si le module change
    from immeuble import H as HAUTEUR_ETAGE
    from immeuble import FONDATION
except Exception:  # pragma: no cover
    HAUTEUR_ETAGE, FONDATION = 144, 192

# Corrections testees AVANT preview_blockout.COULEURS : ses cles sont des sous-chaines, donc
# "t7_asphalt_dirty_dark_desert" tombait sur "dirt" (brun) et le loggia brun sur le creme de "drywall".
COULEURS_PRIORITE = [
    ("asphalt", (70, 70, 74)), ("painted_brown", (96, 66, 46)), ("painted_beige", (208, 190, 150)),
    ("painted_clean_white", (236, 236, 232)), ("paint_worn_grey", (112, 114, 118)),
]

# Materiaux que preview_blockout.COULEURS ne connait pas (testes apres lui)
COULEURS_PLUS = [
    ("trim_dark_brown", (84, 58, 42)), ("plaster_rough", (214, 198, 170)), ("drywall", (226, 220, 205)),
    ("ceramic", (215, 215, 210)), ("floor_sealed", (150, 150, 146)), ("stainless", (170, 172, 176)),
    ("iron", (60, 62, 66)), ("graphite", (70, 72, 76)), ("beveled", (200, 198, 190)), ("oak", (110, 80, 55)),
    ("hedge", (60, 110, 55)),
]
COULEUR_DEFAUT = (190, 185, 175)
COULEUR_FOND_HAUT = np.array([150, 186, 228], float)
COULEUR_FOND_BAS = np.array([214, 226, 236], float)
MAGENTA = (255, 0, 255)

# lumiere fixe dans le monde : deux images d'un meme batiment restent comparables
LUM_CLE = np.array([0.40, -0.60, 0.80]) / np.linalg.norm([0.40, -0.60, 0.80])
LUM_FILL = np.array([-0.50, 0.55, 0.20]) / np.linalg.norm([-0.50, 0.55, 0.20])


def couleur(mat):
    """Couleur d'un materiau, ou None s'il ne doit pas etre dessine (clip, trigger, volume...)."""
    for cle, c in COULEURS_PRIORITE + COULEURS:
        if cle in mat:
            return c
    for cle, c in COULEURS_PLUS:
        if cle in mat:
            return c
    return COULEUR_DEFAUT


def ombrage(n):
    """Facteur de lumiere d'une normale (n : tableau (F,3))."""
    cle = np.clip(n @ LUM_CLE, 0, None)
    fill = np.clip(n @ LUM_FILL, 0, None)
    sol = np.clip(-n[:, 2], 0, None)
    return np.clip(0.52 + 0.45 * cle + 0.14 * fill - 0.06 * sol, 0.2, 1.0)


# --- lecture des fichiers ------------------------------------------------------

def lire_entites(path):
    """[(classname, {cle: valeur})] des entites d'un .map (seules les cles texte nous interessent)."""
    texte = Path(path).read_text(encoding="latin-1")
    out = []
    for bloc in re.split(r"^// entity \d+\r?$", texte, flags=re.M)[1:]:
        kv = dict(re.findall(r'^"([^"]+)" "([^"]*)"\r?$', bloc.split("// brush")[0], flags=re.M))
        out.append((kv.get("classname", ""), kv))
    return out


class Face:
    """Un polygone convexe d'un brush (ou d'un placeholder)."""
    __slots__ = ("n", "pts", "mat", "col", "brush", "src", "plans")

    def __init__(self, n, pts, mat, col, brush, src, plans=None):
        self.n, self.pts, self.mat, self.col, self.brush, self.src = n, pts, mat, col, brush, src
        self.plans = plans      # (normales (k,3), distances (k,)) du brush, pour savoir si un point est enterre


def charger(chemins, ciel=False):
    """Retourne (liste de Face, noms des sources, entites [(src, classname, kv)])."""
    toutes, sources, entites = [], [], []
    brush_id = 0
    for src, chemin in enumerate(chemins):
        sources.append(Path(chemin))
        for planes in read_brushes([chemin]):
            brush_id += 1
            plans = (np.array([n for n, _, _ in planes], float), np.array([d for _, d, _ in planes], float))
            for n, pts, mat in faces(planes):
                col = couleur(mat)
                if col is None or (not ciel and mat == "sky"):
                    continue
                toutes.append(Face(n, pts, mat, col, brush_id, src, plans))
        for cls, kv in lire_entites(chemin):
            entites.append((src, cls, kv))
    return toutes, sources, entites


# --- placeholders de misc_model ------------------------------------------------------

def _boite_faces(cx, cy, z0, lx, ly, hz, yaw, mat, col, brush, src):
    """Boite centree en (cx, cy), tournee de yaw degres, de z0 a z0+hz, comme liste de Face."""
    a = math.radians(yaw)
    ca, sa = math.cos(a), math.sin(a)

    def p(x, y, z):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca, z)

    hx, hy = lx / 2, ly / 2
    b = [p(-hx, -hy, z0), p(hx, -hy, z0), p(hx, hy, z0), p(-hx, hy, z0)]
    h = [(x, y, z0 + hz) for x, y, _ in b]
    quads = [
        ([b[3], b[2], b[1], b[0]], (0, 0, -1)), ([h[0], h[1], h[2], h[3]], (0, 0, 1)),
        ([b[0], b[1], h[1], h[0]], (sa, -ca, 0)),     # pan avant (-y local)
        ([b[1], b[2], h[2], h[1]], (ca, sa, 0)),      # pan droit (+x local)
        ([b[2], b[3], h[3], h[2]], (-sa, ca, 0)),     # pan arriere (+y local)
        ([b[3], b[0], h[0], h[3]], (-ca, -sa, 0)),    # pan gauche (-x local)
    ]
    return [Face(n, pts, mat, col, brush, src) for pts, n in quads]


def _tronc_faces(cx, cy, zb, rb, zt, rt, mat, col, brush, src, cotes=8):
    """Tronc de cone a pans (houppiers)."""
    out = [Face((0, 0, -1), [(cx + rb * math.cos(2 * math.pi * j / cotes), cy + rb * math.sin(2 * math.pi * j / cotes), zb)
                             for j in range(cotes - 1, -1, -1)], mat, col, brush, src),
           Face((0, 0, 1), [(cx + rt * math.cos(2 * math.pi * j / cotes), cy + rt * math.sin(2 * math.pi * j / cotes), zt)
                            for j in range(cotes)], mat, col, brush, src)]
    for j in range(cotes):
        t0, t1 = 2 * math.pi * j / cotes, 2 * math.pi * (j + 1) / cotes
        tm = (t0 + t1) / 2
        pts = [(cx + rb * math.cos(t0), cy + rb * math.sin(t0), zb), (cx + rb * math.cos(t1), cy + rb * math.sin(t1), zb),
               (cx + rt * math.cos(t1), cy + rt * math.sin(t1), zt), (cx + rt * math.cos(t0), cy + rt * math.sin(t0), zt)]
        k = (rb - rt) / max(zt - zb, 1e-6)
        n = np.array([math.cos(tm), math.sin(tm), k])
        n = n / np.linalg.norm(n)
        out.append(Face(tuple(n), pts, mat, col, brush, src))
    return out


COULEURS_VOITURE = {"grey": (112, 114, 120), "blue": (62, 88, 140), "black": (40, 40, 46), "green": (72, 112, 82)}


def placeholder(cls, kv, brush, src):
    """Faces approximatives pour un misc_model ou un prefab zm_core. Tailles ESTIMEES, pas lues dans le jeu."""
    try:
        ox, oy, oz = (float(v) for v in kv["origin"].split())
    except (KeyError, ValueError):
        return []
    yaw = 0.0
    if "angles" in kv:
        try:
            yaw = float(kv["angles"].split()[1])
        except (IndexError, ValueError):
            pass
    k = float(kv.get("modelscale", "1") or 1)
    modele = kv.get("model", "")
    nom = "placeholder_" + modele.split("/")[-1]
    f = []
    if modele.startswith("veh_"):
        couleur_v = next((c for n, c in COULEURS_VOITURE.items() if modele.endswith(n)), (120, 120, 120))
        f += _boite_faces(ox, oy, oz + 6, 168 * k, 70 * k, 34 * k, yaw, nom, couleur_v, brush, src)
        f += _boite_faces(ox - 8 * k * math.cos(math.radians(yaw)), oy - 8 * k * math.sin(math.radians(yaw)),
                          oz + 40 * k, 90 * k, 64 * k, 22 * k, yaw, nom + "_vitres", (70, 84, 100), brush, src)
    elif "tree" in modele:
        f += _boite_faces(ox, oy, oz, 14 * k, 14 * k, 150 * k, 0, nom + "_tronc", (92, 66, 46), brush, src)
        f += _tronc_faces(ox, oy, oz + 140 * k, 120 * k, oz + 330 * k, 150 * k, nom + "_feuillage", (74, 120, 62), brush, src)
        f += _tronc_faces(ox, oy, oz + 330 * k, 150 * k, oz + 480 * k, 40 * k, nom + "_feuillage", (74, 120, 62), brush, src)
    elif "hedge" in modele:
        f += _boite_faces(ox, oy, oz, 48 * k, 48 * k, 36 * k, yaw, nom, (58, 108, 54), brush, src)
    elif "grass" in modele:
        f += _tronc_faces(ox, oy, oz, 9 * k, oz + 16 * k, 2 * k, nom, (96, 140, 70), brush, src, cotes=4)
    elif "bench" in modele:
        f += _boite_faces(ox, oy, oz, 60 * k, 22 * k, 20 * k, yaw, nom, (120, 84, 56), brush, src)
        f += _boite_faces(ox, oy + 8 * k, oz + 20 * k, 60 * k, 4 * k, 22 * k, yaw, nom, (120, 84, 56), brush, src)
    else:
        f += _boite_faces(ox, oy, oz, 24, 24, 24, yaw, nom, (230, 140, 40), brush, src)
    return f


# couleurs des reperes de gameplay (map principale)
REPERES = [("power_switch", (240, 200, 40), (24, 24, 56)), ("magic_box", (200, 40, 40), (60, 28, 36)),
           ("upgrade", (150, 60, 200), (40, 40, 80)), ("vending", (40, 110, 220), (36, 36, 80)),
           ("weapon", (60, 180, 80), (40, 14, 20))]


def reperes(entites, premier_brush):
    """Boites de couleur pour les prefabs zm_core, le spawn joueur et les sorties de zombies."""
    out, b = [], premier_brush
    for src, cls, kv in entites:
        b += 1
        try:
            ox, oy, oz = (float(v) for v in kv["origin"].split())
        except (KeyError, ValueError):
            continue
        yaw = float(kv.get("angles", "0 0 0").split()[1]) if "angles" in kv else 0.0
        if cls == "misc_prefab" and "zm_core" in kv.get("model", ""):
            for cle, col, taille in REPERES:
                if cle in kv["model"]:
                    out += _boite_faces(ox, oy, oz, taille[0], taille[1], taille[2], yaw, "repere_" + cle, col, b, src)
                    break
        elif cls == "info_player_start":
            out += _tronc_faces(ox, oy, oz, 16, oz + 72, 16, "repere_spawn", (255, 255, 255), b, src)
        elif cls == "script_struct" and kv.get("script_noteworthy") == "riser_location":
            out += _tronc_faces(ox, oy, oz, 20, oz + 8, 6, "repere_zombie", (220, 30, 30), b, src)
    return out


# --- coplanarite (z-fighting) --------------------------------------------------------

def _inter(p, q):
    """Intersection de deux polygones convexes 2D (Sutherland-Hodgman) : (aire, sommets)."""
    def aire(poly):
        return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                       for i in range(len(poly)))) / 2

    def orient(poly):
        s = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
        return poly if s > 0 else poly[::-1]

    sortie, clip = orient(list(p)), orient(list(q))
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        if not sortie:
            break
        entree, sortie = sortie, []

        def cote(pt):
            return (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0])

        for j in range(len(entree)):
            c, d = entree[j], entree[(j + 1) % len(entree)]
            sc, sd = cote(c), cote(d)
            if sc >= 0:
                sortie.append(c)
            if (sc >= 0) != (sd >= 0):
                t = sc / (sc - sd)
                sortie.append((c[0] + t * (d[0] - c[0]), c[1] + t * (d[1] - c[1])))
    return (aire(sortie), sortie) if len(sortie) >= 3 else (0.0, [])


def coplanaires(liste, seuil_aire=1.0, tol_plan=0.05, ignorer_enterrees=True):
    """Paires de faces de meme sens, dans le meme plan (a tol_plan pres), de brushes differents, qui se recouvrent.

    Retourne [(aire, i, j, zone)] trie par aire decroissante ; zone = polygone commun en 3D. C'est le z-fighting :
    le moteur ne sait pas laquelle des deux faces afficher.
    Avec ignorer_enterrees, on abandonne les paires dont la zone commune est a l'interieur d'un troisieme brush
    (face cachee dans la matiere : le BSP la supprime, rien ne scintille).
    """
    boites = {}
    for f in liste:
        if f.plans is None:
            continue
        v = np.array(f.pts)
        lo, hi = boites.get(f.brush, (v.min(0), v.max(0)))
        boites[f.brush] = (np.minimum(lo, v.min(0)), np.maximum(hi, v.max(0)))
    plans_brush = {f.brush: f.plans for f in liste if f.plans is not None}
    ids_b = np.array(list(boites))
    lo_b = np.array([boites[b][0] for b in ids_b]).reshape(-1, 3)
    hi_b = np.array([boites[b][1] for b in ids_b]).reshape(-1, 3)

    def enterre(point):
        cand = ids_b[np.all((lo_b - 0.1 <= point) & (point <= hi_b + 0.1), axis=1)]
        for b in cand:
            nn, dd = plans_brush[b]
            if np.all(nn @ point < dd - 0.05):
                return True
        return False

    groupes = {}
    for i, f in enumerate(liste):
        if f.mat.startswith(("placeholder", "repere")):
            continue
        cle = tuple(round(c, 3) + 0.0 for c in f.n)
        groupes.setdefault(cle, []).append(i)
    paires = []
    for cle, idx in groupes.items():
        if len(idx) < 2:
            continue
        n = np.array(cle) / np.linalg.norm(cle)
        a = np.cross(n, (0, 0, 1)) if abs(n[2]) < 0.9 else np.cross(n, (1, 0, 0))
        a /= np.linalg.norm(a)
        b = np.cross(n, a)
        info = []
        for i in idx:
            pts = np.array(liste[i].pts)
            d = float(pts[0] @ n)
            uv = [(float(p @ a), float(p @ b)) for p in pts]
            xs, ys = [u for u, _ in uv], [v for _, v in uv]
            info.append((d, min(xs), max(xs), min(ys), max(ys), i, uv))
        base = (a, b, n)
        info.sort(key=lambda t: t[0])
        for s in range(len(info)):
            d0, x0, x1, y0, y1, i, uv = info[s]
            for t in range(s + 1, len(info)):
                d1, a0, a1, b0, b1, j, uw = info[t]
                if d1 - d0 > tol_plan:
                    break
                if liste[i].brush == liste[j].brush or a0 >= x1 - 0.5 or a1 <= x0 + 0.5 or b0 >= y1 - 0.5 or b1 <= y0 + 0.5:
                    continue
                ai, poly = _inter(uv, uw)
                if ai >= seuil_aire:
                    if ignorer_enterrees and liste[i].plans is not None:
                        cu = sum(x for x, _ in poly) / len(poly)
                        cv = sum(y for _, y in poly) / len(poly)
                        if enterre(cu * base[0] + cv * base[1] + (d0 + 0.4) * base[2]):
                            continue
                    # zone commune en 3D, relevee de 0,35 u pour qu'on la voie au-dessus des deux faces
                    zone = [tuple(x * base[0] + y * base[1] + (d0 + 0.35) * base[2]) for x, y in poly]
                    paires.append((ai, i, j, zone))
    paires.sort(key=lambda t: -t[0])
    return paires


# --- scene : triangles -------------------------------------------------------------------

class Scene:
    def __init__(self, liste):
        self.faces = liste
        tris, tface = [], []
        for k, f in enumerate(liste):
            pts = f.pts
            for i in range(1, len(pts) - 1):
                tris.append((pts[0], pts[i], pts[i + 1]))
                tface.append(k)
        self.tris = np.array(tris, float).reshape(-1, 3, 3)
        self.tface = np.array(tface, np.int64)
        self.normales = np.array([f.n for f in liste], float).reshape(-1, 3)
        self.couleurs = np.array([f.col for f in liste], float).reshape(-1, 3)
        self.brush = np.array([f.brush for f in liste], np.int64)

    def bornes(self):
        v = self.tris.reshape(-1, 3)
        return v.min(0), v.max(0)


def est_vegetation(f, nb_faces):
    """Feuillage et ecorce du generateur : brushes d'au moins 8 faces en herbe (les prismes du terrain en ont 5)."""
    if f.mat.startswith("placeholder"):
        return any(k in f.mat for k in ("tree", "hedge", "grass"))
    return "wood_beam_worn_oak" in f.mat or ("core_grass" in f.mat and nb_faces[f.brush] >= 8)


def filtrer(liste, boite=None, centre=False, sans=(), seulement=(), sans_vegetation=False):
    out = []
    nb_faces = {}
    for f in liste:
        nb_faces[f.brush] = nb_faces.get(f.brush, 0) + 1
    for f in liste:
        if sans_vegetation and est_vegetation(f, nb_faces):
            continue
        if sans and any(m in f.mat for m in sans):
            continue
        if seulement and not any(m in f.mat for m in seulement):
            continue
        if boite:
            test = [tuple(sum(p[t] for p in f.pts) / len(f.pts) for t in range(3))] if centre else f.pts
            if not all(boite[0] <= p[0] <= boite[3] and boite[1] <= p[1] <= boite[4] and boite[2] <= p[2] <= boite[5] for p in test):
                continue
        out.append(f)
    return out


# --- camera -----------------------------------------------------------------------------

class Camera:
    def __init__(self, oeil=None, cible=None, fov=55.0, ortho=None):
        """Perspective (oeil, cible, fov) ou orthographique (ortho = (azimut, elevation))."""
        self.fov = fov
        self.ortho = ortho
        if ortho is not None:
            a, e = math.radians(ortho[0]), math.radians(min(max(ortho[1], -89.5), 89.5))
            self.vers_cam = np.array([math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)])
            self.droite = np.cross((0, 0, 1), self.vers_cam)
            self.droite /= np.linalg.norm(self.droite)
            self.haut = np.cross(self.vers_cam, self.droite)
            self.oeil = None
        else:
            self.oeil = np.array(oeil, float)
            self.cible = np.array(cible, float)
            self.devant = self.cible - self.oeil
            self.devant /= np.linalg.norm(self.devant)
            d = np.cross(self.devant, (0, 0, 1))
            if np.linalg.norm(d) < 1e-6:  # regard vertical
                d = np.array([1.0, 0, 0])
            self.droite = d / np.linalg.norm(d)
            self.haut = np.cross(self.droite, self.devant)


def projeter(scene, cam, W, H, near=4.0, echelle=None, marge=0.04):
    """Triangles visibles -> (sx, sy, q, tface, rang) ; q = 'proximite' (plus grand = plus pres)."""
    tris, tface = scene.tris, scene.tface
    n = scene.normales[tface]
    p0 = tris[:, 0]
    # elimination des faces dos a la camera
    if cam.ortho is not None:
        vis = (n @ cam.vers_cam) > 1e-9
    else:
        vis = np.einsum("ij,ij->i", n, cam.oeil - p0) > 1e-6
    tris, tface = tris[vis], tface[vis]
    rang = np.nonzero(vis)[0]
    if len(tris) == 0:
        return None
    if cam.ortho is not None:
        x = tris @ cam.droite
        y = tris @ cam.haut
        z = tris @ cam.vers_cam
        if echelle is None:
            dx, dy = x.max() - x.min(), y.max() - y.min()
            k = min(W * (1 - 2 * marge) / max(dx, 1e-6), H * (1 - 2 * marge) / max(dy, 1e-6))
        else:
            k = echelle
        cx, cy = (x.max() + x.min()) / 2, (y.max() + y.min()) / 2
        cam.cadre = (k, cx, cy)       # pixels par unite et centre, pour placer des annotations (en pixels de W x H)
        sx = W / 2 + k * (x - cx)
        sy = H / 2 - k * (y - cy)
        return sx, sy, z, tface, rang
    d = tris - cam.oeil
    xc, yc, zc = d @ cam.droite, d @ cam.haut, d @ cam.devant
    f = (H / 2) / math.tan(math.radians(cam.fov) / 2)
    ok = (zc >= near).all(axis=1)
    mixte = (zc >= near).any(axis=1) & ~ok
    xc, yc, zc, tface2, rang2 = xc[ok], yc[ok], zc[ok], tface[ok], rang[ok]
    if mixte.any():  # decoupe contre le plan proche
        ex, ey, ez, ef, er = [], [], [], [], []
        for i in np.nonzero(mixte)[0]:
            poly = []
            for a in range(3):
                b = (a + 1) % 3
                pa = (d[i, a] @ cam.droite, d[i, a] @ cam.haut, d[i, a] @ cam.devant)
                pb = (d[i, b] @ cam.droite, d[i, b] @ cam.haut, d[i, b] @ cam.devant)
                if pa[2] >= near:
                    poly.append(pa)
                if (pa[2] >= near) != (pb[2] >= near):
                    t = (near - pa[2]) / (pb[2] - pa[2])
                    poly.append(tuple(pa[k] + t * (pb[k] - pa[k]) for k in range(3)))
            for k in range(1, len(poly) - 1):
                tri = (poly[0], poly[k], poly[k + 1])
                ex.append([v[0] for v in tri])
                ey.append([v[1] for v in tri])
                ez.append([v[2] for v in tri])
                ef.append(tface[i])
                er.append(rang[i])
        if ex:
            xc, yc, zc = np.vstack([xc, ex]), np.vstack([yc, ey]), np.vstack([zc, ez])
            tface2, rang2 = np.concatenate([tface2, ef]), np.concatenate([rang2, er])
    if len(zc) == 0:
        return None
    return W / 2 + f * xc / zc, H / 2 - f * yc / zc, 1.0 / zc, tface2, rang2


# --- rasterisation -----------------------------------------------------------------------

def rasteriser(sx, sy, q, rang, W, H, budget=250_000):
    """Z-buffer vectorise. Retourne (zbuf, ids) ; ids = indice de triangle (dans les tableaux passes) ou -1."""
    N = len(sx)
    zbuf = np.full(W * H, -np.inf)
    ids = np.full(W * H, -1, np.int32)
    x0, x1, x2 = sx[:, 0], sx[:, 1], sx[:, 2]
    y0, y1, y2 = sy[:, 0], sy[:, 1], sy[:, 2]
    aire = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    bx0 = np.maximum(0, np.ceil(sx.min(1) - 0.5)).astype(np.int64)
    bx1 = np.minimum(W - 1, np.floor(sx.max(1) - 0.5)).astype(np.int64)
    by0 = np.maximum(0, np.ceil(sy.min(1) - 0.5)).astype(np.int64)
    by1 = np.minimum(H - 1, np.floor(sy.max(1) - 0.5)).astype(np.int64)
    valide = (np.abs(aire) > 1e-9) & (bx1 >= bx0) & (by1 >= by0) & np.isfinite(aire)
    larg, haut = bx1 - bx0 + 1, by1 - by0 + 1
    taille = np.maximum(larg, haut)
    inv = np.zeros(N)
    inv[valide] = 1.0 / aire[valide]
    # biais de departage : a profondeur egale, le triangle de rang le plus grand gagne (rendu deterministe)
    biais = 1e-12 * max(float(np.abs(q).max()), 1e-9) * (rang.astype(float) / max(rang.max(), 1))
    qb = q + biais[:, None]
    # fonctions affines en (x, y) pixel : L1, L2 (coordonnees barycentriques) et la proximite q
    A1 = inv * (-x0 * (y2 - y0) + (x2 - x0) * y0)
    B1, C1 = inv * (y2 - y0), -inv * (x2 - x0)
    A2 = inv * (-(x1 - x0) * y0 + x0 * (y1 - y0))
    B2, C2 = -inv * (y1 - y0), inv * (x1 - x0)
    A0, B0, C0 = 1.0 - A1 - A2, -B1 - B2, -C1 - C2
    dq1, dq2 = qb[:, 1] - qb[:, 0], qb[:, 2] - qb[:, 0]
    Bq, Cq = dq1 * B1 + dq2 * B2, dq1 * C1 + dq2 * C2
    Aq = qb[:, 0] + dq1 * A1 + dq2 * A2

    def lot(idx, s, ox, oy):
        g = (np.arange(s) + 0.5).astype(np.float32)
        gx, gy = g[None, None, :], g[None, :, None]
        dedans = None
        for A, B, C in ((A1, B1, C1), (A2, B2, C2), (A0, B0, C0)):   # coordonnees locales : float32 suffit
            a = (A[idx] + B[idx] * ox + C[idx] * oy).astype(np.float32)[:, None, None]
            L = a + B[idx].astype(np.float32)[:, None, None] * gx + C[idx].astype(np.float32)[:, None, None] * gy
            L = L >= -1e-5
            dedans = L if dedans is None else dedans & L
        ti, yi, xi = np.nonzero(dedans)
        if len(ti) == 0:
            return
        X = ox[ti] + xi
        Y = oy[ti] + yi
        bon = (X < W) & (Y < H)
        ti, X, Y = ti[bon], X[bon], Y[bon]
        tri = idx[ti]
        qv = Aq[tri] + Bq[tri] * (X + 0.5) + Cq[tri] * (Y + 0.5)
        pix = Y * W + X
        np.maximum.at(zbuf, pix, qv)
        gagne = qv >= zbuf[pix]
        ids[pix[gagne]] = tri[gagne]

    def par_lots(idx, s, ox, oy):
        pas = max(1, budget // (s * s))
        for k in range(0, len(idx), pas):
            lot(idx[k:k + pas], s, ox[k:k + pas], oy[k:k + pas])

    tout = np.nonzero(valide)[0]
    for s in (4, 8, 16, 32):
        borne_inf = {4: 0, 8: 4, 16: 8, 32: 16}[s]
        sel = tout[(taille[tout] <= s) & (taille[tout] > borne_inf)]
        if len(sel):
            par_lots(sel, s, bx0[sel], by0[sel])
    gros = tout[taille[tout] > 32]
    if len(gros):  # carreaux de 32x32 alignes, avec rejet conservatif ; par paquets pour borner la memoire
        T = 32
        tx0, tx1 = bx0[gros] // T, bx1[gros] // T
        ty0, ty1 = by0[gros] // T, by1[gros] // T
        ntx, nty = tx1 - tx0 + 1, ty1 - ty0 + 1
        cnt_tous = ntx * nty
        debut_paquet = 0
        cumul = np.cumsum(cnt_tous)
        while debut_paquet < len(gros):
            fin = int(np.searchsorted(cumul, (cumul[debut_paquet - 1] if debut_paquet else 0) + 120_000, side="right"))
            fin = max(fin, debut_paquet + 1)
            sel = slice(debut_paquet, fin)
            debut_paquet = fin
            g, cnt = gros[sel], cnt_tous[sel]
            tri = np.repeat(g, cnt)
            loc = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
            ntr = np.repeat(ntx[sel], cnt)
            cx = np.repeat(tx0[sel], cnt) + loc % ntr
            cy = np.repeat(ty0[sel], cnt) + loc // ntr
            gardes = np.ones(len(tri), bool)
            # rejet : si les 4 coins d'un carreau sont du mauvais cote d'une meme arete, le carreau est hors du triangle
            hors = [np.ones(len(tri), bool) for _ in range(3)]
            for ax, ay in ((0, 0), (T, 0), (0, T), (T, T)):
                px = (cx * T + ax).astype(float)
                py = (cy * T + ay).astype(float)
                for k, (A, B, C) in enumerate(((A1, B1, C1), (A2, B2, C2), (A0, B0, C0))):
                    hors[k] &= (A[tri] + B[tri] * px + C[tri] * py) < -1e-6
            for k in range(3):
                gardes &= ~hors[k]
            tri, cx, cy = tri[gardes], cx[gardes], cy[gardes]
            par_lots(tri, T, cx * T, cy * T)
    return zbuf, ids


# --- image -------------------------------------------------------------------------------

def fond_lignes(H):
    """Degrade de ciel : une couleur par ligne, (H, 3) uint8."""
    t = np.linspace(0, 1, H)[:, None]
    return (COULEUR_FOND_HAUT * (1 - t) + COULEUR_FOND_BAS * t).astype(np.uint8)


def rendre(scene, cam, res=(1600, 1000), ss=2, brume=None, aretes=True, surbrillance=None, echelle=None):
    """Retourne (image PIL, nombre de triangles). surbrillance : indices de faces peintes en magenta.

    En orthographique, cam.cadre = (pixels par unite, cx, cy) en pixels de l'image finale apres l'appel :
    pixel = (res_l / 2 + k * (p.droite - cx), res_h / 2 - k * (p.haut - cy)) avec cam.droite et cam.haut.
    """
    W, H = res[0] * ss, res[1] * ss
    img = np.empty((H, W, 3), np.uint8)
    img[:] = fond_lignes(H)[:, None, :]
    proj = projeter(scene, cam, W, H, echelle=None if echelle is None else echelle * ss)
    if proj is None:
        return Image.fromarray(img).reduce(ss) if ss > 1 else Image.fromarray(img), 0
    sx, sy, q, tface, rang = proj
    if cam.ortho is not None:
        cam.cadre = (cam.cadre[0] / ss, cam.cadre[1], cam.cadre[2])
    zbuf, ids = rasteriser(sx, sy, q, rang, W, H)
    ntri = len(sx)
    del sx, sy, q, rang
    # couleur par face (ombrage fixe)
    teinte = scene.couleurs * ombrage(scene.normales)[:, None]
    if surbrillance:
        for k in surbrillance:
            teinte[k] = np.array(MAGENTA, float) * (0.75 + 0.25 * ombrage(scene.normales[k:k + 1])[0])
    couleur_tri = np.clip(teinte[tface], 0, 255).astype(np.uint8)
    bande = 128                                  # traitement par bandes de lignes : peu de memoire
    ptp = 1.0
    if cam.ortho is not None:   # etendue des profondeurs, sans copier le z-buffer
        pl_tout = ids >= 0
        if pl_tout.any():
            ptp = float(zbuf.max() - np.min(zbuf, where=pl_tout, initial=np.inf))
        del pl_tout
    for r0 in range(0, H, bande):
        r1 = min(H, r0 + bande)
        idb = ids[r0 * W:r1 * W]
        pl = idb >= 0
        blk = img[r0:r1].reshape(-1, 3)
        blk[pl] = couleur_tri[idb[pl]]
        if brume and cam.ortho is None:
            z = 1.0 / np.maximum(zbuf[r0 * W:r1 * W][pl], 1e-12)
            t = (1 - np.exp(-z / (brume * ss))).astype(np.float32)[:, None]
            blk[pl] = (blk[pl] * (1 - t) + COULEUR_FOND_BAS.astype(np.float32) * t).astype(np.uint8)
    if aretes:  # contours aux discontinuites de profondeur (la proximite est affine sur un plan : derivee seconde nulle)
        for r0 in range(0, H, bande):
            r1 = min(H, r0 + bande)
            a, b = max(0, r0 - 1), min(H, r1 + 1)
            pl = (ids[a * W:b * W] >= 0).reshape(b - a, W)
            z = np.where(pl, zbuf[a * W:b * W].reshape(b - a, W), 0.0).astype(np.float32)
            ref = np.maximum(np.abs(z), 1e-9) if cam.ortho is None else max(ptp, 1e-6)
            bord = np.zeros((b - a, W), bool)
            d2 = np.abs(z[:, 2:] - 2 * z[:, 1:-1] + z[:, :-2])
            bord[:, 1:-1] |= pl[:, 2:] & pl[:, 1:-1] & pl[:, :-2] & (d2 / (ref[:, 1:-1] if cam.ortho is None else ref) > 0.004)
            d2 = np.abs(z[2:] - 2 * z[1:-1] + z[:-2])
            bord[1:-1] |= pl[2:] & pl[1:-1] & pl[:-2] & (d2 / (ref[1:-1] if cam.ortho is None else ref) > 0.004)
            sel = bord[r0 - a:r1 - a]
            tranche = img[r0:r1]
            tranche[sel] = (tranche[sel] * 0.7).astype(np.uint8)
    im = Image.fromarray(img)
    if ss > 1:
        im = im.reduce(ss)
    return im, ntri


def etiqueter(im, texte):
    d = ImageDraw.Draw(im)
    try:
        police = ImageFont.load_default(size=15)
    except TypeError:  # PIL ancien
        police = ImageFont.load_default()
    bb = d.textbbox((0, 0), texte, font=police)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.rectangle([6, im.height - h - 18, w + 18, im.height - 6], fill=(20, 20, 24))
    d.text((12, im.height - h - 14), texte, fill=(240, 240, 240), font=police)


# --- cadrages nommes -----------------------------------------------------------------------

FACES = {"est": (1.0, 0.0), "ouest": (-1.0, 0.0), "nord": (0.0, 1.0), "sud": (0.0, -1.0)}


def infos_batiment(nom, liste, sources):
    """Boite englobante et niveau du rez-de-chaussee d'un prefab batiment_N.map."""
    idx = [i for i, s in enumerate(sources) if s.stem == nom]
    if idx:
        fs = [f for f in liste if f.src == idx[0]]
    else:
        chemin = PREFABS / f"{nom}.map"
        if not chemin.exists():
            raise SystemExit(f"cible inconnue : {nom} (attendu : un prefab {chemin})")
        fs, _, _ = charger([chemin])
    v = np.array([p for f in fs for p in f.pts])
    lo, hi = v.min(0), v.max(0)
    # le sol du rez est la face +z la plus basse en travertin (sol des halls, cf. immeuble.py) ; sinon bas - fondation
    sols = [f.pts[0][2] for f in fs if f.n[2] > 0.99 and "travertine" in f.mat]
    z0 = min(sols) if sols else lo[2] + FONDATION
    return lo, hi, z0


def cadrer_cible(args, liste, sources, res):
    lo, hi, z0 = infos_batiment(args.cible, liste, sources)
    nx, ny = FACES[args.face]
    nrm = np.array([nx, ny, 0.0])
    droite = np.cross(-nrm, (0, 0, 1))                # a droite de la camera
    axe = 0 if abs(nrm[1]) > 0.5 else 1               # axe de l'etendue le long de la facade
    centre = (lo + hi) / 2
    plan = hi[0] if nx > 0 else lo[0] if nx < 0 else hi[1] if ny > 0 else lo[1]
    tmin, tmax = lo[axe], hi[axe]
    s_gauche = (tmin if droite[axe] > 0 else tmax)    # extremite a gauche vue de la camera
    sens = 1 if droite[axe] > 0 else -1
    larg = tmax - tmin
    f0, f1 = args.portion
    a0, a1 = s_gauche + sens * f0 * larg, s_gauche + sens * f1 * larg
    n0, n1 = args.niveaux if args.niveaux else (0.0, (hi[2] - z0) / HAUTEUR_ETAGE)
    zb0, zb1 = z0 + n0 * HAUTEUR_ETAGE, z0 + n1 * HAUTEUR_ETAGE
    cible = np.zeros(3)
    cible[axe] = (a0 + a1) / 2
    cible[1 - axe] = plan
    cible[2] = (zb0 + zb1) / 2
    ratio = res[0] / res[1]
    tv = math.tan(math.radians(args.fov) / 2)
    th = tv * ratio
    d = args.distance or 1.12 * max(abs(a1 - a0) / 2 / th / math.cos(math.radians(args.yaw)), (zb1 - zb0) / 2 / tv)
    yaw, pitch = math.radians(args.yaw), math.radians(args.pitch)
    dirv = math.cos(pitch) * (math.cos(yaw) * nrm + math.sin(yaw) * droite) + math.sin(pitch) * np.array([0, 0, 1.0])
    oeil = cible + d * dirv
    return oeil, cible


# --- ligne de commande -----------------------------------------------------------------------

def lire_args(argv):
    p = argparse.ArgumentParser(description="Rendu PNG de fichiers .map Radiant (z-buffer, ombrage lambertien).",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fichiers", nargs="*", help="fichiers .map (defaut : quartier, batiments, map principale)")
    p.add_argument("-o", "--sortie", default=str(RACINE / "_build" / "renders" / "rendu.png"))
    p.add_argument("--boite", type=float, nargs=6, metavar=("X0", "Y0", "Z0", "X1", "Y1", "Z1"))
    p.add_argument("--centre", action="store_true")
    p.add_argument("--sans", default="")
    p.add_argument("--seulement", default="")
    p.add_argument("--sans-modeles", action="store_true")
    p.add_argument("--sans-vegetation", action="store_true")
    p.add_argument("--reperes", action="store_true")
    p.add_argument("--ciel", action="store_true")
    p.add_argument("--vue", type=float, nargs=2, metavar=("AZIMUT", "ELEVATION"))
    p.add_argument("--camera", type=float, nargs=6, metavar=("EX", "EY", "EZ", "CX", "CY", "CZ"))
    p.add_argument("--cible")
    p.add_argument("--face", default="est", choices=sorted(FACES))
    p.add_argument("--portion", type=float, nargs=2, default=(0.0, 1.0))
    p.add_argument("--niveaux", type=float, nargs=2)
    p.add_argument("--yaw", type=float, default=20.0)
    p.add_argument("--pitch", type=float, default=8.0)
    p.add_argument("--distance", type=float)
    p.add_argument("--fov", type=float, default=55.0)
    p.add_argument("--res", type=int, nargs=2, default=(1600, 1000))
    p.add_argument("--ss", type=int, default=2)
    p.add_argument("--brume", type=float)
    p.add_argument("--zfight", action="store_true")
    p.add_argument("--sans-aretes", action="store_true")
    p.add_argument("--etiquette")
    p.add_argument("--info", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    """Execute la ligne de commande ; retourne (image PIL, camera, scene) pour les scripts qui annotent le rendu."""
    args = lire_args(sys.argv[1:] if argv is None else argv)
    t0 = time.time()
    chemins = [Path(f) for f in args.fichiers] or [c for c in DEFAUT if c.exists()]
    liste, sources, entites = charger(chemins, ciel=args.ciel)
    if not args.sans_modeles:
        brush = max((f.brush for f in liste), default=0) + 1
        for src, cls, kv in entites:
            if cls == "misc_model":
                liste += placeholder(cls, kv, brush, src)
                brush += 1
    if args.reperes:
        liste += reperes(entites, max((f.brush for f in liste), default=0) + 1)
    if args.info:
        for nom in ("batiment_1", "batiment_2", "batiment_3"):
            try:
                lo, hi, z0 = infos_batiment(nom, liste, sources)
                print(f"{nom} : x {lo[0]:.0f}..{hi[0]:.0f}  y {lo[1]:.0f}..{hi[1]:.0f}  z {lo[2]:.0f}..{hi[2]:.0f}  sol du rez z={z0:.0f}")
            except SystemExit as e:
                print(e)
        return None
    liste = filtrer(liste, args.boite, args.centre, [m for m in args.sans.split(",") if m],
                    [m for m in args.seulement.split(",") if m], args.sans_vegetation)
    if not liste:
        raise SystemExit("aucune face apres filtrage")
    surbrillance, rapport = None, ""
    if args.zfight:
        paires = coplanaires(liste)
        visibles = [t for t in paires if liste[t[1]].mat != liste[t[2]].mat]  # memes materiaux : indiscernable
        print(f"z-fighting : {len(paires)} paires de faces coplanaires de meme sens qui se recouvrent, "
              f"dont {len(visibles)} de materiaux differents (zones communes en magenta)")
        for aire, i, j, _ in visibles[:15]:
            a, b = liste[i], liste[j]
            c = np.mean(a.pts, axis=0)
            print(f"  {aire:8.0f} u2  {a.mat} / {b.mat}  pres de ({c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f})")
        brush = max(f.brush for f in liste) + 1
        liste = liste + [Face(liste[i].n, zone, "zfight_zone", MAGENTA, brush + k, liste[i].src)
                         for k, (_, i, _, zone) in enumerate(visibles)]
        rapport = f" | z-fighting {len(visibles)} paires"
    scene = Scene(liste)

    res = tuple(args.res)
    if args.cible:
        oeil, cible = cadrer_cible(args, liste, sources, res)
        cam = Camera(oeil, cible, args.fov)
        desc = f"cible {args.cible} face {args.face}"
    elif args.camera:
        cam = Camera(args.camera[:3], args.camera[3:], args.fov)
        desc = "camera " + " ".join(f"{v:g}" for v in args.camera)
    else:
        az, el = args.vue or (35.0, 35.0)
        cam = Camera(ortho=(az, el))
        desc = f"vue orthographique azimut {az:g} elevation {el:g}"
    ss = max(1, args.ss)
    try:
        im, ntri = rendre(scene, cam, res, ss, args.brume, not args.sans_aretes, surbrillance)
    except MemoryError:  # machine chargee : on retente sans surechantillonnage (4 fois moins de memoire)
        if ss == 1:
            raise
        gc.collect()
        print("memoire insuffisante : nouvel essai avec --ss 1", file=sys.stderr)
        im, ntri = rendre(scene, cam, res, 1, args.brume, not args.sans_aretes, surbrillance)
    if args.etiquette:
        etiqueter(im, args.etiquette)
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    print(f"{sortie} : {res[0]}x{res[1]}, {len(liste)} faces, {ntri} triangles, {desc}{rapport}, {time.time() - t0:.1f} s")
    if cam.oeil is not None:
        print("  --camera", " ".join(f"{v:.0f}" for v in (*cam.oeil, *cam.cible)))
    return im, cam, scene


if __name__ == "__main__":
    main()
