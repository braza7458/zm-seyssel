"""Voirie du quartier : rubans de chaussee, trottoirs, marquages, places de stationnement.

Les axes viennent de reference/ign/bdtopo_quartier.json (BD TOPO IGN) et, pour les chemins
et allees, d'OpenStreetMap. Chaque ruban est une suite de quadrilateres, chacun fait de deux
prismes triangulaires qui partagent leur arete : pas de fente aux virages.
"""

import json
import math

import monde
from geo import M, REF
from materiaux import MAT

# largeur de chaussee en unites de jeu (docs/conception-v0.3.md, C.3)
LARG_NOM = {
    "AV BORCIER": 368, "CHE DE LA FONTAINE": 320, "R DES PRES DOMBET": 270, "R DE CRETILLON": 220,
    "R DE LA PRAIRIE": 220, "R FRANCOIS DOCHE": 220,
}
TROTTOIR = {"AV BORCIER": 100, "CHE DE LA FONTAINE": 80, "R DES PRES DOMBET": 90}
PAS_ROUTE = 192
EPAIS = 24


def _bdtopo():
    return json.loads((REF / "ign" / "bdtopo_quartier.json").read_text(encoding="utf-8"))


def largeur(r):
    nom = r.get("nom") or ""
    if "2 chauss" in r["nature"]:
        return 150
    if nom in LARG_NOM and "Rond-point" not in r["nature"]:
        return LARG_NOM[nom]
    if "Rond-point" in r["nature"]:
        return 220
    return max(int((r.get("largeur_m") or 4) * M * 1.15), 160)


def reechantillonne(trace, pas):
    pts = [tuple(p) for p in trace]
    out = [pts[0]]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.dist((ax, ay), (bx, by))
        n = max(1, int(math.ceil(L / pas)))
        for k in range(1, n + 1):
            out.append((ax + (bx - ax) * k / n, ay + (by - ay) * k / n))
    return out


def bords(pts, demi):
    """Points gauche/droite avec normales moyennees aux angles."""
    res = []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == len(pts) - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            ax, ay = x - pts[i - 1][0], y - pts[i - 1][1]
            bx, by = pts[i + 1][0] - x, pts[i + 1][1] - y
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        res.append(((x + nx * demi, y + ny * demi), (x - nx * demi, y - ny * demi)))
    return res


def ruban(q, trace, larg, mat, haut=6, decal=0.0, groupe="voirie", pas=None):
    """Ruban de largeur larg le long de trace (decal = decalage lateral de l'axe).

    Chaque section a une seule cote (la plus haute du terrain a gauche, au centre et a droite) puis un
    lissage : la chaussee suit le terrain sans le laisser percer, et deux quadrilateres voisins se
    rejoignent toujours (pas de trou, pas de marche)."""
    from quartier import prisme_triangle
    pts = reechantillonne(trace, pas or PAS_ROUTE)
    if len(pts) < 2:
        return 0
    if decal:
        gauche = bords(pts, abs(decal))
        pts = [g[0] if decal > 0 else g[1] for g in gauche]
    b = bords(pts, larg / 2)
    hs = [max(q.z(*b[k][0]), q.z(*b[k][1]), q.z(*pts[k])) + haut for k in range(len(pts))]
    for _ in range(2):
        hs = [max(h, 0.5 * (hs[max(0, i - 1)] + hs[min(len(hs) - 1, i + 1)])) for i, h in enumerate(hs)]
    n = 0
    for i in range(len(pts) - 1):
        q3 = [(b[i][0][0], b[i][0][1], hs[i]), (b[i + 1][0][0], b[i + 1][0][1], hs[i + 1]),
              (b[i + 1][1][0], b[i + 1][1][1], hs[i + 1]), (b[i][1][0], b[i][1][1], hs[i])]
        zb = min(q.z(*b[i][0]), q.z(*b[i][1]), q.z(*b[i + 1][0]), q.z(*b[i + 1][1])) - EPAIS
        zb = min(zb, min(p[2] for p in q3) - 12)
        q.ajoute(groupe, prisme_triangle(q3[0], q3[1], q3[2], zb, mat))
        q.ajoute(groupe, prisme_triangle(q3[0], q3[2], q3[3], zb, mat))
        n += 2
    return n


HW_LARG = {"primary": 420, "secondary": 400, "tertiary": 320, "unclassified": 260, "residential": 270, "living_street": 200,
           "service": 200, "track": 160, "footway": 90, "path": 80, "cycleway": 100, "pedestrian": 120}
VEHICULE = {"primary", "secondary", "tertiary", "unclassified", "residential", "living_street", "service"}
NOMS = {"Avenue Borcier": 368, "Chemin de la Fontaine": 320, "Rue des Prés Dombet": 270, "Rue de Crétillon": 220,
        "Route de Genève": 400}
TROTTOIRS = {"primary", "secondary", "tertiary"}


def routes_osm(q):
    """Voies d'OpenStreetMap : [(type, nom, [(x, y)], acces)] en unites de jeu, sans escaliers ni chantiers."""
    d = json.loads((REF / "osm" / "corridor.json").read_text(encoding="utf-8"))
    out = []
    for e in d["elements"]:
        t = e.get("tags", {})
        hw = t.get("highway")
        if hw in HW_LARG and t.get("access") not in ("no",):
            out.append((hw, t.get("name") or "", [q.site.proj(n["lat"], n["lon"]) for n in e["geometry"]], t.get("access"), t.get("oneway")))
    return out


def troncons_jouables(pts, dans=None):
    """Morceaux de polyligne a l'interieur d'une zone (jouable par defaut), coupes exactement a sa limite."""
    if dans is None:
        def dans(p):
            return monde.jouable(p[0], p[1], 0)

    runs, run = [], []
    for a, b in zip(pts, pts[1:]):
        da, db = dans(a), dans(b)
        if da and not run:
            run = [a]
        if da and db:
            run.append(b)
        elif da and not db:
            lo, hi = 0.0, 1.0
            for _ in range(24):
                m = (lo + hi) / 2
                if dans((a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)):
                    lo = m
                else:
                    hi = m
            run.append((a[0] + (b[0] - a[0]) * lo, a[1] + (b[1] - a[1]) * lo))
            runs.append(run)
            run = []
        elif not da and db:
            lo, hi = 0.0, 1.0
            for _ in range(24):
                m = (lo + hi) / 2
                if dans((a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)):
                    hi = m
                else:
                    lo = m
            run = [(a[0] + (b[0] - a[0]) * hi, a[1] + (b[1] - a[1]) * hi), b]
    if len(run) >= 2:
        runs.append(run)
    return [r for r in runs if len(r) >= 2]


def _droit(a, b, c):
    """Vrai si a -> b -> c continue a peu pres tout droit (pas de demi-tour)."""
    u = (b[0] - a[0], b[1] - a[1])
    v = (c[0] - b[0], c[1] - b[1])
    n = (math.hypot(*u) * math.hypot(*v)) or 1.0
    return (u[0] * v[0] + u[1] * v[1]) / n > 0.2


def _chaines(ways):
    """Assemble bout a bout les voies a sens unique : [(points, [voies])]."""
    ways = list(ways)
    out = []
    while ways:
        w = ways.pop(0)
        chaine, used = list(w[2]), [w]
        etendu = True
        while etendu:
            etendu = False
            for v in ways:
                vp = v[2]
                if math.dist(vp[0], chaine[-1]) < 3 and _droit(chaine[-2], chaine[-1], vp[1]):
                    chaine += list(vp[1:])
                elif math.dist(vp[-1], chaine[0]) < 3 and _droit(vp[-2], chaine[0], chaine[1]):
                    chaine = list(vp[:-1]) + chaine
                else:
                    continue
                ways.remove(v)
                used.append(v)
                etendu = True
                break
        out.append((chaine, used))
    return out


def fusionne_chaussees(routes):
    """Les deux chaussees d'une route a sens uniques opposes deviennent une seule voie.

    Renvoie [(type, nom, points, acces, oneway, largeur ou None)] ; la largeur n'est donnee que pour les voies fusionnees."""
    par_nom = {}
    for r in routes:
        if r[0] in VEHICULE and r[1] and r[4] == "yes":
            par_nom.setdefault(r[1], []).append(r)
    pris, fusions = set(), []
    for nom, ws in par_nom.items():
        chaines = _chaines(ws)
        for i, (ca, ua) in enumerate(chaines):
            for j, (cb, ub) in enumerate(chaines):
                if j <= i or any(id(w) in pris for w in ua + ub):
                    continue
                da = (ca[-1][0] - ca[0][0], ca[-1][1] - ca[0][1])
                db = (cb[-1][0] - cb[0][0], cb[-1][1] - cb[0][1])
                if da[0] * db[0] + da[1] * db[1] >= 0:
                    continue          # meme sens : pas une paire de chaussees
                ref, autre = (ca, cb) if len(reechantillonne(ca, 100)) >= len(reechantillonne(cb, 100)) else (cb, ca)
                pts = reechantillonne(ref, 200)
                milieu, proches = [], 0
                for pt in pts:
                    d, qq = monde.dist_chemin(pt, autre)
                    if d < 1200:
                        milieu.append(((pt[0] + qq[0]) / 2, (pt[1] + qq[1]) / 2))
                        proches += 1
                    else:
                        milieu.append(pt)
                if proches < 0.5 * len(pts):
                    continue
                for w in ua + ub:
                    pris.add(id(w))
                fusions.append((ua[0][0], nom, milieu, ua[0][3], "yes", 430))
    rest = [r + (None,) for r in routes if id(r) not in pris]
    return rest + fusions


def visible(p):
    return monde.ancre(p)[0] <= monde.R0 - 400


def _le_long(pts, voies, marge):
    """Vrai si tout le trace longe une voie vehicule (trottoir dessine a part dans OSM)."""
    for p in reechantillonne(pts, 150):
        if all(monde.dist_chemin(p, v)[0] > marge for v in voies):
            return False
    return True


def octogone(x, y, r, z, zb, mat):
    planes = [((0, 0, 1), (x, y, z), mat), ((0, 0, -1), (x, y, zb), mat)]
    for k in range(8):
        t = 2 * math.pi * (k + 0.5) / 8
        c = r * math.cos(math.pi / 8)
        planes.append(((math.cos(t), math.sin(t), 0), (x + c * math.cos(t), y + c * math.sin(t), 0), mat))
    return planes


def construire(q):
    """Un seul reseau : les voies OpenStreetMap, continues, sans doublon, jusqu'a l'horizon pour les routes.

    Les sentiers et trottoirs separes ne sont gardes que dans la zone jouable et s'ils ne longent pas une route.
    Chaque carrefour recoit une dalle octogonale qui bouche les angles entre les rubans."""
    voies = fusionne_chaussees(q.osm_routes)
    axes_vehicules = [pts for hw, nom, pts, acces, ow, fus in voies if hw in VEHICULE]
    noeuds = {}
    for hw, nom, pts, acces, oneway, fus in voies:
        larg = fus or NOMS.get(nom, HW_LARG[hw])
        vehicule = hw in VEHICULE
        if vehicule:
            if hw == "service" and acces == "private":
                runs = troncons_jouables(pts)
            else:
                runs = troncons_jouables(pts, visible)
            mat = MAT["asphalte"]
        else:
            if _le_long(pts, axes_vehicules, larg / 2 + 260):
                continue
            runs = troncons_jouables(pts)
            mat = MAT["gravier"] if hw in ("path", "track") else MAT["trottoir"]
        for run in runs:
            jou = sum(1 for p in run if monde.jouable(*p)) >= len(run) / 2
            ruban(q, run, larg, mat, 6 if vehicule else 8, pas=192 if jou else 320)
            if vehicule and hw in TROTTOIRS and jou:
                for c in (1, -1):
                    ruban(q, run, 90, MAT["trottoir"], 12, decal=c * (larg / 2 + 45), groupe="trottoirs")
        if vehicule:
            for i, pt in enumerate(pts):
                k = (round(pt[0]), round(pt[1]))
                noeuds.setdefault(k, []).append(larg)
    # dalles de carrefour
    from quartier import pave  # noqa: F401
    for (x, y), largs in noeuds.items():
        if len(largs) < 2 or not visible((x, y)):
            continue
        r = max(largs) / 2 + 12
        zs = [q.z(x + r * math.cos(t), y + r * math.sin(t)) for t in (0, 1.57, 3.14, 4.71)] + [q.z(x, y)]
        z = 0.5 * (max(zs) + q.z(x, y)) + 6
        q.ajoute("voirie", octogone(x, y, r, z, min(zs) - 24, MAT["asphalte"]))
    marquages(q)


def marquages(q):
    """Passages pietons et places de stationnement (peinture blanche en briques de 1,5 u)."""
    from quartier import pave
    mat = MAT["marquage"]

    def bande(x0, y0, x1, y1):
        z = max(q.z(x0, y0), q.z(x1, y1)) + 6.5
        q.ajoute("marquages", pave(min(x0, x1), min(y0, y1), z - 4, max(x0, x1), max(y0, y1), z, mat))


    for (px, py) in ((-2250, -2000), (2400, 1300), (-1500, 3000)):
        d, qx, qy = _route_proche(q, px, py)
        if d < 400:
            passage_oriente(q, qx, qy)

    def places(x, y, dx, dy, n, pas, prof, ang=90):
        """Rangee de n places : lignes de 4 u de large separees de pas, profondeur prof."""
        ux, uy = dx, dy
        px, py = -dy, dx     # direction de la profondeur
        if prof < 0:
            px, py, prof = -px, -py, -prof
        for i in range(n):
            cx = x + ux * pas * (i + 0.5) + px * prof / 2
            cy = y + uy * pas * (i + 0.5) + py * prof / 2
            q.slots.append((cx, cy, math.degrees(math.atan2(py, px)) % 360))
        for i in range(n + 1):
            x0, y0 = x + ux * pas * i, y + uy * pas * i
            x1, y1 = x0 + px * prof, y0 + py * prof
            if not q.libre(x0, y0, 8) or q.interdit(x0, y0) or q.interdit(x1, y1):
                continue
            lo, hi = sorted((x0, x1)), sorted((y0, y1))
            if abs(px) > abs(py):
                bande(lo[0], y0 - 2, lo[1], y0 + 2)
            else:
                bande(x0 - 2, hi[0], x0 + 2, hi[1])

    places(2080, -1420, 1, 0, 8, 123, 246)
    places(2150, -900, 0, 1, 5, 123, -246)
    places(2150, -400, 0, 1, 4, 123, -246)
    places(0, 3900, 1, 0, 12, 123, 246)
    places(0, 4600, 1, 0, 12, 123, -246)


# --- barrages aux sorties du cadre jouable ------------------------------------------

INSET = 260
VOITURES = ["veh_t7_civ_car_compact_grey", "veh_t7_civ_car_compact_blue", "veh_t7_civ_car_compact_black",
            "veh_t7_civ_car_compact_green"]


def _sortie(q, a, b):
    """Point ou le segment a -> b sort du rectangle jouable reduit, ou None."""
    def dedans(p):
        return monde.jouable(p[0], p[1], INSET)
    if not dedans(a) or dedans(b):
        return None
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        p = (a[0] + (b[0] - a[0]) * mid, a[1] + (b[1] - a[1]) * mid)
        if dedans(p):
            lo = mid
        else:
            hi = mid
    return (a[0] + (b[0] - a[0]) * lo, a[1] + (b[1] - a[1]) * lo)


def boite_orientee(q, groupe, cx, cy, l, w, h, ang, mat, dz=0.0):
    """Pave l x w x h centre en (cx, cy), tourne de ang degres, pose sur le terrain."""
    from quartier import tourne
    z = q.z(cx, cy) + dz
    q.ajoute(groupe, tourne(__import__("immeuble").bloc(-l / 2, -w / 2, 0, l / 2, w / 2, h, mat), math.radians(ang), cx, cy, z))


def barrage(q, x, y, tx, ty, larg, n):
    """Barrage en travers d'une voie : voitures en biais, blocs de beton, sacs de sable, rouleau de barbeles."""
    ang = math.degrees(math.atan2(ty, tx))
    nx, ny = -ty, tx
    n_voit = 2 if larg < 300 else 3
    for k in range(n_voit):
        off = -larg / 2 + (k + 0.5) * larg / n_voit
        yaw = ang + 90 + ((k * 37 + n * 11) % 40 - 20)
        q.modele(VOITURES[(k + n) % 4], x + nx * off, y + ny * off, yaw % 360, 1.25)
    # blocs de beton et sacs de sable derriere les voitures (du cote du quartier)
    for k, off in enumerate((-larg * 0.35, 0, larg * 0.35)):
        q.modele("p7_barricade_concrete_modular_01", x - tx * 130 + nx * off, y - ty * 130 + ny * off, (ang + 90) % 360, 1.25)
    for k in range(3):
        off = -larg / 2 + (k + 0.5) * larg / 3
        q.modele("p7_sandbag_stack_44_middle", x - tx * 190 + nx * off, y - ty * 190 + ny * off, (ang + 90) % 360, 1.25)
    # rangee de barbeles : piquets et deux fils, en travers de toute la voie
    long_ = larg + 160
    nb = int(long_ // 90)
    for k in range(nb + 1):
        off = -long_ / 2 + k * long_ / nb
        px, py = x + tx * 230 + nx * off, y + ty * 230 + ny * off
        boite_orientee(q, "barrages", px, py, 6, 6, 74, ang, MAT["metal"])
    for dz in (28, 52):
        boite_orientee(q, "barrages", x + tx * 230, y + ty * 230, 2, long_, 2.5, ang, MAT["garde_corps"], dz)


def barrages(q):
    """Un barrage a chaque route qui sort de la zone jouable (cadre ou couloir)."""
    vus = []
    n = 0
    voies = [(pts, NOMS.get(nom, HW_LARG[hw])) for hw, nom, pts, acces, oneway in q.osm_routes if hw in VEHICULE]
    for trace, larg in voies:
        pts = [tuple(p) for p in trace]
        for a, b in zip(pts, pts[1:]):
            for (p, q_) in ((a, b), (b, a)):
                s = _sortie(q, p, q_)
                if not s:
                    continue
                if any(math.hypot(s[0] - v[0], s[1] - v[1]) < 450 for v in vus):
                    continue
                vus.append(s)
                L = math.hypot(q_[0] - p[0], q_[1] - p[1]) or 1
                barrage(q, s[0], s[1], (q_[0] - p[0]) / L, (q_[1] - p[1]) / L, larg, n)
                n += 1
    q.nb_barrages = n


def _route_proche(q, x, y):
    """(distance, x, y) du point de route vehicule le plus proche."""
    best = (1e18, x, y)
    for hw, nom, pts, acces, oneway in q.osm_routes:
        if hw not in VEHICULE:
            continue
        for a, b in zip(pts, pts[1:]):
            d, p = monde._seg((x, y), a, b)
            if d < best[0]:
                best = (d, p[0], p[1])
    return best


def passage_oriente(q, x, y):
    """Passage pieton : bandes paralleles a la voie, en travers de la chaussee."""
    from quartier import tourne
    d0 = 1e18
    best = None
    for hw, nom, pts, acces, oneway in q.osm_routes:
        if hw not in VEHICULE:
            continue
        for a, b in zip(pts, pts[1:]):
            d, p = monde._seg((x, y), a, b)
            if d < d0:
                d0, best = d, (a, b, hw, nom)
    a, b, hw, nom = best
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    larg = NOMS.get(nom, HW_LARG[hw])
    for k in range(-3, 4):
        boite_orientee(q, "marquages", x + math.cos(math.radians(ang)) * k * 80, y + math.sin(math.radians(ang)) * k * 80,
                       40, larg - 40, 4, ang, MAT["marquage"], dz=6.5)
