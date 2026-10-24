"""Fabrique la map jouable zm_seyssel a partir du modele zombies des Mod Tools.

    - quartier.py construit le terrain, la voirie, les trois immeubles, la vegetation
      -> prefabs _prefabs/zm_seyssel/quartier.map et batiment_1..3.map
    - le contenu de la salle de test du modele (spawn, atouts, Box, Pack-a-Punch,
      courant) est pose sur le parking du haut, face au batiment 1, comme la photo 1
    - le ciel, le soleil et les volumes sont agrandis au quartier et a ses montagnes
    - l'ascenseur du batiment 1 (entites scriptees) est ecrit dans la map principale

Usage :
    python tools/build_map.py ["<dossier des Mod Tools>"]
"""

import math
import re
import shutil
import sys
from pathlib import Path

from geo import ROOT
from make_blockout import box, brush_lines, brush_lines_mat, check_brush, new_guid, reset_guids
from quartier import Quartier

TOOLS = Path(r"D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130")
MAP = "zm_seyssel"
MAX_BRUSHES = 1800  # brushes par prefab (fichiers de moins de 2 Mo)
GAME = ROOT / "game"
PREFABS = GAME / "map_source" / "_prefabs" / MAP

# Le contenu de la salle de test est tourne de 90 degres puis pose sur le parking du haut
ROTATION = 90
DECALAGE = (2487, -12)

# Entites du modele qu'on ne reprend pas : la barricade colle a un mur de la salle de test
SANS = {"_prefabs/zm/zm_core/barricade_reciever_wood.map",
        "_prefabs/zm/zm_core/spawnable_weapon_shotgun_pump.map"}  # le fusil est remis sur le mur d'armes

# Cameras de fin de partie : le batiment 1 vu du parking du haut, et le quartier vu du nord-ouest
INTERMISSION = {
    "intermission": ("3300 -200 420", "6 180 0"),
    "intermission_b": ("-2600 5200 1500", "18 305 0"),
}

# Points ou les zombies sortent du sol, en plus de ceux du modele (pelouses, cour, abords)
SORTIES_ZOMBIES = [(-1000, 0), (-1000, -2000), (-1000, 2000), (300, 2600), (1300, 3700), (3000, 3500),
                   (4300, 2800), (3300, -1500), (1200, -2600), (-2500, 3900), (-300, -3200), (4500, 5200),
                   (2000, -4500), (5200, 800), (1500, 5300), (-3000, 3000), (-3800, -3000), (5200, -3500)]

# Rendu : ciel, soleil, etalonnage
RENDU = {
    "skyboxmodel": "skybox_default_day",
    "ssi": "default_day",
    "wsi": "default_day",
    "lutmaterial": "luts_t7_default",
    "lightingquality": "1024",
}


def fmt(v):
    return f"{round(v, 2):g}"


def parse(text):
    """Decoupe un .map en (en-tete, [entites]) ; une entite = (cle/valeurs, nombre de brushes, calque)."""
    parts = re.split(r"^// entity \d+\r?$", text, flags=re.M)
    head, ents = parts[0], []
    for part in parts[1:]:
        body = part.strip()
        kv = re.findall(r'^"([^"]+)" "([^"]*)"\r?$', body, flags=re.M)
        # Le calque compte : "000_Global/No Comp" exclut l'entite de la compilation
        layer = re.search(r'^layer "([^"]*)"\r?$', body.split("// brush")[0], flags=re.M)
        ents.append((kv, body.count("// brush"), layer.group(1) if layer else None))
    return head.rstrip(), ents


def entity_lines(index, kv, brushes=(), layer=None, brushes_mat=()):
    lines = [f"// entity {index}", "{", f'guid "{new_guid()}"']
    if layer:
        lines.append(f'layer "{layer}"')
    lines += [f'"{k}" "{v}"' for k, v in kv if k != "guid"]
    lines += brush_lines(brushes)
    lines += brush_lines_mat(brushes_mat)
    lines.append("}")
    return lines


def dict_lines(index, e):
    kv = [(k, v) for k, v in e.items() if not k.startswith("_")]
    return entity_lines(index, kv, brushes_mat=e.get("_brushes", ()))


def ecrire(path, lignes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lignes) + "\n", encoding="latin-1", newline="\r\n")


def prefab(path, brushes, entites):
    bad = [i for i, b in enumerate(brushes) if not check_brush(b)]
    if bad:
        raise SystemExit(f"{path.name} : brushes invalides {bad[:10]}")
    reset_guids(path.name)
    lignes = ["iwmap 4", "// entity 0", "{", f'guid "{new_guid()}"', '"classname" "worldspawn"']
    lignes += brush_lines_mat(brushes)
    lignes.append("}")
    for i, e in enumerate(entites, 1):
        lignes += dict_lines(i, e)
    ecrire(path, lignes)


def box_planes(x0, y0, z0, x1, y1, z1):
    from immeuble import bloc
    return bloc(x0, y0, z0, x1, y1, z1, "trigger")


def sonde(x, y, z, rayon=1024):
    return {"classname": "reflection_probe", "origin": f"{fmt(x)} {fmt(y)} {fmt(z)}", "radius": str(rayon),
            "ao_power": "2", "ao_range": "16", "ao_strength": "1", "blend_maxs": "3 3 3", "blend_mins": "3 3 3",
            "box": "1", "client_server": "ClientSide", "debugColor": "1 1 1", "exploderFade": "1",
            "grid_density": "16", "high_detail": "1", "in_play_space": "1", "name": "probe",
            "placement_offset": "72", "size_max": "72 72 72", "size_min": "72 72 72"}


def main(tools=TOOLS):
    tools = Path(tools)
    tpl = tools / "rex" / "templates" / "ZM Mod Level"
    head, ents = parse((tpl / "map_source" / "zm" / "template.map").read_text(encoding="latin-1"))

    q = Quartier().construire()
    import monde
    # zone jouable : cadre du quartier + bande autour du chemin jusqu'au Carrefour
    sp = monde.SPINE
    X0 = min(q.X0, min(p[0] for p in sp) - monde.WP)
    X1 = max(q.X1, max(p[0] for p in sp) + monde.WP)
    Y0 = min(q.Y0, min(p[1] for p in sp) - monde.WP)
    Y1 = max(q.Y1, max(p[1] for p in sp) + monde.WP)
    # monde visible (terrain jusqu'a l'horizon)
    W0, V0, W1, V1 = monde.boite()

    # prefabs : un par groupe de brushes (decoupes en tranches de MAX_BRUSHES) + un par immeuble
    modeles = [e for e in q.entites if e["classname"] == "misc_model"]
    noms_prefabs = []
    for groupe, liste in q.groupes.items():
        for i in range(0, len(liste), MAX_BRUSHES):
            nom = groupe if len(liste) <= MAX_BRUSHES else f"{groupe}_{i // MAX_BRUSHES + 1}"
            prefab(PREFABS / f"{nom}.map", liste[i:i + MAX_BRUSHES], [])
            noms_prefabs.append(nom)
    prefab(PREFABS / "decor.map", [], modeles)
    noms_prefabs.append("decor")
    for imm in q.immeubles:
        prefab(PREFABS / f"{imm.nom}.map", imm.brushes, imm.entites)
        noms_prefabs.append(imm.nom)
    # prefabs d'anciennes versions : on les supprime du depot (ils ne sont plus references)
    for ancien in PREFABS.glob("*.map"):
        if ancien.stem not in noms_prefabs:
            ancien.unlink()

    def place(origin):
        x, y, z = (float(v) for v in origin.split())
        a = math.radians(ROTATION)
        nx = x * math.cos(a) - y * math.sin(a) + DECALAGE[0]
        ny = x * math.sin(a) + y * math.cos(a) + DECALAGE[1]
        return nx, ny, z + q.z(nx, ny)

    def dans_batiment(x, y, marge=24):
        return any(e[0] - marge < x < e[2] + marge and e[1] - marge < y < e[3] + marge for e in q.emprises)

    # volumes du modele, redimensionnes au quartier
    volumes = {
        "info_volume": ("volume", (X0, Y0, -256, X1, Y1, 1600)),
        "volume_sun": ("sun_volume", (W0, V0, -960, W1, V1, 6500)),
        "umbra_volume": ("umbra_volume", (X0 - 512, Y0 - 512, -512, X1 + 512, Y1 + 512, 2200)),
        "volume_fpstool": ("volume_fpstool", (X0, Y0, -256, X1, Y1, 1600)),
    }
    t = 64
    HC = 6600   # plafond du ciel : au-dessus du plus haut relief
    W0, V0, W1, V1 = W0 - 200, V0 - 200, W1 + 200, V1 + 200
    ciel = [
        ("sky", box(W0 - t, V0 - t, -1024 - t, W1 + t, V1 + t, -1024)),
        ("sky", box(W0 - t, V0 - t, HC, W1 + t, V1 + t, HC + t)),
        ("sky", box(W0 - t, V0 - t, -1024, W0, V1 + t, HC)),
        ("sky", box(W1, V0 - t, -1024, W1 + t, V1 + t, HC)),
        ("sky", box(W0, V0 - t, -1024, W1, V0, HC)),
        ("sky", box(W0, V1, -1024, W1, V1 + t, HC)),
    ]

    reset_guids(f"{MAP}.map")
    out, problemes, n = [head], [], 0
    for kv, nb, layer in ents:
        d = dict(kv)
        cls = d.get("classname")
        if d.get("model") in SANS:
            continue
        if cls == "worldspawn":
            kv = [(k, RENDU.get(k, v)) for k, v in kv]
            out += entity_lines(n, kv, ciel, layer)
        elif cls in volumes:
            mat, b = volumes[cls]
            if cls == "volume_sun":
                kv = [(k, "128" if k == "grid_density" else v) for k, v in kv]
            out += entity_lines(n, kv, [(mat, box(*b))], layer)
        else:
            kv = list(kv)
            if cls == "misc_prefab" and "angles" not in d:
                kv.append(("angles", "0 0 0"))  # angle absent = 0 : il doit tourner comme les autres
            for i, (k, v) in enumerate(kv):
                if k == "origin":
                    x, y, z = place(v)
                    kv[i] = (k, f"{fmt(x)} {fmt(y)} {fmt(z)}")
                    if cls != "actor_zm_nuked_basic_01" and "spawner" not in cls and dans_batiment(x, y):
                        problemes.append(f"{cls} {d.get('model', d.get('targetname', ''))} en ({x:.0f}, {y:.0f})")
                elif k == "angles":
                    p, yaw, r = (float(a) for a in v.split())
                    kv[i] = (k, f"{fmt(p)} {fmt((yaw + ROTATION) % 360)} {fmt(r)}")
                elif k == "script_string" and v == "receiver_set_entry_a":
                    kv[i] = (k, "find_flesh")
                elif k == "radius" and cls == "reflection_probe":
                    kv[i] = (k, "1600")
            name = d.get("targetname")
            if name in INTERMISSION and cls == "script_struct":
                origin, angles = INTERMISSION[name]
                kv = [(k, origin if k == "origin" else angles if k == "angles" else v) for k, v in kv]
            out += entity_lines(n, kv, layer=layer)
        n += 1

    supplement = []
    # sorties de zombies dans tout le quartier
    for x, y in SORTIES_ZOMBIES:
        if not q.libre(x, y, 48):
            continue
        supplement.append({"classname": "script_struct", "origin": f"{x} {y} {fmt(q.z(x, y))}",
                           "angles": f"0 {fmt(math.degrees(math.atan2(-y, -x)) % 360)} 0",
                           "script_noteworthy": "riser_location", "script_string": "find_flesh",
                           "targetname": "start_zone_spawners", "_color": "1 0 0"})
    # zone de test : armes au mur, atouts en plus, machine a points
    for arme, x, y, z in q.test["armes"]:
        supplement.append({"classname": "misc_prefab", "model": f"_prefabs/zm/zm_core/spawnable_weapon_{arme}.map",
                           "origin": f"{fmt(x)} {fmt(y)} {fmt(z)}", "angles": "0 0 0"})
    for nom, x, y, z in q.test["atouts"]:
        supplement.append({"classname": "misc_prefab", "model": f"_prefabs/zm/zm_core/{nom}.map",
                           "origin": f"{fmt(x)} {fmt(y)} {fmt(z)}", "angles": "0 90 0",
                           "script_string": "zclassic_perks_start_room"})
    mx, my, mz = q.test["argent"]
    supplement.append({"classname": "trigger_use", "targetname": "bouton_argent", "cursorhint": "HINT_NOICON",
                       "_brushes": [[(n, p, "trigger") for n, p, _ in box_planes(mx - 50, my - 10, mz, mx + 50, my + 80, mz + 110)]]})
    # ascenseur du batiment 1
    for imm in q.immeubles:
        supplement += imm.ascenseur_entites()
    # sondes de reflets : halls, appartements jouables, exterieur
    for imm in q.immeubles:
        for k in range(imm.halls):
            _, c0, c1, _ = imm.section(k)
            supplement.append(sonde(*imm.monde((c0 + c1) / 2, 0, 64), rayon=400))
        supplement.append(sonde(*imm.sonde, rayon=700))
    for x, y in ((600, 0), (-1200, 1500), (1000, 3200), (3000, 3800)):
        supplement.append(sonde(x, y, q.z(x, y) + 160, rayon=2400))
    # prefabs du quartier et des immeubles
    import os
    sans = [x for x in os.environ.get("ZM_SANS", "").split(",") if x]
    for nom in noms_prefabs:
        if any(nom.startswith(x) for x in sans):
            continue
        supplement.append({"classname": "misc_prefab", "model": f"_prefabs/{MAP}/{nom}.map",
                           "origin": "0 0 0", "angles": "0 0 0"})
    for e in supplement:
        out += dict_lines(n, e)
        n += 1

    if problemes:
        raise SystemExit("Entites dans un batiment :\n  " + "\n  ".join(problemes))

    ecrire(GAME / "map_source" / "zm" / f"{MAP}.map", out)

    # Fichiers du dossier usermaps : copie du modele en renommant "template"
    for src in (tpl / "usermaps" / "template").rglob("*"):
        if src.is_dir():
            continue
        rel = Path(str(src.relative_to(tpl / "usermaps" / "template")).replace("template", MAP))
        target = GAME / "usermaps" / MAP / rel
        if target.exists():
            continue  # ne jamais ecraser un script deja modifie
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in (".png",):
            shutil.copy2(src, target)
        else:
            target.write_text(src.read_text(encoding="latin-1").replace("template", MAP), encoding="latin-1")

    nb_imm = sum(len(i.brushes) for i in q.immeubles)
    print(f"{MAP}.map : {n} entites ; quartier {len(q.brushes)} brushes + {len(modeles)} modeles ; "
          f"immeubles {nb_imm} brushes ; {sum(1 for e in q.entites if e['classname'] == 'light')} lumieres")


if __name__ == "__main__":
    main(*sys.argv[1:])
