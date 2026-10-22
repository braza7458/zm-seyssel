# zm_seyssel — map zombies Black Ops III

Map custom pour le mode Zombies de **Call of Duty: Black Ops III**, qui recrée la ville de **Seyssel (Haute-Savoie)**.
On commence par le quartier des **Prés Dombet** et son HLM, qui sert de zone de départ.

![Plan du site](docs/plans/site-pres-dombet.svg)

## Avancement

| # | Zone | État |
|---|---|---|
| 01 | [HLM des Prés Dombet](docs/batiments/01-hlm-pres-dombet.md) | Relevé fait — blockout à faire |
| 02 | Annexe à toit plat + parking | À faire |
| 03 | Avenue Borcier (peupliers) | À faire |
| 04 | École maternelle | À faire |
| 05 | Barre nord (Chemin de la Fontaine) | À faire |

## Ce qu'il faut

- Black Ops III sur Steam
- **Call of Duty: Black Ops III - Mod Tools** (gratuit, Steam > Bibliothèque > filtre « Outils »)
- Git et Python 3 (pour regénérer les plans)

## Organisation du dépôt

```
game/                       copie des sources de la map, même arborescence que le dossier du jeu
  map_source/zm/zm_seyssel.map
  map_source/_prefabs/zm_seyssel/
  usermaps/zm_seyssel/      scripts, zone_source, sons
docs/
  batiments/                une fiche par bâtiment (photos décrites, dimensions, ordre de construction)
  plans/                    plan de dessus et coordonnées en unités Radiant
reference/osm/              données OpenStreetMap du quartier
reference/photos/           tes photos perso (non publiées sur GitHub)
tools/
  sync.ps1                  copie dépôt <-> dossier du jeu
  osm_to_plan.py            regénère les plans à partir des données OSM
```

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

Le chemin du jeu par défaut est `D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III` ; sinon passe `-Bo3 "<chemin>"`.

## Échelle

1 unité BO3 = 1 pouce = 2,54 cm, donc 1 m ≈ 39,4 unités. Les emprises des bâtiments viennent du cadastre ; la hauteur d'étage est fixée à 128 unités pour que le jeu reste confortable.

## Crédits

- Emprises des bâtiments et routes : © contributeurs [OpenStreetMap](https://www.openstreetmap.org/copyright), licence ODbL (source cadastre DGFiP).
- Les images Google Maps / Street View servent seulement de référence visuelle et ne sont pas incluses dans ce dépôt.
