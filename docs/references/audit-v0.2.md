# Audit de la map v0.2 — état avant refonte

Date : 24 octobre 2026. État analysé : sorties générées par `python tools\build_map.py` (régénération vérifiée identique,
hash identiques) avec `immeuble.py` (516 lignes), `quartier.py` (480), `make_blockout.py` (321), `geo.py` (127).
Les numéros de ligne ci-dessous valent pour ces versions ; si ces fichiers changent, relancer l'audit.

Cet audit répond aux plaintes de l'utilisateur : fenêtres du bâtiment 1, balcons arrière, bâtiments 2 et 3 « mal modélisés »,
maisons voisines « vite faites », textures peu réalistes. Il ne modifie rien dans la map.

## 0. Méthode, sources et limites

**Outil.** `tools/preview_png.py` rend les `.map` en PNG (z-buffer, ombrage par normale, une couleur par famille de matériau).
`tools/vues_standard.py` rend toujours les mêmes 26 cadrages, pour comparer avant/après :

```powershell
python tools\vues_standard.py --dossier _build\renders\avant --prefixe AVANT      # état actuel (déjà fait)
python tools\vues_standard.py --dossier _build\renders\apres --prefixe APRES      # après modification
python tools\preview_png.py -o _build\renders\x.png --cible batiment_1 --face ouest --portion 0 0.36 --zfight
```

Les images citées sont dans `_build/renders/avant/` (dossier ignoré par git : elles ne sont pas versionnées).

**Étiquettes utilisées** pour chaque constat :
- **[vu]** observé sur un rendu ; **[mesuré]** calculé sur les `.map` générés, le code ou les données OSM/IGN ;
- **[déduit]** conclu du code ou des données, sans vérification en jeu ni sur photo ; **[inconnu]** on ne sait pas.

**Limites, à lire avant de se fier aux comparaisons « fidèle à la réalité »** :
- Le dossier `reference/photos/` est vide (seulement `.gitkeep`) et les photos envoyées lors d'une session précédente ne sont pas
  accessibles ici. Je n'ai consulté ni Google Maps ni Street View pour cet audit. **Aucune façade réelle n'a donc été vérifiée.**
  Les seules références réelles utilisées sont le cadastre OSM (source DGI, mise à jour 2011) et la description écrite de
  `docs/batiments/01-hlm-pres-dombet.md`.
- Les rendus ne sont pas ceux du moteur : pas de textures, de lumières ni d'ombres. Les voitures, arbres feuillus et haies (`misc_model`)
  sont dessinés par des boîtes/cônes **approximatifs** (tailles estimées). Rien n'a été ouvert dans Radiant ni compilé.
- Les nombres qui suivent le nom du matériau dans les faces des `.map` (`256 256 0 0 …`, voir § 6, T1) sont interprétés par analogie avec les
  maps officielles : à confirmer dans Radiant (Surface Inspector).

## 1. Chiffres de base

Échelle : 1 m réel = **49,2 unités** (`geo.py:18-19`, ECHELLE 1,25 sur 39,37). Hauteur d'étage `H = 144` u = 2,93 m (`immeuble.py:15`).
La fiche `docs/batiments/01-hlm-pres-dombet.md` parle encore de 39,4 u/m et de 128 u par étage : elle est périmée sur ces deux points.

| | Bâtiment 1 | Bâtiment 2 | Bâtiment 3 |
|---|---|---|---|
| Façade des halls | est (+X), sur le parking | nord (+Y) | nord (+Y) |
| Style (`quartier.py:237-239`) | `beige` | `blanc` | `blanc` |
| Halls × niveaux | 3 × 5 (R+4) | 2 × 5 (R+4) | 3 × 6 (R+5) |
| Généré L × D | 2976 × 800 u = 60,5 × 16,3 m | 1920 × 672 u = 39,0 × 13,7 m | 2976 × 720 u = 60,5 × 14,6 m |
| Emprise cadastre OSM (rectangle minimal) | 60,6 × 12,8 m | 39,5 × 10,6 m | 60,1 × 11,5 m |
| Sol du rez `z0` | 0 | 48 | 104 |
| Pente du toit / cheminées | 24° / 9 | 18° / 6 | 18° / 9 |
| Ascenseur ; appartement jouable (hall, étage, côté) | hall 1 ; (1, 4, +1) | non ; (0, 3, −1) | non ; (0, 5, −1) |
| Brushes / faces | 913 / 5 477 | 559 / 3 353 | 977 / 5 861 |

Quartier (`quartier.map`) : 4 311 brushes + 245 `misc_model`, **3,26 Mo** (voir § 7.6). Les 144 bâtiments OSM hors immeubles/annexe/garages
ne sont pas tous utilisés : 14 voisins sont générés (§ 5).

## 2. Plainte 1 — placement des fenêtres du bâtiment 1

Rendus : `15_bat1_elevation_est`, `16_bat1_elevation_ouest` (élévations orthographiques, à utiliser pour comparer), `10_bat1_est_halls`,
`13_bat1_hall_facade`.

| # | Défaut | Preuve | Cause (lignes) |
|---|---|---|---|
| F1 | **Les positions sont des fractions de la largeur de colonne**, donc la grille change d'une colonne à l'autre. Colonnes de 384 u (halls 0 et 2) : loggia 131 u, panneau 61 u, fenêtres 46-47 u. Colonnes de 320 u (hall 1, à cause de la gaine d'ascenseur) : loggia 109 u, panneau 51 u, fenêtres **39 u**, écart entre les deux fenêtres 12 u au lieu de 15 u. | [mesuré] fenêtres de l'étage 1, u : 253-300, 315-361 | `immeuble.py:210` (loggia 0,06-0,40 w), `:216` (panneau 0,44-0,60 w), `:217-218` (fenêtres 0,66-0,78 et 0,82-0,94 w) |
| F2 | **Le motif est translaté, pas symétrique autour de la cage** : à gauche d'une cage on trouve fenêtres puis escalier (écart 47 u), à droite loggia (écart 47 u). Autour du hall 1 : fenêtres 1203-1293, fenêtre d'escalier 1336-1512, gaine d'ascenseur (mur plein) 1512-1664, loggia 1683-1792. | [vu] `15_bat1_elevation_est` ; [mesuré] | `immeuble.py:157-165` et `:187` : les deux colonnes d'une section reçoivent le même `habillage_colonne` avec `u0` en origine |
| F3 | **Hall 1 : la porte d'entrée et les fenêtres de palier ne sont pas alignées.** Porte (112 u) centrée sur la cage + gaine, u = 1432-1544 (centre 1488) ; fenêtres de palier (176 u) centrées sur l'escalier seul, u = 1336-1512 (centre 1424) : décalage **64 u = 1,3 m**. L'auvent est centré sur la porte. | [mesuré], [vu] `13_bat1_hall_facade` (fenêtres à gauche de l'axe de la porte) | `immeuble.py:297` (porte en `B/2`), `:299` (fenêtre jusqu'à `S(200)` si ascenseur) ; `B` inclut `GAINE` (`:141`) |
| F4 | **Position des halls : sections égales** alors que le cadastre montre des avant-corps de hall à des entraxes inégaux. Centres des escaliers d'après OSM (u) : 512 / 1423 / 2410 ; générés : 496 / 1424 (escalier) / 2480. Écarts : 16 u, 1 u, **70 u (1,4 m)** pour le hall 2. | [mesuré] sommets OSM way 131537388 | `immeuble.py:97` (`ws = L / halls`), `:139-143` (`section`) |
| F5 | **Fenêtres de l'appartement jouable : elles se chevauchent.** Appartement du hall 1, étage 4, côté +1 : colonne de 320 u, donc fenêtre cuisine 160-256 et fenêtre chambre 208-296 de la colonne, soit en u 1824-1920 et 1872-1960 : recouvrement de 48 u (deux vitres et deux appuis superposés, z-fighting). Sur les colonnes de 384 u (bât. 3) il reste 16 u d'écart ; sur celles de 368 u (bât. 2) les deux fenêtres sont jointives (appuis qui se recouvrent de 8 u). | [mesuré] faces `core_glass_plain_trans` v = 6 | `immeuble.py:459-464` (`ouv_av` calculé avec `xc + 24..120` et `W − 112..W − 24`) |
| F6 | **Fenêtres plaquées, sans profondeur ni cadre.** Une fenêtre est un pavé de 2 u collé sur le mur (matériau `core_window_opaque`, opaque), plus un appui de 6 u ; aucune embrasure, aucun montant, aucun vitrage visible. Seules les ouvertures de l'appartement jouable sont percées. | [vu] `13_bat1_hall_facade`, `12_bat1_arriere_balcons` | `immeuble.py:173-185` (`fenetre`), `quartier.py:24` |
| F7 | **Incohérence de format entre faces** : fenêtres avant 46 × 72 u (0,94 × 1,46 m) mais fenêtres arrière 123 × 112 u (porte-fenêtre) et 115 × 76 u. Rien n'indique que ce soit réel. | [mesuré] | `immeuble.py:228-229` (arrière), `:217-218` (avant) |
| F8 | **Façade des halls plate** alors que le cadastre dessine des avant-corps : le hall est en saillie de 1,5 à 1,8 m sur la façade principale (v = 0 contre v ≈ 76-88 u), avec des retraits à 2,5-2,8 m (v ≈ 122-136 u) de part et d'autre du hall 0 et du hall 2. Le générateur fait un plan unique à v = 0 et un auvent de 112 u. **Ces avant-corps sont peut-être une imprécision du cadastre (±1 m)** : à confirmer sur photo. | [mesuré] 28 sommets du polygone OSM, `02_plan_empreintes_osm` ; réalité [inconnu] | `immeuble.py:289-310` (cage), `:301` |
| F9 | **Rez-de-chaussée très simple** : 12 portes de garage (112 × 100 u, `v = −5..0`), pas de fenêtre côté halls ; à l'arrière 6 soupiraux de 48 × 24 u. | [vu] `15_bat1_elevation_est` | `immeuble.py:194-203` |
| F10 | **Pignons** : 2 fenêtres de 56 × 56 u par étage, pas de fenêtre au rez. | [vu] | `immeuble.py:240-245` |

À noter pour la suite : la plupart de ces défauts viennent d'un seul principe — **tout est calculé en fraction de `w`** — au lieu
d'un module de façade en cotes absolues (mètres) répété à pas constant et calé sur les cages.

## 3. Plainte 2 — balcons arrière du bâtiment 1

Rendus : `11_bat1_ouest_arriere`, `12_bat1_arriere_balcons`, `16_bat1_elevation_ouest`, `40_zfight_bat1_arriere`.

| # | Défaut | Preuve | Cause (lignes) |
|---|---|---|---|
| B1 | **Les balcons ne sont pas filants sur tout le bâtiment** : 4 tronçons de 384 / 704 / 704 / 384 u (7,8 / 14,3 / 14,3 / 7,8 m) séparés par 3 trous de 224 / 352 / 224 u (4,6 / 7,2 / 4,6 m) devant les cages. Les 4 étages d'habitation ont le même découpage, sauf l'étage 4 de la colonne de l'appartement jouable (balcon privé, voir B7). | [vu] `16_bat1_elevation_ouest` ; [mesuré] | `immeuble.py:225` : une dalle par **colonne** (`u0..u1`), jamais devant la cage |
| B2 | **Le dos des cages est un mur aveugle** sur toute la hauteur, sans aucune fenêtre : 3 bandes de 4,6 à 7,2 m de large. Si la réalité a des fenêtres d'escalier à l'arrière, elles manquent. | [vu] ; réalité [inconnu] | `immeuble.py:292` (fond de cage plein) |
| B3 | **Le garde-corps est un bloc plein** : 4 u d'épaisseur × 44 u de haut (0,08 × 0,89 m) en `t7_metal_worn_iron_dark`. À l'écran c'est une dalle sombre continue, sans barreaux, sans main courante ni poteaux ; elle masque le bas des portes-fenêtres (la fenêtre 1 part à z+4, le garde-corps monte à z+44). Hauteur de 0,89 m, inférieure au 1 m habituel d'un garde-corps de balcon. | [vu] `12_bat1_arriere_balcons` ; [mesuré] | `immeuble.py:226` ; fenêtres `:228` |
| B4 | **Séparations entre logements dissymétriques et fines** : un voile de 4 u (8 cm) à la **fin** de chaque colonne seulement (`u1 − 4..u1`), jamais au début ; hauteur 112 u. Aux limites de halls (u = 992, 1984), le voile est collé à la dalle de la colonne suivante. | [vu] `12_bat1_arriere_balcons` | `immeuble.py:227` |
| B5 | **Dalle sans finition** : 8 u (16 cm) d'épaisseur, 72 u de profondeur (1,46 m), bord brut, pas de rive, de nez de dalle ni de sous-face traitée. À l'extrémité de chaque tronçon la dalle s'arrête net. | [vu] | `immeuble.py:225` |
| B6 | **Z-fighting aux séparations** : garde-corps (`iron_dark`) et voile (`plaster_smooth_light_01`) ont des faces coplanaires à `v = D+72` sur 4 × 44 u = 176 u² : 39 paires dans le bâtiment 1. Les bandes magenta de `40_zfight_bat1_arriere` les montrent. | [mesuré] | `immeuble.py:226-227` |
| B7 | **Rez-de-chaussée sans balcon** (soupiraux seulement) et appartement jouable (étage 4, hall 1) avec un balcon privé de 96 u de profondeur au lieu de 72 u : il dépasse de 24 u (0,5 m) devant les balcons voisins, et la colonne n'a plus la dalle filante des autres étages. | [vu] `11_bat1_ouest_arriere` (haut, au centre) | `immeuble.py:472-475` |

Réalité : l'utilisateur décrit des « balcons complets » (filants) sur l'arrière. La forme exacte (continuité devant les cages, garde-corps à
barreaux ou plein, nez de dalle) est **[inconnue]** ici ; elle doit être relevée sur Google Maps / Street View, côté avenue Borcier.

## 4. Plainte 3 — bâtiments 2 et 3 différents du 1

Rendus : `20_bat2_nord_halls`, `21_bat2_sud_arriere`, `22_bat3_nord_halls`, `23_bat3_sud_arriere`, `25_bat2_elevation_nord`,
`26_bat3_elevation_nord`.

| # | Défaut | Preuve | Cause (lignes) |
|---|---|---|---|
| D1 | **Deux grammaires de façade distinctes**, choisies par `style` : bat. 1 = loggia saillante de 40 u + panneau brun + 2 fenêtres de 46 u ; bat. 2/3 = 2 fenêtres de 74-77 u avec linteau beige (`volet`) et pas de loggia. Arrière : balcons filants par colonne (bat. 1) contre petits balcons de 136 u décalés d'un étage à l'autre (bat. 2/3). | [vu] `25_bat2_elevation_nord` face à `15_bat1_elevation_est` | `immeuble.py:194-203`, `:208-221`, `:223-238` |
| D2 | **Toit différent** : pente 24° (bat. 1) contre 18° ; cheminées 9 / 6 / 9. | [mesuré] | `immeuble.py:266` |
| D3 | **Garages et soupiraux seulement pour `beige`** ; les bâtiments `blanc` ont deux petites fenêtres au rez. | [vu] | `immeuble.py:194-203` |
| D4 | **Matériau de façade par style** : `t7_plaster_smooth_light_01` contre `t7_concrete_worn_painted_white`. | [mesuré] | `quartier.py:50-53` |
| D5 | **Politique d'élargissement incohérente** (profondeur `D = 1,28 × cadastre`) : bat. 1 garde la façade des halls sur la ligne du cadastre et recule la façade arrière de 172 u (3,5 m) ; bat. 2 et 3 s'élargissent des deux côtés, façade des halls **décalée de 75 u (bât. 2) et 77 u (bât. 3), soit 1,5 m**, vers l'extérieur. | [mesuré] | `quartier.py:244` (D), `:247-249` (bat. 1), `:253-255` (bat. 2/3) |
| D6 | **Le cadastre ne donne pas les mêmes halls** : avant-corps de 218-236 u (4,4-4,8 m) au bât. 1 mais **134-160 u (2,7-3,3 m)** aux bât. 2 et 3 ; les cages générées font 224 u (352 avec la gaine d'ascenseur). Dupliquer le bât. 1 en 2 et 3 revient donc à élargir les halls réels de 40 à 65 %. À arbitrer, la demande étant explicitement de recopier le 1. | [mesuré] | `immeuble.py:19` (`CAGE = 224`) |
| D7 | **Longueurs réelles** : bât. 3 (60,1 m) est quasi jumeau du 1 (60,6 m) → 3 halls ; bât. 2 (39,5 m) = 2 halls. L'arrondi de section à 32 u donne L = 2976 / 1920 / 2976. | [mesuré] | `quartier.py:243` |
| D8 | **Niveaux** : bât. 3 a 6 niveaux, bât. 1 et 2 en ont 5. Aucune source pour « 6 » dans le dépôt (OSM n'a pas de `building:levels`). | [inconnu] | `quartier.py:239` |
| D9 | **Terrain aplani sous chaque immeuble** à `z0 − 2` sur l'emprise + 128 u : bât. 2 à z0 = 48 et bât. 3 à 104 sont sur des plateformes (+1,0 m et +2,1 m par rapport au bât. 1). | [mesuré] | `quartier.py:138-151`, `:257-262` |

**Contraintes gameplay pour la duplication** (elles ne doivent pas régresser) :
- L'ascenseur est unique : `zm_seyssel.gsc:86` fait `GetEnt("ascenseur_cabine")` et `level.ascenseur_nb_etages = GetEntArray("ascenseur_porte").size`.
  Si on copie le bât. 1 en 2 et 3, **garder `ascenseur=None`** pour ces deux-là (`quartier.py:238-239`) ; sinon les noms d'entités se dupliquent.
- Un appartement jouable par immeuble (tuples du § 1) ; l'appartement jouable du bât. 1 est dans la colonne la plus étroite (320 u), d'où F5.
- Positions de gameplay (`docs/gameplay/zone-01-hlm.md`) : spawn (2935, −12), Box (2058, −398), PaP (2292, 924), courant (2447, 941),
  atouts vers x ≈ 2050. `build_map.py:140-141`, `:184-185` et `:228-229` refusent toute entité qui tombe dans une emprise d'immeuble.

## 5. Plainte 4 — maisons voisines

Rendus : `30_voisins_amas_est`, `31_voisin_gros_plan`, `32_zone_ecole`, `02_plan_empreintes_osm`, `01_plan_dessus`.

| # | Défaut | Preuve | Cause (lignes) |
|---|---|---|---|
| V1 | **Une maison = 3 brushes** : un pavé, un toit à deux pans (32°, débord 28 u), une souche de cheminée. 42 brushes pour 14 maisons, contre 913 pour le bât. 1. **Aucune fenêtre, porte, garage, lucarne, gouttière, pignon dessiné.** | [vu] `30_voisins_amas_est`, `31_voisin_gros_plan` ; [mesuré] 42 brushes `plaster_rough`/`roof` | `quartier.py:294-324` |
| V2 | **Hauteur fixe** : 300 u (6,1 m) de mur quel que soit le bâtiment, plus un toit qui monte jusqu'à ~9-10 m. OSM ne fournit ni niveaux, ni forme de toit, ni hauteur (sauf l'armoire fibre : `height=3`, `roof:shape=gabled`), donc ces valeurs sont des **inventions**. | [mesuré] tags OSM | `quartier.py:313-314`, `:318-324` |
| V3 | **Des bâtiments qui ne sont pas des maisons sont rendus comme des maisons à étage** : central téléphonique Orange 10,9 × 10,7 m (OSM 131537511), armoire fibre blanche `height=3` de 7 × 3 m (670060379, toit en bois à deux pans), deux abris sans murs (`wall=no`, OSM 131537506 et 131538654 : 3,7 × 2,9 et 4,0 × 3,2 m). | [mesuré] tags OSM | `quartier.py:296-313` ne lit aucun tag |
| V4 | **Emprise rectangulaire minimale** : les pavillons en L (8 sommets : OSM 131540758 et 131540899) sont remplacés par leur rectangle (83-87 % de la surface). | [mesuré] | `quartier.py:304` (`obb`) |
| V5 | **Un bâtiment est abandonné si une partie de son emprise sort du cadre** (X0 + 128 … X1 − 128). **19 bâtiments OSM sont omis sur 38 autour du cadre** : 9 maisons de la rangée est (x de 5 556 à 6 212, cadre à 5 760), 6 sur le bord ouest dont la **Maison de Pays** (OSM 131537365, 881 m², x jusqu'à −4 970), 2 au sud dont l'**école maternelle** (OSM 131537380, 1 012 m², y de −4 613 à −1 783 : elle dépasse de 133 u) et 2 au nord. Le plan montre un grand vide à la place de l'école. | [mesuré] ; [vu] `02_plan_empreintes_osm` (contours jaunes sans volume dessous), `32_zone_ecole` | `quartier.py:302` (règle « tout ou rien »), `:120` (cadre) |
| V6 | **Branche morte** : le cas « grands volumes à toit plat » (aire > 400 m², école et Maison de Pays) ne sert jamais, puisque ces bâtiments sont déjà omis ; la plus grande maison générée fait 193 m². | [mesuré] | `quartier.py:310-311` |
| V7 | **Orientations en angle quelconque** : les boîtes sont tournées de l'angle du rectangle OSM (p. ex. 52,6° et 141,6°), ce qui crée des plans non alignés sur la grille de Radiant. Valide, mais sommets hors grille. | [mesuré] | `quartier.py:64-70`, `:315` |
| V8 | **Posées à plat sur un terrain en pente** : base au point le plus haut de l'emprise (`zt`), jusqu'à 69 u (1,4 m) de dénivelé sous l'OSM 131540499. | [mesuré] | `quartier.py:308-309`, `:314-315` |
| V9 | **Pas de clôture, de haie, de garage, de terrasse, de voiture** autour des maisons ; 220 touffes d'herbe tirées au hasard (graine fixe 74910) et 5 haies à positions fixes ; rien d'autre. | [vu] | `quartier.py:386-404` |

## 6. Plainte 5 — textures et matériaux des bâtiments

| # | Défaut | Preuve | Cause (lignes) |
|---|---|---|---|
| T1 | **Même paramètres de projection sur 100 % des faces** : `… matériau 256 256 0 0 0 0 lightmap_gray 16384 16384 0 0 0 0` (36 901 faces des prefabs). Dans les maps officielles (16 044 faces `t7_*` échantillonnées dans `mp_sector`) les deux premiers nombres valent 64 (10 240 fois), 32, 128, 16, 8, 24… **jamais 256**. Si ce sont bien les dimensions d'un carreau de texture, les textures sont étirées de 2 à 4 fois, donc floues, et sans décalage (0 0) : les joints tombent tous au même endroit du monde. **À confirmer dans Radiant** avant de corriger. | [mesuré] comptage ; interprétation [déduit] | `make_blockout.py:208` et `:221` |
| T2 | **Un seul matériau par surface, sans variation** : façade beige = `t7_plaster_smooth_light_01` partout, façade blanche = `t7_concrete_worn_painted_white`, loggia = `t7_drywall_painted_brown_01`, panneaux = `t7_wood_panel_01_stain_brown_drk`. Pas de traces, pas de variante « sale/mouillée » alors que `t7_plaster_smooth_dirty_01*`, `t7_plaster_cracked_light_01`, `t7_concrete_painted_*_blend` existent. | [vu] `10_bat1_est_halls` (à-plats) ; existence [mesuré] dans `texture_assets/t7_plaster.gdt`, `t7_concrete.gdt` | `quartier.py:15-47` |
| T3 | **Matériaux T6 génériques** pour 9 des 45 matériaux utilisés (29 `t7_*`, 9 `core_*`, 7 matériaux d'outil) : `core_window_opaque`, `core_glass_plain_trans`, `core_door_*`, `core_roof_dark/med`, `core_grass_med/dark`, `core_dirt_med`, `core_tile_light` (dans `art_assets/t6_legacy`). Leur rendu réel est **[inconnu]** (non ouvert dans Radiant) ; `core_roof_*` couvre tous les toits, `core_grass_*` tout le terrain alors que `t7_grass_lawn_medium_small_green(_vibrant)(_blend)` existe. | [mesuré] | `quartier.py:15-47` |
| T4 | **Matériaux tous présents dans les GDT** (vérifié par recherche textuelle dans `texture_assets/*.gdt` et `art_assets/t6_legacy/texture_assets/core.gdt`, y compris les matériaux dérivés écrits `"nom" [ "parent" ]`). Les GDT sont dans `texture_assets/`, pas dans `source_data/`. | [mesuré] 45/45 trouvés | — |
| T5 | **Décor architectural quasi nul** : pas de cadre de fenêtre, de nez de dalle, de bandeaux, d'enduit de soubassement différencié (seul le socle brique de 72 u), pas de portes d'entrée (ouverture vide de 112 × 120 u sans vantail). L'auvent repose sur des parois vitrées de 4 u d'épaisseur et 104 u de profondeur (`core_glass_plain_trans`, bleues dans les rendus). | [vu] `13_bat1_hall_facade` | `immeuble.py:305-310`, `:247-259` |
| T6 | **Halls** : sol, marches, murs crème (`t7_stone_travertine`, `t7_drywall_base_cream`), main courante pleine de 4 u. Cohérent, mais très uni ; plafond blanc. | [vu] `14_bat1_hall_interieur` | `immeuble.py:313-340` |

## 7. Autres défauts visibles

### 7.1 Z-fighting (faces coplanaires de même sens, de matériaux différents, non enterrées)

| Zone | Paires | Détail |
|---|---|---|
| Bât. 1 | 82 | 39 garde-corps/voile (arrière, 176 u²) ; 24 main courante inox / marches travertin des escaliers (96 u²) ; 10 joue de loggia / rive (32 u²) ; 9 en hall (304 et 832 u²) |
| Bât. 2 | 23 | surtout main courante / marches (16), plus la vitre du pignon de l'appartement (4 608 u²) |
| Bât. 3 | 40 | idem (30 main courante / marches) |
| Quartier | 1 | garage / asphalte à z = −64 (face de dessous, invisible) |
| Entre fichiers | 1 | **plancher de la cabine d'ascenseur** (`script_brushmodel` de la map principale) coplanaire au sol du hall : 10 816 u² à z = 0, scintille quand la cabine est au rez |

Cas grave à part : **vitre de pignon de l'appartement jouable** (z monde 548 au bât. 2, 892 au bât. 3, côté u = 0). Le bloc de verre de 72 × 64 u est posé à 0,01 u de la face intérieure du mur (`immeuble.py:447`, `W − ep − 0.01`) : scintillement certain depuis l'intérieur, et ce n'est pas une vraie ouverture (le mur est plein). Rendu : `41_zfight_bat3_pignon`.

Les faces coplanaires entre brushes du même matériau (203 paires, surtout asphalte) sont indiscernables et ne sont pas comptées.

### 7.2 Routes
- Mesure : **3,5 % des points de contrôle ont le terrain au-dessus de la route** (jusqu'à 8,3 u = 17 cm), sur l'avenue Borcier (96 échantillons) et les rues résidentielles (106). Les routes sont des quadrilatères de 128 u dont seuls les 4 coins suivent le terrain (+5 u), alors que le terrain est trianglé à 256 u. [mesuré] `quartier.py:217-230`
- [vu] `34_route_avenue` : lentilles d'herbe dans l'asphalte tout le long de l'avenue ; `35_chemin_nord_est` : le chemin du nord-est est une large bande criblée de trous d'herbe.
- [vu] Aux virages, les quadrilatères ne se rejoignent pas : encoches triangulaires et recouvrements (`31_voisin_gros_plan`). Même construction.
- [vu] `36_parking_haut` : des bandes de service posées à +5 u sur les cases d'asphalte du parking dessinent des contours superposés dans le parking.
- Largeurs constantes par type (`quartier.py:210`) : 6,1 m (secondaire), 5,7 (tertiaire), 5,3 (résidentielle), 4,1 (service), 1,6 (autres). Réalité **[inconnue]**.

### 7.3 Bord du monde
- [vu] `33_bord_est` : le terrain du quartier est une dalle de relief IGN dont le bord est entre z = 60 et 298 à l'est (83-251 au nord), posée sur une « plaine » plate à z = −64 (`quartier.py:456-459`). Le dessous de la dalle est à `min − 96` (`:181`) : au-dessus de la plaine sur **100 % des bords est et nord**, avec une fente de jusqu'à **253 u (5,1 m) à l'est** et 188 u au nord. On voit le ciel dessous depuis les angles de caméra bas.
- Le bâtiment 3 est à 1 171 u (23,8 m) du bord nord et 1 182 u du bord est : la zone jouable s'arrête très près de lui.

### 7.4 Relief et décor lointain
- Relief au pas de 256 u (5,2 m) : facettes visibles sur les talus ([vu] `30_voisins_amas_est`). Couronne de montagnes d'un seul vert (`core_grass_dark`), sans roche ni forêt. [mesuré] `quartier.py:120-121`, `:438-459`

### 7.5 Végétation et mobilier
- Peupliers = deux cônes à 8 pans, sapins = 4 cônes empilés ; arbres feuillus = `misc_model` `p7_foliage_tree_albizia_tall_full` (aspect réel **[inconnu]**, placeholder dans les rendus). [vu] `00_ensemble_quartier`

### 7.6 Taille des fichiers (règle d'équipe : < 2 Mo)
- **`quartier.map` fait 3,26 Mo** (> 2 Mo). Les ≈ 3 300 prismes de terrain/montagne/plaine pèsent 2,29 Mo (70 %), routes et parkings 0,61 Mo. `batiment_3.map` : 0,95 Mo, `batiment_1.map` : 0,77 Mo.
  Toute amélioration qui ajoute des brushes (maisons détaillées, fenêtres percées) aggravera cela. Pistes : scinder `quartier.map` en plusieurs prefabs (terrain, voirie, voisins, végétation) ou grossir le terrain hors de la zone de jeu ; à décider côté `build_map.py:124-128`.

## 8. Ordre de travail conseillé

1. **Module de façade en cotes absolues** (mètres → unités), répété à pas constant et calé sur les cages, avec grille identique pour les deux colonnes d'une section ; corrige F1-F5 et sert de base à D1-D4. Régler F3 (alignement porte/fenêtre de palier) et F5 (chevauchement) dès cette étape.
2. **Balcons arrière** : relever la réalité sur Street View (avenue Borcier) avant de coder ; ensuite dalle continue, garde-corps ajouré, nez de dalle, fenêtre d'escalier à l'arrière si elle existe (B1-B6) ; supprimer le z-fighting (B6).
3. **Bât. 2 et 3 = bât. 1** : un seul style de façade, paramètres `halls`, `L`, `D`, `z0`, orientation ; décider D5 (politique d'élargissement) et D6 (largeur de cage réelle) ; garder `ascenseur=None` pour 2 et 3.
4. **Textures** : confirmer le sens des deux nombres de projection dans Radiant puis les régler par famille de matériau (T1) ; varier les matériaux (T2).
5. **Voisins** : lire les tags OSM (V3) ; ne plus abandonner les bâtiments qui sortent du cadre (V5) — soit agrandir le cadre jouable, soit couper les bâtiments au cadre ; ajouter fenêtres/portes/pignons (V1).
6. **Routes et bord du monde** (7.2, 7.3) : suivre le terrain sur plusieurs points, joindre les segments, fermer la dalle ; **scinder `quartier.map`** (7.6).
7. Comparer avec `python tools\vues_standard.py --dossier _build\renders\apres --prefixe APRES` et, pour le z-fighting, relancer les vues `40_`, `41_` et `42_`.

## 9. Catalogue des rendus (`_build/renders/avant/`)

| Fichier | Contenu |
|---|---|
| `00_ensemble_quartier`, `01_plan_dessus` | vue d'ensemble oblique et plan de dessus |
| `02_plan_empreintes_osm` | plan de dessus + contours OSM en jaune (montre l'école et les maisons omises, les avant-corps de halls) |
| `10_bat1_est_halls`, `11_bat1_ouest_arriere` | bât. 1 des deux côtés (annexe et arbres masqués) |
| `12_bat1_arriere_balcons`, `13_bat1_hall_facade`, `14_bat1_hall_interieur` | gros plans balcons arrière, hall central (façade et intérieur) |
| `15_`, `16_bat1_elevation_est/ouest`, `25_`, `26_bat2/3_elevation_nord` | élévations orthographiques pour comparer les grilles de fenêtres |
| `20_` à `23_` | bât. 2 et 3, côté halls et arrière |
| `30_`, `31_`, `32_zone_ecole` | maisons voisines (amas, gros plan) et emplacement vide de l'école |
| `33_bord_est` | bord est : la dalle de terrain flotte au-dessus de la plaine |
| `34_`, `35_`, `36_` | défauts de routes (avenue, chemin nord-est, parking du haut) |
| `40_`, `41_`, `42_zfight_*` | z-fighting en magenta (arrière bât. 1, pignon bât. 3, côté halls bât. 1) |
