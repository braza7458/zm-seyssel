"""Donnees ouvertes IGN (Geoplateforme, sans cle) pour le quartier des Pres Dombet.

    wfs   : telecharge les couches BD TOPO (WFS data.geopf.fr) dans _build/ref/wfs/
    json  : convertit en unites de jeu -> reference/ign/bdtopo_quartier.json
    mnh   : telecharge le LiDAR HD (MNH hauteur du sursol, MNS dessus, MNT sol ; 0,5 m) -> _build/ref/*.bil
    ortho : telecharge l'orthophoto (WMS) d'un cadre donne en lat/lon

Usage :
    python tools/ign_donnees.py wfs
    python tools/ign_donnees.py json
    python tools/ign_donnees.py mnh
    python tools/ign_donnees.py ortho sortie.jpg lat lon largeur_m hauteur_m cm_par_pixel [couche]

Remarques sur les services (verifiees le 2026-10-24) :
    - WFS : CQL_FILTER=BBOX(geometrie, lat_min, lon_min, lat_max, lon_max) (ordre lat,lon) ou BBOX=lon_min,lat_min,
      lon_max,lat_max,EPSG:4326 (ordre lon,lat) fonctionnent ; BBOX=lat,lon,... renvoie une collection vide.
      La sortie GeoJSON est en lon,lat. Le serveur renvoie les accents doublement encodes (corriges ici).
    - WMS-R : en WMS 1.3.0 + EPSG:4326 l'ordre de BBOX est lat,lon. Les orthophotos recentes ont une
      resolution native d'environ 20 cm : au dela, l'image est simplement interpolee.
    - Python stdlib uniquement (comme le generateur) ; les vues et analyses d'image sont dans ign_vues.py.
"""

import json
import math
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from geo import M, ROOT, Site, obb

REF = ROOT / "_build" / "ref"
WFS_DIR = REF / "wfs"
SORTIE = ROOT / "reference" / "ign" / "bdtopo_quartier.json"

WFS_URL = "https://data.geopf.fr/wfs/ows"
WMS_URL = "https://data.geopf.fr/wms-r/wms"

# Cadre de telechargement (sud, ouest, nord, est) : un peu plus large que la zone jouable
CADRE = (45.9545, 5.8340, 45.9590, 5.8410)
# Cadre d'export en unites de jeu (zone jouable +/- 2500 unites, soit ~50 m)
EXPORT = (-7100, -7100, 8400, 8400)

COUCHES = ["batiment", "troncon_de_route", "zone_de_vegetation", "equipement_de_transport",
           "construction_surfacique", "construction_lineaire", "construction_ponctuelle", "haie",
           "terrain_de_sport", "zone_d_activite_ou_d_interet", "erp", "surface_hydrographique",
           "troncon_hydrographique", "cimetiere", "zone_d_habitation", "point_de_repere"]

# Batiments de reference : id OSM -> role (geo.py)
ROLES_OSM = {131537388: "bat1", 131537277: "bat2", 131537354: "bat3", 131540438: "annexe", 131539162: "garages"}


# --- Lambert 93 (utile pour le LiDAR HD, servi en EPSG:2154) -------------------------
def lambert93(lat, lon):
    """WGS84 (lat, lon en degres) -> RGF93 / Lambert-93 (E, N en metres)."""
    a, f = 6378137.0, 1 / 298.257222101
    e = math.sqrt(2 * f - f * f)
    phi, lam = math.radians(lat), math.radians(lon)
    phi0, lam0, phi1, phi2 = (math.radians(v) for v in (46.5, 3.0, 44.0, 49.0))

    def m(p):
        return math.cos(p) / math.sqrt(1 - e * e * math.sin(p) ** 2)

    def t(p):
        return math.tan(math.pi / 4 - p / 2) / ((1 - e * math.sin(p)) / (1 + e * math.sin(p))) ** (e / 2)

    n = (math.log(m(phi1)) - math.log(m(phi2))) / (math.log(t(phi1)) - math.log(t(phi2)))
    F = m(phi1) / (n * t(phi1) ** n)
    r, r0 = a * F * t(phi) ** n, a * F * t(phi0) ** n
    th = n * (lam - lam0)
    return 700000 + r * math.sin(th), 6600000 + r0 - r * math.cos(th)


# --- telechargements -------------------------------------------------------------------
def telecharger(url, sortie):
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        sortie.write_bytes(r.read())
    return sortie


def wfs():
    s, o, n, e = CADRE
    for couche in COUCHES:
        q = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": f"BDTOPO_V3:{couche}",
             "OUTPUTFORMAT": "application/json", "COUNT": "2000",
             "CQL_FILTER": f"BBOX(geometrie,{s},{o},{n},{e})"}
        url = WFS_URL + "?" + urllib.parse.urlencode(q, safe="(),:")
        p = telecharger(url, WFS_DIR / f"{couche}.json")
        nb = len(json.loads(p.read_text(encoding="utf-8"))["features"])
        print(f"{couche:32s} {nb:4d} objets  {p.stat().st_size // 1024} Ko")


LIDAR = {"mnh": "IGNF_LIDAR-HD_MNH_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93",     # hauteur du sursol (MNS - MNT)
         "mns": "IGNF_LIDAR-HD_MNS_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93",     # altitude du dessus (toits, cimes)
         "mnt": "IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93"}     # altitude du sol nu


def mnh(demi_cote=250.0, pas=0.5):
    """MNH / MNS / MNT LiDAR HD autour du batiment 1 (grille carree, Lambert 93, flottants 32 bits little-endian).
    Acquisition LiDAR : 13-14 juin 2021 (mission 21LHD5PK1, IGN, metadonnees IGNF_LIDAR-HD_METADONNEE)."""
    site = Site()
    lat, lon = site.vers_latlon(0, 0)
    cx, cy = lambert93(lat, lon)
    n = int(2 * demi_cote / pas)
    bbox = (cx - demi_cote, cy - demi_cote, cx + demi_cote, cy + demi_cote)
    for nom, couche in LIDAR.items():
        q = {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": couche, "STYLES": "", "CRS": "EPSG:2154",
             "BBOX": ",".join(f"{v:.2f}" for v in bbox), "WIDTH": n, "HEIGHT": n, "FORMAT": "image/x-bil;bits=32"}
        sortie = REF / ("mnh.bil" if nom == "mnh" else f"{nom}.bil")
        p = telecharger(WMS_URL + "?" + urllib.parse.urlencode(q, safe=",:;="), sortie)
        print(f"{nom.upper()} {n}x{n} a {pas} m -> {p} ({p.stat().st_size // 1024} Ko)")
    meta = {"E0": bbox[0], "N0": bbox[1], "E1": bbox[2], "N1": bbox[3], "n": n, "pas_m": pas}
    (REF / "mnh.json").write_text(json.dumps(meta), encoding="utf-8")


def ortho(sortie, lat, lon, larg_m, haut_m, cm, couche="ORTHOIMAGERY.ORTHOPHOTOS"):
    dlat = haut_m / 2 / 110540
    dlon = larg_m / 2 / (111320 * math.cos(math.radians(lat)))
    q = {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": couche, "STYLES": "", "CRS": "EPSG:4326",
         "BBOX": f"{lat - dlat:.7f},{lon - dlon:.7f},{lat + dlat:.7f},{lon + dlon:.7f}",
         "WIDTH": int(larg_m * 100 / cm), "HEIGHT": int(haut_m * 100 / cm), "FORMAT": "image/jpeg"}
    return telecharger(WMS_URL + "?" + urllib.parse.urlencode(q, safe=",:"), sortie)


# --- conversion en unites de jeu -----------------------------------------------------------
def corriger(v):
    """Le serveur renvoie de l'UTF-8 lu comme du latin-1 : on retablit les accents."""
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return v
    return v


def charger(couche):
    d = json.loads((WFS_DIR / f"{couche}.json").read_text(encoding="utf-8"))
    for f in d["features"]:
        f["properties"] = {k: corriger(v) for k, v in f["properties"].items()}
    return d["features"]


def anneaux(geom):
    """Liste d'anneaux exterieurs [(lon, lat), ...] d'un Polygon / MultiPolygon."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


def lignes(geom):
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return list(geom["coordinates"])
    return []


def points(geom):
    if geom["type"] == "Point":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPoint":
        return list(geom["coordinates"])
    return []


def vers_unites(site, pts):
    out = []
    for p in pts:
        x, y = site.proj(p[1], p[0])
        out.append([round(x), round(y)])
    return out


def centroide(poly):
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    if abs(a) < 1e-9:
        return sum(x for x, _ in poly) / len(poly), sum(y for _, y in poly) / len(poly)
    return cx / (3 * a), cy / (3 * a)


def dans_poly(x, y, poly):
    ok = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            ok = not ok
    return ok


def aire(poly):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))) / 2


def dans_export(pts):
    x0, y0, x1, y1 = EXPORT
    return any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts)


def sans_vide(d):
    return {k: v for k, v in d.items() if v not in (None, "", [])}


def bati(site):
    osm = {wid: site.poly(wid)[:-1] for wid, w in site.ways.items() if "building" in w.get("tags", {})}
    res = []
    for f in charger("batiment"):
        p = f["properties"]
        for ring in anneaux(f["geometry"]):
            poly = vers_unites(site, ring)
            if poly[0] == poly[-1]:
                poly = poly[:-1]
            if len(poly) < 3 or not dans_export(poly):
                continue
            cx, cy = centroide(poly)
            osm_id = next((wid for wid, q in osm.items() if dans_poly(cx, cy, q)), None)
            ox, oy, longueur, largeur, ang = obb(poly)
            res.append(sans_vide({
                "id": p["cleabs"][-8:],
                "role": ROLES_OSM.get(osm_id),
                "osm": osm_id,
                "usage": p["usage_1"], "usage2": p["usage_2"],
                "h_m": p["hauteur"], "etages": p["nombre_d_etages"], "logements": p["nombre_de_logements"],
                "murs": p["materiaux_des_murs"], "toit": p["materiaux_de_la_toiture"],
                "z_sol_min": p["altitude_minimale_sol"], "z_sol_max": p["altitude_maximale_sol"],
                "z_sol_jeu": None if p["altitude_minimale_sol"] is None else round((p["altitude_minimale_sol"] - site.alt_ref) * M),
                "z_toit_min": p["altitude_minimale_toit"], "z_toit_max": p["altitude_maximale_toit"],
                "apparition": (p["date_d_apparition"] or "")[:4] or None,
                "origine": p["origine_du_batiment"],
                "emprise": poly,
                "aire_m2": round(aire(poly) / M / M),
                "obb": [round(ox), round(oy), round(longueur), round(largeur), round(math.degrees(ang), 1)],
            }))
    res.sort(key=lambda b: (b.get("role") is None, b["id"]))
    return res


def routes(site):
    res = []
    for f in charger("troncon_de_route"):
        p = f["properties"]
        for ligne in lignes(f["geometry"]):
            tr = vers_unites(site, ligne)
            if not dans_export(tr):
                continue
            res.append(sans_vide({
                "id": p["cleabs"][-8:], "nature": p["nature"],
                "nom": p["nom_collaboratif_gauche"] or p["nom_collaboratif_droite"],
                "largeur_m": p["largeur_de_chaussee"], "voies": p["nombre_de_voies"],
                "sens": p["sens_de_circulation"], "importance": p["importance"],
                "vitesse": p["vitesse_moyenne_vl"], "prive": p["prive"],
                "position_sol": p["position_par_rapport_au_sol"],
                "trace": tr}))
    return res


def surfaces(site, couche, champs):
    res = []
    for f in charger(couche):
        p = f["properties"]
        for ring in anneaux(f["geometry"]):
            poly = vers_unites(site, ring)
            if len(poly) < 3 or not dans_export(poly):
                continue
            if poly[0] == poly[-1]:
                poly = poly[:-1]
            res.append(sans_vide({**{c: p.get(c) for c in champs}, "emprise": poly}))
    return res


def haies(site):
    res = []
    for f in charger("haie"):
        for ligne in lignes(f["geometry"]):
            tr = vers_unites(site, ligne)
            if dans_export(tr):
                res.append({"trace": tr})
    return res


def ponctuels(site):
    res = []
    for f in charger("erp"):
        p = f["properties"]
        for pt in points(f["geometry"]):
            xy = vers_unites(site, [pt])[0]
            if dans_export([xy]):
                res.append(sans_vide({"libelle": p["libelle"], "activite": p["activite_principale"],
                                      "capacite": p.get("capacite_d_accueil_du_public"),
                                      "adresse": " ".join(str(p.get(k) or "") for k in ("adresse_numero", "adresse_nom_1")).strip(),
                                      "pos": xy, "geometrie": p["origine_de_la_geometrie"]}))
    for f in charger("construction_ponctuelle"):
        for pt in points(f["geometry"]):
            xy = vers_unites(site, [pt])[0]
            if dans_export([xy]):
                res.append({"libelle": f["properties"]["nature"], "activite": "construction ponctuelle", "pos": xy})
    return res


def convertir():
    site = Site()
    data = {
        "source": "IGN BD TOPO V3 via la Geoplateforme (data.geopf.fr, WFS), Licence Ouverte Etalab 2.0",
        "telecharge_le": "2026-10-24",
        "repere": f"unites de jeu de tools/geo.py (Site.proj) : origine au centre du batiment 1, y le long du batiment 1, "
                  f"1 m reel = {M:.4f} unites (ECHELLE 1.25) ; x,y arrondis a l'unite (~2 cm) ; altitudes en m (NGF) ; "
                  f"z_sol_jeu = altitude du sol en unites de jeu (z = 0 au pied de la facade est du batiment 1, altitude {Site().alt_ref:.2f} m)",
        "cadre_export_unites": list(EXPORT),
        "codes_materiaux": "murs/toit : codes bruts de la BD TOPO (2 chiffres, herites du cadastre). Lecture probable, non verifiee "
                           "dans le descriptif IGN : murs 1=pierre 2=meuliere 3=beton 4=briques 5=agglomere 6=bois 9=autre, "
                           "chiffre 1 = materiau principal, '30' = beton seul, '23' = meuliere + beton ; toit 1=tuiles 2=ardoises 3=zinc/alu 4=beton",
        "hauteur": "h_m = hauteur du batiment mesuree par l'IGN (pied a l'egout, voir z_toit_min) ; "
                   "z_toit_max - z_toit_min = amplitude du toit (faitage - egout) quand les deux existent",
        "batiments": bati(site),
        "routes": routes(site),
        "parkings": surfaces(site, "equipement_de_transport", ["nature", "nature_detaillee", "toponyme"]),
        "vegetation": surfaces(site, "zone_de_vegetation", ["nature"]),
        "haies": haies(site),
        "zones_activite": surfaces(site, "zone_d_activite_ou_d_interet", ["categorie", "nature", "nature_detaillee", "toponyme"]),
        "terrains_de_sport": surfaces(site, "terrain_de_sport", ["nature", "nature_detaillee"]),
        "points": ponctuels(site),
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SORTIE} : {SORTIE.stat().st_size // 1024} Ko")
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k:18s} {len(v)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "wfs":
        wfs()
    elif cmd == "json":
        convertir()
    elif cmd == "mnh":
        mnh()
    elif cmd == "ortho" and len(sys.argv) >= 8:
        ortho(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]),
              float(sys.argv[7]), *(sys.argv[8:9]))
    else:
        print(__doc__)
