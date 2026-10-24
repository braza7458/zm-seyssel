"""Materiaux du quartier : cle -> nom exact (verifie dans les GDT des Mod Tools), echelle des textures.

Genere a partir du cahier des charges docs/conception-v0.3.md (section B), puis edite a la main.
python tools/materiaux.py            verifie que chaque nom existe dans les GDT des Mod Tools
"""

import re
import sys
from pathlib import Path

TOOLS = Path(r"D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130")

# Materiaux a alpha ou au rendu incertain : False les remplace par leur repli (voir REPLI)
ALPHA_OK = True

MAT = {
    "herbe": "core_grass_med",
    "herbe_sombre": "core_grass_dark",
    "herbe_clairsemee": "t7_grass_crab_low_sparse_green",
    "terre": "core_dirt_light",
    "montagne": "core_grass_dark",
    "foret": "t7_dirt_grassy_forest_ground",
    "eau": "t7_water_sector_flow",
    "roche": "t7_dirt_rocky_02",
    "ciel": "sky",
    "clip": "clip_player",
    "asphalte": "core_asphault_med",
    "asphalte_sombre": "core_asphault_dark",
    "trottoir": "t7_concrete_sidewalk_02",
    "dalle_claire": "t7_concrete_sidewalk_01",
    "bordure": "t7_street_concrete_curb_01a",
    "marquage": "t7_plastic_base_clean",
    "marquage_decal": "t7_decal_signage_street_lines_white",
    "gravier": "t7_stone_pebbles_01",
    "gravier_clair": "core_gravel_light",
    "facade_beige": "core_plaster_light",
    "facade_blanche": "t7_plaster_smooth_light_01",
    "socle": "t7_concrete_floor_sealed_01_warm",
    "panneau": "t7_metal_wall_corrugated_hor_brown_drk",
    "loggia": "t7_drywall_painted_brown_01",
    "fenetre": "core_window_opaque",
    "vitre": "core_glass_plain_trans",
    "fond_vitre": "t7_metal_painted_wall_dirty_black",
    "cadre": "t7_plastic_base_clean",
    "appui": "t7_concrete_trim_beveled_03",
    "volet": "t7_metal_wall_corrugated_hor",
    "garage": "t7_metal_panels_painted_2x4",
    "porte": "core_door_wood_dark",
    "porte_asc": "t7_metal_bare_stainless_steel_brushed",
    "garde_corps": "t7_metal_paint_worn_grey_dk",
    "rail_clair": "t7_metal_perforated_small_white",
    "rail_clair_main": "t7_metal_painted_clean_white",
    "rail_sombre": "t7_metal_grating_expanded",
    "rail_sombre_main": "t7_metal_painted_wall_dirty_black",
    "rail_plein": "t7_metal_worn_painted_graphite",
    "rail_vert": "t7_glass_frosted_01_opaque_teal",
    "dalle_balcon": "t7_concrete_bare_weathered_01",
    "balcon": "t7_plaster_smooth_light_01",
    "toit": "core_roof_dark",
    "toit_terre": "core_roof_light",
    "toit_plat": "t7_rubber_roof_granular",
    "rive": "t7_wood_trim_dark_brown",
    "cheminee": "t7_plaster_smooth_light_01",
    "auvent": "t7_concrete_bare_weathered_01",
    "hall_sol": "t7_stone_travertine",
    "hall_mur": "core_plaster_light",
    "plafond": "t7_drywall_painted_white_01",
    "rampe": "t7_metal_bare_stainless_steel_brushed",
    "boites": "t7_metal_bare_aluminum_brushed",
    "dalle": "t7_concrete_floor_sealed_01",
    "gaine": "t7_concrete_floor_sealed_01",
    "cabine": "t7_metal_bare_stainless_steel_brushed",
    "cabine_sol": "t7_linoleum_floor_tile_square",
    "appart_mur": "t7_drywall_painted_white_01",
    "sol_entree": "core_tile_light",
    "sol_cuisine": "t7_ceramic_tiles_16x16",
    "sol_sdb": "t7_ceramic_tile_shower_white",
    "sol_chambre": "t7_wood_veneer_sugarpine_matte",
    "faience": "t7_ceramic_tile_large_white",
    "meuble": "t7_wood_panel_01_stain_brown_drk",
    "annexe": "t7_concrete_poured_bunker_paint_01_grey_lt",
    "garages": "t7_plaster_smooth_light_01",
    "voisin": "t7_plaster_rough_worn_01",
    "voisin_clair": "core_plaster_light",
    "voisin_blanc": "t7_plaster_smooth_light_01",
    "voisin_toit": "core_roof_light",
    "voisin_toit_gris": "core_roof_dark",
    "volet_bleu": "t7_metal_panels_2x16_trim_blue",
    "volet_vert": "t7_metal_panels_painted_2x4_green",
    "volet_brun": "t7_wood_worn_darker_brown",
    "muret": "t7_concrete_bare_weathered_01",
    "grillage": "core_fence_chain_link",
    "ecole": "t7_plaster_smooth_light_01",
    "ecorce": "t7_wood_planks_worn",
    "feuillage": "core_grass_dark",
    "feuillage_clair": "core_grass_med",
    "conteneur": "t7_metal_panels_painted_2x1_grey",
    "metal": "t7_metal_bare_graphite_matte",
}

# nom de materiau -> (largeur, hauteur) en unites d'une repetition de la texture
ECH = {
    "t7_water_sector_flow": (512, 512),
    "t7_dirt_grassy_forest_ground": (256, 256),
    "t7_dirt_rocky_02": (256, 256),
    "core_asphault_dark": (160, 160),
    "core_asphault_med": (160, 160),
    "core_dirt_light": (128, 128),
    "core_door_wood_dark": (40, 80),
    "core_fence_chain_link": (80, 80),
    "core_glass_plain_trans": (80, 80),
    "core_grass_dark": (128, 128),
    "core_grass_med": (128, 128),
    "core_gravel_light": (128, 128),
    "core_plaster_light": (128, 128),
    "core_roof_dark": (128, 128),
    "core_roof_light": (128, 128),
    "core_tile_light": (80, 80),
    "t7_ceramic_tile_large_white": (80, 80),
    "t7_ceramic_tile_shower_white": (80, 80),
    "t7_ceramic_tiles_16x16": (80, 80),
    "t7_concrete_bare_weathered_01": (80, 80),
    "t7_concrete_floor_sealed_01": (160, 160),
    "t7_concrete_floor_sealed_01_warm": (160, 160),
    "t7_concrete_poured_bunker_paint_01_grey_lt": (160, 160),
    "t7_concrete_sidewalk_01": (80, 80),
    "t7_concrete_sidewalk_02": (80, 80),
    "t7_concrete_trim_beveled_03": (160, 40),
    "t7_decal_signage_street_lines_white": (80, 10),
    "t7_drywall_painted_brown_01": (80, 80),
    "t7_drywall_painted_white_01": (80, 80),
    "t7_glass_frosted_01_opaque_teal": (80, 80),
    "t7_grass_crab_low_sparse_green": (128, 128),
    "t7_linoleum_floor_tile_square": (80, 80),
    "t7_metal_bare_aluminum_brushed": (80, 80),
    "t7_metal_bare_graphite_matte": (80, 80),
    "t7_metal_bare_stainless_steel_brushed": (80, 80),
    "t7_metal_grating_expanded": (80, 80),
    "t7_metal_paint_worn_grey_dk": (80, 80),
    "t7_metal_painted_clean_white": (80, 80),
    "t7_metal_painted_wall_dirty_black": (80, 80),
    "t7_metal_panels_2x16_trim_blue": (160, 160),
    "t7_metal_panels_painted_2x1_grey": (160, 160),
    "t7_metal_panels_painted_2x4": (160, 160),
    "t7_metal_panels_painted_2x4_green": (160, 160),
    "t7_metal_perforated_small_white": (80, 80),
    "t7_metal_wall_corrugated_hor": (80, 80),
    "t7_metal_wall_corrugated_hor_brown_drk": (80, 80),
    "t7_metal_worn_painted_graphite": (80, 80),
    "t7_plaster_rough_worn_01": (160, 160),
    "t7_plaster_smooth_light_01": (160, 160),
    "t7_plastic_base_clean": (80, 80),
    "t7_rubber_roof_granular": (160, 160),
    "t7_stone_pebbles_01": (80, 80),
    "t7_stone_travertine": (80, 80),
    "t7_street_concrete_curb_01a": (80, 20),
    "t7_wood_panel_01_stain_brown_drk": (80, 80),
    "t7_wood_planks_worn": (80, 80),
    "t7_wood_trim_dark_brown": (80, 5),
    "t7_wood_veneer_sugarpine_matte": (80, 80),
    "t7_wood_worn_darker_brown": (80, 80),
}

REPLI = {
    "rail_clair": "rail_clair_main", "rail_sombre": "rail_sombre_main", "rail_vert": "rail_plein",
    "grillage": "garde_corps", "marquage_decal": "marquage", "volet_bleu": "volet_brun",
}
if not ALPHA_OK:
    for _k, _v in REPLI.items():
        MAT[_k] = MAT[_v]

# materiaux d'outil, sans texture
OUTILS = {"sky", "clip_player", "trigger", "caulk", "volume"}


def projection(materiau, normale):
    """(largeur, hauteur, decalage x, decalage y, rotation) ecrits sur une face du .map."""
    w, h = ECH.get(materiau, (128, 128))
    # bandes plus longues que hautes : sur une face horizontale le grand cote suit le grand axe x/y de la face
    if w >= 3 * h and abs(normale[2]) > 0.7:
        return w, h, 0, 0, 0
    return w, h, 0, 0, 0


def noms_gdt(tools=TOOLS):
    noms = set()
    motif = re.compile(r'^\s*"([^"]+)"\s*[(\[]', re.M)
    for gdt in Path(tools).rglob("*.gdt"):
        noms.update(motif.findall(gdt.read_text(encoding="latin-1", errors="replace")))
    return noms


def verifier(tools=TOOLS):
    """Noms de MAT absents des GDT (hors materiaux d'outil)."""
    presents = noms_gdt(tools)
    return sorted({m for m in MAT.values() if m not in presents and m not in OUTILS})


if __name__ == "__main__":
    manque = verifier(*sys.argv[1:])
    print(f"{len(set(MAT.values()))} materiaux, {len(manque)} absents des GDT")
    for m in manque:
        print("  absent :", m)
    sys.exit(1 if manque else 0)
