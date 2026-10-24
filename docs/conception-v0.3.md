# Cahier des charges v0.3 : refonte du quartier des Prés Dombet

Date : 24 octobre 2026. Statut : **spécification à implémenter** (aucun code ni fichier de `game/` n'est modifié par ce document).
Périmètre : `tools/immeuble.py`, `tools/quartier.py`, un nouveau `tools/materiaux.py`, et les modules que ce cahier crée (§C.12). Le gameplay existant (spawn, atouts, Mystery Box, Pack-a-Punch, courant, ascenseur, halls, escaliers, un appartement jouable par immeuble) ne doit pas bouger (§C.2).

Documents lus pour l'écrire : [`facades-et-alentours.md`](references/facades-et-alentours.md), [`vue-aerienne.md`](references/vue-aerienne.md), [`materiaux-disponibles.md`](references/materiaux-disponibles.md) et `reference/materiaux.json`, [`audit-v0.2.md`](references/audit-v0.2.md), `reference/ign/bdtopo_quartier.json`, `reference/ign/lidar_quartier.json`, [`gameplay/zone-01-hlm.md`](gameplay/zone-01-hlm.md), et le code `tools/immeuble.py` (516 lignes), `tools/quartier.py` (480), `tools/build_map.py` (253), `tools/geo.py`, `tools/make_blockout.py`, ainsi que `usermaps/zm_seyssel/scripts/zm/zm_seyssel.gsc` (l'ascenseur).

Étiquettes (reprises des documents de référence) : **[VU]** observé sur image ; **[MESURÉ]** relevé sur BD TOPO, LiDAR ou code ; **[DÉDUIT]** conclu, peut être faux ; **[INCONNU]** non vérifiable, valeur de travail choisie ; **[DÉCISION]** choix de conception, modifiable (voir §E pour les questions à l'utilisateur).

## 0. En bref

1. **Un seul gabarit d'immeuble**, celui du bâtiment 1 recalé sur le cadastre IGN, paramétré par la position de ses halls, sa longueur, sa profondeur, ses niveaux, son orientation et son sol. Les bâtiments 2 et 3 en sont deux instances (§A.11). Fini les deux « styles » `beige` et `blanc`.
2. **Façade en cotes absolues**, plus en fractions de largeur : peau de 16 u percée de vraies niches de fenêtre, grille de fenêtres de 64 × 76 u calée sur chaque appartement, halls en **avant-corps saillants** de 80 u, loggias **en retrait** de 48 u, pilastres, soubassement de 56 u (§A.3 à A.6).
3. **Arrière du bâtiment 1 refait** : balcons **filants et continus** sur toute la longueur (dalle de 64 u de profondeur et 10 u d'épaisseur, garde-corps ajouré de 58 u), y compris devant les cages, sans séparatif, avec une teinte de garde-corps par niveau (blanc, blanc, noir, noir et pleins, vert) comme sur Street View ; terrasse au rez (§A.7).
4. **Toits à croupes de 22°** (un seul brush convexe), fascia, souches en deux rangées, lucarnes sur les bâtiments 2 et 3 (§A.9).
5. **Matériaux** : un contrat de **79 clés** (35 inchangées, 20 remplacées, 24 nouvelles), dont les 59 noms distincts ont été retrouvés comme en-têtes d'entrée dans les GDT des Mod Tools par deux recherches textuelles indépendantes (§B). La projection de texture `256 256` partout est remplacée par une échelle par matériau (§B.4).
6. **Quartier** : cadre agrandi pour contenir l'école et la Maison de Pays, voirie en rubans avec trottoirs, bordures et marquages, maisons **pilotées par les données** BD TOPO et LiDAR, végétation lue dans le LiDAR, mobilier et voitures posés selon l'orthophoto (§C).
7. **Budget** : cible **≈ 15 000 brushes** (v0.2 : 6 760), plafond **19 000**, `.map` découpés en prefabs de ≤ 2 200 brushes (< 1,9 Mo chacun, règle d'équipe de 2 Mo) (§D.2).
8. **Ordre de travail** en 7 phases, avec 22 critères de réception dont 19 automatiques (§D).

**Ce qui a été vérifié pour écrire ce cahier, et ce qui ne l'a pas été.** Vérifié par exécution (en lecture seule, hors dépôt) : les 59 noms de matériaux et les 29 modèles contre les GDT (deux méthodes, §B.1) ; la convexité (`check_brush`) et les cotes du toit à croupes des trois immeubles ; le nombre de brushes de la peau avant d'une colonne (15, avec `mur_perce`) ; l'arithmétique des colonnes, loggias, fenêtres, largeurs de toit et plans d'appartement (script de calcul) ; le décompte des bâtiments BD TOPO du nouveau cadre (38) ; les tailles de fichiers actuelles ; la structure des `.map` officiels (§B.4) ; les aperçus de plus de 60 matériaux. **Non vérifié** : tout rendu moteur, tout passage dans Radiant, toute compilation, l'aspect en jeu des matériaux à alpha ; les cotes [INCONNU] (profondeur des balcons, pignons, halls 1 et 3) restent des hypothèses.

### Décisions prises (toutes modifiables)

| # | Décision | Alternative | Pourquoi |
|---|---|---|---|
| D1 | Profondeur des corps = cadastre : **552 / 456 / 480 u** (11,2 / 9,3 / 9,75 m), facteur `ELARGISSEMENT = 1,0` | `1,28` (v0.2) | demande de fidélité ; la v0.2 était 3 m trop profonde [MESURÉ] |
| D2 | **5 niveaux (R+4) pour les trois** immeubles | B3 à 6 niveaux | BD TOPO : 5 étages ; l'appel d'offres de 30 logements = 3 halls × 5 niveaux × 2 [DÉDUIT] ; le LiDAR suggère 6 pour B3 (§E) |
| D3 | Halls de B2 et B3 = **copie de ceux de B1** (cage de 224 u) | halls réels de 140 à 160 u | demande explicite « dupliquer le 1 » ; l'escalier jouable ne tient pas dans 3 m |
| D4 | B2 est **reconstruit** (état 2023) bien que démoli en 2026 [VU] | l'omettre | la demande porte sur trois immeubles |
| D5 | Toits **à croupes**, pente **22°** | pignons droits, 25° | LiDAR + orthophoto (deux sources indépendantes) contre Street View [DÉDUIT] |
| D6 | Peupliers de l'avenue : **12 m**, tous les **5,1 m** | 18 m et plus, 8 à 12 m | LiDAR + ombre portée contre perspective Street View |
| D7 | Appartements jouables déplacés au **hall du milieu, colonne gauche** : B1 (1, 4, −1), B2 (1, 3, −1), B3 (1, 4, −1) | garder (1, 4, +1), (0, 3, −1), (0, 5, −1) | colonne la plus large, sans loggia à plaquer, pas de pignon à percer ; plus de 5e étage en B3 |
| D8 | Rez-de-chaussée côté halls : **fenêtres**, pas de garages | garages (fiche v0.1) | [VU] Street View : le RDC est un niveau habitable ; les garages sont dans l'annexe |
| D9 | Balcons arrière : **continus, 64 u de profondeur, sans séparatifs** | privatifs ou séparés | [VU] sur 19 à 25 m ; profondeur [INCONNU] |
| D10 | **Aucun GDT à nous en phase 1** ; les teintes viennent des matériaux existants | instances teintées (§B.7) | rien à copier dans les Mod Tools, rien à compiler en plus |
| D11 | Cadre : **x de −5120 à 6656, y de −6656 à 5888** | garder −4608 à 5888 | l'école (y jusqu'à −6381) et la Maison de Pays (x jusqu'à −5024) y tiennent |
| D12 | Garde-corps **ajourés par matériau alpha**, repli opaque prévu | opaque d'emblée | rendu réel non testé (§B.5) |
| D13 | Le **goudron du parking du haut** de la v0.2 est conservé sur `ZONE_JEU` | recopier le talus herbeux réel | le gameplay y est posé (§C.2) |
| D14 | `H = 144` conservé ; « genouillère » de 48 u au-dessus du dernier plafond (B1, B3), 0 (B2) | `H` par immeuble | l'ascenseur déplace la cabine de 144 par étage ; égouts proches du LiDAR (§A.9) |
| D15 | Fenêtre = **niche percée + un seul brush de vitrage** (`core_window_opaque`, 2 × 2 carreaux) | cadre en 4 brushes | coût : ≈ 5 brushes par fenêtre contre 8 |
| D16 | Toit des immeubles : `core_roof_dark` (ardoise gris violacé) | tuile brun foncé | couleur lue sur l'orthophoto (120, 115, 119) ; aucune tuile brune n'existe |
| D17 | Façade avant des trois immeubles : `core_plaster_light` (beige crème) ; arrière : `t7_plaster_smooth_light_01` (blanc cassé) | `blanc` pour B2 et B3 | B2 et B3 sont des copies de B1 (D3) |
| D18 | `.map` **découpés** en prefabs thématiques de ≤ 2 200 brushes | un seul `quartier.map` | `quartier.map` pèse 3,26 Mo > 2 Mo |

## 1. Repères et conventions

- **Monde** `(x, y, z)` : celui de `geo.py`. Origine au centre du bâtiment 1, `+y` vers le nord-nord-ouest, `+x` vers l'est-nord-est, `z = 0` au pied de la façade est du bâtiment 1. `M = 39,37 × 1,25 = 49,2125` unités par mètre réel dans le plan horizontal.
- **Immeuble** `(u, v, z)` : `u` le long de la barre (de 0 à `L`), `v` de la **façade principale** (`v = 0`) vers l'arrière (`v = D`, nu du mur arrière), `z` depuis le sol fini du rez (`z0` en monde). Les avant-corps de halls sont en **`v` négatif** (de −80 à 0), les balcons arrière en `v` de `D` à `D + 64`. En v0.2 `v = 0` était le **front des halls** : tout ce qui est dit de `v` dans `cage()` et `appartement()` change (§A.6, §A.10).
- **Vertical** : un étage = `H = 144 u` pour **2,7 m** réels, soit 53,3 u par mètre en hauteur contre 49,2 u par mètre en plan. Toutes les cotes verticales d'ouvrants sont données **directement en unités** ; ne pas les recalculer en mètres.
- **Grille** : toute cote d'immeuble est un multiple de 8 (Radiant), sauf mention contraire.
- Les cotes de position `u` des tableaux sont les positions **finales** à coder ; les mètres entre parenthèses ne sont là que pour le lecteur.
- Les plans d'un brush sont des triplets `(normale, point, matériau)` ; un quatrième élément optionnel `proj = (W, H, xoff, yoff, rot)` porte la projection de texture (§B.4).


## A. Immeubles

### A.1 Un gabarit, trois instances

`tools/immeuble.py` garde la classe `Immeuble` et les briques `bloc`, `morceaux`, `mur_perce`. Elle perd les deux « styles » (`beige`, `blanc`) et le découpage en sections égales. Nouvelle signature :

```python
Immeuble(nom, origine, eu, ev, L, D, halls, niveaux, z0, appartement,
         ascenseur=None, genouillere=48, lucarnes=False, verrieres=False, z_sol_min=None)
# halls : liste des u des centres de hall, multiples de 8   (ex. [520, 1424, 2416])
# appartement : (indice de hall, étage, côté -1/+1)
```

Les trois instances sont créées par une **fonction unique** `creer_immeubles(site)` dans un nouveau fichier `tools/immeubles_hlm.py` (appelée par `Quartier.immeubles_hlm()`), pour que le travail sur `immeuble.py` et celui sur `quartier.py` ne se marchent pas dessus.

Paramètres des trois instances (tous **[MESURÉ]** sur `bdtopo_quartier.json` sauf mention) :

| | Bâtiment 1 | Bâtiment 2 | Bâtiment 3 |
|---|---|---|---|
| `origine` (monde, point `u = 0`, `v = 0`) | `(217, −1444)` | `(−668, 3464)` | `(1763, 4432)` |
| `eu`, `ev` | `(0, 1)`, `(−1, 0)` | `(1, 0)`, `(0, −1)` | `(1, 0)`, `(0, −1)` |
| `L` (longueur) | 2944 (59,8 m) | 1912 (38,9 m) | 2896 (58,8 m) |
| `D` (profondeur du corps) | 552 (11,2 m) | 456 (9,3 m) | 480 (9,75 m) |
| `halls` (u des centres) | `[520, 1424, 2416]` | `[480, 1432]` | `[496, 1456, 2408]` |
| contrôle : x ou y monde des centres | y = −924, −20, 972 (BD : −926, −18, 970) | x = −188, 764 (BD : −189, 764) | x = 2259, 3219, 4171 (BD : 2261, 3220, 4170) |
| `niveaux` | 5 | 5 | 5 |
| `genouillere` | 48 | 0 | 48 |
| `z0` | 0 | calculé (≈ 48) | calculé (≈ 104) |
| `ascenseur` | hall 1 (le milieu) | `None` | `None` |
| `appartement` | `(1, 4, −1)` | `(1, 3, −1)` | `(1, 4, −1)` |
| `lucarnes` / `verrieres` | non / oui | oui (4) / non | oui (6) / non |
| rectangle d'emprise (`emprises`, `aplanir`) | `(−399, −1444, 329, 1500)` | `(−668, 2944, 1244, 3576)` | `(1763, 3888, 4659, 4544)` |

Notes sur le tableau :

- `origine` de B1 : le **nu de la façade principale** est à `x = 217` (cadastre : 216 à 222), les halls vont à `x = 297`, le mur arrière à `x = −335`. En v0.2 l'origine était au front des halls (`x = 297`) et le mur arrière à `−503` (+3,4 m).
- B2 : façade principale à `y = 3464` (cadastre 3458 à 3476), mur arrière à `3008` (cadastre 3007 à 3018), halls jusqu'à `3544` (cadastre 3529 à 3536). B3 : façade à `y = 4432` (4411 à 4442), mur arrière à `3952` (3939 à 3959), halls jusqu'à `4512` (4505 à 4521). Le léger dévers du B3 (−0,4°) est ignoré : les brushes restent alignés sur les axes.
- Les rectangles d'emprise comprennent les balcons (+64), les halls (+80) et les auvents (+32). Ils servent à `build_map.dans_batiment()`, à `Quartier.libre()` et à l'aplanissement du terrain (marge de 128 conservée).
- `z0` des bâtiments 2 et 3 reste « terrain au point `pied` arrondi à 8 » avec `pied = (centre en u, façade + 80 + 120)` ; contrôle : résultat à ± 16 de 48 et de 104, sinon l'orientation est fausse.
- **Niveaux** : le LiDAR donne des égouts à 13,4 m (B2), 15,1 m (B1) et 16,6 m (B3) au-dessus du sol local, ce qui trancherait pour 5 / 5 / 6 niveaux de 2,7 m ; la BD TOPO donne 5 pour les trois. D2 retient 5 ; B3 sera 1,2 m trop bas à l'égout (§A.9).

### A.2 Constantes

| Constante | Valeur | Équivalent | Source |
|---|---|---|---|
| `H` | 144 | 2,7 m | inchangé : `ascenseur_aller()` fait `MoveZ(ecart * 144)` |
| `DALLE`, `MUR`, `CLOISON` | 8, 16, 8 | | inchangé |
| `CAGE`, `GAINE` | 224, 128 | 4,55 m ; 2,6 m | inchangé (l'escalier jouable ne se réduit pas) ; l'avant-corps mesure 4,35 à 4,75 m [MESURÉ] |
| `SAILLIE_HALL` | 80 | 1,6 m | [MESURÉ] 1,6 à 1,7 m (B2 : 1,45 ; B3 : 1,8, ignorés) |
| `LOGGIA_L`, `LOGGIA_P` | 168, 48 | 3,4 m ; 1,0 m | [MESURÉ] 3,3 à 4,0 m ; retrait 1,1 m |
| `FEN_L` | 64 | 1,3 m | [VU] 1,2 à 1,3 m |
| `FEN_Z0`, `FEN_Z1` | 48, 124 | allège 0,9 m ; haut 1,43 m | [VU] allège 0,9, hauteur 1,4 à 1,5 |
| `PF_Z1` | 120 | porte-fenêtre | |
| `PEAU` | 16 (= `MUR`) | | niche de 8 u devant le vitrage |
| `SOUBASSEMENT` | 56 | 1,05 m | [VU] 1,0 à 1,3 m |
| `PROF_BALCON` | 64 | 1,3 m | [INCONNU] hypothèse 1,2 à 1,5 m |
| `DALLE_BALCON` | 10 | 0,2 m | [VU] 0,20 à 0,25 m |
| `RAIL_H`, `RAIL_EP` | 58, 2 | 1,1 m | [DÉDUIT] 1,0 à 1,1 m (panneau `8..52`, main courante `52..58`) |
| `PENTE` | 22° | | [MESURÉ] LiDAR 21 à 23° |
| `DEBORD_AVANT` | 40 | 0,8 m au-delà de l'avant-corps | [DÉCISION] ; largeur de toit voisine du LiDAR |
| `DEBORD_ARR`, `DEBORD_PIGNON` | 24, 28 | 0,5 m ; 0,55 m | [DÉDUIT] |
| `FASCIA` | 22 | 0,45 m | [VU] 0,4 à 0,5 m |
| `LARG_TOIT` | `D + DEBORD_AVANT + SAILLIE_HALL + DEBORD_ARR` | 696 / 600 / 624 | [MESURÉ] LiDAR 689 / 605 / 610 |

### A.3 Découpage : halls, cages, colonnes

Un **hall** = une cage d'escalier de 224 u centrée sur `halls[k]`, cage du hall à ascenseur incluse : `[c − 112, c + 112]` pour l'escalier, la gaine de 128 s'ajoute côté `+u`, soit un palier de 352 u. Les **frontières de section** sont les milieux entre halls, arrondis à 8 :

```
bord[0] = 0 ;  bord[k] = round8((halls[k-1] + halls[k]) / 2) ;  bord[n] = L
cage[k] = (c - 112, c + 112)         si pas d'ascenseur
cage[k] = (c - 112, c + 240)         avec ascenseur (palier de 352 u ; l'avant-corps reste 224)
colonne (k, -1) = [bord[k], cage[k].debut]        colonne (k, +1) = [cage[k].fin, bord[k+1]]
```

Une **colonne** = un logement par niveau. Résultat :

| Colonne | B1 | B2 | B3 |
|---|---|---|---|
| (0, −1) | [0, 408] | [0, 368] | [0, 384] |
| (0, +1) | [632, 976] | [592, 960] | [608, 976] |
| (1, −1) | [976, 1312] **jouable** | [960, 1320] **jouable** | [976, 1344] **jouable** |
| (1, +1) | [1664, 1920] | [1544, 1912] | [1568, 1936] |
| (2, −1) | [1920, 2304] | | [1936, 2296] |
| (2, +1) | [2528, 2944] | | [2520, 2896] |

La **frontière entre deux colonnes voisines** (ex. `u = 976` en B1) est la position de la cloison séparative : **aucune fenêtre ne doit la traverser** (défaut F2 de l'audit).

**Règle des loggias** (copie du plan réel de B1, où elles encadrent les halls 1 et 3 et pas le hall 2) : une loggia de `LOGGIA_L` de large est ajoutée **de chaque côté de chaque hall d'extrémité** (premier et dernier), contre la cage. Pour B1 : `[240, 408]`, `[632, 800]`, `[2136, 2304]`, `[2528, 2696]`. Pour B2 (deux halls, tous deux d'extrémité) : quatre loggias. Le **bout plein** est le reste entre la loggia et le pignon (B1 : `[0, 240]` et `[2696, 2944]`, 4,9 et 5,0 m, cadastre 5,0 et 4,4 m).

### A.4 Remplissage, peau percée, niches

Principe de la v0.2 conservé (les appartements fermés sont des blocs pleins), avec **une peau percée** devant :

1. **Remplissage** par colonne : `bloc(u0, PEAU, z_fond, u1, D − PEAU, top + genouillere)` avec `top = niveaux × H`. Ses faces `v−` et `v+` (visibles seulement au fond des niches) prennent `fond_vitre`. Dans la colonne jouable, le remplissage est coupé comme en v0.2 (sous le plancher et au-dessus du plafond de l'étage jouable).
2. **Peau avant** : `mur_perce('u', u0, u1, 0, PEAU, z_fond, top + genouillere, ouvertures_avant(col), facade_beige)`. **Une seule peau par colonne sur toute la hauteur**, avec les ouvertures de tous les niveaux dans la même liste : `morceaux()` empile alors des bandes pleines entre les fenêtres, sans joint horizontal ni brush par étage (≈ 15 brushes par colonne au lieu de 35).
3. **Peau arrière** : idem en `v` de `D − PEAU` à `D`, matériau `facade_blanche`, ouvertures de `ouvertures_arriere(col)`.
4. **Niche** : l'ouverture traverse les 16 u de la peau ; le vitrage est un brush de 2 u posé à `v = 8..10` (avant) ou `v = D − 10..D − 8` (arrière) : le reste est une embrasure de 8 u devant, 6 u derrière. Le fond de la niche (face du remplissage) est sombre, donc la fenêtre se lit sombre.
5. **Vitrage** : `fenetre` (`core_window_opaque`) avec une projection **par face** égale à la taille de l'ouvrant : `proj = (largeur, hauteur)`. L'image contient 2 × 2 carreaux à cadre blanc : chaque ouvrant montre une fenêtre à 2 vantaux et imposte. Pour les ouvertures réelles de l'appartement jouable, des halls et des sas : `vitre` (transparent), pas `fenetre`.
6. **Appui** de chaque fenêtre : `bloc(a − 4, −6, z0 − 6, b + 4, 0, z0, appui)` avec `proj = (160, 40)` (avant) ; symétrique à l'arrière (`v = D .. D + 6`).
7. **Volets roulants blancs** : pour 1 fenêtre sur 3 (si `(niveau × 7 + indice × 3 + k) % 3 == 0`, déterministe), panneau `volet` de la largeur de la fenêtre, `v = −3..0`, de `z1 − 40` à `z1` (à demi baissé) et coffre `cadre` de 8 u de haut au-dessus.

### A.5 Façade du côté des halls (est pour B1, nord pour B2 et B3)

**Plan de la façade** (de gauche à droite en `u`, B1, somme 2944) : bout plein 240 · loggia 168 · **hall 224** · loggia 168 · mur à fenêtres 512 · **hall 224** · palier de gaine 128 (mur plein, en retrait de l'avant-corps) · mur à fenêtres 472 · loggia 168 · **hall 224** · loggia 168 · bout plein 248. Écart avec le cadastre ≤ 1 m partout (cadastre : bout 5,0 m, loggia 3,3, hall 4,35, loggia 3,5, mur 10,4, hall 4,4, mur 12,0, loggia 3,5, hall 4,75, loggia 4,0, bout 4,4).

**Grille de fenêtres** : pour chaque colonne, le **mur à fenêtres** est l'intervalle de façade entre la loggia (ou la cage) et la cloison. Sa largeur `w` donne le nombre de fenêtres :

```
n = clamp(round(w / 136), 1, 4)        # 0 si w <= 0 (bout plein, loggia)
centre_i = a0 + (i + 0.5) * w / n      # fenêtres de FEN_L = 64, réparties à pas égal
z : FEN_Z0 .. FEN_Z1 à chaque niveau, rez compris
```

| Colonne | B1 | B2 | B3 |
|---|---|---|---|
| (0, −1) | bout plein + loggia | bout plein + loggia | bout plein + loggia |
| (0, +1) | loggia + mur [800, 976] : 1 fenêtre (u = 888) | loggia + mur [760, 960] : 1 | loggia + mur [776, 976] : 1 |
| (1, −1) jouable | mur [976, 1312] : fenêtres calées sur la cuisine (§A.10) | mur [960, 1152] + loggia [1152, 1320] : idem | mur [976, 1344] : idem |
| (1, +1) | mur [1664, 1920] : 2 (u = 1728, 1856) | loggia + bout plein | mur [1568, 1936] : 3 |
| (2, −1) | mur [1920, 2136] : 2 + loggia | | mur [1936, 2128] : 1 + loggia |
| (2, +1) | loggia + bout plein | | loggia + bout plein |
| Fenêtres par niveau (colonne jouable comprise) | 7 | 2 | 8 |

**Pilastres** (plus clairs que le mur, [VU]) : un à chaque extrémité de chaque mur à fenêtres, `bloc(a − 12, −3, 0, a + 12, 0, top + genouillere, facade_blanche)` ; ≈ 8 brushes par immeuble.

**Soubassement** : `bloc(..., z = −48 .. 56, v = −3 .. 0, socle)` le long de toute la façade principale, interrompu devant les portes (≈ 20 brushes) ; autour de l'avant-corps, `v = −83 .. −80` et flancs. Jamais de brique : `socle` est lisse.

**Loggia** (`[l0, l1]`, 168 de large, retrait 48) :

- **remplissage** de la colonne coupé en trois (gauche, derrière, droite) : la partie derrière a sa face `v−` à `v = LOGGIA_P + PEAU = 64` ; les flancs de la fente (faces `u+` de la partie gauche, `u−` de la droite) prennent `loggia` ;
- par niveau (rez compris) : dalle `bloc(l0, 0, z − 8, l1, 64, z, dalle_balcon)` ; fond = peau `v = 48..64` percée d'une baie vitrée `[l0 + 24, l1 − 24] × [z, z + 120]` (vitrage `fenetre`, projection par ouvrant) ; garde-corps à **lisses horizontales** dans le plan `v = −2..2` : main courante `z + 52..58` et deux lisses à `z + 18` et `z + 36`, matériau `garde_corps`, section 4 u ;
- ≈ 9 brushes par niveau et par loggia, 45 par loggia, 180 par immeuble.

**Descentes d'eau** : à chaque angle entre avant-corps et loggia (B1 : `u = 408, 632, 2304, 2528`), pavé `6 × 6` de `z = 0` à l'égout, matériau `garde_corps`, posé en `v = −2..4` ; 4 brushes.

### A.6 Halls et entrées

Le hall est un **avant-corps** de 224 de large et 80 de saillie, sur toute la hauteur jusqu'à l'égout. Le palier et l'escalier **ne bougent pas** par rapport à leur façade : on décale simplement l'origine de `cage()` en `v` de `−SAILLIE_HALL` (`VH = −80`). Toutes les constantes de cage (`PALIER = 176`, `VOLEE`, `FOND_CAGE = 432`) restent des distances **depuis la façade du hall** ; ajouter `VH` à tous les `v` de `cage()` et de `ascenseur_cage()`, et à `self.gaine` (`v0`, `v1`) ; `ascenseur_entites()` ne change pas autrement (portes, appels et cabine suivent la gaine ; le script GSC n'utilise que des noms et des `z`).

**Cotes de l'avant-corps** (`c` = centre du hall, `c0 = c − 112`, `c1 = c + 112`, `v` de −80 à 0) :

| Élément | Cote |
|---|---|
| Flancs | `bloc(c0, −80, z_fond, c0 + 16, 0, top + genouillere)` et `bloc(c1 − 16, ...)`, `facade_beige` au rez, `panneau` dès `z = H` |
| Face avant, rez | peau `v = −80..−64`, `facade_beige`, percée de l'entrée |
| Face avant, étages | peau `v = −80..−64` de `H` à `top + genouillere`, face extérieure `panneau`, percée d'une **fente vitrée** par niveau |
| Fentes de palier | `u = c ± 80` (160 de large), `z = niv × H + 60 .. + 84` pour `niv = 1 .. niveaux − 1` ; vitrage `vitre` à `v = −74..−72` ; (cadastre : fente de 0,2 m ; agrandie à 0,45 m pour l'éclairage de jeu [DÉCISION]) |
| **Entrée** | ouverture `u = c0 + 16 .. c1 − 16` (192 de large, [VU] ≈ 4,0 m), `z = 0..124` ; 3 vitrages : sas gauche `40`, **passage libre `112`** (pas de vantail : gameplay), sas droit `40`, tous `vitre`, `z = 0..124`, `v = −74..−72` ; montants de 4 u en `fond_vitre` (« châssis sombre ») ; linteau plein `z = 124..136` |
| Auvent | `bloc(c0 − 16, −112, 126, c1 + 16, −80, 134, auvent)`, saillie **32** [VU : faible ; le LiDAR voit plus, à vérifier] ; plus aucune paroi vitrée de 104 u de profondeur comme en v0.2 |
| Soubassement | 56, voir §A.5 |
| Sol et marches | trottoir `trottoir` `u = c0 − 40 .. c1 + 40`, `v = −200 .. −80`, dessus à `z = 0` (pas de marche : le sol du hall est au niveau du trottoir) |

**Hall du milieu de B1 (ascenseur)** : l'avant-corps reste de 224 (escalier seul) ; le palier est de 352. La partie du palier côté gaine (`u = c1 .. c1 + 128`) a sa face avant en **`v = 0..16`** (nu de la façade principale, `facade_beige`, pas de fenêtre) ; fermer l'avant-corps à son flanc droit par un mur `u = c1 − 16 .. c1`, `v = −80..0`. **La porte doit être centrée sur l'escalier, pas sur « escalier + gaine »** (défaut F3 : décalage de 1,3 m en v0.2).

**Cage** (`cage()`), corrections obligatoires :

1. **Sol sous la gaine** : le sol du rez `bloc(c0, 0, z_fond, c1, D, 0, ...)` est découpé (par `morceaux`) autour du rectangle de la gaine ; la cuvette (`−40..−24`) y est visible ; le plancher de cabine (`−8..0`, `script_brushmodel`) n'est plus coplanaire avec le sol du hall (10 816 u² de scintillement en v0.2).
2. **Mains courantes** : `u ∈ [VOLEE_A[1] − 12, VOLEE_A[1] − 8]` et `[VOLEE_B[0] + 8, VOLEE_B[0] + 12]` (chevauchent les marches au lieu d'être coplanaires avec leur face), 4 u de large, sans changer `z` ni `v`.
3. **Portes d'appartement** : `porte = (24, 88)` en `v` d'immeuble (au lieu de `(48, 112)` depuis la façade du hall) pour tomber dans le palier décalé, qui va de `v = −64` à `96` ; soit 104 à 168 mesurés depuis la face avant du hall, donc `VH + 104 .. VH + 168` dans `cage()`.
4. Matériaux : `hall_mur` = `core_plaster_light` (crème), `hall_sol` = `t7_stone_travertine`, `plafond` inchangé.
5. Lumières et sondes de réflexion : mêmes positions relatives (suivent `VH`).
6. Boîtes aux lettres : `boites` = `t7_metal_bare_aluminum_brushed`, mêmes cotes.

### A.7 Façade arrière et balcons filants (bâtiment 1, et copies)

Le défaut de la v0.2 : quatre tronçons séparés par trois trous, garde-corps plein de 0,89 m, voile à un seul bout de colonne, 39 paires de faces qui scintillent. Nouveau principe : **un seul système de balcon par niveau, indépendant des colonnes**.

**Pour chaque niveau `niv` de 1 à `niveaux − 1`** (`z = niv × H`) :

| Élément | Cote | Matériau |
|---|---|---|
| Dalle | `bloc(0, D, z − 10, L, D + 64, z)` : **continue de `u = 0` à `L`**, y compris devant les cages ; `faces = {z+: dalle_balcon, z−: dalle_balcon, v+: balcon, u−: balcon, u+: balcon}` ; `proj` de `v+` = `(160, 10)` | `dalle_balcon`, nez `balcon` |
| Garde-corps, panneau ajouré | `bloc(a, D + 62, z + 8, b, D + 64, z + 52)`, **un brush par segment** (ci-dessous) | `rail_clair` ou `rail_sombre` (alpha) |
| Main courante | `bloc(a, D + 60, z + 52, b, D + 64, z + 58)` | `rail_clair_main` ou `rail_sombre_main` |
| Plinthe | `bloc(a, D + 62, z, b, D + 64, z + 8)` | idem |
| Retours aux pignons | à `u = 0` et `u = L`, sur la dalle : panneau `bloc(0, D, z + 8, 2, D + 64, z + 52)` et `bloc(L − 2, D, z + 8, L, D + 64, z + 52)`, avec main courante et plinthe | idem |
| Séparatifs | **aucun** [VU : « sans cloison séparative visible »] | |

Le **rez-de-chaussée** est une **terrasse** continue : dalle `bloc(0, D, −10, L, D + 64, 0)` dont la jupe descend à `−48` en `socle` (`proj` `(160, 56)`), garde-corps de 50 u (panneau `z + 8 .. 44`, main courante `44 .. 50`) en `rail_vert` (repli `rail_plein` si le matériau ne passe pas en jeu), main courante `rail_sombre_main`.

**Segmentation et teintes** : le garde-corps est coupé en `n_seg = round(L / 787)` segments égaux, aux positions des **descentes d'eau** ([VU] espacement ≈ 16 m, « changement net à une descente d'eau ») : B1 : coupures à `u = 736, 1472, 2208` (4 segments) ; B2 : `956` (2) ; B3 : `724, 1448, 2172` (4). Teinte par niveau :

| Niveau | Panneau | Main courante | Variantes par segment |
|---|---|---|---|
| 4 et 3 | `rail_clair` (blanc ajouré) | `rail_clair_main` | aucune |
| 2 | `rail_sombre` (noir ajouré) | `rail_sombre_main` | aucune |
| 1 | `rail_sombre` | `rail_sombre_main` | segments 1 et 3 (comptés de 0) en `rail_plein` opaque (brise-vue noir) |
| rez | `rail_vert` | `rail_sombre_main` | aucune |

**Descentes d'eau arrière** : pavés `6 × 6` en `v = D + 20 .. D + 26`, de `z = −48` à l'égout, aux coupures de segment ; ils **traversent** les dalles (volumes qui se recoupent, pas de face coplanaire visible) ; matériau `garde_corps` ; 3 brushes pour B1.

**Cages** : le **dos de chaque cage est un mur plein** (`facade_blanche`) devant lequel la dalle et le garde-corps passent sans s'interrompre. [INCONNU : fenêtres de cage à l'arrière ; non vues sur Street View.]

**Fenêtres arrière** (`ouvertures_arriere(col)`) : pour chaque colonne de largeur `w`, `n = max(1, w // 192)` travées de largeur `t = w / n` ; dans chaque travée, une **porte-fenêtre** de 104 (`z = 0..120`, vers la dalle) et une **fenêtre** de 56 (`z = 48..124`), séparées et encadrées par trois espaces égaux `g = (t − 160) / 3` ; l'ordre s'inverse d'une travée à l'autre (symétrie en miroir). B1 : 9 travées, donc 18 ouvertures par niveau. Volets : comme à l'avant.

**Brushes** : dalle 1 + 2 retours + 4 segments × 3 + 2 pleins ≈ 20 par niveau, ≈ 100 pour les cinq niveaux, plus ≈ 90 pour les ouvertures arrière.

**Contrôles de réception de cet arrière** (§D.3, R7) : pour chaque niveau, l'union des intervalles `u` des brushes de dalle recouvre `[0, L]` sans trou ; aucune paire de faces coplanaires entre garde-corps et séparatif (il n'y en a plus) ; la vue `12_bat1_arriere_balcons` montre quatre lignes de dalle ininterrompues.

### A.8 Pignons

Peau de 16 u en `u = 0..16` et `u = L − 16..L`, `facade_blanche`, percée de **deux fenêtres par niveau, rez compris** : `v` centrés à `D / 3` et `2 D / 3`, 56 de large, `z = 48..124`, niche de 8, vitrage `fenetre`. [INCONNU : les pignons n'ont pas été vus.] Pas de balcon de pignon. Le retour de dalle et de garde-corps est décrit en §A.7. Aucune fenêtre de pignon ne tombe dans la colonne jouable (D7).

### A.9 Toit

**Géométrie** (un seul brush convexe, `toit_croupe`) :

```python
def toit_croupe(u0, v0, u1, v1, z, pente, m_toit, m_rive, fascia=22):
    run = (v1 - v0) / 2;  h = run * math.tan(math.radians(pente))
    return [((0, 0, -1), (0, 0, z - fascia), m_rive),                  # sous-face
            ((-1, 0, 0), (u0, 0, 0), m_rive), ((1, 0, 0), (u1, 0, 0), m_rive),     # fascia
            ((0, -1, 0), (0, v0, 0), m_rive), ((0, 1, 0), (0, v1, 0), m_rive),
            ((0, -h, run), (0, v0, z), m_toit), ((0, h, run), (0, v1, z), m_toit),  # grands pans
            ((-h, 0, run), (u0, 0, z), m_toit), ((h, 0, run), (u1, 0, z), m_toit)]  # croupes
```

avec `u0 = −28`, `u1 = L + 28`, `v0 = −(SAILLIE_HALL + DEBORD_AVANT) = −120`, `v1 = D + DEBORD_ARR`, `z = niveaux × H + genouillere`. Longueur du faîtage = `(u1 − u0) − (v1 − v0)` (2304 pour B1). Les **croupes sont à la même pente** que les grands pans (hanches à 45° en plan), ce qui redonne « le faîtage descend de 3 m sur les 5 derniers mètres » [MESURÉ].

| | B1 | B2 | B3 | LiDAR |
|---|---|---|---|---|
| Largeur de toit | 696 | 600 | 624 | 689 / 605 / 610 |
| Égout relatif à `z0` | 768 | 720 | 768 | 785 / 657 / 827 |
| Faîtage relatif à `z0` | 909 | 841 | 894 | 922 / 775 / 945 |
| Faîtage absolu (monde) | 909 | 889 | 998 | 922 / 823 / 1049 |

Écarts connus : B2 environ **1,3 m trop haut**, B3 environ **1,2 m trop bas** à l'égout (le sol du hall n'est pas le sol moyen du LiDAR). Acceptés ; voir §E (niveaux de B3).

**Matériaux** : pans `toit` (`core_roof_dark`, projection 128), fascia et sous-face `rive` (brun très foncé, `proj` `(80, 5)`).

**Souches** (≈ 16, groupées par 2 à 4 [VU]) : quatre groupes en `u = round8(L × (0.14, 0.38, 0.62, 0.86))` ; chaque groupe = 4 souches `40 × 40` aux `(u ± 40, v_faîtage ± 60)`, du bas `z_pan − 30` à `z_faîtage + 60` (`z_pan = z_faîtage − 60 × tan 22°`), matériau `cheminee` ; chapeau `bloc(... 48 × 48 × 6)` en `appui`. 32 brushes.

**Verrières de cage (B1 seulement, [VU] « grands panneaux plats sombres »)** : trois plaques de 220 × 80 (suivant la pente), 6 d'épaisseur, posées sur le pan avant au-dessus de chaque cage (`u = c ± 110`), bord bas à `v = 40` ; fonction `plaque_pente(u0, u1, v0, v1, z_en_v0, pente, ep, mat)` (prisme à deux faces parallèles à la pente) ; matériau `fond_vitre`. 3 brushes.

**Lucarnes (B2 : 4, B3 : 6, [ORTHO])** : sur le pan côté halls, à `u = c ± 212` de chaque hall (B2 : `268, 692, 1220, 1644` ; B3 : `284, 708, 1244, 1668, 2196, 2620`). Chacune = 2 brushes : un prisme à pignon (largeur 72, profondeur 56 suivant la pente, hauteur 70 au-dessus du pan, matériaux `facade_blanche` et `toit`) et un vitrage `fenetre` de 48 × 48 sur sa face avant.

### A.10 Appartement jouable

Position : `appartement = (1, étage, −1)` (D7), colonne de 336 (B1), 360 (B2), 368 (B3). **Le code d'`appartement()` est conservé** (miroir `X`, `cloison_x`, `cloison_v`, sols, faïence, lumières, `self.sonde`, `self.centre_appart`), avec ces changements :

| Point | v0.2 | v0.3 |
|---|---|---|
| Profondeur | `D` = 800 / 672 / 720 | `D` = 552 / 456 / 480 |
| Cloisons `v` | fractions de `D` (0,30 / 0,47 / 0,64) | cotes ci-dessous |
| Porte d'entrée | `v = 48..112` | `v = 24..88` (§A.6) |
| Fenêtres avant | calculées par fractions, chevauchement de 48 u | **deux ouvertures de 64 u** à `x = 168..232` et `248..312` (en distance depuis le mur de la cage), calées sur la cuisine |
| Fenêtres arrière | porte-fenêtre + fenêtre sur balcon privé de 96 u | baie de séjour `x = 40 .. xs − 40` et fenêtre de chambre 2 `x = xs + 40 .. W − 48` ouvertes sur le **balcon continu** de §A.7 (plus de balcon privé ni de garde-corps propre) |
| Vitre de pignon | bloc à 0,01 u du mur (z-fighting) | **supprimée** (la colonne jouable n'est jamais au bout) |
| Murs de façade | blocs puis `mur_perce` | **les mêmes `ouvertures_avant` / `ouvertures_arriere` que les colonnes fermées**, avec vitrage `vitre` |

Les deux ouvertures avant en `x = 168..232` et `248..312` tombent dans la cuisine (`x ≥ 144`) et **en dehors** de la loggia éventuelle (les 168 premiers u depuis la cage) : la même cote convient aux trois immeubles. Dans la colonne jouable, la loggia éventuelle (B2) est traitée comme **mur plein**, sans retrait.

**Plan en `v`** (`v_cuis`, `v_sdb`, `v_sej` : débuts de cloison ; murs et cloisons de 8 ; `MUR = 16` aux deux faces) :

| `D` | cuisine | cloison | sdb | cloison | chambre 1 | cloison | séjour + chambre 2 | `v_cuis`, `v_sdb`, `v_sej` |
|---|---|---|---|---|---|---|---|---|
| 552 | 16 → 152 | 152 | 160 → 240 | 240 | 248 → 360 | 360 | 368 → 536 | 152, 240, 360 |
| 480 | 16 → 136 | 136 | 144 → 216 | 216 | 224 → 328 | 328 | 336 → 464 | 136, 216, 328 |
| 456 | 16 → 128 | 128 | 136 → 208 | 208 | 216 → 312 | 312 | 320 → 440 | 128, 208, 312 |

(somme : `16 + cuisine + 8 + sdb + 8 + chambre + 8 + séjour + 16 = D`). Plan en `x` inchangé : `xc = 136`, `xcl = 112`, `xs = round8(0,58 × W)`. Les pièces sont étroites en B2 (séjour de 2,4 m) : c'est le prix du respect du cadastre (D1). Le plafond, les lumières (6) et la sonde sont repris tels quels.

### A.11 Règles de duplication : bâtiments 2 et 3

1. **Mêmes fonctions, mêmes constantes** que B1 ; seules changent les entrées du tableau de §A.1. Aucun test `style == "beige"` ne subsiste dans `immeuble.py`.
2. **Halls** : même cage de 224 (D3), même avant-corps de 80, mêmes fentes ; **pas d'ascenseur** (`ascenseur=None` : l'unicité des noms d'entités lus par `zm_seyssel.gsc:86` et `:96` doit être préservée).
3. **Nombre de halls et de niveaux conservés d'après le cadastre** : B2 = 2 halls (BD TOPO : 2 avant-corps), B3 = 3 ; 5 niveaux pour les deux (D2).
4. **Loggias** de chaque côté des halls d'extrémité (§A.3) : B2 en a quatre.
5. **Appartement jouable** : un par immeuble, au hall 1 (colonne gauche), étage 3 en B2 et 4 en B3.
6. **Variante B3 (option, phase 6)** : `variante = "b3"` ajoute sur la façade nord le soubassement `socle` de 1,2 m (au lieu de 56 u) et des portes de garage sectionnelles `garage` (118 × 100) entre les halls au rez, à la place des fenêtres du rez ; fenêtres de cage étroites au lieu des fentes. Désactivée par défaut (D3).
7. **Verrières** : B1 seulement. **Lucarnes** : B2 et B3 seulement.
8. **Rang d'implémentation** : tout bâtiment est construit à l'origine locale puis posé ; une seule rotation de 90° (`eu`, `ev`). Toute dérive d'orientation (ex. B3 à −0,4°) est ignorée.

### A.12 Défauts de l'audit corrigés par ce cahier

| Audit | Correction | Section |
|---|---|---|
| F1, F2 (grille en fractions, motif translaté) | grille en cotes absolues par colonne, frontières de cloison respectées | A.5 |
| F3 (porte décalée de 1,3 m) | porte centrée sur l'escalier | A.6 |
| F4 (halls à espacement égal, 70 u d'écart) | halls aux `u` du cadastre | A.1, A.3 |
| F5 (fenêtres de l'appartement qui se chevauchent) | deux ouvertures de 64 calées sur la cuisine | A.10 |
| F6, T5 (fenêtres plaquées, pas de cadre, pas de porte) | niches de 8 u, vitrage `fenetre`, appuis, sas vitrés et linteau | A.4, A.6 |
| F7 (formats incohérents) | `FEN_L = 64` partout, porte-fenêtre arrière de 104 | A.2, A.7 |
| F8 (façade plate) | avant-corps de 80, loggias en retrait de 48 | A.5, A.6 |
| F9 (garages au rez) | fenêtres au rez, [VU] | A.5 |
| F10 (pignons) | deux fenêtres par niveau, rez compris | A.8 |
| B1, B2 (balcons en tronçons, dos des cages) | dalle continue, dos de cage plein sous le balcon | A.7 |
| B3, B5 (garde-corps plein, dalle brute) | panneau ajouré, main courante, plinthe (58 u au total), nez de dalle clair | A.7 |
| B4, B6 (séparatif, z-fighting) | séparatifs supprimés | A.7 |
| B7 (balcon privé de l'appartement) | balcon continu | A.10 |
| D1 à D4 (deux grammaires) | un seul gabarit | A.1, A.11 |
| D5 (élargissement incohérent) | origine au nu de la façade, `ELARGISSEMENT = 1,0` | A.1 |
| D6 à D8 (halls, longueurs, niveaux) | décisions D2, D3 | A.1, A.11 |
| D9 (terrain aplani) | `aplanir` sur les nouveaux rectangles | A.1 |
| Z-fighting : mains courantes (24), joues de loggia (10), vitre de pignon, plancher de cabine | §A.6, A.10 | |
| Toits à 24° / 18°, pignons droits | croupes, 22° | A.9 |

### A.13 Interfaces, étiquettes et budget

- `Immeuble.ajoute(planes, tag=None)` mémorise l'étiquette (chaîne : `"balcon_dalle_n2"`, `"fenetre_avant_n3_c1"`, `"toit"`…) dans une liste parallèle `self.tags` (non écrite dans le `.map`). Sert aux tests de réception (§D.3).
- `bloc(..., proj=None)` : `proj` est un dict `{"v-": (W, H), "*": (W, H)}` ; les plans portent un 4e élément. `Immeuble.ajoute()`, `quartier.tourne()` et `make_blockout.brush_lines_mat()` doivent le propager (§B.8).
- Nouvelles briques : `toit_croupe`, `plaque_pente`, `prisme_pignon` (lucarne). Elles vivent dans `tools/geom.py`, **créé en phase P0** (les maisons et l'école utilisent les mêmes toits, §C.5) ; `immeuble.py` les importe. Toutes passent `check_brush` ; `toit_croupe` a été vérifié : convexe pour les trois immeubles, faîtage 909 / 841 / 894 et longueur de faîtage 2304 / 1368 / 2328.
- `mats_immeuble(style)` disparaît : `Immeuble.mat` = `materiaux.MAT` avec `mat["facade"] = MAT["facade_beige"]` (avant, halls, cages) et `mat["facade_arriere"] = MAT["facade_blanche"]` (arrière, pignons).
- `Immeuble.emprise` (rectangle monde) remplace le calcul dans `quartier.immeubles_hlm()`.
- **Budget indicatif** (à mesurer, tags à l'appui) :

| | cible | plafond | détail principal |
|---|---|---|---|
| Bâtiment 1 | 1 400 | 1 800 | remplissages 8, peau avant 100, peau arrière 150, vitrages et appuis 330, loggias 180, balcons 100, halls 90, cages 270, toit 75, appartement 110 |
| Bâtiment 2 | 900 | 1 200 | 2 halls, 4 loggias |
| Bâtiment 3 | 1 400 | 1 800 | + 12 pour les lucarnes |


## B. Matériaux

### B.1 Ce qui a été vérifié, et comment

Toutes les clés ci-dessous pointent vers des noms exacts. Pour ce cahier, **je les ai revérifiés moi-même, sans reprendre le résultat de `reference/materiaux.json`** :

1. un script lit les 339 `.gdt` de `texture_assets\`, `art_assets\t6_legacy\texture_assets\`, `model_export\` et `source_data\` et indexe chaque en-tête d'entrée de la forme `"nom" ( "material.gdf" )` ou `"nom" [ "parent" ]` (14 916 entrées) ; les **79 clés** correspondent à **59 noms distincts**, tous présents ;
2. une seconde recherche, indépendante (`grep -E` sur un motif qui alterne les 59 noms avec l'en-tête exact), retrouve les 59 noms ;
3. les **29 modèles** de §B.6 sont retrouvés de la même façon (`xmodel.gdf` ou instance d'un modèle) ;
4. j'ai **regardé** les aperçus de plus de 60 matériaux (`_build/mat_preview/`) avant de trancher : `core_asphault_med` est un enrobé gris moyen fissuré (le bon), `t7_asphalt_dirty_dark_desert` est brun-ocre ; `core_plaster_light` est un beige crème lisse ; `t7_metal_panels_painted_2x4` est un panneau blanc à joints (porte sectionnelle) alors que `t7_metal_panel_horizontal_painted_grey` est rouillé ; `t7_metal_wall_corrugated_hor` est un bardage blanc à lames horizontales ; `core_roof_dark` est une ardoise gris-bleu violacé ; `core_window_opaque` contient 2 × 2 fenêtres à cadre blanc.

Les GDT sont dans `texture_assets\`, pas dans `source_data\` (voir `materiaux-disponibles.md` §4). Le nom `core_asphault_*` s'écrit bien avec la faute « asphault » dans les GDT.

**Ce qui n'a pas été vérifié** (à tester en jeu, §B.5) : rendu moteur, matériaux à alpha, décalques, verres. Les teintes sont celles des images multipliées par `colorTint`, pas le rendu éclairé.

### B.2 Le contrat : clé → nom exact

`MAT` est déplacé de `tools/quartier.py` vers `tools/materiaux.py` ; `quartier.py` fait `from materiaux import MAT`. **Les 55 clés existantes restent toutes valides** (35 inchangées, 20 remplacées explicitement, §B.3) ; 24 clés sont nouvelles. Colonne « projection » : taille en unités d'une répétition (§B.4).

| Clé | Matériau (nom exact, vérifié) | Statut | Projection (u) | Usage |
|---|---|---|---|---|
| `herbe` | `core_grass_med` | inchangée | 128 x 128 | pelouses, terrain de base |
| `herbe_sombre` | `core_grass_dark` | inchangée | 128 x 128 | plaques sombres du terrain, sous-bois |
| `herbe_clairsemee` | `t7_grass_crab_low_sparse_green` | **nouvelle** | 128 x 128 | plaques d'herbe usée sous les arbres, talus secs, abords des parkings |
| `terre` | `core_dirt_light` | remplace `core_dirt_med` | 128 x 128 | potagers, chemin de l'aire de jeux, talus nus |
| `montagne` | `core_grass_dark` | inchangée | 256 x 256 | couronne de montagnes et plaine lointaine |
| `ciel` | `sky` | inchangée | - | matériau d'outil du ciel (ne pas projeter) |
| `clip` | `clip_player` | inchangée | - | murs invisibles (matériau d'outil) |
| `asphalte` | `core_asphault_med` | remplace `t7_asphalt_dirty_dark_desert` | 160 x 160 | chaussées, parkings, cour d'école (enrobé gris moyen fissuré) |
| `asphalte_sombre` | `core_asphault_dark` | **nouvelle** | 160 x 160 | rapiéçages, enrobé neuf, aires de jeux |
| `trottoir` | `t7_concrete_sidewalk_02` | inchangée | 80 x 80 | trottoirs de rue et trottoir le long de la façade du bâtiment 1 |
| `dalle_claire` | `t7_concrete_sidewalk_01` | **nouvelle** | 80 x 80 | terrasses dallées des maisons, parvis, bandes de la cour |
| `bordure` | `t7_street_concrete_curb_01a` | inchangée | 80 x 20 | bordures de trottoir et de parking |
| `marquage` | `t7_plastic_base_clean` | **nouvelle** | 80 x 80 | peinture blanche au sol (briques de 1,5 u) : places, passages piétons, rond-point |
| `marquage_decal` | `t7_decal_signage_street_lines_white` | **nouvelle** | 80 x 10 | décalque de ligne blanche (à tester ; repli : marquage) |
| `gravier` | `t7_stone_pebbles_01` | inchangée | 80 x 80 | gravillon des allées et abords |
| `gravier_clair` | `core_gravel_light` | **nouvelle** | 128 x 128 | toit gravillonné de l'annexe, toits plats clairs de l'école |
| `facade_beige` | `core_plaster_light` | remplace `t7_plaster_smooth_light_01` | 128 x 128 | façade des halls (avant) des trois immeubles |
| `facade_blanche` | `t7_plaster_smooth_light_01` | remplace `t7_concrete_worn_painted_white` | 160 x 160 | façade arrière, pignons, pilastres, lucarnes |
| `socle` | `t7_concrete_floor_sealed_01_warm` | remplace `t7_brick_worn_heavy_grout_brown_wet` | 160 x 160 | soubassement brun (56 u) et jupe de terrasse |
| `panneau` | `t7_metal_wall_corrugated_hor_brown_drk` | remplace `t7_wood_panel_01_stain_brown_drk` | 80 x 80 | panneaux horizontaux bruns des avant-corps de halls |
| `loggia` | `t7_drywall_painted_brown_01` | inchangée | 80 x 80 | fond des loggias |
| `fenetre` | `core_window_opaque` | inchangée | par ouvrant | fenêtre opaque à cadre blanc et 2 x 2 carreaux (échelle = taille de l'ouvrant) |
| `vitre` | `core_glass_plain_trans` | inchangée | 80 x 80 | vitrage transparent : appartement jouable, halls, sas |
| `fond_vitre` | `t7_metal_painted_wall_dirty_black` | **nouvelle** | 80 x 80 | fond sombre des niches de fenêtre, châssis de hall, verrières de toit |
| `cadre` | `t7_plastic_base_clean` | **nouvelle** | 80 x 80 | menuiseries blanches (montants de porte-fenêtre, coffres de volets) |
| `appui` | `t7_concrete_trim_beveled_03` | inchangée | 160 x 40 | appuis de fenêtre, chapeaux de souche |
| `volet` | `t7_metal_wall_corrugated_hor` | remplace `t7_drywall_painted_beige_01` | 80 x 80 | volets roulants blancs (lames horizontales) |
| `garage` | `t7_metal_panels_painted_2x4` | remplace `core_door_metal_light` | 160 x 160 | portes de garage sectionnelles blanches (annexe, garages, maisons, option B3) |
| `porte` | `core_door_wood_dark` | inchangée | 40 x 80 | portes d'appartement et de maison |
| `porte_asc` | `t7_metal_bare_stainless_steel_brushed` | inchangée | 80 x 80 | portes palières de l'ascenseur (entités scriptées) |
| `garde_corps` | `t7_metal_paint_worn_grey_dk` | remplace `t7_metal_worn_iron_dark` | 80 x 80 | garde-corps des loggias, descentes d'eau, mâts |
| `rail_clair` | `t7_metal_perforated_small_white` | **nouvelle** | 80 x 80 | panneau ajouré blanc des balcons niveaux 3 et 4, grilles blanches de clôture (alpha, à tester) |
| `rail_clair_main` | `t7_metal_painted_clean_white` | **nouvelle** | 80 x 80 | main courante et plinthe des rails blancs |
| `rail_sombre` | `t7_metal_grating_expanded` | **nouvelle** | 80 x 80 | panneau ajouré sombre des balcons niveaux 1 et 2 (alpha, à tester) |
| `rail_sombre_main` | `t7_metal_painted_wall_dirty_black` | **nouvelle** | 80 x 80 | main courante et plinthe des rails sombres |
| `rail_plein` | `t7_metal_worn_painted_graphite` | **nouvelle** | 80 x 80 | segments pleins (brise-vue) du niveau 1 |
| `rail_vert` | `t7_glass_frosted_01_opaque_teal` | **nouvelle** | 80 x 80 | garde-corps vert sarcelle de la terrasse du rez (à tester ; repli : rail_plein) |
| `dalle_balcon` | `t7_concrete_bare_weathered_01` | remplace `t7_concrete_floor_sealed_01` | 80 x 80 | dalles de balcon, murets de clôture |
| `balcon` | `t7_plaster_smooth_light_01` | remplace `t7_concrete_worn_painted_white` | 160 x 160 | nez de dalle (tranche) des balcons |
| `toit` | `core_roof_dark` | inchangée | 128 x 128 | toits des immeubles (ardoise gris violacé), école, maisons grises |
| `toit_terre` | `core_roof_light` | **nouvelle** | 128 x 128 | toits en terre cuite : maisons, toit orange de l'école, Maison de Pays |
| `toit_plat` | `t7_rubber_roof_granular` | **nouvelle** | 160 x 160 | toits plats des maisons et des annexes |
| `rive` | `t7_wood_trim_dark_brown` | inchangée | 80 x 5 | fascia et sous-face du toit (brun très foncé) |
| `cheminee` | `t7_plaster_smooth_light_01` | inchangée | 160 x 160 | souches de cheminée des immeubles et des maisons |
| `auvent` | `t7_concrete_bare_weathered_01` | remplace `t7_metal_paint_worn_grey_dk` | 80 x 80 | auvent mince des halls |
| `hall_sol` | `t7_stone_travertine` | inchangée | 80 x 80 | sol et marches des halls |
| `hall_mur` | `core_plaster_light` | remplace `t7_drywall_base_cream` | 128 x 128 | murs de hall et de cage (crème) |
| `plafond` | `t7_drywall_painted_white_01` | inchangée | 80 x 80 | plafonds |
| `rampe` | `t7_metal_bare_stainless_steel_brushed` | inchangée | 80 x 80 | mains courantes d'escalier |
| `boites` | `t7_metal_bare_aluminum_brushed` | remplace `t7_metal_painted_clean_white` | 80 x 80 | boîtes aux lettres du hall |
| `dalle` | `t7_concrete_floor_sealed_01` | inchangée | 160 x 160 | dalles d'étage et de rez, fondations |
| `gaine` | `t7_concrete_floor_sealed_01` | inchangée | 160 x 160 | gaine d'ascenseur |
| `cabine` | `t7_metal_bare_stainless_steel_brushed` | inchangée | 80 x 80 | cabine d'ascenseur |
| `cabine_sol` | `t7_linoleum_floor_tile_square` | remplace `t7_metal_floor_square_pattern_01` | 80 x 80 | plancher de cabine |
| `appart_mur` | `t7_drywall_painted_white_01` | inchangée | 80 x 80 | cloisons de l'appartement |
| `sol_entree` | `core_tile_light` | inchangée | 80 x 80 | sol de l'entrée |
| `sol_cuisine` | `t7_ceramic_tiles_16x16` | inchangée | 80 x 80 | sol de cuisine |
| `sol_sdb` | `t7_ceramic_tile_shower_white` | inchangée | 80 x 80 | sol de salle de bain |
| `sol_chambre` | `t7_wood_veneer_sugarpine_matte` | inchangée | 80 x 80 | parquet |
| `faience` | `t7_ceramic_tile_large_white` | inchangée | 80 x 80 | faïence et crédence |
| `meuble` | `t7_wood_panel_01_stain_brown_drk` | inchangée | 80 x 80 | plan de travail |
| `annexe` | `t7_concrete_poured_bunker_paint_01_grey_lt` | inchangée | 160 x 160 | annexe basse devant le bâtiment 1 |
| `garages` | `t7_plaster_smooth_light_01` | remplace `t7_concrete_worn_painted_white` | 160 x 160 | bloc de garages blancs |
| `voisin` | `t7_plaster_rough_worn_01` | inchangée | 160 x 160 | crépi beige des pavillons (variante 1) |
| `voisin_clair` | `core_plaster_light` | **nouvelle** | 128 x 128 | crépi crème des pavillons (variante 2) |
| `voisin_blanc` | `t7_plaster_smooth_light_01` | **nouvelle** | 160 x 160 | crépi blanc des pavillons (variante 3) |
| `voisin_toit` | `core_roof_light` | remplace `core_roof_med` | 128 x 128 | tuiles terre cuite des pavillons |
| `voisin_toit_gris` | `core_roof_dark` | **nouvelle** | 128 x 128 | ardoise ou tuiles grises des pavillons |
| `volet_bleu` | `t7_metal_panels_2x16_trim_blue` | **nouvelle** | 160 x 160 | volets bleus de la maison relevée sur Street View (à tester) |
| `volet_vert` | `t7_metal_panels_painted_2x4_green` | **nouvelle** | 160 x 160 | volets verts |
| `volet_brun` | `t7_wood_worn_darker_brown` | **nouvelle** | 80 x 80 | volets bruns |
| `muret` | `t7_concrete_bare_weathered_01` | **nouvelle** | 80 x 80 | murets de clôture (0,55 m) |
| `grillage` | `core_fence_chain_link` | **nouvelle** | 80 x 80 | grillage de l'école et des potagers (alpha, à tester) |
| `ecole` | `t7_plaster_smooth_light_01` | remplace `t7_concrete_wall_weathered_01_wet` | 160 x 160 | murs blancs de l'école maternelle et de la Maison de Pays |
| `ecorce` | `t7_wood_planks_worn` | remplace `t7_wood_beam_worn_oak` | 80 x 80 | troncs des arbres en brushes |
| `feuillage` | `core_grass_dark` | inchangée | 128 x 128 | houppiers sombres (conifères, haies) |
| `feuillage_clair` | `core_grass_med` | inchangée | 128 x 128 | houppiers clairs (peupliers, feuillus) |
| `conteneur` | `t7_metal_panels_painted_2x1_grey` | remplace `t7_metal_paint_worn_grey_dk` | 160 x 160 | grands bacs à déchets gris clair |
| `metal` | `t7_metal_bare_graphite_matte` | inchangée | 80 x 80 | mâts d'éclairage, couvercles, poteaux |

### B.3 Les 20 clés remplacées

| Clé | Ancien | Nouveau | Pourquoi |
|---|---|---|---|
| `terre` | `core_dirt_med` | `core_dirt_light` | `core_dirt_med` ne fait que 256 px ; `core_dirt_light` en fait 512 |
| `asphalte` | `t7_asphalt_dirty_dark_desert` | `core_asphault_med` | l'enrobé « désert » est brun-ocre ; `core_asphault_med` est un gris moyen fissuré, proche du (95, 95, 98) relevé sur Street View |
| `facade_beige` | `t7_plaster_smooth_light_01` | `core_plaster_light` | `t7_plaster_smooth_light_01` est en réalité un gris clair ; `core_plaster_light` est un beige crème lisse (≈ 199, 196, 183 contre 200, 192, 178 proposé) |
| `facade_blanche` | `t7_concrete_worn_painted_white` | `t7_plaster_smooth_light_01` | `t7_concrete_worn_painted_white` est un gris-vert terne et tacheté ; l'enduit clair est un blanc cassé uniforme |
| `socle` | `t7_brick_worn_heavy_grout_brown_wet` | `t7_concrete_floor_sealed_01_warm` | la brique brune en version `_wet` a un aspect mouillé ; le béton ocre-brun, sec et lisse, est plus proche du soubassement brun-mauve lisse [VU] |
| `panneau` | `t7_wood_panel_01_stain_brown_drk` | `t7_metal_wall_corrugated_hor_brown_drk` | le bois a un fil vertical très sombre ; le bardage à lames horizontales brunes imite les panneaux « type persiennes » |
| `volet` | `t7_drywall_painted_beige_01` | `t7_metal_wall_corrugated_hor` | `t7_drywall_painted_beige_01` est une peinture de cloison kaki sans lames ; le bardage blanc à lames se lit comme un volet roulant |
| `garage` | `core_door_metal_light` | `t7_metal_panels_painted_2x4` | `core_door_metal_light` est un métal nu sans panneaux ; `t7_metal_panels_painted_2x4` est un panneau blanc à joints (porte sectionnelle) |
| `garde_corps` | `t7_metal_worn_iron_dark` | `t7_metal_paint_worn_grey_dk` | le fer brut noir est un micro-matériau ; gris anthracite peint pour les loggias et les mâts |
| `dalle_balcon` | `t7_concrete_floor_sealed_01` | `t7_concrete_bare_weathered_01` | béton clair et uniforme au lieu du béton marbré brun-gris ([VU] « gris béton clair ») |
| `balcon` | `t7_concrete_worn_painted_white` | `t7_plaster_smooth_light_01` | même défaut que `facade_blanche` ; le nez de dalle est clair |
| `auvent` | `t7_metal_paint_worn_grey_dk` | `t7_concrete_bare_weathered_01` | [VU] « mince dalle plate grise » : béton, pas tôle peinte |
| `hall_mur` | `t7_drywall_base_cream` | `core_plaster_light` | `t7_drywall_base_cream` est un gris neutre malgré son nom ; `core_plaster_light` est crème |
| `boites` | `t7_metal_painted_clean_white` | `t7_metal_bare_aluminum_brushed` | alu brossé plutôt que blanc (à confirmer sur photo du hall) |
| `cabine_sol` | `t7_metal_floor_square_pattern_01` | `t7_linoleum_floor_tile_square` | la plaque actuelle est de type science-fiction (voyants bleus) ; lino gris à dalles carrées |
| `garages` | `t7_concrete_worn_painted_white` | `t7_plaster_smooth_light_01` | même défaut que `facade_blanche` |
| `voisin_toit` | `core_roof_med` | `core_roof_light` | `core_roof_med` n'a que 64 px (flou) ; `core_roof_light` est une vraie tuile terre cuite de 512 px |
| `ecole` | `t7_concrete_wall_weathered_01_wet` | `t7_plaster_smooth_light_01` | la version `_wet` donne un aspect mouillé ; murs blancs [VU] |
| `ecorce` | `t7_wood_beam_worn_oak` | `t7_wood_planks_worn` | `t7_wood_beam_worn_oak` est une poutre ; planches brun-gris à fil vertical |
| `conteneur` | `t7_metal_paint_worn_grey_dk` | `t7_metal_panels_painted_2x1_grey` | bacs gris clair [VU] et non gris foncé |

### B.4 Projection des textures (le gain de réalisme le moins cher)

**Constat.** `make_blockout.py` écrit `256 256 0 0 0 0` sur **toutes** les faces (lignes 208 et 221), soit 36 901 faces dans les prefabs de la v0.2. J'ai relu les `.map` officiels de `map_source\` : sur les faces de `t7_street_concrete_curb_01a` (456), `t7_concrete_trim_beveled_01_wet` (1 767) et `t7_wood_trim_dark_brown` (231), le format est bien :

```
( p1 ) ( p2 ) ( p3 )  matériau  W H xoff yoff rot 0  lightmap_gray 16384 16384 0 0 0 0
```

- le **5e nombre est une rotation en degrés** (0, 90, −90, 180 observés ; `64 16 0 800 90 0` sur une face de dessous de bordure), les 3e et 4e des décalages [MESURÉ] ;
- `W H` valent le plus souvent `64 16` pour une bordure (image 1024 × 256), `64 4` pour un liseré (1024 × 64), `128 128` pour un enduit (2048 × 2048) : ils **gardent le rapport de l'image** ; c'est donc la taille en unités d'une répétition [DÉDUIT, cohérent avec 724 `.map`] ;
- `256 256` existe aussi dans les `.map` officiels : 420 des 456 faces de la bordure sont à `256 256` (6 faces de 70 brushes), très probablement la valeur par défaut de création, que les artistes règlent sur les faces visibles [DÉDUIT] ; l'audit v0.2 (§6, T1) écrivait « jamais 256 » d'après un échantillon de `mp_sector` : c'est exact pour les faces réglées, pas pour toute la bibliothèque. Une bordure de 1024 × 256 à `256 256` est étirée de 4 fois en longueur et de 16 fois en hauteur par rapport au `64 16` du stock.

**Règle.** `W × H` = valeur du stock × `ECHELLE` (1,25) en gardant le rapport de l'image ; valeurs de départ dans la colonne « projection » de §B.2 (les matériaux naturels, asphalte, herbe, toits, sont réglés à l'œil à 128 ou 160 pour que les fissures et les tuiles aient une taille crédible). Décalages `0 0`.

**Rotation des bandes** (rapport ≥ 3, ex. `bordure` 80 × 20, `appui` 160 × 40, `rive` 80 × 5) : faces verticales `rot 0` (le grand côté de l'image est horizontal) ; faces horizontales `rot 0` si la bande court le long de l'axe `x` du monde, `90` si elle court le long de `y`, sur le modèle des `.map` officiels. `bloc()` reçoit un paramètre `bande=` (`'x'` ou `'y'` ; pour un immeuble orienté en `y`, `Immeuble.ajoute()` bascule seul) ; défaut : 0.

**Projection explicite** : le 4e élément optionnel d'un plan `(n, p, mat, proj)` l'emporte sur la table ; il sert aux fenêtres (`proj = (largeur de l'ouvrant, hauteur de l'ouvrant)`), aux nez de dalle et aux jupes.

**À confirmer une fois dans Radiant (5 minutes, avant de généraliser)** : ouvrir `batiment_1.map`, sélectionner une face de bordure et une face de fenêtre, ouvrir l'inspecteur de surface (`S`) et vérifier que « Scale » et « Rotation » affichent ce qui a été écrit ; noter le résultat en commentaire de `materiaux.py` (constante `ROT_BANDE`). Si l'orientation des bandes est inversée, corriger **cette seule constante**.

### B.5 Matériaux à tester en jeu, et replis

| Clé | Risque | Test | Repli (une ligne dans `REPLI`) |
|---|---|---|---|
| `rail_clair`, `rail_sombre` | alpha non découpé sur un brush (panneau plein ou noir) | regarder un balcon de B1 à 5 m et à 30 m | `rail_clair_main`, `rail_sombre_main` (panneau opaque) |
| `rail_vert` | verre givré opaque, rendu inconnu | idem, rez | `rail_plein` |
| `grillage` | idem | clôture de l'école | `garde_corps` (panneau plein de 40 u) |
| `marquage_decal` | décalque sans surface support | un passage piéton | `marquage` (briques de 1,5 u, déjà le défaut) |
| `vitre` | transparence, reflet de sonde | porte du hall et appartement | `fenetre` |
| `fenetre` | orientation des 2 × 2 carreaux, cadre | une façade vue de 10 m | rien (rotation par `proj`) |
| `volet_bleu` | instance de `t7_metal_panels_2x16_trim` : teinte inconnue | maison 131540499 | `volet_brun` |

`materiaux.py` expose `ALPHA_OK = True` : à `False`, toutes les clés de ce tableau retombent sur leur repli. Ce drapeau est le seul interrupteur à connaître après le test.

### B.6 Modèles (xmodel) retrouvés dans les GDT

Tous les xmodel sont à **1 unité = 1 pouce** ; `modelscale 1,25` les aligne sur l'échelle du quartier pour un objet d'usage courant. Dimensions en « mètres de modèle » mesurées par l'inventaire (`materiaux.json`).

| Modèle | Dimensions | Usage | `modelscale` |
|---|---|---|---|
| `veh_t7_civ_car_compact_grey` / `_blue` / `_black` / `_green` | 3,38 × 1,75 × 1,58 | voitures proches (26 675 sommets chacune) | 1,25 |
| `veh_t7_civ_city_car_vista` | 3,26 × 1,78 × 1,61 | voitures lointaines (328 sommets) | 1,25 |
| `p7_bench_modern_01` | 2,03 × 0,46 × 0,61 | bancs | 1,25 |
| `p7_foliage_tree_albizia_tall_full` | 14,5 × 13,9 × 19,4 | feuillus de plus de 6 m | `h_réelle_m × 0,0644`, borné à `[0,35 ; 1,0]` |
| `p7_foliage_tree_olive_small` | 1,9 × 2,2 × 2,4 | arbres de jardin de 3 m | 1,5 |
| `p7_foliage_tree_acacia_bush` | 2,1 × 1,6 × 1,15 | arbustes de jardin | 1,6 |
| `p7_foliage_hedge_box_128_48_60` | 3,84 × 1,8 × 1,85 | haies hautes (2 m réels) | 1,35 |
| `p7_foliage_hedge_box_128_48_36` | 3,57 × 1,56 × 1,1 | haies basses (1,4 m) | 1,6 |
| `p7_foliage_hedge_round_48_48_36_vibrant` | 1,49 × 1,42 × 1,05 | buissons ronds | 1,6 |
| `p7_foliage_grass_tussock_green_1` / `_2` / `_3`, `p7_foliage_grass_flowers` | 2,1 / 0,95 / 0,35 / 0,65 | touffes (150 au plus, §C.9) | 0,8 à 1,3 |
| `p7_trashcan_metal_modern_glass` / `_paper` / `_organic` | 0,84 × 0,84 × 1,23 | bacs de tri | 1,25 |
| `p7_zm_der_dumpster_metal_large` | 3,91 × 1,57 × 1,3 | benne (option) | 1,25 |
| `p7_civ_sat_dish` | 0,99 × 1,13 × 1,67 | paraboles sur balcons (option) | 1,25 |
| `p7_ac_unit_wall_mount_01` | 0,92 × 0,63 × 0,64 | climatiseurs sur balcons (option) | 1,25 |
| `p7_pipe_pvc_drain_128` | 0,1 × 0,1 × 3,25 | descentes d'eau (option : §A utilise des brushes) | 1,25 |
| `p7_cai_planter_square` | 1,07 × 1,27 × 1,13 | jardinières (option) | 1,25 |
| `p7_sin_bollard_tall_painted` | 0,21 × 0,21 × 1,0 | potelets d'entrée de parking | 1,25 |
| `p7_street_curb_concrete_64a` | 1,63 × 0,21 × 0,21 | non retenu : les bordures restent des brushes | |
| `p7_louver_window_wooden_closed`, `p7_door_metal_rolling_02`, `p7_zm_der2_utility_pole_512` | | non retenus | |

**Absents (vérifié par noms)** : peuplier, sapin ou autre conifère, lampadaire de rue, panneau routier, boîte aux lettres, bouche d'incendie, jeux d'enfants, souche de cheminée. Ils sont donc **en brushes** (§C.9, §C.10, §A.9).

### B.7 Instances teintées : option de phase 6 seulement

Les six instances proposées par l'inventaire (`zm_seyssel_crepi_beige`, `zm_seyssel_toit_brun`, `zm_seyssel_hall_sol_creme`…) donneraient des teintes exactes (beige plus chaud, tuile brune, sol de hall crème). **Elles ne sont pas utilisées** : D10. Conditions pour les ajouter plus tard : un GDT à nous dans `texture_assets\` des Mod Tools, `tools/sync.ps1` étendu pour le copier, un essai de compilation, un jugement à l'œil en jeu. Aucune clé du contrat n'en dépend ; basculer une clé vers une instance sera un changement d'une ligne.

### B.8 `tools/materiaux.py` : interface

Fichier **sans dépendance** (bibliothèque standard).

```python
MAT       = {...}            # les 79 clés (§B.2), ALPHA_OK appliqué
REPLI     = {"rail_clair": "rail_clair_main", ...}      # §B.5
ALPHA_OK  = True
ECH       = {"core_plaster_light": (128, 128), ...}     # nom de matériau -> (W, H), sans doublon
ROT_BANDE = {"x": 0, "y": 90}                           # à confirmer dans Radiant (§B.4)
MODELES   = {"voiture": ("veh_t7_civ_car_compact_{couleur}", 1.25), ...}

def projection(materiau, normale, bande=None) -> (W, H, xoff, yoff, rot)
def verifier(mod_tools, index=None) -> list          # noms de MAT.values() et de MODELES absents des GDT
# python tools\materiaux.py --verifier ["<Mod Tools>"]   code de retour 1 s'il manque un nom
# python tools\materiaux.py --index                      écrit _build\index_gdt.json (ignoré par git), réutilisé ensuite
```

Branchements :

- `make_blockout.brush_lines_mat()` et `brush_lines()` : remplacer le `256 256 0 0 0 0` en dur par `W H xoff yoff rot 0` fournis par `projection()` (ou par le 4e élément du plan) ; accepter des plans à 3 ou 4 éléments ; `check_brush()` n'utilise que `pl[0]`, `pl[1]`.
- `build_map.py` : appelle `verifier()` si l'index existe (échec bloquant) et affiche l'avertissement sinon ; les noms de matériaux d'outil (`sky`, `clip_player`, `trigger`, `caulk`, `volume`) sont exemptés.
- `preview_blockout.COULEURS` : ajouter les sous-chaînes `plaster_light`, `perforated`, `grating`, `corrugated`, `roof_light`, `rubber_roof`, `linoleum`, `aluminum`, `graphite`, `plastic_base`, `gravel`, `planks` pour que les rendus d'aperçu ne retombent pas sur la couleur par défaut.


## C. Quartier

### C.1 Cadre, terrain, bord du monde, montagnes

| Élément | v0.2 | v0.3 |
|---|---|---|
| Cadre `X0, X1, Y0, Y1` | −4608, 5888, −4608, 5888 | **−5120, 6656, −6656, 5888** (11 776 × 12 544 u, 239 × 255 m) |
| Pas du terrain | 256 | **256** (47 × 50 points, 4 508 triangles contre 3 362) |
| Fond des prismes de terrain | `min(z) − 96` : fente de ciel de 5,1 m à l'est | `min(−160, min(z) − 96)` : les prismes recouvrent toujours la plaine (z = −64) |
| Couronne de montagnes | `r0 = 7600`, `r1 = 10200` | `r0 = 9400`, `r1 = 12000`, centre = centre du cadre `(768, −384)` |
| Ciel et volumes (`build_map.C`) | 10 400 | **12 600** ; coordonnées extrêmes 13 368 < 16 384 [DÉDUIT : limite de coordonnées de Radiant, à confirmer à l'ouverture] |
| Murs `clip` | au cadre | au nouveau cadre |

Raisons : l'école va jusqu'à `y = −6381` et la Maison de Pays jusqu'à `x = −5024` [MESURÉ] ; 6 bâtiments BD TOPO du terrain n'étaient pas représentés ; le coin du nouveau cadre est à 8 604 u du centre, soit plus que l'ancien `r0`. Le relief IGN (grille 4 m, écart LiDAR 0,12 ± 0,27 m) **n'est pas modifié**.

- `hauteurs()` : les rectangles aplanis sont ceux d'`Immeuble.emprise` (§A.1) et ceux des maisons et de l'école (marge de 128 conservée).
- **Matériaux de mailles** : base `herbe` ; `herbe_sombre` selon `(i × 7 + j × 3) % 11 == 0` comme en v0.2 ; `herbe_clairsemee` sous les arbres de couronne ≥ 3 m (mailles à moins de 200 u) ; `asphalte` pour les parkings (cellules dont le centre est dans le rectangle, **rectangles calés sur la grille de 256**, bordures au vrai tracé) ; `gravier_clair`/`gravier` aux abords.
- **Levier de budget** (à n'activer que si le plafond de 19 000 brushes est menacé) : fusionner les mailles par blocs de 2 × 2 hors du cœur (`x < −2600` ou `y < −3400`), soit ≈ −1 300 brushes. Les sommets impairs de la frontière prennent la moyenne de leurs deux voisins pairs, et `Quartier.z()` lit la même grille corrigée, pour qu'il n'y ait ni fente ni écart de hauteur.
- **Parkings (rectangles calés sur 256)** :

| Zone | Rectangle `(x0, y0, x1, y1)` | Réel [ORTHO] |
|---|---|---|
| `PARKING_BAS` | `(512, −1024, 1792, 2048)` | enrobé `x 450..1850`, `y −1000..2100` |
| `PARKING_HAUT` (= `ZONE_JEU`) | `(1792, −768, 3072, 1024)` **inchangé** | route, rond-point et places marquées (D13) |
| `ALLEE_GARAGES` | `(1536, 1536, 1792, 3072)` inchangé | route de 4 m le long des garages |
| `PARKING_NORD` (nouveau) | `(0, 3840, 1536, 4864)` | grand parking marqué au nord du bâtiment 2, `x 80..1420`, `y 3920..4900` |
| `COUR_ECOLE` (nouveau) | `(1024, −4864, 3072, −1792)` | cour d'enrobé de l'école |

`PARKING_BAS` ne recouvre plus la façade du bâtiment 1 (le mur est à `x = 217`, les halls à 297) : un **trottoir** `trottoir` court le long de la façade, de `x = 217` (ou 297 devant les halls) à `x = 420`, dessus à `z = 0`, puis une **pelouse** jusqu'au parking. Un îlot planté (`x 1024..1792`, `y 1280..1536`, en herbe, 3 buissons ronds) ouvre le parking au nord de l'annexe.

### C.2 Gameplay à préserver

Aucun brush, modèle, mât ni voiture nouveau n'entre dans ces zones (le sol, la peinture au sol et les bordures y sont permis) :

| Objet (docs/gameplay/zone-01-hlm.md, `build_map.py`) | Position | Zone d'exclusion |
|---|---|---|
| Spawn des joueurs | (2935, −12) | disque de rayon 450 |
| Quick Revive, Juggernog, Speed Cola, Double Tap | alignés vers `x ≈ 2050`, `y 404..788` | rectangle `(1950, 360, 2150, 840)` |
| Mystery Box | (2058, −398) | rayon 200 |
| Pack-a-Punch | (2292, 924) | rayon 250 |
| Interrupteur du courant | (2447, 941) | rayon 200 |
| Fusil à pompe | (2456, −458) | rayon 150 |
| Caméra de fin `intermission` | (3300, −200, 420) | rayon 300 |
| 12 sorties de zombies `SORTIES_ZOMBIES` | liste de `build_map.py` | `Quartier.libre(x, y, 48)` doit rester vrai (sinon la sortie est silencieusement perdue) |

À ajouter à `Quartier` : `ZONES_GAMEPLAY` (liste de disques et rectangles) et `interdit(x, y, marge=0)`, appelée par `mobilier`, `vegetation`, `voitures`, `clotures`. À ajouter à `build_map.py` : **6 sorties de zombies** dans les nouvelles zones, `(2000, −4500)` (cour de l'école), `(5200, 800)`, `(1500, 5300)`, `(−3000, 3000)`, `(−3800, −3000)`, `(5200, −3500)`, filtrées par `libre()`. Le mini-giratoire (centre (2674, 401), anneau de rayon 260 et de largeur 220) est à 119 u au moins du spawn et à plus de 350 u des autres objets : compatible.

### C.3 Voirie

**Sources.** Axes : `bdtopo_quartier.json["routes"]` (41 tronçons, nature, nom, `largeur_m`) pour toutes les voies nommées et les ronds-points ; `site_pres_dombet.json` (OSM) pour les `service` et `footway` qui ne sont pas à moins de 150 u d'un tronçon BD TOPO. Les `secondary`, `residential` et `tertiary` d'OSM ne sont plus tracés (doublons). Les paires `Route à 2 chaussées` de même nom et de sens opposés sont **fusionnées en un axe moyen** (l'avenue Borcier au nord de `y ≈ 1300` : deux chaussées de 3 m devenaient une bande de 10 à 12 m).

| Voie | Chaussée (u) | Réel | Trottoirs | Source |
|---|---|---|---|---|
| Avenue Borcier | **368** | 7 à 8 m | 2 × 100, bordure | [MESURÉ] BD TOPO 7 m ; [ORTHO] 7 à 8 m ; [VU] trottoir ≈ 2 m |
| Chemin de la Fontaine | **320** | 6 à 8 m | côté sud, 80 | [ORTHO] ; BD TOPO (3,5 / 4 m) sous-estime |
| Rue des Prés Dombet | **270** | 5,5 m | côté maisons 90 ; devant B1 : trottoir de façade | [VU] 5,5 à 6,5 m ; BD TOPO 4 à 5 m |
| Rue de Crétillon | 220 | 4,5 m | aucun | BD TOPO 4 m |
| Allées de parking (OSM `service`, BD TOPO sans nom) | 220 | 4,5 m | aucun | BD TOPO 4 à 5 m |
| Mini-giratoire | anneau 220, rayon d'axe 260 | boucle de 10,6 m | | BD TOPO « Rond-point » (3 m) |
| `footway` | 80 | 1,6 m | | OSM |

**Construction** (module `tools/voirie.py`) :

1. **Rubans.** Chaque polyligne est rééchantillonnée tous les `PAS_ROUTE = 96` u (128 si le relief est plat à ± 6 u sur le tronçon, 64 sinon). En chaque point, normales moyennées aux angles (rapport de biseau ≤ 1,5), points gauche et droit ; chaque quadrilatère devient **deux prismes triangulaires** qui partagent leur arête (pas de fente aux virages, plus d'encoches comme en v0.2).
2. **Cote de la chaussée** : `z_route = max(z du terrain aux 4 coins et au centre du quadrilatère) + 5`, fond à `min − 24`. Cela supprime les points où le terrain perce l'asphalte (3,5 % des points de contrôle en v0.2).
3. **Raccord des carrefours** : les rubans de même matériau et de même cote peuvent se recouvrir sans conséquence (même projection mondiale). Un quadrilatère est écarté s'il est entièrement hors cadre (à 64 près) ou dans une `emprise`.
4. **Trottoirs** : bandes de largeur `ws` contre le bord de la chaussée, dessus à `z_route + 6`, matériau `trottoir` ; **bordure** : pavé de 6 de large et 11 de haut le long de l'arête extérieure, un brush par 128 u de bord, matériau `bordure`, `proj` `(80, 20)`, rotation de bande (§B.4). Pas de bordure aux entrées de parking ni devant les portes de halls.
5. **Marquages** (`marquage`, briques de 1,5 u de haut posées sur la chaussée, même projection) :
   - **passage piéton** : 4 bandes de 40 u (le long de la voie) espacées de 80, longues de la largeur de chaussée moins 40. Emplacements : avenue Borcier vers `(−2400, −1650)` [ORTHO] ; entrée du carrefour de la rue des Prés Dombet près de `(2300, 1400)` [DÉDUIT : « 4 bandes à l'entrée du carrefour », Street View] ; à compléter avec des photos ;
   - **places de parking** : lignes blanches de 4 u de large (voir §C.4) ;
   - **mini-giratoire** : disque central de 16 pans, rayon 150 (diamètre 6 m [VU]), 1 brush ; l'anneau est déjà le ruban BD TOPO.
6. Pas de ligne axiale sur la rue des Prés Dombet [VU], pas de marquage sur l'avenue [VU].

Budget voirie : chaussées ≈ 1 500, trottoirs ≈ 600, bordures ≈ 650, marquages ≈ 450.

### C.4 Places de stationnement, annexe, garages

**Places** (largeur 123 = 2,5 m, profondeur 246 = 5 m ; lignes de 4 u ; lues sur l'orthophoto à ± 100 u, **à recaler sur `img/ortho-quartier.jpg`**) :

| Rangée | Départ | Direction | Nombre | Angle |
|---|---|---|---|---|
| Haut sud | `(2080, −1420)` | `+x`, pas 123 | 8 | 90°, profondeur vers `+y` |
| Haut centre, groupe A | `(2150, −900)` | `+y`, pas 123 | 5 | 90°, profondeur vers `+x` |
| Haut centre, groupe B | `(2150, −400)` | `+y`, pas 123 | 4 | 90° |
| Épi sud-ouest | `(890, −1030)` | vers `(1590, −1665)`, pas 165 | 6 | 45° |
| Rue des Prés Dombet nord-est | `(3100, 1000)` | vers `(4300, 2300)`, pas 165 | 10 | 45° |
| Nord du B2 | dans `PARKING_NORD` | `+x`, pas 123, deux rangées dos à dos | 20 | 90° |
| Chemin de la Fontaine sud | `(2670, 5170)` | `+x`, pas 123 | 10 | 90° |

Les groupes A et B passent à moins de 100 u du Mystery Box (2058, −398) et du fusil (2456, −458) : **uniquement de la peinture**, aucun objet (§C.2).

**Annexe et garages** (cotes actuelles conservées, écart ≤ 1,1 m [MESURÉ]) : annexe 21,2 × 12,6 m à toit plat, `annexe`, toit `gravier_clair` avec acrotère de 16 u (`annexe`), portes `garage` (blanches) ; bloc de garages 27,1 × 5,5 m, murs `garages`, portes `garage` toutes les 136 u, toit plat `toit_plat` avec acrotère. **Conteneurs** : deux grands bacs gris clair `conteneur`, 123 × 123 × 98, couvercle `metal`, à `(2300, 150)` et `(2300, 330)` [ORTHO : `x 2100..2300`, `y 100..600`], plus trois bacs de tri `p7_trashcan_metal_modern_*`. Les trois conteneurs semi-enterrés de la v0.2 (`x 1900..2092`, `y 1150`) sont supprimés (10 à 20 m trop au nord).

### C.5 Maisons voisines : pilotées par les données

**Pourquoi.** En v0.2 chaque maison est un pavé, un toit à deux pans de 32° et une souche (3 brushes), avec 300 u de mur partout : ce sont des inventions. La BD TOPO et le LiDAR donnent, pour chaque bâtiment, l'emprise, la hauteur à l'égout et au faîtage, la pente, la forme du toit, l'angle du faîtage et la couleur du toit.

**Pipeline.** Nouvel outil `tools/maisons_donnees.py` (bibliothèque standard) qui écrit **`reference/maisons.json`** (≤ 200 Ko, versionné) : un enregistrement par bâtiment BD TOPO dont le centre est dans le cadre et qui n'est ni un immeuble, ni l'annexe, ni les garages :

```json
{ "id": "00831957", "osm": 131540499, "genre": "maison",
  "emprise": [[x, y], ...], "obb": [cx, cy, l, w, angle],
  "h_egout_m": 4.2, "h_faitage_m": 7.8, "pente_deg": 27,
  "toit": "pignons", "faitage_angle": 142, "toit_couleur": "gris", "etages_bdtopo": 2,
  "z_sol_jeu": 45 }
```

`genre` : `maison` (Résidentiel), `annexe` (Annexe), `commerce`, `technique` (OSM `telecom` ou `operator` : le central Orange 131537511, 10,9 × 10,7 m), `armoire` (OSM `height=3` et `roof:shape`), `abri` (OSM `wall=no` : 131537506 et 131538654), `ecole`, `salle` (Maison de Pays). `toit` ∈ `pignons`, `croupes`, `pignon_croupe`, `plat`, `pyramide` (d'après le LiDAR relu). Le fichier est régénérable ; les décisions de rendu restent dans `maisons.py`.

**Effectifs** dans le nouveau cadre (marge de 64 u) : **38 bâtiments** BD TOPO : les 3 immeubles, l'annexe et les garages (5, traités en §A et §C.4), **21 maisons** (10 à moins de 4 500 u du cœur de jeu `(2000, 500)` : **LOD proche** ; 11 plus loin : **LOD loin**), 3 volumes de l'école (§C.6), le central Orange, la Maison de Pays (§C.7) et 7 petits volumes (abris, annexes).

**Règles de volume** (`maisons.construire(q)`) :

| Point | Règle |
|---|---|
| Emprise | rectangle par rectangle : polygone tourné de l'angle de l'OBB, `is_orthogonal()` puis `rectangles(grid=8)` (les maisons en L ne sont plus remplacées par leur rectangle) ; sinon prisme de l'enveloppe convexe. Un angle à moins de 4° d'un multiple de 90° est arrondi à ce multiple. |
| Pied | `z_ref` = moyenne du terrain aux 4 coins et au centre ; fondation de `min(terrain) − 32` à `z_ref` ; le mur monte jusqu'à `z_ref + h_egout × 49,2` (plus de mur de 300 u partout) |
| Étages | 1 si `h_egout < 4,6 m` (rez et combles), 2 si `< 7,4 m`, 3 sinon |
| Toit | forme du LiDAR ; pente = moyenne des deux pentes mesurées, bornée à 20..34° ; faîtage parallèle à `faitage_angle` s'il est à moins de 30° d'un axe de l'OBB, sinon au grand côté ; débord 24 (gouttereaux), 20 (pignons) ; fascia 14 |
| Fonctions de toit (`tools/geom.py`) | `toit_pignon` (prisme à deux pans dont les bouts sont en crépi, un brush), `toit_croupe` (§A.9), `toit_demi_croupe` (un bout à croupe, un bout en pignon, un brush convexe), `toit_plat` (boîte + acrotère de 16) ; toutes passent `check_brush` |
| Couleur du toit | `toit_couleur` « brun », « tuiles » ou « rouge » → `voisin_toit` (terre cuite) ; « gris », « mousse » → `voisin_toit_gris` ; absent → 55 % gris par hachage de l'`id` ; toit plat : `toit_plat` |
| Mur | par hachage de l'`id` : 40 % `voisin`, 35 % `voisin_clair`, 25 % `voisin_blanc` |
| Ouvertures (LOD proche) | par façade et par niveau, une fenêtre de 54 × 62 (allège 40) par tranche de 150 u de mur après 100 u de marge, centrées ; une **porte** de 44 × 106 (`porte`, perron de 8 u en `dalle_claire`) sur la façade qui regarde la route la plus proche ; fenêtre de combles de 40 × 40 dans chaque pignon des maisons à 1 niveau ; peau de 16 percée comme au §A.4 (niche de 8, vitrage `fenetre`) |
| Volets (LOD proche) | 70 % des fenêtres, deux vantaux de 27 u saillants de 2 u, couleur par hachage entre `volet`, `volet_brun`, `volet_vert` ; bleus (`volet_bleu`) sur la maison de référence |
| Cheminée | une souche `cheminee` de 24 × 24 sur le faîtage à `0,3 L`, chapeau `appui` |
| LOD loin | pas de peau percée : fenêtres plaquées de 2 u (8 par maison), porte, toit ; ≈ 18 brushes |
| Garages | pour le genre `annexe` : une porte `garage` de 118 × 100 sur la façade côté route |

**Maison de référence : 131540499 (BD 00831957, centre (3681, 254)).** C'est la seule vue de près [VU] : crépi crème (`voisin_clair`), toit à pignons de 27° en `voisin_toit` (le LiDAR lit « gris-vert / mousse », Street View des tuiles brun-rouge : Street View, vu de près, l'emporte), débord de 24 avec **3 pannes et consoles** par rampant (`rive`, 8 × 8 × 40), volets bleus, **balcon en fer forgé blanc** au pignon sur rue (2,2 m × 0,8 m : 108 × 40, dalle `dalle_balcon`, garde-corps `rail_clair`), muret `muret` de 27 u surmonté d'une grille `rail_clair` de 33 u (1,15 m au total), piliers de 12 × 12 × 60, portillon, haie `feuillage` de 98 u (2 m) du côté rue, recul de 4 à 6 m. L'orthophoto y voit aussi des panneaux solaires : deux plaques `fond_vitre` sur le pan sud. Pas d'autre maison n'est traitée à ce niveau (aucune autre n'a été vue de près) ; les autres reçoivent les règles génériques.

**Ajouts lus sur l'orthophoto** (phase 6) : terrasses dallées claires devant les maisons 961 et 967 (`dalle_claire`, 4 × 6 m) ; trois piscines hors-sol rondes (prisme de 12 pans, diamètre 221, hauteur 60, `muret`, eau `vitre`) près des maisons 964, 967 et 939 ; abris de jardin (≥ 4, toit orange ou gris).

**Genres particuliers** : `technique` : volume aveugle de 3 u au-dessus de l'égout, mur `annexe`, toit à pignons gris, porte `garage` ; `armoire` : 4 brushes, mur `facade_blanche`, toit à deux pans `rive` ; `abri` : 4 poteaux de 8 u (`rive`) et une dalle de toit `toit_plat`.

### C.6 École maternelle « Les Petits Princes »

Bâtiments BD TOPO / LiDAR de la zone (`zones_activite`, `x −1665..3165`, `y −6381..−1134`) :

| Bâtiment | Emprise | Hauteurs | Toit |
|---|---|---|---|
| `00831974` | 861 m², 54 × 29 m, `x 1068..2526`, `y −4565..−1903` (une dizaine de volumes) | égout 2,6 m (128 u), faîtage 6,2 m | pignons de pente bornée à 19°, ou plat si la largeur < 14 m ; `toit` (gris) ; **toit orange** `toit_terre` sur le volume `x 1350..1620`, `y −3335..−2620` |
| `97619879` | 153 m², 17,6 × 12,1 m | égout 3,3 m, faîtage 5,7 m | `toit_croupe` (pyramide), `toit` |
| `97619863` | 388 m², 28 × 14,6 m, centre (2417, −2245) | égout 2,1 m, faîtage 5,3 m | pignons 18 à 22° |

Murs `ecole` (blanc), fenêtres en bandeau de 88 × 64 (allège 44) tous les 3,5 m, portes `porte`. **Cour** `COUR_ECOLE` en `asphalte` ; **aire de jeux** à `x −350..810`, `y −4470..−2700` : pelouse, **chemin en boucle** de 80 de large le long du rectangle (4 pavés `terre`) et un « jeu » central (plateforme de 120 × 120 × 80 et deux montants, `muret` et `garde_corps`) ; **circuit de tricycles** peint (`marquage`, anneau de 12 segments de 25 u) à `x 2240..2950`, `y −4760..−4100` ; 7 arbres de 6 à 15 m (déjà dans le LiDAR). Pas de clôture périmétrique : aucune source ([INCONNU]).

Budget : ≈ 350 brushes.

### C.7 Maison de Pays

`00832292` : 883 m², 48,5 × 31,5 m, centre (−4186, 2370), angle 82°, égout 3,3 m (162 u), faîtage 8,4 m [MESURÉ]. Murs `ecole` (blanc), `toit_croupe` de 16° en `toit_terre` (toit brun-rouge à pans [VU] ; le LiDAR lit des croupes), rives `rive`, deux portes vertes (`volet_vert`, 88 × 106) côté est, six fenêtres par grand côté (LOD proche), grande aire de gravier clair (`gravier_clair`, `x −3190..−2025`, `y 2200..3800`). Budget ≈ 120 brushes.

### C.8 Clôtures, haies, jardins

Aucune source ne donne les limites de parcelle [INCONNU] ; règle **inférée** pour les maisons de LOD proche : 
- **côté route** (la route la plus proche à moins de 40 m) : muret `muret` de 27 u de haut et 12 d'épaisseur + grille `rail_clair` de 33 u, ou haie `feuillage` de 98 u d'épaisseur 48 (alternance par hachage) ; portillon (trou de 48 u) dans l'axe de la porte ; segments de 192 u ;
- **côtés** : haie de 98 u jusqu'à l'arrière de la maison ;
- **jardins** : potager (4 bandes de `terre`, 60 × 300) pour une maison sur trois (la BD voit des potagers à l'est de la 950) ; pas de piscine ailleurs que celles de §C.5.

≈ 12 brushes par maison de LOD proche ; plafond global 700.

### C.9 Végétation

Source unique : `reference/ign/lidar_quartier.json["arbres"]` (255 arbres, `x`, `y`, `h_m`, `rayon_m`, `elancement`) ; plus aucune position inventée.

| Classe | Critère | Représentation |
|---|---|---|
| **Peupliers de l'avenue** | sur la droite `x = 0,1303 × y − 1650`, `y` de −3358 à 4977, **pas de 251 u (5,1 m)**, ≈ 33 arbres | 3 brushes (tronc 20 × 20, deux troncs de cône à 8 pans, rayon 74), **hauteur 590 u (12 m ± 8 %)** (D6) |
| Conifères | `h ≥ 15 m` et `élancement ≥ 2,2`, hors de la droite | `sapin()` (5 brushes), rayon = `rayon_m`, hauteur = `h_m` ; les trois sapins posés à la main de la v0.2 sont supprimés |
| Feuillus proches | `élancement < 2,2`, `h ≥ 6 m`, à moins de 4 500 u du cœur | `misc_model` `p7_foliage_tree_albizia_tall_full`, échelle `h_m × 0,0644` (§B.6) |
| Petits sujets proches | `h < 6 m` | `p7_foliage_tree_olive_small` (échelle 1,5) ou `p7_foliage_tree_acacia_bush` (1,6) |
| Feuillus lointains | tous les autres | tronc + deux bicônes à 8 pans (3 brushes) |
| Haie de l'avenue | le long de la rangée de peupliers, 60 u vers la route | `bloc` 50 × 192 × 70 en `feuillage` (≈ 43 brushes) |
| Touffes d'herbe | 150 au plus (220 en v0.2), aléatoire à graine fixe, sur les pelouses du cœur | `p7_foliage_grass_tussock_*` |

Exclusions : toute position dans une `emprise`, sur une route (à 120 u près) ou dans une zone de gameplay (§C.2). `ARBRES_EXCLUS = [(57, 2387)]` : le conifère de 26,6 m du LiDAR de 2021 a disparu avant l'orthophoto de 2023. Les peupliers sont à 25 m du mur arrière de B1 [MESURÉ : pelouse de 26 m]. Budget : ≈ 500 brushes et ≈ 320 modèles.

### C.10 Mobilier urbain

| Objet | Représentation | Règle |
|---|---|---|
| Lampadaires | mât `metal` 8 × 8 × 270 (5,5 m [VU : 5 à 6 m]) + crosse 60 × 8 × 8, 2 brushes | tous les 1 800 u le long de la rue des Prés Dombet, de l'avenue et du chemin de la Fontaine, côté trottoir, ≈ 30 ; jamais dans `interdit()` |
| Panneaux | poteau `metal` 8 × 8 × 250 + plaque `marquage` 60 × 4 × 60 | cédez-le-passage près du carrefour de `(2300, 1400)` ; pas de pictogramme (aucun modèle) ; positions [DÉDUIT] |
| Bancs | `p7_bench_modern_01` ×1,25 | les 3 positions de la v0.2 + 2 à l'école |
| Bacs de tri | `p7_trashcan_metal_modern_*` ×1,25 | près des conteneurs et devant l'école |
| Potelets | `p7_sin_bollard_tall_painted` ×1,25 | aux 4 entrées de parking |
| Boîtes aux lettres | brushes de hall (déjà là) | |
| Poteaux électriques | non | aucune source |

Budget ≈ 250 brushes.

### C.11 Voitures

`veh_t7_civ_car_compact_{grey,blue,black,green}`, **`modelscale 1,25`** (la v0.2 les posait à l'échelle 1 : 2,7 m au lieu de 3,4 m). Au plus **40 voitures** : 26 compactes (à moins de 4 500 u du cœur) et 14 `veh_t7_civ_city_car_vista` (328 sommets) plus loin, car la compacte pèse 26 675 sommets. Placement : sur les rangées de §C.4 avec un taux d'occupation de 55 % décidé par hachage (graine fixe), orientées dans l'axe de la place ; deux rangées perpendiculaires dans le parking bas (`x 800..1300` vers `y = −300` ; `x 500..900` vers `y = −950` [ORTHO]) ; la rangée en épi devant le bâtiment 1 de la v0.2 (`x = 560`, pas de 230, hors des halls) est conservée parce qu'elle vient des photos de l'utilisateur. Aucune voiture dans `ZONES_GAMEPLAY`.

### C.12 Organisation du code et des prefabs

Pour que plusieurs personnes travaillent sans conflit :

| Fichier | Contenu | Propriétaire de la tâche |
|---|---|---|
| `tools/geom.py` (nouveau, **phase P0**) | `pave`, `tourne` (propage `proj`), `prisme_triangle`, `tronc_cone`, `boite_obb`, `dans_poly` (déplacés de `quartier.py`, ré-exportés par lui), `toit_pignon`, `toit_croupe`, `toit_demi_croupe`, `toit_plat`, `plaque_pente`, `prisme_pignon` ; importé par `immeuble.py`, `maisons.py`, `vegetation.py` | matériaux (infrastructure) |
| `tools/quartier.py` | classe `Quartier` : cadre, relief, `hauteurs`, `terrain`, `montagnes`, `ZONES_GAMEPLAY`, `construire()` qui appelle les modules | quartier |
| `tools/voirie.py` | rubans, trottoirs, bordures, marquages, places, parkings | quartier |
| `tools/maisons_donnees.py`, `tools/maisons.py` | pipeline `maisons.json`, maisons, annexes, garages, école, Maison de Pays, clôtures | quartier |
| `tools/vegetation.py`, `tools/mobilier.py` | arbres, haies, touffes ; lampadaires, bancs, conteneurs, voitures | quartier |
| `tools/immeuble.py`, `tools/immeubles_hlm.py` | §A | immeuble |
| `tools/materiaux.py`, `tools/make_blockout.py`, `tools/build_map.py`, `tools/controle_v03.py`, `preview_*` | §B et réception | matériaux (infrastructure) |

Interface de `Quartier` : `q.ajoute(groupe, planes)` avec `groupe` ∈ `terrain, montagnes, voirie, trottoirs, bordures, marquages, parkings, maisons, ecole, pays, clotures, vegetation, mobilier, annexes` ; `q.modele(nom, x, y, angle, echelle, dz, groupe)` (le modèle est écrit dans le prefab du groupe : `vegetation`, `mobilier`…) ; `q.emprises` ; `q.z(x, y)` ; `q.libre(...)` ; `q.interdit(...)`. La propriété `q.brushes` reste (concaténation des groupes) pour la compatibilité.

**Prefabs** : `build_map.prefab_groupe(nom, brushes, entites, max_brushes=2200)` écrit `nom.map` ou `nom_1.map`, `nom_2.map`… ; `build_map.py` supprime les `.map` du dossier des prefabs qu'il n'a pas écrits pendant l'exécution (comme `site_blockout.map`) et **échoue** si un fichier dépasse 1,9 Mo. Fichiers attendus : `terrain_1..2`, `montagnes`, `voirie_1..2`, `trottoirs`, `bordures`, `marquages`, `parkings`, `annexes`, `maisons_1..2`, `ecole`, `pays`, `clotures`, `vegetation`, `mobilier`, `batiment_1..3` (≈ 20 fichiers) ; chacun est référencé par un `misc_prefab` à l'origine, comme aujourd'hui. Le dossier des Mod Tools garde les anciens fichiers (`sync.ps1` ne supprime rien) : inoffensif tant que la map principale ne les référence pas.

Mises à jour d'outils d'aperçu : `preview_png.DEFAUT` lit **tous** les `.map` du dossier des prefabs ; `vues_standard.py` garde ses noms de cibles (`batiment_1..3`) et ajoute les vues de §D.4.


## D. Ordre d'implémentation, budget et réception

### D.1 Phases

Chaque phase se termine par `python tools\build_map.py` qui passe (« 2 secondes, déterministe ») et par ses critères de §D.3. Les phases P1 et P3 peuvent avancer en parallèle dès que P0 a fixé `materiaux.MAT` (les clés sont déjà dans §B.2 : on peut coder avec les chaînes avant que le fichier existe).

| Phase | Contenu | Fichiers | Dépend de | Critères |
|---|---|---|---|---|
| **P0 Infrastructure** | `materiaux.py` (MAT, ECH, projection, vérification), `make_blockout.brush_lines*` (projection par face), `build_map.prefab_groupe` (découpe, suppression des prefabs périmés, contrôle des 1,9 Mo, bilan des brushes), `geom.py` (dont les toits partagés), `controle_v03.py` (squelette) et instantanés de l'annexe 2, mises à jour de `preview_png.DEFAUT` et `preview_blockout.COULEURS` | §B.8, §C.12 | | R1 à R5 |
| **P1 Gabarit sur le bâtiment 1** | grille de fenêtres et peau percée, avant-corps de halls et entrées, loggias, soubassement, balcons filants et terrasse, fenêtres arrière, pignons, toit à croupes, souches, verrières, corrections de cage (sol sous la gaine, mains courantes, portes), appartement jouable recalé | `immeuble.py`, `immeubles_hlm.py` | P0 (clés et `proj`) | R6 à R10, R12 à R14 |
| **P2 Bâtiments 2 et 3** | instances du même gabarit, lucarnes, appartement (1, 3, −1) et (1, 4, −1) | `immeubles_hlm.py`, `immeuble.py` | P1 | R6, R11, R12 |
| **P3 Cadre, terrain, voirie** | nouveau cadre, fond de prisme, montagnes, ciel (`build_map.C`), rubans, trottoirs, bordures, marquages, parkings, places, mini-giratoire, `ZONES_GAMEPLAY`, nouvelles sorties de zombies | `quartier.py`, `voirie.py`, `build_map.py` | P0 | R3, R11, R15, R19 |
| **P4 Maisons** | `maisons_donnees.py`, `maisons.json`, `maisons.py` (volumes, toits, ouvertures LOD proche et loin, genres particuliers, maison de référence, clôtures et haies) | `maisons_donnees.py`, `maisons.py` | P3 (cadre, routes pour l'orientation des portes) | R16 |
| **P5 École, Maison de Pays, végétation, mobilier, voitures** | §C.6 à C.11 | `maisons.py`, `vegetation.py`, `mobilier.py` | P3, P4 | R17, R18 |
| **P6 Finitions et options** | variante B3, piscines, jeu de l'école, circuit de tricycles, paraboles et climatiseurs sur les balcons, descentes d'eau en modèles, instances teintées (§B.7), levier 2 × 2 du terrain si besoin | tous | P1 à P5 | R20 à R22 |

### D.2 Budget de brushes et de fichiers

**Choix : cible ≈ 15 200 brushes, plafond dur 19 000** (la demande était < 20 000). La v0.2 en a 6 760. La compilation BSP et la lumière dépendent surtout des surfaces visibles et des lumières ; le point sensible est le **poids des `.map`** (≈ 0,76 Ko par brush, mesuré : `quartier.map` fait 3,26 Mo pour 4 311 brushes), d'où les prefabs de 2 200 brushes au plus (≈ 1,7 Mo).

| Poste | v0.2 | cible | plafond |
|---|---|---|---|
| Terrain (4 508 triangles au pas de 256) | 3 362 | 4 500 | 4 700 |
| Montagnes, plaine, clip | 80 | 100 | 150 |
| Chaussées | 584 | 1 500 | 1 800 |
| Trottoirs | 0 | 600 | 800 |
| Bordures | 70 | 650 | 900 |
| Marquages et places | 0 | 450 | 600 |
| Parkings, annexe, garages | 19 | 150 | 250 |
| Bâtiment 1 | 913 | 1 400 | 1 800 |
| Bâtiment 2 | 559 | 900 | 1 200 |
| Bâtiment 3 | 977 | 1 400 | 1 800 |
| Maisons et petits volumes (38 bâtiments, 10 en LOD proche) | 42 | 1 800 | 2 300 |
| Clôtures et haies | 0 | 500 | 700 |
| École | 0 | 350 | 450 |
| Maison de Pays | 0 | 120 | 150 |
| Végétation (brushes) | 138 | 500 | 700 |
| Mobilier | 16 | 250 | 400 |
| **Total** | **6 760** | **≈ 15 200** | **19 000** (somme des plafonds : 18 700) |

Autres compteurs : `misc_model` 245 → ≈ 600 (arbres ≈ 70, touffes 150, haies ≈ 100, voitures ≤ 40, bancs et bacs ≈ 30, etc.) ; sorties de zombies 12 → 18 ; lumières inchangées. **Ordre de coupe si le plafond est menacé** : (1) fusion 2 × 2 du terrain hors cœur (−1 300) ; (2) maisons de LOD proche rétrogradées en LOD loin, de la plus lointaine à la plus proche ; (3) bordures en un brush par 192 u ; (4) feuillus lointains supprimés ; (5) volets.

### D.3 Critères de réception (vérifiables)

`tools/controle_v03.py` regroupe les contrôles automatiques : `python tools\controle_v03.py` affiche un tableau R1 à R19 et sort avec le code 1 au premier échec. Les trois derniers critères sont manuels.

| # | Critère | Comment |
|---|---|---|
| R1 | `python tools\build_map.py` sort avec le code 0, sans « brushes invalides » ni « Entites dans un batiment » | commande |
| R2 | `python tools\materiaux.py --verifier` : **0 nom manquant** (79 clés, 29 modèles) | commande (nécessite `--index` une fois) |
| R3 | total de brushes ≤ 19 000 ; **aucun `.map` au-dessus de 1,9 Mo** ; les prefabs périmés (`quartier.map`) ont disparu de `game/` | bilan imprimé par `build_map.py` |
| R4 | `MAT` contient les 55 anciennes clés et exactement les 79 clés de §B.2 avec les noms exacts | test |
| R5 | **aucune face à `256 256`** dans les prefabs, hors matériaux d'outil (`sky`, `clip_player`, `trigger`, `caulk`, `volume`) | analyse des `.map` |
| R6 | B2 et B3 sont des **instances du gabarit de B1** : mêmes constantes ; mêmes largeurs (64) et allèges (48 à 124) de fenêtre ; même profondeur de niche ; nombre de halls = 2 / 3 ; 5 niveaux ; `ascenseur=None` | test sur les étiquettes de `Immeuble.tags` |
| R7 | **balcons continus** : pour chaque niveau de 1 à 4 et pour la terrasse du rez, l'union des intervalles `u` des brushes `balcon_dalle_*` couvre `[0, L]` sans trou, sur B1, B2 et B3 ; aucun brush `balcon_separatif_*` | test sur les étiquettes |
| R8 | **fenêtres** : aucune ouverture ne traverse une frontière de colonne ; aucun recouvrement en `u` entre deux ouvertures d'une même rangée ; toutes les fenêtres avant mesurent 64 ; toutes les colonnes de même type ont la même grille | test |
| R9 | **porte de hall centrée** sur l'escalier à ± 8 u (défaut F3) pour les 8 halls | test |
| R10 | **ascenseur** : 1 cabine, 5 portes (`script_int` 0 à 4, `script_vector` de module 72), 5 appels, 1 bouton, tous avec les mêmes `targetname` qu'en v0.2 ; cabine à `z` conforme (H = 144) | comparaison avec un instantané de v0.2 |
| R11 | **gameplay** : les origines `x y` des entités du modèle (spawns, atouts, Box, Pack-a-Punch, courant) sont **identiques** à la v0.2 (seul `z` suit le terrain) ; aucune entité dans une emprise ; ≥ 18 sorties de zombies | comparaison avec un instantané de v0.2 |
| R12 | **un seul appartement jouable par immeuble** : exactement une colonne creusée, la porte de palier est une ouverture réelle, les trois immeubles ont leurs `lumiere` et leur `sonde` | test |
| R13 | **toit** : `toit_croupe` valide pour les trois ; faîtage de B1 entre 895 et 925 u ; largeur de toit 696 / 600 / 624 ; 4 et 6 lucarnes en B2 et B3 | test |
| R14 | **z-fighting** : 0 paire coplanaire pour les familles corrigées (garde-corps et séparatifs, mains courantes et marches, joues de loggia et rive, plancher de cabine et sol de hall, vitre de pignon) ; vues `40_`, `41_`, `42_` sans bande magenta | `preview_png.py --zfight` + comptage |
| R15 | **routes au-dessus du terrain** : 2 000 points tirés sur les chaussées, `z_route ≥ z_terrain + 1` partout | test |
| R16 | **maisons** : `reference/maisons.json` contient les 38 bâtiments ; chaque maison de LOD proche a ≥ 1 porte et ≥ 2 fenêtres ; la maison de référence a son balcon, son muret et ses volets bleus | test sur les étiquettes |
| R17 | **végétation** : ≥ 150 arbres ; 33 ± 3 peupliers de 12 m ; aucun arbre dans une emprise, sur une route ou dans une zone de gameplay | test |
| R18 | **école et Maison de Pays** présentes : volumes dans leurs emprises BD TOPO, toit orange de l'école, aire de jeux | test |
| R19 | **ZONES_GAMEPLAY** : aucun mât, voiture, modèle ni brush de mobilier dans les zones de §C.2 | test |
| R20 | **Rendus** : `python tools\vues_standard.py --dossier _build\renders\apres --prefixe APRES`, puis inspection des vues de §D.4 selon leur grille | manuel |
| R21 | **Compilation** : `.\tools\sync.ps1 -Vers Jeu` puis `.\tools\compile.ps1` : BSP, éclairage et link sans erreur de brush ni fuite ; temps de compilation noté | manuel (orchestrateur) |
| R22 | **En jeu** : du spawn à l'appartement de B1 par le hall du milieu, ascenseur à chaque étage, regard sur les balcons (alpha : §B.5), tour des maisons ; confirmation dans Radiant du sens de `W H rot` (§B.4) | manuel (orchestrateur) |

### D.4 Vues de comparaison avant / après (R20)

À ajouter à `vues_standard.py` (les 26 existantes restent) :

| Vue | Cadrage | Ce qu'on doit voir |
|---|---|---|
| `50_bat1_est_v3` | élévation est, annexe masquée | 3 avant-corps saillants de 224, loggias en retrait, grille de fenêtres alignée, soubassement brun, panneaux bruns des halls |
| `51_bat1_ouest_v3` | élévation ouest, arbres masqués | **4 lignes de dalles continues** de bout en bout, teintes des garde-corps par niveau, terrasse, descentes d'eau |
| `52_bat1_halls` | gros plan du hall du milieu | porte centrée sur l'escalier, sas vitrés, auvent mince, fentes de palier |
| `53_bat1_toit` | vue en perspective depuis le sud-est, 40° | croupes aux deux bouts, faîtage unique, souches en deux rangées, verrières |
| `54_bat2_v3`, `55_bat3_v3` | halls au nord | même grammaire que `50_`, lucarnes |
| `56_appart_b1` | coupe de l'étage 4 de B1 | pièces, deux fenêtres avant de 64 sans recouvrement, baie arrière ouverte sur le balcon |
| `57_rue_maisons` | rue des Prés Dombet vers les maisons de l'est | toits variés (pignons, croupes, plat), deux familles de couleurs, murets et haies |
| `58_maison_ref` | maison 131540499 de face | balcon blanc, volets bleus, muret et grille, haie |
| `59_ecole` | vue aérienne oblique | volumes bas, toit orange, cour, aire de jeux |
| `60_vue_aerienne` | plan de dessus avec contours BD TOPO | tout le quartier, routes avec trottoirs, parkings marqués |
| `61_parking_haut` | depuis le spawn vers le bâtiment 1 | rond-point blanc, places, voitures à l'échelle, aucun obstacle sur le gameplay |

## E. Ce qu'on ne fait pas, risques et questions ouvertes

### E.1 Ce qu'on ne fait pas, et pourquoi

| Non | Pourquoi |
|---|---|
| Intérieurs détaillés des logements fermés, caves, chaufferie | un seul appartement jouable par immeuble (consigne) ; le budget irait aux intérieurs |
| Séparatifs, stores, jardinières, linge, tables sur les balcons | [VU] mais sans intérêt de jeu ; coût de brushes |
| Fenêtres d'escalier à l'arrière des cages | non vues [INCONNU] |
| Cadres de fenêtre en brushes (4 par fenêtre) | D15 : la texture `core_window_opaque` porte le cadre |
| Pictogrammes de panneaux routiers, boîtes aux lettres de rue, bouches d'incendie, jeux d'enfants en modèles, peupliers ou sapins en modèles | aucun modèle n'existe (vérifié) ; les silhouettes sont en brushes |
| Textures importées (photos de façade) | aucun pipeline d'import ; instances teintées en option seulement (§B.7) |
| Clôture périmétrique de l'école, parcelles exactes | aucune source |
| Reproduction de l'état 2026 (B2 démoli, chantier, B3 en démolition) | on garde l'état 2023 de B2, le plus lisible sur l'orthophoto (D4) |
| Mise à jour du relief | l'écart avec le LiDAR est de 0,12 ± 0,27 m |
| Bâtiments hors du cadre (x > 6656, y > 5888 …) | 61 bâtiments BD TOPO restent hors cadre ; hors périmètre jouable |
| Modification de `zm_seyssel.gsc`, des zones de gameplay, du NavMesh | consigne : gameplay intact ; le NavMesh sera calculé par `compile.ps1` |
| Aménagements non sourcés : bande claire et deux carrés bordés derrière B1, camions garés sur l'avenue, arrêt de bus | nature [INCONNU] ou hors cadre |
| Outils externes (Blender, éditeur de textures, plug-ins) | tout le quartier est généré en Python (bibliothèque standard) ; Pillow et numpy ne servent qu'aux aperçus. Le dossier `outils-reference` ne contient que des scripts GSC (`T7-Scripts`, `t7-source`) : utiles pour le gameplay des phases suivantes (portes payantes, easter egg), sans rapport avec la géométrie. Je n'en ai lu que l'arborescence. |

### E.2 Risques

1. **Rendu des matériaux** : rien n'a été éclairé ni compilé ; les teintes sont celles des images. Le test de §B.5 (alpha, verres, décalques) est le plus important : un garde-corps alpha mal découpé change l'aspect de tout l'arrière de B1.
2. **Sens de `W H rot`** : déduit des `.map` officiels, à confirmer dans Radiant (§B.4) avant de généraliser.
3. **Taille du monde** : 239 × 255 m, 15 000 brushes, 600 modèles. Compilation et NavMesh plus longs ; surveiller R21. Le levier 2 × 2 du terrain et la rétrogradation des maisons sont prêts (§D.2).
4. **Sommets des voitures** : 40 voitures de 26 675 sommets pèseraient 1 M de sommets ; la règle 26 + 14 les limite, et la berline lointaine n'en a que 328.
5. **Limite de coordonnées de Radiant** (|x|, |y| < 16 384 supposé) : coordonnées extrêmes du ciel 13 368.
6. **Dérive des sources** : B2 démoli, peupliers de 2021 contre 2026 ; chaque donnée porte sa date dans §A et §C.
7. **Conflits de fichiers entre implémenteurs** : réduits par §C.12 ; `quartier.py` et `immeuble.py` n'ont plus de lignes en commun.

### E.3 Questions à poser à l'utilisateur (avec la valeur retenue par défaut)

1. **Profondeur des immeubles** : fidèle au cadastre (552 / 456 / 480, les pièces de B2 sont étroites) ou élargie comme en v0.2 (×1,28, plus de place pour jouer) ? *Défaut : cadastre (D1).*
2. **Niveaux du bâtiment 3** : 5 (BD TOPO, 30 logements) ou 6 (LiDAR : égout 3 m plus haut que B2) ? *Défaut : 5.*
3. **Halls de B2 et B3** : copie exacte du B1 (4,5 m de large) ou largeur réelle (2,8 à 3,2 m, qui ne contient pas l'escalier jouable) ? *Défaut : copie.*
4. **Bâtiment 2** : le reconstruire alors qu'il est démoli depuis 2023-2025 ? *Défaut : oui.*
5. **Toit** : croupes à 22° (LiDAR, orthophoto) ou pignons droits (Street View) ? *Défaut : croupes.*
6. **Étendue** : accepter le cadre agrandi (école et Maison de Pays) avec ses ≈ 15 000 brushes et un temps de compilation plus long ? *Défaut : oui.*
7. **Photos** : peux-tu déposer dans `reference/photos/` (jamais publié) des vues d'angle de l'arrière du B1 (profondeur des balcons, retour au pignon), les halls 1 et 3, la façade sud du B3, et des maisons autres que celle de Street View ? Elles remplaceraient les [INCONNU] de §A.7 et §C.5.
8. **Appartements jouables** : déplacés au hall du milieu, colonne gauche (D7) : d'accord ? Le Mystery Box et les atouts ne sont pas concernés (ils sont sur le parking).
9. **Teintes** : la façade est de B1 est-elle plutôt beige crème ou blanc cassé (Street View à contre-jour) ? Les toits gris violacé te conviennent-ils (les tuiles brun foncé n'existent pas) ? Autorises-tu un GDT à nous dans les Mod Tools pour des teintes exactes (§B.7) ?
10. **Rez-de-chaussée est de B1** : fenêtres (Street View) ou garages (ta fiche d'origine) ? *Défaut : fenêtres, les garages sont dans l'annexe.*
11. **Peupliers** : 12 m (LiDAR et ombre) ou nettement plus hauts (Street View : « plus haut que l'égout ») ? *Défaut : 12 m.*
12. **Goudron du parking du haut** : le garder (gameplay) tout en y peignant le rond-point et les places réels ? *Défaut : oui (D13).*
13. **Variante B3** (garages blancs et soubassement ocre au rez nord) : la veux-tu ? *Défaut : non (phase 6).*

## Annexe 1. Où chaque demande est traitée

| Demande de l'utilisateur | Sections |
|---|---|
| Reproduire tout le quartier : routes, bâtiments, textures, alentours | C entier, B |
| Bâtiments 2 et 3 mal modélisés : prendre le 1 comme modèle et le dupliquer | A.1, A.11 |
| Améliorer le 1 : placement des fenêtres | A.4, A.5, A.10 |
| Arrière du 1 : vrais balcons complets, filants, mal faits | A.7 |
| Maisons voisines faites trop vite | C.5, C.8 |
| Textures plus réalistes | B.2 à B.5 |
| Installer les outils nécessaires | E.1 (aucun outil externe) ; B.8 (nouveaux scripts du dépôt) |

## Annexe 2. Instantanés à prendre avant de commencer (pour R10 et R11)

Avant toute modification, enregistrer dans `_build/` (ignoré par git) : la liste `targetname`, `script_int`, `script_vector` des entités `ascenseur_*` produites par `build_map.py`, et les origines `x y` des entités de `zm_seyssel.map` de classe `script_struct`, `zombie_spawner`, `zombie_*`, `trigger_*` du modèle. Les critères R10 et R11 comparent à ces fichiers.
