"""Ecrit docs/references/materiaux-disponibles.md a partir des donnees de inventaire_materiaux.py."""

import datetime

ORDRE_RANG = {"recommandé": 0, "alternative": 1, "limité": 2, "à éviter": 3}
ETOILES = {1: "1/5", 2: "2/5", 3: "3/5", 4: "4/5", 5: "5/5"}


def _c(txt):
    return str(txt).replace("|", "/").replace("\n", " ")


def _fmt_m(v):
    return ("%.2f" % v).replace(".", ",")


def _cellule_materiau(c):
    if not c.get("verifie", False):
        return "`%s`<br>**NON TROUVÉ dans les GDT**" % c["nom"]
    gdt = c.get("gdt", "").replace("texture_assets/", "ta/").replace("art_assets/t6_legacy/texture_assets/", "t6/").replace("model_export/", "me/")
    extra = ""
    if c.get("parent"):
        extra = "<br>instance de `%s`" % c["parent"]
    return "`%s`<br><sub>%s</sub>%s" % (c["nom"], gdt, extra)


def _cellule_image(c):
    ci = c.get("colorMap")
    if not ci:
        return "aucune"
    if ci.get("code"):
        return "`%s` (couleur uniforme)" % ci["image"]
    s = "`%s`" % ci["image"]
    d = ci.get("dimensions")
    if d:
        s += "<br>%d × %d px" % (d[0], d[1])
    if not ci.get("existe"):
        s += "<br>**image absente**"
    a = (c.get("analyse") or {}).get("alpha")
    mt_ = (c.get("materialType") or "") + " " + (c.get("usage") or "")
    if a and a.get("utile") and any(k in mt_ for k in ("alpha", "transpar", "glass", "decal", "reveal", "foliage", "backlit")):
        if a["max"] - a["min"] <= 3:
            s += "<br>alpha uniforme (%d)" % a["min"]
        elif a["part_sous_128"] >= 0.96:
            s += "<br>alpha faible partout (%d à %d)" % (a["min"], a["max"])
        elif a["part_sous_128"] >= 0.04:
            s += "<br>alpha : %d %% des pixels sous 50 %%" % round(100 * a["part_sous_128"])
    return s


def _cellule_teinte(c):
    an = c.get("analyse") or {}
    col = an.get("couleur_moyenne")
    s = "`%s`" % col if col else "n/m"
    t = c.get("colorTint")
    if c.get("parent") and t and t.split()[:3] not in (["1", "1", "1"], ["1.000000", "1.000000", "1.000000"]):
        s += "<br><sub>teinte ×(%s)</sub>" % " ".join(t.split()[:3])
    return s


def _cellule_echelle(c):
    e = c.get("echelle_map") or {}
    if not e or e.get("valeur") == "inconnue":
        return "n/m"
    val = e["valeur"].replace(" x ", " × ")
    src = e.get("source")
    detail = e.get("detail", "")
    faces = detail.split(" : ")[-1] if src == "stock_variante" else detail
    if src == "stock":
        s = "%s<br><sub>stock : %s</sub>" % (val, faces.replace(" dans les .map officiels", ""))
    elif src == "stock_variante":
        s = "%s<br><sub>stock de la variante `%s` : %s</sub>" % (val, detail.split("(")[-1].split(")")[0], faces)
    else:
        s = "%s<br><sub>estimée, à régler à l'œil</sub>" % val
    p = e.get("unites_projet_x1_25")
    if p and src in ("stock", "stock_variante"):
        s += "<br><sub>projet ×1,25 : %s × %s</sub>" % (("%g" % p[0]).replace(".", ","), ("%g" % p[1]).replace(".", ","))
    return s


def _cellule_avis(c):
    s = _c(c.get("avis", ""))
    r = c.get("reserves")
    if r:
        s += " **Réserve :** " + _c(r)
    an = c.get("analyse") or {}
    flags = []
    if an.get("raccord_douteux"):
        flags.append("raccord des bords douteux (mesuré)")
    if c.get("images_manquantes"):
        flags.append("images liées absentes : " + ", ".join(c["images_manquantes"]))
    if c.get("doNotUse"):
        flags.append("drapeau doNotUse (hérité)")
    if (c.get("usage") or "") == "<not in editor>":
        flags.append("usage « not in editor » (non listé dans Radiant)")
    if flags:
        s += " <sub>[" + " ; ".join(flags) + "]</sub>"
    return s


def _tableau_materiaux(cands):
    lignes = ["| Rang | Matériau | Image couleur | Teinte moy. | Échelle .map | Avis |", "|---|---|---|---|---|---|"]
    for c in sorted(cands, key=lambda x: ORDRE_RANG.get(x["rang"], 9)):
        lignes.append("| %s (%s) | %s | %s | %s | %s | %s |" % (
            c["rang"], ETOILES.get(c["note"], "?"), _cellule_materiau(c), _cellule_image(c), _cellule_teinte(c), _cellule_echelle(c), _cellule_avis(c)))
    return "\n".join(lignes)


def _tableau_modeles(cands):
    lignes = ["| Rang | Modèle | Taille mesurée L × l × H (m) | Sommets LOD0 | Type · LOD | Avis |", "|---|---|---|---|---|---|"]
    for c in sorted(cands, key=lambda x: ORDRE_RANG.get(x["rang"], 9)):
        if not c.get("verifie", False):
            lignes.append("| %s | `%s` | **NON TROUVÉ** | | | %s |" % (c["rang"], c["nom"], _c(c.get("avis", ""))))
            continue
        d = c.get("dimensions_m")
        dim = " × ".join(_fmt_m(v) for v in d) if d else "n/m"
        nv = (c.get("boite") or {}).get("sommets_lod0", "n/m")
        gdt = c.get("gdt", "").replace("model_export/", "me/")
        parent = "<br>instance de `%s`" % c["parent"] if c.get("parent") else ""
        lignes.append("| %s (%s) | `%s`<br><sub>%s</sub>%s | %s | %s | %s · %s autre(s) LOD | %s |" % (
            c["rang"], ETOILES.get(c["note"], "?"), c["nom"], gdt, parent, dim, nv, c.get("type") or "?", c.get("lod_autres_presents", 0), _cellule_avis(c)))
    return "\n".join(lignes)


def ecrire_md(d, SP):
    m = d["meta"]
    L = []
    a = L.append
    a("# Matériaux et modèles disponibles dans les Mod Tools BO3")
    a("")
    a("Inventaire en **lecture seule** de `%s` pour la map zm_seyssel : quels matériaux et quels modèles existent vraiment, "
      "lesquels choisir pour chaque besoin du quartier, et ce qu'il faut remplacer dans le dictionnaire `MAT` de `tools/quartier.py`." % m["mod_tools"].replace("\\", "/"))
    a("")
    a("> Généré le %s par `tools/inventaire_materiaux.py` (contenu éditorial dans `tools/inventaire_materiaux_spec.py`). "
      "Les mêmes données, sous forme exploitable par un script, sont dans `reference/materiaux.json`. "
      "Un candidat n'est marqué « vérifié » que si son nom exact est l'en-tête d'une entrée d'un `.gdt` (recherche textuelle indépendante de l'analyse)." % m["genere_le"])
    a("")
    a("Degré de certitude : **vu** = lu dans un GDT, mesuré sur le fichier ou regardé dans un aperçu PNG ; **déduit** = conclu d'indices (noms, valeurs) sans l'avoir vu tourner dans le jeu ; **inconnu** = non vérifiable ici (rendu moteur, couleur réelle du bâti).")
    a("")
    a("## 1. À retenir")
    a("")
    for i, c in enumerate(d["constats"], 1):
        a("%d. %s" % (i, c))
    a("")
    a("## 2. Actions prioritaires pour la suite")
    a("")
    for i, c in enumerate(d["priorites"], 1):
        a("%d. %s" % (i, c))
    a("")
    a("## 3. Choix recommandés en un coup d'œil")
    a("")
    a("| Besoin | Actuel dans `MAT` | Recommandé | Alternatives utiles |")
    a("|---|---|---|---|")
    mat = d["mat_projet"]
    for b in d["besoins_materiaux"]:
        rec = [c["nom"] for c in b["candidats"] if c["rang"] == "recommandé"]
        alt = [c["nom"] for c in b["candidats"] if c["rang"] == "alternative"][:3]
        act = ", ".join("`%s` → `%s`" % (k, mat[k]["nom"]) for k in b.get("mat_projet", []) if k in mat) or "(non utilisé)"
        a("| %s | %s | %s | %s |" % (b["titre"], act, ", ".join("`%s`" % n for n in rec) or "voir §6", ", ".join("`%s`" % n for n in alt) or "-"))
    a("")
    a("Modèles :")
    a("")
    a("| Besoin | Recommandé | Remarque |")
    a("|---|---|---|")
    for b in d["besoins_modeles"]:
        rec = [c["nom"] for c in b["candidats"] if c["rang"] == "recommandé"]
        a("| %s | %s | %s |" % (b["titre"], ", ".join("`%s`" % n for n in rec) or "aucun modèle adapté", _c(b["resume"].split(". ")[0].rstrip(".") + ".")))
    a("")
    a("## 4. Où sont les matériaux (et où ils ne sont pas)")
    a("")
    a("| Dossier | Fichiers .gdt | Matériaux | Images | Modèles | Autres entrées (instances, sons, armes…) |")
    a("|---|---|---|---|---|---|")
    for z in d["zones_gdt"]:
        a("| `%s` | %d | %d | %d | %d | %d |" % (z["zone"], z["fichiers"], z["materiaux"], z["images"], z["modeles"], z["instances_ou_autres"]))
    a("")
    a("Total lu : %d fichiers, %d entrées dont %d instances `\"nom\" [ \"parent\" ]` (comptées avec le type de leur parent). "
      "Matériaux distincts : %d ; images : %d ; modèles : %d. La dernière colonne regroupe les autres types : sons, armes, animations, brouillards, personnages…" %
      (m["gdt_lus"], m["entrees"], m["instances"], m["materiaux_definis"], m["images_definies"], m["modeles_definis"]))
    a("")
    a("## 5. Lire les tableaux")
    a("")
    a("- **Matériau** : nom exact à écrire dans le `.map`. Les instances sont signalées (« instance de ») : elles reprennent le parent et ne changent que quelques valeurs, surtout `colorTint` (multiplie la couleur de l'image).")
    a("- **Teinte moy.** : couleur moyenne de l'image après `colorTint`, mesurée sur le fichier (pixels visibles seulement pour les cartes à alpha). Ce n'est pas la couleur affichée en jeu (lumière, spéculaire et exposition la modifient) ; elle sert à comparer.")
    a("- **Échelle .map** : taille en unités de monde d'une répétition (les deux nombres après le nom du matériau dans le `.map`). « stock » = valeur la plus fréquente dans les .map officiels (%d fichiers lus) ; « estimée » = proportions de l'image sur 64 unités (à régler à l'œil). "
      "La ligne « projet ×1,25 » tient compte de `ECHELLE` (geo.py)." % m["maps_officielles_lues_pour_les_echelles"])
    a("- **Suffixes** (déduits des GDT) : `_wet` = carte de normales mouillée et gloss plus élevé (aspect mouillé) ; `_blend` / `_reveal` = matériaux de fusion pour décalques et terrain ; `_nw` = variante dont le sens exact n'est pas documenté ; `_dark`, `_grey`, `_tan`, `_warm` = instances teintées.")
    a("- **Drapeaux** : `doNotUse` (matériaux core_* hérités, mais compilés sans erreur dans zm_seyssel) ; `usage = <not in editor>` (matériaux mtl_* de modèles, non listés dans Radiant) ; types `lit_alphatest*` (grillages : le canal alpha est présent, mesuré).")
    a("")
    a("### Échelles de référence relevées dans les .map officiels")
    a("")
    a("| Matériau | Échelle la plus fréquente | Faces | Image |")
    a("|---|---|---|---|")
    for e in d.get("echelles_reference", []):
        a("| `%s` | %s | %s | %s |" % (e["nom"], e["echelle"], e["faces"], e["image"]))
    a("")
    a("## 6. Matériaux par besoin")
    a("")
    famille = None
    for b in d["besoins_materiaux"]:
        if b["famille"] != famille:
            famille = b["famille"]
            a("### %s" % famille)
            a("")
        a("#### %s" % b["titre"])
        a("")
        if b.get("mat_projet"):
            a("Utilisé aujourd'hui : " + ", ".join("`%s` → `%s`" % (k, mat[k]["nom"]) for k in b["mat_projet"] if k in mat) + ".")
            a("")
        a("**Avis.** " + b["resume"])
        a("")
        a(_tableau_materiaux(b["candidats"]))
        a("")
    a("## 7. Modèles (xmodel)")
    a("")
    a("Les tailles sont mesurées sur les sommets du LOD0 (unité = pouce, soit 2,54 cm). **À `modelscale 1.25`, le modèle garde ces dimensions dans le quartier** (qui est agrandi de 1,25) ; "
      "à `modelscale 1`, il paraît 20 % plus petit que les immeubles. Les modèles déjà utilisés par `quartier.py` sont listés au §7.1.")
    a("")
    for mo in d["besoins_modeles"]:
        a("### %s" % mo["titre"])
        a("")
        a("**Avis.** " + mo["resume"])
        a("")
        a(_tableau_modeles(mo["candidats"]))
        a("")
    a("### 7.1 Modèles déjà utilisés dans le projet")
    a("")
    a("| Modèle | Vérifié | Taille mesurée (m) | Sommets LOD0 |")
    a("|---|---|---|---|")
    for n, f in d["modeles_deja_utilises_dans_le_projet"].items():
        dim = " × ".join(_fmt_m(v) for v in f["dimensions_m"]) if f.get("dimensions_m") else "n/m"
        a("| `%s` | %s | %s | %s |" % (n, "oui" if f.get("verifie") else "**NON**", dim, (f.get("boite") or {}).get("sommets_lod0", "n/m")))
    a("")
    a("## 8. Ce qui manque ou n'est pas vérifiable")
    a("")
    for x in d["limites_et_manques"]:
        a("- " + x)
    a("")
    a("## 9. Remplacements à faire dans `MAT` (`tools/quartier.py`)")
    a("")
    a("Statuts : **garder** (le matériau actuel est bon), **ajuster** (bon matériau mais échelle, variante ou usage à corriger), **remplacer**.")
    a("")
    a("| Clé | Actuel | Statut | Proposé | Alternative | Pourquoi |")
    a("|---|---|---|---|---|---|")
    for r in d["remplacements_mat"]:
        act = "`%s`" % r["actuel"] if r["actuel"] else "(clé absente de MAT)"
        if r["actuel"] and not r["actuel_verifie"]:
            act += " **NON TROUVÉ**"
        par = "`%s`" % r["remplacer_par"] if r["remplacer_par"] else "-"
        if r["remplacer_par"] and r.get("remplacer_par_verifie") is False:
            par += " **NON TROUVÉ**"
        alt = "`%s`" % r["alternative"] if r["alternative"] else "-"
        if r["alternative"] and r.get("alternative_type") == "modele":
            alt += " (modèle)"
        if r["alternative"] and r.get("alternative_verifie") is False:
            alt += " **NON TROUVÉ**"
        a("| `%s` | %s | **%s** | %s | %s | %s |" % (r["cle"], act, r["statut"], par, alt, _c(r["pourquoi"])))
    a("")
    if d["cles_mat_sans_avis"]:
        a("Clés de `MAT` sans avis (ajoutées depuis la dernière mise à jour de ce document) : " + ", ".join("`%s`" % k for k in d["cles_mat_sans_avis"]) + ".")
        a("")
    ok = sum(1 for v in mat.values() if v["verifie"])
    img = sum(1 for v in mat.values() if v["image_couleur_presente"])
    a("Sur %d noms de `MAT`, %d existent dans les GDT (instances résolues) et %d ont leur image couleur sur disque." % (len(mat), ok, img))
    a("")
    a("## 10. Matériaux à créer : instances teintées (propositions, non testées)")
    a("")
    a("Treyarch obtient ses variantes de couleur avec des instances (`t7_plaster_smooth_light_01_grey`, `t7_drywall_painted_beige_01`, `t7_ceramic_tile_shower_red`…). On peut faire de même dans un GDT à nous :")
    a("")
    a("```")
    for p in d["instances_a_creer"]:
        if p["statut"].startswith("inutile"):
            continue
        a('"%s" [ "%s" ]' % (p["nom"], p["parent"]))
        a("{")
        a('\t"colorTint" "%s"' % p["colorTint"])
        a("}")
    a("```")
    a("")
    for p in d["instances_a_creer"]:
        a("- `%s` (parent `%s`, teinte `%s`) : %s Statut : %s." % (p["nom"], p["parent"], p["colorTint"], p["objectif"], p["statut"]))
    a("")
    a("Réserves : (1) la syntaxe est celle des GDT officiels (vue dans t7_plaster.gdt, lignes 7196 à 7277) mais **aucune instance n'a été compilée ici** ; "
      "(2) un fichier GDT à nous devrait vivre dans `source_data\\` ou `texture_assets\\` des Mod Tools ; `tools/sync.ps1` ne copie aujourd'hui que `map_source\\_prefabs\\zm_seyssel`, `usermaps\\zm_seyssel` et `map_source\\zm\\zm_seyssel.map`, "
      "il faudrait donc l'étendre ; (3) la teinte exacte se juge en jeu, pas sur l'image.")
    a("")
    a("## 11. Aperçus")
    a("")
    a("Dossier `_build/mat_preview/` (ignoré par git) : un PNG de 512 px maximum par matériau analysé (`<nom>.png`, teinte appliquée ; les cartes à alpha sont montrées sur damier), "
      "des planches contact `planche_cles_*.png` (chaque texture répétée 2 × 2 pour juger les raccords) et des silhouettes de modèles dans `modeles/` (nuage de sommets vu de face et de côté : indicatif, les modèles très plats y paraissent vides).")
    a("")
    a("Matériaux clés regardés pour cet avis : " + ", ".join("`%s`" % n for n in SP.APERCUS_CLES) + ".")
    a("")
    a("## 12. Reproduire")
    a("")
    a("```powershell")
    a('python tools\\inventaire_materiaux.py                 # JSON + Markdown + aperçus')
    a('python tools\\inventaire_materiaux.py --sans-apercus  # JSON + Markdown seulement')
    a("```")
    a("")
    a("Dépendances : Pillow, numpy, OpenCV (outil d'aperçu uniquement ; `build_map.py` reste en bibliothèque standard).")
    a("")
    return "\n".join(L)
