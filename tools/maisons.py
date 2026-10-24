"""Maisons voisines, ecole et petits batiments, pilotes par les donnees IGN.

Pour chaque batiment de reference/ign/bdtopo_quartier.json qui n'est pas un des trois immeubles,
l'annexe ou les garages : emprise (rectangle oriente), hauteur a l'egout, forme et pente du toit
(reference/ign/lidar_quartier.json), puis murs, toit, fenetres, porte, volets, cheminee.
"""

import json
import math

import monde
from geo import M, REF
from geom import toit_croupe, toit_pignon, toit_plat
from immeuble import bloc
from materiaux import MAT

HM = 49.2      # unites par metre en hauteur
COEUR = (2000, 500)
PROCHE = 4500
HAUT_ETAGE = 3.0


def _donnees():
    bd = json.loads((REF / "ign" / "bdtopo_quartier.json").read_text(encoding="utf-8"))
    li = json.loads((REF / "ign" / "lidar_quartier.json").read_text(encoding="utf-8"))
    toits = {t["id"]: t for t in li["toitures"]}
    routes = [r["trace"] for r in bd["routes"]]
    return bd, toits, routes


def _dist_route(routes, x, y):
    best = (1e9, 0, 0)
    for tr in routes:
        for (ax, ay), (bx, by) in zip(tr, tr[1:]):
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy or 1
            t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L2))
            px, py = ax + t * dx, ay + t * dy
            d = math.hypot(x - px, y - py)
            if d < best[0]:
                best = (d, px, py)
    return best


def _plan(q, b, toits, routes):
    """Parametres d'une maison, ou None si elle est a ignorer."""
    if b.get("role"):
        return None
    cx, cy, l, w, ang = b["obb"]
    if monde.ancre((cx, cy))[0] > monde.R0:
        return None
    if l < 150 or w < 120:
        return None
    t = toits.get(b["id"], {})
    if not t and "h_egout_m" not in t:
        # batiment du couloir : pas de LiDAR, forme deduite de la taille et de l'usage
        aire = l * w / M / M
        commerce = any(k in (b.get("usage") or "") for k in ("Commercial", "Industriel", "Agricole", "Sportif"))
        t = {"type": "plat" if (aire > 450 or commerce) else "deux pans (pignons)",
             "h_egout_m": min(max(b.get("h_m") or (3.2 if aire < 60 else 5.0), 2.4), 14),
             "pente_deg": [27, 27], "couleur": None}
    h_eg = (t.get("h_egout_m") or b.get("h_m") or 4.5)
    h_eg = max(2.4, min(h_eg, 12.0))
    pente_l = t.get("pente_deg")
    pente = sum(pente_l) / len(pente_l) if pente_l else 27
    pente = max(18, min(pente, 34))
    forme = t.get("type", "deux pans (pignons)")
    fa = t.get("faitage_angle_jeu_deg")
    if fa is not None and 45 < ((fa - ang) % 180) < 135:
        l, w, ang = w, l, ang + 90
    return {"id": b["id"], "n": int(b["id"]), "cx": cx, "cy": cy, "l": l, "w": w, "ang": ang,
            "h": h_eg, "pente": pente, "forme": forme, "couleur": t.get("couleur"),
            "usage": b.get("usage", ""), "aire": l * w / M / M,
            "proche": monde.jouable(cx, cy)}


def _aire_poly(pts):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2


def _rectangles(emprise, cx, cy, l, w, ang, pas=49):
    """Decoupe une emprise en rectangles alignes sur l'orientation de la maison : [(u0, v0, u1, v1)]."""
    from quartier import dans_poly
    a = -math.radians(ang)
    c, s_ = math.cos(a), math.sin(a)
    loc = [((x - cx) * c - (y - cy) * s_, (x - cx) * s_ + (y - cy) * c) for x, y in emprise]
    nu, nv = int(l // pas) + 2, int(w // pas) + 2
    u0, v0 = -nu * pas / 2, -nv * pas / 2
    g = [[dans_poly(u0 + (i + .5) * pas, v0 + (j + .5) * pas, loc) for j in range(nv)] for i in range(nu)]
    res = []
    while True:
        best = None
        # recherche exhaustive simple : agrandit depuis chaque case pleine
        for i in range(nu):
            for j in range(nv):
                if not g[i][j]:
                    continue
                wi = 0
                while i + wi < nu and g[i + wi][j]:
                    wi += 1
                hj = 0
                ok = True
                while j + hj < nv and ok:
                    ok = all(g[i + t][j + hj] for t in range(wi))
                    if ok:
                        hj += 1
                for ww in range(1, wi + 1):
                    hh = 0
                    while j + hh < nv and all(g[i + t][j + hh] for t in range(ww)):
                        hh += 1
                    if ww * hh > (best[0] if best else 0):
                        best = (ww * hh, i, j, ww, hh)
        if not best or best[0] < 12:
            break
        _, i, j, ww, hh = best
        for t in range(ww):
            for r in range(hh):
                g[i + t][j + r] = False
        res.append((u0 + i * pas, v0 + j * pas, u0 + (i + ww) * pas, v0 + (j + hh) * pas))
    return res, a


def _sur_route(q, p):
    """Vrai si une voie vehicule traverse l'emprise de la maison (le plan BD TOPO est a quelques metres pres)."""
    import voirie
    demi = min(p["l"], p["w"]) * 0.3
    for hw, nom, pts, acces, oneway in q.osm_routes:
        if hw not in voirie.VEHICULE:
            continue
        larg = voirie.NOMS.get(nom, voirie.HW_LARG[hw]) / 2
        for a, b in zip(pts, pts[1:]):
            if max(a[0], b[0]) < p["cx"] - p["l"] or min(a[0], b[0]) > p["cx"] + p["l"]:
                continue
            if max(a[1], b[1]) < p["cy"] - p["l"] or min(a[1], b[1]) > p["cy"] + p["l"]:
                continue
            d, _ = monde._seg((p["cx"], p["cy"]), a, b)
            if d < larg * 0.8 + demi:
                return True
    return False


def preparer(q):
    """Declare les emprises et aplanit le terrain avant le calcul des hauteurs."""
    bd, toits, routes = _donnees()
    routes = list(q.routes_axes)
    couloir = json.loads((REF / "ign" / "bdtopo_couloir.json").read_text(encoding="utf-8"))
    deja = {b["id"] for b in bd["batiments"]}
    tous = bd["batiments"] + [b for b in couloir if b["id"] not in deja]
    q.maisons = []
    for b in tous:
        p = _plan(q, b, toits, routes)
        if not p:
            continue
        # emprise non rectangulaire : un volume par rectangle (ecole, maisons en L)
        cx0, cy0, l0, w0, ang0 = b["obb"]
        if p["aire"] > 80 and _aire_poly([tuple(e) for e in b["emprise"]]) < 0.8 * l0 * w0:
            rects, _ = _rectangles(b["emprise"], cx0, cy0, l0, w0, ang0)
            zref0 = round(q.relief.h0(cx0, cy0) / 8) * 8
            ar = math.radians(ang0)
            for k, (u0, v0, u1, v1) in enumerate(rects):
                cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
                sub = dict(p)
                sub["cx"] = cx0 + cu * math.cos(ar) - cv * math.sin(ar)
                sub["cy"] = cy0 + cu * math.sin(ar) + cv * math.cos(ar)
                sub["l"], sub["w"], sub["ang"] = u1 - u0, v1 - v0, ang0
                if sub["w"] > sub["l"]:
                    sub["l"], sub["w"], sub["ang"] = sub["w"], sub["l"], ang0 + 90
                sub["n"] = p["n"] + k
                sub["aire"] = sub["l"] * sub["w"] / M / M
                sub["zref"] = zref0
                sub["routes"] = routes
                a2 = math.radians(sub["ang"])
                ex = abs(sub["l"] * math.cos(a2)) / 2 + abs(sub["w"] * math.sin(a2)) / 2
                ey = abs(sub["l"] * math.sin(a2)) / 2 + abs(sub["w"] * math.cos(a2)) / 2
                rect = (sub["cx"] - ex, sub["cy"] - ey, sub["cx"] + ex, sub["cy"] + ey)
                if any(rect[0] < e[2] and rect[2] > e[0] and rect[1] < e[3] and rect[3] > e[1] for e in q.emprises[:q.nb_fixes]):  # immeubles, annexe, garages
                    continue
                if _sur_route(q, sub):
                    continue
                q.emprises.append(rect + (zref0,))
                q.aplanir.append(rect + (zref0,))
                q.maisons.append(sub)
            groupe = [m for m in q.maisons if m['id'] == p['id']]
            if groupe:
                max(groupe, key=lambda m: m['l'] * m['w'])['principal'] = True
            continue
        a = math.radians(p["ang"])
        ex = abs(p["l"] * math.cos(a)) / 2 + abs(p["w"] * math.sin(a)) / 2
        ey = abs(p["l"] * math.sin(a)) / 2 + abs(p["w"] * math.cos(a)) / 2
        rect = (p["cx"] - ex, p["cy"] - ey, p["cx"] + ex, p["cy"] + ey)
        # pose sur un immeuble, l'annexe ou les garages : on ne double pas (les maisons voisines, elles,
        # peuvent avoir des rectangles englobants qui se touchent)
        if any(rect[0] < e[2] and rect[2] > e[0] and rect[1] < e[3] and rect[3] > e[1] for e in q.emprises[:q.nb_fixes]):
            continue
        if _sur_route(q, p):
            continue
        p["zref"] = round(q.relief.h0(p["cx"], p["cy"]) / 8) * 8
        q.emprises.append(rect + (p["zref"],))
        q.aplanir.append(rect + (p["zref"],))
        p["routes"] = routes
        p["principal"] = True
        q.maisons.append(p)


def _choix(n, options):
    return options[n % len(options)]


def construire(q):
    """Construit toutes les maisons preparees."""
    from quartier import tourne
    for p in q.maisons:
        for brush in _maison(q, p):
            q.ajoute("maisons", tourne(brush, math.radians(p["ang"]), p["cx"], p["cy"], p["zref"]))
    q.nb_maisons = len(q.maisons)


def _maison(q, p):
    n, l, w = p["n"], p["l"], p["w"]
    h = int(p["h"] * HM)
    grand = p["aire"] > 350 or "nseignement" in p["usage"]
    mur = MAT["ecole"] if grand else _choix(n // 7, [MAT["voisin"], MAT["voisin_clair"], MAT["voisin_blanc"]])
    plat = p["forme"] == "plat"
    c = p["couleur"] or ""
    if "brun" in c or "rouge" in c or "tuiles" in c:
        toit = MAT["voisin_toit"]
    elif c:
        toit = MAT["voisin_toit_gris"]
    else:
        toit = _choix(n // 3, [MAT["voisin_toit_gris"], MAT["voisin_toit"], MAT["voisin_toit_gris"]])
    zmin = min(q.z(p["cx"] + dx * l / 2, p["cy"] + dy * w / 2) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    zfond = min(zmin - p["zref"], 0) - 48
    out = [bloc(-l / 2, -w / 2, zfond, l / 2, w / 2, h, mur)]

    # toit
    haut_toit = h
    if plat:
        out.append(toit_plat(-l / 2 - 8, -w / 2 - 8, l / 2 + 8, w / 2 + 8, h + 14, MAT["toit_plat"], MAT["gravier_clair"]))
        for (a0, b0, a1, b1) in ((-l / 2 - 8, -w / 2 - 8, l / 2 + 8, -w / 2), (-l / 2 - 8, w / 2, l / 2 + 8, w / 2 + 8),
                                 (-l / 2 - 8, -w / 2, -l / 2, w / 2), (l / 2, -w / 2, l / 2 + 8, w / 2)):
            out.append(bloc(a0, b0, h + 8, a1, b1, h + 30, mur))
    else:
        if "pyramide" in p["forme"] or "croupes" in p["forme"] or "croupe" in p["forme"]:
            planes, zf = toit_croupe(-l / 2 - 20, -w / 2 - 24, l / 2 + 20, w / 2 + 24, h, p["pente"], toit, MAT["rive"], 14)
        else:
            planes, zf = toit_pignon(-l / 2 - 20, -w / 2 - 24, l / 2 + 20, w / 2 + 24, h, p["pente"], toit, MAT["rive"], mur, 14)
        out.append(planes)
        haut_toit = zf
        # souche de cheminee sur le faitage
        uc = -l * 0.2
        out.append(bloc(uc - 14, -14, zf - 40, uc + 14, 14, zf + 40, MAT["cheminee"]))
        out.append(bloc(uc - 18, -18, zf + 40, uc + 18, 18, zf + 46, MAT["appui"]))

    # ouvertures : fenetres collees et porte, par facade
    nb_niv = 1 if p["h"] < 4.6 else (2 if p["h"] < 7.4 else 3)
    ht = h / nb_niv
    d, px, py = _dist_route(p["routes"], p["cx"], p["cy"])
    a = math.radians(p["ang"])
    # cote de la porte : la grande facade tournee vers la route
    vx, vy = -math.sin(a), math.cos(a)           # direction locale +v dans le monde
    cote_porte = 1 if ((px - p["cx"]) * vx + (py - p["cy"]) * vy) >= 0 else -1
    for sens in (-1, 1):
        for axe in ("u", "v"):
            if axe == "u":
                Ls, face = w, sens * l / 2
            else:
                Ls, face = l, sens * w / 2
            if Ls < 200 or (grand and axe == "u"):
                continue
            nfen = max(1, int((Ls - 100) // (150 if not grand else 175)))
            for niv in range(nb_niv):
                z0 = niv * ht + 40
                for i in range(nfen):
                    c0 = -Ls / 2 + (i + 0.5) * Ls / nfen
                    porte = (axe == "v" and sens == cote_porte and niv == 0 and abs(c0) <= Ls / nfen * 0.6 and not grand)
                    if porte:
                        a0, a1 = c0 - 22, c0 + 22
                        _coller(out, axe, sens, face, a0, a1, 0, 106, MAT["porte"], (44, 106))
                        out.append(_plan_cube(axe, sens, face, a0 - 26, a1 + 26, 0, 8, MAT["dalle_claire"], 24))
                        continue
                    a0, a1 = c0 - 27, c0 + 27
                    fh = 62 if not grand else 64
                    _coller(out, axe, sens, face, a0, a1, z0, z0 + fh, MAT["fenetre"], (a1 - a0, fh))
                    if not grand:
                        _coller(out, axe, sens, face, a0 - 4, a1 + 4, z0 - 5, z0, MAT["appui"], None)
                        if p["proche"] and (n + niv + i) % 10 < 7:
                            vol = _choix(n + i, [MAT["volet"], MAT["volet_brun"], MAT["volet_vert"], MAT["volet_brun"]])
                            _coller(out, axe, sens, face, a0 - 22, a0 - 1, z0, z0 + fh, vol, None, 3)
                            _coller(out, axe, sens, face, a1 + 1, a1 + 22, z0, z0 + fh, vol, None, 3)
    # porte de garage des annexes
    if "Annexe" in p["usage"] and not grand:
        _coller(out, "v", cote_porte, cote_porte * w / 2, -59, 59, 0, 100, MAT["garage"], (118, 100))
    return out


def _coller(out, axe, sens, face, a0, a1, z0, z1, mat, proj, ep=2):
    """Ajoute un pave de decor colle sur une facade ; (axe, sens) designe la facade."""
    out.append(_plan_cube(axe, sens, face, a0, a1, z0, z1, mat, ep, proj))


def _plan_cube(axe, sens, face, a0, a1, z0, z1, mat, ep=2, proj=None):
    if axe == "v":
        v0, v1 = (face, face + ep) if sens > 0 else (face - ep, face)
        return bloc(a0, v0, z0, a1, v1, z1, mat, proj=proj)
    u0, u1 = (face, face + ep) if sens > 0 else (face - ep, face)
    return bloc(u0, a0, z0, u1, a1, z1, mat, proj=proj)
