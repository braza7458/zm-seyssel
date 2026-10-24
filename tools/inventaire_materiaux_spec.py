"""Contenu editorial de l'inventaire des materiaux (besoins, candidats, avis, remplacements).

Utilise par inventaire_materiaux.py, qui ajoute pour chaque candidat les faits mesures
(GDT, image, dimensions, teinte moyenne, echelle .map, dimensions des modeles).
Les textes sont ecrits pour le document .md : ils portent donc des accents.
Chaque avis dit ce qui est VU (lu dans un GDT, mesure ou regarde dans un apercu), DEDUIT ou INCONNU.
"""


def C(nom, rang, note, avis, reserves=""):
    return {"nom": nom, "rang": rang, "note": note, "avis": avis, "reserves": reserves}


REC, ALT, LIM, EVI = "recommandé", "alternative", "limité", "à éviter"

# ---------------------------------------------------------------------------------------------------
CONSTATS = [
    "Les matériaux ne sont PAS dans source_data\\*.gdt : ces 56 fichiers contiennent des sons de pas, armes, caméras, brouillards, etc. ; leurs seuls matériaux sont 4 matériaux de lens flare. "
    "Les matériaux sont dans texture_assets\\*.gdt (56 fichiers), art_assets\\t6_legacy\\texture_assets\\*.gdt (13 fichiers, famille core_*) et model_export\\**\\*.gdt "
    "(214 fichiers, matériaux mtl_* propres aux modèles). Les 354 GDT et 16 062 entrées correspondent exactement au journal de la base (gdtdb.log).",
    "Beaucoup de matériaux ne sont PAS des définitions complètes mais des instances `\"nom\" [ \"parent\" ]` qui reprennent un parent et ne changent que quelques valeurs, "
    "surtout `colorTint`. Une recherche textuelle de `\"t7_drywall_base_cream\" ( \"material.gdf\" )` ne les trouve pas : il faut chercher l'en-tête avec des crochets. "
    "Six noms de MAT paraissaient absents pour cette raison ; ils existent tous.",
    "Les images sources (.tif) sont présentes pour 97 % des matériaux (4 683 sur 4 823) : la bibliothèque livrée est un sous-ensemble cohérent du jeu, pas une liste d'identifiants sans fichier. "
    "Le journal de liaison (_build/link.log) montre que le linker convertit ces .tif à la demande : tout matériau dont l'image est présente est utilisable.",
    "L'échelle de répétition des textures est 2 à 4 fois trop grande dans le projet : make_blockout.py écrit `256 256` pour toutes les faces (lignes 208 et 221 à la date de lecture). Dans les 724 .map officiels des Mod Tools, "
    "les deux premiers nombres après le nom du matériau valent le plus souvent 64 ou 128 et gardent les proportions de l'image (bordure 1024×256 → 64 × 16, bandeau 1024×64 → 64 × 4) ; "
    "déduit : ce sont les dimensions en unités de monde d'une répétition de la texture. "
    "Avec 256 × 256, une bordure ou un liseré est étiré 4 à 16 fois. Valeur à retenir : celle du stock (colonne « Échelle .map »), multipliée par 1,25 pour rester proportionnée à ECHELLE.",
    "Les modèles et les unités : tous les xmodel sont dessinés à 1 unité = 1 pouce. Le quartier est agrandi de 1,25 (geo.py) : pour qu'une voiture ou un banc ait la bonne taille à côté des immeubles, "
    "il faut `modelscale 1.25`. Les voitures sont posées à l'échelle 1 dans quartier.py : elles font environ 2,7 m « à l'échelle du quartier » au lieu de 3,4 m.",
    "Aucun beige clair lisse n'existe tel quel : le « beige » du bâtiment 1 (t7_plaster_smooth_light_01) est en réalité un gris clair, et le « blanc » des bâtiments 2 et 3 "
    "(t7_concrete_worn_painted_white) un gris-vert terne. Le moyen propre est une instance teintée (§10), exactement comme Treyarch le fait (t7_plaster_smooth_light_01_grey, t7_drywall_painted_beige_01…).",
    "Aucune tuile brun foncé n'existe : core_roof_dark est une ardoise gris-bleu, core_roof_light une tuile mécanique rose-orangé (très réaliste), core_roof_med est en 64 px. "
    "Pour le toit « brun foncé » des immeubles : instance teintée de core_roof_light (§10).",
    "Modèles absents (vérifié par noms, par fichiers et par GDT) : peuplier, sapin ou conifère quelconque, feuillus autres que l'albizia et l'acacia, lampadaire de rue, panneau routier, "
    "boîte aux lettres, bouche d'incendie, jeux d'enfants, souche de cheminée. Les dossiers p7_cai_street_signage et p7_road_guard_metal ne contiennent que des matériaux orphelins, aucun modèle.",
    "Trouvailles utiles : p7_trashcan_metal_modern_glass / _organic / _paper (trois bacs de tri, 0,84 × 1,23 m) ; p7_pipe_pvc_drain_* (descentes d'eaux pluviales, 10 cm × 3,25 m) ; "
    "p7_louver_window_wooden_closed (persienne bois 1,63 × 2,84 m) ; p7_door_metal_rolling_02 (rideau roulant 2,87 × 2,56 m) ; p7_street_curb_concrete_64a/b (bordure 1,63 m) ; "
    "t7_decal_signage_street_lines_white / _yellow (marquages au sol) ; p7_civ_sat_dish (antenne parabolique) ; p7_ac_unit_wall_mount_01 (climatiseur mural).",
    "Les cartes de brillance (_g), d'occlusion (_o) et spéculaires (_s) ne sont pas toutes livrées : pour les matériaux t7_ et core_, il en manque 50 à 60 % (brillance 299 sur 597, occlusion 147 sur 244, spéculaire 104 sur 210), "
    "alors que les cartes de couleur (3 manquantes sur 886) et de normales (12 sur 637) sont presque toutes là. Le linker passe sans erreur sur des matériaux dans ce cas (t7_plaster_smooth_light_01 : seuls _c et _n sont convertis dans link.log) ; "
    "déduit : valeurs par défaut, donc un rendu un peu plus plat que dans le jeu officiel. Inconnu : l'écart visuel réel.",
    "Les matériaux core_* portent le drapeau `doNotUse = 1` (héritage de l'ancien jeu), mais ils sont déjà compilés dans zm_seyssel sans erreur (link.log : core_grass_med, core_roof_dark, "
    "core_window_opaque, core_door_wood_dark…). Les matériaux mtl_* ont `usage = <not in editor>` : ils ne sont pas listés dans Radiant ; on peut les écrire à la main dans le .map "
    "mais ils sont conçus pour des modèles précis, donc rarement adaptés à un brush.",
]

MANQUES = [
    "Rendu dans le moteur : on ne sait pas ici comment un matériau réagit au soleil, aux sondes de reflets ou à l'exposition ; les teintes données sont celles des images, multipliées par colorTint.",
    "Couleur réelle des bâtiments : les couleurs « beige », « brun foncé », « blanc » viennent de la fiche docs/batiments (texte) ; aucune photo n'a été lue pour cet inventaire.",
    "Les matériaux de type decal / reveal / blend (marquages, *_blend) n'ont pas été testés sur un brush ; leur comportement dans Radiant et au linker est un à-vérifier.",
    "Les matériaux à alpha (grillages, métal déployé, feuillages) : le canal alpha est bien présent dans les .tif (mesuré), mais le découpage réel en jeu dépend du type de matériau ; non testé.",
    "Les dimensions des modèles sont mesurées sur les sommets du LOD0 (méthode validée sur les bordures de 64 pouces, les tuyaux de 64/128 pouces, les haies de 48 × 48 × 36) ; "
    "elles incluent les feuillages et les accessoires. Le nombre de sommets du LOD0 donne le coût relatif, pas un budget de jeu.",
    "Les rotations de projection (tourner une texture de 90°) : le format .map de make_blockout.py a un champ après les décalages ; son effet n'a pas été vérifié ici.",
]

APERCUS_CLES = [
    "t7_plaster_smooth_light_01", "t7_plaster_rough_worn_01", "core_plaster_light", "t7_concrete_worn_painted_white",
    "t7_concrete_bare_weathered_01", "t7_concrete_floor_sealed_01", "t7_brick_worn_red", "t7_brick_worn_heavy_grout_brown",
    "core_roof_dark", "core_roof_light", "core_roof_med", "t7_metal_wall_corrugated_hor_brown_drk",
    "t7_asphalt_dirty_dark_desert", "core_asphault_dark", "t7_asphalt_damaged_dark_wet", "t7_concrete_sidewalk_02",
    "t7_concrete_sidewalk_01", "t7_street_concrete_curb_01a", "core_grass_med", "t7_grass_crab_low_sparse_green",
    "t7_stone_pebbles_01", "core_gravel_dark", "core_dirt_med", "t7_wood_panel_01_stain_brown_drk",
    "t7_wood_trim_dark_brown", "t7_plastic_base_clean", "core_window_opaque", "t7_metal_wall_corrugated_panel_hor_grey",
    "core_fence_chain_link", "t7_metal_chainlink", "t7_metal_fence_post_cable", "core_foliage_bushline",
    "t7_stone_travertine", "t7_drywall_base_cream", "t7_drywall_painted_white_01", "t7_metal_panels_painted_2x1_grey",
    "core_tile_light", "t7_ceramic_tiles_16x16", "t7_ceramic_tile_shower_white", "t7_ceramic_tile_large_white",
    "t7_wood_veneer_sugarpine_matte", "t7_metal_floor_square_pattern_01", "t7_linoleum_floor_tile_square", "t7_concrete_poured_bunker_paint_01_grey_lt",
]

# echelles de reference affichees dans le document
REF_ECHELLES = [
    "t7_plaster_smooth_light_01", "t7_plaster_rough_worn_01_wet", "t7_concrete_wall_weathered_01_wet", "t7_concrete_bare_dark_01_wet",
    "t7_brick_worn_dirty_red_wet", "t7_brick_worn_heavy_grout_red", "t7_asphalt_dirty_dark_desert", "t7_asphalt_advanced_strips",
    "t7_concrete_sidewalk_02", "t7_concrete_sidewalk_2x2_01", "t7_concrete_trim_beveled_01_wet", "t7_street_concrete_curb_01a",
    "t7_wood_panel_01_stain_brown_drk", "t7_wood_trim_dark_brown", "t7_metal_paint_worn_white", "t7_metal_planter_top_trim",
    "t7_glass_plain_opaque", "t7_stone_pebbles_01",
]

SILHOUETTES = [
    "veh_t7_civ_car_compact_grey", "veh_t7_civ_city_car_vista", "p7_light_metal_circle_pole", "p7_zm_der2_utility_pole_512",
    "p7_foliage_tree_albizia_tall_full", "p7_foliage_hedge_box_128_48_36", "p7_zm_der_dumpster_metal_large", "p7_trashcan_metal_modern_paper",
    "p7_civ_sat_dish", "p7_ac_unit_wall_mount_01", "p7_door_metal_rolling_02", "p7_louver_window_wooden_closed",
    "p7_cai_planter_square", "p7_bench_modern_01", "p7_sin_bollard_tall_painted", "p7_barricade_metal_gate_02",
    "p7_foliage_tree_olive_small", "p7_street_curb_concrete_64a",
]

MODELES_PROJET = [
    "veh_t7_civ_car_compact_grey", "veh_t7_civ_car_compact_blue", "veh_t7_civ_car_compact_black", "veh_t7_civ_car_compact_green",
    "p7_bench_modern_01", "p7_foliage_tree_albizia_tall_full", "p7_foliage_hedge_round_48_48_36_vibrant",
    "p7_foliage_grass_tussock_green_1", "p7_foliage_grass_tussock_green_2", "p7_foliage_grass_tussock_green_3", "p7_foliage_grass_flowers",
]

PRIORITES = [
    "Corriger l'échelle de projection des textures (make_blockout.py) : au lieu de `256 256` partout, utiliser par matériau la valeur du stock ×1,25 en gardant les proportions de l'image "
    "(colonne « Échelle .map » des tableaux). C'est le gain de réalisme le plus important et le moins cher.",
    "Remplacer dans `MAT` : asphalte (core_asphault_dark), facade_blanche, garages et balcon (t7_plaster_smooth_light_01), voisin_toit (core_roof_light), volet (t7_metal_wall_corrugated_panel_hor_grey), "
    "ecole et socle (versions sèches), cabine_sol (t7_linoleum_floor_tile_square) ; voir le tableau du §9.",
    "Créer un petit GDT d'instances teintées (§10) pour le beige du bâtiment 1, le brun des toits et le crème des halls : c'est la seule façon d'obtenir ces teintes avec de vraies textures.",
    "Poser les modèles à `modelscale 1.25` (voitures, banc, haies, arbres) pour rester proportionnés aux immeubles.",
    "Utiliser les modèles trouvés pour les détails de façade et d'abords : tuyaux de descente p7_pipe_pvc_drain_*, persiennes p7_louver_window_wooden_closed, rideau roulant p7_door_metal_rolling_02, "
    "bordures p7_street_curb_concrete_64a/b, bacs de tri p7_trashcan_metal_modern_*, paraboles p7_civ_sat_dish, climatiseurs p7_ac_unit_wall_mount_01, haies p7_foliage_hedge_*.",
    "Garder des brushes pour ce qui n'existe pas : peupliers et sapins, lampadaires, panneaux routiers, boîtes aux lettres, souches de cheminée, jeux d'enfants, barreaudage des balcons.",
    "Vérifier en jeu avant de généraliser : décalques de marquage routier, grillages à alpha, verres (t7_glass_*), instances teintées.",
]

# ---------------------------------------------------------------------------------------------------
BESOINS = [
    # ===================================================================== FACADES ET MURS
    {"id": "crepi_beige", "famille": "Façades et murs", "titre": "Crépi / enduit beige (façade du bâtiment 1)",
     "mat_projet": ["facade_beige"],
     "resume": "Aucun matériau officiel n'est un enduit beige clair lisse. Le plus proche en teinte est t7_plaster_rough_worn_01, mais il est moucheté et écaillé. "
               "Pour la façade est du bâtiment 1 (fiche : « enduit beige clair »), la solution propre est une instance teintée de t7_plaster_smooth_light_01 (§10) ; "
               "en attendant, core_plaster_light donne un beige crème lisse, mais en 512 px.",
     "candidats": [
         C("core_plaster_light", REC, 3, "Vu : beige crème lisse, grain fin de crépi, se raccorde bien ; le plus beige utilisable tout de suite, sans GDT. Défaut : 512 px, soit quatre fois moins défini que les t7_. "
           "Déduit : le drapeau doNotUse est un héritage, ces core_* sont déjà compilés dans zm_seyssel.", "Définition faible de près ; beige très discret."),
         C("t7_plaster_smooth_light_01", ALT, 3, "Vu : gris très clair, à peine chaud, très uniforme, aucun motif répétitif ; c'est l'actuel « beige » du bâtiment 1 et il rend gris-blanc. "
           "Excellent support pour une instance teintée (même image, même relief ; §10).", "Pas beige en l'état."),
         C("t7_plaster_rough_worn_01", ALT, 3, "Vu : beige chaud à reflets orangés, crépi grossier vieilli avec de larges plages claires et foncées. Convient à un pavillon ancien, "
           "trop abîmé pour un immeuble entretenu. Déduit : les grandes plages se répètent à l'œil sur de grandes surfaces (visible dès 2 × 2).",
           "La variante _wet multiplie la teinte par 0,8 et ajoute un aspect mouillé (déduit) : à éviter par temps sec."),
         C("t7_plaster_smooth_dirty_01_light_brown", LIM, 2, "Vu : gris-brun sali, taches sombres qui se répètent nettement. Trop sombre et sale pour un beige clair ; "
           "utile pour un soubassement ou un mur de garage vieilli."),
         C("t7_drywall_painted_beige_01", LIM, 2, "Vu : kaki-gris plat, sans relief, 1024 px, usage « interior wall » (cloison). Trop foncé et verdâtre pour du beige clair dehors ; correct dans un hall."),
         C("core_concrete_light_warm", LIM, 2, "Vu : béton gravillonné beige-sable. Ce n'est pas un enduit lisse (cailloutis visibles), mais il convient à une dalle ou un muret chaud."),
         C("t7_drywall_base_cream", EVI, 1, "Vu : malgré son nom, la colorMap est un gris neutre ; la variante _cream_orange n'est qu'une teinte orange multipliée dessus. "
           "Ne pas compter sur lui pour du crème (il sert aujourd'hui de « hall_mur »). Inconnu : rendu en jeu."),
     ]},
    {"id": "crepi_blanc", "famille": "Façades et murs", "titre": "Enduit blanc cassé (bâtiments 2 et 3)",
     "mat_projet": ["facade_blanche", "garages", "balcon"],
     "resume": "t7_plaster_smooth_light_01 est le meilleur blanc cassé disponible (uniforme, sans répétition visible, 2048 px). Le matériau actuel (t7_concrete_worn_painted_white) "
               "tire sur le gris-vert terne et paraît sale à côté d'un beige.",
     "candidats": [
         C("t7_plaster_smooth_light_01", REC, 4, "Vu : gris très clair quasi uniforme, aucun motif répétitif, se raccorde proprement. Déduit : sous le soleil de la map il se lit « blanc cassé ». "
           "Stock .map : 128 × 128."),
         C("t7_drywall_painted_white_01", ALT, 3, "Vu : blanc cassé plat (écart-type de luminance voisin de 1), 1024 px, usage cloison : propre mais sans grain ; peut paraître plastique sur une façade."),
         C("t7_plastic_base_clean", LIM, 2, "Vu : blanc franc, 1024 px, sans relief ; spéculaire de plastique (PVC). Pour des menuiseries, pas pour un mur."),
         C("t7_metal_painted_wall_dirty_grey", LIM, 2, "Vu : blanc uni malgré son nom « grey », 1024 px, matériau métal. Pour un cadre ou un panneau blanc."),
         C("t7_concrete_worn_painted_white", EVI, 2, "Vu : gris-vert terne tacheté, 1024 px ; ne se lit pas comme blanc. C'est l'actuel « facade_blanche »."),
         C("t7_concrete_painted_white_blend", EVI, 1, "Vu dans le GDT : type lit_decal_diffuse_reveal, tri « blend / additive », catégorie Decal. C'est un matériau de fusion pour décalques ou terrain ; "
           "inconnu : comportement sur un brush.", "Matériau de fusion, non testé sur brush."),
     ]},
    {"id": "crepi_pavillon", "famille": "Façades et murs", "titre": "Crépi des pavillons voisins",
     "mat_projet": ["voisin"],
     "resume": "Les pavillons des alentours sont aujourd'hui en t7_plaster_rough_worn_01 projeté en 256 × 256. La texture convient (beige chaud, crépi grossier) mais ses grandes plages se répètent : "
               "réduire l'échelle à 128 et alterner avec une seconde teinte pour casser la répétition d'une maison à l'autre.",
     "candidats": [
         C("t7_plaster_rough_worn_01", REC, 3, "Vu : beige chaud, crépi grossier vieilli ; stock .map (variante _wet) : 128 × 128. Alterner avec une instance teintée pour varier les maisons."),
         C("t7_plaster_smooth_dirty_01_light_brown", ALT, 2, "Vu : gris-brun sali, taches sombres. Donne un second ton de crépi, mais répétition très visible."),
         C("core_plaster_light", ALT, 3, "Vu : beige crème lisse 512 px ; pour des pavillons récents au crépi propre."),
         C("t7_plaster_smooth_light_01", ALT, 3, "Vu : gris clair uniforme ; base d'instances teintées (rose pâle, jaune pâle, ocre) pour varier les maisons sans répétition visible."),
         C("t7_concrete_floor_sealed_01_warm", LIM, 2, "Vu : brun-ocre foncé marbré (teinte 0,72 / 0,62 / 0,47 sur béton) ; pour un mur de soutènement ou un garage, pas un crépi."),
         C("t7_drywall_painted_beige_01", LIM, 2, "Vu : kaki plat ; correct pour un intérieur de pavillon."),
     ]},
    {"id": "beton_brut", "famille": "Façades et murs", "titre": "Béton brut",
     "mat_projet": ["dalle_balcon", "dalle", "gaine", "ecole"],
     "resume": "Le béton brut officiel est abondant et réaliste. Pour du sec : t7_concrete_bare_weathered_01 ou t7_concrete_floor_sealed_01 (même image que wall_weathered, sans la variante _wet). "
               "L'actuel « ecole » (t7_concrete_wall_weathered_01_wet) prend un aspect mouillé.",
     "candidats": [
         C("t7_concrete_bare_weathered_01", REC, 4, "Vu : gris clair granuleux, taches douces, pas de motif répétitif gênant, 2048 px. Stock .map : 64 ou 128 unités. Existe en _dark (teinte × 0,45) et _wet."),
         C("t7_concrete_floor_sealed_01", REC, 3, "Vu : mêmes taches marbrées que concrete_wall_weathered_01 (même image), sans l'aspect mouillé ; type lit_detail avec carte de détail. C'est l'actuel « dalle » et « gaine »."),
         C("core_concrete_light", ALT, 3, "Vu : béton clair à pores et gravillons, très réaliste, mais 512 px seulement."),
         C("t7_concrete_bare_dark_01", ALT, 3, "Vu : gris moyen sombre, uniforme ; bon pour soubassements et murs de soutènement. Stock : 128 × 128 (surtout la variante _wet)."),
         C("t7_concrete_wall_poured_thick_01", LIM, 3, "Vu : béton banché avec joints verticaux de coffrage (effet bunker). Le raccord gauche-droite est douteux (écart de bord 30 contre 9 entre colonnes voisines) : tester avant d'étendre.",
           "Raccord horizontal douteux."),
         C("t7_concrete_brushed_01", LIM, 2, "Vu : gris tiède très bruité, aspect balayé, peu de relief grand format."),
     ]},
    {"id": "beton_peint", "famille": "Façades et murs", "titre": "Béton peint",
     "mat_projet": ["annexe", "garages"],
     "resume": "Il n'existe pas de « peinture sur béton » propre en matériau de brush. Deux pistes : le micro-matériau t7_concrete_poured_bunker_paint_01_grey_lt (actuel de l'annexe) ou un enduit lisse "
               "(t7_plaster_smooth_light_01). Les variantes *_painted_*_blend sont des matériaux de fusion.",
     "candidats": [
         C("t7_concrete_poured_bunker_paint_01_grey_lt", ALT, 3, "Vu : gris-beige très uni avec micro-grain ; type lit_micro_tile_blend (image micro 1024 px, tuilée finement). Stock : 128 × 128. La variante _blue_lt existe."),
         C("t7_plaster_smooth_light_01", REC, 3, "Vu : gris clair uniforme ; un enduit peint se lit comme du béton peint à distance."),
         C("t7_concrete_worn_painted_white", EVI, 2, "Vu : gris-vert terne ; actuel « garages ». Stock : 64 × 64."),
         C("t7_concrete_painted_grey_blend", EVI, 1, "Vu dans le GDT : type lit_decal_diffuse_reveal, catégorie Decal ; gris par teinte 0,45. Matériau de fusion, non testé sur brush.", "Matériau de fusion."),
     ]},
    {"id": "soubassement", "famille": "Façades et murs", "titre": "Soubassement",
     "mat_projet": ["socle"],
     "resume": "Le socle actuel utilise la version _wet de la brique brune (aspect mouillé, déduit de sa carte de normales « wet » et de glossRangeMax 11). Plus neutre pour un soubassement d'immeuble : "
               "béton gris foncé ou la même brique en version sèche.",
     "candidats": [
         C("t7_concrete_bare_dark_01", REC, 3, "Vu : gris moyen sombre, uniforme, discret. Déduit : bon soubassement sous un enduit clair."),
         C("t7_brick_worn_heavy_grout_brown", ALT, 3, "Vu : brique brun-gris à gros joints clairs, 2048 px ; même image que le socle actuel sans le gloss mouillé."),
         C("t7_concrete_wall_blocks_wet", LIM, 2, "Vu : parpaings gris bleutés, 1024 px ; aspect mouillé déduit du nom et de la carte de normales."),
         C("core_concrete_cinderblocks", LIM, 2, "Vu : parpaings gris-bleu avec mousse, 512 px ; plutôt un aspect de ruine."),
         C("t7_concrete_floor_trim_01", LIM, 3, "Vu : bande 1024 × 128 (rapport 8:1) de plinthe béton ; stock : 32 × 4. À utiliser en liseré, pas en surface."),
         C("t7_concrete_trim_edge_damaged_01", LIM, 2, "Vu : bande 2048 × 256, bord de béton abîmé ; stock : 64 × 8. Pour un angle ou un nez de marche."),
     ]},
    {"id": "brique", "famille": "Façades et murs", "titre": "Brique",
     "mat_projet": [],
     "resume": "La brique est le point fort de la bibliothèque (16 matériaux t7_ et 3 core_). Brique rouge propre : t7_brick_worn_red ; plus sombre : t7_brick_worn_dirty_red ; ocre : t7_brick_worn_dirty_tan.",
     "candidats": [
         C("t7_brick_worn_red", REC, 4, "Vu : brique rouge-rosé régulière, joints fins clairs, peu de défauts ; 2048 px. La meilleure brique « propre » et le meilleur raccord de la série."),
         C("t7_brick_worn_dirty_red", ALT, 3, "Vu : brique rouge sombre patinée, contraste marqué ; 2048 px. Stock : 64 × 64."),
         C("t7_brick_worn_heavy_grout_red", ALT, 3, "Vu : briques rouges à gros joints clairs et taches de salpêtre ; 1024 px. Stock : 64 × 64."),
         C("t7_brick_worn_dirty_tan", ALT, 3, "Vu : brique ocre-brun (même motif que dirty_red avec une autre teinte)."),
         C("t7_brick_worn_heavy_grout_brown", ALT, 3, "Vu : brique brun-gris à gros joints ; stock (variante _wet) : 64 × 64."),
         C("core_brick_light", LIM, 2, "Vu : brique rouge-orangé 512 px au motif régulier ; raccord vertical un peu visible."),
     ]},
    # ===================================================================== TOITURE ET BOIS
    {"id": "toit_brun", "famille": "Toiture, bois et boiseries", "titre": "Tuiles / ardoise brun foncé (toit des immeubles)",
     "mat_projet": ["toit"],
     "resume": "Aucune tuile brun foncé n'existe. core_roof_dark est une vraie ardoise (gris-bleu), core_roof_light une tuile mécanique orange. La solution propre est une instance teintée de core_roof_light (§10) ; "
               "sinon garder core_roof_dark.",
     "candidats": [
         C("core_roof_dark", REC, 3, "Vu : ardoises rectangulaires gris-bleu foncé, joints ombrés, 512 px, belle définition, motif régulier sans raccord gênant. Pas brun (gris-violet). Utilisé aujourd'hui."),
         C("core_roof_light", ALT, 4, "Vu : tuiles mécaniques rose-orangé avec traces de mousse, 512 px, très réaliste. Teinte à assombrir par une instance pour obtenir le brun foncé."),
         C("core_roof_med", LIM, 2, "Vu : bardeaux brun-rouge mais 64 × 64 px : flou dès qu'on s'approche.", "64 px."),
         C("t7_rubber_roof_granular", LIM, 2, "Vu : membrane granuleuse brun-gris foncé, usage « roof » ; se lit comme bitume de loin, pas comme tuile."),
         C("t7_stone_slate_tile_grey", LIM, 2, "Vu : dalles d'ardoise gris foncé en appareil, 1024 px, mais raccord vertical visible (bord 42 contre 13) ; usage « floor ».", "Raccord douteux."),
         C("t7_metal_wall_corrugated_hor_brown_drk", LIM, 2, "Vu : lames horizontales brun très foncé (bac acier brun) ; à réserver aux panneaux/volets bruns plutôt qu'à un toit de tuiles."),
     ]},
    {"id": "tuiles_pavillon", "famille": "Toiture, bois et boiseries", "titre": "Tuiles rouge-brun (pavillons)",
     "mat_projet": ["voisin_toit"],
     "resume": "core_roof_light est la bonne tuile (orange-rosé, 512 px). L'actuel core_roof_med est en 64 px.",
     "candidats": [
         C("core_roof_light", REC, 4, "Vu : tuiles mécaniques rose-orangé avec mousse, 512 px ; pour un rouge-brun plus sombre, instance teintée (§10)."),
         C("core_roof_med", LIM, 2, "Vu : bardeaux brun-rouge en 64 × 64 px (actuel « voisin_toit ») : trop flou.", "64 px."),
         C("core_roof_dark", ALT, 3, "Vu : ardoise gris-bleu ; pour des pavillons à toit d'ardoise."),
         C("t7_ceramic_tiles_6x6_dirty_tan", EVI, 1, "Vu : carreaux de sol (grille de petits carrés) brun-ocre ; ce ne sont pas des tuiles."),
     ]},
    {"id": "rive_bois", "famille": "Toiture, bois et boiseries", "titre": "Rive, bardage et panneaux de bois bruns",
     "mat_projet": ["rive", "panneau", "ecorce"],
     "resume": "Rive et chevrons : bandes 1024 × 64 (t7_wood_trim_dark_brown). Panneaux bruns horizontaux « type persiennes » de la fiche : bardage t7_metal_wall_corrugated_hor_brown_drk ou le bois "
               "t7_wood_panel_01_stain_brown_drk (matériau le plus employé des .map officiels).",
     "candidats": [
         C("t7_wood_trim_dark_brown", REC, 4, "Vu : bande brun foncé 16:1, veinage fin. Stock : 64 × 4."),
         C("t7_wood_panel_01_stain_brown_drk", REC, 4, "Vu : brun chocolat très foncé uni, fil vertical fin, 2048 px ; stock : 64 × 64, c'est le matériau le plus utilisé des maps officielles. "
           "Déduit : une rotation de projection de 90° donnerait des panneaux horizontaux."),
         C("t7_metal_wall_corrugated_hor_brown_drk", REC, 3, "Vu : lames horizontales brun foncé, légères rayures ; stock : 64 × 64. Rend bien les « panneaux bruns horizontaux » de la fiche."),
         C("t7_wood_trim_brown_01", ALT, 3, "Vu : bande 1024 × 128 plus large et plus claire ; stock : 64 × 8."),
         C("t7_wood_worn_darker_brown", ALT, 3, "Vu : brun foncé uni à peine vieilli."),
         C("t7_wood_planks_rustic", LIM, 2, "Vu : planches grisâtres très vieillies, aspect cabane ; stock : 64 × 64."),
         C("t7_wood_beam_worn_oak", LIM, 2, "Vu : poutre étroite 256 × 1024 brun roux. Utilisé comme « écorce » : ce n'est pas une écorce, juste un bois."),
     ]},
    # ===================================================================== OUVERTURES
    {"id": "menuiserie_blanche", "famille": "Ouvertures et volets", "titre": "Menuiseries de fenêtre blanches",
     "mat_projet": ["fenetre"],
     "resume": "PVC blanc : t7_plastic_base_clean. L'actuel core_window_opaque est une fenêtre complète (cadre blanc à petits bois et vitrage) en 512 px : pratique sur une seule face, mais ni modulaire ni haute définition.",
     "candidats": [
         C("t7_plastic_base_clean", REC, 4, "Vu : blanc franc, 1024 px, sans relief ; existe aussi en gris et noir. À utiliser pour des cadres construits en brushes autour d'une vitre."),
         C("core_window_opaque", ALT, 3, "Vu : cadre blanc à petits bois et vitre gris sombre, quatre fenêtres par tuile, 512 px. Exige que chaque face de fenêtre ait la bonne taille de projection. Actuel « fenetre »."),
         C("t7_plastic_molding_trim_white", LIM, 3, "Vu : profilé blanc 1024 × 256 ; pour un encadrement ou un appui."),
         C("t7_metal_painted_wall_dirty_grey", ALT, 2, "Vu : blanc uni (nom trompeur)."),
         C("t7_metal_painted_clean_white", LIM, 2, "Vu : gris clair seulement (teinte 0,7) ; actuel « boites »."),
         C("t7_wood_varnished_clean_white", EVI, 1, "Vu : gris, pas blanc."),
     ]},
    {"id": "menuiserie_brune", "famille": "Ouvertures et volets", "titre": "Menuiseries brunes (portes, loggias)",
     "mat_projet": ["loggia", "porte"],
     "resume": "Bruns disponibles : bois très foncé (t7_wood_panel_01_stain_brown_drk), brun vieilli (t7_wood_worn_darker_brown) et peinture brun olive (t7_drywall_painted_brown_01, actuel des loggias).",
     "candidats": [
         C("t7_wood_panel_01_stain_brown_drk", REC, 4, "Vu : brun chocolat très foncé, uni et propre."),
         C("t7_wood_worn_darker_brown", ALT, 3, "Vu : brun foncé légèrement vieilli, 1024 px."),
         C("t7_drywall_painted_brown_01", ALT, 3, "Vu : brun olive uni, 1024 px, type cloison. Actuel « loggia » ; plat mais propre."),
         C("core_door_wood_dark", ALT, 3, "Vu : porte à panneaux moulurés en bois sombre, 256 × 512 px ; actuel « porte » (la texture est une porte entière, pas un bois)."),
         C("t7_wood_trim_dark_brown", LIM, 3, "Vu : bande 16:1 pour liserés et chambranles."),
         C("t7_metal_wall_corrugated_hor_brown_drk", ALT, 3, "Vu : lames horizontales brunes ; pour volets ou panneaux."),
     ]},
    {"id": "vitrage", "famille": "Ouvertures et volets", "titre": "Vitrage",
     "mat_projet": ["vitre"],
     "resume": "Types de verre du moteur : glass, lit_transparent_backlit, glass_nocolor. Leur rendu (reflets, transparence) n'est pas vérifiable sans lancer le jeu ; l'actuel core_glass_plain_trans est déjà compilé.",
     "candidats": [
         C("t7_glass_clean_01_transparent", REC, 3, "Vu dans le GDT : type glass, alpha uniforme 127 (50 %), teinte 0,16 : le verre propre moderne de Treyarch (usage « window »). Inconnu : intensité des reflets sur un panneau plat."),
         C("core_glass_plain_trans", ALT, 3, "Vu : type glass, alpha uniforme faible (19 à 42), 256 px ; déjà compilé dans zm_seyssel. Actuel « vitre »."),
         C("t7_glass_dirty_streaks", ALT, 3, "Vu : verre avec traînées de poussière, 2048 px, alpha 66 à 111 (glass_nocolor) ; apporte du réalisme aux vitres de cage d'escalier."),
         C("t7_glass_frosted_cold", ALT, 3, "Vu : verre dépoli froid, 1024 px, alpha 39 à 175 ; pour portes de halls, salles de bain, imposte."),
         C("t7_glass_reinforced_01", ALT, 3, "Vu : verre armé turquoise à motif de losanges, alpha 115 à 237. Déduit : ressemble aux vitres de cages d'escalier d'HLM."),
         C("t7_glass_plain_translucent", LIM, 2, "Vu : type lit_transparent_backlit, image quasi noire, alpha très bas : vitre sombre."),
         C("t7_glass_smoked", LIM, 2, "Vu : verre fumé presque noir ; pour vitrines ou portes de garage vitrées."),
     ]},
    {"id": "volets_persiennes", "famille": "Ouvertures et volets", "titre": "Volets roulants et persiennes",
     "mat_projet": ["volet"],
     "resume": "Pas de volet roulant en texture « toute faite », mais plusieurs bardages à lames horizontales : t7_metal_wall_corrugated_panel_hor_grey (gris), t7_metal_wall_corrugated_hor (blanc cassé), "
               "t7_metal_wall_corrugated_hor_brown_drk (brun). Pour de vraies persiennes à lames : le modèle p7_louver_window_wooden_closed (§7).",
     "candidats": [
         C("t7_metal_wall_corrugated_panel_hor_grey", REC, 3, "Vu : lames horizontales gris bleuté nettes, 2048 px ; stock : 64 × 64. Se lit comme un volet roulant fermé."),
         C("t7_metal_wall_corrugated_hor", ALT, 3, "Vu : lames horizontales blanc cassé légèrement sales, 2048 px ; volet roulant blanc."),
         C("t7_metal_wall_corrugated_hor_brown_drk", ALT, 3, "Vu : lames horizontales brun foncé ; volets bruns."),
         C("t7_metal_panel_horizontal_painted", LIM, 2, "Vu : panneaux peints blanc-beige avec coulures de rouille, 2048 × 1024 ; effet vieux bardage."),
         C("t7_cloth_blinds_striped_01", LIM, 2, "Vu : stores en tissu rayé brun et gris ; type lit_transparent_nocull (alpha 100 à 254). Ressemble à un store intérieur, pas à un volet."),
         C("t7_glass_slats", EVI, 1, "Vu : lames turquoise (teinte 0,05 / 0,28 / 0,36) de type lit_backlit : verre à lamelles, pas un volet."),
     ]},
    # ===================================================================== BALCONS
    {"id": "garde_corps_ajoure", "famille": "Balcons et garde-corps", "titre": "Garde-corps métal peint : barreaudage",
     "mat_projet": ["garde_corps"],
     "resume": "Aucune texture de barreaux verticaux n'existe. Pour un vrai barreaudage : brushes fins (comme dans immeuble.py) avec un métal peint uni. "
               "Pour un garde-corps ajouré à moindre coût : les cartes à alpha (câbles en losanges, métal déployé, tôle perforée), dont le canal alpha est bien présent (mesuré).",
     "candidats": [
         C("t7_metal_paint_worn_grey_dk", REC, 3, "Vu : gris anthracite uni peint, grain très fin ; pour barreaux et main courante en brushes. Actuel « auvent »."),
         C("t7_metal_worn_iron_dark", ALT, 3, "Vu : colorMap noire uniforme avec micro-textures (lit_micro_tile_blend_advanced) : aspect fer brut plutôt que peint. Stock : 64 × 64. Actuel « garde_corps »."),
         C("t7_metal_fence_post_cable", ALT, 2, "Vu : treillis de câbles en losanges sur fond transparent (alpha : environ 80 % transparent), 1024 px ; type lit_alphatest. Inconnu : visible des deux côtés ou non."),
         C("t7_metal_grating_expanded", ALT, 2, "Vu : métal déployé, environ 53 % transparent, 1024 px ; garde-corps ajouré industriel."),
         C("t7_metal_perforated_small_white", ALT, 2, "Vu : tôle perforée blanche, environ 23 % transparente ; allège perforée."),
         C("t7_metal_painted_wall_dirty_black", ALT, 2, "Vu : noir uni très propre (teinte 0,19) ; main courante noire."),
     ]},
    {"id": "garde_corps_plein", "famille": "Balcons et garde-corps", "titre": "Garde-corps métal peint : allège pleine",
     "mat_projet": ["garde_corps"],
     "resume": "Allège pleine en tôle peinte : panneaux gris (t7_metal_panels_painted_2x1_grey) ou graphite uni. Les teintes gris moyen vont bien avec un enduit beige.",
     "candidats": [
         C("t7_metal_panels_painted_2x1_grey", REC, 3, "Vu : panneaux de tôle peinte gris, joints fins nets, 2048 px ; stock : 128 × 128."),
         C("t7_metal_panel_horizontal_painted_grey", ALT, 3, "Vu : panneaux horizontaux gris-vert avec légères coulures, 2048 × 1024 px."),
         C("t7_metal_worn_painted_graphite", ALT, 3, "Vu : graphite très uni, quasi sans grain ; allège sombre. Stock (variante t7_metal_worn_painted_white) : 64 × 64."),
         C("t7_metal_panels_4x1_grey_drk", ALT, 3, "Vu : gris foncé bleuté uni, joints à peine visibles ; stock : 128 × 128."),
         C("t7_metal_panels_painted_2x4", ALT, 2, "Vu : panneaux blancs striés 2 × 4 ; allège blanche. Stock : 128 × 128."),
         C("t7_metal_painted_wall_dirty_grey", LIM, 2, "Vu : blanc uni, sans joint."),
     ]},
    {"id": "dalle_balcon", "famille": "Balcons et garde-corps", "titre": "Dalle et nez de balcon",
     "mat_projet": ["dalle_balcon", "balcon", "appui"],
     "resume": "Dessus de dalle : béton brut sec ; tranche : bande chanfreinée 4:1 (t7_concrete_trim_beveled_03) ou plinthe 8:1 (t7_concrete_floor_trim_01) en respectant leurs proportions.",
     "candidats": [
         C("t7_concrete_bare_weathered_01", REC, 3, "Vu : béton gris clair granuleux, sans motif répétitif gênant."),
         C("t7_concrete_floor_sealed_01", ALT, 3, "Vu : béton marbré, version sèche ; actuel « dalle_balcon »."),
         C("t7_concrete_trim_beveled_03", REC, 3, "Vu : tranche chanfreinée 1024 × 256 ; stock : 128 × 32 ou 64 × 16. Actuel « appui »."),
         C("t7_concrete_floor_trim_01", ALT, 3, "Vu : plinthe 1024 × 128, rapport 8:1 ; stock : 32 × 4 ou 112 × 14."),
         C("t7_concrete_slabs_interlocked", LIM, 2, "Vu : dalles de béton emboîtées gris clair ; plutôt un sol extérieur."),
         C("t7_concrete_brushed_01", LIM, 2, "Vu : béton balayé très bruité ; aspect de terrasse."),
     ]},
    # ===================================================================== HALLS ET PORTES
    {"id": "porte_vitree_hall", "famille": "Halls, portes et boîtes", "titre": "Porte vitrée de hall",
     "mat_projet": ["vitre", "porte", "auvent"],
     "resume": "Il n'existe pas de « porte vitrée » toute faite. Assemblage conseillé : cadre métal (alu brossé ou peint) + vitre transparente, en brushes. Les modèles de portes disponibles sont industriels ou de laboratoire (§7).",
     "candidats": [
         C("t7_glass_clean_01_transparent", REC, 3, "Vu dans le GDT : verre propre transparent (alpha 127) ; pour la vitre."),
         C("t7_metal_bare_aluminum_brushed", REC, 3, "Vu dans le GDT : aluminium brossé, type lit_advanced sans colorMap (la couleur vient du spéculaire, non mesuré) ; pour les montants."),
         C("t7_metal_trim_painted_black", ALT, 3, "Vu dans le GDT : peinture noire (teinte 0,27 sur une image grise uniforme) ; cadre noir."),
         C("t7_plastic_base_clean", ALT, 3, "Vu : blanc franc ; cadre PVC blanc."),
         C("t7_metal_frame_trim_01", LIM, 2, "Vu : profilé foncé 1024 × 64 à rivets, usage « window » ; stock : 64 × 4."),
         C("t7_glass_frosted_cold", ALT, 3, "Vu : verre dépoli ; pour un panneau latéral ou une imposte."),
     ]},
    {"id": "portes_garage", "famille": "Halls, portes et boîtes", "titre": "Portes de garage",
     "mat_projet": ["garage"],
     "resume": "Le « garage » actuel (core_door_metal_light) est un métal nu clair sans image de couleur ni panneaux. Pour des portes basculantes peintes : panneaux gris ou blancs. Pour un rideau roulant : modèle p7_door_metal_rolling_02.",
     "candidats": [
         C("t7_metal_panel_horizontal_painted_grey", REC, 3, "Vu : panneaux horizontaux gris-vert, 2048 × 1024 px ; lit comme une porte de garage basculante."),
         C("t7_metal_panels_painted_2x4", ALT, 3, "Vu : panneaux blancs striés 2 × 4 ; porte de garage blanche. Stock : 128 × 128."),
         C("core_door_metal_dark", ALT, 3, "Vu : porte métallique grise avec cadre et panneau, 256 × 512 px ; basse définition."),
         C("t7_metal_garage_door_rollup_01_bare", ALT, 2, "Vu dans le GDT : rideau métallique à normales rainurées, micro-matériau sans colorMap ; stock (variante _wet) : 64 × 64."),
         C("core_door_metal_light", LIM, 2, "Vu dans le GDT : lit_advanced sans colorMap, couleur portée par le spéculaire : métal nu clair sans panneaux. Actuel « garage »."),
         C("t7_metal_paint_worn_grey_dk", LIM, 2, "Vu : gris anthracite uni ; porte sombre sans détail."),
     ]},
    {"id": "boites_lettres", "famille": "Halls, portes et boîtes", "titre": "Boîtes aux lettres",
     "mat_projet": ["boites"],
     "resume": "Ni modèle ni texture de boîtes aux lettres n'existent. Construire un bloc de boîtes en brushes (comme dans immeuble.py) avec un métal peint : alu brossé, jaune ou gris.",
     "candidats": [
         C("t7_metal_bare_aluminum_brushed", REC, 3, "Vu dans le GDT : aluminium brossé (type lit_advanced) ; boîtes aux lettres en alu."),
         C("t7_metal_paint_worn_yellow", ALT, 3, "Vu : jaune moutarde uni légèrement usé ; boîtes jaunes."),
         C("t7_metal_painted_clean_white", ALT, 2, "Vu : gris clair uni ; actuel « boites »."),
         C("t7_metal_panels_painted_2x1_yellow", LIM, 2, "Vu : panneaux jaunes à joints ; trop industriel."),
     ]},
    # ===================================================================== VOIRIE
    {"id": "asphalte_neuf", "famille": "Voirie et sols urbains", "titre": "Asphalte neuf",
     "mat_projet": ["asphalte"],
     "resume": "L'actuel t7_asphalt_dirty_dark_desert est un asphalte « désert » à plages brun-ocre marquées, peu alpin et répétitif. core_asphault_dark (sic, l'orthographe d'origine) est un enrobé sombre fin, plus neutre.",
     "candidats": [
         C("core_asphault_dark", REC, 4, "Vu : gris anthracite fin, pores minuscules, 512 px ; ressemble à un enrobé récent. Variante _wet existe. Le nom contient bien la faute « asphault »."),
         C("t7_asphalt_advanced_strips", ALT, 3, "Vu : très sombre avec une grille de bandes de reprise, 2048 px ; stock : 128 × 128. Donne un enrobé neuf rapiécé."),
         C("t7_asphalt_bleached_desert", LIM, 2, "Vu : gris-beige clair délavé ; trop clair et chaud pour une rue."),
         C("core_asphault_light", LIM, 1, "Vu : 64 × 64 px, gris-bleu moucheté ; trop flou.", "64 px."),
         C("t7_asphalt_dirty_dark_desert", EVI, 2, "Vu : plages brun-ocre sur fond gris, 1024 px ; actuel « asphalte ». Stock : 64 × 64. Répétition lisible."),
     ]},
    {"id": "asphalte_use", "famille": "Voirie et sols urbains", "titre": "Asphalte usé",
     "mat_projet": [],
     "resume": "Pour un enrobé fissuré : t7_asphalt_damaged_dark_wet (fissures en peau de crocodile, 2048 px). Sa variante _nw est le même matériau avec un canal supplémentaire ($white_reveal).",
     "candidats": [
         C("t7_asphalt_damaged_dark_wet", REC, 4, "Vu : réseau de fissures sur fond noir-brun, 2048 px ; stock (variante _nw) : 128 × 128. Le nom contient « wet » : carte de normales mouillée (déduit)."),
         C("t7_asphalt_damaged_dark_wet_nw", ALT, 4, "Vu dans le GDT : instance du précédent qui ne change que colorMap14 ($white_reveal). Inconnu : ce que « nw » désigne."),
         C("core_asphault_med", ALT, 3, "Vu : gris-bleu à fissures fines, 512 px."),
         C("t7_concrete_floor_garage_cracked_wet_nw", ALT, 3, "Vu : béton fissuré de parking, 2048 px ; stock : 128 × 128. Pour un parking ou une allée de garages."),
         C("t7_asphalt_dirty_dark_desert", LIM, 2, "Vu : plages brun-ocre ; actuel « asphalte »."),
     ]},
    {"id": "marquages", "famille": "Voirie et sols urbains", "titre": "Marquages routiers blancs et jaunes",
     "mat_projet": [],
     "resume": "Les marquages existent comme décalques : t7_decal_signage_street_lines_white et _yellow (2048 × 256, ligne continue). Leur type lit_decal_reveal demande une carte de révélation (présente) et un brush « décalque ; "
               "le rendu n'est pas testé ici. Alternative sûre : bordures peintes (t7_street_concrete_curb_01a_white / _yellow).",
     "candidats": [
         C("t7_decal_signage_street_lines_white", ALT, 3, "Vu dans le GDT : lit_decal_reveal, couche « Signage - Old », usage « exterior trim ». Image 2048 × 256 de ligne continue sale. À tester sur un brush mince posé sur la route.", "Décalque non testé."),
         C("t7_decal_signage_street_lines_yellow", ALT, 3, "Vu dans le GDT : même image que le blanc avec une teinte jaune (0,83 / 0,68 / 0,23).", "Décalque non testé."),
         C("t7_street_concrete_curb_01a_yellow", ALT, 3, "Vu : bordure grise à bandes jaunes (marquage de stationnement interdit), 1024 × 256."),
         C("t7_street_concrete_curb_01a_white", ALT, 3, "Vu : bordure à bandes blanches, 1024 × 256."),
         C("t7_street_concrete_curb_01a_white_solid", LIM, 2, "Vu dans le GDT : bordure entièrement blanche."),
     ]},
    {"id": "trottoir", "famille": "Voirie et sols urbains", "titre": "Trottoir",
     "mat_projet": ["trottoir"],
     "resume": "t7_concrete_sidewalk_02 est un béton gris tiède uniforme, sans motif visible : le meilleur trottoir. Les variantes à joints (sidewalk_01, 2x2_01) donnent des dalles.",
     "candidats": [
         C("t7_concrete_sidewalk_02", REC, 4, "Vu : béton gris tiède fin, très uniforme, aucun motif répétitif ; stock : 64 × 64. Actuel « trottoir »."),
         C("t7_concrete_sidewalk_01", ALT, 3, "Vu : dalles carrées (4 × 4 par tuile) gris-beige à joints visibles ; stock : 64 × 64."),
         C("t7_concrete_sidewalk_2x2_01", ALT, 3, "Vu : dalles 2 × 2 gris clair à joints nets, 2048 px ; stock : 128 × 128."),
         C("t7_concrete_tiles_2x2_dirty_01", LIM, 2, "Vu : dalles gris sombre sales ; plutôt un parking."),
         C("t7_concrete_slabs_interlocked", LIM, 2, "Vu : dalles emboîtées gris clair ; sol de place."),
     ]},
    {"id": "bordure", "famille": "Voirie et sols urbains", "titre": "Bordure",
     "mat_projet": ["bordure"],
     "resume": "Le matériau actuel est le bon, mais il est étiré : 1024 × 256 mappé en 256 × 256. Le modèle p7_street_curb_concrete_64a/b (§7) donne une bordure déjà modélisée.",
     "candidats": [
         C("t7_street_concrete_curb_01a", REC, 4, "Vu : bordure grise avec arête et face, bande 1024 × 256 ; stock : 64 × 16. Actuel « bordure ». À mapper en 4:1."),
         C("t7_street_concrete_curb_01b", ALT, 3, "Vu : variante de teinte et de motif ; 1024 × 256."),
         C("t7_concrete_trim_beveled_01_wet", ALT, 3, "Vu dans le GDT : tranche chanfreinée 1024 × 256, la plus employée des maps officielles (64 × 16) ; variante mouillée."),
         C("t7_street_concrete_curb_01a_white", ALT, 3, "Vu : version peinte en blanc par bandes."),
         C("t7_street_concrete_curb_01a_yellow", ALT, 3, "Vu : version peinte en jaune par bandes."),
     ]},
    {"id": "paves", "famille": "Voirie et sols urbains", "titre": "Pavés et dalles",
     "mat_projet": [],
     "resume": "Pavés rectangulaires de ville : t7_stone_cobblestone_01_wet_nw (le seul pavé régulier). Les dalles emboîtées de béton font un « pavé autobloquant » acceptable pour un parking.",
     "candidats": [
         C("t7_stone_cobblestone_01_wet_nw", REC, 3, "Vu : pavés rectangulaires gris-brun-rose en appareil régulier, 2048 px ; bien raccordé. Le nom porte « wet » ; carte de normales mouillée (déduit)."),
         C("t7_concrete_slabs_interlocked", ALT, 3, "Vu : dalles béton emboîtées gris clair, 2048 px ; stock : 64 × 64. Pavage de parking."),
         C("t7_rock_cobblestone_round", ALT, 2, "Vu : galets/pavés ronds gris, 1024 px ; plutôt chemin rustique."),
         C("t7_concrete_tiles_4x4_dirty_01_grey", LIM, 2, "Vu : dalles 4 × 4 gris très sombre ; stock : 64 × 64."),
         C("t7_stone_flagstone_floor", LIM, 2, "Vu : dalles irrégulières brun-rouge, 2048 px ; terrasse, pas rue."),
     ]},
    # ===================================================================== SOLS NATURELS
    {"id": "herbe", "famille": "Sols naturels et végétation", "titre": "Herbe",
     "mat_projet": ["herbe", "herbe_sombre", "montagne", "feuillage", "feuillage_clair"],
     "resume": "core_grass_med est la pelouse la plus naturelle (vert moyen uniforme, aucune répétition visible). Les t7_grass_lawn_* sont très sombres. Pour casser l'uniformité : mêler des plaques de t7_grass_crab_low_sparse_green (herbe clairsemée avec terre).",
     "candidats": [
         C("core_grass_med", REC, 4, "Vu : pelouse vert moyen naturel, uniforme, aucun motif répétitif, 512 px. Actuel « herbe »."),
         C("core_grass_dark", ALT, 3, "Vu : herbe dense plus sombre à petites fleurs blanches, variation marquée mais acceptable ; actuel « herbe_sombre »."),
         C("t7_grass_crab_low_sparse_green", ALT, 3, "Vu : herbe rase clairsemée mêlée de terre brune, 2048 px ; réaliste pour des pelouses usées de quartier."),
         C("core_grass_light", LIM, 2, "Vu : vert bleuté désaturé, uni ; herbe fanée ou lointaine."),
         C("t7_grass_lawn_medium_small_green_vibrant", LIM, 2, "Vu : vert très sombre et saturé (teinte 0,67 / 0,82 / 0,41 sur une image déjà sombre). Pelouse de jeu vidéo plutôt que de quartier."),
     ]},
    {"id": "gravier", "famille": "Sols naturels et végétation", "titre": "Gravier",
     "mat_projet": ["gravier"],
     "resume": "t7_stone_pebbles_01 (actuel) est un gravillon gris-bleu très fin, sans répétition visible ; core_gravel_dark est plus naturel de près ; core_gravel_light montre des taches fantômes qui se répètent.",
     "candidats": [
         C("t7_stone_pebbles_01", REC, 4, "Vu : gravillon gris moucheté très uniforme, 2048 px ; stock : 64 × 64. Actuel « gravier »."),
         C("core_gravel_dark", ALT, 3, "Vu : gravier gris foncé naturel, 512 px, pas de motif visible."),
         C("core_gravel_light", ALT, 2, "Vu : gravier clair, mais des taches fantômes se répètent nettement dans une tuile 2 × 2.", "Répétition visible."),
         C("t7_stone_pebbles_01_warm", ALT, 3, "Vu : même image en teinte brun chaud (0,91 / 0,77 / 0,63) ; allées de terre-pierre."),
         C("t7_rock_sand_crumbled_medium", LIM, 2, "Vu : sable grossier beige à cailloux bruns, 2048 px ; chemin de terre."),
     ]},
    {"id": "terre", "famille": "Sols naturels et végétation", "titre": "Terre",
     "mat_projet": ["terre"],
     "resume": "core_dirt_med (actuel) est une terre brun chaud réaliste mais en 256 px ; core_dirt_light en 512 px est plus définie.",
     "candidats": [
         C("core_dirt_med", REC, 3, "Vu : terre brun chaud, grain fin, 256 px seulement."),
         C("core_dirt_light", ALT, 3, "Vu : terre claire rosée à petits cailloux, 512 px."),
         C("t7_dirt_grassy_forest_ground", ALT, 3, "Vu : terre sombre de sous-bois, 1024 px ; pied de haie ou massif."),
         C("t7_mud_ground_dirt_wet_01", LIM, 2, "Vu : boue brun sombre avec brindilles, aspect mouillé."),
         C("t7_sand_pebbles_fine", LIM, 2, "Vu : sable beige clair uni, 2048 px ; bac à sable ou chemin."),
         C("t7_dirt_rocky_01", LIM, 2, "Vu : terre rocailleuse beige floue, 2048 px, peu de détail."),
     ]},
    {"id": "haie", "famille": "Sols naturels et végétation", "titre": "Haies et rideaux d'arbres",
     "mat_projet": [],
     "resume": "Les haies existent en modèles (p7_foliage_hedge_*, §7). En texture : core_foliage_bushline (arbustes sur fond transparent) et core_foliage_treewall (rideau d'arbres), à poser verticalement.",
     "candidats": [
         C("core_foliage_bushline", ALT, 2, "Vu : arbustes vert sombre sur fond transparent (environ 26 % transparent), 256 px ; carte plane. Type « lit » : le détourage alpha en jeu n'est pas vérifié ici.", "Alpha non testé en jeu ; doNotUse."),
         C("core_foliage_treewall", ALT, 2, "Vu : rideau d'arbres feuillus sur fond transparent (environ 15 % transparent), 512 px ; fond de décor.", "Alpha non testé en jeu ; doNotUse."),
     ]},
    {"id": "grillage", "famille": "Sols naturels et végétation", "titre": "Grillage",
     "mat_projet": [],
     "resume": "Deux vrais grillages à mailles losangées avec alpha : core_fence_chain_link (128 px, légère) et t7_metal_chainlink (1024 px, double face). Les pièces de poteaux sont des modèles (§7).",
     "candidats": [
         C("core_fence_chain_link", REC, 3, "Vu : RGBA 8 bits, 128 px, environ 74 % transparent, type lit_alphatest (face unique probable) ; maille argentée claire."),
         C("t7_metal_chainlink", ALT, 3, "Vu : 1024 px, alpha environ 83 % transparent, type lit_alphatest_nocull_advanced (double face) ; plus défini, couleur sombre. Aucun usage dans les .map officiels lus."),
         C("t7_metal_chainlink_worn", ALT, 2, "Vu dans le GDT : variante usée (image jaune, teinte grise 0,49)."),
         C("t7_metal_fence_post_cable", LIM, 2, "Vu : treillis en losanges de câbles, environ 80 % transparent ; plutôt un câble qu'un grillage."),
     ]},
    {"id": "mur_cloture", "famille": "Sols naturels et végétation", "titre": "Mur de clôture",
     "mat_projet": [],
     "resume": "Mur de clôture : brushes avec un enduit (t7_plaster_smooth_light_01) ou des parpaings. Les panneaux préfabriqués de béton (t7_concrete_block_barrier_01) ont des trous de banches très visibles.",
     "candidats": [
         C("t7_plaster_smooth_light_01", REC, 3, "Vu : gris clair uniforme ; mur enduit."),
         C("t7_concrete_wall_blocks_wet", ALT, 3, "Vu : parpaings gris-bleu, 1024 px ; stock : 64 × 64 ou 128 × 128 ; aspect mouillé déduit du nom."),
         C("core_concrete_cinderblocks", ALT, 2, "Vu : parpaings gris-bleu avec mousse, 512 px."),
         C("t7_brick_worn_red", ALT, 3, "Vu : brique rouge propre ; muret de brique."),
         C("t7_concrete_block_barrier_01", LIM, 2, "Vu : grands panneaux de béton gris clair avec deux trous de banche par panneau, 1024 px ; stock : 64 × 64. Mur « préfa » seulement."),
     ]},
]

# ---------------------------------------------------------------------------------------------------
MODELES = [
    {"id": "voitures", "titre": "Voitures",
     "resume": "Seule la citadine compacte est vraiment exploitable (4 couleurs). Elle pèse environ 26 700 sommets au LOD0 ; la berline veh_t7_civ_city_car_vista n'en a que 328 (très simple, 3 couleurs) et sert pour le lointain.",
     "candidats": [
         C("veh_t7_civ_car_compact_grey", REC, 4, "Citadine, 4 couleurs : grey, blue, black, green (+ variantes « cairo » à plaque différente). Utilisée dans le projet à l'échelle 1 : passer à modelscale 1.25."),
         C("veh_t7_civ_car_compact_blue", ALT, 4, "Même modèle en bleu."),
         C("veh_t7_civ_car_compact_black", ALT, 4, "Même modèle en noir."),
         C("veh_t7_civ_car_compact_green", ALT, 4, "Même modèle en vert."),
         C("veh_t7_civ_city_car_vista", ALT, 3, "Berline très simplifiée (328 sommets), pour des voitures au loin ; _blu et _grn existent (veh_t7_civ_city_car_vista_blu / _grn)."),
         C("veh_t7_civ_gt", LIM, 2, "Coupé de sport 5,2 m, type « animated » : peu plausible dans un parking de HLM."),
         C("veh_t7_civ_truck_semi_trailer", LIM, 2, "Remorque de 14,8 m : seulement pour un décor de route lointaine."),
     ]},
    {"id": "lampadaires", "titre": "Lampadaires et poteaux d'éclairage",
     "resume": "Aucun lampadaire de rue simple n'existe. p7_light_metal_circle_pole est un grand mât (9,5 m) terminé par un anneau ; son aspect exact est à vérifier dans Radiant. Les lampadaires en brushes du projet restent le plus sûr.",
     "candidats": [
         C("p7_light_metal_circle_pole", ALT, 2, "Mât de 9,5 m à anneau lumineux en tête (déduit de la silhouette). À regarder dans Radiant avant usage."),
         C("p7_cai_light_garden", ALT, 3, "Borne de jardin de 0,41 × 0,25 m ; pour des abords d'entrée."),
         C("p7_light_path_metal_small", LIM, 2, "Petite balise de chemin (0,24 m)."),
         C("p7_zm_der2_utility_pole_512", ALT, 3, "Poteau électrique de 13,2 m ; pour une ligne aérienne le long de l'avenue."),
     ]},
    {"id": "bancs", "titre": "Bancs",
     "resume": "Un seul banc, mais en trois finitions : p7_bench_modern_01 (utilisé), _metal_bare, _metal_green.",
     "candidats": [
         C("p7_bench_modern_01", REC, 4, "Banc moderne 2,03 m ; utilisé dans le projet (à modelscale 1.25 pour rester proportionné)."),
         C("p7_bench_modern_01_metal_green", ALT, 4, "Même banc, structure métal verte (nom à vérifier visuellement)."),
         C("p7_bench_modern_01_metal_bare", ALT, 4, "Même banc, structure en métal nu."),
     ]},
    {"id": "conteneurs", "titre": "Conteneurs à ordures et bacs",
     "resume": "Bacs de tri p7_trashcan_metal_modern_glass / _organic / _paper (trois flux), benne p7_zm_der_dumpster_metal_large, fûts plastique p7_barrel_plastic (plusieurs couleurs). "
               "Les conteneurs semi-enterrés du projet sont des brushes.",
     "candidats": [
         C("p7_trashcan_metal_modern_glass", REC, 3, "Bac de tri 0,84 × 1,23 m ; « glass » = verre (déduit du nom). Bon pour un point de tri."),
         C("p7_trashcan_metal_modern_paper", REC, 3, "Même bac, flux « papier » (déduit)."),
         C("p7_trashcan_metal_modern_organic", REC, 3, "Même bac, flux « organique » (déduit)."),
         C("p7_zm_der_dumpster_metal_large", ALT, 3, "Benne métallique 3,9 × 1,6 × 1,3 m ; pour une cour de service."),
         C("p7_barrel_plastic", LIM, 2, "Fût plastique 0,77 × 1,11 m (blue, green, yellow aussi) ; plutôt industriel."),
     ]},
    {"id": "barrieres", "titre": "Barrières, clôtures et portails",
     "resume": "Pas de panneau de grillage en modèle, seulement les pièces (bases, capuchons, serrures). Le grillage = texture (core_fence_chain_link) sur un brush fin. Pour les portails : p7_barricade_metal_gate_02 (3,35 m).",
     "candidats": [
         C("p7_barricade_metal_gate_02", ALT, 3, "Portail métallique 3,35 × 1,63 m, 6 cm d'épaisseur ; clôture ou portail de parking (version _damaged aussi)."),
         C("p7_cai_sec_wall_metal", LIM, 2, "Panneau de mur métallique 4,65 × 3,06 m ; plutôt sécuritaire."),
         C("p7_slab_concrete_interlocked", ALT, 3, "Dalle de béton emboîtable 1,70 × 0,88 m ; mur de clôture préfabriqué."),
         C("p7_global_chainlink_fence_metal_base", LIM, 2, "Pied de poteau 0,25 m ; pièces seulement."),
         C("p7_global_chainlink_fence_post_cap", LIM, 2, "Capuchon de poteau de 11 cm ; pièces seulement."),
         C("p7_rail_post_metal_01", ALT, 3, "Poteau de rambarde 1,24 m ; garde-corps de balcon (avec p7_railing_metal_post_end_lt, 1,09 m)."),
     ]},
    {"id": "arbres", "titre": "Arbres (peuplier, sapin, feuillus)",
     "resume": "Aucun peuplier ni conifère. Feuillus : p7_foliage_tree_albizia_tall_full (19,4 m, houppier large, la grande vedette), p7_foliage_tree_olive_small (2,4 m), p7_foliage_tree_acacia_bush (2 m). "
               "Les palmiers sont hors sujet. Les peupliers et les sapins du projet (brushes) restent donc nécessaires ; l'albizia convient aux feuillus d'agrément.",
     "candidats": [
         C("p7_foliage_tree_albizia_tall_full", REC, 3, "Feuillu à houppier large et tronc fin, 14,5 × 13,9 × 19,4 m, 7 388 sommets ; utilisé aujourd'hui (échelle 0,9 à 1,2). Silhouette arrondie, pas de peuplier."),
         C("p7_foliage_tree_albizia_tall_full_sway", ALT, 3, "Même arbre avec balancement du feuillage (déduit du suffixe _sway et du matériau fxanim_vegetation) ; coût plus élevé."),
         C("p7_foliage_tree_olive_small", ALT, 3, "Petit arbre de 2,4 m ; jardin ou pied d'immeuble."),
         C("p7_foliage_tree_acacia_bush", LIM, 2, "Buisson-arbre bas (2 × 1,6 × 1,15 m) ; massif."),
         C("p7_foliage_palm_date_med_half_crown", EVI, 1, "Palmier-dattier de 13,6 m : hors sujet en Haute-Savoie."),
     ]},
    {"id": "buissons", "titre": "Buissons et haies",
     "resume": "Haies taillées prêtes à l'emploi, en deux largeurs et deux hauteurs : p7_foliage_hedge_box_128_48_36 (3,6 m de long), _128_48_60 (haie haute 1,85 m), _48_48_36 (cube), _round_48_48_36 (arrondi), "
               "avec des variantes _vibrant (vert plus clair) et _sway.",
     "candidats": [
         C("p7_foliage_hedge_box_128_48_60", REC, 4, "Haie taillée haute 3,84 × 1,80 × 1,85 m ; haie de séparation ; variantes _vibrant et _sway."),
         C("p7_foliage_hedge_box_128_48_36", REC, 4, "Haie basse 3,57 × 1,56 × 1,10 m, 7 285 sommets ; variantes _vibrant et _sway."),
         C("p7_foliage_hedge_box_48_48_36", ALT, 3, "Cube de haie 1,35 × 1,52 × 1,10 m."),
         C("p7_foliage_hedge_round_48_48_36_vibrant", ALT, 3, "Arbuste arrondi 1,49 × 1,42 × 1,05 m, vert clair ; utilisé aujourd'hui avec modelscale 1.6."),
         C("p7_foliage_plant_fern_01", ALT, 3, "Fougère 3 × 3 × 1,3 m ; sous-bois."),
         C("p7_foliage_wild_ginger_cover_32_tall", LIM, 2, "Couvre-sol de 0,8 m ; massif."),
     ]},
    {"id": "herbes", "titre": "Touffes d'herbe et fleurs",
     "resume": "Touffes d'herbe en trois tailles (p7_foliage_grass_tussock_green_1 : 2,1 m ; _2 : 0,95 m ; _3 : 0,35 m), fleurs sauvages p7_foliage_grass_flowers (0,65 × 1,06 m), herbes hautes et mauvaises herbes.",
     "candidats": [
         C("p7_foliage_grass_tussock_green_3", REC, 3, "Petite touffe 0,35 × 0,25 m ; pelouses."),
         C("p7_foliage_grass_tussock_green_2", REC, 3, "Touffe moyenne 0,95 × 0,35 m."),
         C("p7_foliage_grass_tussock_green_1", ALT, 3, "Grande touffe 2,1 × 1,2 m : très grande pour une pelouse, à réserver aux talus."),
         C("p7_foliage_grass_flowers", ALT, 3, "Fleurs sauvages 0,65 × 1,06 m ; utilisé aujourd'hui."),
         C("p7_foliage_weed_cluster_lrg", LIM, 2, "Mauvaises herbes 0,43 m ; pieds de mur."),
     ]},
    {"id": "panneaux", "titre": "Panneaux routiers et signalétique",
     "resume": "Aucun panneau routier n'existe. Restent des signalétiques intérieures/industrielles (garage, zone de chargement, sortie) et le potelet p7_sin_bollard_tall_painted. Pour les panneaux de rue : brushes plats + décalque.",
     "candidats": [
         C("p7_sin_bollard_tall_painted", ALT, 3, "Potelet de 1 m, 21 cm de diamètre ; entrées de parking."),
         C("p7_zm_der_signage_garage", LIM, 2, "Enseigne « garage » 0,87 × 0,21 m ; texte anglais probable, non vérifié."),
         C("p7_signage_loading_zone_01", LIM, 2, "Panneau de zone de chargement 0,71 × 0,46 m."),
         C("p7_cai_signage_plastic_exit", LIM, 2, "Panneau de sortie 0,43 × 0,40 m."),
     ]},
    {"id": "paraboles", "titre": "Antennes paraboliques et antennes",
     "resume": "p7_civ_sat_dish est une vraie parabole sur pied (1 × 1,1 × 1,7 m). Les antennes de toit : p6_antenna_rooftop (3,3 m, ancien jeu) et p7_cell_antenna_roof (4,6 m, antenne-relais).",
     "candidats": [
         C("p7_civ_sat_dish", REC, 3, "Parabole 0,99 × 1,13 × 1,67 m, 10 975 sommets : lourde pour la répéter ; réserver à quelques balcons ou toits."),
         C("p6_antenna_rooftop", ALT, 3, "Antenne de toit de 3,3 m (ancien jeu) ; antenne TV de toit."),
         C("p7_cell_antenna_roof", LIM, 2, "Antenne-relais 4,6 m ; trop industriel pour un immeuble."),
     ]},
    {"id": "climatiseurs", "titre": "Climatiseurs",
     "resume": "Climatiseur mural p7_ac_unit_wall_mount_01 (0,92 × 0,63 × 0,64 m) pour les façades ; groupe p7_ac_unit_large (2 × 1,4 × 1 m) pour un toit-terrasse.",
     "candidats": [
         C("p7_ac_unit_wall_mount_01", REC, 3, "Unité murale 0,92 × 0,63 × 0,64 m ; balcons et façades (rare en HLM, à doser)."),
         C("p7_ac_unit_large", ALT, 3, "Groupe de toiture 2,01 × 1,36 × 0,97 m."),
         C("p7_roof_vent_tall_01_metal_white", ALT, 3, "Aérateur de toit blanc 0,9 m ; sorties de ventilation sur le toit."),
     ]},
    {"id": "cheminees", "titre": "Souches de cheminée",
     "resume": "Aucune souche de cheminée. Les souches du projet sont des brushes ; les aérateurs p7_roof_vent_turbine_metal et p7_roof_vent_tall_01_metal_white peuvent compléter le faîtage.",
     "candidats": [
         C("p7_roof_vent_turbine_metal", ALT, 3, "Aérateur à turbine 0,98 × 0,84 × 0,81 m."),
         C("p7_roof_vent_tall_01_metal_white", ALT, 3, "Ventilation de toit blanche 0,95 m."),
         C("p7_brick_dirty_01", LIM, 2, "Fragment de mur de briques de 0,14 × 0,30 × 0,10 m (décor de gravats) : pas une souche."),
     ]},
    {"id": "fenetres_portes", "titre": "Fenêtres et portes en modèle",
     "resume": "Aucune fenêtre d'appartement français ; mais p7_louver_window_wooden(_closed) (persienne 1,63 × 2,84 m) et p7_door_metal_rolling_02 (rideau roulant 2,87 × 2,56 m) sont directement utiles ; "
               "p7_cai_apt_window_taller_01 (1,32 × 0,40 × 2,36 m) est une baie haute.",
     "candidats": [
         C("p7_louver_window_wooden_closed", REC, 3, "Persienne bois fermée 1,63 × 2,84 m, 196 sommets (très légère) ; volets des pavillons."),
         C("p7_louver_window_wooden", ALT, 3, "Même persienne ouverte."),
         C("p7_door_metal_rolling_02", REC, 3, "Rideau métallique roulant 2,87 × 2,56 m ; portes de garage. Variante _matte."),
         C("p7_cai_apt_window_taller_01", ALT, 2, "Baie haute 1,32 × 2,36 m, 88 sommets ; style Moyen-Orient (cai), à regarder avant usage."),
         C("p7_blinds_01_closed", ALT, 2, "Store vénitien fermé 1,01 × 2,15 m ; intérieur des appartements."),
         C("p7_door_metal_industrial_02_left_white", LIM, 2, "Porte industrielle blanche 1,38 × 2,45 m ; locaux techniques."),
     ]},
    {"id": "bacs_fleurs", "titre": "Bacs à fleurs et jardinières",
     "resume": "Série p7_cai_planter_* (béton/bois, 1 à 3,7 m) et p7_planters_sphere (0,98 m). Taille plutôt grande : pour une entrée d'immeuble, planter_square (1,07 m).",
     "candidats": [
         C("p7_cai_planter_square", REC, 3, "Bac carré 1,07 × 1,27 × 1,13 m."),
         C("p7_cai_planter_rectangle_sml", ALT, 3, "Bac rectangulaire 2,39 × 1,25 × 1,17 m."),
         C("p7_cai_planter_rectangle", LIM, 2, "Grand bac 3,66 × 1,73 × 1,54 m."),
         C("p7_planters_sphere", ALT, 3, "Jardinière sphérique 0,98 m."),
         C("p7_plant_tray_plastic_planter", LIM, 2, "Bac plastique de 0,36 × 0,69 m ; balcons."),
     ]},
    {"id": "poteaux", "titre": "Poteaux et potelets",
     "resume": "Poteau électrique p7_zm_der2_utility_pole_512 (13,2 m, avec ses bras p7_zm_der_utility_pole_arm), potelets p7_sin_bollard_tall_painted / _indents (1 m) pour les entrées de parking, "
               "poteau-obélisque p7_cai_fence_obelisk (1,95 m, style Moyen-Orient) et poteaux de rambarde p7_rail_post_metal_01.",
     "candidats": [
         C("p7_sin_bollard_tall_painted", REC, 3, "Potelet peint de 1 m, 21 cm de diamètre ; entrées de parking et devant les halls."),
         C("p7_sin_bollard_tall_indents", ALT, 3, "Potelet à rainures de 0,96 m, 27 cm de diamètre."),
         C("p7_zm_der2_utility_pole_512", ALT, 3, "Poteau électrique de 13,2 m ; ligne aérienne le long de l'avenue Borcier."),
         C("p7_zm_der_utility_pole_arm", LIM, 2, "Bras de poteau électrique de 3,3 m (0,22 × 0,49 m) ; à fixer au poteau précédent."),
         C("p7_rail_post_metal_01", ALT, 3, "Poteau de rambarde 1,24 m ; garde-corps."),
         C("p7_cai_fence_obelisk", LIM, 2, "Poteau-obélisque de clôture de 1,95 m (base 0,41 m) ; style Moyen-Orient, à regarder avant usage."),
     ]},
    {"id": "boites_lettres_modele", "titre": "Boîtes aux lettres",
     "resume": "Aucun modèle de boîte aux lettres. Substituts : coffrets électriques p7_electrical_box_set2_* (0,4 × 0,2 × 0,8 m) et compteurs ; à défaut, des brushes.",
     "candidats": [
         C("p7_electrical_box_set2_box02", LIM, 2, "Coffret mural 0,43 × 0,29 × 0,78 m ; coffret de hall (pas une boîte aux lettres)."),
         C("p7_electrical_box_set2_box05", LIM, 2, "Coffret 0,40 × 0,21 × 0,80 m."),
         C("p7_electrical_box_set2_meter05", LIM, 2, "Compteur 0,28 × 0,34 m ; locaux techniques."),
     ]},
    {"id": "jeux_enfants", "titre": "Jeux d'enfants",
     "resume": "Aucun jeu d'enfants (ni toboggan, ni balançoire, ni bac à sable). Substituts très partiels : fûts et palettes. À construire en brushes (cadre métal + sol souple t7_rubber_hex_floor_tiles ou t7_mat_floor_rubber_01).",
     "candidats": [
         C("p7_pallet_wood_damaged", LIM, 1, "Palette de 1,22 × 1,02 m ; décor seulement."),
         C("p7_crate_wood_01", LIM, 1, "Caisse en bois 1,54 × 0,78 m ; décor."),
     ]},
    {"id": "bordures_regards", "titre": "Bordures, regards et avaloirs",
     "resume": "Bordure modélisée p7_street_curb_concrete_64a/64b (1,63 m, 21 cm), variantes endommagées (_dmg), peintes (_black_white, _black_yellow) et sableuses (_sandy). Regard p7_street_manhole_cover_cairo_01 (0,88 m), avaloir p7_street_curb_sewer_drain_01.",
     "candidats": [
         C("p7_street_curb_concrete_64a", REC, 4, "Bordure 64 pouces (1,63 m) × 0,21 × 0,21 m, 52 sommets ; plus fidèle qu'un brush texturé."),
         C("p7_street_curb_concrete_64b", ALT, 4, "Variante b, même gabarit."),
         C("p7_street_curb_sewer_drain_01", ALT, 3, "Avaloir de bordure 1,63 × 1,02 × 0,61 m."),
         C("p7_street_manhole_cover_cairo_01", ALT, 3, "Plaque d'égout ronde 0,88 m (style Le Caire : motif à vérifier)."),
     ]},
    {"id": "descentes_eau", "titre": "Descentes d'eaux pluviales et gouttières",
     "resume": "Tuyaux PVC prêts à l'emploi : p7_pipe_pvc_drain_128 (10 cm × 3,25 m), _64, _32, _16, avec coudes, tés et raccords. Parfait pour les descentes de façade (en gris ou blanc) et les évacuations de balcon.",
     "candidats": [
         C("p7_pipe_pvc_drain_128", REC, 4, "Tuyau 3,25 m de long, 10 cm de diamètre (128 pouces) ; descente EP d'un étage et demi."),
         C("p7_pipe_pvc_drain_64", ALT, 4, "Tuyau 1,63 m (64 pouces)."),
         C("p7_pipe_pvc_drain_elbow_90", ALT, 4, "Coude à 90° de 16 cm."),
         C("p7_pipe_metal_water_straight_64_white", ALT, 3, "Tuyau métal blanc 1,63 m, 8 cm de diamètre ; alimentation visible, plutôt local technique."),
     ]},
    {"id": "luminaires_facade", "titre": "Luminaires et petits équipements de façade",
     "resume": "Luminaires muraux p7_light_fixture_led_wall_01 (1,63 m de long) et p7_light_wall_runner_led ; caméra p7_camera_security_03 (0,4 m) ; interrupteur p7_lightswitch_metal_m_sensor.",
     "candidats": [
         C("p7_light_fixture_led_wall_01", ALT, 2, "Barre lumineuse murale 1,63 m ; style bureau/labo, à regarder avant usage."),
         C("p7_camera_security_03", ALT, 2, "Caméra de surveillance 0,37 × 0,43 m ; entrées de parking."),
         C("p7_vent_wall_metal_01_white", ALT, 3, "Grille d'aération murale blanche 0,99 × 0,61 m ; façades et caves."),
     ]},
]

# ---------------------------------------------------------------------------------------------------
# statuts : garder / ajuster / remplacer
REMPLACEMENTS = [
    {"cle": "herbe", "statut": "garder", "pourquoi": "Pelouse la plus naturelle (uniforme, sans répétition). Mêler des plaques de t7_grass_crab_low_sparse_green pour casser l'uniformité.", "alt": "t7_grass_crab_low_sparse_green"},
    {"cle": "herbe_sombre", "statut": "garder", "pourquoi": "Herbe dense plus sombre, bonne variation ; utile sous les arbres."},
    {"cle": "terre", "statut": "ajuster", "pourquoi": "Terre réaliste mais en 256 px : passer à core_dirt_light (512 px) pour les grandes surfaces.", "par": "core_dirt_light"},
    {"cle": "asphalte", "statut": "remplacer", "par": "core_asphault_dark", "alt": "t7_asphalt_damaged_dark_wet",
     "pourquoi": "L'asphalte « désert » brun-ocre est peu alpin et ses plages se répètent. Enrobé neuf : core_asphault_dark ; route usée : t7_asphalt_damaged_dark_wet."},
    {"cle": "trottoir", "statut": "ajuster", "pourquoi": "Bon matériau, mais projeter à 64 × 64 (stock) ×1,25 = 80 au lieu de 256 × 256.", "par": "t7_concrete_sidewalk_02"},
    {"cle": "bordure", "statut": "ajuster", "pourquoi": "Bon matériau mais étiré : l'image fait 1024 × 256, la projeter à 64 × 16 (stock) ×1,25 = 80 × 20, jamais en 256 × 256.", "par": "t7_street_concrete_curb_01a"},
    {"cle": "montagne", "statut": "garder", "pourquoi": "Silhouette lointaine : l'herbe sombre suffit ; un rideau d'arbres alpha (core_foliage_treewall) pourrait être ajouté plus tard.", "alt": "core_foliage_treewall"},
    {"cle": "ciel", "statut": "garder", "pourquoi": "Matériau d'outil (tools.gdt) : ne pas changer."},
    {"cle": "clip", "statut": "garder", "pourquoi": "Matériau d'outil (clip.gdt) : ne pas changer."},
    {"cle": "facade_beige", "statut": "remplacer", "par": "core_plaster_light", "alt": "t7_plaster_rough_worn_01",
     "pourquoi": "t7_plaster_smooth_light_01 est un gris clair, pas un beige. Idéal : instance teintée zm_seyssel_crepi_beige (§10). Sans GDT : core_plaster_light (beige crème discret, 512 px) ou t7_plaster_rough_worn_01 (vrai beige mais écaillé)."},
    {"cle": "facade_blanche", "statut": "remplacer", "par": "t7_plaster_smooth_light_01",
     "pourquoi": "Le matériau actuel est un gris-vert terne tacheté. Le blanc cassé uniforme de t7_plaster_smooth_light_01 convient mieux ; stock : 128 × 128."},
    {"cle": "socle", "statut": "ajuster", "par": "t7_brick_worn_heavy_grout_brown", "alt": "t7_concrete_bare_dark_01",
     "pourquoi": "La version _wet donne un aspect mouillé (normales « wet »). Même brique en version sèche, ou béton gris foncé pour un soubassement plus neutre."},
    {"cle": "panneau", "statut": "garder", "alt": "t7_metal_wall_corrugated_hor_brown_drk",
     "pourquoi": "Brun très foncé et propre, matériau de référence des maps officielles (64 × 64). Pour des lames horizontales type persiennes, essayer t7_metal_wall_corrugated_hor_brown_drk."},
    {"cle": "loggia", "statut": "garder", "pourquoi": "Brun olive plat, propre ; un peu uniforme mais cohérent avec les panneaux bruns."},
    {"cle": "fenetre", "statut": "garder", "alt": "t7_plastic_base_clean",
     "pourquoi": "Fenêtre complète à cadre blanc, pratique mais en 512 px et dépendante de la taille de chaque face. À terme : cadre en brushes (t7_plastic_base_clean) + vitre séparée."},
    {"cle": "vitre", "statut": "garder", "alt": "t7_glass_clean_01_transparent",
     "pourquoi": "Déjà compilé. Alternative plus moderne : t7_glass_clean_01_transparent (alpha 127, type glass) ; à comparer en jeu."},
    {"cle": "appui", "statut": "ajuster", "pourquoi": "Bon matériau ; projeter à 128 × 32 ou 64 × 16 (stock) ×1,25, jamais en 256 × 256 (bande 4:1).", "par": "t7_concrete_trim_beveled_03"},
    {"cle": "volet", "statut": "remplacer", "par": "t7_metal_wall_corrugated_panel_hor_grey", "alt": "t7_metal_wall_corrugated_hor_brown_drk",
     "pourquoi": "t7_drywall_painted_beige_01 est une peinture de cloison kaki, sans lames. Un bardage à lames horizontales se lit comme un volet roulant ; brun pour les « panneaux type persiennes »."},
    {"cle": "garage", "statut": "ajuster", "par": "t7_metal_panel_horizontal_painted_grey", "alt": "p7_door_metal_rolling_02",
     "pourquoi": "core_door_metal_light est un métal nu clair sans panneaux. Panneaux peints gris, ou le modèle de rideau roulant p7_door_metal_rolling_02 (2,87 × 2,56 m)."},
    {"cle": "porte", "statut": "garder", "pourquoi": "Porte de bois sombre à panneaux moulurés ; correcte pour une porte d'immeuble ou d'appartement."},
    {"cle": "porte_asc", "statut": "garder", "pourquoi": "Inox brossé : cohérent pour des portes d'ascenseur."},
    {"cle": "garde_corps", "statut": "ajuster", "par": "t7_metal_paint_worn_grey_dk", "alt": "t7_metal_panels_painted_2x1_grey",
     "pourquoi": "Fer brut noir (micro-matériau) : pour du « métal peint » de la fiche, un gris anthracite peint est plus juste. Pour une allège pleine : t7_metal_panels_painted_2x1_grey."},
    {"cle": "dalle_balcon", "statut": "garder", "pourquoi": "Béton marbré sec, correct ; t7_concrete_bare_weathered_01 est un peu plus clair et plus uniforme."},
    {"cle": "balcon", "statut": "remplacer", "par": "t7_plaster_smooth_light_01",
     "pourquoi": "Même gris-vert terne que facade_blanche ; l'enduit clair donne une façade arrière plus propre."},
    {"cle": "toit", "statut": "ajuster", "par": "core_roof_dark", "alt": "core_roof_light",
     "pourquoi": "L'ardoise gris-bleu est belle mais pas brun foncé comme la fiche : instance teintée de core_roof_light (§10) pour le brun, sinon garder."},
    {"cle": "rive", "statut": "garder", "pourquoi": "Bande 16:1 : stock 64 × 4 (×1,25 = 80 × 5)."},
    {"cle": "cheminee", "statut": "garder", "pourquoi": "Enduit clair, cohérent avec le faîtage. Une brique rouge (t7_brick_worn_red) est possible si la photo le montre.", "alt": "t7_brick_worn_red"},
    {"cle": "auvent", "statut": "garder", "pourquoi": "Gris anthracite peint uni."},
    {"cle": "hall_sol", "statut": "ajuster", "par": "t7_stone_travertine", "alt": "t7_stone_travertine_tiles",
     "pourquoi": "Vu : c'est un marbre blanc-gris veiné, pas du crème (le README annonce des sols et marches crème). Pour du crème : instance teintée zm_seyssel_hall_sol_creme (§10). t7_stone_travertine_tiles est un pavage ocre-brun, trop foncé."},
    {"cle": "hall_mur", "statut": "ajuster", "par": "t7_drywall_painted_white_01", "alt": "t7_plaster_smooth_light_01",
     "pourquoi": "t7_drywall_base_cream est un gris neutre (le crème n'est que dans le nom). Pour du crème : instance teintée de t7_drywall_painted_white_01 (§10)."},
    {"cle": "plafond", "statut": "garder", "pourquoi": "Blanc de plafond uniforme."},
    {"cle": "rampe", "statut": "garder", "pourquoi": "Inox brossé."},
    {"cle": "boites", "statut": "ajuster", "par": "t7_metal_bare_aluminum_brushed", "alt": "t7_metal_paint_worn_yellow",
     "pourquoi": "Gris clair actuellement. Alu brossé ou jaune selon les boîtes réelles du hall (à confirmer sur photo)."},
    {"cle": "dalle", "statut": "garder", "pourquoi": "Béton marbré sec."},
    {"cle": "gaine", "statut": "garder", "pourquoi": "Béton de cage d'ascenseur."},
    {"cle": "cabine", "statut": "garder", "pourquoi": "Inox brossé."},
    {"cle": "cabine_sol", "statut": "ajuster", "par": "t7_linoleum_floor_tile_square",
     "pourquoi": "Vu : plaque de sol sombre de type science-fiction (voyants bleus, boulons), peu crédible dans l'ascenseur d'un immeuble. Le lino gris à dalles carrées est plus sobre (stock : 64 × 64)."},
    {"cle": "appart_mur", "statut": "garder", "pourquoi": "Blanc cassé de cloison, uniforme."},
    {"cle": "sol_entree", "statut": "ajuster", "alt": "t7_ceramic_tile_large_white", "pourquoi": "Vu : grands carreaux gris clair craquelés (2 × 2 par répétition), 512 px de l'ancien jeu. Un carrelage t7_ de 1024 px est plus défini (t7_ceramic_tile_large_white : grands carreaux blancs, stock 64 × 64)."},
    {"cle": "sol_cuisine", "statut": "garder", "pourquoi": "Vu : mosaïque de petits carreaux (grille de 16 × 16 par répétition) sur fond marbré clair, 1024 px ; à projeter assez grand pour que les carreaux restent lisibles."},
    {"cle": "sol_sdb", "statut": "garder", "pourquoi": "Vu : petits carreaux gris-blanc en damier lâche, 1024 px."},
    {"cle": "sol_chambre", "statut": "garder", "pourquoi": "Parquet clair ; stock : 64 × 64."},
    {"cle": "faience", "statut": "garder", "pourquoi": "Grand carreau blanc ; stock : 64 × 64."},
    {"cle": "meuble", "statut": "garder", "pourquoi": "Bois brun foncé."},
    {"cle": "annexe", "statut": "garder", "pourquoi": "Béton peint gris-beige uni ; projeter à 128 × 128 (stock) ×1,25 = 160."},
    {"cle": "gravier", "statut": "garder", "pourquoi": "Gravillon très uniforme, sans répétition ; stock : 64 × 64."},
    {"cle": "garages", "statut": "remplacer", "par": "t7_plaster_smooth_light_01", "pourquoi": "Même gris-vert terne que facade_blanche ; un enduit clair raccorde mieux les garages à l'annexe."},
    {"cle": "voisin", "statut": "ajuster", "par": "t7_plaster_rough_worn_01", "alt": "core_plaster_light",
     "pourquoi": "Bon beige de pavillon, mais 256 × 256 est trop grand : 128 × 128 (stock) ×1,25 = 160, et alterner avec core_plaster_light ou une instance teintée pour varier les maisons."},
    {"cle": "voisin_toit", "statut": "remplacer", "par": "core_roof_light", "alt": "core_roof_dark",
     "pourquoi": "core_roof_med ne fait que 64 × 64 px (flou). core_roof_light (512 px) est la vraie tuile des pavillons."},
    {"cle": "ecole", "statut": "remplacer", "par": "t7_concrete_floor_sealed_01", "alt": "t7_plaster_smooth_light_01",
     "pourquoi": "Version _wet (aspect mouillé, taches sombres). Même image en version sèche, ou un enduit clair pour une école maternelle."},
    {"cle": "ecorce", "statut": "ajuster", "pourquoi": "t7_wood_beam_worn_oak est une poutre, pas une écorce. Pour des troncs en brushes : t7_wood_planks_worn (brun-gris) ou garder.", "alt": "t7_wood_planks_worn"},
    {"cle": "feuillage", "statut": "garder", "pourquoi": "Herbe sombre posée sur des cônes : acceptable de loin. Les arbres modélisés (albizia) sont plus crédibles de près."},
    {"cle": "feuillage_clair", "statut": "garder", "pourquoi": "Herbe moyenne sur les houppiers de peupliers : acceptable de loin."},
    {"cle": "conteneur", "statut": "ajuster", "par": "t7_metal_panels_painted_2x4_green", "alt": "t7_metal_paint_worn_grey_dk",
     "pourquoi": "Les conteneurs de tri sont souvent verts : à confirmer sur photo ; sinon garder le gris."},
    {"cle": "metal", "statut": "garder", "pourquoi": "Graphite mat pour lampadaires et couvercles."},
]

# ---------------------------------------------------------------------------------------------------
PROPOSITIONS = [
    {"nom": "zm_seyssel_hall_sol_creme", "parent": "t7_stone_travertine", "colorTint": "1 0.94 0.80 1",
     "objectif": "Sol et marches de hall crème : t7_stone_travertine est un marbre blanc-gris (#e5e5e5) ; 1 / 0,94 / 0,80 donne environ #e5d7b7.",
     "statut": "à créer et à juger en jeu"},
    {"nom": "zm_seyssel_crepi_beige", "parent": "t7_plaster_smooth_light_01", "colorTint": "1 0.94 0.80 1",
     "objectif": "Enduit beige clair du bâtiment 1 (fiche : « enduit beige clair »). La teinte multiplie la colorMap : sur une base #cdccc7 environ, 1 / 0,94 / 0,80 donne un beige d'environ #cdc09f.",
     "statut": "à créer et à juger en jeu ; teinte à ajuster à l'œil"},
    {"nom": "zm_seyssel_crepi_blanc", "parent": "t7_plaster_smooth_light_01", "colorTint": "1 1 1 1",
     "objectif": "Alias propre du blanc cassé pour les bâtiments 2 et 3 (pas nécessaire : utiliser t7_plaster_smooth_light_01 directement).",
     "statut": "inutile en l'état"},
    {"nom": "zm_seyssel_toit_brun", "parent": "core_roof_light", "colorTint": "0.50 0.40 0.36 1",
     "objectif": "Tuiles brun foncé des immeubles, à partir de la tuile mécanique core_roof_light (rose-orangé, 512 px).",
     "statut": "à créer et à juger en jeu"},
    {"nom": "zm_seyssel_toit_pavillon", "parent": "core_roof_light", "colorTint": "0.78 0.56 0.46 1",
     "objectif": "Rouge-brun plus sombre pour les pavillons.",
     "statut": "à créer et à juger en jeu"},
    {"nom": "zm_seyssel_hall_creme", "parent": "t7_drywall_painted_white_01", "colorTint": "1 0.94 0.80 1",
     "objectif": "Murs de hall crème (le « t7_drywall_base_cream » actuel est gris neutre).",
     "statut": "à créer et à juger en jeu"},
]
