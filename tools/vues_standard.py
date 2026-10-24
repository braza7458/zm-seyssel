"""Jeu de vues standard : rend toujours les memes cadrages pour comparer avant/apres une modification.

Chaque vue est une ligne de commande de preview_png.py ; les noms sont numerotes comme dans
docs/references/audit-v0.2.md. A lancer depuis la racine du depot :

    python tools/vues_standard.py                       # toutes les vues -> _build/renders/vues/
    python tools/vues_standard.py --dossier _build/renders/apres --prefixe APRES
    python tools/vues_standard.py 10_bat1_est_halls 12_bat1_arriere_balcons   # seulement celles-la
    python tools/vues_standard.py --liste               # affiche les noms

Un rendu complet prend 5 a 13 s par vue (lecture des .map comprise) et environ 200 Mo de memoire.
Les vues "elevation" sont orthographiques (azimut + elevation 0) et ne gardent que l'immeuble : elles
servent a comparer la position des fenetres, balcons et halls d'un rendu a l'autre.
"""

import argparse
import gc
import sys
from pathlib import Path

from PIL import ImageDraw, ImageFont

import preview_png as pp
from geo import M, Site

RACINE = pp.RACINE
SANS_ANNEXE = ["--sans-vegetation", "--sans", "bunker,pebbles"]
BOITE_Q = ["--boite", "-4700", "-4700", "-500", "6000", "6000", "2600"]
# boites englobant un immeuble seul (unites de jeu), pour les elevations
BOITE_B1 = ["--boite", "-600", "-1600", "-250", "450", "1600", "1100"]
BOITE_B2 = ["--boite", "-760", "2840", "-250", "1290", "3760", "1100"]
BOITE_B3 = ["--boite", "1630", "3770", "-120", "4730", "4730", "1250"]

# nom -> (arguments de preview_png.py, titre de l'etiquette)
VUES = {
    "00_ensemble_quartier": (["--vue", "35", "42"] + BOITE_Q, "ensemble du quartier"),
    "01_plan_dessus": (["--vue", "0", "90"] + BOITE_Q, "plan de dessus (X vers la droite, Y vers le haut)"),
    "02_plan_empreintes_osm": (["--vue", "0", "90"] + BOITE_Q, "plan de dessus + contours OSM (jaune)"),
    "10_bat1_est_halls": (["--cible", "batiment_1", "--face", "est"] + SANS_ANNEXE, "batiment 1 cote halls (est), annexe masquee"),
    "11_bat1_ouest_arriere": (["--cible", "batiment_1", "--face", "ouest", "--sans-vegetation"], "batiment 1 arriere (ouest), arbres masques"),
    "12_bat1_arriere_balcons": (["--cible", "batiment_1", "--face", "ouest", "--sans-vegetation", "--portion", "0", "0.36",
                                 "--niveaux", "0", "5", "--yaw", "30", "--pitch", "6"], "gros plan balcons arriere (bat 1, hall 0)"),
    "13_bat1_hall_facade": (["--cible", "batiment_1", "--face", "est"] + SANS_ANNEXE + ["--portion", "0.36", "0.64", "--niveaux", "0", "2.4",
                                                                                         "--yaw", "18", "--pitch", "6"], "gros plan hall central (facade)"),
    "14_bat1_hall_interieur": (["--camera", "250", "-95", "75", "100", "-10", "95", "--fov", "80"],
                               "interieur du hall central (escalier a gauche, ascenseur a droite)"),
    "15_bat1_elevation_est": (["--vue", "90", "0"] + BOITE_B1, "batiment 1, elevation cote halls (est)"),
    "16_bat1_elevation_ouest": (["--vue", "270", "0"] + BOITE_B1, "batiment 1, elevation arriere (ouest)"),
    "20_bat2_nord_halls": (["--cible", "batiment_2", "--face", "nord", "--sans-vegetation"], "batiment 2 cote halls (nord)"),
    "21_bat2_sud_arriere": (["--cible", "batiment_2", "--face", "sud", "--sans-vegetation"], "batiment 2 arriere (sud)"),
    "22_bat3_nord_halls": (["--cible", "batiment_3", "--face", "nord", "--sans-vegetation"], "batiment 3 cote halls (nord)"),
    "23_bat3_sud_arriere": (["--cible", "batiment_3", "--face", "sud", "--sans-vegetation"], "batiment 3 arriere (sud)"),
    "25_bat2_elevation_nord": (["--vue", "180", "0"] + BOITE_B2, "batiment 2, elevation cote halls (nord)"),
    "26_bat3_elevation_nord": (["--vue", "180", "0"] + BOITE_B3, "batiment 3, elevation cote halls (nord)"),
    "30_voisins_amas_est": (["--camera", "1500", "-3900", "900", "3900", "-1300", "120", "--fov", "58"], "maisons voisines (amas est)"),
    "31_voisin_gros_plan": (["--camera", "3000", "-1800", "330", "3950", "-1000", "150", "--fov", "62", "--sans-vegetation"],
                            "maisons voisines, gros plan (pavillons OSM 131540758 et 131540899)"),
    "32_zone_ecole": (["--vue", "15", "38", "--boite", "-600", "-4700", "-400", "3700", "-1400", "1500"],
                      "zone de l'ecole maternelle (OSM 131537380)"),
    "33_bord_est": (["--vue", "65", "12", "--centre", "--boite", "3800", "-2600", "-700", "9500", "2600", "900", "--sans-vegetation"],
                    "bord est : la dalle de terrain flotte au-dessus de la plaine (fente de ciel)"),
    "34_route_avenue": (["--vue", "0", "90", "--boite", "-2600", "-900", "-500", "-1300", "900", "800", "--sans-vegetation"],
                        "avenue Borcier vue de dessus"),
    "35_chemin_nord_est": (["--vue", "0", "90", "--boite", "4200", "2500", "-500", "6000", "4600", "1500", "--sans-vegetation"],
                           "chemin nord-est vu de dessus"),
    "36_parking_haut": (["--vue", "0", "90", "--boite", "1400", "-1100", "-500", "3400", "1400", "1500", "--sans-vegetation"],
                        "parking du haut vu de dessus"),
    "40_zfight_bat1_arriere": (["--cible", "batiment_1", "--face", "ouest", "--sans-vegetation", "--portion", "0", "0.36", "--niveaux", "0", "5",
                                "--yaw", "30", "--pitch", "6", "--zfight"], "z-fighting en magenta (bat 1 arriere)"),
    "41_zfight_bat3_pignon": (["--cible", "batiment_3", "--face", "ouest", "--sans-vegetation", "--zfight"],
                              "z-fighting en magenta (pignon ouest bat 3, appartement)"),
    "42_zfight_bat1_est": (["--cible", "batiment_1", "--face", "est"] + SANS_ANNEXE + ["--zfight", "--portion", "0.3", "1", "--niveaux", "0", "5"],
                           "z-fighting en magenta (bat 1 cote halls)"),
}


def contours_osm(im, cam, res):
    """Dessine en jaune les contours de tous les batiments OSM sur un plan de dessus (pour voir ce qui manque)."""
    site = Site()
    k, cx, cy = cam.cadre
    d = ImageDraw.Draw(im, "RGBA")
    n = 0
    for w in site.ways.values():
        if "building" not in w.get("tags", {}):
            continue
        pts = [site.proj(p["lat"], p["lon"]) for p in w["geometry"]]
        px = [(res[0] / 2 + k * (x * cam.droite[0] + y * cam.droite[1] - cx),
               res[1] / 2 - k * (x * cam.haut[0] + y * cam.haut[1] - cy)) for x, y in pts]
        if all(not (0 <= x <= res[0] and 0 <= y <= res[1]) for x, y in px):
            continue
        d.line(px, fill=(255, 235, 0, 255), width=2)
        n += 1
    try:
        police = ImageFont.load_default(size=14)
    except TypeError:
        police = ImageFont.load_default()
    d.rectangle([6, 6, 470, 30], fill=(20, 20, 24, 230))
    d.text((12, 10), f"{n} batiments OSM dans l'image (contour jaune)", fill=(240, 240, 240), font=police)
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vues", nargs="*", help="noms de vues (defaut : toutes)")
    ap.add_argument("--dossier", default=str(RACINE / "_build" / "renders" / "vues"))
    ap.add_argument("--prefixe", default="", help="mot ecrit au debut de chaque etiquette (AVANT, APRES...)")
    ap.add_argument("--res", type=int, nargs=2, default=(1600, 1000))
    ap.add_argument("--liste", action="store_true")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if args.liste:
        print("\n".join(VUES))
        return
    noms = args.vues or list(VUES)
    inconnues = [n for n in noms if n not in VUES]
    if inconnues:
        raise SystemExit(f"vues inconnues : {inconnues} (voir --liste)")
    dossier = Path(args.dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    for nom in noms:
        cmd, titre = VUES[nom]
        etiquette = f"{args.prefixe} - {titre}" if args.prefixe else titre
        sortie = dossier / f"{nom}.png"
        im, cam, _ = pp.main(cmd + ["--res", str(args.res[0]), str(args.res[1]), "--etiquette", etiquette, "-o", str(sortie)])
        if nom == "02_plan_empreintes_osm":
            contours_osm(im, cam, args.res)
            im.save(sortie)
        del im, cam
        gc.collect()


if __name__ == "__main__":
    main()
