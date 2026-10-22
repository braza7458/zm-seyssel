"""Apercu 3D (vue isometrique en SVG) de fichiers .map Radiant, colore par materiau.

Relit les brushes, reconstruit leurs faces et les dessine (tri par profondeur sur
petits triangles), ce qui permet de verifier la geometrie sans ouvrir Radiant.

Usage :
    python tools/preview_blockout.py sortie.svg fichier.map [autres.map ...]
        [--boite x0 y0 z0 x1 y1 z1] [--vue azimut elevation] [--taille 160]
"""

import math
import re
import sys
from pathlib import Path

from make_blockout import add, cross, dot, norm, scale, sub

FACE = re.compile(r"\(\s*([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)\s*\)\s*\(\s*([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)\s*\)"
                  r"\s*\(\s*([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)\s*\)\s+(\S+)")

# couleur approximative de chaque famille de materiau
COULEURS = [
    ("grass", (110, 150, 80)), ("dirt", (130, 110, 80)), ("asphalt", (70, 70, 74)), ("sidewalk", (170, 168, 160)),
    ("curb", (185, 185, 180)), ("roof", (120, 85, 65)), ("plaster_smooth", (225, 212, 185)),
    ("painted_white", (232, 232, 228)), ("worn_painted_white", (226, 226, 222)), ("brick", (150, 90, 75)),
    ("wood_panel", (95, 65, 45)), ("window", (55, 65, 80)), ("glass", (120, 160, 190)), ("travertine", (226, 214, 180)),
    ("cream", (236, 222, 190)), ("tile", (220, 220, 215)), ("veneer", (175, 135, 90)), ("metal", (90, 92, 96)),
    ("door", (120, 95, 70)), ("concrete", (160, 158, 152)), ("pebbles", (150, 145, 135)), ("sky", (170, 200, 235)),
    ("clip", None), ("trigger", None), ("volume", None), ("caulk", None),
]


def couleur(mat):
    for cle, c in COULEURS:
        if cle in mat:
            return c
    return (190, 185, 175)


def read_brushes(paths):
    brushes = []
    for path in paths:
        current = None
        for line in Path(path).read_text(encoding="latin-1").splitlines():
            m = FACE.search(line)
            if m and current is not None:
                v = [float(x) for x in m.groups()[:9]]
                p1, p2, p3 = tuple(v[0:3]), tuple(v[3:6]), tuple(v[6:9])
                n = norm(cross(sub(p3, p1), sub(p2, p1)))
                current.append((n, dot(n, p1), m.group(10)))
            elif line.startswith("// brush"):
                current = []
                brushes.append(current)
            elif line.startswith("// entity"):
                current = None
    return brushes


def faces(planes):
    verts = []
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            for k in range(j + 1, len(planes)):
                (a, da, _), (b, db, _), (c, dc, _) = planes[i], planes[j], planes[k]
                det = dot(a, cross(b, c))
                if abs(det) < 1e-9:
                    continue
                v = scale(add(add(scale(cross(b, c), da), scale(cross(c, a), db)), scale(cross(a, b), dc)), 1 / det)
                if all(dot(n, v) <= d + 0.01 for n, d, _ in planes):
                    verts.append(v)
    out = []
    for n, d, mat in planes:
        on = [v for v in verts if abs(dot(n, v) - d) < 0.01]
        uniq = []
        for v in on:
            if all(sum((v[t] - w[t]) ** 2 for t in range(3)) > 0.01 for w in uniq):
                uniq.append(v)
        if len(uniq) < 3:
            continue
        c = scale(uniq[0], 0)
        for v in uniq:
            c = add(c, scale(v, 1 / len(uniq)))
        u = norm(sub(uniq[0], c))
        w = cross(n, u)
        uniq.sort(key=lambda v: math.atan2(dot(sub(v, c), w), dot(sub(v, c), u)))
        out.append((n, uniq, mat))
    return out


def split(tri, size):
    a, b, c = tri
    edges = [(math.dist(a, b), (a, b, c)), (math.dist(b, c), (b, c, a)), (math.dist(c, a), (c, a, b))]
    length, (p, q, r) = max(edges)
    if length <= size:
        return [tri]
    m = scale(add(p, q), 0.5)
    return split((p, m, r), size) + split((m, q, r), size)


def main(argv):
    dst, paths, boite, az, el, taille, centre = argv[0], [], None, -35, 32, 160, False
    i = 1
    while i < len(argv):
        if argv[i] == "--boite":
            boite = [float(v) for v in argv[i + 1:i + 7]]
            i += 7
        elif argv[i] == "--vue":
            az, el = float(argv[i + 1]), float(argv[i + 2])
            i += 3
        elif argv[i] == "--centre":
            centre = True  # garde une face si son centre est dans la boite (coupes, plans d'etage)
            i += 1
        elif argv[i] == "--taille":
            taille = float(argv[i + 1])
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    a, e = math.radians(az), math.radians(el)
    cam = (math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e))
    right = norm(cross((0, 0, 1), cam))
    up = cross(cam, right)
    light = norm((0.4, -0.6, 0.8))

    polys = []
    for planes in read_brushes(paths):
        for n, pts, mat in faces(planes):
            col = couleur(mat)
            if col is None or dot(n, cam) <= 0:
                continue
            if boite:
                test = [tuple(sum(p[t] for p in pts) / len(pts) for t in range(3))] if centre else pts
                if not all(boite[0] <= p[0] <= boite[3] and boite[1] <= p[1] <= boite[4] and boite[2] <= p[2] <= boite[5] for p in test):
                    continue
            shade = 0.5 + 0.5 * max(0, dot(n, light))
            col = "#%02x%02x%02x" % tuple(int(min(255, ch * shade)) for ch in col)
            for k in range(1, len(pts) - 1):
                for tri in split((pts[0], pts[k], pts[k + 1]), taille):
                    depth = sum(dot(p, cam) for p in tri) / 3
                    polys.append((depth, col, [(dot(p, right), -dot(p, up)) for p in tri]))
    polys.sort(key=lambda t: t[0])
    xs = [x for *_, pts in polys for x, _ in pts]
    ys = [y for *_, pts in polys for _, y in pts]
    pad, W = 20, 1600
    k = W / (max(xs) - min(xs))
    h = (max(ys) - min(ys)) * k + 2 * pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * pad:.0f} {h:.0f}">',
           f'<rect width="100%" height="100%" fill="#bcd3e6"/>']
    for _, col, pts in polys:
        d = " ".join(f"{(x - min(xs)) * k + pad:.1f},{(y - min(ys)) * k + pad:.1f}" for x, y in pts)
        out.append(f'<polygon points="{d}" fill="{col}" stroke="{col}" stroke-width="0.5"/>')
    out.append("</svg>")
    Path(dst).write_text("\n".join(out), encoding="utf-8")
    print(f"{len(polys)} triangles -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1:])
