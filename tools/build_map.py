"""Fabrique la map jouable zm_seyssel a partir du modele zombies des Mod Tools.

Ce que fait le script, comme le bouton "Create New Map" du Launcher :
    - copie le modele "ZM Mod Level" en remplacant "template" par zm_seyssel
puis, en plus :
    - remplace la salle de test par le quartier (prefab site_blockout.map)
    - agrandit le ciel et les volumes (soleil, umbra, zone de depart) au quartier
    - deplace spawn, atouts, Mystery Box, Pack-a-Punch et courant sur le parking
      a l'est du HLM, et verifie qu'aucun ne tombe dans un batiment

Usage :
    python tools/build_map.py ["<dossier des Mod Tools>"]
"""

import math
import re
import shutil
import sys
from pathlib import Path

from make_blockout import (box, brush_lines, build_site, check_brush, dot, new_guid, norm,
                           reset_guids, write_map, OUT as SITE_PREFAB)
from osm_to_plan import ROOT

TOOLS = Path(r"D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130")
MAP = "zm_seyssel"
GAME = ROOT / "game"

# Le contenu de la salle de test est tourne de 90 degres puis pose sur le parking
ROTATION = 90
DECALAGE = (900, -900)

# Entites du modele qu'on ne reprend pas : la barricade colle a un mur de la salle de test
SANS = {"_prefabs/zm/zm_core/barricade_reciever_wood.map"}

# Cameras de fin de partie : vues sur le HLM depuis le parking et depuis l'avenue
INTERMISSION = {
    "intermission": ("1800 -1800 700", "9 135 0"),
    "intermission_b": ("-1500 1600 600", "8 313 0"),
}

CIEL = 4160  # demi-largeur interieure de la boite de ciel
CIEL_BAS, CIEL_HAUT = -128, 2304


def place(origin):
    x, y, z = (float(v) for v in origin.split())
    a = math.radians(ROTATION)
    nx = x * math.cos(a) - y * math.sin(a) + DECALAGE[0]
    ny = x * math.sin(a) + y * math.cos(a) + DECALAGE[1]
    return nx, ny, z


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


def sky_box():
    t, c = 64, CIEL
    return [
        ("sky", box(-c - t, -c - t, CIEL_BAS - t, c + t, c + t, CIEL_BAS)),
        ("sky", box(-c - t, -c - t, CIEL_HAUT, c + t, c + t, CIEL_HAUT + t)),
        ("sky", box(-c - t, -c - t, CIEL_BAS, -c, c + t, CIEL_HAUT)),
        ("sky", box(c, -c - t, CIEL_BAS, c + t, c + t, CIEL_HAUT)),
        ("sky", box(-c, -c - t, CIEL_BAS, c, -c, CIEL_HAUT)),
        ("sky", box(-c, c, CIEL_BAS, c, c + t, CIEL_HAUT)),
    ]


# Volumes du modele, redimensionnes au quartier
VOLUMES = {
    "info_volume": ("volume", (-1400, -2600, 0, 2600, 2600, 1024)),
    "volume_sun": ("sun_volume", (-CIEL, -CIEL, -64, CIEL, CIEL, CIEL_HAUT - 64)),
    "umbra_volume": ("umbra_volume", (-CIEL, -CIEL, -256, CIEL, CIEL, 1600)),
    "volume_fpstool": ("volume_fpstool", (-4096, -4096, -64, 4096, 4096, 1024)),
}


def entity_lines(index, kv, brushes=(), layer=None):
    lines = [f"// entity {index}", "{", f'guid "{new_guid()}"']
    if layer:
        lines.append(f'layer "{layer}"')
    lines += [f'"{k}" "{v}"' for k, v in kv if k != "guid"]
    lines += brush_lines(brushes)
    lines.append("}")
    return lines


def main(tools=TOOLS):
    tools = Path(tools)
    tpl = tools / "rex" / "templates" / "ZM Mod Level"
    head, ents = parse((tpl / "map_source" / "zm" / "template.map").read_text(encoding="latin-1"))

    site, _, _ = build_site()
    write_map(site, SITE_PREFAB)
    solides = [p for cat, p in site if cat in ("mur", "toit", "cheminee", "annexe", "voisin")]
    solides = [[(norm(n), dot(norm(n), pt)) for n, pt in planes] for planes in solides]

    def dans_batiment(x, y, z, marge=24):
        for planes in solides:
            if all(dot(n, (x, y, z + 8)) <= d + marge for n, d in planes):
                return True
        return False

    reset_guids(f"{MAP}.map")
    out, problemes, n = [head], [], 0
    for kv, nb, layer in ents:
        d = dict(kv)
        cls = d.get("classname")
        if d.get("model") in SANS:
            continue
        if cls == "worldspawn":
            brushes = sky_box()
            if not all(check_brush(p) for _, p in brushes):
                raise SystemExit("boite de ciel invalide")
            out += entity_lines(n, kv, brushes, layer)
        elif cls in VOLUMES:
            mat, b = VOLUMES[cls]
            out += entity_lines(n, kv, [(mat, box(*b))], layer)
        else:
            kv = list(kv)
            if cls == "misc_prefab" and "angles" not in d:
                kv.append(("angles", "0 0 0"))  # angle absent = 0 : il doit tourner comme les autres
            for i, (k, v) in enumerate(kv):
                if k == "origin":
                    x, y, z = place(v)
                    kv[i] = (k, f"{fmt(x)} {fmt(y)} {fmt(z)}")
                    if cls != "actor_zm_nuked_basic_01" and "spawner" not in cls and dans_batiment(x, y, z):
                        problemes.append(f"{cls} {d.get('model', d.get('targetname', ''))} en ({x:.0f}, {y:.0f})")
                elif k == "angles":
                    p, yaw, r = (float(a) for a in v.split())
                    kv[i] = (k, f"{fmt(p)} {fmt((yaw + ROTATION) % 360)} {fmt(r)}")
                elif k == "script_string" and v == "receiver_set_entry_a":
                    kv[i] = (k, "find_flesh")
            name = d.get("targetname")
            if name in INTERMISSION and cls == "script_struct":
                origin, angles = INTERMISSION[name]
                kv = [(k, origin if k == "origin" else angles if k == "angles" else v) for k, v in kv]
            out += entity_lines(n, kv, layer=layer)
        n += 1

    out += entity_lines(n, [
        ("classname", "misc_prefab"),
        ("model", f"_prefabs/{MAP}/site_blockout.map"),
        ("origin", "0 0 0"),
    ])

    if problemes:
        raise SystemExit("Entites dans un batiment :\n  " + "\n  ".join(problemes))

    dst = GAME / "map_source" / "zm" / f"{MAP}.map"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n", encoding="latin-1", newline="\r\n")

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

    print(f"{dst.relative_to(ROOT)} : {n + 1} entites, prefab du quartier : {len(site)} brushes")


if __name__ == "__main__":
    main(*sys.argv[1:])
