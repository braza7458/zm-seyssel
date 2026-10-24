# zm_seyssel — map zombies Black Ops III

Map custom pour le mode Zombies de **Call of Duty: Black Ops III**, qui recrée la ville de **Seyssel (Haute-Savoie)**.
On commence par le quartier des **Prés Dombet** et ses trois immeubles HLM.

![Aperçu du quartier](docs/plans/apercu-quartier.png)

## Avancement

État détaillé et chantiers : [`DEVELOPPEMENT.md`](DEVELOPPEMENT.md) · journal des sessions : [`DEVLOG.md`](DEVLOG.md) · règles pour Claude Code : [`CLAUDE.md`](CLAUDE.md).

| # | Zone | État |
|---|---|---|
| 01 | [Bâtiment 1 (HLM, 3 halls, R+4)](docs/batiments/01-hlm-pres-dombet.md) | Façades, 3 halls crème, escaliers, ascenseur scripté, 1 appartement jouable |
| 02 | Bâtiment 2 (démoli, état 2023 : 2 halls, R+4) | Copie du gabarit du bâtiment 1, lucarnes, 1 appartement jouable |
| 03 | Bâtiment 3 (3 halls, R+4) | Copie du gabarit du bâtiment 1, lucarnes, 1 appartement jouable |
| 04 | Terrain (relief IGN), parkings, annexe, garages, voirie (BD TOPO), trottoirs, marquages | Fait (v0.3) |
| 05 | Végétation d'après le LiDAR, voitures, mobilier | Fait (v0.3) |
| 06 | Textures réalistes (échelle par matériau, 59 matériaux vérifiés dans les GDT) | Fait (v0.3), à juger en jeu |
| 07 | École maternelle, Maison de Pays, maisons voisines (volumes, toits, fenêtres, volets, portes d'après IGN) | Fait (v0.3), à affiner |

## Ce qu'il faut

- Black Ops III sur Steam
- **Call of Duty: Black Ops III - Mod Tools** (gratuit, Steam > Bibliothèque > filtre « Outils »)
- Git et Python 3 (pour regénérer les plans)

## Organisation du dépôt

```
game/                       copie des sources de la map, même arborescence que le dossier du jeu
  map_source/zm/zm_seyssel.map                 map principale (gameplay, ascenseur, volumes, ciel)
  map_source/_prefabs/zm_seyssel/*.map         terrain, voirie, trottoirs, maisons, végétation, décor... un prefab par groupe (généré)
  map_source/_prefabs/zm_seyssel/batiment_*.map les trois immeubles (générés)
  usermaps/zm_seyssel/      scripts (dont l'ascenseur), zone_source, sons
docs/
  batiments/                une fiche par bâtiment (photos décrites, dimensions, ordre de construction)
  gameplay/                 parcours, portes, atouts, Mystery Box par zone
  plans/                    plan de dessus, aperçu 3D et coordonnées en unités Radiant
reference/osm/              données OpenStreetMap du quartier (+ bâtiment 2 et garages d'après l'historique 2018)
reference/ign/              relief IGN RGE ALTI (grille de 4 m), bâtiments et routes BD TOPO, arbres et toits LiDAR
reference/materiaux.json    inventaire des matériaux et modèles des Mod Tools
reference/photos/           tes photos perso (non publiées sur GitHub)
tools/
  build_map.py              génère toute la map (appelle quartier.py et immeuble.py)
  quartier.py               terrain, parkings, annexe, garages, végétation, décor, montagnes
  voirie.py                 routes (rubans BD TOPO), trottoirs, passages piétons, places de stationnement
  maisons.py                maisons, école, Maison de Pays d'après la BD TOPO et le LiDAR
  immeuble.py               gabarit des immeubles HLM : façades, halls, loggias, balcons filants, toit, escaliers, appartement, ascenseur
  geom.py                   toits (croupes, pignons, plats) et lucarnes
  monde.py                  zone jouable (quartier + couloir jusqu'au Carrefour), terrain en quadtree, horizon comprimé
  grille.py                 constantes du cadre et loi de compression de l'horizon
  corridor_donnees.py       télécharge altitudes IGN, bâtiments BD TOPO, parcelles, végétation du couloir
  sols.py                   cours et surfaces dures, parkings et places, jardins fermés (haies, murets)
  sols_donnees.py           lit la nature du sol sur l'orthophoto -> reference/ign/sols_couloir.json
  carrefour.py              Carrefour Market et sa station-service
  ortho_jeu.py              orthophoto IGN dans le repère du jeu ; controle_ortho.py y superpose la map générée
  materiaux.py              dictionnaire des matériaux, échelle des textures ; `python tools/materiaux.py` vérifie les noms dans les GDT
  geo.py                    projection en unités de jeu, relief IGN
  compile.ps1               compile (BSP, éclairage, link) et lance le jeu
  sync.ps1                  copie dépôt <-> dossier des Mod Tools
  preview_blockout.py       aperçu 3D / plans d'étage à partir des .map (SVG, lent)
  preview_png.py            rendu PNG rapide (z-buffer) des .map : vues de façade, plans, z-fighting
  vues_standard.py          26 cadrages fixes (façades, balcons, voisins, routes) pour comparer avant/après
  make_blockout.py          briques géométriques et écriture des .map
  osm_to_plan.py            plan de dessus et coordonnées (premier relevé)
```

Les rendus de `preview_png.py` vont dans `_build/renders/` (ignoré par git). L'audit de l'état v0.2 est dans [`docs/references/audit-v0.2.md`](docs/references/audit-v0.2.md).

## Ce qu'il y a dans la map

- **Trois immeubles** construits avec le même gabarit (celui du bâtiment 1) : halls en avant-corps à panneaux bruns, loggias en retrait, grille de fenêtres par logement, balcons filants et continus à l'arrière, toit à quatre pans, souches de cheminée. Les bâtiments 2 et 3 ont en plus des lucarnes. Détails et cotes : [`docs/conception-v0.3.md`](docs/conception-v0.3.md).
- **Halls** identiques : entrée vitrée avec auvent, boîtes aux lettres, escalier à deux volées, paliers ; sols et marches couleur crème, murs crème.
- **Ascenseur** dans le hall du milieu du bâtiment 1 : bouton dans la cabine (étage suivant) et bouton d'appel à chaque palier.
- **Un appartement jouable par immeuble** (entrée, cuisine, salle de bain, deux chambres, séjour avec balcon), éclairé, prêt à être meublé.
- **Couloir jusqu'au Carrefour** : la rue des Prés Dombet, la rue François Doche, la rue du Mont des Princes et la route de Genève, à l'échelle réelle (environ 1 km), avec leurs maisons (BD TOPO), parkings, jardins fermés, la station-service et le Carrefour Market. Les rues de côté sont barrées.
- **Horizon réel** : au-delà du cadre jouable, le terrain suit le relief IGN jusqu'au Grand Colombier ; les routes de sortie sont barrées (voitures, béton, sacs de sable, barbelés).
- **Terrain réel** (relief IGN) : le parking du haut est ~2,5 m au-dessus du parking qui longe le bâtiment 1.
- **Rendu** : ciel et soleil de jour, étalonnage neutre, éclairage calculé en qualité moyenne, sondes de reflets dans les halls et les appartements.

Les prefabs générés peuvent être ouverts dans Radiant, mais ils sont réécrits à chaque `build_map.py` : les ajouts faits à la main vont dans la map principale ou dans un prefab à part.

## Travailler sur la map

```powershell
# après avoir récupéré les dernières modifs
git pull
.\tools\sync.ps1 -Vers Jeu

# ... travailler dans Radiant, compiler avec le Launcher ...

# avant d'enregistrer ton travail
.\tools\sync.ps1 -Vers Depot
git add .
git commit -m "HLM : façade est"
git push
```

Avec Claude Code, ces étapes sont automatiques : à la fin de chaque réponse, `tools/fin-de-session.ps1` récupère la map depuis le jeu, puis fait le commit et le push s'il y a des changements. On peut aussi le lancer à la main.

Le dossier des Mod Tools par défaut est `D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130` ; sinon passe `-Bo3 "<chemin>"`.

## Fabriquer, compiler et jouer

```powershell
python tools/build_map.py        # (re)génère zm_seyssel.map et le prefab du quartier depuis le modèle zombies
.\tools\sync.ps1 -Vers Jeu       # copie vers le dossier des Mod Tools
.\tools\compile.ps1              # base des assets, BSP + navmesh, éclairage, link, puis lance le jeu
.\tools\compile.ps1 -Etapes Jouer   # relancer sans recompiler
```

Pièges réglés par `compile.ps1`, à connaître si tu passes par le Launcher :

- **Langue du jeu.** Un BO3 en français charge `fr_zm_seyssel.ff`. Si la map est liée en anglais, le jeu s'arrête avec `Could not find zone 'fr_zm_seyssel'`. Le script détecte la langue du jeu installé ; dans le Launcher, règle « Build Language » sur la langue de ton jeu.

- **Mod Tools dans un dossier à part.** Steam les a mis dans `Call of Duty Black Ops III 455130`, à côté du jeu. Le bouton « Run » du Launcher cherche `BlackOps3.exe` dans ce dossier et ne le trouve pas. Le script lance le jeu depuis son vrai dossier, où un lien `usermaps` pointe vers celui des Mod Tools.
- **Windows en français.** L'outil `gdtdb` lit les décimaux à la française (« 0,5 ») et plante sur les fichiers BO3 (« 0.5 »). Le script le lance en anglais, sans rien changer à Windows.
  Le compilateur de sons intégré au linker a le même défaut, et là aucun contournement n'est possible : tant que le symbole décimal de Windows est la virgule, le link signale `unable to load file 'sound/zone//zm_seyssel.all.alias.sz'`. La map compile et se lance quand même, mais sans sons personnalisés. Correctif : `Win + R` → `intl.cpl` → **Paramètres supplémentaires** → **Symbole décimal** = `.` (et **Symbole de groupement des chiffres** = espace).

## Échelle

1 unité BO3 = 1 pouce = 2,54 cm. Le quartier entier est agrandi de 25 % (`ECHELLE` dans `tools/geo.py`, 1 m réel ≈ 49 unités) : à l'échelle exacte, tout paraît petit en jeu, les maps officielles font pareil. Les immeubles sont en plus élargis (×1,6 au total en profondeur). Hauteur d'étage : 144 unités.

## Crédits

- Emprises des bâtiments et routes : © contributeurs [OpenStreetMap](https://www.openstreetmap.org/copyright), licence ODbL (source cadastre DGFiP).
- Les images Google Maps / Street View servent seulement de référence visuelle et ne sont pas incluses dans ce dépôt.
