"""Generateur d'immeubles HLM : coque, facades, halls, escaliers, appartement jouable, ascenseur.

Chaque immeuble est construit dans un repere local puis pose dans le monde :
    u : le long de l'immeuble (0 -> longueur)
    v : en travers, depuis la facade des halls (0) vers la facade arriere (profondeur)
    z : hauteur depuis le sol fini du rez-de-chaussee

Un immeuble = des sections (une par hall). Dans chaque section : la cage d'escalier
au milieu, un appartement de chaque cote. Les appartements fermes sont des blocs
pleins habilles en facade ; un seul appartement par immeuble est creuse et amenage.
"""

import math

H = 144          # hauteur d'etage (sol a sol)
DALLE = 8
MUR = 16         # mur exterieur
CLOISON = 8
CAGE = 224       # largeur de la cage d'escalier
GAINE = 128      # largeur ajoutee pour l'ascenseur
PALIER = 176     # profondeur du palier (v de MUR a PALIER)
VOLEE = 144      # longueur d'une volee (9 marches de 16)
FOND_CAGE = 432  # fond de la cage (palier intermediaire jusqu'ici)
MARCHES = 9
VOLEE_A = (0, 104)    # volee montante, en s (position dans la cage)
VOLEE_B = (120, 224)  # volee de retour
FONDATION = 192


# --- briques de base ---------------------------------------------------------

def bloc(u0, v0, z0, u1, v1, z1, mat, faces=None):
    """Pave local avec materiau par face : faces = {'u-': mat, 'v+': mat, ...}."""
    f = faces or {}
    return [
        ((-1, 0, 0), (u0, 0, 0), f.get("u-", mat)), ((1, 0, 0), (u1, 0, 0), f.get("u+", mat)),
        ((0, -1, 0), (0, v0, 0), f.get("v-", mat)), ((0, 1, 0), (0, v1, 0), f.get("v+", mat)),
        ((0, 0, -1), (0, 0, z0), f.get("z-", mat)), ((0, 0, 1), (0, 0, z1), f.get("z+", mat)),
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


def toit_deux_pans(u0, v0, u1, v1, z, pente, mat):
    """Toit a deux pans, faitage le long de u."""
    vm = (v0 + v1) / 2
    h = (vm - v0) * math.tan(math.radians(pente))
    planes = [
        ((0, 0, -1), (0, 0, z), mat),
        ((-1, 0, 0), (u0, 0, 0), mat), ((1, 0, 0), (u1, 0, 0), mat),
        ((0, -h, vm - v0), (0, v0, z), mat),
        ((0, h, v1 - vm), (0, v1, z), mat),
    ]
    return planes, z + h


# --- l'immeuble --------------------------------------------------------------

class Immeuble:
    def __init__(self, nom, origine, eu, ev, longueur, profondeur, halls, niveaux, z0, style,
                 appartement, ascenseur=None, z_sol_min=None):
        self.nom, self.style = nom, style
        self.o, self.eu, self.ev = origine, eu, ev
        self.L, self.D = longueur, profondeur
        self.halls, self.N, self.z0 = halls, niveaux, z0
        self.appart = appartement          # (hall, etage, cote -1/+1)
        self.ascenseur = ascenseur         # numero du hall avec ascenseur, ou None
        self.z_fond = (z_sol_min if z_sol_min is not None else z0) - FONDATION
        self.brushes, self.entites = [], []
        self.ws = self.L / self.halls

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
        for n, p, mat in planes:
            nx, ny = self.dir_monde(n[0], n[1])
            out.append(((nx, ny, n[2]), self.monde(*p), mat))
        self.brushes.append(out)

    def entite(self, classname, u, v, z, **kv):
        x, y, zz = self.monde(u, v, z)
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

    # --- decoupage ---------------------------------------------------------
    def section(self, k):
        u0 = k * self.ws
        cage = CAGE + (GAINE if self.ascenseur == k else 0)
        c0 = u0 + (self.ws - cage) / 2
        return u0, c0, c0 + cage, u0 + self.ws

    def colonnes(self):
        """Colonnes d'appartements : (hall, cote, u0, u1)."""
        for k in range(self.halls):
            u0, c0, c1, u1 = self.section(k)
            yield k, -1, u0, c0
            yield k, 1, c1, u1

    # --- construction --------------------------------------------------------
    def construire(self, mat):
        self.mat = mat
        top = self.N * H
        hall_ouvert, etage_ouvert, cote_ouvert = self.appart
        for k, cote, u0, u1 in self.colonnes():
            if (k, cote) == (hall_ouvert, cote_ouvert):
                fz = etage_ouvert * H
                self.ajoute(bloc(u0, 0, self.z_fond, u1, self.D, fz, mat["facade"], {"z+": mat["dalle"]}))
                self.ajoute(bloc(u0, 0, fz + H - DALLE, u1, self.D, top, mat["facade"], {"z-": mat["plafond"]}))
                self.appartement(k, cote, u0, u1, fz)
            else:
                self.ajoute(bloc(u0, 0, self.z_fond, u1, self.D, top, mat["facade"]))
            self.habillage_colonne(k, cote, u0, u1)
        for k in range(self.halls):
            self.cage(k)
        self.toiture()
        self.socle()
        return self

    # --- facades -------------------------------------------------------------
    def fenetre(self, u0, u1, z0, z1, avant, volet=False):
        """Fenetre decor collee sur la facade avant (v=0) ou arriere (v=D)."""
        m = self.mat
        if avant:
            self.ajoute(bloc(u0, -2, z0, u1, 0, z1, m["fenetre"]))
            self.ajoute(bloc(u0 - 4, -6, z0 - 6, u1 + 4, 0, z0, m["appui"]))
            if volet:
                self.ajoute(bloc(u0 - 4, -6, z1, u1 + 4, 0, z1 + 14, m["volet"]))
        else:
            self.ajoute(bloc(u0, self.D, z0, u1, self.D + 2, z1, m["fenetre"]))
            self.ajoute(bloc(u0 - 4, self.D, z0 - 6, u1 + 4, self.D + 6, z0, m["appui"]))
            if volet:
                self.ajoute(bloc(u0 - 4, self.D, z1, u1 + 4, self.D + 6, z1 + 14, m["volet"]))

    def habillage_colonne(self, k, cote, u0, u1):
        m, w = self.mat, u1 - u0
        ouvert = (k, cote) == (self.appart[0], self.appart[2])
        bout = u0 == 0 or abs(u1 - self.L) < 1
        for niv in range(self.N):
            z = niv * H
            if niv == 0:
                if self.style == "beige":
                    # garages au rez-de-chaussee cote halls, soupiraux a l'arriere
                    nb = max(1, int(w // 144))
                    for i in range(nb):
                        g0 = u0 + (w - nb * 128) / 2 + i * 128 + 8
                        self.ajoute(bloc(g0, -5, 0, g0 + 112, 0, 100, m["garage"]))
                    self.fenetre(u0 + w * 0.3, u0 + w * 0.3 + 48, 56, 80, avant=False)
                else:
                    self.fenetre(u0 + w * 0.25, u0 + w * 0.25 + 64, 48, 96, avant=True)
                    self.fenetre(u0 + w * 0.6, u0 + w * 0.6 + 64, 48, 96, avant=False)
                continue
            if ouvert and niv == self.appart[1]:
                continue  # vraies ouvertures, faites par appartement()
            # facade cote halls
            if self.style == "beige":
                # loggia sombre + bande de panneaux bruns + fenetres
                lo0, lo1 = u0 + w * 0.06, u0 + w * 0.40
                self.ajoute(bloc(lo0, -3, z + 4, lo1, 0, z + 120, m["loggia"]))
                self.ajoute(bloc(lo0, -40, z, lo1, -3, z + 8, m["dalle_balcon"]))
                self.ajoute(bloc(lo0, -40, z + 8, lo1, -36, z + 46, m["garde_corps"]))
                for f in (lo0 - 8, lo1):
                    self.ajoute(bloc(f, -40, z, f + 8, 0, z + 136, m["facade"]))
                self.ajoute(bloc(u0 + w * 0.44, -3, z + 16, u0 + w * 0.60, 0, z + 128, m["panneau"]))
                self.fenetre(u0 + w * 0.66, u0 + w * 0.78, z + 40, z + 112, avant=True)
                self.fenetre(u0 + w * 0.82, u0 + w * 0.94, z + 40, z + 112, avant=True)
            else:
                self.fenetre(u0 + w * 0.15, u0 + w * 0.35, z + 40, z + 112, avant=True, volet=True)
                self.fenetre(u0 + w * 0.60, u0 + w * 0.80, z + 40, z + 112, avant=True, volet=True)
            # facade arriere
            if self.style == "beige":
                # balcons filants : dalle + garde-corps + separations entre logements
                self.ajoute(bloc(u0, self.D, z - DALLE, u1, self.D + 72, z, m["dalle_balcon"]))
                self.ajoute(bloc(u0, self.D + 68, z, u1, self.D + 72, z + 44, m["garde_corps"]))
                self.ajoute(bloc(u1 - 4, self.D, z, u1, self.D + 72, z + 112, m["facade"]))
                self.fenetre(u0 + w * 0.10, u0 + w * 0.42, z + 4, z + 116, avant=False)
                self.fenetre(u0 + w * 0.58, u0 + w * 0.88, z + 40, z + 116, avant=False)
            else:
                # balcons en saillie, decales d'un etage a l'autre comme sur les photos
                b0 = u0 + (w * 0.12 if niv % 2 else w * 0.52)
                self.ajoute(bloc(b0, self.D, z - DALLE, b0 + 136, self.D + 64, z, m["dalle_balcon"]))
                self.ajoute(bloc(b0, self.D + 56, z, b0 + 136, self.D + 64, z + 28, m["balcon"]))
                self.ajoute(bloc(b0, self.D + 60, z + 28, b0 + 136, self.D + 64, z + 44, m["garde_corps"]))
                self.ajoute(bloc(b0 + 16, self.D, z + 4, b0 + 120, self.D + 2, z + 116, m["fenetre"]))
                f0 = u0 + (w * 0.62 if niv % 2 else w * 0.15)
                self.fenetre(f0, f0 + 72, z + 40, z + 112, avant=False, volet=True)
            # pignon : petites fenetres
            if bout:
                for vv in (self.D * 0.3, self.D * 0.6):
                    if u0 == 0:
                        self.ajoute(bloc(-2, vv, z + 48, 0, vv + 56, z + 104, m["fenetre"]))
                    else:
                        self.ajoute(bloc(self.L, vv, z + 48, self.L + 2, vv + 56, z + 104, m["fenetre"]))

    def socle(self):
        m = self.mat
        # le socle s'interrompt devant chaque entree de hall
        entrees = []
        for k in range(self.halls):
            _, c0, c1, _ = self.section(k)
            mid = c0 + (c1 - c0) / 2
            entrees.append((mid - 104, mid + 104, -48, 24))
        for a, c, za, zb in morceaux(-3, self.L + 3, -48, 24, entrees):
            self.ajoute(bloc(a, -3, za, c, 0, zb, m["socle"]))
        self.ajoute(bloc(-3, self.D, -48, self.L + 3, self.D + 3, 24, m["socle"]))
        self.ajoute(bloc(-3, 0, -48, 0, self.D, 24, m["socle"]))
        self.ajoute(bloc(self.L, 0, -48, self.L + 3, self.D, 24, m["socle"]))

    def toiture(self):
        m = self.mat
        top = self.N * H
        debord = 40
        planes, z_faitage = toit_deux_pans(-debord, -debord, self.L + debord, self.D + debord, top,
                                           24 if self.style == "beige" else 18, m["toit"])
        self.ajoute(planes)
        # bandeau de rive sous le debord
        self.ajoute(bloc(-debord, -debord, top - 12, self.L + debord, 0, top, m["rive"]))
        self.ajoute(bloc(-debord, self.D, top - 12, self.L + debord, self.D + debord, top, m["rive"]))
        # cheminees le long du faitage
        nb = max(4, int(self.L // 300))
        vm = self.D / 2
        for i in range(nb):
            u = self.L * (i + 0.5) / nb
            self.ajoute(bloc(u - 22, vm - 18, z_faitage - 40, u + 22, vm + 18, z_faitage + 56, m["cheminee"]))
            self.ajoute(bloc(u - 26, vm - 22, z_faitage + 56, u + 26, vm + 22, z_faitage + 62, m["appui"]))
        self.z_faitage = z_faitage

    # --- cage d'escalier ----------------------------------------------------
    def cage(self, k):
        m = self.mat
        u0, c0, c1, u1 = self.section(k)
        top = self.N * H
        B = c1 - c0
        asc = self.ascenseur == k
        S = lambda s: c0 + s  # noqa: E731  position dans la cage -> u

        # fondation et dalle du rez-de-chaussee
        self.ajoute(bloc(c0, 0, self.z_fond, c1, self.D, 0, m["facade"], {"z+": m["hall_sol"]}))
        # fond de la cage : plein
        self.ajoute(bloc(c0, FOND_CAGE, 0, c1, self.D, top, m["facade"], {"v-": m["hall_mur"]}))
        # plafond sous toiture
        self.ajoute(bloc(c0, MUR, top - DALLE, c1, FOND_CAGE, top, m["facade"], {"z-": m["plafond"]}))

        # facade cote hall : porte d'entree au rez, fenetres de palier aux etages
        ouv = [(S(B / 2 - 56), S(B / 2 + 56), 0, 120)]
        for niv in range(1, self.N):
            ouv.append((S(24), S(B - 24) if not asc else S(200), niv * H + 40, niv * H + 104))
        faces_mur = {"v+": m["hall_mur"], "v-": m["facade"]}
        self.ajoute(mur_perce("u", c0, c1, 0, MUR, 0, top - DALLE, ouv, m["facade"], faces_mur))
        for niv in range(1, self.N):
            self.ajoute(bloc(S(24), 6, niv * H + 40, S(B - 24) if not asc else S(200), 10, niv * H + 104, m["vitre"]))
        # auvent + parois vitrees de l'entree
        self.ajoute(bloc(S(B / 2 - 104), -112, 124, S(B / 2 + 104), 0, 136, m["auvent"]))
        for s in (B / 2 - 104, B / 2 + 100):
            self.ajoute(bloc(S(s), -112, 0, S(s + 4), -8, 124, m["vitre"]))
        self.ajoute(bloc(S(B / 2 - 104), -112, 0, S(B / 2 - 56), -108, 124, m["vitre"]))
        self.ajoute(bloc(S(B / 2 + 56), -112, 0, S(B / 2 + 104), -108, 124, m["vitre"]))
        self.ajoute(bloc(S(B / 2 - 104), -112, -8, S(B / 2 + 104), 0, 0, m["hall_sol"]))

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
            # main courante le long du mur central
            for s0 in (VOLEE_A[1] - 4, VOLEE_B[0]):
                self.ajoute(bloc(S(s0), PALIER, z + 36, S(s0 + 4), PALIER + VOLEE, z + 40 + H / 2, m["rampe"]))

        # portes d'appartement sur chaque palier (fermees), boites aux lettres au rez
        for niv in range(1, self.N):
            z = niv * H
            for cote in (-1, 1):
                ouverte = (k, niv, cote) == self.appart
                if ouverte:
                    continue
                if cote < 0:
                    self.ajoute(bloc(c0, 48, z, c0 + 3, 112, z + 112, m["porte"]))
                else:
                    self.ajoute(bloc(c1 - 3, 48, z, c1, 112, z + 112, m["porte"]))
            self.lumiere(c0 + B / 2, PALIER / 2 + 16, z + H - 24, rayon=280)
        self.ajoute(bloc(c0, 120, 40, c0 + 6, 168, 104, m["boites"]))
        self.lumiere(c0 + B / 2, 96, H - 24, rayon=300)
        self.lumiere(c0 + B / 2, -60, 116, rayon=200)

        if asc:
            self.ascenseur_cage(c0)

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
        # cuvette
        self.ajoute(bloc(s0 + 8, v0 + 8, -40, s1 - 8, v1 - 8, -24, m["gaine"]))
        self.gaine = (s0, s1, v0, v1)

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
                out.append([(self.dir_monde(n[0], n[1]) + (n[2],), self.monde(*p), mat) for n, p, mat in b])
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
        """Appartement traversant creuse dans la colonne, porte sur le palier du hall k."""
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
        # murs : cote cage (avec porte), cote voisin / pignon, facades avec vraies ouvertures
        porte = (48, 112)
        for (va, vb) in ((MUR, porte[0]), (porte[1], D - MUR)):
            self.ajoute(b(0, va, z0, CLOISON, vb, z1, mur_app, {"u-": m["hall_mur"]}))
        self.ajoute(b(0, porte[0], z0 + 112, CLOISON, porte[1], z1, mur_app, {"u-": m["hall_mur"]}))
        pignon = u0 == 0 or abs(u1 - self.L) < 1
        ep = MUR if pignon else CLOISON
        self.ajoute(b(W - ep, MUR, z0, W, D - MUR, z1, mur_app, {"u+": m["facade"]}))
        if pignon:
            self.ajoute(b(W - ep - 0.01, D * 0.30, z0 + 40, W, D * 0.30 + 72, z0 + 104, m["vitre"]))

        # plan : entree, cuisine (facade halls), sdb, chambre 1, sejour + chambre 2 (facade arriere)
        xc = 136                          # cuisine a partir de x
        xcl = 112                         # mur du couloir
        v_cuis = round(D * 0.30 / 8) * 8  # fond de cuisine
        v_sdb = round(D * 0.47 / 8) * 8
        v_sej = round(D * 0.64 / 8) * 8
        xs = round(W * 0.58 / 8) * 8      # separation sejour / chambre 2
        fa, fb = sorted((X(0), X(W)))     # facades sur toute la largeur de la colonne

        # facade cote halls : fenetres de la cuisine et de la chambre-cuisine
        ouv_av = [(X(xc + 24), X(xc + 120)), (X(W - 112), X(W - 24))]
        ouv_av = [(min(a, c), max(a, c), z0 + 40, z0 + 112) for a, c in ouv_av]
        self.ajoute(mur_perce("u", fa, fb, 0, MUR, z0, z1, ouv_av, m["facade"], {"v+": mur_app}))
        for a, c, za, zb in ouv_av:
            self.ajoute(bloc(a, 6, za, c, 10, zb, m["vitre"]))
            self.ajoute(bloc(a - 4, -6, za - 6, c + 4, 0, za, m["appui"]))
        # facade arriere : porte-fenetre du sejour (ouverte sur le balcon) + fenetre chambre 2
        pf = sorted((X(40), X(xs - 40)))
        fc = sorted((X(xs + 40), X(W - 48)))
        ouv_ar = [(pf[0], pf[1], z0, z0 + 116), (fc[0], fc[1], z0 + 40, z0 + 112)]
        self.ajoute(mur_perce("u", fa, fb, D - MUR, D, z0, z1, ouv_ar, m["facade"], {"v-": mur_app}))
        self.ajoute(bloc(fc[0], D - 10, z0 + 40, fc[1], D - 6, z0 + 112, m["vitre"]))
        # balcon prive devant la porte-fenetre
        self.ajoute(bloc(pf[0] - 32, D, z0 - DALLE, pf[1] + 32, D + 96, z0, m["dalle_balcon"]))
        self.ajoute(bloc(pf[0] - 32, D + 92, z0, pf[1] + 32, D + 96, z0 + 44, m["garde_corps"]))
        for x in (pf[0] - 32, pf[1] + 28):
            self.ajoute(bloc(x, D, z0, x + 4, D + 96, z0 + 44, m["garde_corps"]))

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
