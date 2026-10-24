# zm_seyssel — instructions pour Claude

Map Zombies **Black Ops III** de Seyssel (Haute-Savoie) faite à trois (Ryad et deux potes).
Lu automatiquement quand une session s'ouvre dans ce dossier.

## Le projet
Le quartier des Prés Dombet (trois HLM, maisons, école) et la route réelle jusqu'au
**Carrefour Market** et sa station-service (≈ 1,1 km), à l'échelle du jeu, fidèle au plan
satellite IGN. Toute la map est **générée par du Python** (`tools/`), puis compilée par les
Mod Tools. Publiée sur le Workshop Steam en « amis seulement ».

## Au démarrage d'une session
1. `git pull` (on est trois sur le dépôt).
2. Lire `DEVELOPPEMENT.md` (état de chaque partie, chantiers) puis l'entrée la plus récente
   de `DEVLOG.md`.
3. Réponses courtes, en français.

## Règles fermes
- **Ne jamais modifier à la main** `game/map_source/` : tout est réécrit par
  `python tools/build_map.py`. On change le générateur (`tools/*.py`), pas le `.map`.
  Exceptions écrites à la main et jamais écrasées : `game/usermaps/zm_seyssel/scripts/zm/zm_seyssel.gsc`
  (ascenseur, zone de test), `.csc`, `zone_source/zm_seyssel.zone`.
- **Radiant doit être fermé pendant une compilation** (sinon l'éclairage plante et Radiant
  peut écraser la map dans le dossier des Mod Tools).
- Un matériau ou un modèle n'est utilisé que s'il existe dans les GDT des Mod Tools :
  `python tools/materiaux.py` doit répondre « 0 absents ».
- Toute modification de routes, bâtiments ou sols se **vérifie sur l'orthophoto IGN**
  (`tools/controle_ortho.py`) avant de dire que c'est fait.
- Téléchargement (textures, outils, données) : annoncer nom, source, taille et demander avant.
  Pas d'images Google Street View comme textures (droits) : textures CC0 seulement.
- Aucun fichier de plus de ~2 Mo écrit à la main dans le dépôt ; les fichiers compilés
  (`.ff`, `.xpak`, `.d3dbsp`) et `_build/` ne vont jamais sur GitHub.
- Avancer par étapes courtes et vérifiées (rendu ou compilation), pas de gros workflows
  multi-agents sans demande explicite.

## Chaîne de travail
```powershell
git pull
python tools\build_map.py            # génère toute la map (~3 min)
python tools\controle_ortho.py       # contrôle sur le satellite -> _build\ref\controle_map.png
.\tools\sync.ps1 -Vers Jeu           # copie vers les Mod Tools
.\tools\compile.ps1                  # gdtdb, BSP (~2 min), éclairage (~1,5 min), link (~9 min), lance le jeu
.\tools\compile.ps1 -Etapes Jouer    # relancer sans recompiler
```
- Mod Tools : `D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130`
  (chemin par défaut des scripts ; sinon `-Bo3` / `-Tools`).
- Aperçus sans le jeu : `python tools\preview_png.py` (rendu à plat, **pas** le rendu du moteur)
  et `python tools\vues_standard.py`. Pour un plan avec `--boite`, ajouter `--centre`
  (sinon les grandes mailles coupées par la boîte disparaissent et font de faux trous).
- Isoler un plantage de compilation : `$env:ZM_SANS="groupe1,groupe2"` puis
  `.\tools\essai_lumiere.ps1` (exclut des prefabs de la map principale).

## Données de référence (à régénérer seulement si besoin)
| Commande | Produit |
|---|---|
| `python tools\corridor_donnees.py relief batiments parcelles vegetation arbres` | altitudes IGN, bâtiments BD TOPO, cadastre, végétation, arbres OSM du couloir |
| `python tools\ortho_jeu.py` | orthophoto dans le repère du jeu (`_build\ref\ortho_jeu.png`) |
| `python tools\sols_donnees.py` | nature du sol lue sur la photo (`reference\ign\sols_couloir.json`) |
| `reference\osm\corridor.json` | routes, bâtiments, parkings OSM (requête Overpass, voir DEVLOG) |
| `reference\osm\spine.json` | chemin quartier → Carrefour (Dijkstra sur les routes OSM) |

Si le chemin (`spine.json`) change, relancer `corridor_donnees.py relief` : les sommets du
terrain changent et leurs altitudes doivent être téléchargées.

## Repères
- 1 unité = 1 pouce ; le monde est agrandi de 25 % (`ECHELLE` dans `geo.py`) : **1 m réel ≈ 49,2 u**.
  Étage des immeubles : `H = 144`.
- Origine au centre du bâtiment 1 ; `y` le long du bâtiment 1 (vers le nord-nord-ouest).
- Zone jouable : cadre du quartier (`grille.py`) + bande de ±3600 u autour de `spine.json`
  (`monde.WP`). Au-delà : décor visible jusqu'à `R0 = 9400` u, puis horizon comprimé.
- Spawn joueurs : parking du haut (≈ 2935, −12). Zone de test : mur d'armes au sud du parking,
  atouts à l'ouest, borne à points (2700, −560). Ne rien poser de solide dans
  `Quartier.ZONES_GAMEPLAY`.

## Fichiers du générateur
`build_map.py` (map principale, prefabs, entités) · `quartier.py` (terrain quadtree, annexe,
garages, végétation, décor, zone de test, murs invisibles) · `immeuble.py` (gabarit HLM) ·
`maisons.py` (maisons BD TOPO + LiDAR) · `voirie.py` (routes OSM, carrefours, barrages,
marquages) · `sols.py` (cours, parkings, jardins/haies) · `carrefour.py` (magasin, station) ·
`monde.py` (zone jouable, quadtree, relief) · `grille.py` · `geom.py` (toits) ·
`materiaux.py` (matériaux, échelles) · `geo.py` (projection).

## Fin de session
Nouvelle entrée en haut de `DEVLOG.md` (date, prénom, ce qui a été fait / testé / reste),
mise à jour de `DEVELOPPEMENT.md`, puis commit et push. Commit en français.
