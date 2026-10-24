"""Vues aeriennes IGN recalees sur le repere de jeu, avec calques de comparaison.

Outil d'apercu (PIL + numpy, pas utilise par le generateur) :
    - telecharge l'orthophoto IGN (WMS) d'un cadre exprime en unites de jeu, la tourne pour que l'axe
      du batiment 1 soit vertical (meme orientation que les plans du depot) ;
    - superpose les emprises OSM (cyan), BD TOPO (jaune), la map generee (rouge), les arbres LiDAR (vert) ;
    - analyse le MNH LiDAR HD (hauteurs du sursol) : arbres, toitures.

Usage :
    python tools/ign_vues.py vues            # toutes les vues -> _build/ref/vues/
    python tools/ign_vues.py arbres          # arbres et toitures mesures au LiDAR -> reference/ign/lidar_quartier.json
    python tools/ign_vues.py vue nom x0 y0 x1 y1 px_par_m [calques] [couche]
        calques : lettres parmi o (OSM) b (BD TOPO) g (map generee) a (arbres LiDAR) m (MNH en fond) q (grille en unites de jeu) i (numero BD TOPO des batiments)
"""

import io
import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from geo import BAT1, BAT2, BAT3, M, ROOT, Site
from ign_donnees import REF, WMS_URL, lambert93

VUES = REF / "vues"
BDTOPO = ROOT / "reference" / "ign" / "bdtopo_quartier.json"
LIDAR_JSON = ROOT / "reference" / "ign" / "lidar_quartier.json"

SITE = Site()


# --- orthophoto dans le repere de jeu ------------------------------------------------------
def latlon(x, y):
    return SITE.vers_latlon(x, y)


def telecharger_nord(lat_s, lon_o, lat_n, lon_e, larg, haut, couche, cache):
    cache = Path(cache)
    if cache.exists():
        return Image.open(cache).convert("RGB")
    q = {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": couche, "STYLES": "", "CRS": "EPSG:4326",
         "BBOX": f"{lat_s:.7f},{lon_o:.7f},{lat_n:.7f},{lon_e:.7f}", "WIDTH": larg, "HEIGHT": haut, "FORMAT": "image/jpeg"}
    with urllib.request.urlopen(WMS_URL + "?" + urllib.parse.urlencode(q, safe=",:"), timeout=180) as r:
        data = r.read()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    return Image.open(io.BytesIO(data)).convert("RGB")


class Cadre:
    """Rectangle (x0, y0, x1, y1) en unites de jeu, rendu a `ppm` pixels par metre reel."""

    def __init__(self, x0, y0, x1, y1, ppm):
        self.x0, self.y0, self.x1, self.y1, self.ppm = x0, y0, x1, y1, ppm
        self.u = M / ppm                                  # unites de jeu par pixel
        self.W = int(round((x1 - x0) / self.u))
        self.H = int(round((y1 - y0) / self.u))

    def px(self, x, y):
        return (x - self.x0) / self.u, (self.y1 - y) / self.u

    def jeu(self, u, v):
        return self.x0 + u * self.u, self.y1 - v * self.u


def ortho_jeu(cadre, couche="ORTHOIMAGERY.ORTHOPHOTOS", res_native=5.0, nom="ortho"):
    """Orthophoto (couche WMS) rendue dans le repere de jeu, au pas du cadre."""
    coins = [latlon(*c) for c in ((cadre.x0, cadre.y0), (cadre.x1, cadre.y0), (cadre.x1, cadre.y1), (cadre.x0, cadre.y1))]
    lat_s = min(c[0] for c in coins) - 2e-5
    lat_n = max(c[0] for c in coins) + 2e-5
    lon_o = min(c[1] for c in coins) - 2e-5
    lon_e = max(c[1] for c in coins) + 2e-5
    # image nord en haut a la resolution du cadre (au plus 4096 px), carree en metres
    h_m = (lat_n - lat_s) * 110540
    w_m = (lon_e - lon_o) * 111320 * math.cos(math.radians(SITE.lat0))
    ppm = min(cadre.ppm, 4000 / max(h_m, w_m))
    larg, haut = int(w_m * ppm), int(h_m * ppm)
    cache = REF / "wms" / f"{nom}_{couche}_{lat_s:.6f}_{lon_o:.6f}_{larg}x{haut}.jpg"
    src = telecharger_nord(lat_s, lon_o, lat_n, lon_e, larg, haut, couche, cache)

    def vers_src(u, v):
        la, lo = latlon(*cadre.jeu(u, v))
        return (lo - lon_o) / (lon_e - lon_o) * larg, (lat_n - la) / (lat_n - lat_s) * haut

    p00, p10, p01 = vers_src(0, 0), vers_src(1, 0), vers_src(0, 1)
    coef = (p10[0] - p00[0], p01[0] - p00[0], p00[0], p10[1] - p00[1], p01[1] - p00[1], p00[1])
    return src.transform((cadre.W, cadre.H), Image.AFFINE, coef, resample=Image.BICUBIC)


# --- donnees a superposer ----------------------------------------------------------------
def bdtopo():
    return json.loads(BDTOPO.read_text(encoding="utf-8"))


def polygones_osm():
    return {wid: SITE.poly(wid)[:-1] for wid, w in SITE.ways.items() if "building" in w.get("tags", {})}


def map_generee():
    """Elements de la map generee (unites de jeu) : immeubles, voisins, parkings, routes, arbres."""
    from quartier import Quartier
    q = Quartier()
    arbres = []
    for nom in ("peuplier", "sapin"):
        def faux(self, x, y, *a, _n=nom, **k):
            arbres.append((x, y, _n))
        setattr(q, nom, faux.__get__(q))

    def modele(nom, x, y, angle=0.0, echelle=1.0, dz=0.0):
        if "tree" in nom or "hedge" in nom:
            arbres.append((x, y, nom))
    q.modele = modele
    q.construire()
    imm = []
    for i in q.immeubles:
        pts = [i.monde(u, v, 0)[:2] for u, v in ((0, 0), (i.L, 0), (i.L, i.D), (0, i.D))]
        imm.append((i.nom, pts))
    voisins = []
    ignorer = {BAT1, BAT2, BAT3}
    for wid, w in SITE.ways.items():
        if "building" not in w.get("tags", {}) or wid in ignorer:
            continue
        poly = SITE.poly(wid)[:-1]
        if len(poly) < 3 or not all(q.X0 + 128 < x < q.X1 - 128 and q.Y0 + 128 < y < q.Y1 - 128 for x, y in poly):
            continue
        from geo import obb
        cx, cy, l, wd, a = obb(poly)
        if l < 120 or wd < 120:
            continue
        c, s = math.cos(a), math.sin(a)
        voisins.append([(cx + u * c - v * s, cy + u * s + v * c) for u, v in ((-l / 2, -wd / 2), (l / 2, -wd / 2), (l / 2, wd / 2), (-l / 2, wd / 2))])
    routes = []
    larg = {"secondary": 300, "tertiary": 280, "residential": 260, "service": 200}
    for wid, w in SITE.ways.items():
        hw = w.get("tags", {}).get("highway")
        if hw and hw not in ("steps",):
            routes.append((SITE.poly(wid), larg.get(hw, 80)))
    parkings = [q.PARKING_BAS, q.PARKING_HAUT, q.ALLEE_GARAGES]
    return {"immeubles": imm, "voisins": voisins, "routes": routes, "parkings": parkings, "arbres": arbres,
            "annexe": q.annexe_boite, "emprises": q.emprises, "terrain": (q.X0, q.Y0, q.X1, q.Y1)}


# --- MNH LiDAR HD ----------------------------------------------------------------------
def charger_mnh():
    meta = json.loads((REF / "mnh.json").read_text())
    a = np.fromfile(REF / "mnh.bil", dtype="<f4").reshape(meta["n"], meta["n"])
    return np.where(a < -100, 0, a), meta


def mnh_jeu(cadre):
    """MNH rendu dans le cadre de jeu (tableau H x W, metres)."""
    a, meta = charger_mnh()
    u, v = np.meshgrid(np.arange(cadre.W) + 0.5, np.arange(cadre.H) + 0.5)
    x, y = cadre.x0 + u.ravel() * cadre.u, cadre.y1 - v.ravel() * cadre.u
    # transformation affine exacte par 3 points puis application vectorielle
    def ll(xx, yy):
        la, lo = latlon(xx, yy)
        E, N = lambert93(la, lo)
        return E, N
    e0, n0 = ll(cadre.x0, cadre.y1)
    e1, n1 = ll(cadre.x0 + cadre.u, cadre.y1)
    e2, n2 = ll(cadre.x0, cadre.y1 - cadre.u)
    E = e0 + (u - 0.5) * (e1 - e0) + (v - 0.5) * (e2 - e0)
    N = n0 + (u - 0.5) * (n1 - n0) + (v - 0.5) * (n2 - n0)
    i = np.clip(((E - meta["E0"]) / meta["pas_m"]).astype(int), 0, meta["n"] - 1)
    j = np.clip(((meta["N1"] - N) / meta["pas_m"]).astype(int), 0, meta["n"] - 1)
    return a[j, i]


class GrilleMnh:
    """MNH LiDAR HD (0,5 m) avec conversion repere de jeu <-> pixel (affine, exacte a ~1 cm sur 250 m)."""

    def __init__(self):
        self.a, self.meta = charger_mnh()
        self.pas = self.meta["pas_m"]
        n = self.meta["n"]
        self.mns = np.fromfile(REF / "mns.bil", dtype="<f4").reshape(n, n)
        self.mnt = np.fromfile(REF / "mnt.bil", dtype="<f4").reshape(n, n)
        pts = [(0.0, 0.0), (1000.0, 0.0), (0.0, 1000.0)]
        (e0, n0), (e1, n1), (e2, n2) = (lambert93(*latlon(*p)) for p in pts)
        # (E, N) = origine + x * ex + y * ey   (par unite de jeu)
        self.o = (e0, n0)
        self.ex = ((e1 - e0) / 1000, (n1 - n0) / 1000)
        self.ey = ((e2 - e0) / 1000, (n2 - n0) / 1000)

    def pixel(self, x, y):
        E = self.o[0] + x * self.ex[0] + y * self.ey[0]
        N = self.o[1] + x * self.ex[1] + y * self.ey[1]
        return (E - self.meta["E0"]) / self.pas, (self.meta["N1"] - N) / self.pas

    def jeu(self, i, j):
        """Pixel (i, j) du MNH -> repere de jeu (inverse de pixel)."""
        E = self.meta["E0"] + i * self.pas
        N = self.meta["N1"] - j * self.pas
        det = self.ex[0] * self.ey[1] - self.ex[1] * self.ey[0]
        dE, dN = E - self.o[0], N - self.o[1]
        return (dE * self.ey[1] - dN * self.ey[0]) / det, (self.ex[0] * dN - self.ex[1] * dE) / det

    def masque(self, polys, marge_m=0.0):
        """Masque booleen des pixels dans les polygones (unites de jeu), dilates de marge_m."""
        n = self.meta["n"]
        im = Image.new("L", (n, n), 0)
        d = ImageDraw.Draw(im)
        for poly in polys:
            d.polygon([self.pixel(x, y) for x, y in poly], fill=255)
        m = np.array(im) > 0
        k = int(round(marge_m / self.pas))
        for _ in range(k):
            m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
        return m


def maxima_locaux(a, rayon):
    """Pixels qui sont le maximum de leur voisinage carre (2 rayon + 1)."""
    p = np.pad(a, rayon, mode="constant", constant_values=-1)
    mx = np.full(a.shape, -1.0, dtype=a.dtype)
    n0, n1 = a.shape
    for dj in range(2 * rayon + 1):
        for di in range(2 * rayon + 1):
            mx = np.maximum(mx, p[dj:dj + n0, di:di + n1])
    return a >= mx


def rayon_couronne(a, i, j, h, pas):
    """Rayon moyen (m) de la couronne : distance ou le MNH retombe sous 45 % de la hauteur du sommet."""
    n = a.shape[0]
    res = []
    for k in range(16):
        ang = 2 * math.pi * k / 16
        d = 0
        while d < 24:                                    # 12 m max
            ii, jj = int(round(i + math.cos(ang) * d)), int(round(j - math.sin(ang) * d))
            if not (0 <= ii < n and 0 <= jj < n) or a[jj, ii] < 0.45 * h:
                break
            d += 1
        res.append(d * pas)
    return max(0.4, float(np.median(res)))


def polygones_batis():
    polys = [b["emprise"] for b in bdtopo()["batiments"]]
    polys += list(polygones_osm().values())
    return polys


def arbres_lidar(g, seuil=2.5):
    """Arbres : sommets du MNH hors batiments. Un sommet est un arbre distinct s'il est separe de tout sommet plus haut
    et voisin (< 8 m) par un creux d'au moins 6 % de sa hauteur (et 0,7 m) ; sinon c'est une branche du plus grand."""
    a = g.a
    lis = sum(np.roll(np.roll(a, dj, 0), di, 1) for dj in (-1, 0, 1) for di in (-1, 0, 1)) / 9.0     # lissage 3x3
    bati = g.masque(polygones_batis(), marge_m=0.75)
    cand = maxima_locaux(lis, 3) & (lis >= seuil) & ~bati
    js, is_ = np.nonzero(cand)
    pics = sorted(((float(lis[j, i]), int(i), int(j)) for j, i in zip(js, is_)), reverse=True)
    gardes = []
    for h, i, j in pics:
        distinct = True
        for h2, i2, j2, _ in gardes:
            d = math.hypot(i - i2, j - j2) * g.pas
            if d > 8.0:
                continue
            n = max(2, int(d / 0.25))
            seg = [lis[int(round(j + (j2 - j) * k / n)), int(round(i + (i2 - i) * k / n))] for k in range(n + 1)]
            if h - min(seg) < max(0.7, 0.06 * h):
                distinct = False
                break
        if distinct:
            gardes.append((h, i, j, 0))
    arbres = []
    for h, i, j, _ in gardes:
        x, y = g.jeu(i + 0.5, j + 0.5)
        if not (-6500 < x < 7800 and -6500 < y < 7800):
            continue
        hb = float(a[max(j - 1, 0):j + 2, max(i - 1, 0):i + 2].max())       # sommet brut (le lissage rabote les fleches)
        r = rayon_couronne(lis, i, j, h, g.pas)
        arbres.append({"x": round(x), "y": round(y), "h_m": round(hb, 1), "rayon_m": round(r, 1), "elancement": round(hb / (2 * r), 1)})
    return arbres


def nom_couleur(rgb):
    """Libelle grossier d'une couleur de toit (ortho de plein jour, voile atmospherique : un ordre de grandeur)."""
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    h *= 360
    if v < 0.28:
        return "tres sombre"
    if s < 0.13:
        return "gris clair" if v > 0.55 else "gris sombre"
    if h < 25 or h > 340:
        return "brun-rouge (tuiles)" if s > 0.3 else "brun-gris"
    if h < 60:
        return "ocre / beige"
    return "gris-vert / mousse"


def toitures_lidar(g):
    """Forme des toits mesuree au LiDAR : hauteurs de faitage/egout, pentes, type, direction du faitage, couleur (ortho)."""
    zone = Cadre(-6500, -6500, 7800, 7800, 5)
    ortho = np.array(ortho_jeu(zone, nom="toits"))
    res = []
    for b in bdtopo()["batiments"]:
        if b["aire_m2"] < 20:
            continue
        emp = g.masque([b["emprise"]], marge_m=1.0)
        m = emp & (g.a > 1.5)
        if m.sum() < 25:
            continue
        anneau = g.masque([b["emprise"]], marge_m=2.5) & ~g.masque([b["emprise"]], marge_m=0.75)
        sol = float(np.median(g.mnt[anneau]))
        js, is_ = np.nonzero(m)
        xy = np.array([g.jeu(i + 0.5, j + 0.5) for j, i in zip(js, is_)]) / M       # metres, repere de jeu
        z = g.mns[js, is_] - sol
        z_f = float(np.percentile(z, 98))
        ox, oy, L, W, ang0 = b["obb"]
        ang0 = math.radians(ang0)
        # couleur : pixels du toit retrecis de 1 m (le relief decale les toits sur l'ortho)
        cols = []
        for (x, y) in xy[::7]:
            u_, v_ = (x * M - zone.x0) / zone.u, (zone.y1 - y * M) / zone.u
            if 0 <= u_ < zone.W and 0 <= v_ < zone.H:
                cols.append(ortho[int(v_), int(u_)])
        rgb = tuple(int(c) for c in np.median(np.array(cols), axis=0)) if cols else None
        # axe du faitage : acp des points hauts si elle est nette, sinon grande dimension de l'emprise
        haut0 = z >= z_f - 0.3 * max(z_f - float(np.percentile(z, 5)), 0.5)
        pts = xy[haut0]
        ang = ang0
        if haut0.sum() > 12:
            w_, vec = np.linalg.eigh(np.cov(pts.T))
            if w_[1] > 3.0 * max(w_[0], 1e-6):
                ang = math.atan2(vec[1, 1], vec[0, 1])
        ca, sa = math.cos(ang), math.sin(ang)
        u = xy[:, 0] * ca + xy[:, 1] * sa
        v = -xy[:, 0] * sa + xy[:, 1] * ca
        # profil transversal par tranches de 0,5 m (mediane)
        bins = np.floor((v - v.min()) / 0.5).astype(int)
        milieu = np.abs(u - (u.min() + u.max()) / 2) <= 0.3 * (u.max() - u.min())      # hors croupes et pignons
        prof = []
        for k in range(bins.max() + 1):
            sel = (bins == k) & milieu
            prof.append(float(np.median(z[sel])) if sel.sum() >= 4 else None)
        pleins = [k for k, h in enumerate(prof) if h is not None]
        if len(pleins) < 3:
            continue
        prof = [prof[k] for k in range(pleins[0], pleins[-1] + 1) if prof[k] is not None]
        zr = max(prof)
        kr = prof.index(zr)

        def egout(sens):
            """Depuis le faitage vers l'exterieur, jusqu'au bord du toit (chute de plus de 1,2 m entre deux tranches)."""
            k = kr
            while 0 <= k + sens < len(prof) and prof[k] - prof[k + sens] < 1.2:
                k += sens
            return k, prof[k]
        kg, ze_g = egout(-1)
        kd, ze_d = egout(1)
        rise = zr - min(ze_g, ze_d)
        if rise < 1.0:
            typ, pente_g, pente_d, long_f, ang_f = "plat", 0, 0, None, None
        else:
            run_g, run_d = max((kr - kg) * 0.5, 0.5), max((kd - kr) * 0.5, 0.5)
            pente_g = math.degrees(math.atan2(zr - ze_g, run_g))
            pente_d = math.degrees(math.atan2(zr - ze_d, run_d))
            # pignon ou croupe : le long du faitage, la hauteur retombe-t-elle a l'approche des bouts ?
            vr = v.min() + (kr + 0.5) * 0.5
            axe = np.abs(v - vr) < 0.75
            ub = np.floor((u[axe] - u[axe].min()) / 0.5).astype(int)
            ligne = [float(np.median(z[axe][ub == k])) for k in range(ub.max() + 1) if (ub == k).sum() >= 1]
            n = len(ligne)
            plateau = float(np.median(ligne[n // 4: n - n // 4])) if n >= 8 else zr
            bouts = []
            for sens in (0, 1):
                k = 3 if n > 8 else 0                                      # 1,5 m a l'interieur du bout
                zb = ligne[k] if sens == 0 else ligne[n - 1 - k]
                bouts.append(plateau - zb > 0.35 * rise)
            long_f = None
            typ = {(True, True): "4 pans (croupes)", (False, False): "deux pans (pignons)"}.get(tuple(bouts), "pignon + croupe")
            crete = u[z >= zr - 0.15 * rise]
            if typ == "4 pans (croupes)" and np.ptp(crete) < 0.3 * np.ptp(u):
                typ = "pyramide (4 pans)"
            ang_f = round(math.degrees(ang) % 180)
        res.append({"id": b["id"], "role": b.get("role"), "x": ox, "y": oy, "long_m": round(L / M, 1), "larg_m": round(W / M, 1),
                    "h_faitage_m": round(zr, 1), "h_egout_m": round(min(ze_g, ze_d), 1), "z_sol_m": round(sol, 1),
                    "pente_deg": [round(pente_g), round(pente_d)], "type": typ, "faitage_angle_jeu_deg": ang_f,
                    "couleur_rgb": rgb, "couleur": nom_couleur(rgb) if rgb else None, "etages_bdtopo": b.get("etages")})
    return res


def ecrire_lidar():
    g = GrilleMnh()
    arbres, toits = arbres_lidar(g), toitures_lidar(g)
    data = {"source": "IGN LiDAR HD (acquisition 13-14 juin 2021, mission 21LHD5PK1), MNH/MNS/MNT 0,5 m via WMS data.geopf.fr ; "
                      "traitement : tools/ign_vues.py",
            "repere": "unites de jeu ; arbres : h_m = sommet au-dessus du sol, rayon_m = rayon moyen de la couronne, "
                      "elancement = h / diametre (>2,2 : peuplier ou conifere) ; maxima locaux hors batiments (seuil 2,5 m)",
            "toitures": "h_faitage_m / h_egout_m = hauteur au-dessus du sol (MNT) ; pente = angle des pans ; type deduit de la forme des "
                        "points hauts ; faitage_angle_jeu_deg = direction du faitage dans le repere de jeu (0 = axe x, 90 = axe y)",
            "arbres": arbres, "toitures": toits}
    LIDAR_JSON.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{LIDAR_JSON} : {len(arbres)} arbres, {len(toits)} toitures, {LIDAR_JSON.stat().st_size // 1024} Ko")


# --- dessin -----------------------------------------------------------------------------------
def police(taille=14):
    for nom in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(nom, taille)
        except OSError:
            pass
    return ImageFont.load_default()


def tracer(draw, cadre, pts, couleur, ferme=True, epaisseur=2):
    p = [cadre.px(x, y) for x, y in pts]
    if ferme:
        p = p + p[:1]
    draw.line(p, fill=couleur, width=epaisseur)


def echelle_et_nord(img, cadre):
    d = ImageDraw.Draw(img)
    f = police(15)
    # barre d'echelle de 10 m
    L = 10 * cadre.ppm
    x0, y0 = 14, img.height - 18
    d.rectangle((x0 - 4, y0 - 20, x0 + L + 44, y0 + 10), fill=(0, 0, 0))
    d.line((x0, y0, x0 + L, y0), fill=(255, 255, 255), width=3)
    d.text((x0 + L + 5, y0 - 9), "10 m", fill=(255, 255, 255), font=f)
    # axes du repere de jeu
    d.text((x0, y0 - 18), "haut = +y (axe du bat. 1)  droite = +x", fill=(255, 255, 255), font=f)


def vue(nom, x0, y0, x1, y1, ppm, calques="", couche="ORTHOIMAGERY.ORTHOPHOTOS", gen=None, etiquettes=True):
    cadre = Cadre(x0, y0, x1, y1, ppm)
    if "m" in calques:
        h = mnh_jeu(cadre)
        v = np.clip(h / 20.0, 0, 1)
        rgb = np.stack([np.where(v > 0.02, 90 + 165 * v, 20), np.where(v > 0.02, 160 - 90 * v, 40), np.where(v > 0.02, 70 * (1 - v), 40)], -1)
        img = Image.fromarray(rgb.astype(np.uint8))
    else:
        img = ortho_jeu(cadre, couche, nom=nom)
    d = ImageDraw.Draw(img)
    f = police(13)
    if "o" in calques:
        for wid, poly in polygones_osm().items():
            tracer(d, cadre, poly, (0, 255, 255), True, 2)
    if "b" in calques:
        for b in bdtopo()["batiments"]:
            tracer(d, cadre, b["emprise"], (255, 235, 0), True, 2)
            if etiquettes and b.get("h_m") and x0 < b["obb"][0] < x1 and y0 < b["obb"][1] < y1:
                px, py = cadre.px(b["obb"][0], b["obb"][1])
                d.text((px - 14, py - 8), (f'{b["id"][-3:]} ' if "i" in calques else "") + f'{b["h_m"]:g}m', fill=(255, 235, 0), font=f)
    if "g" in calques:
        gen = gen or map_generee()
        for _, pts in gen["immeubles"]:
            tracer(d, cadre, pts, (255, 40, 40), True, 3)
        for pts in gen["voisins"]:
            tracer(d, cadre, pts, (255, 40, 40), True, 2)
        px0, py0, px1, py1, *_ = gen["annexe"]
        tracer(d, cadre, [(px0, py0), (px1, py0), (px1, py1), (px0, py1)], (255, 40, 40), True, 2)
        for (a, b, c, e) in gen["parkings"]:
            tracer(d, cadre, [(a, b), (c, b), (c, e), (a, e)], (255, 130, 0), True, 2)
        for pts, larg in gen["routes"]:
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                L = math.dist((ax, ay), (bx, by))
                if L < 1:
                    continue
                nx, ny = -(by - ay) / L * larg / 2, (bx - ax) / L * larg / 2
                tracer(d, cadre, [(ax - nx, ay - ny), (bx - nx, by - ny)], (255, 130, 0), False, 1)
                tracer(d, cadre, [(ax + nx, ay + ny), (bx + nx, by + ny)], (255, 130, 0), False, 1)
        for x, y, n in gen["arbres"]:
            px, py = cadre.px(x, y)
            r = 0.9 * cadre.ppm * (1.0 if "tree" in n or "hedge" in n else 1.6)
            d.ellipse((px - r, py - r, px + r, py + r), outline=(255, 0, 255), width=2)
    if "a" in calques and LIDAR_JSON.exists():
        for t in json.loads(LIDAR_JSON.read_text(encoding="utf-8"))["arbres"]:
            x, y, h, r = t["x"], t["y"], t["h_m"], t["rayon_m"]
            if x0 < x < x1 and y0 < y < y1:
                px, py = cadre.px(x, y)
                rr = max(r * cadre.ppm, 3)
                d.ellipse((px - rr, py - rr, px + rr, py + rr), outline=(60, 255, 60), width=2)
                if etiquettes and cadre.ppm >= 6:
                    d.text((px + rr, py - 7), f"{h:.0f}", fill=(60, 255, 60), font=f)
    if "q" in calques:                                   # grille tous les 500 unites (~10 m), etiquetee en unites de jeu
        pas = 500
        for gx in range(int(math.ceil(x0 / pas)) * pas, int(x1) + 1, pas):
            px, _ = cadre.px(gx, y0)
            d.line((px, 0, px, img.height), fill=(255, 255, 255), width=1)
            d.text((px + 2, 2), str(gx), fill=(255, 255, 255), font=f)
        for gy in range(int(math.ceil(y0 / pas)) * pas, int(y1) + 1, pas):
            _, py = cadre.px(x0, gy)
            d.line((0, py, img.width, py), fill=(255, 255, 255), width=1)
            d.text((2, py + 2), str(gy), fill=(255, 255, 255), font=f)
    legende = []
    if "o" in calques:
        legende.append(((0, 255, 255), "OSM (cadastre 2010-2011)"))
    if "b" in calques:
        legende.append(((255, 235, 0), "BD TOPO (hauteur en m)"))
    if "g" in calques:
        legende += [((255, 40, 40), "immeubles et maisons de la map"), ((255, 130, 0), "routes et parkings de la map"),
                    ((255, 0, 255), "arbres de la map")]
    if "a" in calques:
        legende.append(((60, 255, 60), "arbres LiDAR 2021 (hauteur en m)"))
    if legende:
        h_leg = 8 + 18 * len(legende)
        d.rectangle((6, 6, 290, 6 + h_leg), fill=(0, 0, 0))
        for k, (couleur, texte) in enumerate(legende):
            d.rectangle((14, 14 + 18 * k, 34, 22 + 18 * k), outline=couleur, width=3)
            d.text((42, 10 + 18 * k), texte, fill=(255, 255, 255), font=police(14))
    echelle_et_nord(img, cadre)
    VUES.mkdir(parents=True, exist_ok=True)
    sortie = VUES / f"{nom}.jpg"
    img.convert("RGB").save(sortie, quality=88)
    print(sortie, img.size)
    return sortie


# zones etudiees : nom -> (x0, y0, x1, y1, pixels par metre)
ZONES = {
    "10_bat1_est": (-400, -1900, 2600, 1900, 20),         # facade des halls, parking, annexe
    "11_bat1_ouest": (-2300, -1800, 500, 1800, 20),       # arriere, pelouse, peupliers
    "12_bat2": (-1100, 2500, 1700, 4100, 24),
    "13_bat3": (1400, 3500, 5000, 5000, 20),
    "14_nord": (-1800, 3800, 5800, 6600, 11),             # parking du haut, arbres, rue
    "20_maisons_est_nord": (3000, 600, 6200, 3700, 16),
    "21_maisons_est_sud": (3000, -2600, 6200, 700, 16),
    "22_ecole": (-1500, -6800, 3600, -900, 10),
    "23_borcier_ouest": (-4800, -2200, -1000, 2200, 14),
}


def toutes():
    gen = map_generee()
    X0, Y0, X1, Y1 = gen["terrain"]
    vue("01_quartier_ortho", X0, Y0, X1, Y1, 8)
    vue("02_quartier_calques", X0, Y0, X1, Y1, 8, "obg", gen=gen)
    vue("03_quartier_mnh", X0, Y0, X1, Y1, 8, "m")
    for nom, (x0, y0, x1, y1, ppm) in ZONES.items():
        vue(nom, x0, y0, x1, y1, ppm)
        vue(nom + "_calques", x0, y0, x1, y1, ppm, "obga", gen=gen)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "vues":
        toutes()
    elif cmd == "arbres":
        ecrire_lidar()
    elif cmd == "vue" and len(sys.argv) >= 8:
        vue(sys.argv[2], *(float(v) for v in sys.argv[3:8]), *(sys.argv[8:10]))
    else:
        print(__doc__)
