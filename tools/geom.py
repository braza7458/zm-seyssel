"""Briques de geometrie partagees : toits (a croupes, a pignons, plats), lucarnes.

Un brush = liste de plans (normale, point, materiau [, projection]). Tous les plans
ci-dessous donnent des volumes convexes (verifies par make_blockout.check_brush).
"""

import math


def toit_croupe(u0, v0, u1, v1, z, pente, m_toit, m_rive, fascia=22):
    """Toit a quatre pans de meme pente (un seul brush convexe), faitage le long de u.

    z : hauteur de l'egout ; (u0, v0)-(u1, v1) : emprise du debord.
    Renvoie (plans, z_faitage).
    """
    run = (v1 - v0) / 2
    h = run * math.tan(math.radians(pente))
    planes = [
        ((0, 0, -1), (0, 0, z - fascia), m_rive),
        ((-1, 0, 0), (u0, 0, 0), m_rive), ((1, 0, 0), (u1, 0, 0), m_rive),
        ((0, -1, 0), (0, v0, 0), m_rive), ((0, 1, 0), (0, v1, 0), m_rive),
        ((0, -h, run), (0, v0, z), m_toit), ((0, h, run), (0, v1, z), m_toit),
        ((-h, 0, run), (u0, 0, z), m_toit), ((h, 0, run), (u1, 0, z), m_toit),
    ]
    return planes, z + h


def toit_pignon(u0, v0, u1, v1, z, pente, m_toit, m_rive, m_pignon, fascia=14):
    """Toit a deux pans, faitage le long de u, bouts en pignon (un seul brush convexe)."""
    run = (v1 - v0) / 2
    h = run * math.tan(math.radians(pente))
    planes = [
        ((0, 0, -1), (0, 0, z - fascia), m_rive),
        ((-1, 0, 0), (u0, 0, 0), m_pignon), ((1, 0, 0), (u1, 0, 0), m_pignon),
        ((0, -1, 0), (0, v0, 0), m_rive), ((0, 1, 0), (0, v1, 0), m_rive),
        ((0, -h, run), (0, v0, z), m_toit), ((0, h, run), (0, v1, z), m_toit),
    ]
    return planes, z + h


def toit_plat(u0, v0, u1, v1, z, mat, mat_dessus=None, epaisseur=12):
    """Dalle de toit plate."""
    f = mat_dessus or mat
    return [
        ((0, 0, -1), (0, 0, z - epaisseur), mat), ((0, 0, 1), (0, 0, z), f),
        ((-1, 0, 0), (u0, 0, 0), mat), ((1, 0, 0), (u1, 0, 0), mat),
        ((0, -1, 0), (0, v0, 0), mat), ((0, 1, 0), (0, v1, 0), mat),
    ]


def prisme_pignon(u0, u1, v0, v1, z_bas, z_mur, h_toit, m_mur, m_toit):
    """Lucarne a deux pans : boite de z_bas a z_mur surmontee d'un toit dont le faitage suit v."""
    um = (u0 + u1) / 2
    run = (u1 - u0) / 2
    pente = h_toit / run
    return [
        ((0, 0, -1), (0, 0, z_bas), m_mur),
        ((0, -1, 0), (0, v0, 0), m_mur), ((0, 1, 0), (0, v1, 0), m_mur),
        ((-1, 0, 0), (u0, 0, 0), m_mur), ((1, 0, 0), (u1, 0, 0), m_mur),
        ((-pente, 0, 1), (u0, 0, z_mur), m_toit), ((pente, 0, 1), (u1, 0, z_mur), m_toit),
    ]
