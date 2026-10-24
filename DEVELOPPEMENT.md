# zm_seyssel — état du développement

Tableau de bord à tenir à jour en fin de session (le journal détaillé est dans `DEVLOG.md`).
Légende : ✅ à jour et testé en jeu · 🟡 fait mais à vérifier en jeu · ❌ à faire.
Dernière mise à jour : 2026-10-24 (v0.3, Ryad).

## État par partie

| Partie | État | Où | Remarques |
|---|---|---|---|
| Compilation complète (BSP, éclairage, link) | ✅ | `tools/compile.ps1` | ~13 min, 54 000 brushes ; Radiant fermé obligatoire |
| Lancement et partie à 3 (Workshop amis) | ✅ | Launcher > Publish | testé le 2026-10-24 : ça fonctionne |
| Zone de test (mur de 13 armes, borne à points, 7 atouts, Box, PaP, courant allumé) | ✅ | `quartier.zone_test`, `build_map.py`, `zm_seyssel.gsc` | **à retirer ou cacher avant une vraie version** |
| Immeubles 1, 2, 3 (même gabarit, loggias, balcons filants, lucarnes) | 🟡 | `immeuble.py` | positions IGN ; profondeur élargie ×1,28 pour le jeu |
| Ascenseur du bâtiment 1 | 🟡 | `zm_seyssel.gsc` | à retester depuis la v0.3 (halls décalés de 80 u) |
| Appartements jouables (un par immeuble) | 🟡 | `immeuble.appartement` | vides, à meubler |
| Routes, ronds-points, carrefours | 🟡 | `voirie.py` | réseau OSM unique, calé sur le satellite ; chaussées doubles fusionnées |
| Parkings et places, voitures | 🟡 | `sols.parkings` | parkings OSM ; quelques parkings non cartographiés manquent |
| Cours et sols durs (lus sur la photo) | 🟡 | `sols_donnees.py`, `sols.surfaces` | détection imparfaite (ombres prises pour du béton) |
| Jardins fermés (haies, murets, portillons) | 🟡 | `sols.jardins` | d'après le cadastre, seulement dans le couloir |
| Maisons, école, Maison de Pays | 🟡 | `maisons.py` | volumes, toits, fenêtres, volets ; pas d'intérieurs |
| Couloir jusqu'au Carrefour | 🟡 | `monde.py`, `spine.json` | ~1,1 km réel ; rues de côté barrées |
| Carrefour Market et station-service | 🟡 | `carrefour.py` | façade et marquise seulement, pas d'intérieur |
| Barrages (voitures, béton, sacs, barbelés) | 🟡 | `voirie.barrages` | aux sorties de la zone jouable |
| Murs invisibles de la zone jouable | 🟡 | `quartier.montagnes` | vérifier qu'on ne sort pas |
| Horizon réel (Grand Colombier, Rhône) | 🟡 | `monde.py`, `grille.py` | terre comprimée au-delà de 190 m ; l'horizon suit le joueur le long du couloir |
| Végétation (LiDAR, BD TOPO, OSM) | 🟡 | `quartier.vegetation*` | arbres en brushes (cônes) loin, modèles près |
| Textures (62 matériaux des Mod Tools) | 🟡 | `materiaux.py` | garde-corps ajourés (alpha) à juger ; `ALPHA_OK = False` sinon |
| Sons personnalisés | ❌ | — | ne compilent pas tant que le symbole décimal de Windows est la virgule |

## Chantiers à faire (par priorité)

1. **Zones et portes** : découper la map en zones (`zm_zonemgr`, `info_volume` nommés), portes
   payantes, et points d'apparition des zombies le long du couloir. Aujourd'hui tout est une seule
   zone de départ et les zombies ne sortent que dans le quartier : au Carrefour ils marchent 1 km.
2. **Fenêtres à barricader** (planches) aux entrées des halls et des appartements.
3. **Retester en jeu** les points 🟡 et noter ce qui ne va pas ici.
4. **Textures réalistes** : textures CC0 (ambientCG…) pour façades, enrobé, tuiles, portes de
   garage → GDT à nous dans les Mod Tools ; demander avant chaque téléchargement.
5. **Intérieurs** : meubler les appartements, intérieur du Carrefour, de la station.
6. **Performances** : réduire les brushes loin du couloir si les FPS sont bas (fusion des mailles,
   moins de haies lointaines) ; `_le_long` rend `build_map.py` lent (~3 min).
7. **Sons** : régler le symbole décimal de Windows (`intl.cpl` → `.`) puis recompiler.
8. **Gameplay** : position définitive de la Box, du Pack-a-Punch, atouts répartis dans la ville,
   easter egg ; retirer la zone de test.
9. Atouts sans prefab dans les Mod Tools (Widow's Wine, Electric Cherry) et machine à chewing-gums :
   à chercher dans des packs communautaires.

## Problèmes connus
- Le lancement direct `BlackOps3.exe +devmap zm_seyssel` se ferme parfois : passer par Steam
  (ou accepter la fenêtre Steam qui demande d'autoriser les arguments).
- `cod2map64` refuse les faces percées (assert `tris_mergeconcave`) : pas de paves qui
  dépassent d'un mur sur la même face (voir DEVLOG du 2026-10-24).
- Deux textures manquantes signalées par le BSP (`t7_zm_chalk_buy_hvk30`,
  `jun_art_wood_plywood_dark03`), venant des prefabs du Mod Tools : sans danger.
- Le dossier des Mod Tools garde d'anciens prefabs (`quartier.map`…) que `sync.ps1` ne supprime
  pas : inoffensif, ils ne sont plus référencés.
