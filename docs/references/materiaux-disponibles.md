# Matériaux et modèles disponibles dans les Mod Tools BO3

Inventaire en **lecture seule** de `D:/SteamLibrary/steamapps/common/Call of Duty Black Ops III 455130` pour la map zm_seyssel : quels matériaux et quels modèles existent vraiment, lesquels choisir pour chaque besoin du quartier, et ce qu'il faut remplacer dans le dictionnaire `MAT` de `tools/quartier.py`.

> Généré le 2026-10-24 par `tools/inventaire_materiaux.py` (contenu éditorial dans `tools/inventaire_materiaux_spec.py`). Les mêmes données, sous forme exploitable par un script, sont dans `reference/materiaux.json`. Un candidat n'est marqué « vérifié » que si son nom exact est l'en-tête d'une entrée d'un `.gdt` (recherche textuelle indépendante de l'analyse).

Degré de certitude : **vu** = lu dans un GDT, mesuré sur le fichier ou regardé dans un aperçu PNG ; **déduit** = conclu d'indices (noms, valeurs) sans l'avoir vu tourner dans le jeu ; **inconnu** = non vérifiable ici (rendu moteur, couleur réelle du bâti).

## 1. À retenir

1. Les matériaux ne sont PAS dans source_data\*.gdt : ces 56 fichiers contiennent des sons de pas, armes, caméras, brouillards, etc. ; leurs seuls matériaux sont 4 matériaux de lens flare. Les matériaux sont dans texture_assets\*.gdt (56 fichiers), art_assets\t6_legacy\texture_assets\*.gdt (13 fichiers, famille core_*) et model_export\**\*.gdt (214 fichiers, matériaux mtl_* propres aux modèles). Les 354 GDT et 16 062 entrées correspondent exactement au journal de la base (gdtdb.log).
2. Beaucoup de matériaux ne sont PAS des définitions complètes mais des instances `"nom" [ "parent" ]` qui reprennent un parent et ne changent que quelques valeurs, surtout `colorTint`. Une recherche textuelle de `"t7_drywall_base_cream" ( "material.gdf" )` ne les trouve pas : il faut chercher l'en-tête avec des crochets. Six noms de MAT paraissaient absents pour cette raison ; ils existent tous.
3. Les images sources (.tif) sont présentes pour 97 % des matériaux (4 683 sur 4 823) : la bibliothèque livrée est un sous-ensemble cohérent du jeu, pas une liste d'identifiants sans fichier. Le journal de liaison (_build/link.log) montre que le linker convertit ces .tif à la demande : tout matériau dont l'image est présente est utilisable.
4. L'échelle de répétition des textures est 2 à 4 fois trop grande dans le projet : make_blockout.py écrit `256 256` pour toutes les faces (lignes 208 et 221 à la date de lecture). Dans les 724 .map officiels des Mod Tools, les deux premiers nombres après le nom du matériau valent le plus souvent 64 ou 128 et gardent les proportions de l'image (bordure 1024×256 → 64 × 16, bandeau 1024×64 → 64 × 4) ; déduit : ce sont les dimensions en unités de monde d'une répétition de la texture. Avec 256 × 256, une bordure ou un liseré est étiré 4 à 16 fois. Valeur à retenir : celle du stock (colonne « Échelle .map »), multipliée par 1,25 pour rester proportionnée à ECHELLE.
5. Les modèles et les unités : tous les xmodel sont dessinés à 1 unité = 1 pouce. Le quartier est agrandi de 1,25 (geo.py) : pour qu'une voiture ou un banc ait la bonne taille à côté des immeubles, il faut `modelscale 1.25`. Les voitures sont posées à l'échelle 1 dans quartier.py : elles font environ 2,7 m « à l'échelle du quartier » au lieu de 3,4 m.
6. Aucun beige clair lisse n'existe tel quel : le « beige » du bâtiment 1 (t7_plaster_smooth_light_01) est en réalité un gris clair, et le « blanc » des bâtiments 2 et 3 (t7_concrete_worn_painted_white) un gris-vert terne. Le moyen propre est une instance teintée (§10), exactement comme Treyarch le fait (t7_plaster_smooth_light_01_grey, t7_drywall_painted_beige_01…).
7. Aucune tuile brun foncé n'existe : core_roof_dark est une ardoise gris-bleu, core_roof_light une tuile mécanique rose-orangé (très réaliste), core_roof_med est en 64 px. Pour le toit « brun foncé » des immeubles : instance teintée de core_roof_light (§10).
8. Modèles absents (vérifié par noms, par fichiers et par GDT) : peuplier, sapin ou conifère quelconque, feuillus autres que l'albizia et l'acacia, lampadaire de rue, panneau routier, boîte aux lettres, bouche d'incendie, jeux d'enfants, souche de cheminée. Les dossiers p7_cai_street_signage et p7_road_guard_metal ne contiennent que des matériaux orphelins, aucun modèle.
9. Trouvailles utiles : p7_trashcan_metal_modern_glass / _organic / _paper (trois bacs de tri, 0,84 × 1,23 m) ; p7_pipe_pvc_drain_* (descentes d'eaux pluviales, 10 cm × 3,25 m) ; p7_louver_window_wooden_closed (persienne bois 1,63 × 2,84 m) ; p7_door_metal_rolling_02 (rideau roulant 2,87 × 2,56 m) ; p7_street_curb_concrete_64a/b (bordure 1,63 m) ; t7_decal_signage_street_lines_white / _yellow (marquages au sol) ; p7_civ_sat_dish (antenne parabolique) ; p7_ac_unit_wall_mount_01 (climatiseur mural).
10. Les cartes de brillance (_g), d'occlusion (_o) et spéculaires (_s) ne sont pas toutes livrées : pour les matériaux t7_ et core_, il en manque 50 à 60 % (brillance 299 sur 597, occlusion 147 sur 244, spéculaire 104 sur 210), alors que les cartes de couleur (3 manquantes sur 886) et de normales (12 sur 637) sont presque toutes là. Le linker passe sans erreur sur des matériaux dans ce cas (t7_plaster_smooth_light_01 : seuls _c et _n sont convertis dans link.log) ; déduit : valeurs par défaut, donc un rendu un peu plus plat que dans le jeu officiel. Inconnu : l'écart visuel réel.
11. Les matériaux core_* portent le drapeau `doNotUse = 1` (héritage de l'ancien jeu), mais ils sont déjà compilés dans zm_seyssel sans erreur (link.log : core_grass_med, core_roof_dark, core_window_opaque, core_door_wood_dark…). Les matériaux mtl_* ont `usage = <not in editor>` : ils ne sont pas listés dans Radiant ; on peut les écrire à la main dans le .map mais ils sont conçus pour des modèles précis, donc rarement adaptés à un brush.

## 2. Actions prioritaires pour la suite

1. Corriger l'échelle de projection des textures (make_blockout.py) : au lieu de `256 256` partout, utiliser par matériau la valeur du stock ×1,25 en gardant les proportions de l'image (colonne « Échelle .map » des tableaux). C'est le gain de réalisme le plus important et le moins cher.
2. Remplacer dans `MAT` : asphalte (core_asphault_dark), facade_blanche, garages et balcon (t7_plaster_smooth_light_01), voisin_toit (core_roof_light), volet (t7_metal_wall_corrugated_panel_hor_grey), ecole et socle (versions sèches), cabine_sol (t7_linoleum_floor_tile_square) ; voir le tableau du §9.
3. Créer un petit GDT d'instances teintées (§10) pour le beige du bâtiment 1, le brun des toits et le crème des halls : c'est la seule façon d'obtenir ces teintes avec de vraies textures.
4. Poser les modèles à `modelscale 1.25` (voitures, banc, haies, arbres) pour rester proportionnés aux immeubles.
5. Utiliser les modèles trouvés pour les détails de façade et d'abords : tuyaux de descente p7_pipe_pvc_drain_*, persiennes p7_louver_window_wooden_closed, rideau roulant p7_door_metal_rolling_02, bordures p7_street_curb_concrete_64a/b, bacs de tri p7_trashcan_metal_modern_*, paraboles p7_civ_sat_dish, climatiseurs p7_ac_unit_wall_mount_01, haies p7_foliage_hedge_*.
6. Garder des brushes pour ce qui n'existe pas : peupliers et sapins, lampadaires, panneaux routiers, boîtes aux lettres, souches de cheminée, jeux d'enfants, barreaudage des balcons.
7. Vérifier en jeu avant de généraliser : décalques de marquage routier, grillages à alpha, verres (t7_glass_*), instances teintées.

## 3. Choix recommandés en un coup d'œil

| Besoin | Actuel dans `MAT` | Recommandé | Alternatives utiles |
|---|---|---|---|
| Crépi / enduit beige (façade du bâtiment 1) | `facade_beige` → `t7_plaster_smooth_light_01` | `core_plaster_light` | `t7_plaster_smooth_light_01`, `t7_plaster_rough_worn_01` |
| Enduit blanc cassé (bâtiments 2 et 3) | `facade_blanche` → `t7_concrete_worn_painted_white`, `garages` → `t7_concrete_worn_painted_white`, `balcon` → `t7_concrete_worn_painted_white` | `t7_plaster_smooth_light_01` | `t7_drywall_painted_white_01` |
| Crépi des pavillons voisins | `voisin` → `t7_plaster_rough_worn_01` | `t7_plaster_rough_worn_01` | `t7_plaster_smooth_dirty_01_light_brown`, `core_plaster_light`, `t7_plaster_smooth_light_01` |
| Béton brut | `dalle_balcon` → `t7_concrete_floor_sealed_01`, `dalle` → `t7_concrete_floor_sealed_01`, `gaine` → `t7_concrete_floor_sealed_01`, `ecole` → `t7_concrete_wall_weathered_01_wet` | `t7_concrete_bare_weathered_01`, `t7_concrete_floor_sealed_01` | `core_concrete_light`, `t7_concrete_bare_dark_01` |
| Béton peint | `annexe` → `t7_concrete_poured_bunker_paint_01_grey_lt`, `garages` → `t7_concrete_worn_painted_white` | `t7_plaster_smooth_light_01` | `t7_concrete_poured_bunker_paint_01_grey_lt` |
| Soubassement | `socle` → `t7_brick_worn_heavy_grout_brown_wet` | `t7_concrete_bare_dark_01` | `t7_brick_worn_heavy_grout_brown` |
| Brique | (non utilisé) | `t7_brick_worn_red` | `t7_brick_worn_dirty_red`, `t7_brick_worn_heavy_grout_red`, `t7_brick_worn_dirty_tan` |
| Tuiles / ardoise brun foncé (toit des immeubles) | `toit` → `core_roof_dark` | `core_roof_dark` | `core_roof_light` |
| Tuiles rouge-brun (pavillons) | `voisin_toit` → `core_roof_med` | `core_roof_light` | `core_roof_dark` |
| Rive, bardage et panneaux de bois bruns | `rive` → `t7_wood_trim_dark_brown`, `panneau` → `t7_wood_panel_01_stain_brown_drk`, `ecorce` → `t7_wood_beam_worn_oak` | `t7_wood_trim_dark_brown`, `t7_wood_panel_01_stain_brown_drk`, `t7_metal_wall_corrugated_hor_brown_drk` | `t7_wood_trim_brown_01`, `t7_wood_worn_darker_brown` |
| Menuiseries de fenêtre blanches | `fenetre` → `core_window_opaque` | `t7_plastic_base_clean` | `core_window_opaque`, `t7_metal_painted_wall_dirty_grey` |
| Menuiseries brunes (portes, loggias) | `loggia` → `t7_drywall_painted_brown_01`, `porte` → `core_door_wood_dark` | `t7_wood_panel_01_stain_brown_drk` | `t7_wood_worn_darker_brown`, `t7_drywall_painted_brown_01`, `core_door_wood_dark` |
| Vitrage | `vitre` → `core_glass_plain_trans` | `t7_glass_clean_01_transparent` | `core_glass_plain_trans`, `t7_glass_dirty_streaks`, `t7_glass_frosted_cold` |
| Volets roulants et persiennes | `volet` → `t7_drywall_painted_beige_01` | `t7_metal_wall_corrugated_panel_hor_grey` | `t7_metal_wall_corrugated_hor`, `t7_metal_wall_corrugated_hor_brown_drk` |
| Garde-corps métal peint : barreaudage | `garde_corps` → `t7_metal_worn_iron_dark` | `t7_metal_paint_worn_grey_dk` | `t7_metal_worn_iron_dark`, `t7_metal_fence_post_cable`, `t7_metal_grating_expanded` |
| Garde-corps métal peint : allège pleine | `garde_corps` → `t7_metal_worn_iron_dark` | `t7_metal_panels_painted_2x1_grey` | `t7_metal_panel_horizontal_painted_grey`, `t7_metal_worn_painted_graphite`, `t7_metal_panels_4x1_grey_drk` |
| Dalle et nez de balcon | `dalle_balcon` → `t7_concrete_floor_sealed_01`, `balcon` → `t7_concrete_worn_painted_white`, `appui` → `t7_concrete_trim_beveled_03` | `t7_concrete_bare_weathered_01`, `t7_concrete_trim_beveled_03` | `t7_concrete_floor_sealed_01`, `t7_concrete_floor_trim_01` |
| Porte vitrée de hall | `vitre` → `core_glass_plain_trans`, `porte` → `core_door_wood_dark`, `auvent` → `t7_metal_paint_worn_grey_dk` | `t7_glass_clean_01_transparent`, `t7_metal_bare_aluminum_brushed` | `t7_metal_trim_painted_black`, `t7_plastic_base_clean`, `t7_glass_frosted_cold` |
| Portes de garage | `garage` → `core_door_metal_light` | `t7_metal_panel_horizontal_painted_grey` | `t7_metal_panels_painted_2x4`, `core_door_metal_dark`, `t7_metal_garage_door_rollup_01_bare` |
| Boîtes aux lettres | `boites` → `t7_metal_painted_clean_white` | `t7_metal_bare_aluminum_brushed` | `t7_metal_paint_worn_yellow`, `t7_metal_painted_clean_white` |
| Asphalte neuf | `asphalte` → `t7_asphalt_dirty_dark_desert` | `core_asphault_dark` | `t7_asphalt_advanced_strips` |
| Asphalte usé | (non utilisé) | `t7_asphalt_damaged_dark_wet` | `t7_asphalt_damaged_dark_wet_nw`, `core_asphault_med`, `t7_concrete_floor_garage_cracked_wet_nw` |
| Marquages routiers blancs et jaunes | (non utilisé) | voir §6 | `t7_decal_signage_street_lines_white`, `t7_decal_signage_street_lines_yellow`, `t7_street_concrete_curb_01a_yellow` |
| Trottoir | `trottoir` → `t7_concrete_sidewalk_02` | `t7_concrete_sidewalk_02` | `t7_concrete_sidewalk_01`, `t7_concrete_sidewalk_2x2_01` |
| Bordure | `bordure` → `t7_street_concrete_curb_01a` | `t7_street_concrete_curb_01a` | `t7_street_concrete_curb_01b`, `t7_concrete_trim_beveled_01_wet`, `t7_street_concrete_curb_01a_white` |
| Pavés et dalles | (non utilisé) | `t7_stone_cobblestone_01_wet_nw` | `t7_concrete_slabs_interlocked`, `t7_rock_cobblestone_round` |
| Herbe | `herbe` → `core_grass_med`, `herbe_sombre` → `core_grass_dark`, `montagne` → `core_grass_dark`, `feuillage` → `core_grass_dark`, `feuillage_clair` → `core_grass_med` | `core_grass_med` | `core_grass_dark`, `t7_grass_crab_low_sparse_green` |
| Gravier | `gravier` → `t7_stone_pebbles_01` | `t7_stone_pebbles_01` | `core_gravel_dark`, `core_gravel_light`, `t7_stone_pebbles_01_warm` |
| Terre | `terre` → `core_dirt_med` | `core_dirt_med` | `core_dirt_light`, `t7_dirt_grassy_forest_ground` |
| Haies et rideaux d'arbres | (non utilisé) | voir §6 | `core_foliage_bushline`, `core_foliage_treewall` |
| Grillage | (non utilisé) | `core_fence_chain_link` | `t7_metal_chainlink`, `t7_metal_chainlink_worn` |
| Mur de clôture | (non utilisé) | `t7_plaster_smooth_light_01` | `t7_concrete_wall_blocks_wet`, `core_concrete_cinderblocks`, `t7_brick_worn_red` |

Modèles :

| Besoin | Recommandé | Remarque |
|---|---|---|
| Voitures | `veh_t7_civ_car_compact_grey` | Seule la citadine compacte est vraiment exploitable (4 couleurs). |
| Lampadaires et poteaux d'éclairage | aucun modèle adapté | Aucun lampadaire de rue simple n'existe. |
| Bancs | `p7_bench_modern_01` | Un seul banc, mais en trois finitions : p7_bench_modern_01 (utilisé), _metal_bare, _metal_green. |
| Conteneurs à ordures et bacs | `p7_trashcan_metal_modern_glass`, `p7_trashcan_metal_modern_paper`, `p7_trashcan_metal_modern_organic` | Bacs de tri p7_trashcan_metal_modern_glass / _organic / _paper (trois flux), benne p7_zm_der_dumpster_metal_large, fûts plastique p7_barrel_plastic (plusieurs couleurs). |
| Barrières, clôtures et portails | aucun modèle adapté | Pas de panneau de grillage en modèle, seulement les pièces (bases, capuchons, serrures). |
| Arbres (peuplier, sapin, feuillus) | `p7_foliage_tree_albizia_tall_full` | Aucun peuplier ni conifère. |
| Buissons et haies | `p7_foliage_hedge_box_128_48_60`, `p7_foliage_hedge_box_128_48_36` | Haies taillées prêtes à l'emploi, en deux largeurs et deux hauteurs : p7_foliage_hedge_box_128_48_36 (3,6 m de long), _128_48_60 (haie haute 1,85 m), _48_48_36 (cube), _round_48_48_36 (arrondi), avec des variantes _vibrant (vert plus clair) et _sway. |
| Touffes d'herbe et fleurs | `p7_foliage_grass_tussock_green_3`, `p7_foliage_grass_tussock_green_2` | Touffes d'herbe en trois tailles (p7_foliage_grass_tussock_green_1 : 2,1 m ; _2 : 0,95 m ; _3 : 0,35 m), fleurs sauvages p7_foliage_grass_flowers (0,65 × 1,06 m), herbes hautes et mauvaises herbes. |
| Panneaux routiers et signalétique | aucun modèle adapté | Aucun panneau routier n'existe. |
| Antennes paraboliques et antennes | `p7_civ_sat_dish` | p7_civ_sat_dish est une vraie parabole sur pied (1 × 1,1 × 1,7 m). |
| Climatiseurs | `p7_ac_unit_wall_mount_01` | Climatiseur mural p7_ac_unit_wall_mount_01 (0,92 × 0,63 × 0,64 m) pour les façades ; groupe p7_ac_unit_large (2 × 1,4 × 1 m) pour un toit-terrasse. |
| Souches de cheminée | aucun modèle adapté | Aucune souche de cheminée. |
| Fenêtres et portes en modèle | `p7_louver_window_wooden_closed`, `p7_door_metal_rolling_02` | Aucune fenêtre d'appartement français ; mais p7_louver_window_wooden(_closed) (persienne 1,63 × 2,84 m) et p7_door_metal_rolling_02 (rideau roulant 2,87 × 2,56 m) sont directement utiles ; p7_cai_apt_window_taller_01 (1,32 × 0,40 × 2,36 m) est une baie haute. |
| Bacs à fleurs et jardinières | `p7_cai_planter_square` | Série p7_cai_planter_* (béton/bois, 1 à 3,7 m) et p7_planters_sphere (0,98 m). |
| Poteaux et potelets | `p7_sin_bollard_tall_painted` | Poteau électrique p7_zm_der2_utility_pole_512 (13,2 m, avec ses bras p7_zm_der_utility_pole_arm), potelets p7_sin_bollard_tall_painted / _indents (1 m) pour les entrées de parking, poteau-obélisque p7_cai_fence_obelisk (1,95 m, style Moyen-Orient) et poteaux de rambarde p7_rail_post_metal_01. |
| Boîtes aux lettres | aucun modèle adapté | Aucun modèle de boîte aux lettres. |
| Jeux d'enfants | aucun modèle adapté | Aucun jeu d'enfants (ni toboggan, ni balançoire, ni bac à sable). |
| Bordures, regards et avaloirs | `p7_street_curb_concrete_64a` | Bordure modélisée p7_street_curb_concrete_64a/64b (1,63 m, 21 cm), variantes endommagées (_dmg), peintes (_black_white, _black_yellow) et sableuses (_sandy). |
| Descentes d'eaux pluviales et gouttières | `p7_pipe_pvc_drain_128` | Tuyaux PVC prêts à l'emploi : p7_pipe_pvc_drain_128 (10 cm × 3,25 m), _64, _32, _16, avec coudes, tés et raccords. |
| Luminaires et petits équipements de façade | aucun modèle adapté | Luminaires muraux p7_light_fixture_led_wall_01 (1,63 m de long) et p7_light_wall_runner_led ; caméra p7_camera_security_03 (0,4 m) ; interrupteur p7_lightswitch_metal_m_sensor. |

## 4. Où sont les matériaux (et où ils ne sont pas)

| Dossier | Fichiers .gdt | Matériaux | Images | Modèles | Autres entrées (instances, sons, armes…) |
|---|---|---|---|---|---|
| `archetypes/*.gdt` | 1 | 0 | 0 | 0 | 9 |
| `art_assets/t6_legacy/texture_assets/*.gdt` | 13 | 252 | 27 | 0 | 0 |
| `model_export/**.gdt` | 214 | 3012 | 4567 | 2456 | 348 |
| `source_data/*.gdt` | 56 | 4 | 5 | 0 | 465 |
| `texture_assets/*.gdt` | 56 | 1555 | 2438 | 2 | 37 |
| `xanim_export/*.gdt` | 14 | 0 | 0 | 0 | 885 |

Total lu : 354 fichiers, 16062 entrées dont 2708 instances `"nom" [ "parent" ]` (comptées avec le type de leur parent). Matériaux distincts : 4823 ; images : 7032 ; modèles : 2458. La dernière colonne regroupe les autres types : sons, armes, animations, brouillards, personnages…

## 5. Lire les tableaux

- **Matériau** : nom exact à écrire dans le `.map`. Les instances sont signalées (« instance de ») : elles reprennent le parent et ne changent que quelques valeurs, surtout `colorTint` (multiplie la couleur de l'image).
- **Teinte moy.** : couleur moyenne de l'image après `colorTint`, mesurée sur le fichier (pixels visibles seulement pour les cartes à alpha). Ce n'est pas la couleur affichée en jeu (lumière, spéculaire et exposition la modifient) ; elle sert à comparer.
- **Échelle .map** : taille en unités de monde d'une répétition (les deux nombres après le nom du matériau dans le `.map`). « stock » = valeur la plus fréquente dans les .map officiels (724 fichiers lus) ; « estimée » = proportions de l'image sur 64 unités (à régler à l'œil). La ligne « projet ×1,25 » tient compte de `ECHELLE` (geo.py).
- **Suffixes** (déduits des GDT) : `_wet` = carte de normales mouillée et gloss plus élevé (aspect mouillé) ; `_blend` / `_reveal` = matériaux de fusion pour décalques et terrain ; `_nw` = variante dont le sens exact n'est pas documenté ; `_dark`, `_grey`, `_tan`, `_warm` = instances teintées.
- **Drapeaux** : `doNotUse` (matériaux core_* hérités, mais compilés sans erreur dans zm_seyssel) ; `usage = <not in editor>` (matériaux mtl_* de modèles, non listés dans Radiant) ; types `lit_alphatest*` (grillages : le canal alpha est présent, mesuré).

### Échelles de référence relevées dans les .map officiels

| Matériau | Échelle la plus fréquente | Faces | Image |
|---|---|---|---|
| `t7_plaster_smooth_light_01` | 128 x 128 | 262 sur 278 | i_t7_plaster_smooth_light_01_c (2048 x 2048 px) |
| `t7_plaster_rough_worn_01_wet` | 128 x 128 | 228 sur 234 | i_t7_plaster_rough_worn_01_c (2048 x 2048 px) |
| `t7_concrete_wall_weathered_01_wet` | 128 x 128 | 893 sur 1041 | i_t7_concrete_wall_weathered_01_c (2048 x 2048 px) |
| `t7_concrete_bare_dark_01_wet` | 128 x 128 | 646 sur 667 | i_t7_concrete_bare_dark_01_c (2048 x 2048 px) |
| `t7_brick_worn_dirty_red_wet` | 64 x 64 | 2083 sur 2122 | i_t7_brick_worn_dirty_red_c (2048 x 2048 px) |
| `t7_brick_worn_heavy_grout_red` | 64 x 64 | 1135 sur 1169 | i_t7_brick_worn_red_heavy_grout_c (1024 x 1024 px) |
| `t7_asphalt_dirty_dark_desert` | 64 x 64 | 62 sur 86 | i_t7_asphalt_dirty_dark_desert_c (1024 x 1024 px) |
| `t7_asphalt_advanced_strips` | 128 x 128 | 42 sur 42 | i_t7_asphalt_advanced_strips_c (2048 x 2048 px) |
| `t7_concrete_sidewalk_02` | 64 x 64 | 94 sur 104 | i_t7_concrete_sidewalk_02_c (1024 x 1024 px) |
| `t7_concrete_sidewalk_2x2_01` | 128 x 128 | 16 sur 16 | i_t7_concrete_sidewalk_2x2_01_c (2048 x 2048 px) |
| `t7_concrete_trim_beveled_01_wet` | 64 x 16 | 1425 sur 1767 | i_t7_concrete_trim_beveled_01_c (1024 x 256 px) |
| `t7_street_concrete_curb_01a` | 64 x 16 | 36 sur 36 | i_t7_street_concrete_curb_01a_c (1024 x 256 px) |
| `t7_wood_panel_01_stain_brown_drk` | 64 x 64 | 4662 sur 4662 | i_t7_wood_panel_01_c (2048 x 2048 px) |
| `t7_wood_trim_dark_brown` | 64 x 4 | 170 sur 195 | i_t7_wood_trim_dark_brown_c (1024 x 64 px) |
| `t7_metal_paint_worn_white` | 64 x 64 | 390 sur 390 | i_t7_metal_paint_worn_white_c (1024 x 1024 px) |
| `t7_metal_planter_top_trim` | 32 x 4 | 1361 sur 3268 | i_t7_metal_planter_top_trim_c (512 x 64 px) |
| `t7_glass_plain_opaque` | 128 x 128 | 383 sur 383 | i_t7_glass_plain_opaque_c (2048 x 2048 px) |
| `t7_stone_pebbles_01` | 64 x 64 | 228 sur 252 | i_t7_stone_pebbles_01_c (2048 x 2048 px) |

## 6. Matériaux par besoin

### Façades et murs

#### Crépi / enduit beige (façade du bâtiment 1)

Utilisé aujourd'hui : `facade_beige` → `t7_plaster_smooth_light_01`.

**Avis.** Aucun matériau officiel n'est un enduit beige clair lisse. Le plus proche en teinte est t7_plaster_rough_worn_01, mais il est moucheté et écaillé. Pour la façade est du bâtiment 1 (fiche : « enduit beige clair »), la solution propre est une instance teintée de t7_plaster_smooth_light_01 (§10) ; en attendant, core_plaster_light donne un beige crème lisse, mais en 512 px.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `core_plaster_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_plaster_light_c`<br>512 × 512 px | `#c7c4b7` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : beige crème lisse, grain fin de crépi, se raccorde bien ; le plus beige utilisable tout de suite, sans GDT. Défaut : 512 px, soit quatre fois moins défini que les t7_. Déduit : le drapeau doNotUse est un héritage, ces core_* sont déjà compilés dans zm_seyssel. **Réserve :** Définition faible de près ; beige très discret. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_plaster_smooth_light_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_smooth_light_01_c`<br>2048 × 2048 px | `#cccbc6` | 128 × 128<br><sub>stock : 262 faces sur 278</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris très clair, à peine chaud, très uniforme, aucun motif répétitif ; c'est l'actuel « beige » du bâtiment 1 et il rend gris-blanc. Excellent support pour une instance teintée (même image, même relief ; §10). **Réserve :** Pas beige en l'état. |
| alternative (3/5) | `t7_plaster_rough_worn_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_rough_worn_01_c`<br>2048 × 2048 px | `#ccbfa9` | 128 × 128<br><sub>stock de la variante `t7_plaster_rough_worn_01_wet` : 228 faces sur 234</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : beige chaud à reflets orangés, crépi grossier vieilli avec de larges plages claires et foncées. Convient à un pavillon ancien, trop abîmé pour un immeuble entretenu. Déduit : les grandes plages se répètent à l'œil sur de grandes surfaces (visible dès 2 × 2). **Réserve :** La variante _wet multiplie la teinte par 0,8 et ajoute un aspect mouillé (déduit) : à éviter par temps sec. |
| limité (2/5) | `t7_plaster_smooth_dirty_01_light_brown`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_plaster_smooth_dirty_01` | `i_t7_plaster_smooth_dirty_01_c`<br>2048 × 2048 px | `#918b81`<br><sub>teinte ×(0.745098 0.716213 0.674968)</sub> | 128 × 128<br><sub>stock de la variante `t7_plaster_smooth_dirty_01_blue_pale_wet` : 153 faces sur 160</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris-brun sali, taches sombres qui se répètent nettement. Trop sombre et sale pour un beige clair ; utile pour un soubassement ou un mur de garage vieilli. |
| limité (2/5) | `t7_drywall_painted_beige_01`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_drywall_painted_white_01` | `i_t7_drywall_paited_white_c`<br>1024 × 1024 px | `#96907f`<br><sub>teinte ×(0.733333 0.698039 0.639216)</sub> | 64 × 64<br><sub>stock : 36 faces sur 36</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : kaki-gris plat, sans relief, 1024 px, usage « interior wall » (cloison). Trop foncé et verdâtre pour du beige clair dehors ; correct dans un hall. |
| limité (2/5) | `core_concrete_light_warm`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_concrete_light_warm_c`<br>512 × 512 px | `#ada493` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : béton gravillonné beige-sable. Ce n'est pas un enduit lisse (cailloutis visibles), mais il convient à une dalle ou un muret chaud. <sub>[drapeau doNotUse (hérité)]</sub> |
| à éviter (1/5) | `t7_drywall_base_cream`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_drywall_painted_white_01` | `i_t7_drywall_base_cream_c`<br>2048 × 2048 px | `#b0aead` | 64 × 64<br><sub>stock de la variante `t7_drywall_base_cream_orange` : 82 faces sur 90</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : malgré son nom, la colorMap est un gris neutre ; la variante _cream_orange n'est qu'une teinte orange multipliée dessus. Ne pas compter sur lui pour du crème (il sert aujourd'hui de « hall_mur »). Inconnu : rendu en jeu. |

#### Enduit blanc cassé (bâtiments 2 et 3)

Utilisé aujourd'hui : `facade_blanche` → `t7_concrete_worn_painted_white`, `garages` → `t7_concrete_worn_painted_white`, `balcon` → `t7_concrete_worn_painted_white`.

**Avis.** t7_plaster_smooth_light_01 est le meilleur blanc cassé disponible (uniforme, sans répétition visible, 2048 px). Le matériau actuel (t7_concrete_worn_painted_white) tire sur le gris-vert terne et paraît sale à côté d'un beige.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_plaster_smooth_light_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_smooth_light_01_c`<br>2048 × 2048 px | `#cccbc6` | 128 × 128<br><sub>stock : 262 faces sur 278</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris très clair quasi uniforme, aucun motif répétitif, se raccorde proprement. Déduit : sous le soleil de la map il se lit « blanc cassé ». Stock .map : 128 × 128. |
| alternative (3/5) | `t7_drywall_painted_white_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_drywall_paited_white_c`<br>1024 × 1024 px | `#cccec7` | 64 × 64<br><sub>stock : 138 faces sur 138</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc cassé plat (écart-type de luminance voisin de 1), 1024 px, usage cloison : propre mais sans grain ; peut paraître plastique sur une façade. |
| limité (2/5) | `t7_plastic_base_clean`<br><sub>ta/t7_plastic.gdt</sub> | `i_t7_plastic_base_clean_c`<br>1024 × 1024 px | `#eaeaea` | 64 × 64<br><sub>stock : 80 faces sur 180</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc franc, 1024 px, sans relief ; spéculaire de plastique (PVC). Pour des menuiseries, pas pour un mur. |
| limité (2/5) | `t7_metal_painted_wall_dirty_grey`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_painted_wall_dirty_grey_c`<br>1024 × 1024 px | `#eeeeee` | 64 × 64<br><sub>stock de la variante `t7_metal_painted_wall_dirty_black` : 156 faces sur 156</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc uni malgré son nom « grey », 1024 px, matériau métal. Pour un cadre ou un panneau blanc. |
| à éviter (2/5) | `t7_concrete_worn_painted_white`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_worn_painted_white_c`<br>1024 × 1024 px | `#b0b1a8` | 64 × 64<br><sub>stock : 126 faces sur 126</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris-vert terne tacheté, 1024 px ; ne se lit pas comme blanc. C'est l'actuel « facade_blanche ». |
| à éviter (1/5) | `t7_concrete_painted_white_blend`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_painted_wet_white_c`<br>1024 × 1024 px | `#c6c4c6` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : type lit_decal_diffuse_reveal, tri « blend / additive », catégorie Decal. C'est un matériau de fusion pour décalques ou terrain ; inconnu : comportement sur un brush. **Réserve :** Matériau de fusion, non testé sur brush. |

#### Crépi des pavillons voisins

Utilisé aujourd'hui : `voisin` → `t7_plaster_rough_worn_01`.

**Avis.** Les pavillons des alentours sont aujourd'hui en t7_plaster_rough_worn_01 projeté en 256 × 256. La texture convient (beige chaud, crépi grossier) mais ses grandes plages se répètent : réduire l'échelle à 128 et alterner avec une seconde teinte pour casser la répétition d'une maison à l'autre.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_plaster_rough_worn_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_rough_worn_01_c`<br>2048 × 2048 px | `#ccbfa9` | 128 × 128<br><sub>stock de la variante `t7_plaster_rough_worn_01_wet` : 228 faces sur 234</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : beige chaud, crépi grossier vieilli ; stock .map (variante _wet) : 128 × 128. Alterner avec une instance teintée pour varier les maisons. |
| alternative (2/5) | `t7_plaster_smooth_dirty_01_light_brown`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_plaster_smooth_dirty_01` | `i_t7_plaster_smooth_dirty_01_c`<br>2048 × 2048 px | `#918b81`<br><sub>teinte ×(0.745098 0.716213 0.674968)</sub> | 128 × 128<br><sub>stock de la variante `t7_plaster_smooth_dirty_01_blue_pale_wet` : 153 faces sur 160</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris-brun sali, taches sombres. Donne un second ton de crépi, mais répétition très visible. |
| alternative (3/5) | `core_plaster_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_plaster_light_c`<br>512 × 512 px | `#c7c4b7` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : beige crème lisse 512 px ; pour des pavillons récents au crépi propre. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_plaster_smooth_light_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_smooth_light_01_c`<br>2048 × 2048 px | `#cccbc6` | 128 × 128<br><sub>stock : 262 faces sur 278</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris clair uniforme ; base d'instances teintées (rose pâle, jaune pâle, ocre) pour varier les maisons sans répétition visible. |
| limité (2/5) | `t7_concrete_floor_sealed_01_warm`<br><sub>ta/t7_concrete.gdt</sub><br>instance de `t7_concrete_floor_sealed_01` | `i_t7_concrete_bare_weathered_01_c`<br>2048 × 2048 px | `#76654a`<br><sub>teinte ×(0.721569 0.616236 0.472557)</sub> | 128 × 128<br><sub>stock : 28 faces sur 28</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : brun-ocre foncé marbré (teinte 0,72 / 0,62 / 0,47 sur béton) ; pour un mur de soutènement ou un garage, pas un crépi. |
| limité (2/5) | `t7_drywall_painted_beige_01`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_drywall_painted_white_01` | `i_t7_drywall_paited_white_c`<br>1024 × 1024 px | `#96907f`<br><sub>teinte ×(0.733333 0.698039 0.639216)</sub> | 64 × 64<br><sub>stock : 36 faces sur 36</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : kaki plat ; correct pour un intérieur de pavillon. |

#### Béton brut

Utilisé aujourd'hui : `dalle_balcon` → `t7_concrete_floor_sealed_01`, `dalle` → `t7_concrete_floor_sealed_01`, `gaine` → `t7_concrete_floor_sealed_01`, `ecole` → `t7_concrete_wall_weathered_01_wet`.

**Avis.** Le béton brut officiel est abondant et réaliste. Pour du sec : t7_concrete_bare_weathered_01 ou t7_concrete_floor_sealed_01 (même image que wall_weathered, sans la variante _wet). L'actuel « ecole » (t7_concrete_wall_weathered_01_wet) prend un aspect mouillé.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_concrete_bare_weathered_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_bare_weathered_01_c`<br>2048 × 2048 px | `#a3a39d` | 64 × 64<br><sub>stock : 22 faces sur 40</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris clair granuleux, taches douces, pas de motif répétitif gênant, 2048 px. Stock .map : 64 ou 128 unités. Existe en _dark (teinte × 0,45) et _wet. |
| recommandé (3/5) | `t7_concrete_floor_sealed_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_wall_weathered_01_c`<br>2048 × 2048 px | `#827d70` | 128 × 128<br><sub>stock de la variante `t7_concrete_wall_weathered_01_wet` : 893 faces sur 1041</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : mêmes taches marbrées que concrete_wall_weathered_01 (même image), sans l'aspect mouillé ; type lit_detail avec carte de détail. C'est l'actuel « dalle » et « gaine ». |
| alternative (3/5) | `core_concrete_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_concrete_light_c`<br>512 × 512 px | `#a3a4a2` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : béton clair à pores et gravillons, très réaliste, mais 512 px seulement. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_concrete_bare_dark_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_bare_dark_01_c`<br>2048 × 2048 px | `#676863` | 128 × 128<br><sub>stock : 50 faces sur 58</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris moyen sombre, uniforme ; bon pour soubassements et murs de soutènement. Stock : 128 × 128 (surtout la variante _wet). |
| limité (3/5) | `t7_concrete_wall_poured_thick_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_wall_poured_thick_01_c`<br>2048 × 2048 px | `#8e8e85` | 128 × 128<br><sub>stock de la variante `t7_concrete_wall_poured_thick_01_wet` : 548 faces sur 694</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : béton banché avec joints verticaux de coffrage (effet bunker). Le raccord gauche-droite est douteux (écart de bord 30 contre 9 entre colonnes voisines) : tester avant d'étendre. **Réserve :** Raccord horizontal douteux. <sub>[raccord des bords douteux (mesuré)]</sub> |
| limité (2/5) | `t7_concrete_brushed_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_brushed_01_c`<br>1024 × 1024 px | `#848079` | 64 × 64<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris tiède très bruité, aspect balayé, peu de relief grand format. |

#### Béton peint

Utilisé aujourd'hui : `annexe` → `t7_concrete_poured_bunker_paint_01_grey_lt`, `garages` → `t7_concrete_worn_painted_white`.

**Avis.** Il n'existe pas de « peinture sur béton » propre en matériau de brush. Deux pistes : le micro-matériau t7_concrete_poured_bunker_paint_01_grey_lt (actuel de l'annexe) ou un enduit lisse (t7_plaster_smooth_light_01). Les variantes *_painted_*_blend sont des matériaux de fusion.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_plaster_smooth_light_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_smooth_light_01_c`<br>2048 × 2048 px | `#cccbc6` | 128 × 128<br><sub>stock : 262 faces sur 278</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris clair uniforme ; un enduit peint se lit comme du béton peint à distance. |
| alternative (3/5) | `t7_concrete_poured_bunker_paint_01_grey_lt`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_micro_plaster_smooth_light_01_c`<br>1024 × 1024 px | `#a9a59b` | 128 × 128<br><sub>stock : 349 faces sur 350</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris-beige très uni avec micro-grain ; type lit_micro_tile_blend (image micro 1024 px, tuilée finement). Stock : 128 × 128. La variante _blue_lt existe. |
| à éviter (2/5) | `t7_concrete_worn_painted_white`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_worn_painted_white_c`<br>1024 × 1024 px | `#b0b1a8` | 64 × 64<br><sub>stock : 126 faces sur 126</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris-vert terne ; actuel « garages ». Stock : 64 × 64. |
| à éviter (1/5) | `t7_concrete_painted_grey_blend`<br><sub>ta/t7_concrete.gdt</sub><br>instance de `t7_concrete_painted_white_blend` | `i_t7_concrete_painted_wet_white_c`<br>1024 × 1024 px | `#636363`<br><sub>teinte ×(0.450202 0.450584 0.466667)</sub> | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : type lit_decal_diffuse_reveal, catégorie Decal ; gris par teinte 0,45. Matériau de fusion, non testé sur brush. **Réserve :** Matériau de fusion. |

#### Soubassement

Utilisé aujourd'hui : `socle` → `t7_brick_worn_heavy_grout_brown_wet`.

**Avis.** Le socle actuel utilise la version _wet de la brique brune (aspect mouillé, déduit de sa carte de normales « wet » et de glossRangeMax 11). Plus neutre pour un soubassement d'immeuble : béton gris foncé ou la même brique en version sèche.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_concrete_bare_dark_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_bare_dark_01_c`<br>2048 × 2048 px | `#676863` | 128 × 128<br><sub>stock : 50 faces sur 58</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris moyen sombre, uniforme, discret. Déduit : bon soubassement sous un enduit clair. |
| alternative (3/5) | `t7_brick_worn_heavy_grout_brown`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_brown_heavy_grout_c`<br>2048 × 2048 px | `#6c6559` | 64 × 64<br><sub>stock de la variante `t7_brick_worn_heavy_grout_brown_wet` : 271 faces sur 271</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brique brun-gris à gros joints clairs, 2048 px ; même image que le socle actuel sans le gloss mouillé. |
| limité (2/5) | `t7_concrete_wall_blocks_wet`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_wall_blocks_c`<br>1024 × 1024 px | `#848382` | 64 × 64<br><sub>stock : 20 faces sur 38</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : parpaings gris bleutés, 1024 px ; aspect mouillé déduit du nom et de la carte de normales. <sub>[raccord des bords douteux (mesuré)]</sub> |
| limité (2/5) | `core_concrete_cinderblocks`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_concrete_cinderblock_c`<br>512 × 512 px | `#7d7f7d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : parpaings gris-bleu avec mousse, 512 px ; plutôt un aspect de ruine. <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (3/5) | `t7_concrete_floor_trim_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_floor_trim_01_c`<br>1024 × 128 px | `#757069` | 32 × 4<br><sub>stock : 22 faces sur 75</sub><br><sub>projet ×1,25 : 40 × 5</sub> | Vu : bande 1024 × 128 (rapport 8:1) de plinthe béton ; stock : 32 × 4. À utiliser en liseré, pas en surface. |
| limité (2/5) | `t7_concrete_trim_edge_damaged_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_trim_edge_damaged_01_c`<br>2048 × 256 px | `#7c7c7a` | 64 × 8<br><sub>stock : 50 faces sur 103</sub><br><sub>projet ×1,25 : 80 × 10</sub> | Vu : bande 2048 × 256, bord de béton abîmé ; stock : 64 × 8. Pour un angle ou un nez de marche. |

#### Brique

**Avis.** La brique est le point fort de la bibliothèque (16 matériaux t7_ et 3 core_). Brique rouge propre : t7_brick_worn_red ; plus sombre : t7_brick_worn_dirty_red ; ocre : t7_brick_worn_dirty_tan.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_brick_worn_red`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_red_c`<br>2048 × 2048 px | `#866456` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brique rouge-rosé régulière, joints fins clairs, peu de défauts ; 2048 px. La meilleure brique « propre » et le meilleur raccord de la série. |
| alternative (3/5) | `t7_brick_worn_dirty_red`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_dirty_red_c`<br>2048 × 2048 px | `#60473d` | 64 × 64<br><sub>stock de la variante `t7_brick_worn_dirty_red_wet` : 2083 faces sur 2122</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brique rouge sombre patinée, contraste marqué ; 2048 px. Stock : 64 × 64. |
| alternative (3/5) | `t7_brick_worn_heavy_grout_red`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_red_heavy_grout_c`<br>1024 × 1024 px | `#77665c` | 64 × 64<br><sub>stock : 1135 faces sur 1169</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : briques rouges à gros joints clairs et taches de salpêtre ; 1024 px. Stock : 64 × 64. |
| alternative (3/5) | `t7_brick_worn_dirty_tan`<br><sub>ta/t7_brick.gdt</sub><br>instance de `t7_brick_worn_dirty_red` | `i_t7_brick_worn_dirty_tan_c`<br>2048 × 2048 px | `#685847` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brique ocre-brun (même motif que dirty_red avec une autre teinte). |
| alternative (3/5) | `t7_brick_worn_heavy_grout_brown`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_brown_heavy_grout_c`<br>2048 × 2048 px | `#6c6559` | 64 × 64<br><sub>stock de la variante `t7_brick_worn_heavy_grout_brown_wet` : 271 faces sur 271</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brique brun-gris à gros joints ; stock (variante _wet) : 64 × 64. |
| limité (2/5) | `core_brick_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_brick_light_c`<br>512 × 512 px | `#897a6e` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brique rouge-orangé 512 px au motif régulier ; raccord vertical un peu visible. <sub>[drapeau doNotUse (hérité)]</sub> |

### Toiture, bois et boiseries

#### Tuiles / ardoise brun foncé (toit des immeubles)

Utilisé aujourd'hui : `toit` → `core_roof_dark`.

**Avis.** Aucune tuile brun foncé n'existe. core_roof_dark est une vraie ardoise (gris-bleu), core_roof_light une tuile mécanique orange. La solution propre est une instance teintée de core_roof_light (§10) ; sinon garder core_roof_dark.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `core_roof_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_dark_c`<br>512 × 512 px | `#636168` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : ardoises rectangulaires gris-bleu foncé, joints ombrés, 512 px, belle définition, motif régulier sans raccord gênant. Pas brun (gris-violet). Utilisé aujourd'hui. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (4/5) | `core_roof_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_light_c`<br>512 × 512 px | `#896e60` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : tuiles mécaniques rose-orangé avec traces de mousse, 512 px, très réaliste. Teinte à assombrir par une instance pour obtenir le brun foncé. <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `core_roof_med`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_med_c`<br>64 × 64 px | `#6d5a51` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : bardeaux brun-rouge mais 64 × 64 px : flou dès qu'on s'approche. **Réserve :** 64 px. <sub>[raccord des bords douteux (mesuré) ; drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `t7_rubber_roof_granular`<br><sub>ta/t7_rubber.gdt</sub> | `i_t7_rubber_roof_granular_c`<br>1024 × 1024 px | `#4c4947` | 128 × 128<br><sub>stock : 8 faces sur 10</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : membrane granuleuse brun-gris foncé, usage « roof » ; se lit comme bitume de loin, pas comme tuile. |
| limité (2/5) | `t7_stone_slate_tile_grey`<br><sub>ta/t7_stone.gdt</sub> | `i_t7_stone_slate_tile_grey_c`<br>1024 × 1024 px | `#424243` | 128 × 128<br><sub>stock : 4 faces sur 4</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : dalles d'ardoise gris foncé en appareil, 1024 px, mais raccord vertical visible (bord 42 contre 13) ; usage « floor ». **Réserve :** Raccord douteux. <sub>[raccord des bords douteux (mesuré)]</sub> |
| limité (2/5) | `t7_metal_wall_corrugated_hor_brown_drk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_wall_corrugated_hor` | `i_t7_metal_wall_corrugated_hor_c`<br>2048 × 2048 px | `#3e3124`<br><sub>teinte ×(0.305882 0.244495 0.178729)</sub> | 64 × 64<br><sub>stock : 64 faces sur 68</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales brun très foncé (bac acier brun) ; à réserver aux panneaux/volets bruns plutôt qu'à un toit de tuiles. |

#### Tuiles rouge-brun (pavillons)

Utilisé aujourd'hui : `voisin_toit` → `core_roof_med`.

**Avis.** core_roof_light est la bonne tuile (orange-rosé, 512 px). L'actuel core_roof_med est en 64 px.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `core_roof_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_light_c`<br>512 × 512 px | `#896e60` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : tuiles mécaniques rose-orangé avec mousse, 512 px ; pour un rouge-brun plus sombre, instance teintée (§10). <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `core_roof_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_dark_c`<br>512 × 512 px | `#636168` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : ardoise gris-bleu ; pour des pavillons à toit d'ardoise. <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `core_roof_med`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_roof_med_c`<br>64 × 64 px | `#6d5a51` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : bardeaux brun-rouge en 64 × 64 px (actuel « voisin_toit ») : trop flou. **Réserve :** 64 px. <sub>[raccord des bords douteux (mesuré) ; drapeau doNotUse (hérité)]</sub> |
| à éviter (1/5) | `t7_ceramic_tiles_6x6_dirty_tan`<br><sub>ta/t7_ceramic.gdt</sub><br>instance de `t7_ceramic_tiles_6x6_dirty_01` | `i_t7_ceramic_tiles_6x6_dirty_c`<br>2048 × 2048 px | `#6e594a`<br><sub>teinte ×(0.607843 0.489128 0.409995)</sub> | 64 × 64<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : carreaux de sol (grille de petits carrés) brun-ocre ; ce ne sont pas des tuiles. |

#### Rive, bardage et panneaux de bois bruns

Utilisé aujourd'hui : `rive` → `t7_wood_trim_dark_brown`, `panneau` → `t7_wood_panel_01_stain_brown_drk`, `ecorce` → `t7_wood_beam_worn_oak`.

**Avis.** Rive et chevrons : bandes 1024 × 64 (t7_wood_trim_dark_brown). Panneaux bruns horizontaux « type persiennes » de la fiche : bardage t7_metal_wall_corrugated_hor_brown_drk ou le bois t7_wood_panel_01_stain_brown_drk (matériau le plus employé des .map officiels).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_wood_trim_dark_brown`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_trim_dark_brown_c`<br>1024 × 64 px | `#594330` | 64 × 4<br><sub>stock : 170 faces sur 195</sub><br><sub>projet ×1,25 : 80 × 5</sub> | Vu : bande brun foncé 16:1, veinage fin. Stock : 64 × 4. <sub>[raccord des bords douteux (mesuré)]</sub> |
| recommandé (4/5) | `t7_wood_panel_01_stain_brown_drk`<br><sub>ta/t7_wood.gdt</sub><br>instance de `t7_wood_panel_01` | `i_t7_wood_panel_01_c`<br>2048 × 2048 px | `#41281c`<br><sub>teinte ×(0.447059 0.35404 0.303304)</sub> | 64 × 64<br><sub>stock : 4662 faces sur 4662</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brun chocolat très foncé uni, fil vertical fin, 2048 px ; stock : 64 × 64, c'est le matériau le plus utilisé des maps officielles. Déduit : une rotation de projection de 90° donnerait des panneaux horizontaux. |
| recommandé (3/5) | `t7_metal_wall_corrugated_hor_brown_drk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_wall_corrugated_hor` | `i_t7_metal_wall_corrugated_hor_c`<br>2048 × 2048 px | `#3e3124`<br><sub>teinte ×(0.305882 0.244495 0.178729)</sub> | 64 × 64<br><sub>stock : 64 faces sur 68</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales brun foncé, légères rayures ; stock : 64 × 64. Rend bien les « panneaux bruns horizontaux » de la fiche. |
| alternative (3/5) | `t7_wood_trim_brown_01`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_trim_brown_01_c`<br>1024 × 128 px | `#5a4530` | 64 × 8<br><sub>stock : 62 faces sur 139</sub><br><sub>projet ×1,25 : 80 × 10</sub> | Vu : bande 1024 × 128 plus large et plus claire ; stock : 64 × 8. <sub>[raccord des bords douteux (mesuré)]</sub> |
| alternative (3/5) | `t7_wood_worn_darker_brown`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_worn_dark_brown_c`<br>1024 × 1024 px | `#513926` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brun foncé uni à peine vieilli. |
| limité (2/5) | `t7_wood_planks_rustic`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_planks_rustic_c`<br>1024 × 1024 px | `#6e6153` | 64 × 64<br><sub>stock : 1250 faces sur 1455</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : planches grisâtres très vieillies, aspect cabane ; stock : 64 × 64. |
| limité (2/5) | `t7_wood_beam_worn_oak`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_beam_worn_oak_c`<br>256 × 1024 px | `#7b593d` | 16 × 64<br><sub>stock : 201 faces sur 478</sub><br><sub>projet ×1,25 : 20 × 80</sub> | Vu : poutre étroite 256 × 1024 brun roux. Utilisé comme « écorce » : ce n'est pas une écorce, juste un bois. |

### Ouvertures et volets

#### Menuiseries de fenêtre blanches

Utilisé aujourd'hui : `fenetre` → `core_window_opaque`.

**Avis.** PVC blanc : t7_plastic_base_clean. L'actuel core_window_opaque est une fenêtre complète (cadre blanc à petits bois et vitrage) en 512 px : pratique sur une seule face, mais ni modulaire ni haute définition.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_plastic_base_clean`<br><sub>ta/t7_plastic.gdt</sub> | `i_t7_plastic_base_clean_c`<br>1024 × 1024 px | `#eaeaea` | 64 × 64<br><sub>stock : 80 faces sur 180</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc franc, 1024 px, sans relief ; existe aussi en gris et noir. À utiliser pour des cadres construits en brushes autour d'une vitre. |
| alternative (3/5) | `core_window_opaque`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_window_opaque_c`<br>512 × 512 px | `#5a6061` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : cadre blanc à petits bois et vitre gris sombre, quatre fenêtres par tuile, 512 px. Exige que chaque face de fenêtre ait la bonne taille de projection. Actuel « fenetre ». <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (2/5) | `t7_metal_painted_wall_dirty_grey`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_painted_wall_dirty_grey_c`<br>1024 × 1024 px | `#eeeeee` | 64 × 64<br><sub>stock de la variante `t7_metal_painted_wall_dirty_black` : 156 faces sur 156</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc uni (nom trompeur). |
| limité (3/5) | `t7_plastic_molding_trim_white`<br><sub>ta/t7_plastic.gdt</sub> | `i_t7_plastic_molding_trim_white_c`<br>1024 × 256 px | `#b7b6b6` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : profilé blanc 1024 × 256 ; pour un encadrement ou un appui. |
| limité (2/5) | `t7_metal_painted_clean_white`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_painted_clean_white_c`<br>1024 × 1024 px | `#9e9e9c` | 64 × 64<br><sub>stock : 558 faces sur 1142</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris clair seulement (teinte 0,7) ; actuel « boites ». |
| à éviter (1/5) | `t7_wood_varnished_clean_white`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_varnished_clean_white_c`<br>1024 × 1024 px | `#a4a4a2` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : gris, pas blanc. <sub>[drapeau doNotUse (hérité)]</sub> |

#### Menuiseries brunes (portes, loggias)

Utilisé aujourd'hui : `loggia` → `t7_drywall_painted_brown_01`, `porte` → `core_door_wood_dark`.

**Avis.** Bruns disponibles : bois très foncé (t7_wood_panel_01_stain_brown_drk), brun vieilli (t7_wood_worn_darker_brown) et peinture brun olive (t7_drywall_painted_brown_01, actuel des loggias).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_wood_panel_01_stain_brown_drk`<br><sub>ta/t7_wood.gdt</sub><br>instance de `t7_wood_panel_01` | `i_t7_wood_panel_01_c`<br>2048 × 2048 px | `#41281c`<br><sub>teinte ×(0.447059 0.35404 0.303304)</sub> | 64 × 64<br><sub>stock : 4662 faces sur 4662</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brun chocolat très foncé, uni et propre. |
| alternative (3/5) | `t7_wood_worn_darker_brown`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_worn_dark_brown_c`<br>1024 × 1024 px | `#513926` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brun foncé légèrement vieilli, 1024 px. |
| alternative (3/5) | `t7_drywall_painted_brown_01`<br><sub>ta/t7_plaster.gdt</sub><br>instance de `t7_drywall_painted_white_01` | `i_t7_drywall_paited_white_c`<br>1024 × 1024 px | `#524d43`<br><sub>teinte ×(0.4 0.372549 0.337255)</sub> | 64 × 64<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : brun olive uni, 1024 px, type cloison. Actuel « loggia » ; plat mais propre. |
| alternative (3/5) | `core_door_wood_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_door_wood_dark_c`<br>256 × 512 px | `#684b38` | 32 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : porte à panneaux moulurés en bois sombre, 256 × 512 px ; actuel « porte » (la texture est une porte entière, pas un bois). <sub>[raccord des bords douteux (mesuré) ; drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_metal_wall_corrugated_hor_brown_drk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_wall_corrugated_hor` | `i_t7_metal_wall_corrugated_hor_c`<br>2048 × 2048 px | `#3e3124`<br><sub>teinte ×(0.305882 0.244495 0.178729)</sub> | 64 × 64<br><sub>stock : 64 faces sur 68</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales brunes ; pour volets ou panneaux. |
| limité (3/5) | `t7_wood_trim_dark_brown`<br><sub>ta/t7_wood.gdt</sub> | `i_t7_wood_trim_dark_brown_c`<br>1024 × 64 px | `#594330` | 64 × 4<br><sub>stock : 170 faces sur 195</sub><br><sub>projet ×1,25 : 80 × 5</sub> | Vu : bande 16:1 pour liserés et chambranles. <sub>[raccord des bords douteux (mesuré)]</sub> |

#### Vitrage

Utilisé aujourd'hui : `vitre` → `core_glass_plain_trans`.

**Avis.** Types de verre du moteur : glass, lit_transparent_backlit, glass_nocolor. Leur rendu (reflets, transparence) n'est pas vérifiable sans lancer le jeu ; l'actuel core_glass_plain_trans est déjà compilé.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_glass_clean_01_transparent`<br><sub>ta/t7_glass.gdt</sub><br>instance de `t7_glass_clean_01` | `i_t7_glass_grey_50_c`<br>8 × 8 px<br>alpha uniforme (127) | `#222222`<br><sub>teinte ×(0.164706 0.164706 0.164706)</sub> | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : type glass, alpha uniforme 127 (50 %), teinte 0,16 : le verre propre moderne de Treyarch (usage « window »). Inconnu : intensité des reflets sur un panneau plat. |
| alternative (3/5) | `core_glass_plain_trans`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_glass_plain_c`<br>256 × 256 px<br>alpha faible partout (19 à 42) | `#596565` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : type glass, alpha uniforme faible (19 à 42), 256 px ; déjà compilé dans zm_seyssel. Actuel « vitre ». <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_glass_dirty_streaks`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_dirty_streaks_c`<br>2048 × 2048 px<br>alpha faible partout (66 à 111) | `#505352` | 128 × 128<br><sub>stock : 112 faces sur 162</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : verre avec traînées de poussière, 2048 px, alpha 66 à 111 (glass_nocolor) ; apporte du réalisme aux vitres de cage d'escalier. |
| alternative (3/5) | `t7_glass_frosted_cold`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_frosted_cold_c`<br>1024 × 1024 px<br>alpha faible partout (39 à 175) | `#333333` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : verre dépoli froid, 1024 px, alpha 39 à 175 ; pour portes de halls, salles de bain, imposte. |
| alternative (3/5) | `t7_glass_reinforced_01`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_reinforced_01_c`<br>1024 × 1024 px<br>alpha : 65 % des pixels sous 50 % | `#4c7b7b` | 64 × 64<br><sub>stock : 50 faces sur 50</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : verre armé turquoise à motif de losanges, alpha 115 à 237. Déduit : ressemble aux vitres de cages d'escalier d'HLM. |
| limité (2/5) | `t7_glass_plain_translucent`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_plain_translucent_c`<br>2048 × 2048 px<br>alpha faible partout (23 à 40) | `#111111` | 64 × 64<br><sub>stock : 80 faces sur 80</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : type lit_transparent_backlit, image quasi noire, alpha très bas : vitre sombre. |
| limité (2/5) | `t7_glass_smoked`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_smoked_c`<br>1024 × 1024 px<br>alpha faible partout (12 à 41) | `#080604` | 64 × 64<br><sub>stock : 88 faces sur 88</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : verre fumé presque noir ; pour vitrines ou portes de garage vitrées. |

#### Volets roulants et persiennes

Utilisé aujourd'hui : `volet` → `t7_drywall_painted_beige_01`.

**Avis.** Pas de volet roulant en texture « toute faite », mais plusieurs bardages à lames horizontales : t7_metal_wall_corrugated_panel_hor_grey (gris), t7_metal_wall_corrugated_hor (blanc cassé), t7_metal_wall_corrugated_hor_brown_drk (brun). Pour de vraies persiennes à lames : le modèle p7_louver_window_wooden_closed (§7).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_metal_wall_corrugated_panel_hor_grey`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_wall_corrugated_panel_hor` | `i_t7_metal_wall_corrugated_panel_hor_c`<br>2048 × 2048 px | `#5d6066`<br><sub>teinte ×(0.45098 0.466667 0.501961)</sub> | 64 × 64<br><sub>stock : 16 faces sur 18</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales gris bleuté nettes, 2048 px ; stock : 64 × 64. Se lit comme un volet roulant fermé. |
| alternative (3/5) | `t7_metal_wall_corrugated_hor`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_wall_corrugated_hor_c`<br>2048 × 2048 px | `#cbcac9` | 64 × 64<br><sub>stock de la variante `t7_metal_wall_corrugated_hor_brown_drk` : 64 faces sur 68</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales blanc cassé légèrement sales, 2048 px ; volet roulant blanc. |
| alternative (3/5) | `t7_metal_wall_corrugated_hor_brown_drk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_wall_corrugated_hor` | `i_t7_metal_wall_corrugated_hor_c`<br>2048 × 2048 px | `#3e3124`<br><sub>teinte ×(0.305882 0.244495 0.178729)</sub> | 64 × 64<br><sub>stock : 64 faces sur 68</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : lames horizontales brun foncé ; volets bruns. |
| limité (2/5) | `t7_metal_panel_horizontal_painted`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_panel_horizontal_painted_c`<br>2048 × 1024 px | `#b5afa3` | 64 × 32<br><sub>estimée, à régler à l'œil</sub> | Vu : panneaux peints blanc-beige avec coulures de rouille, 2048 × 1024 ; effet vieux bardage. <sub>[raccord des bords douteux (mesuré)]</sub> |
| limité (2/5) | `t7_cloth_blinds_striped_01`<br><sub>ta/t7_cloth.gdt</sub> | `i_t7_cloth_blinds_striped_01_c`<br>1024 × 1024 px<br>alpha : 48 % des pixels sous 50 % | `#574d44` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : stores en tissu rayé brun et gris ; type lit_transparent_nocull (alpha 100 à 254). Ressemble à un store intérieur, pas à un volet. <sub>[raccord des bords douteux (mesuré)]</sub> |
| à éviter (1/5) | `t7_glass_slats`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_slats_c`<br>512 × 512 px<br>alpha : 6 % des pixels sous 50 % | `#0b3646` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : lames turquoise (teinte 0,05 / 0,28 / 0,36) de type lit_backlit : verre à lamelles, pas un volet. |

### Balcons et garde-corps

#### Garde-corps métal peint : barreaudage

Utilisé aujourd'hui : `garde_corps` → `t7_metal_worn_iron_dark`.

**Avis.** Aucune texture de barreaux verticaux n'existe. Pour un vrai barreaudage : brushes fins (comme dans immeuble.py) avec un métal peint uni. Pour un garde-corps ajouré à moindre coût : les cartes à alpha (câbles en losanges, métal déployé, tôle perforée), dont le canal alpha est bien présent (mesuré).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_metal_paint_worn_grey_dk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_paint_worn_white` | `i_t7_metal_paint_worn_white_c`<br>1024 × 1024 px | `#414141`<br><sub>teinte ×(0.403922 0.403922 0.403922)</sub> | 64 × 64<br><sub>stock : 170 faces sur 170</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris anthracite uni peint, grain très fin ; pour barreaux et main courante en brushes. Actuel « auvent ». |
| alternative (3/5) | `t7_metal_worn_iron_dark`<br><sub>ta/t7_metal.gdt</sub> | `$black_color` (couleur uniforme) | n/m | 64 × 64<br><sub>stock : 5958 faces sur 6656</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : colorMap noire uniforme avec micro-textures (lit_micro_tile_blend_advanced) : aspect fer brut plutôt que peint. Stock : 64 × 64. Actuel « garde_corps ». |
| alternative (2/5) | `t7_metal_fence_post_cable`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_fence_post_cable_c`<br>1024 × 1024 px<br>alpha : 80 % des pixels sous 50 % | `#343533` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : treillis de câbles en losanges sur fond transparent (alpha : environ 80 % transparent), 1024 px ; type lit_alphatest. Inconnu : visible des deux côtés ou non. |
| alternative (2/5) | `t7_metal_grating_expanded`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_grating_expanded_c`<br>1024 × 1024 px<br>alpha : 53 % des pixels sous 50 % | `#7d7d7d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : métal déployé, environ 53 % transparent, 1024 px ; garde-corps ajouré industriel. |
| alternative (2/5) | `t7_metal_perforated_small_white`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_perforated_white_c`<br>1024 × 1024 px<br>alpha : 23 % des pixels sous 50 % | `#ededed` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : tôle perforée blanche, environ 23 % transparente ; allège perforée. |
| alternative (2/5) | `t7_metal_painted_wall_dirty_black`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_painted_wall_dirty_grey` | `i_t7_metal_painted_wall_dirty_grey_c`<br>1024 × 1024 px | `#2d2d2d`<br><sub>teinte ×(0.188235 0.188235 0.188235)</sub> | 64 × 64<br><sub>stock : 156 faces sur 156</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : noir uni très propre (teinte 0,19) ; main courante noire. |

#### Garde-corps métal peint : allège pleine

Utilisé aujourd'hui : `garde_corps` → `t7_metal_worn_iron_dark`.

**Avis.** Allège pleine en tôle peinte : panneaux gris (t7_metal_panels_painted_2x1_grey) ou graphite uni. Les teintes gris moyen vont bien avec un enduit beige.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_metal_panels_painted_2x1_grey`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_panels_painted_2x1` | `i_t7_metal_panels_painted_2x1_c`<br>2048 × 2048 px | `#777b7c`<br><sub>teinte ×(0.568627 0.588235 0.592157)</sub> | 128 × 128<br><sub>stock : 62 faces sur 66</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : panneaux de tôle peinte gris, joints fins nets, 2048 px ; stock : 128 × 128. |
| alternative (3/5) | `t7_metal_panel_horizontal_painted_grey`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_panel_horizontal_painted` | `i_t7_metal_panel_horizontal_painted_c`<br>2048 × 1024 px | `#6e706b`<br><sub>teinte ×(0.552941 0.580392 0.568627)</sub> | 64 × 32<br><sub>estimée, à régler à l'œil</sub> | Vu : panneaux horizontaux gris-vert avec légères coulures, 2048 × 1024 px. <sub>[raccord des bords douteux (mesuré)]</sub> |
| alternative (3/5) | `t7_metal_worn_painted_graphite`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_worn_painted_graphite_c`<br>1024 × 1024 px | `#363637` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : graphite très uni, quasi sans grain ; allège sombre. Stock (variante t7_metal_worn_painted_white) : 64 × 64. |
| alternative (3/5) | `t7_metal_panels_4x1_grey_drk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_panels_4x1` | `i_t7_metal_panels_4x1_c`<br>2048 × 2048 px | `#3e3f42`<br><sub>teinte ×(0.313725 0.31986 0.333333)</sub> | 128 × 128<br><sub>stock : 22 faces sur 30</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris foncé bleuté uni, joints à peine visibles ; stock : 128 × 128. |
| alternative (2/5) | `t7_metal_panels_painted_2x4`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_panels_painted_2x4_c`<br>2048 × 2048 px | `#c9c9c9` | 128 × 128<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : panneaux blancs striés 2 × 4 ; allège blanche. Stock : 128 × 128. <sub>[raccord des bords douteux (mesuré)]</sub> |
| limité (2/5) | `t7_metal_painted_wall_dirty_grey`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_painted_wall_dirty_grey_c`<br>1024 × 1024 px | `#eeeeee` | 64 × 64<br><sub>stock de la variante `t7_metal_painted_wall_dirty_black` : 156 faces sur 156</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc uni, sans joint. |

#### Dalle et nez de balcon

Utilisé aujourd'hui : `dalle_balcon` → `t7_concrete_floor_sealed_01`, `balcon` → `t7_concrete_worn_painted_white`, `appui` → `t7_concrete_trim_beveled_03`.

**Avis.** Dessus de dalle : béton brut sec ; tranche : bande chanfreinée 4:1 (t7_concrete_trim_beveled_03) ou plinthe 8:1 (t7_concrete_floor_trim_01) en respectant leurs proportions.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_concrete_bare_weathered_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_bare_weathered_01_c`<br>2048 × 2048 px | `#a3a39d` | 64 × 64<br><sub>stock : 22 faces sur 40</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : béton gris clair granuleux, sans motif répétitif gênant. |
| recommandé (3/5) | `t7_concrete_trim_beveled_03`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_trim_beveled_03_c`<br>1024 × 256 px | `#78746a` | 128 × 32<br><sub>stock : 74 faces sur 248</sub><br><sub>projet ×1,25 : 160 × 40</sub> | Vu : tranche chanfreinée 1024 × 256 ; stock : 128 × 32 ou 64 × 16. Actuel « appui ». |
| alternative (3/5) | `t7_concrete_floor_sealed_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_wall_weathered_01_c`<br>2048 × 2048 px | `#827d70` | 128 × 128<br><sub>stock de la variante `t7_concrete_wall_weathered_01_wet` : 893 faces sur 1041</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : béton marbré, version sèche ; actuel « dalle_balcon ». |
| alternative (3/5) | `t7_concrete_floor_trim_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_floor_trim_01_c`<br>1024 × 128 px | `#757069` | 32 × 4<br><sub>stock : 22 faces sur 75</sub><br><sub>projet ×1,25 : 40 × 5</sub> | Vu : plinthe 1024 × 128, rapport 8:1 ; stock : 32 × 4 ou 112 × 14. |
| limité (2/5) | `t7_concrete_slabs_interlocked`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_slabs_interlocked_c`<br>2048 × 2048 px | `#95908b` | 64 × 64<br><sub>stock : 22 faces sur 22</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles de béton emboîtées gris clair ; plutôt un sol extérieur. |
| limité (2/5) | `t7_concrete_brushed_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_brushed_01_c`<br>1024 × 1024 px | `#848079` | 64 × 64<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : béton balayé très bruité ; aspect de terrasse. |

### Halls, portes et boîtes

#### Porte vitrée de hall

Utilisé aujourd'hui : `vitre` → `core_glass_plain_trans`, `porte` → `core_door_wood_dark`, `auvent` → `t7_metal_paint_worn_grey_dk`.

**Avis.** Il n'existe pas de « porte vitrée » toute faite. Assemblage conseillé : cadre métal (alu brossé ou peint) + vitre transparente, en brushes. Les modèles de portes disponibles sont industriels ou de laboratoire (§7).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_glass_clean_01_transparent`<br><sub>ta/t7_glass.gdt</sub><br>instance de `t7_glass_clean_01` | `i_t7_glass_grey_50_c`<br>8 × 8 px<br>alpha uniforme (127) | `#222222`<br><sub>teinte ×(0.164706 0.164706 0.164706)</sub> | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : verre propre transparent (alpha 127) ; pour la vitre. |
| recommandé (3/5) | `t7_metal_bare_aluminum_brushed`<br><sub>ta/t7_metal.gdt</sub> | `$black_color` (couleur uniforme) | n/m | n/m | Vu dans le GDT : aluminium brossé, type lit_advanced sans colorMap (la couleur vient du spéculaire, non mesuré) ; pour les montants. |
| alternative (3/5) | `t7_metal_trim_painted_black`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_trim_chrome` | `$gray_color` (couleur uniforme) | n/m<br><sub>teinte ×(0.270588 0.270588 0.270588)</sub> | n/m | Vu dans le GDT : peinture noire (teinte 0,27 sur une image grise uniforme) ; cadre noir. <sub>[images liées absentes : i_t7_metal_trim_flashing_r]</sub> |
| alternative (3/5) | `t7_plastic_base_clean`<br><sub>ta/t7_plastic.gdt</sub> | `i_t7_plastic_base_clean_c`<br>1024 × 1024 px | `#eaeaea` | 64 × 64<br><sub>stock : 80 faces sur 180</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : blanc franc ; cadre PVC blanc. |
| alternative (3/5) | `t7_glass_frosted_cold`<br><sub>ta/t7_glass.gdt</sub> | `i_t7_glass_frosted_cold_c`<br>1024 × 1024 px<br>alpha faible partout (39 à 175) | `#333333` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : verre dépoli ; pour un panneau latéral ou une imposte. |
| limité (2/5) | `t7_metal_frame_trim_01`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_frame_trim_01_c`<br>1024 × 64 px | `#353636` | 64 × 4<br><sub>stock : 80 faces sur 130</sub><br><sub>projet ×1,25 : 80 × 5</sub> | Vu : profilé foncé 1024 × 64 à rivets, usage « window » ; stock : 64 × 4. |

#### Portes de garage

Utilisé aujourd'hui : `garage` → `core_door_metal_light`.

**Avis.** Le « garage » actuel (core_door_metal_light) est un métal nu clair sans image de couleur ni panneaux. Pour des portes basculantes peintes : panneaux gris ou blancs. Pour un rideau roulant : modèle p7_door_metal_rolling_02.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_metal_panel_horizontal_painted_grey`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_panel_horizontal_painted` | `i_t7_metal_panel_horizontal_painted_c`<br>2048 × 1024 px | `#6e706b`<br><sub>teinte ×(0.552941 0.580392 0.568627)</sub> | 64 × 32<br><sub>estimée, à régler à l'œil</sub> | Vu : panneaux horizontaux gris-vert, 2048 × 1024 px ; lit comme une porte de garage basculante. <sub>[raccord des bords douteux (mesuré)]</sub> |
| alternative (3/5) | `t7_metal_panels_painted_2x4`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_panels_painted_2x4_c`<br>2048 × 2048 px | `#c9c9c9` | 128 × 128<br><sub>stock : 8 faces sur 8</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : panneaux blancs striés 2 × 4 ; porte de garage blanche. Stock : 128 × 128. <sub>[raccord des bords douteux (mesuré)]</sub> |
| alternative (3/5) | `core_door_metal_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_door_metal_dark_c`<br>256 × 512 px | `#787571` | 32 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : porte métallique grise avec cadre et panneau, 256 × 512 px ; basse définition. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (2/5) | `t7_metal_garage_door_rollup_01_bare`<br><sub>ta/t7_metal.gdt</sub> | `$black_color` (couleur uniforme) | n/m | 64 × 64<br><sub>stock de la variante `t7_metal_garage_door_rollup_01_bare_wet` : 10 faces sur 12</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu dans le GDT : rideau métallique à normales rainurées, micro-matériau sans colorMap ; stock (variante _wet) : 64 × 64. |
| limité (2/5) | `core_door_metal_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `$black_color` (couleur uniforme) | n/m | n/m | Vu dans le GDT : lit_advanced sans colorMap, couleur portée par le spéculaire : métal nu clair sans panneaux. Actuel « garage ». <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `t7_metal_paint_worn_grey_dk`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_paint_worn_white` | `i_t7_metal_paint_worn_white_c`<br>1024 × 1024 px | `#414141`<br><sub>teinte ×(0.403922 0.403922 0.403922)</sub> | 64 × 64<br><sub>stock : 170 faces sur 170</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris anthracite uni ; porte sombre sans détail. |

#### Boîtes aux lettres

Utilisé aujourd'hui : `boites` → `t7_metal_painted_clean_white`.

**Avis.** Ni modèle ni texture de boîtes aux lettres n'existent. Construire un bloc de boîtes en brushes (comme dans immeuble.py) avec un métal peint : alu brossé, jaune ou gris.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_metal_bare_aluminum_brushed`<br><sub>ta/t7_metal.gdt</sub> | `$black_color` (couleur uniforme) | n/m | n/m | Vu dans le GDT : aluminium brossé (type lit_advanced) ; boîtes aux lettres en alu. |
| alternative (3/5) | `t7_metal_paint_worn_yellow`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_paint_worn_white` | `i_t7_metal_paint_worn_white_c`<br>1024 × 1024 px | `#917240`<br><sub>teinte ×(0.898039 0.709804 0.4)</sub> | 64 × 64<br><sub>stock : 18 faces sur 18</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : jaune moutarde uni légèrement usé ; boîtes jaunes. |
| alternative (2/5) | `t7_metal_painted_clean_white`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_painted_clean_white_c`<br>1024 × 1024 px | `#9e9e9c` | 64 × 64<br><sub>stock : 558 faces sur 1142</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gris clair uni ; actuel « boites ». |
| limité (2/5) | `t7_metal_panels_painted_2x1_yellow`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_panels_painted_2x1` | `i_t7_metal_panels_painted_2x1_c`<br>2048 × 2048 px | `#bc9521`<br><sub>teinte ×(0.894118 0.709804 0.156863)</sub> | 124 × 138<br><sub>stock : 6 faces sur 6</sub><br><sub>projet ×1,25 : 155 × 172,5</sub> | Vu : panneaux jaunes à joints ; trop industriel. |

### Voirie et sols urbains

#### Asphalte neuf

Utilisé aujourd'hui : `asphalte` → `t7_asphalt_dirty_dark_desert`.

**Avis.** L'actuel t7_asphalt_dirty_dark_desert est un asphalte « désert » à plages brun-ocre marquées, peu alpin et répétitif. core_asphault_dark (sic, l'orthographe d'origine) est un enrobé sombre fin, plus neutre.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `core_asphault_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_asphalt_dark_c`<br>512 × 512 px | `#4d4d4b` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : gris anthracite fin, pores minuscules, 512 px ; ressemble à un enrobé récent. Variante _wet existe. Le nom contient bien la faute « asphault ». <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_asphalt_advanced_strips`<br><sub>ta/t7_asphalt.gdt</sub> | `i_t7_asphalt_advanced_strips_c`<br>2048 × 2048 px | `#353531` | 128 × 128<br><sub>stock : 42 faces sur 42</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : très sombre avec une grille de bandes de reprise, 2048 px ; stock : 128 × 128. Donne un enrobé neuf rapiécé. |
| limité (2/5) | `t7_asphalt_bleached_desert`<br><sub>ta/t7_asphalt.gdt</sub> | `i_t7_asphalt_bleached_desert_c`<br>1024 × 1024 px | `#77726a` | 350.6 × 329.3<br><sub>stock : 10 faces sur 10</sub><br><sub>projet ×1,25 : 438,2 × 411,6</sub> | Vu : gris-beige clair délavé ; trop clair et chaud pour une rue. |
| limité (1/5) | `core_asphault_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_asphalt_light_c`<br>64 × 64 px | `#7d7e7d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : 64 × 64 px, gris-bleu moucheté ; trop flou. **Réserve :** 64 px. <sub>[drapeau doNotUse (hérité)]</sub> |
| à éviter (2/5) | `t7_asphalt_dirty_dark_desert`<br><sub>ta/t7_asphalt.gdt</sub> | `i_t7_asphalt_dirty_dark_desert_c`<br>1024 × 1024 px | `#56524b` | 64 × 64<br><sub>stock : 62 faces sur 86</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : plages brun-ocre sur fond gris, 1024 px ; actuel « asphalte ». Stock : 64 × 64. Répétition lisible. |

#### Asphalte usé

**Avis.** Pour un enrobé fissuré : t7_asphalt_damaged_dark_wet (fissures en peau de crocodile, 2048 px). Sa variante _nw est le même matériau avec un canal supplémentaire ($white_reveal).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_asphalt_damaged_dark_wet`<br><sub>ta/t7_asphalt.gdt</sub> | `i_t7_asphalt_damaged_dark_c`<br>2048 × 2048 px | `#423f3c` | 128 × 128<br><sub>stock de la variante `t7_asphalt_damaged_dark_wet_nw` : 9 faces sur 10</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : réseau de fissures sur fond noir-brun, 2048 px ; stock (variante _nw) : 128 × 128. Le nom contient « wet » : carte de normales mouillée (déduit). |
| alternative (4/5) | `t7_asphalt_damaged_dark_wet_nw`<br><sub>ta/t7_asphalt.gdt</sub><br>instance de `t7_asphalt_damaged_dark_wet` | `i_t7_asphalt_damaged_dark_c`<br>2048 × 2048 px | `#423f3c` | 128 × 128<br><sub>stock : 9 faces sur 10</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu dans le GDT : instance du précédent qui ne change que colorMap14 ($white_reveal). Inconnu : ce que « nw » désigne. |
| alternative (3/5) | `core_asphault_med`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_asphalt_med_c`<br>512 × 512 px | `#636363` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : gris-bleu à fissures fines, 512 px. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_concrete_floor_garage_cracked_wet_nw`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_floor_garage_cracked_c`<br>2048 × 2048 px | `#76756e` | 128 × 128<br><sub>stock : 29 faces sur 29</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : béton fissuré de parking, 2048 px ; stock : 128 × 128. Pour un parking ou une allée de garages. |
| limité (2/5) | `t7_asphalt_dirty_dark_desert`<br><sub>ta/t7_asphalt.gdt</sub> | `i_t7_asphalt_dirty_dark_desert_c`<br>1024 × 1024 px | `#56524b` | 64 × 64<br><sub>stock : 62 faces sur 86</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : plages brun-ocre ; actuel « asphalte ». |

#### Marquages routiers blancs et jaunes

**Avis.** Les marquages existent comme décalques : t7_decal_signage_street_lines_white et _yellow (2048 × 256, ligne continue). Leur type lit_decal_reveal demande une carte de révélation (présente) et un brush « décalque ; le rendu n'est pas testé ici. Alternative sûre : bordures peintes (t7_street_concrete_curb_01a_white / _yellow).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| alternative (3/5) | `t7_decal_signage_street_lines_white`<br><sub>ta/t7_decal_signage.gdt</sub> | `i_t7_decal_signage_street_lines_white_c`<br>2048 × 256 px | `#a5a49a` | 64 × 8<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : lit_decal_reveal, couche « Signage - Old », usage « exterior trim ». Image 2048 × 256 de ligne continue sale. À tester sur un brush mince posé sur la route. **Réserve :** Décalque non testé. |
| alternative (3/5) | `t7_decal_signage_street_lines_yellow`<br><sub>ta/t7_decal_signage.gdt</sub> | `i_t7_decal_signage_street_lines_white_c`<br>2048 × 256 px | `#897024` | 64 × 8<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : même image que le blanc avec une teinte jaune (0,83 / 0,68 / 0,23). **Réserve :** Décalque non testé. |
| alternative (3/5) | `t7_street_concrete_curb_01a_yellow`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_yellow_c`<br>1024 × 256 px | `#837e6b` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : bordure grise à bandes jaunes (marquage de stationnement interdit), 1024 × 256. |
| alternative (3/5) | `t7_street_concrete_curb_01a_white`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_white_c`<br>1024 × 256 px | `#87857d` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : bordure à bandes blanches, 1024 × 256. |
| limité (2/5) | `t7_street_concrete_curb_01a_white_solid`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_white_solid_c`<br>1024 × 256 px | `#aaa8a3` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : bordure entièrement blanche. |

#### Trottoir

Utilisé aujourd'hui : `trottoir` → `t7_concrete_sidewalk_02`.

**Avis.** t7_concrete_sidewalk_02 est un béton gris tiède uniforme, sans motif visible : le meilleur trottoir. Les variantes à joints (sidewalk_01, 2x2_01) donnent des dalles.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_concrete_sidewalk_02`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_sidewalk_02_c`<br>1024 × 1024 px | `#79736b` | 64 × 64<br><sub>stock : 94 faces sur 104</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : béton gris tiède fin, très uniforme, aucun motif répétitif ; stock : 64 × 64. Actuel « trottoir ». |
| alternative (3/5) | `t7_concrete_sidewalk_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_sidewalk_01_c`<br>1024 × 1024 px | `#8f8880` | 64 × 64<br><sub>stock : 58 faces sur 58</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles carrées (4 × 4 par tuile) gris-beige à joints visibles ; stock : 64 × 64. |
| alternative (3/5) | `t7_concrete_sidewalk_2x2_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_sidewalk_2x2_01_c`<br>2048 × 2048 px | `#908b83` | 128 × 128<br><sub>stock : 16 faces sur 16</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : dalles 2 × 2 gris clair à joints nets, 2048 px ; stock : 128 × 128. |
| limité (2/5) | `t7_concrete_tiles_2x2_dirty_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_tiles_2x2_dirty_01_c`<br>1024 × 1024 px | `#494844` | 64 × 64<br><sub>stock : 2 faces sur 2</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles gris sombre sales ; plutôt un parking. |
| limité (2/5) | `t7_concrete_slabs_interlocked`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_slabs_interlocked_c`<br>2048 × 2048 px | `#95908b` | 64 × 64<br><sub>stock : 22 faces sur 22</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles emboîtées gris clair ; sol de place. |

#### Bordure

Utilisé aujourd'hui : `bordure` → `t7_street_concrete_curb_01a`.

**Avis.** Le matériau actuel est le bon, mais il est étiré : 1024 × 256 mappé en 256 × 256. Le modèle p7_street_curb_concrete_64a/b (§7) donne une bordure déjà modélisée.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_street_concrete_curb_01a`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_c`<br>1024 × 256 px | `#817e76` | 64 × 16<br><sub>stock : 36 faces sur 36</sub><br><sub>projet ×1,25 : 80 × 20</sub> | Vu : bordure grise avec arête et face, bande 1024 × 256 ; stock : 64 × 16. Actuel « bordure ». À mapper en 4:1. |
| alternative (3/5) | `t7_street_concrete_curb_01b`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01b_c`<br>1024 × 256 px | `#8a877d` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : variante de teinte et de motif ; 1024 × 256. |
| alternative (3/5) | `t7_concrete_trim_beveled_01_wet`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_trim_beveled_01_c`<br>1024 × 256 px | `#75746c` | 64 × 16<br><sub>stock : 1425 faces sur 1767</sub><br><sub>projet ×1,25 : 80 × 20</sub> | Vu dans le GDT : tranche chanfreinée 1024 × 256, la plus employée des maps officielles (64 × 16) ; variante mouillée. |
| alternative (3/5) | `t7_street_concrete_curb_01a_white`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_white_c`<br>1024 × 256 px | `#87857d` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : version peinte en blanc par bandes. |
| alternative (3/5) | `t7_street_concrete_curb_01a_yellow`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_street_concrete_curb_01a_yellow_c`<br>1024 × 256 px | `#837e6b` | 64 × 16<br><sub>estimée, à régler à l'œil</sub> | Vu : version peinte en jaune par bandes. |

#### Pavés et dalles

**Avis.** Pavés rectangulaires de ville : t7_stone_cobblestone_01_wet_nw (le seul pavé régulier). Les dalles emboîtées de béton font un « pavé autobloquant » acceptable pour un parking.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_stone_cobblestone_01_wet_nw`<br><sub>ta/t7_stone.gdt</sub> | `i_t7_stone_cobblestone_01_c`<br>2048 × 2048 px | `#6f6c68` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : pavés rectangulaires gris-brun-rose en appareil régulier, 2048 px ; bien raccordé. Le nom porte « wet » ; carte de normales mouillée (déduit). |
| alternative (3/5) | `t7_concrete_slabs_interlocked`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_slabs_interlocked_c`<br>2048 × 2048 px | `#95908b` | 64 × 64<br><sub>stock : 22 faces sur 22</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles béton emboîtées gris clair, 2048 px ; stock : 64 × 64. Pavage de parking. |
| alternative (2/5) | `t7_rock_cobblestone_round`<br><sub>ta/t7_rock.gdt</sub> | `i_t7_rock_cobblestone_round_c`<br>1024 × 1024 px | `#6b6863` | 64 × 64<br><sub>stock de la variante `t7_rock_cobblestone_round_wet` : 6 faces sur 6</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : galets/pavés ronds gris, 1024 px ; plutôt chemin rustique. |
| limité (2/5) | `t7_concrete_tiles_4x4_dirty_01_grey`<br><sub>ta/t7_concrete.gdt</sub><br>instance de `t7_concrete_tiles_4x4_dirty_01` | `i_t7_concrete_tiles_4x4_dirty_01_c`<br>2048 × 2048 px | `#35342f`<br><sub>teinte ×(0.619608 0.619608 0.619608)</sub> | 64 × 64<br><sub>stock : 118 faces sur 118</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : dalles 4 × 4 gris très sombre ; stock : 64 × 64. |
| limité (2/5) | `t7_stone_flagstone_floor`<br><sub>ta/t7_stone.gdt</sub> | `i_t7_stone_flagstone_floor_c`<br>2048 × 2048 px | `#514744` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : dalles irrégulières brun-rouge, 2048 px ; terrasse, pas rue. |

### Sols naturels et végétation

#### Herbe

Utilisé aujourd'hui : `herbe` → `core_grass_med`, `herbe_sombre` → `core_grass_dark`, `montagne` → `core_grass_dark`, `feuillage` → `core_grass_dark`, `feuillage_clair` → `core_grass_med`.

**Avis.** core_grass_med est la pelouse la plus naturelle (vert moyen uniforme, aucune répétition visible). Les t7_grass_lawn_* sont très sombres. Pour casser l'uniformité : mêler des plaques de t7_grass_crab_low_sparse_green (herbe clairsemée avec terre).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `core_grass_med`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_grass_med_c`<br>512 × 512 px | `#5a6535` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : pelouse vert moyen naturel, uniforme, aucun motif répétitif, 512 px. Actuel « herbe ». <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `core_grass_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_grass_dark_c`<br>512 × 512 px | `#3a421d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : herbe dense plus sombre à petites fleurs blanches, variation marquée mais acceptable ; actuel « herbe_sombre ». <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_grass_crab_low_sparse_green`<br><sub>ta/t7_grass.gdt</sub> | `i_t7_grass_crab_low_sparse_green_c`<br>2048 × 2048 px | `#4e4d33` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : herbe rase clairsemée mêlée de terre brune, 2048 px ; réaliste pour des pelouses usées de quartier. <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `core_grass_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_grass_light_c`<br>512 × 512 px | `#556b4d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : vert bleuté désaturé, uni ; herbe fanée ou lointaine. <sub>[drapeau doNotUse (hérité)]</sub> |
| limité (2/5) | `t7_grass_lawn_medium_small_green_vibrant`<br><sub>ta/t7_grass.gdt</sub><br>instance de `t7_grass_lawn_medium_small_green` | `i_t7_grass_lawn_medium_small_green_c`<br>1024 × 1024 px | `#323e13`<br><sub>teinte ×(0.671611 0.823529 0.406928)</sub> | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : vert très sombre et saturé (teinte 0,67 / 0,82 / 0,41 sur une image déjà sombre). Pelouse de jeu vidéo plutôt que de quartier. |

#### Gravier

Utilisé aujourd'hui : `gravier` → `t7_stone_pebbles_01`.

**Avis.** t7_stone_pebbles_01 (actuel) est un gravillon gris-bleu très fin, sans répétition visible ; core_gravel_dark est plus naturel de près ; core_gravel_light montre des taches fantômes qui se répètent.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `t7_stone_pebbles_01`<br><sub>ta/t7_stone.gdt</sub> | `i_t7_stone_pebbles_01_c`<br>2048 × 2048 px | `#5b595c` | 64 × 64<br><sub>stock : 228 faces sur 252</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : gravillon gris moucheté très uniforme, 2048 px ; stock : 64 × 64. Actuel « gravier ». |
| alternative (3/5) | `core_gravel_dark`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_gravel_dark_c`<br>512 × 512 px | `#626563` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : gravier gris foncé naturel, 512 px, pas de motif visible. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (2/5) | `core_gravel_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_gravel_light_c`<br>512 × 512 px | `#979695` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : gravier clair, mais des taches fantômes se répètent nettement dans une tuile 2 × 2. **Réserve :** Répétition visible. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_stone_pebbles_01_warm`<br><sub>ta/t7_stone.gdt</sub><br>instance de `t7_stone_pebbles_01` | `i_t7_stone_pebbles_01_c`<br>2048 × 2048 px | `#705d49`<br><sub>teinte ×(0.909804 0.773846 0.627939)</sub> | 64 × 64<br><sub>stock : 4 faces sur 4</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : même image en teinte brun chaud (0,91 / 0,77 / 0,63) ; allées de terre-pierre. |
| limité (2/5) | `t7_rock_sand_crumbled_medium`<br><sub>ta/t7_rock.gdt</sub> | `i_t7_rock_sand_crumbled_medium_c`<br>2048 × 2048 px | `#a29481` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : sable grossier beige à cailloux bruns, 2048 px ; chemin de terre. |

#### Terre

Utilisé aujourd'hui : `terre` → `core_dirt_med`.

**Avis.** core_dirt_med (actuel) est une terre brun chaud réaliste mais en 256 px ; core_dirt_light en 512 px est plus définie.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `core_dirt_med`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_dirt_med_c`<br>256 × 256 px | `#7e6d5e` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : terre brun chaud, grain fin, 256 px seulement. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `core_dirt_light`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_dirt_light_c`<br>512 × 512 px | `#9e8e86` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : terre claire rosée à petits cailloux, 512 px. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_dirt_grassy_forest_ground`<br><sub>ta/t7_dirt.gdt</sub> | `i_t7_dirt_grassy_forest_ground_c`<br>1024 × 1024 px | `#4b4337` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : terre sombre de sous-bois, 1024 px ; pied de haie ou massif. |
| limité (2/5) | `t7_mud_ground_dirt_wet_01`<br><sub>ta/t7_mud.gdt</sub> | `i_t7_mud_ground_dirt_wet_01_c`<br>1024 × 1024 px | `#594d43` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : boue brun sombre avec brindilles, aspect mouillé. |
| limité (2/5) | `t7_sand_pebbles_fine`<br><sub>ta/t7_sand.gdt</sub> | `i_t7_sand_pebbles_fine_c`<br>2048 × 2048 px | `#b9aa94` | 106.5 × 128<br><sub>stock de la variante `t7_sand_pebbles_fine_golden` : 12 faces sur 16</sub><br><sub>projet ×1,25 : 133,1 × 160</sub> | Vu : sable beige clair uni, 2048 px ; bac à sable ou chemin. |
| limité (2/5) | `t7_dirt_rocky_01`<br><sub>ta/t7_dirt.gdt</sub> | `i_t7_dirt_rocky_01_c`<br>2048 × 2048 px | `#887b68` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : terre rocailleuse beige floue, 2048 px, peu de détail. |

#### Haies et rideaux d'arbres

**Avis.** Les haies existent en modèles (p7_foliage_hedge_*, §7). En texture : core_foliage_bushline (arbustes sur fond transparent) et core_foliage_treewall (rideau d'arbres), à poser verticalement.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| alternative (2/5) | `core_foliage_bushline`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_foliage_bushline_c`<br>256 × 256 px<br>alpha : 26 % des pixels sous 50 % | `#3f4126` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : arbustes vert sombre sur fond transparent (environ 26 % transparent), 256 px ; carte plane. Type « lit » : le détourage alpha en jeu n'est pas vérifié ici. **Réserve :** Alpha non testé en jeu ; doNotUse. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (2/5) | `core_foliage_treewall`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_foliage_treewall_c`<br>512 × 512 px<br>alpha : 15 % des pixels sous 50 % | `#323221` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : rideau d'arbres feuillus sur fond transparent (environ 15 % transparent), 512 px ; fond de décor. **Réserve :** Alpha non testé en jeu ; doNotUse. <sub>[raccord des bords douteux (mesuré) ; drapeau doNotUse (hérité)]</sub> |

#### Grillage

**Avis.** Deux vrais grillages à mailles losangées avec alpha : core_fence_chain_link (128 px, légère) et t7_metal_chainlink (1024 px, double face). Les pièces de poteaux sont des modèles (§7).

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `core_fence_chain_link`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_fence_chainlink_c`<br>128 × 128 px<br>alpha : 74 % des pixels sous 50 % | `#7b7875` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : RGBA 8 bits, 128 px, environ 74 % transparent, type lit_alphatest (face unique probable) ; maille argentée claire. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_metal_chainlink`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_chainlink_c`<br>1024 × 1024 px<br>alpha : 83 % des pixels sous 50 % | `#060606` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : 1024 px, alpha environ 83 % transparent, type lit_alphatest_nocull_advanced (double face) ; plus défini, couleur sombre. Aucun usage dans les .map officiels lus. |
| alternative (2/5) | `t7_metal_chainlink_worn`<br><sub>ta/t7_metal.gdt</sub><br>instance de `t7_metal_chainlink` | `i_t7_metal_chainlink_yellow_c`<br>1024 × 1024 px<br>alpha : 83 % des pixels sous 50 % | `#585858`<br><sub>teinte ×(0.486275 0.486275 0.486275)</sub> | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu dans le GDT : variante usée (image jaune, teinte grise 0,49). |
| limité (2/5) | `t7_metal_fence_post_cable`<br><sub>ta/t7_metal.gdt</sub> | `i_t7_metal_fence_post_cable_c`<br>1024 × 1024 px<br>alpha : 80 % des pixels sous 50 % | `#343533` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : treillis en losanges de câbles, environ 80 % transparent ; plutôt un câble qu'un grillage. |

#### Mur de clôture

**Avis.** Mur de clôture : brushes avec un enduit (t7_plaster_smooth_light_01) ou des parpaings. Les panneaux préfabriqués de béton (t7_concrete_block_barrier_01) ont des trous de banches très visibles.

| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `t7_plaster_smooth_light_01`<br><sub>ta/t7_plaster.gdt</sub> | `i_t7_plaster_smooth_light_01_c`<br>2048 × 2048 px | `#cccbc6` | 128 × 128<br><sub>stock : 262 faces sur 278</sub><br><sub>projet ×1,25 : 160 × 160</sub> | Vu : gris clair uniforme ; mur enduit. |
| alternative (3/5) | `t7_concrete_wall_blocks_wet`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_wall_blocks_c`<br>1024 × 1024 px | `#848382` | 64 × 64<br><sub>stock : 20 faces sur 38</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : parpaings gris-bleu, 1024 px ; stock : 64 × 64 ou 128 × 128 ; aspect mouillé déduit du nom. <sub>[raccord des bords douteux (mesuré)]</sub> |
| alternative (2/5) | `core_concrete_cinderblocks`<br><sub>art_assets/t6_legacy/ta/core.gdt</sub> | `core_concrete_cinderblock_c`<br>512 × 512 px | `#7d7f7d` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : parpaings gris-bleu avec mousse, 512 px. <sub>[drapeau doNotUse (hérité)]</sub> |
| alternative (3/5) | `t7_brick_worn_red`<br><sub>ta/t7_brick.gdt</sub> | `i_t7_brick_worn_red_c`<br>2048 × 2048 px | `#866456` | 64 × 64<br><sub>estimée, à régler à l'œil</sub> | Vu : brique rouge propre ; muret de brique. |
| limité (2/5) | `t7_concrete_block_barrier_01`<br><sub>ta/t7_concrete.gdt</sub> | `i_t7_concrete_block_barrier_01_c`<br>1024 × 1024 px | `#98948f` | 64 × 64<br><sub>stock : 488 faces sur 534</sub><br><sub>projet ×1,25 : 80 × 80</sub> | Vu : grands panneaux de béton gris clair avec deux trous de banche par panneau, 1024 px ; stock : 64 × 64. Mur « préfa » seulement. |

## 7. Modèles (xmodel)

Les tailles sont mesurées sur les sommets du LOD0 (unité = pouce, soit 2,54 cm). **À `modelscale 1.25`, le modèle garde ces dimensions dans le quartier** (qui est agrandi de 1,25) ; à `modelscale 1`, il paraît 20 % plus petit que les immeubles. Les modèles déjà utilisés par `quartier.py` sont listés au §7.1.

### Voitures

**Avis.** Seule la citadine compacte est vraiment exploitable (4 couleurs). Elle pèse environ 26 700 sommets au LOD0 ; la berline veh_t7_civ_city_car_vista n'en a que 328 (très simple, 3 couleurs) et sert pour le lointain.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `veh_t7_civ_car_compact_grey`<br><sub>me/veh_t7_civ_car_compact.gdt</sub><br>instance de `veh_t7_civ_car_compact` | 3,38 × 1,75 × 1,58 | 26675 | rigid · 0 autre(s) LOD | Citadine, 4 couleurs : grey, blue, black, green (+ variantes « cairo » à plaque différente). Utilisée dans le projet à l'échelle 1 : passer à modelscale 1.25. |
| alternative (4/5) | `veh_t7_civ_car_compact_blue`<br><sub>me/veh_t7_civ_car_compact.gdt</sub><br>instance de `veh_t7_civ_car_compact` | 3,38 × 1,75 × 1,58 | 26675 | rigid · 0 autre(s) LOD | Même modèle en bleu. |
| alternative (4/5) | `veh_t7_civ_car_compact_black`<br><sub>me/veh_t7_civ_car_compact.gdt</sub><br>instance de `veh_t7_civ_car_compact` | 3,38 × 1,75 × 1,58 | 26675 | rigid · 0 autre(s) LOD | Même modèle en noir. |
| alternative (4/5) | `veh_t7_civ_car_compact_green`<br><sub>me/veh_t7_civ_car_compact.gdt</sub><br>instance de `veh_t7_civ_car_compact` | 3,38 × 1,75 × 1,58 | 26675 | rigid · 0 autre(s) LOD | Même modèle en vert. |
| alternative (3/5) | `veh_t7_civ_city_car_vista`<br><sub>me/veh_t7_civ_city_car.gdt</sub> | 3,26 × 1,78 × 1,61 | 328 | rigid · 0 autre(s) LOD | Berline très simplifiée (328 sommets), pour des voitures au loin ; _blu et _grn existent (veh_t7_civ_city_car_vista_blu / _grn). |
| limité (2/5) | `veh_t7_civ_gt`<br><sub>me/veh_t7_civ_gt.gdt</sub> | 5,18 × 2,28 × 1,42 | 19572 | animated · 0 autre(s) LOD | Coupé de sport 5,2 m, type « animated » : peu plausible dans un parking de HLM. |
| limité (2/5) | `veh_t7_civ_truck_semi_trailer`<br><sub>me/veh_t7_civ_truck_semi.gdt</sub> | 14,79 × 3,13 × 4,16 | 3219 | rigid · 0 autre(s) LOD | Remorque de 14,8 m : seulement pour un décor de route lointaine. |

### Lampadaires et poteaux d'éclairage

**Avis.** Aucun lampadaire de rue simple n'existe. p7_light_metal_circle_pole est un grand mât (9,5 m) terminé par un anneau ; son aspect exact est à vérifier dans Radiant. Les lampadaires en brushes du projet restent le plus sûr.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| alternative (2/5) | `p7_light_metal_circle_pole`<br><sub>me/t7_props_lights.gdt</sub> | 2,80 × 3,03 × 9,49 | 2718 | rigid · 0 autre(s) LOD | Mât de 9,5 m à anneau lumineux en tête (déduit de la silhouette). À regarder dans Radiant avant usage. |
| alternative (3/5) | `p7_cai_light_garden`<br><sub>me/t7_props_lights.gdt</sub> | 0,41 × 0,41 × 0,25 | 123 | rigid · 3 autre(s) LOD | Borne de jardin de 0,41 × 0,25 m ; pour des abords d'entrée. |
| alternative (3/5) | `p7_zm_der2_utility_pole_512`<br><sub>me/t7_props_dlc/zm/dlc0/der_riese/p7_zm_der2_utility_pole_512/p7_zm_der2_utility_pole_512.gdt</sub> | 0,43 × 0,85 × 13,23 | 1099 | rigid · 0 autre(s) LOD | Poteau électrique de 13,2 m ; pour une ligne aérienne le long de l'avenue. |
| limité (2/5) | `p7_light_path_metal_small`<br><sub>me/t7_props_lights.gdt</sub> | 0,20 × 0,09 × 0,24 | 210 | rigid · 0 autre(s) LOD | Petite balise de chemin (0,24 m). |

### Bancs

**Avis.** Un seul banc, mais en trois finitions : p7_bench_modern_01 (utilisé), _metal_bare, _metal_green.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `p7_bench_modern_01`<br><sub>me/t7_props_furnishing.gdt</sub> | 2,03 × 0,46 × 0,61 | 392 | rigid · 0 autre(s) LOD | Banc moderne 2,03 m ; utilisé dans le projet (à modelscale 1.25 pour rester proportionné). |
| alternative (4/5) | `p7_bench_modern_01_metal_green`<br><sub>me/t7_props_furnishing.gdt</sub><br>instance de `p7_bench_modern_01` | 2,03 × 0,46 × 0,61 | 392 | rigid · 0 autre(s) LOD | Même banc, structure métal verte (nom à vérifier visuellement). |
| alternative (4/5) | `p7_bench_modern_01_metal_bare`<br><sub>me/t7_props_furnishing.gdt</sub><br>instance de `p7_bench_modern_01_metal_green` | 2,03 × 0,46 × 0,61 | 392 | rigid · 0 autre(s) LOD | Même banc, structure en métal nu. |

### Conteneurs à ordures et bacs

**Avis.** Bacs de tri p7_trashcan_metal_modern_glass / _organic / _paper (trois flux), benne p7_zm_der_dumpster_metal_large, fûts plastique p7_barrel_plastic (plusieurs couleurs). Les conteneurs semi-enterrés du projet sont des brushes.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_trashcan_metal_modern_glass`<br><sub>me/t7_props_street_global.gdt</sub> | 0,84 × 0,84 × 1,23 | 1442 | rigid · 3 autre(s) LOD | Bac de tri 0,84 × 1,23 m ; « glass » = verre (déduit du nom). Bon pour un point de tri. |
| recommandé (3/5) | `p7_trashcan_metal_modern_paper`<br><sub>me/t7_props_street_global.gdt</sub><br>instance de `p7_trashcan_metal_modern_glass` | 0,84 × 0,84 × 1,23 | 1442 | rigid · 3 autre(s) LOD | Même bac, flux « papier » (déduit). |
| recommandé (3/5) | `p7_trashcan_metal_modern_organic`<br><sub>me/t7_props_street_global.gdt</sub><br>instance de `p7_trashcan_metal_modern_glass` | 0,84 × 0,84 × 1,23 | 1442 | rigid · 3 autre(s) LOD | Même bac, flux « organique » (déduit). |
| alternative (3/5) | `p7_zm_der_dumpster_metal_large`<br><sub>me/t7_props_zombie.gdt</sub> | 3,91 × 1,57 × 1,30 | 322 | rigid · 0 autre(s) LOD | Benne métallique 3,9 × 1,6 × 1,3 m ; pour une cour de service. |
| limité (2/5) | `p7_barrel_plastic`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,77 × 0,77 × 1,11 | 1553 | rigid · 1 autre(s) LOD | Fût plastique 0,77 × 1,11 m (blue, green, yellow aussi) ; plutôt industriel. |

### Barrières, clôtures et portails

**Avis.** Pas de panneau de grillage en modèle, seulement les pièces (bases, capuchons, serrures). Le grillage = texture (core_fence_chain_link) sur un brush fin. Pour les portails : p7_barricade_metal_gate_02 (3,35 m).

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| alternative (3/5) | `p7_barricade_metal_gate_02`<br><sub>me/t7_props_industrial_small.gdt</sub> | 3,35 × 0,06 × 1,63 | 1160 | rigid · 0 autre(s) LOD | Portail métallique 3,35 × 1,63 m, 6 cm d'épaisseur ; clôture ou portail de parking (version _damaged aussi). |
| alternative (3/5) | `p7_slab_concrete_interlocked`<br><sub>me/t7_props_architecture_global.gdt</sub> | 1,70 × 0,08 × 0,88 | 399 | rigid · 0 autre(s) LOD | Dalle de béton emboîtable 1,70 × 0,88 m ; mur de clôture préfabriqué. |
| alternative (3/5) | `p7_rail_post_metal_01`<br><sub>me/t7_props_architecture_global.gdt</sub> | 0,25 × 0,10 × 1,24 | 502 | rigid · 1 autre(s) LOD | Poteau de rambarde 1,24 m ; garde-corps de balcon (avec p7_railing_metal_post_end_lt, 1,09 m). |
| limité (2/5) | `p7_cai_sec_wall_metal`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 4,65 × 0,33 × 3,06 | 552 | rigid · 0 autre(s) LOD | Panneau de mur métallique 4,65 × 3,06 m ; plutôt sécuritaire. |
| limité (2/5) | `p7_global_chainlink_fence_metal_base`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,25 × 0,25 × 0,25 | 233 | rigid · 2 autre(s) LOD | Pied de poteau 0,25 m ; pièces seulement. |
| limité (2/5) | `p7_global_chainlink_fence_post_cap`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,11 × 0,11 × 0,09 | 178 | rigid · 0 autre(s) LOD | Capuchon de poteau de 11 cm ; pièces seulement. |

### Arbres (peuplier, sapin, feuillus)

**Avis.** Aucun peuplier ni conifère. Feuillus : p7_foliage_tree_albizia_tall_full (19,4 m, houppier large, la grande vedette), p7_foliage_tree_olive_small (2,4 m), p7_foliage_tree_acacia_bush (2 m). Les palmiers sont hors sujet. Les peupliers et les sapins du projet (brushes) restent donc nécessaires ; l'albizia convient aux feuillus d'agrément.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_foliage_tree_albizia_tall_full`<br><sub>me/t7_props_foliage.gdt</sub> | 14,50 × 13,91 × 19,40 | 7388 | rigid · 3 autre(s) LOD | Feuillu à houppier large et tronc fin, 14,5 × 13,9 × 19,4 m, 7 388 sommets ; utilisé aujourd'hui (échelle 0,9 à 1,2). Silhouette arrondie, pas de peuplier. |
| alternative (3/5) | `p7_foliage_tree_albizia_tall_full_sway`<br><sub>me/t7_props_foliage.gdt</sub><br>instance de `p7_foliage_tree_albizia_tall_full` | 14,50 × 13,91 × 19,40 | 7388 | rigid · 3 autre(s) LOD | Même arbre avec balancement du feuillage (déduit du suffixe _sway et du matériau fxanim_vegetation) ; coût plus élevé. |
| alternative (3/5) | `p7_foliage_tree_olive_small`<br><sub>me/t7_props_technicolor.gdt</sub> | 1,91 × 2,24 × 2,44 | 9963 | rigid · 3 autre(s) LOD | Petit arbre de 2,4 m ; jardin ou pied d'immeuble. |
| limité (2/5) | `p7_foliage_tree_acacia_bush`<br><sub>me/t7_props_foliage.gdt</sub> | 2,09 × 1,63 × 1,15 | 2428 | rigid · 0 autre(s) LOD | Buisson-arbre bas (2 × 1,6 × 1,15 m) ; massif. |
| à éviter (1/5) | `p7_foliage_palm_date_med_half_crown`<br><sub>me/t7_props/p7_foliage_palm_date_optimized_set/p7_foliage_palm_date_optimized.gdt</sub> | 8,85 × 9,10 × 13,63 | 8700 | rigid · 3 autre(s) LOD | Palmier-dattier de 13,6 m : hors sujet en Haute-Savoie. |

### Buissons et haies

**Avis.** Haies taillées prêtes à l'emploi, en deux largeurs et deux hauteurs : p7_foliage_hedge_box_128_48_36 (3,6 m de long), _128_48_60 (haie haute 1,85 m), _48_48_36 (cube), _round_48_48_36 (arrondi), avec des variantes _vibrant (vert plus clair) et _sway.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `p7_foliage_hedge_box_128_48_60`<br><sub>me/t7_props_foliage.gdt</sub> | 3,84 × 1,80 × 1,85 | 7283 | rigid · 0 autre(s) LOD | Haie taillée haute 3,84 × 1,80 × 1,85 m ; haie de séparation ; variantes _vibrant et _sway. |
| recommandé (4/5) | `p7_foliage_hedge_box_128_48_36`<br><sub>me/t7_props_foliage.gdt</sub> | 3,57 × 1,56 × 1,10 | 7285 | rigid · 3 autre(s) LOD | Haie basse 3,57 × 1,56 × 1,10 m, 7 285 sommets ; variantes _vibrant et _sway. |
| alternative (3/5) | `p7_foliage_hedge_box_48_48_36`<br><sub>me/t7_props_foliage.gdt</sub> | 1,35 × 1,52 × 1,10 | 2738 | rigid · 0 autre(s) LOD | Cube de haie 1,35 × 1,52 × 1,10 m. |
| alternative (3/5) | `p7_foliage_hedge_round_48_48_36_vibrant`<br><sub>me/t7_props_foliage.gdt</sub><br>instance de `p7_foliage_hedge_round_48_48_36` | 1,49 × 1,42 × 1,05 | 2164 | rigid · 0 autre(s) LOD | Arbuste arrondi 1,49 × 1,42 × 1,05 m, vert clair ; utilisé aujourd'hui avec modelscale 1.6. |
| alternative (3/5) | `p7_foliage_plant_fern_01`<br><sub>me/t7_beautiful_corner_props.gdt</sub> | 3,00 × 3,01 × 1,27 | 4799 | rigid · 2 autre(s) LOD | Fougère 3 × 3 × 1,3 m ; sous-bois. |
| limité (2/5) | `p7_foliage_wild_ginger_cover_32_tall`<br><sub>me/t7_props_foliage.gdt</sub> | 0,80 × 0,86 × 0,41 | 326 | rigid · 3 autre(s) LOD | Couvre-sol de 0,8 m ; massif. |

### Touffes d'herbe et fleurs

**Avis.** Touffes d'herbe en trois tailles (p7_foliage_grass_tussock_green_1 : 2,1 m ; _2 : 0,95 m ; _3 : 0,35 m), fleurs sauvages p7_foliage_grass_flowers (0,65 × 1,06 m), herbes hautes et mauvaises herbes.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_foliage_grass_tussock_green_3`<br><sub>me/t7_props_technicolor.gdt</sub> | 0,35 × 0,35 × 0,25 | 2040 | rigid · 3 autre(s) LOD | Petite touffe 0,35 × 0,25 m ; pelouses. |
| recommandé (3/5) | `p7_foliage_grass_tussock_green_2`<br><sub>me/t7_props_technicolor.gdt</sub> | 0,95 × 0,91 × 0,35 | 4029 | rigid · 3 autre(s) LOD | Touffe moyenne 0,95 × 0,35 m. |
| alternative (3/5) | `p7_foliage_grass_tussock_green_1`<br><sub>me/t7_props_technicolor.gdt</sub> | 2,13 × 1,85 × 1,18 | 3574 | rigid · 3 autre(s) LOD | Grande touffe 2,1 × 1,2 m : très grande pour une pelouse, à réserver aux talus. |
| alternative (3/5) | `p7_foliage_grass_flowers`<br><sub>me/t7_beautiful_corner_props.gdt</sub> | 0,65 × 1,06 × 0,46 | 1016 | rigid · 0 autre(s) LOD | Fleurs sauvages 0,65 × 1,06 m ; utilisé aujourd'hui. |
| limité (2/5) | `p7_foliage_weed_cluster_lrg`<br><sub>me/t7_props_foliage.gdt</sub> | 0,43 × 0,13 × 0,17 | 776 | rigid · 0 autre(s) LOD | Mauvaises herbes 0,43 m ; pieds de mur. |

### Panneaux routiers et signalétique

**Avis.** Aucun panneau routier n'existe. Restent des signalétiques intérieures/industrielles (garage, zone de chargement, sortie) et le potelet p7_sin_bollard_tall_painted. Pour les panneaux de rue : brushes plats + décalque.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| alternative (3/5) | `p7_sin_bollard_tall_painted`<br><sub>me/t7_props_adia.gdt</sub> | 0,21 × 0,21 × 1,00 | 314 | rigid · 3 autre(s) LOD | Potelet de 1 m, 21 cm de diamètre ; entrées de parking. |
| limité (2/5) | `p7_zm_der_signage_garage`<br><sub>me/t7_props_zombie.gdt</sub> | 0,87 × 0,02 × 0,21 | 118 | rigid · 0 autre(s) LOD | Enseigne « garage » 0,87 × 0,21 m ; texte anglais probable, non vérifié. |
| limité (2/5) | `p7_signage_loading_zone_01`<br><sub>me/t7_props_signage_global.gdt</sub> | 0,71 × 0,01 × 0,46 | 72 | rigid · 0 autre(s) LOD | Panneau de zone de chargement 0,71 × 0,46 m. |
| limité (2/5) | `p7_cai_signage_plastic_exit`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 0,43 × 0,07 × 0,40 | 112 | rigid · 0 autre(s) LOD | Panneau de sortie 0,43 × 0,40 m. |

### Antennes paraboliques et antennes

**Avis.** p7_civ_sat_dish est une vraie parabole sur pied (1 × 1,1 × 1,7 m). Les antennes de toit : p6_antenna_rooftop (3,3 m, ancien jeu) et p7_cell_antenna_roof (4,6 m, antenne-relais).

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_civ_sat_dish`<br><sub>me/t7_props_electronic.gdt</sub> | 0,99 × 1,13 × 1,67 | 10975 | rigid · 0 autre(s) LOD | Parabole 0,99 × 1,13 × 1,67 m, 10 975 sommets : lourde pour la répéter ; réserver à quelques balcons ou toits. |
| alternative (3/5) | `p6_antenna_rooftop`<br><sub>me/legacy_apartments_props.gdt</sub> | 1,07 × 1,23 × 3,31 | 342 | rigid · 3 autre(s) LOD | Antenne de toit de 3,3 m (ancien jeu) ; antenne TV de toit. |
| limité (2/5) | `p7_cell_antenna_roof`<br><sub>me/t7_props_industrial_small.gdt</sub> | 1,36 × 1,36 × 4,62 | 4864 | rigid · 3 autre(s) LOD | Antenne-relais 4,6 m ; trop industriel pour un immeuble. |

### Climatiseurs

**Avis.** Climatiseur mural p7_ac_unit_wall_mount_01 (0,92 × 0,63 × 0,64 m) pour les façades ; groupe p7_ac_unit_large (2 × 1,4 × 1 m) pour un toit-terrasse.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_ac_unit_wall_mount_01`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,92 × 0,63 × 0,64 | 564 | rigid · 0 autre(s) LOD | Unité murale 0,92 × 0,63 × 0,64 m ; balcons et façades (rare en HLM, à doser). |
| alternative (3/5) | `p7_ac_unit_large`<br><sub>me/t7_props_industrial_large.gdt</sub> | 2,01 × 1,36 × 0,97 | 2653 | rigid · 0 autre(s) LOD | Groupe de toiture 2,01 × 1,36 × 0,97 m. |
| alternative (3/5) | `p7_roof_vent_tall_01_metal_white`<br><sub>me/t7_props_industrial_small.gdt</sub><br>instance de `p7_roof_vent_tall_01_metal_bare` | 0,95 × 0,93 × 0,91 | 1650 | rigid · 3 autre(s) LOD | Aérateur de toit blanc 0,9 m ; sorties de ventilation sur le toit. |

### Souches de cheminée

**Avis.** Aucune souche de cheminée. Les souches du projet sont des brushes ; les aérateurs p7_roof_vent_turbine_metal et p7_roof_vent_tall_01_metal_white peuvent compléter le faîtage.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| alternative (3/5) | `p7_roof_vent_turbine_metal`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,98 × 0,84 × 0,81 | 2084 | rigid · 3 autre(s) LOD | Aérateur à turbine 0,98 × 0,84 × 0,81 m. |
| alternative (3/5) | `p7_roof_vent_tall_01_metal_white`<br><sub>me/t7_props_industrial_small.gdt</sub><br>instance de `p7_roof_vent_tall_01_metal_bare` | 0,95 × 0,93 × 0,91 | 1650 | rigid · 3 autre(s) LOD | Ventilation de toit blanche 0,95 m. |
| limité (2/5) | `p7_brick_dirty_01`<br><sub>me/t7_props_architecture_global.gdt</sub> | 0,14 × 0,30 × 0,10 | 28 | rigid · 0 autre(s) LOD | Fragment de mur de briques de 0,14 × 0,30 × 0,10 m (décor de gravats) : pas une souche. |

### Fenêtres et portes en modèle

**Avis.** Aucune fenêtre d'appartement français ; mais p7_louver_window_wooden(_closed) (persienne 1,63 × 2,84 m) et p7_door_metal_rolling_02 (rideau roulant 2,87 × 2,56 m) sont directement utiles ; p7_cai_apt_window_taller_01 (1,32 × 0,40 × 2,36 m) est une baie haute.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_louver_window_wooden_closed`<br><sub>me/t7_props_architecture_global.gdt</sub> | 0,06 × 1,63 × 2,84 | 196 | rigid · 0 autre(s) LOD | Persienne bois fermée 1,63 × 2,84 m, 196 sommets (très légère) ; volets des pavillons. |
| recommandé (3/5) | `p7_door_metal_rolling_02`<br><sub>me/t7_props/p7_door_metal_rolling_02/p7_door_metal_rolling_02.gdt</sub> | 0,11 × 2,87 × 2,56 | 3188 | rigid · 3 autre(s) LOD | Rideau métallique roulant 2,87 × 2,56 m ; portes de garage. Variante _matte. |
| alternative (3/5) | `p7_louver_window_wooden`<br><sub>me/t7_props_architecture_global.gdt</sub> | 0,10 × 1,63 × 2,84 | 196 | rigid · 0 autre(s) LOD | Même persienne ouverte. |
| alternative (2/5) | `p7_cai_apt_window_taller_01`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 1,32 × 0,40 × 2,36 | 88 | rigid · 0 autre(s) LOD | Baie haute 1,32 × 2,36 m, 88 sommets ; style Moyen-Orient (cai), à regarder avant usage. |
| alternative (2/5) | `p7_blinds_01_closed`<br><sub>me/t7_props_redhotcg.gdt</sub> | 1,01 × 0,09 × 2,15 | 401 | rigid · 3 autre(s) LOD | Store vénitien fermé 1,01 × 2,15 m ; intérieur des appartements. |
| limité (2/5) | `p7_door_metal_industrial_02_left_white`<br><sub>me/t7_props_architecture_global.gdt</sub> | 1,38 × 0,50 × 2,45 | 1248 | rigid · 2 autre(s) LOD | Porte industrielle blanche 1,38 × 2,45 m ; locaux techniques. |

### Bacs à fleurs et jardinières

**Avis.** Série p7_cai_planter_* (béton/bois, 1 à 3,7 m) et p7_planters_sphere (0,98 m). Taille plutôt grande : pour une entrée d'immeuble, planter_square (1,07 m).

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_cai_planter_square`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 1,07 × 1,27 × 1,13 | 611 | rigid · 3 autre(s) LOD | Bac carré 1,07 × 1,27 × 1,13 m. |
| alternative (3/5) | `p7_cai_planter_rectangle_sml`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 2,39 × 1,25 × 1,17 | 642 | rigid · 3 autre(s) LOD | Bac rectangulaire 2,39 × 1,25 × 1,17 m. |
| alternative (3/5) | `p7_planters_sphere`<br><sub>me/t7_props_technicolor.gdt</sub> | 0,98 × 0,98 × 0,81 | 865 | rigid · 3 autre(s) LOD | Jardinière sphérique 0,98 m. |
| limité (2/5) | `p7_cai_planter_rectangle`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 3,66 × 1,73 × 1,54 | 822 | rigid · 3 autre(s) LOD | Grand bac 3,66 × 1,73 × 1,54 m. |
| limité (2/5) | `p7_plant_tray_plastic_planter`<br><sub>me/t7_props/p7_foliage_plant_basil_set/p7_foliage_plant_basil_set.gdt</sub> | 0,36 × 0,69 × 0,11 | 5932 | rigid · 3 autre(s) LOD | Bac plastique de 0,36 × 0,69 m ; balcons. |

### Poteaux et potelets

**Avis.** Poteau électrique p7_zm_der2_utility_pole_512 (13,2 m, avec ses bras p7_zm_der_utility_pole_arm), potelets p7_sin_bollard_tall_painted / _indents (1 m) pour les entrées de parking, poteau-obélisque p7_cai_fence_obelisk (1,95 m, style Moyen-Orient) et poteaux de rambarde p7_rail_post_metal_01.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (3/5) | `p7_sin_bollard_tall_painted`<br><sub>me/t7_props_adia.gdt</sub> | 0,21 × 0,21 × 1,00 | 314 | rigid · 3 autre(s) LOD | Potelet peint de 1 m, 21 cm de diamètre ; entrées de parking et devant les halls. |
| alternative (3/5) | `p7_sin_bollard_tall_indents`<br><sub>me/t7_props_adia.gdt</sub> | 0,27 × 0,27 × 0,96 | 386 | rigid · 3 autre(s) LOD | Potelet à rainures de 0,96 m, 27 cm de diamètre. |
| alternative (3/5) | `p7_zm_der2_utility_pole_512`<br><sub>me/t7_props_dlc/zm/dlc0/der_riese/p7_zm_der2_utility_pole_512/p7_zm_der2_utility_pole_512.gdt</sub> | 0,43 × 0,85 × 13,23 | 1099 | rigid · 0 autre(s) LOD | Poteau électrique de 13,2 m ; ligne aérienne le long de l'avenue Borcier. |
| alternative (3/5) | `p7_rail_post_metal_01`<br><sub>me/t7_props_architecture_global.gdt</sub> | 0,25 × 0,10 × 1,24 | 502 | rigid · 1 autre(s) LOD | Poteau de rambarde 1,24 m ; garde-corps. |
| limité (2/5) | `p7_zm_der_utility_pole_arm`<br><sub>me/t7_props_zombie.gdt</sub> | 0,22 × 3,29 × 0,49 | 408 | rigid · 0 autre(s) LOD | Bras de poteau électrique de 3,3 m (0,22 × 0,49 m) ; à fixer au poteau précédent. |
| limité (2/5) | `p7_cai_fence_obelisk`<br><sub>me/t7_props_architecture_middle_east.gdt</sub> | 0,41 × 0,41 × 1,95 | 681 | rigid · 3 autre(s) LOD | Poteau-obélisque de clôture de 1,95 m (base 0,41 m) ; style Moyen-Orient, à regarder avant usage. |

### Boîtes aux lettres

**Avis.** Aucun modèle de boîte aux lettres. Substituts : coffrets électriques p7_electrical_box_set2_* (0,4 × 0,2 × 0,8 m) et compteurs ; à défaut, des brushes.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| limité (2/5) | `p7_electrical_box_set2_box02`<br><sub>me/t7_props_electrical_box_set2.gdt</sub> | 0,43 × 0,29 × 0,78 | 581 | rigid · 0 autre(s) LOD | Coffret mural 0,43 × 0,29 × 0,78 m ; coffret de hall (pas une boîte aux lettres). |
| limité (2/5) | `p7_electrical_box_set2_box05`<br><sub>me/t7_props_electrical_box_set2.gdt</sub> | 0,40 × 0,21 × 0,80 | 138 | rigid · 0 autre(s) LOD | Coffret 0,40 × 0,21 × 0,80 m. |
| limité (2/5) | `p7_electrical_box_set2_meter05`<br><sub>me/t7_props_electrical_box_set2.gdt</sub> | 0,28 × 0,16 × 0,34 | 186 | rigid · 0 autre(s) LOD | Compteur 0,28 × 0,34 m ; locaux techniques. |

### Jeux d'enfants

**Avis.** Aucun jeu d'enfants (ni toboggan, ni balançoire, ni bac à sable). Substituts très partiels : fûts et palettes. À construire en brushes (cadre métal + sol souple t7_rubber_hex_floor_tiles ou t7_mat_floor_rubber_01).

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| limité (1/5) | `p7_pallet_wood_damaged`<br><sub>me/t7_beautiful_corner_props.gdt</sub> | 1,22 × 1,02 × 0,13 | 705 | rigid · 3 autre(s) LOD | Palette de 1,22 × 1,02 m ; décor seulement. |
| limité (1/5) | `p7_crate_wood_01`<br><sub>me/t7_props_redhotcg.gdt</sub> | 1,54 × 0,78 × 0,79 | 256 | rigid · 2 autre(s) LOD | Caisse en bois 1,54 × 0,78 m ; décor. |

### Bordures, regards et avaloirs

**Avis.** Bordure modélisée p7_street_curb_concrete_64a/64b (1,63 m, 21 cm), variantes endommagées (_dmg), peintes (_black_white, _black_yellow) et sableuses (_sandy). Regard p7_street_manhole_cover_cairo_01 (0,88 m), avaloir p7_street_curb_sewer_drain_01.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `p7_street_curb_concrete_64a`<br><sub>me/t7_props_street_global.gdt</sub> | 1,63 × 0,21 × 0,21 | 52 | rigid · 0 autre(s) LOD | Bordure 64 pouces (1,63 m) × 0,21 × 0,21 m, 52 sommets ; plus fidèle qu'un brush texturé. |
| alternative (4/5) | `p7_street_curb_concrete_64b`<br><sub>me/t7_props_street_global.gdt</sub><br>instance de `p7_street_curb_concrete_64a` | 1,63 × 0,21 × 0,21 | 52 | rigid · 0 autre(s) LOD | Variante b, même gabarit. |
| alternative (3/5) | `p7_street_curb_sewer_drain_01`<br><sub>me/t7_props_street_global.gdt</sub> | 1,63 × 1,02 × 0,61 | 890 | rigid · 0 autre(s) LOD | Avaloir de bordure 1,63 × 1,02 × 0,61 m. |
| alternative (3/5) | `p7_street_manhole_cover_cairo_01`<br><sub>me/t7_props_street_global.gdt</sub> | 0,87 × 0,88 × 0,02 | 155 | rigid · 0 autre(s) LOD | Plaque d'égout ronde 0,88 m (style Le Caire : motif à vérifier). |

### Descentes d'eaux pluviales et gouttières

**Avis.** Tuyaux PVC prêts à l'emploi : p7_pipe_pvc_drain_128 (10 cm × 3,25 m), _64, _32, _16, avec coudes, tés et raccords. Parfait pour les descentes de façade (en gris ou blanc) et les évacuations de balcon.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| recommandé (4/5) | `p7_pipe_pvc_drain_128`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,10 × 0,10 × 3,25 | 98 | rigid · 0 autre(s) LOD | Tuyau 3,25 m de long, 10 cm de diamètre (128 pouces) ; descente EP d'un étage et demi. |
| alternative (4/5) | `p7_pipe_pvc_drain_64`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,10 × 0,10 × 1,63 | 66 | rigid · 0 autre(s) LOD | Tuyau 1,63 m (64 pouces). |
| alternative (4/5) | `p7_pipe_pvc_drain_elbow_90`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,16 × 0,11 × 0,16 | 647 | rigid · 0 autre(s) LOD | Coude à 90° de 16 cm. |
| alternative (3/5) | `p7_pipe_metal_water_straight_64_white`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,08 × 0,08 × 1,63 | 168 | rigid · 0 autre(s) LOD | Tuyau métal blanc 1,63 m, 8 cm de diamètre ; alimentation visible, plutôt local technique. |

### Luminaires et petits équipements de façade

**Avis.** Luminaires muraux p7_light_fixture_led_wall_01 (1,63 m de long) et p7_light_wall_runner_led ; caméra p7_camera_security_03 (0,4 m) ; interrupteur p7_lightswitch_metal_m_sensor.

| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |
|---|---|---|---|---|---|
| alternative (2/5) | `p7_light_fixture_led_wall_01`<br><sub>me/t7_props_lights.gdt</sub> | 0,24 × 1,63 × 0,38 | 832 | rigid · 0 autre(s) LOD | Barre lumineuse murale 1,63 m ; style bureau/labo, à regarder avant usage. |
| alternative (2/5) | `p7_camera_security_03`<br><sub>me/t7_props/p7_camera_security_03/p7_camera_security_03.gdt</sub> | 0,37 × 0,14 × 0,43 | 2771 | rigid · 3 autre(s) LOD | Caméra de surveillance 0,37 × 0,43 m ; entrées de parking. |
| alternative (3/5) | `p7_vent_wall_metal_01_white`<br><sub>me/t7_props_industrial_small.gdt</sub> | 0,99 × 0,04 × 0,61 | 140 | rigid · 0 autre(s) LOD | Grille d'aération murale blanche 0,99 × 0,61 m ; façades et caves. |

### 7.1 Modèles déjà utilisés dans le projet

| Modèle | Vérifié | Taille mesurée (m) | Sommets LOD0 |
|---|---|---|---|
| `veh_t7_civ_car_compact_grey` | oui | 3,38 × 1,75 × 1,58 | 26675 |
| `veh_t7_civ_car_compact_blue` | oui | 3,38 × 1,75 × 1,58 | 26675 |
| `veh_t7_civ_car_compact_black` | oui | 3,38 × 1,75 × 1,58 | 26675 |
| `veh_t7_civ_car_compact_green` | oui | 3,38 × 1,75 × 1,58 | 26675 |
| `p7_bench_modern_01` | oui | 2,03 × 0,46 × 0,61 | 392 |
| `p7_foliage_tree_albizia_tall_full` | oui | 14,50 × 13,91 × 19,40 | 7388 |
| `p7_foliage_hedge_round_48_48_36_vibrant` | oui | 1,49 × 1,42 × 1,05 | 2164 |
| `p7_foliage_grass_tussock_green_1` | oui | 2,13 × 1,85 × 1,18 | 3574 |
| `p7_foliage_grass_tussock_green_2` | oui | 0,95 × 0,91 × 0,35 | 4029 |
| `p7_foliage_grass_tussock_green_3` | oui | 0,35 × 0,35 × 0,25 | 2040 |
| `p7_foliage_grass_flowers` | oui | 0,65 × 1,06 × 0,46 | 1016 |

## 8. Ce qui manque ou n'est pas vérifiable

- Rendu dans le moteur : on ne sait pas ici comment un matériau réagit au soleil, aux sondes de reflets ou à l'exposition ; les teintes données sont celles des images, multipliées par colorTint.
- Couleur réelle des bâtiments : les couleurs « beige », « brun foncé », « blanc » viennent de la fiche docs/batiments (texte) ; aucune photo n'a été lue pour cet inventaire.
- Les matériaux de type decal / reveal / blend (marquages, *_blend) n'ont pas été testés sur un brush ; leur comportement dans Radiant et au linker est un à-vérifier.
- Les matériaux à alpha (grillages, métal déployé, feuillages) : le canal alpha est bien présent dans les .tif (mesuré), mais le découpage réel en jeu dépend du type de matériau ; non testé.
- Les dimensions des modèles sont mesurées sur les sommets du LOD0 (méthode validée sur les bordures de 64 pouces, les tuyaux de 64/128 pouces, les haies de 48 × 48 × 36) ; elles incluent les feuillages et les accessoires. Le nombre de sommets du LOD0 donne le coût relatif, pas un budget de jeu.
- Les rotations de projection (tourner une texture de 90°) : le format .map de make_blockout.py a un champ après les décalages ; son effet n'a pas été vérifié ici.

## 9. Remplacements à faire dans `MAT` (`tools/quartier.py`)

Statuts : **garder** (le matériau actuel est bon), **ajuster** (bon matériau mais échelle, variante ou usage à corriger), **remplacer**.

| Clé | Actuel | Statut | Proposé | Alternative | Pourquoi |
|---|---|---|---|---|---|
| `herbe` | `core_grass_med` | **garder** | - | `t7_grass_crab_low_sparse_green` | Pelouse la plus naturelle (uniforme, sans répétition). Mêler des plaques de t7_grass_crab_low_sparse_green pour casser l'uniformité. |
| `herbe_sombre` | `core_grass_dark` | **garder** | - | - | Herbe dense plus sombre, bonne variation ; utile sous les arbres. |
| `terre` | `core_dirt_med` | **ajuster** | `core_dirt_light` | - | Terre réaliste mais en 256 px : passer à core_dirt_light (512 px) pour les grandes surfaces. |
| `asphalte` | `t7_asphalt_dirty_dark_desert` | **remplacer** | `core_asphault_dark` | `t7_asphalt_damaged_dark_wet` | L'asphalte « désert » brun-ocre est peu alpin et ses plages se répètent. Enrobé neuf : core_asphault_dark ; route usée : t7_asphalt_damaged_dark_wet. |
| `trottoir` | `t7_concrete_sidewalk_02` | **ajuster** | `t7_concrete_sidewalk_02` | - | Bon matériau, mais projeter à 64 × 64 (stock) ×1,25 = 80 au lieu de 256 × 256. |
| `bordure` | `t7_street_concrete_curb_01a` | **ajuster** | `t7_street_concrete_curb_01a` | - | Bon matériau mais étiré : l'image fait 1024 × 256, la projeter à 64 × 16 (stock) ×1,25 = 80 × 20, jamais en 256 × 256. |
| `montagne` | `core_grass_dark` | **garder** | - | `core_foliage_treewall` | Silhouette lointaine : l'herbe sombre suffit ; un rideau d'arbres alpha (core_foliage_treewall) pourrait être ajouté plus tard. |
| `ciel` | `sky` | **garder** | - | - | Matériau d'outil (tools.gdt) : ne pas changer. |
| `clip` | `clip_player` | **garder** | - | - | Matériau d'outil (clip.gdt) : ne pas changer. |
| `facade_beige` | `t7_plaster_smooth_light_01` | **remplacer** | `core_plaster_light` | `t7_plaster_rough_worn_01` | t7_plaster_smooth_light_01 est un gris clair, pas un beige. Idéal : instance teintée zm_seyssel_crepi_beige (§10). Sans GDT : core_plaster_light (beige crème discret, 512 px) ou t7_plaster_rough_worn_01 (vrai beige mais écaillé). |
| `facade_blanche` | `t7_concrete_worn_painted_white` | **remplacer** | `t7_plaster_smooth_light_01` | - | Le matériau actuel est un gris-vert terne tacheté. Le blanc cassé uniforme de t7_plaster_smooth_light_01 convient mieux ; stock : 128 × 128. |
| `socle` | `t7_brick_worn_heavy_grout_brown_wet` | **ajuster** | `t7_brick_worn_heavy_grout_brown` | `t7_concrete_bare_dark_01` | La version _wet donne un aspect mouillé (normales « wet »). Même brique en version sèche, ou béton gris foncé pour un soubassement plus neutre. |
| `panneau` | `t7_wood_panel_01_stain_brown_drk` | **garder** | - | `t7_metal_wall_corrugated_hor_brown_drk` | Brun très foncé et propre, matériau de référence des maps officielles (64 × 64). Pour des lames horizontales type persiennes, essayer t7_metal_wall_corrugated_hor_brown_drk. |
| `loggia` | `t7_drywall_painted_brown_01` | **garder** | - | - | Brun olive plat, propre ; un peu uniforme mais cohérent avec les panneaux bruns. |
| `fenetre` | `core_window_opaque` | **garder** | - | `t7_plastic_base_clean` | Fenêtre complète à cadre blanc, pratique mais en 512 px et dépendante de la taille de chaque face. À terme : cadre en brushes (t7_plastic_base_clean) + vitre séparée. |
| `vitre` | `core_glass_plain_trans` | **garder** | - | `t7_glass_clean_01_transparent` | Déjà compilé. Alternative plus moderne : t7_glass_clean_01_transparent (alpha 127, type glass) ; à comparer en jeu. |
| `appui` | `t7_concrete_trim_beveled_03` | **ajuster** | `t7_concrete_trim_beveled_03` | - | Bon matériau ; projeter à 128 × 32 ou 64 × 16 (stock) ×1,25, jamais en 256 × 256 (bande 4:1). |
| `volet` | `t7_drywall_painted_beige_01` | **remplacer** | `t7_metal_wall_corrugated_panel_hor_grey` | `t7_metal_wall_corrugated_hor_brown_drk` | t7_drywall_painted_beige_01 est une peinture de cloison kaki, sans lames. Un bardage à lames horizontales se lit comme un volet roulant ; brun pour les « panneaux type persiennes ». |
| `garage` | `core_door_metal_light` | **ajuster** | `t7_metal_panel_horizontal_painted_grey` | `p7_door_metal_rolling_02` (modèle) | core_door_metal_light est un métal nu clair sans panneaux. Panneaux peints gris, ou le modèle de rideau roulant p7_door_metal_rolling_02 (2,87 × 2,56 m). |
| `porte` | `core_door_wood_dark` | **garder** | - | - | Porte de bois sombre à panneaux moulurés ; correcte pour une porte d'immeuble ou d'appartement. |
| `porte_asc` | `t7_metal_bare_stainless_steel_brushed` | **garder** | - | - | Inox brossé : cohérent pour des portes d'ascenseur. |
| `garde_corps` | `t7_metal_worn_iron_dark` | **ajuster** | `t7_metal_paint_worn_grey_dk` | `t7_metal_panels_painted_2x1_grey` | Fer brut noir (micro-matériau) : pour du « métal peint » de la fiche, un gris anthracite peint est plus juste. Pour une allège pleine : t7_metal_panels_painted_2x1_grey. |
| `dalle_balcon` | `t7_concrete_floor_sealed_01` | **garder** | - | - | Béton marbré sec, correct ; t7_concrete_bare_weathered_01 est un peu plus clair et plus uniforme. |
| `balcon` | `t7_concrete_worn_painted_white` | **remplacer** | `t7_plaster_smooth_light_01` | - | Même gris-vert terne que facade_blanche ; l'enduit clair donne une façade arrière plus propre. |
| `toit` | `core_roof_dark` | **ajuster** | `core_roof_dark` | `core_roof_light` | L'ardoise gris-bleu est belle mais pas brun foncé comme la fiche : instance teintée de core_roof_light (§10) pour le brun, sinon garder. |
| `rive` | `t7_wood_trim_dark_brown` | **garder** | - | - | Bande 16:1 : stock 64 × 4 (×1,25 = 80 × 5). |
| `cheminee` | `t7_plaster_smooth_light_01` | **garder** | - | `t7_brick_worn_red` | Enduit clair, cohérent avec le faîtage. Une brique rouge (t7_brick_worn_red) est possible si la photo le montre. |
| `auvent` | `t7_metal_paint_worn_grey_dk` | **garder** | - | - | Gris anthracite peint uni. |
| `hall_sol` | `t7_stone_travertine` | **ajuster** | `t7_stone_travertine` | `t7_stone_travertine_tiles` | Vu : c'est un marbre blanc-gris veiné, pas du crème (le README annonce des sols et marches crème). Pour du crème : instance teintée zm_seyssel_hall_sol_creme (§10). t7_stone_travertine_tiles est un pavage ocre-brun, trop foncé. |
| `hall_mur` | `t7_drywall_base_cream` | **ajuster** | `t7_drywall_painted_white_01` | `t7_plaster_smooth_light_01` | t7_drywall_base_cream est un gris neutre (le crème n'est que dans le nom). Pour du crème : instance teintée de t7_drywall_painted_white_01 (§10). |
| `plafond` | `t7_drywall_painted_white_01` | **garder** | - | - | Blanc de plafond uniforme. |
| `rampe` | `t7_metal_bare_stainless_steel_brushed` | **garder** | - | - | Inox brossé. |
| `boites` | `t7_metal_painted_clean_white` | **ajuster** | `t7_metal_bare_aluminum_brushed` | `t7_metal_paint_worn_yellow` | Gris clair actuellement. Alu brossé ou jaune selon les boîtes réelles du hall (à confirmer sur photo). |
| `dalle` | `t7_concrete_floor_sealed_01` | **garder** | - | - | Béton marbré sec. |
| `gaine` | `t7_concrete_floor_sealed_01` | **garder** | - | - | Béton de cage d'ascenseur. |
| `cabine` | `t7_metal_bare_stainless_steel_brushed` | **garder** | - | - | Inox brossé. |
| `cabine_sol` | `t7_metal_floor_square_pattern_01` | **ajuster** | `t7_linoleum_floor_tile_square` | - | Vu : plaque de sol sombre de type science-fiction (voyants bleus, boulons), peu crédible dans l'ascenseur d'un immeuble. Le lino gris à dalles carrées est plus sobre (stock : 64 × 64). |
| `appart_mur` | `t7_drywall_painted_white_01` | **garder** | - | - | Blanc cassé de cloison, uniforme. |
| `sol_entree` | `core_tile_light` | **ajuster** | - | `t7_ceramic_tile_large_white` | Vu : grands carreaux gris clair craquelés (2 × 2 par répétition), 512 px de l'ancien jeu. Un carrelage t7_ de 1024 px est plus défini (t7_ceramic_tile_large_white : grands carreaux blancs, stock 64 × 64). |
| `sol_cuisine` | `t7_ceramic_tiles_16x16` | **garder** | - | - | Vu : mosaïque de petits carreaux (grille de 16 × 16 par répétition) sur fond marbré clair, 1024 px ; à projeter assez grand pour que les carreaux restent lisibles. |
| `sol_sdb` | `t7_ceramic_tile_shower_white` | **garder** | - | - | Vu : petits carreaux gris-blanc en damier lâche, 1024 px. |
| `sol_chambre` | `t7_wood_veneer_sugarpine_matte` | **garder** | - | - | Parquet clair ; stock : 64 × 64. |
| `faience` | `t7_ceramic_tile_large_white` | **garder** | - | - | Grand carreau blanc ; stock : 64 × 64. |
| `meuble` | `t7_wood_panel_01_stain_brown_drk` | **garder** | - | - | Bois brun foncé. |
| `annexe` | `t7_concrete_poured_bunker_paint_01_grey_lt` | **garder** | - | - | Béton peint gris-beige uni ; projeter à 128 × 128 (stock) ×1,25 = 160. |
| `gravier` | `t7_stone_pebbles_01` | **garder** | - | - | Gravillon très uniforme, sans répétition ; stock : 64 × 64. |
| `garages` | `t7_concrete_worn_painted_white` | **remplacer** | `t7_plaster_smooth_light_01` | - | Même gris-vert terne que facade_blanche ; un enduit clair raccorde mieux les garages à l'annexe. |
| `voisin` | `t7_plaster_rough_worn_01` | **ajuster** | `t7_plaster_rough_worn_01` | `core_plaster_light` | Bon beige de pavillon, mais 256 × 256 est trop grand : 128 × 128 (stock) ×1,25 = 160, et alterner avec core_plaster_light ou une instance teintée pour varier les maisons. |
| `voisin_toit` | `core_roof_med` | **remplacer** | `core_roof_light` | `core_roof_dark` | core_roof_med ne fait que 64 × 64 px (flou). core_roof_light (512 px) est la vraie tuile des pavillons. |
| `ecole` | `t7_concrete_wall_weathered_01_wet` | **remplacer** | `t7_concrete_floor_sealed_01` | `t7_plaster_smooth_light_01` | Version _wet (aspect mouillé, taches sombres). Même image en version sèche, ou un enduit clair pour une école maternelle. |
| `ecorce` | `t7_wood_beam_worn_oak` | **ajuster** | - | `t7_wood_planks_worn` | t7_wood_beam_worn_oak est une poutre, pas une écorce. Pour des troncs en brushes : t7_wood_planks_worn (brun-gris) ou garder. |
| `feuillage` | `core_grass_dark` | **garder** | - | - | Herbe sombre posée sur des cônes : acceptable de loin. Les arbres modélisés (albizia) sont plus crédibles de près. |
| `feuillage_clair` | `core_grass_med` | **garder** | - | - | Herbe moyenne sur les houppiers de peupliers : acceptable de loin. |
| `conteneur` | `t7_metal_paint_worn_grey_dk` | **ajuster** | `t7_metal_panels_painted_2x4_green` | `t7_metal_paint_worn_grey_dk` | Les conteneurs de tri sont souvent verts : à confirmer sur photo ; sinon garder le gris. |
| `metal` | `t7_metal_bare_graphite_matte` | **garder** | - | - | Graphite mat pour lampadaires et couvercles. |

Sur 55 noms de `MAT`, 55 existent dans les GDT (instances résolues) et 55 ont leur image couleur sur disque.

## 10. Matériaux à créer : instances teintées (propositions, non testées)

Treyarch obtient ses variantes de couleur avec des instances (`t7_plaster_smooth_light_01_grey`, `t7_drywall_painted_beige_01`, `t7_ceramic_tile_shower_red`…). On peut faire de même dans un GDT à nous :

```
"zm_seyssel_hall_sol_creme" [ "t7_stone_travertine" ]
{
	"colorTint" "1 0.94 0.80 1"
}
"zm_seyssel_crepi_beige" [ "t7_plaster_smooth_light_01" ]
{
	"colorTint" "1 0.94 0.80 1"
}
"zm_seyssel_toit_brun" [ "core_roof_light" ]
{
	"colorTint" "0.50 0.40 0.36 1"
}
"zm_seyssel_toit_pavillon" [ "core_roof_light" ]
{
	"colorTint" "0.78 0.56 0.46 1"
}
"zm_seyssel_hall_creme" [ "t7_drywall_painted_white_01" ]
{
	"colorTint" "1 0.94 0.80 1"
}
```

- `zm_seyssel_hall_sol_creme` (parent `t7_stone_travertine`, teinte `1 0.94 0.80 1`) : Sol et marches de hall crème : t7_stone_travertine est un marbre blanc-gris (#e5e5e5) ; 1 / 0,94 / 0,80 donne environ #e5d7b7. Statut : à créer et à juger en jeu.
- `zm_seyssel_crepi_beige` (parent `t7_plaster_smooth_light_01`, teinte `1 0.94 0.80 1`) : Enduit beige clair du bâtiment 1 (fiche : « enduit beige clair »). La teinte multiplie la colorMap : sur une base #cdccc7 environ, 1 / 0,94 / 0,80 donne un beige d'environ #cdc09f. Statut : à créer et à juger en jeu ; teinte à ajuster à l'œil.
- `zm_seyssel_crepi_blanc` (parent `t7_plaster_smooth_light_01`, teinte `1 1 1 1`) : Alias propre du blanc cassé pour les bâtiments 2 et 3 (pas nécessaire : utiliser t7_plaster_smooth_light_01 directement). Statut : inutile en l'état.
- `zm_seyssel_toit_brun` (parent `core_roof_light`, teinte `0.50 0.40 0.36 1`) : Tuiles brun foncé des immeubles, à partir de la tuile mécanique core_roof_light (rose-orangé, 512 px). Statut : à créer et à juger en jeu.
- `zm_seyssel_toit_pavillon` (parent `core_roof_light`, teinte `0.78 0.56 0.46 1`) : Rouge-brun plus sombre pour les pavillons. Statut : à créer et à juger en jeu.
- `zm_seyssel_hall_creme` (parent `t7_drywall_painted_white_01`, teinte `1 0.94 0.80 1`) : Murs de hall crème (le « t7_drywall_base_cream » actuel est gris neutre). Statut : à créer et à juger en jeu.

Réserves : (1) la syntaxe est celle des GDT officiels (vue dans t7_plaster.gdt, lignes 7196 à 7277) mais **aucune instance n'a été compilée ici** ; (2) un fichier GDT à nous devrait vivre dans `source_data\` ou `texture_assets\` des Mod Tools ; `tools/sync.ps1` ne copie aujourd'hui que `map_source\_prefabs\zm_seyssel`, `usermaps\zm_seyssel` et `map_source\zm\zm_seyssel.map`, il faudrait donc l'étendre ; (3) la teinte exacte se juge en jeu, pas sur l'image.

## 11. Aperçus

Dossier `_build/mat_preview/` (ignoré par git) : un PNG de 512 px maximum par matériau analysé (`<nom>.png`, teinte appliquée ; les cartes à alpha sont montrées sur damier), des planches contact `planche_cles_*.png` (chaque texture répétée 2 × 2 pour juger les raccords) et des silhouettes de modèles dans `modeles/` (nuage de sommets vu de face et de côté : indicatif, les modèles très plats y paraissent vides).

Matériaux clés regardés pour cet avis : `t7_plaster_smooth_light_01`, `t7_plaster_rough_worn_01`, `core_plaster_light`, `t7_concrete_worn_painted_white`, `t7_concrete_bare_weathered_01`, `t7_concrete_floor_sealed_01`, `t7_brick_worn_red`, `t7_brick_worn_heavy_grout_brown`, `core_roof_dark`, `core_roof_light`, `core_roof_med`, `t7_metal_wall_corrugated_hor_brown_drk`, `t7_asphalt_dirty_dark_desert`, `core_asphault_dark`, `t7_asphalt_damaged_dark_wet`, `t7_concrete_sidewalk_02`, `t7_concrete_sidewalk_01`, `t7_street_concrete_curb_01a`, `core_grass_med`, `t7_grass_crab_low_sparse_green`, `t7_stone_pebbles_01`, `core_gravel_dark`, `core_dirt_med`, `t7_wood_panel_01_stain_brown_drk`, `t7_wood_trim_dark_brown`, `t7_plastic_base_clean`, `core_window_opaque`, `t7_metal_wall_corrugated_panel_hor_grey`, `core_fence_chain_link`, `t7_metal_chainlink`, `t7_metal_fence_post_cable`, `core_foliage_bushline`, `t7_stone_travertine`, `t7_drywall_base_cream`, `t7_drywall_painted_white_01`, `t7_metal_panels_painted_2x1_grey`, `core_tile_light`, `t7_ceramic_tiles_16x16`, `t7_ceramic_tile_shower_white`, `t7_ceramic_tile_large_white`, `t7_wood_veneer_sugarpine_matte`, `t7_metal_floor_square_pattern_01`, `t7_linoleum_floor_tile_square`, `t7_concrete_poured_bunker_paint_01_grey_lt`.

## 12. Reproduire

```powershell
python tools\inventaire_materiaux.py                 # JSON + Markdown + aperçus
python tools\inventaire_materiaux.py --sans-apercus  # JSON + Markdown seulement
```

Dépendances : Pillow, numpy, OpenCV (outil d'aperçu uniquement ; `build_map.py` reste en bibliothèque standard).
