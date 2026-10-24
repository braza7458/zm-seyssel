"""Telecharge l'altitude IGN (RGE ALTI, service altimetrie de data.geopf.fr) des sommets du terrain
hors du coeur jouable : reference/ign/relief_large.json  ([[x, y, altitude_m], ...]).

    python tools/ign_relief_large.py
"""

import json
import sys
import time
import urllib.request

import grille
from geo import REF, Site

URL = "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json?resource=ign_rge_alti_wld&zonly=true&"


def altitudes(points):
    """points : [(lat, lon)] -> [altitude m]."""
    res = []
    for i in range(0, len(points), 120):
        lot = points[i:i + 120]
        q = "lon=" + "|".join(f"{lo:.6f}" for _, lo in lot) + "&lat=" + "|".join(f"{la:.6f}" for la, _ in lot)
        for essai in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(URL + q, headers={"User-Agent": "zm-seyssel"}), timeout=60) as r:
                    res += json.loads(r.read())["elevations"]
                break
            except Exception as e:  # noqa: BLE001
                print("  nouvel essai", essai, e, file=sys.stderr)
                time.sleep(2)
        else:
            raise SystemExit("altimetrie indisponible")
        print(f"  {len(res)}/{len(points)}")
    return res


def main():
    site = Site()
    xs, ys = grille.lignes()
    pts, pos = [], []
    for x in xs:
        for y in ys:
            if grille.dans_coeur(x, y):
                continue
            xv, yv, _ = grille.position_vraie(x, y)
            pts.append(site.vers_latlon(xv, yv))
            pos.append((x, y))
    print(len(xs), "x", len(ys), "lignes ;", len(pts), "points hors du coeur")
    alt = altitudes(pts)
    out = [[x, y, a] for (x, y), a in zip(pos, alt)]
    (REF / "ign" / "relief_large.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("ecrit", len(out), "points, altitude de reference du jeu :", site.alt_ref)


if __name__ == "__main__":
    main()
