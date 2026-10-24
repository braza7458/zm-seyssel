"""Grille du terrain a pas variable et loi de compression de l'horizon.

Le coeur (cadre jouable) garde le pas de 256 ; autour, le pas croit (512 puis geometrique)
jusqu'au bord du monde visible. Au-dela de R0, les points sont places a leur vraie direction mais
a une distance comprimee (r = R0 + K ln(d / R0)) et leur hauteur est reduite du meme facteur :
les montagnes gardent leur taille apparente depuis le centre, comme dans un decor lointain.
"""

import math

# cadre jouable (unites de jeu)
X0, X1, Y0, Y1 = -5120, 6656, -6656, 5888
PAS = 256
BORD = 14400        # bord du monde visible, de chaque cote de l'origine
BANDE = 9400        # au-dela, la terre est comprimee
R0 = 9400
K = 1000.0


def _etend(depart, sens):
    out, p, pas = [], depart, 512.0
    while True:
        if abs(p) >= BANDE:
            pas *= 1.35
        p += sens * pas
        if abs(p) >= BORD:
            out.append(sens * BORD)
            return out
        out.append(int(round(p / 16.0)) * 16)


def lignes():
    xs = list(range(X0, X1 + 1, PAS))
    ys = list(range(Y0, Y1 + 1, PAS))
    xs = sorted(set(_etend(X0, -1) + xs + _etend(X1, 1)))
    ys = sorted(set(_etend(Y0, -1) + ys + _etend(Y1, 1)))
    return xs, ys


def dans_coeur(x, y):
    return X0 <= x <= X1 and Y0 <= y <= Y1


def distance_vraie(r):
    """Distance reelle (unites) qui correspond au rayon de jeu r."""
    return r if r <= R0 else R0 * math.exp((r - R0) / K)


def position_vraie(x, y):
    """(x_vrai, y_vrai, facteur d'echelle des hauteurs) du point de jeu (x, y)."""
    r = math.hypot(x, y)
    if r <= R0 or r == 0:
        return x, y, 1.0
    rc = min(r, 13400.0)          # les coins de la grille carree sont ramenes a la meme distance
    d = distance_vraie(rc)
    return x * d / r, y * d / r, rc / d
