# Gameplay — zone 1 : le HLM des Prés Dombet

## Version jouable actuelle (v0.1, générée par `tools/build_map.py`)

Le contenu de la salle de test officielle est posé sur le **parking, à l'est du HLM**. Le HLM reste un bloc plein pour l'instant.

| Élément | Position (unités) |
|---|---|
| Spawn des joueurs | autour de (1300, -900), face au HLM |
| Quick Revive, Juggernog, Speed Cola, Double Tap | alignés vers x ≈ 465, entre y -484 et -100 |
| Mystery Box | (471, -1286) |
| Pack-a-Punch | (705, 36) |
| Interrupteur du courant | (860, 53) |
| Fusil à pompe au mur | (869, -1346) |
| Zombies (sortent du sol) | (708, -324), (708, -1476), (324, -900) au pied du HLM |
| Zone de départ | tout le quartier entre x -1400 et 2600 |

## Plan cible

Proposition de départ, à ajuster en jouant. Les prix suivent ceux des maps officielles de BO3.

## Parcours du joueur

```
[Hall d'entrée + cage d'escalier]  <- SPAWN
        |  porte 750
        v
[Palier 1er étage + appartement ouvert]
        |  porte 1000                       |  escalier 1250
        v                                   v
[Parking + conteneurs]              [Étages 2 à 4 + toit]
        |  porte 1000
        v
[Garages de l'annexe]  ->  [Caves : courant]
        |  porte 1250
        v
[École maternelle]  (zone 2, plus tard)
```

## Pièces

| Pièce | Ce qu'on y trouve | Fenêtres / barricades |
|---|---|---|
| Hall d'entrée (RDC) | Spawn des 4 joueurs, boîtes aux lettres, **Quick Revive** | 2 (porte vitrée, fenêtre du local vélos) |
| Cage d'escalier | Arme murale de départ (500 pts) | 1 (fenêtre du palier) |
| Appartement du 1er | Deuxième arme murale, **première position de la Mystery Box** | 3 (fenêtres et balcon côté avenue Borcier) |
| Parking | Conteneurs à déchets comme couvertures, voitures | Zombies qui arrivent à découvert, sans barricade |
| Garages de l'annexe | **Juggernog**, établi | 2 (portes de garage) |
| Caves sous le HLM | **Interrupteur du courant** (chaufferie) | 1 (soupirail) |
| Étages 2 à 4 | Autres positions de la Box, **Speed Cola** au 4e | 2 par étage |
| Toit | Point de vue sur Seyssel et les montagnes, accès réservé à l'easter egg | — |

## Points d'apparition des zombies

- Pelouse et peupliers de l'avenue Borcier (côté ouest) : ils grimpent par les balcons.
- Parking et conteneurs (côté est).
- Caves : ils remontent par l'escalier une fois les caves ouvertes.

## À décider ensemble

- Le Pack-a-Punch : sur le toit du HLM, ou plus loin dans la ville (le pont sur le Rhône ?)
- Le nom des zones affiché en jeu (« Hall », « Parking des Prés Dombet »…)
- La musique et l'ambiance : jour, nuit ou brouillard sur le Rhône
