"""Generateur d'immeubles HLM : coque, facades, halls, escaliers, appartement jouable, ascenseur.

Un seul gabarit (celui du batiment 1) sert aux trois immeubles. Repere local :
    u : le long de l'immeuble (0 -> longueur)
    v : de la facade principale (0) vers l'arriere (profondeur D) ; les halls
        sont des avant-corps en v negatif (de -SAILLIE a 0), les balcons de D a D + PROF_BALCON
    z : hauteur depuis le sol fini du rez-de-chaussee

Cotes en cotes absolues (voir docs/conception-v0.3.md, section A) : halls aux positions du
cadastre, loggias en retrait, grille de fenetres par logement, balcons arriere filants,
toit a quatre pans. Un seul appartement par immeuble est creuse et amenage.
"""

import math

from geom import prisme_pignon, toit_croupe

H = 144          # hauteur d'etage (sol a sol)
DALLE = 8
MUR = 16         # mur exterieur
CLOISON = 8
CAGE = 224       # largeur de la cage d'escalier
GAINE = 128      # largeur ajoutee pour l'ascenseur
PALIER = 176     # profondeur du palier depuis la face avant du hall
VOLEE = 144      # longueur d'une volee (9 marches de 16)
FOND_CAGE = 432  # fond de la cage depuis la face avant du hall
MARCHES = 9
VOLEE_A = (0, 104)    # volee montante, en s (position dans la cage)
VOLEE_B = (120, 224)  # volee de retour
FONDATION = 192

SAILLIE = 80       # avant-corps des halls
LOGGIA_L = 168     # largeur d'une loggia
LOGGIA_P = 48      # retrait des loggias
PEAU = 16
FEN_L = 64
FEN_Z0, FEN_Z1 = 48, 124
PF_Z1 = 120
SOUBASSEMENT = 56
PROF_BALCON = 64
DALLE_BALCON = 10
RAIL_H = 58
PENTE = 22
DEBORD_AVANT, DEBORD_ARR, DEBORD_PIGNON = 40, 24, 28
FASCIA = 22


def r8(x):
    return int(round(x / 8.0)) * 8


# --- briques de base ---------------------------------------------------------

def bloc(u0, v0, z0, u1, v1, z1, mat, faces=None, proj=None):
    """Pave local avec materiau par face : faces = {'u-': mat, 'v+': mat, ...}.

    proj = (largeur, hauteur) de la texture, applique a toutes les faces (sinon echelle du materiau).
    """
    f = faces or {}

    def pl(n, p, cle):
        m = f.get(cle, mat)
        return (n, p, m) if proj is None else (n, p, m, tuple(proj))

    return [
        pl((-1, 0, 0), (u0, 0, 0), "u-"), pl((1, 0, 0), (u1, 0, 0), "u+"),
        pl((0, -1, 0), (0, v0, 0), "v-"), pl((0, 1, 0), (0, v1, 0), "v+"),
        pl((0, 0, -1), (0, 0, z0), "z-"), pl((0, 0, 1), (0, 0, z1), "z+"),
    ]


def morceaux(a0, a1, z0, z1, ouvertures):
    """Rectangles (a, b, za, zb) qui couvrent [a0,a1] x [z0,z1] moins les ouvertures."""
    xs = sorted({a0, a1} | {max(a0, min(a1, o[i])) for o in ouvertures for i in (0, 1)})
    out = []
    for xa, xb in zip(xs, xs[1:]):
        if xb - xa < 0.5:
            continue
        trous = sorted((o[2], o[3]) for o in ouvertures if o[0] <= xa + 0.01 and o[1] >= xb - 0.01)
        z = z0
        for zb, zh in trous:
            if zb > z:
                out.append((xa, xb, z, min(zb, z1)))
            z = max(z, zh)
        if z < z1:
            out.append((xa, xb, z, z1))
    return [m for m in out if m[3] - m[2] >= 0.5]


def mur_perce(axe, a0, a1, e0, e1, z0, z1, ouvertures, mat, faces=None):
    """Mur plein moins des ouvertures rectangulaires.

    axe 'u' : le mur court le long de u (epaisseur en v de e0 a e1) ; axe 'v' : l'inverse.
    ouvertures : [(a_debut, a_fin, z_bas, z_haut)].
    """
    if axe == "u":
        return [bloc(a, e0, za, b, e1, zb, mat, faces) for a, b, za, zb in morceaux(a0, a1, z0, z1, ouvertures)]
    return [bloc(e0, a, za, e1, b, zb, mat, faces) for a, b, za, zb in morceaux(a0, a1, z0, z1, ouvertures)]


# --- l'immeuble --------------------------------------------------------------

class Immeuble:
    def __init__(self, nom, origine, eu, ev, longueur, profondeur, halls, niveaux, z0,
                 appartement, ascenseur=None, genouillere=48, lucarnes=(), z_sol_min=None):
        self.nom = nom
        self.o, self.eu, self.ev = origine, eu, ev
        self.L, self.D = longueur, profondeur
        self.halls = len(halls)
        self.centres = list(halls)           # u du centre de chaque hall
        self.N, self.z0 = niveaux, z0
        self.appart = appartement            # (hall, etage, cote -1/+1)
        self.ascenseur = ascenseur           # numero du hall avec ascenseur, ou None
        self.gen = genouillere               # mur au-dessus du dernier plafond
        self.lucarnes = list(lucarnes)       # u des lucarnes (pan avant)
        self.z_fond = (z_sol_min if z_sol_min is not None else z0) - FONDATION
        self.brushes, self.entites = [], []
        self.voff = 0                        # decalage en v applique pendant la construction des cages
        self.trous_arriere = []              # intervalles u des ouvertures arriere (pour placer les descentes d'eau)

        c = self.centres
        self.bord = [0] + [r8((c[k - 1] + c[k]) / 2) for k in range(1, len(c))] + [self.L]

    # repere local -> monde (rotations de 90 degres seulement : les paves restent alignes)
    def monde(self, u, v, z):
        return (self.o[0] + u * self.eu[0] + v * self.ev[0],
                self.o[1] + u * self.eu[1] + v * self.ev[1],
                self.z0 + z)

    def dir_monde(self, du, dv):
        return (du * self.eu[0] + dv * self.ev[0], du * self.eu[1] + dv * self.ev[1])

    def ajoute(self, planes):
        if planes and isinstance(planes[0], list):
            for p in planes:
                self.ajoute(p)
            return
        out = []
        for pl in planes:
            n, p, mat = pl[:3]
            nx, ny = self.dir_monde(n[0], n[1])
            out.append(((nx, ny, n[2]), self.monde(p[0], p[1] + self.voff, p[2]), mat) + tuple(pl[3:]))
        self.brushes.append(out)

    def entite(self, classname, u, v, z, **kv):
        x, y, zz = self.monde(u, v + self.voff, z)
        e = {"classname": classname, "origin": f"{x:g} {y:g} {zz:g}"}
        e.update({k: str(val) for k, val in kv.items()})
        self.entites.append(e)
        return e

    def lumiere(self, u, v, z, rayon=320, couleur="1 0.93 0.82", stops=14.5):
        self.entite("light", u, v, z, **{
            "PRIMARY_TYPE": "PRIMARY_OMNI", "PRIMARY_NOSHADOWMAP": "1", "_color": couleur,
            "def": "white_light", "radius": rayon, "stops": stops, "ENABLE_FALLOFF": "1",
            "client_server": "ClientSide", "shadowUpdate": "Never", "bulbRadius": "4",
            "lightingstate1": "1", "lightingstate2": "1", "lightingstate3": "1", "lightingstate4": "1",
            "spawnflags": "66"})

    def angle_monde(self, du, dv):
        x, y = self.dir_monde(du, dv)
        return math.degrees(math.atan2(y, x)) % 360

    @property
    def emprise(self):
        """Rectangle monde (x0, y0, x1, y1) qui englobe l'immeuble, halls, trottoir et balcons compris."""
        pts = [self.monde(u, v, 0) for u in (-40, self.L + 40) for v in (-SAILLIE - 130, self.D + PROF_BALCON + 16)]
        return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))

    # --- decoupage ---------------------------------------------------------
    def section(self, k):
        """(debut de section, debut de cage, fin de cage, fin de section) en u."""
        c = self.centres[k]
        c0 = c - CAGE // 2
        c1 = c + CAGE // 2 + (GAINE if self.ascenseur == k else 0)
        return self.bord[k], c0, c1, self.bord[k + 1]

    def colonnes(self):
        """Colonnes d'appartements : (hall, cote, u0, u1)."""
        for k in range(self.halls):
            u0, c0, c1, u1 = self.section(k)
            yield k, -1, u0, c0
            yield k, 1, c1, u1

    def est_jouable(self, k, cote):
        return (k, cote) == (self.appart[0], self.appart[2])

    def loggias(self, k, cote, u0, u1):
        """Loggias d'une colonne : une de chaque cote des halls d'extremite (pas dans la colonne jouable)."""
        if self.est_jouable(k, cote) or k not in (0, self.halls - 1):
            return []
        w = u1 - u0
        if w < LOGGIA_L + 96:
            return []
        return [(u1 - LOGGIA_L, u1)] if cote < 0 else [(u0, u0 + LOGGIA_L)]

    # --- ouvertures --------------------------------------------------------
    def fenetres_avant(self, k, cote, u0, u1):
        """Positions (a, b) des fenetres de la facade avant d'une colonne, repetees a chaque niveau."""
        if self.est_jouable(k, cote):
            return self.fenetres_appart(u0, u1, cote)
        mur0, mur1 = u0, u1
        for l0, l1 in self.loggias(k, cote, u0, u1):
            if cote < 0:
                mur1 = l0
            else:
                mur0 = l1
        w = mur1 - mur0
        if w < 96:
            return []
        n = max(1, min(4, int(round(w / 136.0))))
        return [(r8(mur0 + (i + 0.5) * w / n - FEN_L / 2), r8(mur0 + (i + 0.5) * w / n - FEN_L / 2) + FEN_L)
                for i in range(n)]

    def fenetres_appart(self, u0, u1, cote):
        """Deux fenetres de cuisine, a 168..232 et 248..312 du mur de la cage."""
        paires = [(168, 232), (248, 312)]
        if cote < 0:
            return sorted((u1 - b, u1 - a) for a, b in paires)
        return [(u0 + a, u0 + b) for a, b in paires]

    def ouvertures_arriere(self, k, cote, u0, u1, niv):
        """Liste (a, b, z0, z1) des ouvertures arriere : porte-fenetre et fenetre par travee."""
        w = u1 - u0
        if self.est_jouable(k, cote) and niv == self.appart[1]:
            return self.ouvertures_arriere_appart(u0, u1, cote)
        n = max(1, int(w // 192))
        t = w / n
        g = (t - 160) / 3
        out = []
        for i in range(n):
            a = u0 + i * t
            if i % 2 == 0:
                pf = (a + g, a + g + 104)
                fe = (pf[1] + g, pf[1] + g + 56)
            else:
                fe = (a + g, a + g + 56)
                pf = (fe[1] + g, fe[1] + g + 104)
            out.append((r8(pf[0]), r8(pf[0]) + 104, 0, PF_Z1))
            out.append((r8(fe[0]), r8(fe[0]) + 56, FEN_Z0, FEN_Z1))
        return out

    def ouvertures_arriere_appart(self, u0, u1, cote):
        W = u1 - u0
        xs = r8(W * 0.58)
        X = (lambda x: u1 - x) if cote < 0 else (lambda x: u0 + x)  # noqa: E731
        pf = sorted((X(40), X(xs - 40)))
        fc = sorted((X(xs + 40), X(W - 48)))
        return [(pf[0], pf[1], 0, PF_Z1 - 4), (fc[0], fc[1], FEN_Z0 - 8, FEN_Z1 - 12)]

    # --- construction --------------------------------------------------------
    def construire(self, mat):
        m = self.mat = dict(mat)
        m["facade"] = m["facade_beige"]
        top = self.N * H
        haut = top + self.gen
        for k, cote, u0, u1 in self.colonnes():
            self.colonne(k, cote, u0, u1)
        for k in range(self.halls):
            self.cage(k)
            self.avant_corps(k)
        self.balcons()
        self.pignons()
        self.pilastres_et_soubassement()
        self.toiture()
        self.haut = haut
        return self

    def tranches(self, u0, u1, loggias):
        """Decoupe [u0, u1] autour des loggias : liste (a, b, loggia?)."""
        out, x = [], u0
        for l0, l1 in sorted(loggias):
            if l0 > x:
                out.append((x, l0, False))
            out.append((l0, l1, True))
            x = l1
        if x < u1:
            out.append((x, u1, False))
        return out

    def colonne(self, k, cote, u0, u1):
        m = self.mat
        top = self.N * H
        haut = top + self.gen
        D = self.D
        jouable = self.est_jouable(k, cote)
        loggias = self.loggias(k, cote, u0, u1)
        fv = {"v-": m["fond_vitre"], "v+": m["fond_vitre"], "u-": m["facade_blanche"], "u+": m["facade_blanche"]}

        # remplissage plein (sauf l'appartement jouable, creuse), en retrait dans les loggias
        for a, b, lg in self.tranches(u0, u1, loggias):
            v0 = PEAU + (LOGGIA_P if lg else 0)
            if jouable:
                fz, _ = self.appart[1] * H, 0
                self.ajoute(bloc(a, v0, self.z_fond, b, D - PEAU, fz, m["facade"], {"z+": m["dalle"]}))
                self.ajoute(bloc(a, v0, fz + H - DALLE, b, D - PEAU, haut, m["facade"], {"z-": m["plafond"]}))
            else:
                self.ajoute(bloc(a, v0, self.z_fond, b, D - PEAU, haut, m["facade"], fv))
        if jouable:
            self.appartement(k, cote, u0, u1, self.appart[1] * H)

        # peau avant, une seule par colonne et par tranche, avec les fenetres de tous les niveaux
        fen = self.fenetres_avant(k, cote, u0, u1)
        ouv = []
        for niv in range(self.N):
            for a, b in fen:
                ouv.append((a, b, niv * H + FEN_Z0, niv * H + FEN_Z1))
        faces_av = {"v-": m["facade"], "v+": m["appart_mur"] if jouable else m["fond_vitre"]}
        for a, b, lg in self.tranches(u0, u1, loggias):
            if lg:
                self.loggia(a, b, cote)
            else:
                self.ajoute(mur_perce("u", a, b, 0, PEAU, self.z_fond, haut,
                                      [o for o in ouv if o[0] >= a - 0.01 and o[1] <= b + 0.01], m["facade"], faces_av))
        for niv in range(self.N):
            for i, (a, b) in enumerate(fen):
                self.fenetre(a, b, niv * H + FEN_Z0, niv * H + FEN_Z1, True,
                             volet=((niv * 7 + i * 3 + k) % 3 == 0), vitre=jouable and niv == self.appart[1])

        # peau arriere
        ouv_ar = []
        for niv in range(self.N):
            for a, b, za, zb in self.ouvertures_arriere(k, cote, u0, u1, niv):
                ouv_ar.append((a, b, niv * H + za, niv * H + zb))
                self.trous_arriere.append((a - 8, b + 8))
        faces_ar = {"v+": m["facade_blanche"], "v-": m["appart_mur"] if jouable else m["fond_vitre"]}
        self.ajoute(mur_perce("u", u0, u1, D - PEAU, D, self.z_fond, haut, ouv_ar, m["facade_blanche"], faces_ar))
        for niv in range(self.N):
            for i, (a, b, za, zb) in enumerate(self.ouvertures_arriere(k, cote, u0, u1, niv)):
                self.fenetre(a, b, niv * H + za, niv * H + zb, False,
                             volet=False, vitre=jouable and niv == self.appart[1], porte=(za == 0))

    def fenetre(self, a, b, z0, z1, avant, volet=False, vitre=False, porte=False):
        """Vitrage dans la niche de la peau (8 u d'embrasure devant, 6 derriere), appui et volet."""
        m = self.mat
        mv = m["vitre"] if vitre else m["fenetre"]
        proj = (b - a, z1 - z0)
        if avant:
            self.ajoute(bloc(a, 8, z0, b, 10, z1, mv, proj=proj))
            self.ajoute(bloc(a - 4, -6, z0 - 6, b + 4, 0, z0, m["appui"]))
            if volet:
                self.ajoute(bloc(a, -3, z1 - 40, b, 0, z1, m["volet"]))
                self.ajoute(bloc(a - 2, -4, z1, b + 2, 0, z1 + 8, m["cadre"]))
        else:
            D = self.D
            self.ajoute(bloc(a, D - 10, z0, b, D - 8, z1, mv, proj=proj))
            if not porte:
                self.ajoute(bloc(a - 4, D, z0 - 6, b + 4, D + 6, z0, m["appui"]))
            if volet:
                self.ajoute(bloc(a, D, z1 - 40, b, D + 3, z1, m["volet"]))

    def loggia(self, l0, l1, cote):
        """Loggia en retrait : fond vitre, dalle et garde-corps a lisses a chaque niveau."""
        m = self.mat
        haut = self.N * H + self.gen
        fond = LOGGIA_P + PEAU - 16  # face avant du fond de loggia : v = 48
        # joues de la fente (la colonne voisine est pleine)
        for u in (l0, l1 - 2):
            self.ajoute(bloc(u, 0, self.z_fond, u + 2, fond, haut, m["loggia"]))
        # fond : peau de 16 percee d'une baie vitree par niveau
        ouv = [(l0 + 24, l1 - 24, niv * H, niv * H + 120) for niv in range(self.N)]
        self.ajoute(mur_perce("u", l0, l1, fond, fond + 16, self.z_fond, haut, ouv, m["loggia"],
                              {"v-": m["loggia"], "v+": m["fond_vitre"]}))
        for niv in range(self.N):
            z = niv * H
            self.ajoute(bloc(l0 + 24, fond + 8, z, l1 - 24, fond + 10, z + 120, m["fenetre"], proj=(l1 - l0 - 48, 120)))
            self.ajoute(bloc(l0, 0, z - 8, l1, fond, z, m["dalle_balcon"], {"v-": m["balcon"]}))
            for zz in (18, 36):
                self.ajoute(bloc(l0 + 2, -2, z + zz, l1 - 2, 2, z + zz + 3, m["garde_corps"]))
            self.ajoute(bloc(l0 + 2, -2, z + 52, l1 - 2, 2, z + 58, m["garde_corps"]))
            for u in (l0 + 2, l1 - 6):
                self.ajoute(bloc(u, -2, z, u + 4, 2, z + 52, m["garde_corps"]))

    def avant_corps(self, k):
        """Habillage exterieur d'un hall : flancs, face avant, entree, fentes, auvent, trottoir."""
        m = self.mat
        u0, c0, c1, u1 = self.section(k)
        haut = self.N * H + self.gen
        self.voff = -SAILLIE
        sc = c0 + CAGE // 2           # centre de l'escalier
        S = lambda s: s  # noqa: E731
        # flancs : crepi au rez, panneaux bruns au-dessus
        for u in (c0, c1 - MUR):
            self.ajoute(bloc(u, 0, self.z_fond, u + MUR, SAILLIE, H, m["facade"]))
            self.ajoute(bloc(u, 0, H, u + MUR, SAILLIE, haut, m["panneau"], {"v+": m["facade"]}))
        # face avant percee : entree (z 0..124) et fente de palier a chaque etage
        ouv = [(sc - 96, sc + 96, 0, 124)] + [(sc - 80, sc + 80, niv * H + 60, niv * H + 84) for niv in range(1, self.N)]
        self.ajoute(mur_perce("u", c0, c1, 0, MUR, self.z_fond, H, ouv, m["facade"], {"v-": m["facade"], "v+": m["hall_mur"]}))
        self.ajoute(mur_perce("u", c0, c1, 0, MUR, H, haut, ouv, m["panneau"], {"v+": m["hall_mur"]}))
        for niv in range(1, self.N):
            self.ajoute(bloc(sc - 80, 6, niv * H + 60, sc + 80, 8, niv * H + 84, m["vitre"]))
        # entree : sas vitres de part et d'autre d'un passage libre de 112
        self.ajoute(bloc(sc - 96, 6, 0, sc - 56, 8, 124, m["vitre"]))
        self.ajoute(bloc(sc + 56, 6, 0, sc + 96, 8, 124, m["vitre"]))
        for u in (sc - 96, sc - 56 - 4, sc + 56, sc + 92):
            self.ajoute(bloc(u, 4, 0, u + 4, 10, 124, m["fond_vitre"]))
        # auvent mince, trottoir devant l'entree
        self.ajoute(bloc(sc - 112, -32, 126, sc + 112, 0, 134, m["auvent"]))
        self.ajoute(bloc(sc - 150, -140, -16, sc + 150, 0, 0, m["trottoir"]))
        self.voff = 0

    # --- balcons arriere -------------------------------------------------------
    def balcons(self):
        """Balcons filants et continus a chaque niveau, terrasse au rez ; garde-corps ajoure par segment."""
        m, D, L = self.mat, self.D, self.L
        P = PROF_BALCON
        n_seg = max(1, int(round(L / 787.0)))
        coupes = [0] + [r8(L * i / n_seg) for i in range(1, n_seg)] + [L]
        for niv in range(self.N):
            z = niv * H
            self.ajoute(bloc(0, D, z - DALLE_BALCON, L, D + P, z, m["dalle_balcon"],
                             {"v+": m["balcon"], "u-": m["balcon"], "u+": m["balcon"]}))
            if niv == 0:
                self.ajoute(bloc(0, D, -48, L, D + P, -DALLE_BALCON, m["socle"]))
            for s in range(n_seg):
                a, b = coupes[s], coupes[s + 1]
                if niv == 0:
                    panneau, main, hh = m["rail_vert"], m["rail_sombre_main"], 44
                elif niv >= self.N - 2:
                    panneau, main, hh = m["rail_clair"], m["rail_clair_main"], 52
                elif niv == 1 and s % 2 == 1:
                    panneau, main, hh = m["rail_plein"], m["rail_sombre_main"], 52
                else:
                    panneau, main, hh = m["rail_sombre"], m["rail_sombre_main"], 52
                a2, b2 = a + (2 if s == 0 else 0), b - (2 if s == n_seg - 1 else 0)
                self.ajoute(bloc(a2, D + P - 2, z + 8, b2, D + P, z + hh, panneau))
                self.ajoute(bloc(a2, D + P - 4, z + hh, b2, D + P, z + hh + 6, main))
                self.ajoute(bloc(a2, D + P - 2, z, b2, D + P, z + 8, main))
            # retours aux pignons
            for u in (0, L - 2):
                self.ajoute(bloc(u, D, z + 8, u + 2, D + P, z + (44 if niv == 0 else 52), m["rail_clair_main"]))
        # descentes d'eau arriere aux coupures
        for u in coupes[1:-1]:
            for d in range(0, 400, 8):
                cand = [x for x in (u + d, u - d) if not any(a <= x <= b for a, b in self.trous_arriere)]
                if cand:
                    u = cand[0]
                    break
            self.ajoute(bloc(u - 3, D + 20, -48, u + 3, D + 26, self.N * H + 8, m["garde_corps"]))

    def pignons(self):
        """Petites fenetres de pignon, deux par niveau."""
        m = self.mat
        for niv in range(self.N):
            z = niv * H
            for vv in (self.D / 3 - 28, 2 * self.D / 3 - 28):
                a, b = r8(vv), r8(vv) + 56
                self.ajoute(bloc(-2, a, z + FEN_Z0, 0, b, z + FEN_Z1, m["fenetre"], proj=(56, FEN_Z1 - FEN_Z0)))
                self.ajoute(bloc(self.L, a, z + FEN_Z0, self.L + 2, b, z + FEN_Z1, m["fenetre"], proj=(56, FEN_Z1 - FEN_Z0)))

    def pilastres_et_soubassement(self):
        m = self.mat
        haut = self.N * H + self.gen
        # soubassement le long de la facade principale, interrompu devant les halls
        entrees = [(c0 - 8, c1 + 8, -48, SOUBASSEMENT) for _, c0, c1, _ in (self.section(k) for k in range(self.halls))]
        for a, b, za, zb in morceaux(-3, self.L + 3, -48, SOUBASSEMENT, entrees):
            self.ajoute(bloc(a, -3, za, b, 0, zb, m["socle"]))
        for u in (-3, self.L):
            self.ajoute(bloc(u, -3, -48, u + 3, self.D + 3, SOUBASSEMENT, m["socle"]))
        self.ajoute(bloc(-3, self.D, -48, self.L + 3, self.D + 3, -DALLE_BALCON, m["socle"]))
        # pilastres plus clairs aux extremites des murs a fenetres
        for k, cote, u0, u1 in self.colonnes():
            if self.est_jouable(k, cote) or self.loggias(k, cote, u0, u1):
                continue
            fen = self.fenetres_avant(k, cote, u0, u1)
            if not fen:
                continue
            for a in (fen[0][0] - 24, fen[-1][1] + 24):
                if u0 + 12 < a < u1 - 12:
                    self.ajoute(bloc(a - 6, -3, SOUBASSEMENT, a + 6, 0, haut, m["facade_blanche"]))
        # descentes d'eau avant, aux angles des loggias
        for k in range(self.halls):
            for k2, cote, u0, u1 in self.colonnes():
                for l0, l1 in self.loggias(k2, cote, u0, u1):
                    if k2 != k:
                        continue
                    u = l1 if cote < 0 else l0
                    self.ajoute(bloc(u - 3, -2, 0, u + 3, 4, self.N * H + 8, m["garde_corps"]))

    # --- toiture -----------------------------------------------------------
    def toiture(self):
        m = self.mat
        top = self.N * H + self.gen
        u0, u1 = -DEBORD_PIGNON, self.L + DEBORD_PIGNON
        v0, v1 = -(SAILLIE + DEBORD_AVANT), self.D + DEBORD_ARR
        planes, z_faitage = toit_croupe(u0, v0, u1, v1, top, PENTE, m["toit"], m["rive"], FASCIA)
        self.ajoute(planes)
        self.z_faitage = z_faitage
        vm = (v0 + v1) / 2
        lf = (u1 - u0) - (v1 - v0)  # longueur du faitage
        uf0 = (u0 + u1) / 2 - lf / 2
        # souches de cheminee par groupes de quatre
        t = math.tan(math.radians(PENTE))
        for frac in (0.14, 0.38, 0.62, 0.86):
            uc = r8(self.L * frac)
            for du in (-40, 40):
                for dv in (-60, 60):
                    zp = z_faitage - abs(dv) * t
                    self.ajoute(bloc(uc + du - 20, vm + dv - 20, zp - 30, uc + du + 20, vm + dv + 20, z_faitage + 60, m["cheminee"]))
                    self.ajoute(bloc(uc + du - 24, vm + dv - 24, z_faitage + 60, uc + du + 24, vm + dv + 24, z_faitage + 66, m["appui"]))
        # lucarnes sur le pan avant
        for u in self.lucarnes:
            vd = -SAILLIE - 20
            zp = top + (vd - v0) * t
            self.ajoute(prisme_pignon(u - 36, u + 36, vd - 16, vd + 40, zp - 10, zp + 40, 34, m["facade_blanche"], m["toit"]))
            self.ajoute(bloc(u - 24, vd - 18, zp + 4, u + 24, vd - 16, zp + 38, m["fenetre"], proj=(48, 34)))

    # --- cage d'escalier ----------------------------------------------------
    def cage(self, k):
        """Escalier a deux volees. Coordonnees v relatives a la face avant du hall (decalee de -SAILLIE)."""
        m = self.mat
        u0, c0, c1, u1 = self.section(k)
        top = self.N * H
        B = c1 - c0
        Dc = self.D + SAILLIE
        asc = self.ascenseur == k
        self.voff = -SAILLIE
        S = lambda s: c0 + s  # noqa: E731  position dans la cage -> u

        # fondation et sol du rez ; sous la gaine, la cuvette est creusee pour que le plancher de cabine
        # ne soit pas coplanaire avec le sol du hall
        if asc:
            g0, g1 = PALIER, PALIER + GAINE
            self.ajoute(bloc(c0, 0, self.z_fond, c0 + CAGE, Dc, 0, m["facade"], {"z+": m["hall_sol"]}))
            self.ajoute(bloc(c0 + CAGE, 0, self.z_fond, c1, g0, 0, m["facade"], {"z+": m["hall_sol"]}))
            self.ajoute(bloc(c0 + CAGE, g0, self.z_fond, c1, g1, -24, m["facade"], {"z+": m["gaine"]}))
            self.ajoute(bloc(c0 + CAGE, g1, self.z_fond, c1, Dc, 0, m["facade"], {"z+": m["hall_sol"]}))
        else:
            self.ajoute(bloc(c0, 0, self.z_fond, c1, Dc, 0, m["facade"], {"z+": m["hall_sol"]}))
        # fond de la cage : plein
        self.ajoute(bloc(c0, FOND_CAGE, 0, c1, Dc, top + self.gen, m["facade"],
                         {"v-": m["hall_mur"], "v+": m["facade_blanche"]}))
        # plafond sous toiture
        self.ajoute(bloc(c0, MUR, top - DALLE, c1, FOND_CAGE, top, m["facade"], {"z-": m["plafond"]}))

        # mur entre les deux volees, du rez au dernier palier
        self.ajoute(bloc(S(VOLEE_A[1]), PALIER, 0, S(VOLEE_B[0]), PALIER + VOLEE, top - DALLE, m["hall_mur"]))
        # placard sous la premiere volee de retour
        self.ajoute(bloc(S(VOLEE_B[0]), PALIER, 0, S(VOLEE_B[1]), PALIER + 8, 120, m["hall_mur"]))
        self.ajoute(bloc(S(VOLEE_B[0]), PALIER + 8, 0, S(VOLEE_B[1]), PALIER + VOLEE, 64, m["hall_mur"]))

        r = (H / 2) / MARCHES
        g = VOLEE / MARCHES
        for niv in range(self.N - 1):
            z = niv * H
            # volee A : de PALIER vers le fond, monte d'un demi-etage
            for i in range(MARCHES):
                zt = z + (i + 1) * r
                self.ajoute(bloc(S(VOLEE_A[0]), PALIER + i * g, zt - 24, S(VOLEE_A[1]), PALIER + (i + 1) * g, zt,
                                 m["hall_sol"]))
            # palier intermediaire
            self.ajoute(bloc(S(0), PALIER + VOLEE, z + H / 2 - DALLE, S(CAGE), FOND_CAGE, z + H / 2,
                             m["hall_sol"], {"z-": m["plafond"]}))
            # volee B : retour vers le palier d'etage
            for i in range(MARCHES):
                zt = z + H / 2 + (i + 1) * r
                self.ajoute(bloc(S(VOLEE_B[0]), PALIER + VOLEE - (i + 1) * g, zt - 24, S(VOLEE_B[1]),
                                 PALIER + VOLEE - i * g, zt, m["hall_sol"]))
            # palier d'etage (dalle)
            self.ajoute(bloc(S(0), MUR, (niv + 1) * H - DALLE, S(B), PALIER, (niv + 1) * H,
                             m["hall_sol"], {"z-": m["plafond"]}))
            # main courante le long du mur central (decalee pour ne plus etre coplanaire avec les marches)
            for s0 in (VOLEE_A[1] - 12, VOLEE_B[0] + 8):
                self.ajoute(bloc(S(s0), PALIER, z + 36, S(s0 + 4), PALIER + VOLEE, z + 40 + H / 2, m["rampe"]))

        # portes d'appartement sur chaque palier (fermees), boites aux lettres au rez
        for niv in range(1, self.N):
            z = niv * H
            for cote in (-1, 1):
                if (k, niv, cote) == self.appart:
                    continue
                if cote < 0:
                    self.ajoute(bloc(c0, 104, z, c0 + 3, 168, z + 112, m["porte"]))
                else:
                    self.ajoute(bloc(c1 - 3, 104, z, c1, 168, z + 112, m["porte"]))
            self.lumiere(c0 + CAGE / 2, PALIER / 2 + 16, z + H - 24, rayon=280)
        self.ajoute(bloc(c0, 120, 40, c0 + 6, 168, 104, m["boites"]))
        self.lumiere(c0 + CAGE / 2, 96, H - 24, rayon=300)
        self.lumiere(c0 + CAGE / 2, 20, 116, rayon=200)

        if asc:
            self.ascenseur_cage(c0)
        self.voff = 0

    # --- ascenseur (batiment 1) ------------------------------------------------
    def ascenseur_cage(self, c0):
        m = self.mat
        top = self.N * H
        s0, s1 = c0 + CAGE, c0 + CAGE + GAINE
        v0, v1 = PALIER, PALIER + GAINE
        # parois de la gaine
        self.ajoute(bloc(s0, v0, 0, s0 + 8, v1, top - DALLE, m["hall_mur"], {"u+": m["gaine"]}))
        self.ajoute(bloc(s1 - 8, v0, 0, s1, v1, top - DALLE, m["hall_mur"], {"u-": m["gaine"]}))
        self.ajoute(bloc(s0, v1 - 8, 0, s1, v1, top - DALLE, m["gaine"]))
        self.ajoute(bloc(s0, v1, 0, s1, FOND_CAGE, top - DALLE, m["facade"]))
        ouv = [(s0 + 32, s1 - 32, niv * H, niv * H + 112) for niv in range(self.N)]
        self.ajoute(mur_perce("u", s0, s1, v0, v0 + 8, 0, top - DALLE, ouv, m["hall_mur"], {"v+": m["gaine"]}))
        # coordonnees de la gaine dans le repere de l'immeuble (face avant du hall en v = -SAILLIE)
        self.gaine = (s0, s1, v0 - SAILLIE, v1 - SAILLIE)

    def ascenseur_entites(self):
        """Cabine, portes palieres et boutons : entites scriptees pour zm_seyssel.gsc."""
        if self.ascenseur is None:
            return []
        m = self.mat
        s0, s1, v0, v1 = self.gaine
        ents = []

        def brushmodel(nom, briques, **kv):
            out = []
            for b in briques:
                out.append([(self.dir_monde(n[0], n[1]) + (n[2],), self.monde(*p), mat) for n, p, mat in (pl[:3] for pl in b)])
            e = {"classname": "script_brushmodel", "targetname": nom, "_brushes": out}
            e.update({k: str(v) for k, v in kv.items()})
            ents.append(e)
            return e

        # cabine : plancher, plafond, trois parois (ouverte cote palier)
        a0, a1, b0, b1 = s0 + 12, s1 - 12, v0 + 12, v1 - 12
        brushmodel("ascenseur_cabine", [
            bloc(a0, b0, -8, a1, b1, 0, m["cabine_sol"]),
            bloc(a0, b0, 120, a1, b1, 128, m["cabine"]),
            bloc(a0, b1 - 4, 0, a1, b1, 120, m["cabine"]),
            bloc(a0, b0, 0, a0 + 4, b1, 120, m["cabine"]),
            bloc(a1 - 4, b0, 0, a1, b1, 120, m["cabine"]),
        ])
        # bouton dans la cabine (suit la cabine)
        trig = [bloc(a0 + 8, b0 + 8, 0, a1 - 8, b1 - 8, 96, "trigger")]
        e = brushmodel("ascenseur_bouton", trig)
        e["classname"] = "trigger_use"
        e["cursorhint"] = "HINT_NOICON"
        # portes palieres + boutons d'appel
        glisse = self.dir_monde(72, 0)  # la porte s'efface dans le mur, cote appartement voisin
        for niv in range(self.N):
            z = niv * H
            brushmodel("ascenseur_porte", [bloc(s0 + 32, v0 + 1, z, s1 - 32, v0 + 7, z + 112, m["porte_asc"])],
                       script_int=niv, script_vector=f"{glisse[0]:g} {glisse[1]:g} 0")
            t = brushmodel("ascenseur_appel", [bloc(s0 + 16, v0 - 72, z, s1 - 16, v0, z + 96, "trigger")],
                           script_int=niv)
            t["classname"] = "trigger_use"
            t["cursorhint"] = "HINT_NOICON"
        return ents

    # --- appartement jouable ---------------------------------------------------
    def appartement(self, k, cote, u0, u1, fz):
        """Appartement traversant creuse dans la colonne, porte sur le palier du hall k.

        Les facades (peau percee) sont faites par colonne() : ici seulement les cloisons,
        les sols, la porte d'entree et les lumieres.
        """
        m = self.mat
        D, W = self.D, u1 - u0
        z0, z1 = fz, fz + H - DALLE
        # x : distance au mur de la cage (0) vers le pignon (W) ; u reel selon le cote
        X = (lambda x: u1 - x) if cote < 0 else (lambda x: u0 + x)  # noqa: E731

        def b(x0, v0, za, x1, v1, zb, mat, faces=None):
            ua, ub = sorted((X(x0), X(x1)))
            # les noms de faces u-/u+ sont inverses quand x va dans le sens des u decroissants
            if faces and cote < 0:
                faces = {("u+" if f == "u-" else "u-" if f == "u+" else f): v for f, v in faces.items()}
            return bloc(ua, v0, za, ub, v1, zb, mat, faces)

        mur_app = m["appart_mur"]
        # murs : cote cage (avec porte sur le palier), cote voisin
        porte = (24, 88)
        for (va, vb) in ((MUR, porte[0]), (porte[1], D - MUR)):
            self.ajoute(b(0, va, z0, CLOISON, vb, z1, mur_app, {"u-": m["hall_mur"]}))
        self.ajoute(b(0, porte[0], z0 + 112, CLOISON, porte[1], z1, mur_app, {"u-": m["hall_mur"]}))
        self.ajoute(b(W - CLOISON, MUR, z0, W, D - MUR, z1, mur_app, {"u+": m["facade"]}))

        # plan : entree, cuisine (facade avant), sdb, chambre 1, sejour + chambre 2 (facade arriere)
        xc = 136                          # cuisine a partir de x
        xcl = 112                         # mur du couloir
        v_cuis = round(D * 0.30 / 8) * 8  # fond de cuisine
        v_sdb = round(D * 0.47 / 8) * 8
        v_sej = round(D * 0.64 / 8) * 8
        xs = round(W * 0.58 / 8) * 8      # separation sejour / chambre 2
        ep = CLOISON

        # cloisons interieures (porte = trou de 64 x 112)
        def cloison_x(x, va, vb, portes=()):
            ouv = [(p, p + 64, z0, z0 + 112) for p in portes]
            for a, c, za, zb in morceaux(va, vb, z0, z1, ouv):
                self.ajoute(b(x, a, za, x + CLOISON, c, zb, mur_app))

        def cloison_v(v, xa, xb, portes=()):
            ouv = [(p, p + 64, z0, z0 + 112) for p in portes]
            for a, c, za, zb in morceaux(xa, xb, z0, z1, ouv):
                self.ajoute(b(a, v, za, c, v + CLOISON, zb, mur_app))

        milieu = lambda a, c: round(((a + c) / 2 - 32) / 8) * 8  # noqa: E731
        cloison_x(xc, MUR, v_cuis, portes=(milieu(MUR, v_cuis),))                      # entree | cuisine
        cloison_v(v_cuis, xc, W - ep)                                                   # cuisine | sdb, ch. 1
        cloison_x(xcl, v_cuis, v_sej, portes=(milieu(v_cuis, v_sdb), milieu(v_sdb, v_sej)))  # couloir
        cloison_v(v_sdb, xcl, W - ep)                                                   # sdb | chambre 1
        cloison_v(v_sej, xcl, W - ep)                                                   # chambre 1 | sejour
        cloison_x(xs, v_sej, D - MUR, portes=(v_sej + 32,))                            # sejour | chambre 2

        # revetements de sol (2 unites), sans chevauchement
        def sol(x0, v0, x1, v1, mat):
            self.ajoute(b(x0, v0, z0, x1, v1, z0 + 2, mat))
        sol(CLOISON, MUR, xc, v_cuis, m["sol_entree"])
        sol(CLOISON, v_cuis, xcl, v_sej, m["sol_entree"])
        sol(xc + CLOISON, MUR, W - ep, v_cuis, m["sol_cuisine"])
        sol(xcl + CLOISON, v_cuis + CLOISON, W - ep, v_sdb, m["sol_sdb"])
        sol(xcl + CLOISON, v_sdb + CLOISON, W - ep, v_sej, m["sol_chambre"])
        sol(CLOISON, v_sej + CLOISON, W - ep, D - MUR, m["sol_chambre"])
        # faience sur le mur du fond de la salle de bain et credence de cuisine
        self.ajoute(b(W - ep - 2, v_cuis + CLOISON, z0 + 2, W - ep, v_sdb, z0 + 96, m["faience"]))
        self.ajoute(b(xc + CLOISON, v_cuis - 2, z0 + 2, W - ep, v_cuis, z0 + 96, m["faience"]))
        # plan de travail
        self.ajoute(b(xc + CLOISON, v_cuis - 40, z0 + 2, W - ep - 8, v_cuis - 2, z0 + 36, m["meuble"]))

        # lumieres et sonde de reflexion
        for (x, v) in (((xc + W) / 2, v_cuis / 2), (W * 0.3, (v_sej + D) / 2), ((xs + W) / 2, (v_sej + D) / 2),
                       ((xcl + W) / 2, (v_sdb + v_sej) / 2), (60, (v_cuis + v_sej) / 2), ((xcl + W) / 2, (v_cuis + v_sdb) / 2)):
            self.lumiere(X(x), v, fz + H - 32, rayon=260)
        self.sonde = self.monde(X(W / 2), D / 2, fz + 64)
        self.centre_appart = self.monde(X(W / 2), (v_sej + D) / 2, fz + 8)
