"""Nature du sol lue sur l'orthophoto IGN : enrobe, beton, terre (le reste reste en herbe).

    python tools/ortho_jeu.py          (une fois : photo dans le repere du jeu, _build/ref/ortho_jeu.png)
    python tools/sols_donnees.py       -> reference/ign/sols_couloir.json

Cases de 128 unites autour de la zone jouable ; on ecarte les routes (dessinees a part) et les toits ;
un filtre majoritaire 3x3 enleve les voitures et les ombres isolees ; les cases voisines de meme nature
sont fusionnees en rectangles. Outil d'apercu (PIL et numpy), pas utilise par la generation elle-meme.
"""

import json

import numpy as np
from PIL import Image, ImageDraw

import monde
import voirie
from geo import REF, ROOT, Site

X0, Y0, X1, Y1, UPP = -7000, -8000, 21000, 45000, 20.0
CELL = 128
CLASSES = {0: None, 1: "asphalte", 2: "dalle_claire", 3: "terre"}


def main():
    site = Site()
    img = np.asarray(Image.open(ROOT / "_build" / "ref" / "ortho_jeu.png").convert("RGB")).astype(np.float32)
    H, W = img.shape[:2]
    k = int(CELL / UPP)                      # pixels par case (6)
    nx, ny = W * UPP // CELL, H * UPP // CELL
    nx, ny = int(nx), int(ny)

    # masque des routes et des batiments (ce qui est deja modelise)
    masque = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(masque)

    def P(x, y):
        return ((x - X0) / UPP, (Y1 - y) / UPP)

    class Q:
        pass
    q = Q()
    q.site = site
    for hw, nom, pts, acces, ow in voirie.routes_osm(q):
        larg = voirie.NOMS.get(nom, voirie.HW_LARG[hw])
        d.line([P(*p) for p in pts], fill=255, width=max(1, int(larg / UPP)))
    for f in ("bdtopo_couloir.json",):
        for b in json.loads((REF / "ign" / f).read_text(encoding="utf-8")):
            d.polygon([P(*p) for p in b["emprise"]], fill=255)
    for b in json.loads((REF / "ign" / "bdtopo_quartier.json").read_text(encoding="utf-8"))["batiments"]:
        d.polygon([P(*p) for p in b["emprise"]], fill=255)
    m = np.asarray(masque) > 0

    classe = np.zeros((ny, nx), np.int8)
    for j in range(ny):
        for i in range(nx):
            x, y = X0 + (i + 0.5) * CELL, Y1 - (j + 0.5) * CELL
            if monde.dist_jouable(x, y) > 2500:
                continue
            bloc = img[j * k:(j + 1) * k, i * k:(i + 1) * k]
            mb = m[j * k:(j + 1) * k, i * k:(i + 1) * k]
            if bloc.size == 0 or mb.mean() > 0.4:
                continue
            r, g, b = np.median(bloc.reshape(-1, 3), 0)
            mx, mn = max(r, g, b), min(r, g, b)
            lum = (r + g + b) / 3
            sat = mx - mn
            if b > g + 6 and b > r + 6:
                continue                    # eau
            exg = 2 * g - r - b
            if exg > 8 or (exg > 3 and sat >= 18):
                continue                    # vegetation (indice de vert)
            if lum < 85:
                continue                    # ombre ou herbe sombre : on ne sait pas
            # dispersion interne : un enrobe est uniforme, un jardin ou un arbre est bruite
            if r > g > b and 25 <= sat < 80 and lum > 120:
                classe[j, i] = 3            # terre, gravier ocre
            elif sat < 40:
                classe[j, i] = 1 if lum < 165 else 2
    # filtre majoritaire 3x3
    lisse = classe.copy()
    for j in range(1, ny - 1):
        for i in range(1, nx - 1):
            v = classe[j - 1:j + 2, i - 1:i + 2].ravel()
            cnt = np.bincount(v.astype(np.int64), minlength=4)
            c = int(cnt.argmax())
            lisse[j, i] = c if cnt[c] >= 5 else (classe[j, i] if cnt[classe[j, i]] >= 4 else 0)
    # composantes connexes : on ne garde que les grandes surfaces uniformes (cours, grands parkings)
    vu = np.zeros_like(lisse, bool)
    for j in range(ny):
        for i in range(nx):
            if lisse[j, i] == 0 or vu[j, i]:
                continue
            c = lisse[j, i]
            pile, comp = [(j, i)], []
            vu[j, i] = True
            while pile:
                a, b = pile.pop()
                comp.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    aa, bb = a + da, b + db
                    if 0 <= aa < ny and 0 <= bb < nx and not vu[aa, bb] and lisse[aa, bb] == c:
                        vu[aa, bb] = True
                        pile.append((aa, bb))
            if len(comp) < 30:
                for a, b in comp:
                    lisse[a, b] = 0
    # rectangles : runs horizontaux puis fusion verticale (4 x 4 cases au plus, pour suivre le relief)
    rects = []
    pris = np.zeros_like(lisse, bool)
    for j in range(ny):
        i = 0
        while i < nx:
            c = lisse[j, i]
            if c == 0 or pris[j, i]:
                i += 1
                continue
            w = 1
            while i + w < nx and w < 4 and lisse[j, i + w] == c and not pris[j, i + w]:
                w += 1
            h = 1
            while j + h < ny and h < 4 and all(lisse[j + h, i + t] == c and not pris[j + h, i + t] for t in range(w)):
                h += 1
            pris[j:j + h, i:i + w] = True
            x0 = X0 + i * CELL
            y1 = Y1 - j * CELL
            rects.append([round(x0), round(y1 - h * CELL), round(x0 + w * CELL), round(y1), CLASSES[int(c)]])
            i += w
    (REF / "ign" / "sols_couloir.json").write_text(json.dumps(rects, separators=(",", ":")), encoding="utf-8")
    import collections
    print(len(rects), "rectangles", dict(collections.Counter(r[4] for r in rects)))


if __name__ == "__main__":
    main()
