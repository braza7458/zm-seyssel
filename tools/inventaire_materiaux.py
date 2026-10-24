"""Inventaire des materiaux et des modeles disponibles dans les Mod Tools BO3 (lecture seule).

Lit tous les .gdt des Mod Tools (materiaux, images, modeles), resout l'heritage des
instances `"nom" [ "parent" ]`, verifie que les images existent, mesure les modeles
(boite englobante lue dans les .xmodel_bin), prepare des apercus PNG et ecrit :

    reference/materiaux.json                    donnees structurees (besoin -> candidats)
    docs/references/materiaux-disponibles.md    tableau par besoin, avec avis motive
    _build/mat_preview/*.png                    apercus (ignores par git)

Les besoins, candidats et avis sont dans inventaire_materiaux_spec.py : ce fichier-ci
ne contient que le moteur (il ne decide rien). Un candidat n'est marque "verifie" que si
son nom exact est retrouve comme en-tete d'entree dans un .gdt.

Usage :
    python tools/inventaire_materiaux.py [--mt "<dossier des Mod Tools>"] [--sans-apercus]

Dependances : Pillow, numpy, opencv (seulement pour les images ; c'est un outil, pas le generateur).
"""

import argparse
import ast
import datetime
import json
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MT_DEFAUT = Path(r"D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130")
BS = chr(92)

RX_ENTETE = re.compile(r'^\s*"([^"]+)"\s*\(\s*"([^"]+)"\s*\)\s*$')
RX_ENTETE_P = re.compile(r'^\s*"([^"]+)"\s*\[\s*"([^"]+)"\s*\]\s*$')
RX_CLE = re.compile(r'^\s*"([^"]*)"\s+"(.*)"\s*$')
RX_FACE = re.compile(r'\)\s+(\S+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\S+)\s+(-?[\d.]+)\s+(-?[\d.]+)')
RX_SOMMET = re.compile(rb'\x03\x8f(..)\x83\x93\x00\x00', re.S)


# --- lecture des GDT --------------------------------------------------------------------

def lire_gdt(chemin):
    sortie, cur, attente = [], None, None
    with open(chemin, "r", encoding="latin-1", errors="replace") as f:
        for ligne in f:
            if cur is None:
                m = RX_ENTETE.match(ligne)
                if m:
                    attente = (m.group(1), m.group(2), None)
                    continue
                m = RX_ENTETE_P.match(ligne)
                if m:
                    attente = (m.group(1), None, m.group(2))
                    continue
                if ligne.strip() == "{" and attente:
                    cur = {"nom": attente[0], "gdf": attente[1], "parent": attente[2], "props": {}}
                    attente = None
                continue
            if ligne.strip() == "}":
                sortie.append(cur)
                cur = None
                continue
            m = RX_CLE.match(ligne)
            if m:
                cur["props"][m.group(1)] = m.group(2)
    return sortie


class Inventaire:
    def __init__(self, mt):
        self.mt = Path(mt)
        self.entrees = []
        self.fichiers = []
        for racine, _, noms in os.walk(self.mt):
            for fn in noms:
                if fn.lower().endswith(".gdt"):
                    p = Path(racine) / fn
                    rel = str(p.relative_to(self.mt)).replace(BS, "/")
                    self.fichiers.append(rel)
                    for e in lire_gdt(p):
                        e["fichier"] = rel
                        self.entrees.append(e)
        self.par_nom = defaultdict(list)
        for e in self.entrees:
            self.par_nom[e["nom"]].append(e)
        for e in self.entrees:
            e["genre"] = self._genre(e)
        self._eff = {}
        self.materiaux = defaultdict(list)
        self.images = defaultdict(list)
        self.modeles = defaultdict(list)
        for e in self.entrees:
            if e["genre"] == "material.gdf":
                self.materiaux[e["nom"]].append(e)
            elif e["genre"] == "image.gdf":
                self.images[e["nom"]].append(e)
            elif e["genre"] == "xmodel.gdf":
                self.modeles[e["nom"]].append(e)
        self._dims = {}

    def _genre(self, e, prof=0):
        if e["gdf"]:
            return e["gdf"]
        if prof > 12:
            return None
        for c in self.par_nom.get(e["parent"], []):
            if c is not e:
                g = self._genre(c, prof + 1)
                if g:
                    return g
        return None

    def chaine(self, e, prof=0):
        if e["gdf"] or prof > 12:
            return [e]
        for c in self.par_nom.get(e["parent"], []):
            if c is not e and self._genre(c):
                return self.chaine(c, prof + 1) + [e]
        return [e]

    def eff(self, e):
        k = id(e)
        if k not in self._eff:
            p = {}
            for x in self.chaine(e):
                p.update(x["props"])
            self._eff[k] = p
        return self._eff[k]

    def chemin_image(self, base):
        return self.mt / base.replace(BS + BS, BS) if base else None

    # --- images ---
    def info_image(self, nom):
        if not nom:
            return None
        if nom.startswith("$"):
            return {"image": nom, "code": True, "existe": True, "dimensions": None}
        ents = self.images.get(nom)
        if not ents:
            return {"image": nom, "gdt_image": False, "existe": False, "dimensions": None}
        p = self.eff(ents[0])
        base = p.get("baseImage", "").replace(BS + BS, BS)
        chemin = self.mt / base if base else None
        existe = bool(chemin and chemin.is_file())
        dims, bits = None, None
        if existe:
            if chemin not in self._dims:
                try:
                    from PIL import Image
                    im = Image.open(chemin)
                    self._dims[chemin] = (list(im.size), im.tag_v2.get(258, [None])[0] if hasattr(im, "tag_v2") else None)
                except Exception:
                    self._dims[chemin] = (None, None)
            dims, bits = self._dims[chemin]
        return {"image": nom, "gdt_image": True, "fichier_image": base.replace(BS, "/"), "existe": existe,
                "dimensions": dims, "bits": bits, "gdt": ents[0]["fichier"]}

    def info_materiau(self, nom):
        ents = self.materiaux.get(nom)
        if not ents:
            return None
        e = ents[0]
        p = self.eff(e)
        cm = p.get("colorMap") or p.get("colorMap00") or ""
        manquantes, secondaires = [], []
        for k in ("colorMap", "normalMap", "alphaRevealMap", "detailMap", "specColorMap", "cosinePowerMap", "occMap"):
            v = p.get(k, "")
            if v and not v.startswith("$"):
                ii = self.info_image(v)
                if not ii["existe"]:
                    (manquantes if k in ("colorMap", "normalMap", "alphaRevealMap", "detailMap") else secondaires).append(v)
        return {
            "nom": nom, "verifie": True, "gdt": e["fichier"], "parent": e["parent"],
            "racine": self.chaine(e)[0]["nom"], "nb_definitions": len(ents),
            "materialType": p.get("materialType"), "surfaceType": p.get("surfaceType"), "usage": p.get("usage"),
            "colorTint": p.get("colorTint"), "colorMap": self.info_image(cm), "normalMap": self.info_image(p.get("normalMap")),
            "detailMap": p.get("detailMap") or None, "doNotUse": p.get("doNotUse") == "1",
            "images_manquantes": manquantes, "cartes_secondaires_absentes": secondaires,
        }

    def info_modele(self, nom):
        ents = self.modeles.get(nom)
        if not ents:
            return None
        e = ents[0]
        p = self.eff(e)
        fn = p.get("filename", "").replace(BS + BS, BS)
        chemin = self.mt / "model_export" / fn
        lods = []
        for k in ("mediumLod", "lowLod", "lowestLod"):
            v = p.get(k, "").replace(BS + BS, BS)
            if v:
                lods.append((self.mt / "model_export" / v).is_file())
        return {"nom": nom, "verifie": True, "gdt": e["fichier"], "parent": e["parent"], "type": p.get("type"),
                "fichier": ("model_export/" + fn.replace(BS, "/")) if fn else None, "fichier_present": chemin.is_file(),
                "lod_autres": len(lods), "lod_autres_presents": sum(lods), "scale_gdt": p.get("scale")}

    def comptes_par_zone(self):
        zones = defaultdict(Counter)
        for e in self.entrees:
            rel = e["fichier"]
            if rel.startswith("texture_assets/"):
                z = "texture_assets/*.gdt"
            elif rel.startswith("art_assets/t6_legacy/texture_assets/"):
                z = "art_assets/t6_legacy/texture_assets/*.gdt"
            elif rel.startswith("model_export/"):
                z = "model_export/**.gdt"
            elif rel.startswith("source_data/"):
                z = "source_data/*.gdt"
            else:
                z = rel.split("/")[0] + "/*.gdt"
            zones[z][e["genre"] or "autre"] += 1
        nb_fichiers = Counter()
        for rel in self.fichiers:
            if rel.startswith("texture_assets/"):
                nb_fichiers["texture_assets/*.gdt"] += 1
            elif rel.startswith("art_assets/t6_legacy/texture_assets/"):
                nb_fichiers["art_assets/t6_legacy/texture_assets/*.gdt"] += 1
            elif rel.startswith("model_export/"):
                nb_fichiers["model_export/**.gdt"] += 1
            elif rel.startswith("source_data/"):
                nb_fichiers["source_data/*.gdt"] += 1
            else:
                nb_fichiers[rel.split("/")[0] + "/*.gdt"] += 1
        return zones, nb_fichiers


# --- verification textuelle independante des noms ----------------------------------------

def verifier_noms_texte(mt, noms):
    """Recherche textuelle exacte : le nom doit etre l'en-tete d'une entree ("nom" ( ou "nom" [)."""
    restants = set(noms)
    trouves = {}
    rx = re.compile(r'^\s*"([^"\r\n]+)"\s*[\(\[]', re.M)
    for racine, _, fns in os.walk(mt):
        for fn in fns:
            if not fn.lower().endswith(".gdt"):
                continue
            p = Path(racine) / fn
            txt = p.read_text(encoding="latin-1", errors="replace")
            for m in rx.finditer(txt):
                n = m.group(1)
                if n in restants and n not in trouves:
                    trouves[n] = str(p.relative_to(mt)).replace(BS, "/")
    return trouves


# --- echelles de repetition observees dans les .map officiels -------------------------------

def echelles_stock(mt):
    tally = defaultdict(Counter)
    nb = 0
    for racine, _, fns in os.walk(Path(mt) / "map_source"):
        for fn in fns:
            if not fn.lower().endswith(".map") or "seyssel" in (racine + fn).lower():
                continue
            nb += 1
            with open(Path(racine) / fn, "r", encoding="latin-1") as f:
                for ligne in f:
                    if ligne.lstrip().startswith("( "):
                        m = RX_FACE.search(ligne)
                        if m:
                            a, b = abs(float(m.group(2))), abs(float(m.group(3)))
                            tally[m.group(1)][(round(a, 1), round(b, 1))] += 1
    return tally, nb


def lire_mat_projet():
    """Lit le dictionnaire MAT de tools/quartier.py sans l'importer."""
    src = (ROOT / "tools" / "quartier.py").read_text(encoding="utf-8")
    i = src.index("MAT = {")
    j = src.index("\n}\n", i) + 2
    return ast.literal_eval(src[i + len("MAT = "):j])


# --- images : apercus et statistiques ----------------------------------------------------------

def _outils_image():
    import cv2
    import numpy as np
    try:
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
    except Exception:
        pass
    return cv2, np


def lire_rgba(chemin):
    cv2, np = _outils_image()
    im = cv2.imread(str(chemin), cv2.IMREAD_UNCHANGED)
    if im is None:
        raise ValueError("lecture impossible")
    if im.dtype == np.uint16:
        im = (im / 257.0).astype(np.uint8)
    elif im.dtype != np.uint8:
        im = np.clip(im * 255.0, 0, 255).astype(np.uint8)
    if im.ndim == 2:
        return np.stack([im] * 3, axis=-1), None
    if im.shape[2] == 4:
        return np.ascontiguousarray(im[:, :, 2::-1]), np.ascontiguousarray(im[:, :, 3])
    if im.shape[2] == 3:
        return np.ascontiguousarray(im[:, :, ::-1]), None
    return np.repeat(im[:, :, :1], 3, axis=2), None


def analyser_image(chemin, teinte, png_sortie, alpha_decoupe):
    """Statistiques + apercu PNG (<= 512 px). alpha_decoupe : montrer le motif de l'alpha sur un damier."""
    cv2, np = _outils_image()
    from PIL import Image
    rgb, a = lire_rgba(chemin)
    t = [1.0, 1.0, 1.0]
    if teinte:
        try:
            t = [float(x) for x in teinte.split()[:3]]
        except ValueError:
            pass
    rgbf = np.clip(rgb.astype(np.float32) * np.array(t, dtype=np.float32), 0, 255)
    h, w = rgb.shape[:2]
    masque = None
    stats_alpha = None
    if a is not None:
        stats_alpha = {"min": int(a.min()), "max": int(a.max()), "moyenne": round(float(a.mean()), 1),
                       "part_sous_128": round(float((a < 128).mean()), 3), "utile": bool(a.min() < 250)}
        if alpha_decoupe and stats_alpha["utile"]:
            masque = a >= 128
    px = rgbf[masque] if masque is not None and masque.any() else rgbf.reshape(-1, 3)
    moy = px.astype(np.float64).mean(axis=0)
    lum = rgbf.astype(np.float64).mean(axis=2)
    ecart = float(lum.std())
    # raccord : ecart moyen entre bords opposes, compare a l'ecart entre colonnes voisines
    dx = float(np.abs(lum[:, 0] - lum[:, -1]).mean())
    dy = float(np.abs(lum[0, :] - lum[-1, :]).mean())
    ref = float(np.abs(lum[:, 0] - lum[:, 1]).mean())
    aperc = rgbf.astype(np.uint8)
    if masque is not None or (a is not None and alpha_decoupe and stats_alpha["utile"]):
        yy, xx = np.mgrid[0:h, 0:w]
        case = max(8, min(w, h) // 32)
        damier = np.where(((yy // case + xx // case) % 2 == 0)[:, :, None], 190, 120).astype(np.float32)
        al = (a.astype(np.float32) / 255.0)[:, :, None]
        aperc = (rgbf * al + damier * (1 - al)).astype(np.uint8)
    im = Image.fromarray(aperc)
    k = 512 / max(w, h) if max(w, h) > 512 else 1.0
    if k < 1.0:
        im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    if png_sortie is not None:
        png_sortie.parent.mkdir(parents=True, exist_ok=True)
        im.save(png_sortie, optimize=True)
    r, g, b = (int(round(x)) for x in moy)
    return {"couleur_moyenne": "#%02x%02x%02x" % (r, g, b), "ecart_type_luminance": round(ecart, 1),
            "raccord_x": round(dx, 1), "raccord_y": round(dy, 1), "bruit_reference": round(ref, 1),
            "raccord_douteux": bool(max(dx if w < 3 * h else 0.0, dy if h < 3 * w else 0.0) > 12
                                    and max(dx if w < 3 * h else 0.0, dy if h < 3 * w else 0.0) > 3 * max(ref, 1.0)),
            "dimensions": [w, h], "alpha": stats_alpha}


def planche(png_dir, noms, fichier, colonnes=3, cellule=320, repetition=2):
    """Planche contact : chaque case montre la texture repetee repetition x repetition."""
    from PIL import Image, ImageDraw, ImageFont
    lignes = math.ceil(len(noms) / colonnes)
    lab = 34
    feuille = Image.new("RGB", (colonnes * cellule, lignes * (cellule + lab)), (30, 30, 30))
    d = ImageDraw.Draw(feuille)
    try:
        police = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        police = ImageFont.load_default()
    for i, n in enumerate(noms):
        p = png_dir / (n + ".png")
        if not p.is_file():
            continue
        im = Image.open(p).convert("RGB")
        w, h = im.size
        t = cellule // repetition
        s = t / max(w, h)
        petit = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        sw, sh = petit.size
        toile = Image.new("RGB", (cellule, cellule), (60, 60, 60))
        for ix in range(repetition):
            for iy in range(repetition):
                toile.paste(petit, (ix * sw, iy * sh))
        cx, cy = (i % colonnes) * cellule, (i // colonnes) * (cellule + lab)
        feuille.paste(toile, (cx, cy))
        d.text((cx + 4, cy + cellule + 2), n[:46], fill=(255, 255, 255), font=police)
        d.text((cx + 4, cy + cellule + 18), "%dx%d" % (w, h), fill=(180, 180, 180), font=police)
    feuille.save(png_dir / fichier, optimize=True)


# --- modeles : boite englobante (les .xmodel_bin sont du LZ4 contenant un maillage binaire) ----------

def lz4_bloc(src, debut, taille_sortie):
    out = bytearray()
    i, n = debut, len(src)
    while i < n and len(out) < taille_sortie:
        tok = src[i]
        i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        out += src[i:i + lit]
        i += lit
        if len(out) >= taille_sortie or i >= n:
            break
        dec = src[i] | (src[i + 1] << 8)
        i += 2
        ml = tok & 15
        if ml == 15:
            while True:
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        ml += 4
        d0 = len(out) - dec
        if d0 < 0:
            raise ValueError("decalage LZ4 invalide")
        for k in range(ml):
            out.append(out[d0 + k])
    return bytes(out)


def sommets_modele(chemin):
    d = Path(chemin).read_bytes()
    if d[:5] == b"*LZ4*":
        d = lz4_bloc(d, 9, struct.unpack("<I", d[5:9])[0])
    pts = []
    for m in RX_SOMMET.finditer(d):
        p = m.end()
        if p + 12 > len(d):
            break
        x, y, z = struct.unpack("<fff", d[p:p + 12])
        if all(abs(v) < 1e5 and v == v for v in (x, y, z)):
            pts.append((x, y, z))
    return pts


def boite_modele(chemin):
    """Dimensions (pouces = unites de jeu a l'echelle 1) du LOD0, mesurees sur les sommets. None si illisible."""
    try:
        if Path(chemin).stat().st_size > 2_500_000:
            return None
        pts = sommets_modele(chemin)
    except Exception:
        return None
    if len(pts) < 3:
        return None
    mn = [min(p[i] for p in pts) for i in range(3)]
    mx = [max(p[i] for p in pts) for i in range(3)]
    return {"dim_unites": [round(mx[i] - mn[i], 1) for i in range(3)], "min": [round(v, 1) for v in mn], "max": [round(v, 1) for v in mx],
            "sommets_lod0": len(pts)}


def planche_silhouettes(chemins, noms, sortie, cellule=300):
    """Silhouettes (nuage de sommets du LOD0) vue de face et de cote, a l'echelle ; une case par modele."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    colonnes = 3
    lignes = math.ceil(len(noms) / colonnes)
    lab = 30
    feuille = Image.new("RGB", (colonnes * cellule, lignes * (cellule + lab)), (28, 28, 28))
    d = ImageDraw.Draw(feuille)
    try:
        police = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        police = ImageFont.load_default()
    for i, (n, ch) in enumerate(zip(noms, chemins)):
        try:
            pts = np.array(sommets_modele(ch), dtype=np.float32)
        except Exception:
            continue
        if len(pts) < 3:
            continue
        mn, mx = pts.min(axis=0), pts.max(axis=0)
        dim = mx - mn
        moitie = cellule // 2 - 6
        sc = min(moitie / max(dim[0], dim[1], 1e-3), (cellule - 20) / max(dim[2], 1e-3))
        cx, cy = (i % colonnes) * cellule, (i // colonnes) * (cellule + lab)
        for k, a in enumerate((0, 1)):
            w, h = int(dim[a] * sc) + 2, int(dim[2] * sc) + 2
            img = np.zeros((h, w), dtype=np.uint16)
            u = ((pts[:, a] - mn[a]) * sc).astype(int)
            v = (h - 1 - ((pts[:, 2] - mn[2]) * sc)).astype(int)
            ok = (u >= 0) & (u < w) & (v >= 0) & (v < h)
            np.add.at(img, (v[ok], u[ok]), 1)
            g = Image.fromarray(np.clip(img * 40, 0, 255).astype(np.uint8))
            feuille.paste(Image.merge("RGB", [g, g, g]), (cx + 4 + k * (moitie + 8), cy + cellule - 6 - h))
        d.text((cx + 4, cy + cellule + 2), n[:44], fill=(255, 255, 255), font=police)
        d.text((cx + 4, cy + cellule + 16), "%.1f x %.1f x %.1f m (L x l x H)" % (dim[0] * 0.0254, dim[1] * 0.0254, dim[2] * 0.0254), fill=(170, 170, 170), font=police)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    feuille.save(sortie, optimize=True)


# --- echelle de repetition conseillee ------------------------------------------------------------

def echelle_conseillee(nom, dims, stock, stock_image, image):
    """-> dict(valeur, source, detail, unites). Valeurs en unites de jeu a l'echelle 1 (un pouce)."""
    c = stock.get(nom)
    if c:
        (w, h), n = c.most_common(1)[0]
        return {"valeur": "%g x %g" % (w, h), "source": "stock", "detail": "%d faces sur %d dans les .map officiels" % (n, sum(c.values())), "unites": (w, h)}
    for suf in ("_wet", "_nw", "_blend", "_wet_nw"):
        c = stock.get(nom + suf)
        if c:
            (w, h), n = c.most_common(1)[0]
            return {"valeur": "%g x %g" % (w, h), "source": "stock_variante",
                    "detail": "stock d'un autre materiau de meme nom (%s) : %d faces sur %d" % (nom + suf, n, sum(c.values())), "unites": (w, h), "variante": nom + suf}
    if image and image in stock_image:
        c, autre = stock_image[image]
        (w, h), n = c.most_common(1)[0]
        return {"valeur": "%g x %g" % (w, h), "source": "stock_variante",
                "detail": "stock d'un autre materiau de meme image (%s) : %d faces sur %d" % (autre, n, sum(c.values())), "unites": (w, h), "variante": autre}
    if dims and dims[0] and dims[1]:
        ratio = dims[1] / dims[0]
        w, h = (64.0 / ratio, 64.0) if ratio >= 1 else (64.0, 64.0 * ratio)
        return {"valeur": "%g x %g" % (round(w, 1), round(h, 1)), "source": "estimee",
                "detail": "estimation : proportions de l'image, 64 unites sur le grand cote", "unites": (round(w, 1), round(h, 1))}
    return {"valeur": "inconnue", "source": "inconnue", "detail": "aucune donnee", "unites": None}


def stock_par_image(inv, stock):
    """image couleur -> (cumul des echelles de tous les materiaux du stock qui l'utilisent, materiau le plus utilise)."""
    par = {}
    for mat, cnt in stock.items():
        ents = inv.materiaux.get(mat)
        if not ents:
            continue
        p = inv.eff(ents[0])
        img = p.get("colorMap") or p.get("colorMap00")
        if not img or img.startswith("$"):
            continue
        tot, best = par.get(img, (Counter(), (None, 0)))
        tot.update(cnt)
        n = sum(cnt.values())
        if n > best[1]:
            best = (mat, n)
        par[img] = (tot, best)
    return {img: (tot, best[0]) for img, (tot, best) in par.items()}


# --- generation ----------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mt", default=str(MT_DEFAUT))
    ap.add_argument("--sans-apercus", action="store_true")
    args = ap.parse_args()
    mt = Path(args.mt)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import inventaire_materiaux_spec as SP
    from inventaire_materiaux_rendu import ecrire_md

    print("lecture des GDT dans", mt)
    inv = Inventaire(mt)
    print(len(inv.fichiers), "fichiers .gdt,", len(inv.entrees), "entrees")
    mat_projet = lire_mat_projet()
    stock, nb_map = echelles_stock(mt)
    stock_image = stock_par_image(inv, stock)
    png_dir = ROOT / "_build" / "mat_preview"

    # noms a verifier par recherche textuelle
    noms_mat = set(mat_projet.values())
    for b in SP.BESOINS:
        noms_mat.update(c["nom"] for c in b["candidats"])
    for r in SP.REMPLACEMENTS:
        for k in ("par", "alt"):
            if r.get(k):
                noms_mat.add(r[k])
    noms_mod = set()
    for m in SP.MODELES:
        noms_mod.update(c["nom"] for c in m["candidats"])
    noms_mod.update(SP.MODELES_PROJET)
    texte = verifier_noms_texte(mt, noms_mat | noms_mod)
    print(len(texte), "noms retrouves par recherche textuelle sur", len(noms_mat | noms_mod))

    cache = {}

    def fiche_materiau(nom, apercu=True):
        if nom in cache:
            return cache[nom]
        mi = inv.info_materiau(nom)
        if mi is None:
            fiche = {"nom": nom, "verifie": False, "note": "nom exact introuvable dans les GDT"}
            cache[nom] = fiche
            return fiche
        mi["verifie"] = nom in texte
        mi["gdt_recherche_texte"] = texte.get(nom)
        ci = mi["colorMap"]
        mi["image_couleur_presente"] = bool(ci and ci.get("existe"))
        p = inv.eff(inv.materiaux[nom][0])
        mt_ = mi["materialType"] or ""
        decoupe = "alphatest" in mt_
        if ci and ci.get("fichier_image") and ci["existe"] and not ci["image"].startswith("$"):
            if apercu and not args.sans_apercus:
                try:
                    mi["analyse"] = analyser_image(mt / ci["fichier_image"], mi["colorTint"], png_dir / (nom + ".png"), decoupe)
                    mi["apercu"] = "_build/mat_preview/%s.png" % nom
                except Exception as ex:
                    mi["analyse"] = {"erreur": str(ex)[:80]}
        else:
            mi["analyse"] = {"note": "couleur de base uniforme ($ code) : l'aspect vient de la teinte et des cartes speculaires, non mesure"}
            tt = mi["colorTint"]
            if tt and ci and ci.get("image") == "$white_diffuse":
                try:
                    r, g, b = [float(x) for x in tt.split()[:3]]
                    mi["analyse"]["couleur_moyenne"] = "#%02x%02x%02x" % tuple(int(round(255 * v)) for v in (r, g, b))
                except ValueError:
                    pass
        dims = (mi["colorMap"] or {}).get("dimensions")
        e = echelle_conseillee(nom, dims, stock, stock_image, (mi["colorMap"] or {}).get("image"))
        wh = e["unites"]
        mi["echelle_map"] = {"valeur": e["valeur"], "source": e["source"], "detail": e["detail"], "unites": list(wh) if wh else None,
                             "unites_projet_x1_25": [round(wh[0] * 1.25, 1), round(wh[1] * 1.25, 1)] if wh else None}
        cache[nom] = mi
        return mi

    # besoins
    besoins_out = []
    for b in SP.BESOINS:
        cands = []
        for c in b["candidats"]:
            f = dict(fiche_materiau(c["nom"]))
            f.update({"rang": c["rang"], "note": c["note"], "avis": c["avis"], "reserves": c.get("reserves", "")})
            cands.append(f)
        sortie = {k: v for k, v in b.items() if k != "candidats"}
        sortie["candidats"] = cands
        besoins_out.append(sortie)

    # materiaux de MAT (toujours analyses, pour le tableau des remplacements)
    mat_out = {}
    for cle, nom in mat_projet.items():
        mat_out[cle] = fiche_materiau(nom)

    # modeles
    modeles_cache = {}

    def fiche_modele(nom):
        mi = inv.info_modele(nom)
        if mi is None:
            return {"nom": nom, "verifie": False, "note": "nom exact introuvable dans les GDT"}
        modeles_cache[nom] = mi
        mi["verifie"] = nom in texte
        mi["gdt_recherche_texte"] = texte.get(nom)
        if mi["fichier"] and mi["fichier_present"]:
            bm = boite_modele(mt / mi["fichier"])
            if bm:
                mi["boite"] = bm
                d = bm["dim_unites"]
                mi["dimensions_m"] = [round(v * 0.0254, 2) for v in d]
                mi["dimensions_m_projet_x1_25"] = [round(v * 0.0254 / 1.25, 2) for v in d]
        return mi

    modeles_out = []
    for m in SP.MODELES:
        cands = []
        for c in m["candidats"]:
            f = fiche_modele(c["nom"])
            f.update({"rang": c["rang"], "note": c["note"], "avis": c["avis"], "reserves": c.get("reserves", "")})
            cands.append(f)
        sortie = {k: v for k, v in m.items() if k != "candidats"}
        sortie["candidats"] = cands
        modeles_out.append(sortie)
    modeles_projet = {n: fiche_modele(n) for n in SP.MODELES_PROJET}

    # remplacements
    remplacements = []
    for r in SP.REMPLACEMENTS:
        cle = r["cle"]
        actuel = mat_projet.get(cle)
        ligne = {"cle": cle, "actuel": actuel, "actuel_verifie": bool(actuel and cache.get(actuel, {}).get("verifie")),
                 "statut": r["statut"], "remplacer_par": r.get("par"), "alternative": r.get("alt"), "pourquoi": r["pourquoi"]}
        for k, cle_j in (("par", "remplacer_par"), ("alt", "alternative")):
            n = r.get(k)
            if not n:
                continue
            if n in inv.materiaux:
                fiche_materiau(n)
                ligne[cle_j + "_type"] = "materiau"
                ligne[cle_j + "_verifie"] = bool(cache[n].get("verifie"))
            elif n in inv.modeles:
                ligne[cle_j + "_type"] = "modele"
                ligne[cle_j + "_verifie"] = n in texte
            else:
                ligne[cle_j + "_type"] = "inconnu"
                ligne[cle_j + "_verifie"] = False
        remplacements.append(ligne)
    cles_non_traitees = sorted(set(mat_projet) - {r["cle"] for r in SP.REMPLACEMENTS})

    zones, nb_fichiers = inv.comptes_par_zone()
    zones_out = []
    for z in sorted(zones):
        c = zones[z]
        zones_out.append({"zone": z, "fichiers": nb_fichiers[z], "materiaux": c["material.gdf"], "images": c["image.gdf"],
                          "modeles": c["xmodel.gdf"], "instances_ou_autres": sum(c.values()) - c["material.gdf"] - c["image.gdf"] - c["xmodel.gdf"]})

    # planches contact des materiaux cles
    if not args.sans_apercus:
        cles = [n for n in SP.APERCUS_CLES if (png_dir / (n + ".png")).is_file()]
        for k in range(0, len(cles), 12):
            planche(png_dir, cles[k:k + 12], "planche_cles_%d.png" % (k // 12 + 1))

    # echelles de reference observees dans les .map officiels
    echelles_reference = []
    for n in SP.REF_ECHELLES:
        c = stock.get(n)
        mi = inv.info_materiau(n)
        img = ""
        if mi and mi["colorMap"] and mi["colorMap"].get("dimensions"):
            img = "%s (%d x %d px)" % (mi["colorMap"]["image"], mi["colorMap"]["dimensions"][0], mi["colorMap"]["dimensions"][1])
        if c:
            (w, h), nb = c.most_common(1)[0]
            echelles_reference.append({"nom": n, "echelle": "%g x %g" % (w, h), "faces": "%d sur %d" % (nb, sum(c.values())), "image": img})
        else:
            echelles_reference.append({"nom": n, "echelle": "non vu", "faces": "0", "image": img})

    # silhouettes de modeles
    if not args.sans_apercus:
        tous = [n for n in SP.SILHOUETTES if n in modeles_cache]
        for k in range(0, len(tous), 6):
            lot = tous[k:k + 6]
            planche_silhouettes([mt / modeles_cache[n]["fichier"] for n in lot], lot, png_dir / "modeles" / ("silhouettes_%d.png" % (k // 6 + 1)))

    donnees = {
        "meta": {
            "genere_le": datetime.date.today().isoformat(),
            "outil": "tools/inventaire_materiaux.py",
            "mod_tools": str(mt),
            "lecture_seule": True,
            "gdt_lus": len(inv.fichiers), "entrees": len(inv.entrees), "instances": sum(1 for e in inv.entrees if e["parent"]),
            "materiaux_definis": len(inv.materiaux), "images_definies": len(inv.images), "modeles_definis": len(inv.modeles),
            "maps_officielles_lues_pour_les_echelles": nb_map,
            "schema": {
                "besoins_materiaux[].candidats[]": "un materiau : nom, verifie, gdt, parent, materialType, usage, colorTint, colorMap{image,dimensions,existe}, analyse{couleur_moyenne,alpha,raccord_douteux}, "
                                                   "echelle_map{valeur,source,unites,unites_projet_x1_25}, rang, note (1 a 5), avis, reserves",
                "besoins_modeles[].candidats[]": "un modele : nom, verifie, gdt, fichier, type, boite{dim_unites,sommets_lod0}, dimensions_m, rang, note, avis",
                "choix": "raccourci besoin -> noms recommandes / alternatives / limites / a eviter",
                "remplacements_mat[]": "une cle de MAT : actuel, statut (garder/ajuster/remplacer), remplacer_par, alternative, pourquoi, et la verification des noms",
                "instances_a_creer[]": "instances teintees proposees (non testees)",
                "echelle_map.unites": "taille d'une repetition en unites de jeu a l'echelle 1 ; unites_projet_x1_25 tient compte de ECHELLE = 1,25",
                "rang": "recommandé / alternative / limité / à éviter",
            },
            "legende_certitude": {"vu": "lu dans un GDT, mesure sur le fichier image, ou regarde dans un apercu PNG",
                                  "deduit": "conclu a partir d'indices (noms, valeurs, comparaisons) sans le voir tourner dans le jeu",
                                  "inconnu": "non verifiable ici (rendu dans le moteur, couleur reelle du bati)"},
            "verifie": "true seulement si le nom exact est l'en-tete d'une entree d'un .gdt (recherche textuelle independante du parseur)",
            "unites": "1 unite de jeu = 1 pouce = 2,54 cm ; le projet agrandit tout de 1,25 (geo.py : M = 39,37 x 1,25 unites par metre reel)",
        },
        "constats": SP.CONSTATS,
        "priorites": SP.PRIORITES,
        "choix": {
            "materiaux": {b["id"]: {"recommande": [c["nom"] for c in b["candidats"] if c["rang"] == "recommandé"],
                                    "alternatives": [c["nom"] for c in b["candidats"] if c["rang"] == "alternative"],
                                    "limites": [c["nom"] for c in b["candidats"] if c["rang"] == "limité"],
                                    "a_eviter": [c["nom"] for c in b["candidats"] if c["rang"] == "à éviter"]} for b in besoins_out},
            "modeles": {m["id"]: {"recommande": [c["nom"] for c in m["candidats"] if c["rang"] == "recommandé"],
                                  "alternatives": [c["nom"] for c in m["candidats"] if c["rang"] == "alternative"],
                                  "limites": [c["nom"] for c in m["candidats"] if c["rang"] == "limité"],
                                  "a_eviter": [c["nom"] for c in m["candidats"] if c["rang"] == "à éviter"]} for m in modeles_out},
        },
        "zones_gdt": zones_out,
        "echelles_reference": echelles_reference,
        "besoins_materiaux": besoins_out,
        "besoins_modeles": modeles_out,
        "modeles_deja_utilises_dans_le_projet": modeles_projet,
        "mat_projet": {cle: {"nom": nom, "verifie": bool(mat_out[cle].get("verifie")), "gdt": mat_out[cle].get("gdt"),
                             "image_couleur_presente": mat_out[cle].get("image_couleur_presente")} for cle, nom in mat_projet.items()},
        "remplacements_mat": remplacements,
        "cles_mat_sans_avis": cles_non_traitees,
        "instances_a_creer": SP.PROPOSITIONS,
        "limites_et_manques": SP.MANQUES,
    }
    sortie_json = ROOT / "reference" / "materiaux.json"
    sortie_json.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("ecrit", sortie_json, round(sortie_json.stat().st_size / 1024), "Ko")

    sortie_md = ROOT / "docs" / "references" / "materiaux-disponibles.md"
    sortie_md.parent.mkdir(parents=True, exist_ok=True)
    sortie_md.write_text(ecrire_md(donnees, SP), encoding="utf-8", newline="\n")
    print("ecrit", sortie_md, round(sortie_md.stat().st_size / 1024), "Ko")
    if cles_non_traitees:
        print("ATTENTION : cles de MAT sans avis dans la spec :", cles_non_traitees)
    manquants = [c["nom"] for b in besoins_out for c in b["candidats"] if not c.get("verifie")]
    if manquants:
        print("ATTENTION : candidats non verifies :", sorted(set(manquants)))


if __name__ == "__main__":
    main()
