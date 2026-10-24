# zm_seyssel — journal

Une entrée par session, la plus récente en haut. Jamais réécrite : on ajoute.
Format : `## AAAA-MM-JJ — Prénom — titre`, puis ce qui a été fait, testé, et la suite.

## 2026-10-24 — Ryad — v0.3 : quartier réaliste, couloir jusqu'au Carrefour, premier test à 3

- **Installation** : BO3 réinstallé sur `D:\SteamLibrary`, Mod Tools réinstallés (24,9 Go) ;
  scripts d'origine BO3 décompilés (`t7-source`) et `Resxt/T7-Scripts` clonés en lecture seule
  dans `..\outils-reference\` (hors dépôt).
- **Recherche** (workflow multi-agents, arrêté après la conception car trop lent) : Street View,
  orthophoto et BD TOPO IGN, LiDAR, inventaire des matériaux des Mod Tools →
  `docs/references/*.md`, `docs/conception-v0.3.md` (cahier des charges, en partie suivi).
- **Immeubles** : un seul gabarit (celui du bâtiment 1) pour les trois, positions et halls relevés
  sur la BD TOPO ; avant-corps des halls, loggias en retrait, grille de fenêtres par logement,
  balcons arrière filants et continus, toit à quatre pans, lucarnes sur 2 et 3.
- **Matériaux** : `tools/materiaux.py` (62 noms vérifiés dans les GDT) et échelle de texture par
  matériau écrite dans les `.map` (avant : `256 256` partout).
- **Garages** : portes basculantes en retrait, cadres, seuils, pilastres, rive.
- **Couloir jusqu'au Carrefour Market** (choix de Ryad : échelle réelle) : chemin calculé sur les
  routes OSM (rue des Prés Dombet → rue François Doche → rue du Mont des Princes → route de
  Genève, 1,08 km). Terrain en quadtree (256 u dans le quartier, 512 dans le couloir, puis plus
  gros), altitudes IGN 10 m, horizon comprimé au-delà de 190 m (`monde.py`).
- **Routes refaites** après remarques de Ryad (doublons BD TOPO/OSM, trous, routes coupées) :
  réseau OSM unique, chaussées à sens unique fusionnées, dalles de carrefour, routes jusqu'à
  l'horizon, trottoirs OSM en double retirés. **Contrôle sur l'orthophoto** :
  `tools/ortho_jeu.py` + `tools/controle_ortho.py`.
- **Maisons** : BD TOPO (+ LiDAR dans le quartier), décomposition des emprises en L, plus aucune
  maison supprimée à tort ; celles traversées par une route sont écartées.
- **Sols** : parkings OSM avec places et voitures, cours lues sur la photo (`sols_donnees.py`),
  jardins fermés par des haies et murets d'après le cadastre, Rhône en eau.
- **Barrages** aux sorties (voitures, béton, sacs de sable, barbelés) et murs invisibles.
- **Zone de test** : mur de 13 armes, borne +10 000 points, Mule Kick, Deadshot, Stamin-Up en plus,
  courant allumé au départ.
- **Compilation** : plantages résolus — éclairage qui plantait quand Radiant était ouvert ;
  BSP `tris_mergeconcave` causé par des paves qui dépassaient du mur d'armes (géométrie
  simplifiée). Compilation complète ~13 min.
- **Testé** : publication Workshop « amis seulement », partie à trois : ça fonctionne.
- **Suite** : voir `DEVELOPPEMENT.md` (zones et portes en premier).

## 2026-10-22 — Ryad — v0.1 / v0.2 : premier relevé, map jouable

- Relevé du HLM des Prés Dombet (OSM, cadastre, photos personnelles non publiées), plan de
  gameplay de la zone 1 (`docs/gameplay/zone-01-hlm.md`).
- Blockout du quartier en prefab Radiant, puis génération Python complète (`tools/`) : terrain IGN,
  trois immeubles avec halls, escaliers, un appartement jouable chacun, ascenseur scripté.
- Compilation en ligne de commande (`compile.ps1`) : langue du jeu, `gdtdb` en anglais,
  lien `usermaps` ; sauvegarde automatique GitHub en fin de session (`fin-de-session.ps1`).
