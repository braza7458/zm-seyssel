"""Orthophoto IGN remise dans le repere du jeu, avec en surimpression les routes et les batiments generes.

    python tools/ortho_jeu.py [x0 y0 x1 y1] [unites par pixel]

Ecrit _build/ref/ortho_jeu.png (photo seule) et _build/ref/ortho_controle.png (photo + routes OSM en rouge,
batiments BD TOPO en jaune, chemin jusqu'au Carrefour en bleu, limite de la zone jouable en blanc).
"""

import io
import json
import math
import sys
import urllib.request

from PIL import Image, ImageDraw

import monde
from geo import REF, ROOT, Site

WMS = ("https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=ORTHOIMAGERY.ORTHOPHOTOS"
       "&STYLES=&CRS=EPSG:4326&BBOX={la0},{lo0},{la1},{lo1}&WIDTH={w}&HEIGHT={h}&FORMAT=image/jpeg")


def main(x0=-7000, y0=-8000, x1=21000, y1=45000, upp=20.0):
    site = Site()
    out_dir = ROOT / "_build" / "ref"
    out_dir.mkdir(parents=True, exist_ok=True)
    coins = [site.vers_latlon(x, y) for x in (x0, x1) for y in (y0, y1)]
    la0, la1 = min(c[0] for c in coins), max(c[0] for c in coins)
    lo0, lo1 = min(c[1] for c in coins), max(c[1] for c in coins)
    # photo en tuiles de 2048 px maximum
    W, H = 4096, int(4096 * (la1 - la0) * 110540 / ((lo1 - lo0) * 111320 * math.cos(math.radians(la0))))
    photo = Image.new("RGB", (W, H))
    nt = 2
    for i in range(nt):
        for j in range(math.ceil(H / 2048)):
            tw, th = W // nt, min(2048, H - j * 2048)
            b = dict(la0=la1 - (j * 2048 + th) / H * (la1 - la0), la1=la1 - j * 2048 / H * (la1 - la0),
                     lo0=lo0 + i * tw / W * (lo1 - lo0), lo1=lo0 + (i + 1) * tw / W * (lo1 - lo0), w=tw, h=th)
            with urllib.request.urlopen(urllib.request.Request(WMS.format(**b), headers={"User-Agent": "zm-seyssel"}),
                                        timeout=120) as r:
                photo.paste(Image.open(io.BytesIO(r.read())).convert("RGB"), (i * tw, j * 2048))
    # reechantillonnage dans le repere du jeu (x vers la droite, y vers le haut)
    gw, gh = int((x1 - x0) / upp), int((y1 - y0) / upp)
    img = Image.new("RGB", (gw, gh))
    px = img.load()
    src = photo.load()
    for v in range(gh):
        y = y1 - (v + 0.5) * upp
        for u in range(gw):
            x = x0 + (u + 0.5) * upp
            la, lo = site.vers_latlon(x, y)
            sx = int((lo - lo0) / (lo1 - lo0) * W)
            sy = int((la1 - la) / (la1 - la0) * H)
            if 0 <= sx < W and 0 <= sy < H:
                px[u, v] = src[sx, sy]
    img.save(out_dir / "ortho_jeu.png")

    def P(x, y):
        return ((x - x0) / upp, (y1 - y) / upp)

    ctl = img.copy()
    d = ImageDraw.Draw(ctl)
    osm = json.loads((REF / "osm" / "corridor.json").read_text(encoding="utf-8"))
    for e in osm["elements"]:
        t = e.get("tags", {})
        if "highway" in t:
            d.line([P(*site.proj(n["lat"], n["lon"])) for n in e["geometry"]], fill=(255, 40, 40), width=2)
    for b in json.loads((REF / "ign" / "bdtopo_couloir.json").read_text(encoding="utf-8")):
        d.polygon([P(*p) for p in b["emprise"]], outline=(255, 230, 0))
    d.line([P(*p) for p in monde.SPINE], fill=(40, 120, 255), width=3)
    ctl.save(out_dir / "ortho_controle.png")
    print("ecrit", out_dir / "ortho_controle.png", ctl.size)


if __name__ == "__main__":
    a = [float(v) for v in sys.argv[1:]]
    main(*a) if a else main()
