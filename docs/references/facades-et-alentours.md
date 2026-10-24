# Références visuelles : façades et alentours (Prés Dombet, Seyssel)

Relevé fait le 24 octobre 2026 sur des images Google Street View (prises de vue d'avril 2026), aucune image n'est copiée dans le dépôt. Ce document sert de cahier des charges visuel pour `tools/immeuble.py` et `tools/quartier.py`.

Étiquettes utilisées pour chaque affirmation :

- **[VU]** : visible directement sur une image, mesure comprise dans la tolérance indiquée.
- **[DÉDUIT]** : calcul (perspective, cadastre OSM, comparaison) ou interprétation d'un détail partiel. Peut être faux.
- **[INCONNU]** : non visible ou non vérifié. Ne pas inventer, choisir librement ou aller voir sur place.

Repère de jeu rappelé : 1 m réel ≈ 49 unités BO3 (ECHELLE 1,25). Axe Y du bâtiment 1 = azimut 337° (nord-nord-ouest), axe X = azimut 67° (est-nord-est). Façade des halls de B1 = côté +X (est-nord-est), façade arrière = côté -X (ouest-sud-ouest, avenue Borcier).

## 0. Sources, méthode, fiabilité

Aucune photo n'était présente dans `reference/photos/` (dossier vide) : tout vient du web.

| Code | Panoramique Street View (identifiant) | Position | Ce qu'il montre | Lien |
|---|---|---|---|---|
| SV-A | `8qJlhxGs_FMaRZ_I5U2AJw` | 45,95642 N 5,83686 E, avenue Borcier (D992), ~40 m à l'ouest de B1 | façade arrière (ouest) de B1, peupliers, Maison de Pays | [lien](https://www.google.com/maps/@45.9564249,5.8368595,3a,75y,85h,90t/data=!3m6!1e1!3m4!1s8qJlhxGs_FMaRZ_I5U2AJw!2e0!7i16384!8i8192) |
| SV-B | `N9fPpQc2X62yqCOe0blmsA` | 45,95713 N 5,83657 E, avenue Borcier | l'emplacement de B2 vu de l'ouest ; date lue : « avr. 2026 » | [lien](https://www.google.com/maps/@45.957134,5.8365663,3a,75y,100h,90t/data=!3m6!1e1!3m4!1sN9fPpQc2X62yqCOe0blmsA!2e0!7i16384!8i8192) |
| SV-C | `-3EUsTFBuyOQ5s3amYPFkQ` | 45,95682 N 5,83811 E, rue des Prés Dombet | façade des halls (est) de B1, annexe, conteneurs, maison voisine, rue | [lien](https://www.google.com/maps/@45.9568209,5.8381117,3a,75y,240h,90t/data=!3m6!1e1!3m4!1s-3EUsTFBuyOQ5s3amYPFkQ!2e0!7i16384!8i8192) |
| SV-D | `rB01wvPPH9Jke17tEV6Maw` | 45,95691 N 5,83817 E, 5 rue des Prés Dombet | vers l'ouest : emplacement de B2, voitures, local technique | [lien](https://www.google.com/maps/@45.9569081,5.8381671,3a,75y,285h,90t/data=!3m6!1e1!3m4!1srB01wvPPH9Jke17tEV6Maw!2e0!7i16384!8i8192) |
| SV-E | `IfVRLp39yrgV6aFei4iPDA` | 45,95765 N 5,83760 E, 13 chemin de la Fontaine | façade nord (halls) de B3 | [lien](https://www.google.com/maps/@45.9576529,5.8376005,3a,75y,180h,90t/data=!3m6!1e1!3m4!1sIfVRLp39yrgV6aFei4iPDA!2e0!7i16384!8i8192) |

Méthode : le visualiseur Street View interactif n'affichait rien dans le navigateur intégré ; les vues ont donc été reconstruites à partir des tuiles d'image du panoramique (domaine `streetviewpixels-pa.googleapis.com`), reprojetées en perspective normale (champ 26° à 90°). Le cap de chaque panoramique a été recalé par corrélation avec les vignettes officielles de Google (précision de cap estimée ±3 à 5°). Les distances viennent des coordonnées des panoramiques et du cadastre OSM.

Précision des cotes : hauteur d'étage obtenue indépendamment sur deux vues (2,64 m à l'est, 2,73 m à l'ouest). Les largeurs mesurées sur images ont une incertitude de l'ordre de ±10 à 15 %. Les profondeurs (balcons, loggias) ne se mesurent pas de face : elles sont marquées [DÉDUIT] ou [INCONNU].

Couleurs : valeurs RGB données à titre indicatif. Les captures de la façade est sont à contre-jour et en ombre portée ; les moyennes brutes mesurées sont plus sombres que la teinte réelle au soleil. Les valeurs « proposées » sont corrigées à l'œil et sont [DÉDUIT].

Autres sources (texte) : avis d'appel d'offres de démolition à Seyssel, voir section 2.

## 1. Constat qui change le brief : B2 n'existe plus, B3 est en démolition

- **B2** (OSM way 131537277, barre de ~39 × 9 m au nord de B1, entrées au nord) : à son emplacement, les panoramiques d'avril 2026 montrent un terrain nu, des tas de gravier, une clôture de chantier, des conifères et un petit local technique beige. [VU] SV-B (cap 100°), SV-D (cap 285°). Il n'y a plus de bâtiment. Le fichier `reference/osm/batiment2_2018.json` est un état OSM ancien de ce bâtiment ; B2 est donc réputé démoli. [DÉDUIT]
- **B3** (OSM way 131537354, chemin de la Fontaine) : toujours debout sur SV-E. [VU] Un appel d'offres de la SA d'HLM Le Mont Blanc (publié le 19/09/2026, offres jusqu'au 05/10/2026) porte sur la « démolition d'un bâtiment de 30 logements et 2 garages » au « 4 chemin de la Fontaine », 74910 Seyssel. Le texte ne nomme ni Prés Dombet ni B3. [VU : le texte de l'avis] Le rapprochement avec B3 est [DÉDUIT] : 3 halls × 5 niveaux × 2 logements = 30 logements, et B3 est la barre du chemin de la Fontaine. Source : [avis marchesonline](https://www.marchesonline.com/appels-offres/avis/travaux-relatifs-a-la-demolition-d-un-batiment-de-30/ao-4327245-1) (page lue, détail du marché réservé aux abonnés).
- Un second avis, vu seulement comme résumé de recherche (page non confirmée à la lecture), évoque le désamiantage avant démolition de « 16 logements et un bloc de 8 garages » sur l'opération « Le Clos de la Fontaine » (4/6 chemin de la Fontaine). Cela concorde avec B2 + le bloc de garages OSM 131539162 (27 × 6 m). [INCONNU] : lien non confirmé. Source : [avis](https://www.marchesonline.com/appels-offres/attribution/travaux-de-desamiantage-deplombage-et-demolition-en/am-9585168-1) (la page lue ne contenait pas ce texte).
- Conséquence : la demande de l'utilisateur (dupliquer B1 à la place de B2 et B3) reste valable pour le jeu, mais **la réalité de B2 et B3 n'est plus un modèle d'architecture fiable** : on ne peut pas dire qu'ils sont « identiques au 1 » (voir section 4). B1 (rue des Prés Dombet) est, lui, bien debout en avril 2026. [VU] SV-A, SV-C.

## 2. Bâtiment 1 (HLM rue des Prés Dombet, OSM way 131537388)

### 2.1 Volume général

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Niveaux | RDC + 4 étages (5 niveaux) | [VU] | SV-A, SV-C |
| Hauteur d'étage | 2,6 à 2,75 m (retenir 2,7) | [VU] ±0,15 m | SV-A, SV-C |
| Hauteur à l'égout | ≈ 13,5 m (5 × 2,7) | [DÉDUIT] | idem |
| Longueur | 59,6 m (Y de -30,1 à +29,5) | [DÉDUIT] cadastre | `tools/geo.py` |
| Mur ouest | droit, X = -6,4 m, sans retrait | [DÉDUIT] cadastre | idem |
| Mur est principal | X = +3,7 à +4,8 m avec retraits et avant-corps (voir 2.3) | [DÉDUIT] cadastre | idem |
| Profondeur du corps | ≈ 10 à 11 m (hors avant-corps) ; 12,8 m hors tout | [DÉDUIT] cadastre | idem |
| Les deux bouts | les derniers 4 à 5 m de la façade est, à chaque extrémité, sont des murs pleins sans fenêtre ; les pignons eux-mêmes n'ont pas été vus de face [INCONNU] | [VU] pour les murs pleins | SV-C (cap 208° et 248°) |
| Teinte générale | crépi clair neutre côté est, plus blanc côté ouest | [VU] | SV-A, SV-C |

### 2.2 Toit

| Élément | Valeur | Statut |
|---|---|---|
| Forme | deux pans, faîtage parallèle à l'axe Y, pignons droits (pas de croupe) | [VU] SV-C |
| Pente | ≈ 25° (fourchette 22 à 28°) | [DÉDUIT] par calcul de perspective sur la bande de tuiles vue depuis SV-C. Plus faible que les 30° de la fiche `01-hlm-pres-dombet.md`. |
| Matériau | tuiles mécaniques, brun-gris foncé, sans motif marqué | [VU] |
| Débord | profond (≈ 0,8 à 1,0 m) sur les grands côtés ; ≈ 0,5 à 0,6 m sur les pignons | [DÉDUIT] |
| Bandeau de rive (fascia) | brun très foncé, épais (≈ 0,4 à 0,5 m), sous-face sombre visible de dessous | [VU] SV-A (cap 52°) ; hauteur [DÉDUIT] |
| Souches de cheminée | une douzaine, groupées par 2 à 4, carrées gris clair avec chapeau ; ≈ 0,8 à 1,0 m de large, 1,2 à 1,5 m de haut hors toit | nombre et teinte [VU] SV-C ; cotes [DÉDUIT] |
| Au faîtage, côté arrière | deux souches espacées d'environ 16 m sur la partie visible ; antenne TV et paraboles sur le toit et en haut de façade | [VU] SV-A |
| Grands panneaux plats sombres sur le pan est | 2 à 3 rectangles noirs (≈ 4 à 5 m × 1,5 m) posés dans la pente, situés au-dessus des cages d'escalier | [VU] SV-C ; fonction (verrière ou désenfumage de cage) [DÉDUIT] |
| Ligne de gouttière arrière | descentes d'eau pluviale grises verticales, espacement ≈ 16 m, qui traversent les dalles de balcon | [VU] SV-A ; espacement [DÉDUIT] |

Le toit du bâtiment au rez-de-chaussée (annexe) est différent : voir 2.7.

### 2.3 Façade est (côté halls, parking) : composition réelle

Le cadastre OSM donne le plan de la façade (cotes dans le repère de jeu, en mètres réels). Les images confirment les modules ; ils sont donc [VU] en aspect et [DÉDUIT] en position.

Du sud (Y = -30) au nord (Y = +30) :

| Y (m) | X du mur (m) | Élément | Aspect observé | Statut |
|---|---|---|---|---|
| -30,3 à -25,3 | +4,7 | mur d'extrémité sud, aveugle | plein, sans fenêtre | [VU] SV-C (cap 208°) |
| -25,4 à -22,0 | +3,7 | loggia en retrait (~1 m), 3,4 m de large | fond sombre, garde-corps métal noir | [DÉDUIT] cadastre + [VU] aspect |
| -22,0 à -17,6 | +6,4 | **cage d'escalier n°1** : avant-corps 4,4 m de large, saillie ≈ 1,7 m | colonne de panneaux horizontaux beige-brun (type persiennes) avec fente vitrée étroite par palier | [VU] + [DÉDUIT] |
| -17,6 à -13,9 | +3,9 | loggia en retrait (~2,5 m derrière l'avant-corps), 3,7 m de large | idem | idem |
| -13,9 à -3,5 | +4,7 | pan de mur à fenêtres, 10,4 m | par étage : paire de fenêtres | [VU] aspect |
| -3,5 à +0,9 | +6,2 | **cage n°2** (4,4 m) | idem cage 1 | idem |
| +0,9 à +12,8 | +4,6 | pan de mur à fenêtres, 11,9 m | paires de fenêtres, une loggia plate possible [INCONNU] | [VU] partiel |
| +12,8 à +16,3 | +3,7 à 3,8 | loggia en retrait, 3,5 m | idem | [DÉDUIT] + [VU] |
| +16,3 à +21,1 | +6,3 | **cage n°3** (4,8 m), dont le hall a été vu de près | idem + porte vitrée au RDC | [VU] SV-C (cap 248°) |
| +21,2 à +25,1 | +3,6 | loggia en retrait, 3,9 m | idem | [VU] |
| +25,1 à +29,5 | +4,8 | mur d'extrémité nord, aveugle, 4,4 m | plein, sans fenêtre | [VU] SV-C (cap 248°) |

Écart entre cages : 18,5 m et 20,0 m. Il y a donc **3 cages / 3 halls** sur la façade est, avec une répétition d'environ 19 m. Les trois avant-corps ressortent de 1,5 à 2,7 m par rapport au mur voisin. [DÉDUIT]

Détails d'un module (vus sur SV-C, cap 248°, champ 26°, échelle ≈ 3,4 cm par pixel) :

| Élément | Valeur | Statut |
|---|---|---|
| Fenêtres du pan de mur | par paire ; 1,2 à 1,3 m de large × 1,4 à 1,5 m de haut ; l'une avec volet roulant blanc, l'autre sans | [VU] ±15 % |
| Allège (hauteur d'appui) | ≈ 0,9 m (appui au tiers du niveau) | [DÉDUIT] |
| Loggias | fond vitré sombre, garde-corps métal noir à lisses horizontales, hauteur ≈ 1,0 m, au milieu de la hauteur d'étage | [VU] ; hauteur [DÉDUIT] |
| Panneaux des cages | bandes beige-brun (tan) horizontales, une fente vitrée étroite (≈ 0,2 m de haut, ≈ 2 m de long) par palier, légère teinte verte du vitrage vue sur le sud | [VU] SV-C (cap 208°) ; cotes [DÉDUIT] |
| Pilastres entre colonnes | plus clairs que le mur, ≈ 0,6 m de large | [VU] |
| Nombre de fenêtres par logement | non déterminé : le RDC est un niveau habitable normal côté est (mêmes fenêtres qu'aux étages), pas de garages vus de ce côté | [VU] pour le RDC ; [INCONNU] pour le nombre de logements par palier |
| Descentes d'eau | grises, verticales, à l'angle entre avant-corps et loggia | [VU] |

### 2.4 Entrée des halls (RDC de la cage)

Seule l'entrée de la cage n°3 (Y de +16,3 à +21,1) a été vue de près (SV-C, cap 248°).

| Élément | Valeur | Statut |
|---|---|---|
| Porte | double porte vitrée avec châssis métal sombre et vitrages fixes de chaque côté ; largeur totale ≈ 4,0 m, hauteur ≈ 2,6 m | [VU] ±15 % |
| Auvent | mince dalle plate grise juste au-dessus de la porte, saillie faible (≈ 0,5 m), sans pilier | [VU] ; saillie [DÉDUIT] |
| Perron | quelques marches basses et rampe/garde-corps métal ; trottoir de béton lisse | [VU] aspect |
| Soubassement | bande brun-mauve foncé, ≈ 1,0 à 1,3 m de haut, plus lisse que le crépi | [VU] teinte ; hauteur [DÉDUIT] |
| Entrées des cages 1 et 2 | [INCONNU] (masquées par l'annexe, les conteneurs et un arbre) ; l'organisation est supposée identique | [DÉDUIT] |

### 2.5 Façade ouest (arrière, côté avenue Borcier) : les balcons filants

C'est la partie la mieux documentée : SV-A, caps 52°, 62°, 84°, tailles de champ 30°, 50°, 46°, échelle ≈ 2,4 cm par pixel.

**Structure d'ensemble** [VU] :

- Quatre niveaux d'étage portent chacun une **dalle de balcon continue** sur toute la longueur visible (au moins 19 m d'un seul tenant sur la vue la plus nette, et 25 m environ sur l'aperçu large), sans interruption, sans retour de refend et sans cloison séparative visible entre appartements. La longueur totale (59,6 m) n'est visible nulle part en entier à cause des peupliers et de la haie.
- Le rez-de-chaussée a une **terrasse** continue à la place d'un balcon, à ≈ 0,5 à 1,0 m au-dessus de la pelouse [DÉDUIT], avec un petit soubassement brun en dessous.
- Épaisseur de la dalle (tranche visible) : ≈ 0,20 à 0,25 m, gris béton clair avec ombre portée dessous. [VU] ; cote [DÉDUIT].
- Profondeur des balcons : non mesurable de face. [INCONNU]. Hypothèse de travail 1,2 à 1,5 m, à valider avec une vue d'angle ou sur place.
- Hauteur du garde-corps : 1,0 à 1,1 m au-dessus de la dalle (≈ 1,45 m semble mesuré au niveau 3, mais le point haut est mal défini sur l'image). [DÉDUIT]
- Les dalles passent devant les descentes d'eau pluviale, qui les traversent tous les ≈ 16 m. [VU]
- Devant les cages d'escalier : [INCONNU] (le tronçon est caché ou n'a pas été identifié).
- Extrémités (retour de la dalle et du garde-corps sur le pignon) : [INCONNU]. Du côté nord, les dalles des étages 3 et 4 semblent s'arrêter au nu du mur d'extrémité, mais l'effet de perspective empêche de conclure.

**Garde-corps par niveau** (de haut en bas, vus depuis SV-A) [VU] :

| Niveau | Aspect du garde-corps | Statut |
|---|---|---|
| Étage 4 (haut) | blanc/gris très clair, barreaudage fin vertical ou grille, parties pleines ponctuelles ; plus loin vers le sud (derrière un peuplier), garde-corps plus sombre à barreaudage | [VU] |
| Étage 3 | blanc/gris clair, barreaudage vertical fin | [VU] |
| Étage 2 | noir ou gris très sombre, barreaudage vertical fin, plus dense | [VU] |
| Étage 1 | gris-bleu sombre avec barreaudage et brise-vue gris sur la gauche, panneau plein noir sur la droite (changement net à une descente d'eau) | [VU] |
| RDC | vert sarcelle (teal), barreaudage, avec tissus ou brise-vue sombres | [VU] |

Le style change donc selon le tronçon et le niveau, sans logique régulière apparente : probable changement par copropriétaire ou rénovation partielle. [DÉDUIT]. Pour la map, la solution simple est une rangée de garde-corps à barreaudage fin dont la teinte varie par niveau (clair en haut, sombre en bas, vert au RDC).

**Baies et fenêtres derrière les balcons** [VU], échelle ≈ 2,4 cm par pixel :

| Élément | Valeur | Statut |
|---|---|---|
| Grande baie de séjour | double battant ou coulissant, ≈ 2,0 à 2,4 m de large, avec volet roulant blanc visible (volet baissé sur beaucoup de fenêtres) | [VU] ±15 % |
| Porte-fenêtre étroite | ≈ 0,9 m de large, souvent juxtaposée à une fenêtre | [VU] |
| Fenêtre plus petite | ≈ 1,0 à 1,2 m, parfois avec persienne blanche | [VU] |
| Nombre exact par logement | non déterminé ; la distribution est irrégulière d'un tronçon à l'autre | [INCONNU] |
| Menuiseries | blanc ou gris clair ; volets roulants blanc cassé | [VU] |

**Accessoires** [VU] : tables et chaises, jardinières, étendage, un store banne bleu replié au niveau 1, climatisation et paraboles. Ils ne sont pas nécessaires pour le jeu.

### 2.6 Soubassement, sol et abords immédiats

- Soubassement côté est : brun-mauve foncé, lisse, ≈ 1 m. [VU] ; hauteur [DÉDUIT].
- Soubassement côté ouest : bande brun-roux en bas de la terrasse du RDC, ≈ 0,5 m visible. [VU] ; hauteur [DÉDUIT].
- Pelouse tondue entre le bâtiment et l'avenue Borcier, pas de chemin dallé visible à l'arrière. [VU] SV-A
- Côté est : trottoir de béton lisse le long de la façade, puis pelouse avec arbustes, puis parking en enrobé et conteneurs. [VU] SV-C

### 2.7 Annexe basse (OSM way 131540438, ≈ 21 × 12,5 m) et conteneurs

| Élément | Valeur | Statut |
|---|---|---|
| Volume | bas, hauteur ≈ 3,0 m, devant la façade est de B1 | [VU] ; hauteur [DÉDUIT] |
| Toit | plat, en gravillon gris clair, avec un relevé (acrotère) en béton clair d'≈ 0,4 à 0,5 m | [VU] SV-C |
| Murs | crépi gris sombre/vert-gris, rugueux | [VU] |
| Passage | un accès cintré ou rectangulaire sombre vers un passage/garage à côté d'une voiture garée | [VU] ; nature [INCONNU] |
| Conteneurs | deux grands bacs gris clair à base sombre (conteneurs semi-enterrés), ≈ 2,5 m de large et ≈ 2 m de haut hors sol, côté pelouse | [VU] ; cotes [DÉDUIT] à ±30 % |

## 3. Les alentours immédiats de B1

### 3.1 Rue des Prés Dombet, trottoirs, marquages

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Chaussée | enrobé gris moyen, usé, rapiécé ; pas de ligne axiale ; largeur ≈ 5,5 à 6,5 m | aspect [VU] ; largeur [DÉDUIT] | SV-C |
| Trottoir | côté maison : ≈ 1,5 à 2 m, béton/enrobé clair, bordure béton gris clair arrondie ≈ 15 cm | [VU] ; cotes [DÉDUIT] | SV-C (cap 105° et 165°) |
| Passage piéton | 4 bandes blanches à l'entrée du carrefour | [VU] | SV-C (cap 222°) |
| Cercle blanc peint au sol | ≈ 6 m de diamètre (mini-giratoire ou aire de retournement) | [VU] ; diamètre [DÉDUIT] | SV-C (cap 165°) |
| Panneaux | « cédez le passage » avec panonceau, triangle « enfants/passage piéton » près du parking | [VU] | SV-C |
| Éclairage | mât acier galvanisé gris, ≈ 5 à 6 m, une crosse | [VU] ; hauteur [DÉDUIT] | SV-C |
| Voitures | citadines, monospace gris-bleu, break argent, utilitaire blanc, berline gris foncé : modèles courants des années 2000-2020 | [VU] | SV-C, SV-D |
| Parking | enrobé gris avec bandes blanches (marquage perpendiculaire à la façade), places en épi non visibles | [VU] | SV-C |

### 3.2 Avenue Borcier (côté ouest de B1)

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Chaussée | enrobé gris, deux voies, pas de marquage visible sur les vues utilisées | [VU] | SV-A, SV-B |
| Trottoir | ≈ 2 m, enrobé gris, bordure béton gris continue | [VU] ; largeur [DÉDUIT] | SV-A |
| Haie | thuyas/charmille taillée, ≈ 1,2 à 1,5 m, continue le long du trottoir | [VU] ; hauteur [DÉDUIT] | SV-A |
| Peupliers | peupliers d'Italie en alignement (une dizaine visibles sur le panorama large), espacement ≈ 8 à 12 m, hauteur supérieure à l'égout du toit (≥ 18 m), feuillage jeune vert vif | [VU] ; cotes [DÉDUIT] | SV-A |
| Lampadaires | mât gris clair, ≈ 6 m | [VU] | SV-A (panorama large) |
| Arrière-plan | collines boisées du Jura, brunes/vert sombre | [VU] | tous |

## 4. Bâtiments 2 et 3 : sont-ils identiques au 1 ?

**Non, ni dans la réalité, ni sur le plan.**

| Point | B1 | B2 (cadastre ancien) | B3 | Source |
|---|---|---|---|---|
| Orientation | grand axe NNO-SSE (337°) | grand axe ENE-OSO (67°), perpendiculaire à B1 | idem B2 | cadastre |
| Longueur × profondeur | ≈ 59,6 × 10-11 m | ≈ 38,8 × 9,1 m | ≈ 59,1 × 9,4 m (11,9 m avec les porches) | cadastre [DÉDUIT] |
| Façade des entrées | est (ENE) | côté +Y, nord-nord-ouest (2 porches saillants de 3,1 m × 1,5 m, centres à X = -4,0 et +15,4 m) | côté +Y, nord-nord-ouest (3 porches saillants de 3,3 m × 1,8 m, centres à X = 45,8, 65,1, 84,5 m, soit un écart de 19,3 m) | cadastre [DÉDUIT] |
| Nombre de halls | 3 | 2 | 3 | cadastre [DÉDUIT] |
| Existence en 2026 | oui | non (terrain nu) | oui, démolition annoncée | SV-B, SV-D, SV-E, avis |

**B3, façade nord (halls)** (SV-E, caps 162° et 190°) [VU] sauf mention :

- Même gabarit : R+4, toit à deux pans brun foncé avec débord sombre, souches de cheminée, mur d'extrémité plein (pignon). 
- Teinte : crépi crème clair (plus clair et plus chaud que B1). Le RDC a un **soubassement ocre/saumon** d'≈ 1,2 m de haut et des **portes de garage sectionnelles blanches** (≈ 2,4 m de large, 3 vues) entre les halls, alors que B1 a des fenêtres au RDC côté est.
- Cages d'escalier : deux colonnes de fenêtres étroites et hautes (≈ 0,4 à 0,5 m de large) décalées d'un demi-niveau, et non les panneaux horizontaux de B1.
- Entrée de hall : porche plat avec un auvent mince et des marches à garde-corps métal. Deux halls vus sur SV-E, séparés d'environ 19 m, cohérents avec les porches du cadastre.
- Loggias : colonnes de loggias sombres empilées (4 niveaux) à proximité des cages, comme sur B1. Garde-corps non détaillés. [INCONNU]
- Façade sud (arrière, côté parking) de B3 : [INCONNU] (non photographiée).

**Recommandation pour le jeu** (demande de l'utilisateur) : copier B1, avec les cages et les loggias de B1, à l'emplacement et à l'orientation de B2 et B3 (entrées vers le nord pour B2 et B3). Pour B2, retenir **2 cages** (longueur 38,8 m, entre 2 halls) ; pour B3, **3 cages**. Ce choix est une décision de jeu : il ne reproduit pas les détails réels de B3 (garages, fenêtres d'escalier verticales, ocre). Si l'objectif est de rester fidèle à B3, ajouter seulement le soubassement ocre et les portes de garage sur le RDC nord.

## 5. Maisons voisines

Maisons OSM `building=house` autour du parking : 131540499 (14 × 14 m, face à SV-C), 131540899, 131540758, 131537776, 131537470, 131537735, 131539452. **Une seule a été vue de près** : 131540499. Les autres se voient seulement en silhouette (cap 165° depuis SV-C), peu détaillée. Ne pas généraliser sans vérification.

**Maison 131540499** (SV-C, cap 105°, champ 85°) :

| Élément | Valeur | Statut |
|---|---|---|
| Volume | maison individuelle des années 1970 : RDC (caché par la haie) + étage + combles, pignon tourné vers la rue | [VU] |
| Toit | deux pans, pente ≈ 30° (calculée sur le rampant du pignon), tuiles brun-rouge, grand débord ≈ 0,8 à 1,0 m avec **pannes et consoles en bois brun foncé visibles** (3 consoles par rampant) | [VU] ; pente [DÉDUIT] |
| Murs | crépi crème/sable, lisse à grain fin | [VU] |
| Pignon sur rue | balcon à garde-corps en fer forgé blanc (≈ 2,2 m de large, saillie ≈ 0,8 m), porte-fenêtre à deux volets **bleu franc**, en dessous une loggia ou baie avec garde-corps blanc | [VU] |
| Volets | bois, bleu franc (rail bleu visible aussi au RDC) | [VU] |
| Porte | brun-orangé, derrière la haie | [VU] |
| Clôture | muret béton gris ≈ 0,5 à 0,6 m surmonté d'une grille blanche ouvragée (hauteur totale ≈ 1,1 à 1,2 m), piliers en béton, boîte aux lettres blanche, portillon à grille blanche et panneau bleu | [VU] ; cotes [DÉDUIT] |
| Haie | mélange thuya/laurier/arbustes caducs, ≈ 1,8 à 2,2 m, sur le côté rue | [VU] ; hauteur [DÉDUIT] |
| Recul | environ 4 à 6 m derrière la clôture | [DÉDUIT] |

## 6. École maternelle et Maison de Pays

- **École maternelle** (OSM way 131537380, 30 × 58 m) : vue seulement de loin (≈ 90 m, SV-C cap 165°) : bâtiment bas, un seul niveau, murs blancs, grand toit brun foncé à pans. Le détail des façades, des préaux et de la cour n'a pas été relevé. [INCONNU]
- **Maison de Pays** (OSM way 131537365, salle des fêtes) : vue de loin depuis SV-A (cap 270°) : bâtiment bas, murs blancs, toits brun-rouge à pignons multiples, rives rouge-bordeaux, portes vertes à l'entrée ; devant, un pré avec buissons nus. [VU] aspect ; cotes [INCONNU].
- **Fond de paysage** : collines boisées du Jura, bruns et verts sombres, au sud-ouest et à l'ouest. [VU]

## 7. Couleurs (RGB approximatives)

« Mesuré » = moyenne brute de la capture (sous-exposée par ombre ou contre-jour). « Proposé » = valeur recommandée pour les textures, corrigée à l'œil. [DÉDUIT] dans tous les cas.

| Élément | Mesuré | Proposé | Teinte (VU) |
|---|---|---|---|
| Crépi B1 est | 129, 126, 125 | 200, 192, 178 | gris-beige clair neutre |
| Panneaux des cages B1 | 143, 128, 110 | 205, 180, 150 | tan/beige-brun chaud |
| Soubassement B1 est | non mesuré | 120, 95, 90 | brun-mauve foncé |
| Crépi B1 ouest | non mesuré proprement | 228, 225, 214 | blanc cassé, très légèrement jaune |
| Dalles de balcon | 69, 81, 75 (ombre) | 150, 150, 145 | gris béton |
| Garde-corps N4/N3 | non mesuré | 225, 225, 222 | blanc/gris très clair |
| Garde-corps N2 | non mesuré | 45, 45, 48 | noir/gris très foncé |
| Garde-corps N1 (droite) | 3, 18, 25 | 12, 20, 26 | noir bleuté |
| Garde-corps RDC | non mesuré | 40, 105, 100 | vert sarcelle |
| Tuiles B1 | 108, 103, 96 | 120, 105, 92 | brun-gris foncé |
| Fascia et sous-face du toit | 55, 56, 40 | 60, 45, 35 | brun très foncé |
| Souches de cheminée | non mesuré | 175, 172, 165 | gris clair |
| Gravillon de l'annexe | 151, 146, 136 | 170, 165, 155 | gris clair |
| B3 crépi nord | 130, 128, 121 (ombre) | 220, 210, 190 | crème clair |
| B3 soubassement | 113, 102, 79 (ombre) | 200, 150, 105 | ocre/saumon |
| Portes de garage B3 | non mesuré | 235, 235, 230 | blanc |
| Maison : crépi | 170, 162, 124 | 220, 210, 180 | crème/sable |
| Maison : tuiles | non mesuré | 140, 85, 65 | brun-rouge |
| Maison : volets | non mesuré | 30, 90, 200 | bleu franc |
| Maison : garde-corps et clôture | 206, 206, 195 | 235, 235, 228 | blanc |
| Asphalte | non mesuré | 95, 95, 98 | gris moyen |
| Bordures | non mesuré | 165, 165, 160 | gris clair |

## 8. Pistes de paramétrage pour le générateur (propositions, pas des relevés)

Tout ce qui suit est une proposition fondée sur les relevés ci-dessus. Les cotes marquées [INCONNU] y sont remplacées par un choix de travail.

| Paramètre | Proposition | Origine |
|---|---|---|
| Hauteur d'étage | 2,7 m (≈ 132 unités) | [VU] |
| Pente du toit | 25° | [DÉDUIT] |
| Débord de toit | 0,9 m (grands côtés), 0,55 m (pignons) | [DÉDUIT] |
| Fascia | 0,45 m de haut, brun très foncé | [DÉDUIT] |
| Balcon arrière | dalle 0,22 m d'épaisseur, 1,3 m de profondeur, garde-corps 1,05 m | épaisseur [DÉDUIT], profondeur [INCONNU], garde-corps [DÉDUIT] |
| Continuité des balcons | continus sur toute la longueur, sans cloison, 4 étages + terrasse au RDC | [VU] sur 19 à 25 m, extrapolé sur le reste |
| Avant-corps est | 3 cages à Y = -19,8 ; -1,3 ; +18,7 m (largeur 4,4 à 4,8 m, saillie 1,5 à 2,7 m) | [DÉDUIT] cadastre |
| Loggias est | en retrait de chaque côté des cages 1 et 3 (3,4 à 3,9 m de large) | [DÉDUIT] cadastre |
| Extrémités | pignons aveugles à l'est sur 4,4 m (nord) et 5,0 m (sud) | [DÉDUIT] cadastre + [VU] |
| RDC est | fenêtres comme aux étages, hall vitré à chaque cage | [VU] cage 3 ; cages 1 et 2 [DÉDUIT] |

## 9. Ce qu'il reste à vérifier

1. Longueur complète du balcon filant ouest et son passage devant les cages d'escalier (arbres et haie masquent l'essentiel) : une vue Street View prise plus au sud sur l'avenue Borcier serait utile, ou un relevé sur place.
2. Profondeur réelle des balcons et des loggias : nécessite une vue d'angle (depuis un pignon) ; non obtenue.
3. Pignon sud de B1 (côté ouest) : fenêtres éventuelles non vues.
4. Entrées des cages 1 et 2 de B1 (masquées).
5. Façade sud (arrière) de B3 et façade arrière réelle de l'ancien B2.
6. Maisons voisines autres que 131540499 ; école maternelle ; Maison de Pays : seulement de loin.
7. Date de prise de vue : lue pour SV-B (avril 2026) uniquement ; les autres panoramiques présentent la même végétation de début de printemps mais n'ont pas été vérifiés individuellement.
8. Le rapprochement de l'appel d'offres du 4 chemin de la Fontaine (30 logements) avec B3 reste une déduction.
