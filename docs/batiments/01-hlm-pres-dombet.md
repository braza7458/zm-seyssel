# Bâtiment 01 — HLM des Prés Dombet

Premier bâtiment de la map, point de départ (spawn) des joueurs.

- **Lieu** : rue des Prés Dombet, Seyssel (74), entre l'avenue Borcier (ouest) et le parking de l'école maternelle (est)
- **Cadastre / OSM** : [way 131537388](https://www.openstreetmap.org/way/131537388) (annexe : [way 131540438](https://www.openstreetmap.org/way/131540438))
- **Repères visuels** : Google Maps / Street View — ouvrir sur la rue des Prés Dombet, côté parking, et sur l'avenue Borcier pour la façade arrière

## Ce qu'on voit

| Élément | Description |
|---|---|
| Forme | Longue barre rectangulaire, orientée à peu près nord-nord-ouest / sud-sud-est |
| Niveaux | **R+4** : rez-de-chaussée (garages + entrées) et 4 étages d'habitation |
| Toit | Deux pans, tuiles brun foncé, débord de toit, une rangée de souches de cheminée sur le faîtage |
| Façade est (parking) | Enduit beige clair ; colonnes verticales de loggias séparées par des bandes de panneaux bruns horizontaux (type persiennes) ; pignons pleins aux deux bouts |
| Façade ouest (avenue Borcier) | Balcons filants sur toute la longueur à chaque étage, garde-corps métalliques |
| Rez-de-chaussée | Portes de garage, entrées d'immeuble avec petit auvent |
| Devant (est) | Annexe basse à **toit plat** (garages / caves), ~21 × 13 m, puis parking et conteneurs à déchets semi-enterrés |
| Derrière (ouest) | Pelouse, puis alignement de **peupliers** le long de l'avenue Borcier |
| Fond | Montagnes boisées (Grand Colombier / Jura) — à faire en skybox ou en décor lointain |

## Dimensions (mesurées sur le cadastre)

1 unité BO3 = 1 pouce = 2,54 cm, donc **1 m ≈ 39,4 unités**.

| Mesure | Réel | Unités BO3 |
|---|---|---|
| Longueur | ~60,6 m | **2384** (Y de -1192 à 1192) |
| Profondeur hors tout | ~12,8 m | **496** (X de -248 à 248) |
| Profondeur du corps principal | ~11 m | ~432 |
| Hauteur d'étage (réel ~2,75 m) | — | **128** conseillé (plus confortable en jeu) |
| Hauteur à l'égout du toit (5 niveaux × 128) | ~14 m | ~640 |
| Faîtage (toit à ~30°) | ~17 m | ~770 |
| Annexe toit plat | ~21 × 13 m, ~3 m de haut | 824 × 496, 128 de haut |

Les coordonnées exactes de chaque coin sont dans [../plans/coordonnees-radiant.md](../plans/coordonnees-radiant.md), et la vue de dessus dans [../plans/site-pres-dombet.svg](../plans/site-pres-dombet.svg).

## Ordre de construction dans Radiant

1. **Blockout (greybox)** : un brush de 2384 × 496 × 640 centré sur (0,0), avec la texture `caulk`. Vérifier en jeu que l'échelle « sonne juste ».
2. **Sol et terrain** : pelouse derrière, parking devant, l'annexe à toit plat.
3. **Coque** : murs extérieurs creusés, dalles d'étage tous les 128, cage d'escalier.
4. **Toit** : deux pans + cheminées.
5. **Façades** : loggias côté est, balcons filants côté ouest, garages au RDC.
6. **Intérieur jouable** : au moins une cage d'escalier et 1 ou 2 appartements ouverts (zone de départ).
7. **Gameplay** : spawns joueurs, spawners zombies, fenêtres à barricader, premier mur d'achat, porte payante vers l'extérieur.
