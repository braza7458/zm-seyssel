# Gameplay — zone 1 : le HLM des Prés Dombet

## Version jouable actuelle (v0.2, générée par `tools/build_map.py`)

Le contenu de la salle de test officielle est posé sur le **parking du haut**, face au bâtiment 1 (comme la photo prise depuis ce parking). Les trois immeubles ont leurs halls, escaliers et un appartement ouvert chacun ; l'ascenseur du bâtiment 1 fonctionne.

| Élément | Position (unités) |
|---|---|
| Spawn des joueurs | (2935, -12), bord est du parking du haut, face au bâtiment 1 |
| Quick Revive, Juggernog, Speed Cola, Double Tap | alignés vers x ≈ 2050, entre y 404 et 788 |
| Mystery Box | (2058, -398) |
| Pack-a-Punch | (2292, 924) |
| Interrupteur du courant | (2447, 941) |
| Fusil à pompe | (2456, -458) |
| Zombies (sortent du sol) | 3 sur le parking du haut + 12 répartis sur les pelouses du quartier |
| Zone de départ | tout le quartier, intérieurs compris |

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
