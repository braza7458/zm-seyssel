"""Superpose la map generee (dessus des routes, trottoirs, maisons, immeubles) a l'orthophoto IGN.

    python tools/ortho_jeu.py            (une fois : photo dans le repere du jeu)
    python tools/controle_ortho.py       -> _build/ref/controle_map.png

Routes en gris clair, trottoirs en blanc, maisons et immeubles en contour rouge : ce qui ne tombe pas
sur la photo est mal place.
"""

from PIL import Image, ImageDraw

from geo import ROOT
from preview_blockout import faces, read_brushes

X0, Y0, X1, Y1, UPP = -7000, -8000, 21000, 45000, 20.0
PREFABS = ROOT / "game" / "map_source" / "_prefabs" / "zm_seyssel"


def P(x, y):
    return ((x - X0) / UPP, (Y1 - y) / UPP)


def main():
    img = Image.open(ROOT / "_build" / "ref" / "ortho_jeu.png").convert("RGBA")
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    groupes = {"voirie": ((255, 220, 0, 90), None), "trottoirs": ((0, 255, 255, 110), None),
               "parkings": ((80, 80, 255, 120), None), "sols": ((255, 0, 255, 90), None), "clotures": ((0, 255, 0, 220), None),
               "marquages": ((255, 255, 255, 255), None), "maisons": (None, (255, 40, 40, 255)),
               "batiment": (None, (255, 0, 255, 255)), "annexes": (None, (255, 140, 0, 255))}
    for chemin in sorted(PREFABS.glob("*.map")):
        g = next((k for k in groupes if chemin.stem.startswith(k)), None)
        if not g:
            continue
        rempli, contour = groupes[g]
        for planes in read_brushes([chemin]):
            for n, poly, mat in faces(planes):
                if n[2] < 0.5:
                    continue
                pts = [P(v[0], v[1]) for v in poly]
                if rempli:
                    d.polygon(pts, fill=rempli)
                elif "roof" in mat or "rubber" in mat or "gravel" in mat:
                    d.polygon(pts, outline=contour)
    Image.alpha_composite(img, calque).convert("RGB").save(ROOT / "_build" / "ref" / "controle_map.png")
    print("ecrit _build/ref/controle_map.png")


if __name__ == "__main__":
    main()
