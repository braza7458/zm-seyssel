"""Donnees du couloir jusqu'au Carrefour : altitudes IGN, batiments BD TOPO, arbres OpenStreetMap.

    python tools/corridor_donnees.py            tout (altitudes, batiments, arbres)
    python tools/corridor_donnees.py relief     seulement les altitudes
    python tools/corridor_donnees.py batiments  seulement les batiments
    python tools/corridor_donnees.py arbres     seulement les arbres

Ecrit reference/ign/relief_monde.json, reference/ign/bdtopo_couloir.json et reference/osm/arbres_couloir.json.
"""

import json
import math
import sys
import time
import urllib.parse
import urllib.request

import monde
from geo import M, REF, Site, obb

ALTI = "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json?resource=ign_rge_alti_wld&zonly=true&"
WFS = "https://data.geopf.fr/wfs/ows"
UA = {"User-Agent": "zm-seyssel/0.3"}


def http(url, data=None, essais=4):
    for k in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            print("  nouvel essai", k, e, file=sys.stderr)
            time.sleep(3)
    raise SystemExit("service indisponible : " + url[:80])


def altitudes(points):
    res = []
    for i in range(0, len(points), 120):
        lot = points[i:i + 120]
        q = "lon=" + "|".join(f"{lo:.6f}" for _, lo in lot) + "&lat=" + "|".join(f"{la:.6f}" for la, _ in lot)
        res += http(ALTI + q)["elevations"]
        if (i // 120) % 10 == 0:
            print(f"  {len(res)}/{len(points)}")
    return res


def relief(site):
    fs = monde.feuilles()
    sommets = monde.sommets(fs)
    noeuds = monde.noeuds_raster()
    loin = [p for p in sommets if not monde.dans_cadre(*p) and monde.ancre(p)[0] > monde.R0]
    print(len(noeuds), "noeuds de raster,", len(loin), "sommets lointains")
    pts = [site.vers_latlon(i * monde.PAS_RASTER, j * monde.PAS_RASTER) for i, j in noeuds]
    pts += [site.vers_latlon(*monde.position_vraie(*p)[:2]) for p in loin]
    alt = altitudes(pts)
    raster = {f"{i},{j}": a for (i, j), a in zip(noeuds, alt[:len(noeuds)])}
    lointain = {f"{int(x)},{int(y)}": a for (x, y), a in zip(loin, alt[len(noeuds):])}
    (REF / "ign" / "relief_monde.json").write_text(json.dumps({"raster": raster, "lointain": lointain},
                                                              separators=(",", ":")), encoding="utf-8")
    print("relief ecrit :", len(raster), "+", len(lointain))


def boite_latlon(site, marge=0.002):
    ll = [site.vers_latlon(*p) for p in monde.SPINE]
    return (min(a for a, _ in ll) - marge, min(b for _, b in ll) - marge,
            max(a for a, _ in ll) + marge, max(b for _, b in ll) + marge)


def batiments(site):
    la0, lo0, la1, lo1 = boite_latlon(site)
    out, debut = [], 0
    while True:
        q = urllib.parse.urlencode({
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": "BDTOPO_V3:batiment",
            "OUTPUTFORMAT": "application/json", "SRSNAME": "EPSG:4326", "COUNT": 1000, "STARTINDEX": debut,
            "SORTBY": "cleabs", "CQL_FILTER": f"BBOX(geometrie,{la0},{lo0},{la1},{lo1})"})
        d = http(WFS + "?" + q)
        feats = d["features"]
        for f in feats:
            g = f["geometry"]
            if not g:
                continue
            poly = g["coordinates"][0][0]
            pts = [site.proj(c[1], c[0]) for c in poly[:-1]]
            if len(pts) < 3:
                continue
            c = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            if monde.ancre(c)[0] > monde.R0:
                continue
            p = f["properties"]
            cx, cy, l, w, a = obb(pts)
            out.append({"id": p["cleabs"][-8:], "usage": p.get("usage_1") or "", "h_m": p.get("hauteur"),
                        "etages": p.get("nombre_d_etages"), "logements": p.get("nombre_de_logements"),
                        "emprise": [[round(x), round(y)] for x, y in pts],
                        "obb": [round(cx), round(cy), round(l), round(w), round(math.degrees(a), 1)]})
        print(f"  {len(out)} batiments retenus ({debut + len(feats)} lus)")
        if len(feats) < 1000:
            break
        debut += 1000
    (REF / "ign" / "bdtopo_couloir.json").write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def vegetation(site):
    la0, lo0, la1, lo1 = boite_latlon(site)
    out, debut = [], 0
    while True:
        q = urllib.parse.urlencode({
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": "BDTOPO_V3:zone_de_vegetation",
            "OUTPUTFORMAT": "application/json", "SRSNAME": "EPSG:4326", "COUNT": 1000, "STARTINDEX": debut,
            "SORTBY": "cleabs", "CQL_FILTER": f"BBOX(geometrie,{la0},{lo0},{la1},{lo1})"})
        feats = http(WFS + "?" + q)["features"]
        for f in feats:
            g = f["geometry"]
            if not g:
                continue
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for pg in polys:
                pts = [[round(v) for v in site.proj(c[1], c[0])] for c in pg[0][:-1]]
                if len(pts) >= 3:
                    out.append({"nature": f["properties"].get("nature", ""), "pts": pts})
        if len(feats) < 1000:
            break
        debut += 1000
    (REF / "ign" / "bdtopo_vegetation_couloir.json").write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    import collections
    print(len(out), "zones de vegetation", dict(collections.Counter(o["nature"] for o in out)))


def parcelles(site):
    """Parcelles cadastrales (Parcellaire Express) autour du chemin : sert aux jardins et aux haies."""
    la0, lo0, la1, lo1 = boite_latlon(site)
    out, debut = [], 0
    while True:
        q = urllib.parse.urlencode({
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
            "TYPENAMES": "CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle", "OUTPUTFORMAT": "application/json",
            "SRSNAME": "EPSG:4326", "COUNT": 1000, "STARTINDEX": debut,
            "BBOX": f"{la0},{lo0},{la1},{lo1},urn:ogc:def:crs:EPSG::4326"})
        feats = http(WFS + "?" + q)["features"]
        for f in feats:
            g = f["geometry"]
            if not g:
                continue
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for pg in polys:
                pts = [[round(v) for v in site.proj(c[1], c[0])] for c in pg[0][:-1]]
                if len(pts) >= 3:
                    out.append({"id": f["properties"].get("idu", ""), "pts": pts})
        print(f"  {len(out)} parcelles")
        if len(feats) < 1000:
            break
        debut += 1000
    (REF / "ign" / "parcelles_couloir.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")


def arbres(site):
    la0, lo0, la1, lo1 = boite_latlon(site, 0.0015)
    bb = f"({la0},{lo0},{la1},{lo1})"
    req = (f'[out:json][timeout:80];(node["natural"="tree"]{bb};way["natural"="tree_row"]{bb};'
           f'way["natural"="wood"]{bb};way["landuse"="forest"]{bb};way["natural"="scrub"]{bb};'
           f'way["leisure"~"park|pitch|playground"]{bb};way["landuse"~"farmland|meadow|grass|orchard|vineyard"]{bb};'
           f'way["natural"="water"]{bb};way["waterway"~"river|stream"]{bb};way["barrier"~"hedge|fence|wall"]{bb};);out geom;')
    d = http("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": req}).encode())
    arb, bois, rangs, eau, haies, usages = [], [], [], [], [], []
    for e in d["elements"]:
        t = e.get("tags", {})
        if e["type"] == "node":
            arb.append([round(v) for v in site.proj(e["lat"], e["lon"])])
            continue
        pts = [[round(v) for v in site.proj(n["lat"], n["lon"])] for n in e["geometry"]]
        if t.get("natural") == "tree_row":
            rangs.append(pts)
        elif t.get("natural") in ("wood", "scrub") or t.get("landuse") == "forest":
            bois.append(pts)
        elif t.get("natural") == "water" or "waterway" in t:
            eau.append(pts)
        elif "barrier" in t:
            haies.append({"type": t["barrier"], "pts": pts})
        else:
            usages.append({"type": t.get("landuse") or t.get("leisure"), "pts": pts})
    (REF / "osm" / "arbres_couloir.json").write_text(json.dumps({"arbres": arb, "bois": bois, "rangees": rangs, "eau": eau,
                                                                  "haies": haies, "usages": usages},
                                                                 separators=(",", ":")), encoding="utf-8")
    print(len(arb), "arbres,", len(rangs), "rangees,", len(bois), "bois,", len(eau), "eau,", len(haies), "haies,", len(usages), "usages")


if __name__ == "__main__":
    site = Site()
    quoi = sys.argv[1:] or ["relief", "batiments", "arbres"]
    if "relief" in quoi:
        relief(site)
    if "batiments" in quoi:
        batiments(site)
    if "arbres" in quoi:
        arbres(site)
    if "parcelles" in quoi:
        parcelles(site)
    if "vegetation" in quoi:
        vegetation(site)
