"""Apercu 3D (vue isometrique en SVG) d'un fichier .map Radiant.

Relit les brushes du fichier, reconstruit leurs faces et les dessine,
ce qui permet de verifier un prefab sans ouvrir Radiant.

Usage :
    python tools/preview_blockout.py [fichier.map] [sortie.svg]
"""

import math
import re
import sys
from pathlib import Path

from make_blockout import OUT, add, cross, dot, norm, scale, sub
from osm_to_plan import ROOT

FACE = re.compile(r"\(\s*([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)\s*\)")


def read_brushes(path):
    brushes, current = [], None
    for line in Path(path).read_text(encoding="ascii").splitlines():
        pts = FACE.findall(line)
        if len(pts) == 3:
            p1, p2, p3 = [tuple(float(c) for c in p) for p in pts]
            n = norm(cross(sub(p3, p1), sub(p2, p1)))
            current.append((n, dot(n, p1)))
        elif line.startswith("// brush"):
            current = []
            brushes.append(current)
    return brushes


def faces(planes):
    """Polygones des faces d'un brush convexe."""
    verts = []
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            for k in range(j + 1, len(planes)):
                (a, da), (b, db), (c, dc) = planes[i], planes[j], planes[k]
                det = dot(a, cross(b, c))
                if abs(det) < 1e-9:
                    continue
                v = scale(add(add(scale(cross(b, c), da), scale(cross(c, a), db)), scale(cross(a, b), dc)), 1 / det)
                if all(dot(n, v) <= d + 0.01 for n, d in planes):
                    verts.append(v)
    out = []
    for n, d in planes:
        on = [v for v in verts if abs(dot(n, v) - d) < 0.01]
        if len(on) < 3:
            continue
        c = scale(on[0], 0)
        for v in on:
            c = add(c, scale(v, 1 / len(on)))
        u = norm(sub(on[0], c)) if dot(sub(on[0], c), sub(on[0], c)) > 1e-6 else norm(sub(on[1], c))
        w = cross(n, u)
        on.sort(key=lambda v: math.atan2(dot(sub(v, c), w), dot(sub(v, c), u)))
        out.append((n, on))
    return out


def split(tri, size=160):
    """Decoupe un triangle en petits triangles, pour que le tri par profondeur reste juste."""
    a, b, c = tri
    edges = [(math.dist(a, b), (a, b, c)), (math.dist(b, c), (b, c, a)), (math.dist(c, a), (c, a, b))]
    length, (p, q, r) = max(edges)
    if length <= size:
        return [tri]
    m = scale(add(p, q), 0.5)
    return split((p, m, r), size) + split((m, q, r), size)


def main(src=OUT, dst=ROOT / "docs" / "plans" / "apercu-blockout.svg", view=2600):
    az, el = math.radians(-35), math.radians(32)
    # Camera : regarde le HLM depuis le sud-est
    cam = (math.cos(el) * math.sin(az), -math.cos(el) * math.cos(az), math.sin(el))
    right = norm(cross((0, 0, 1), cam))
    up = cross(cam, right)
    light = norm((0.4, -0.6, 0.8))

    polys = []
    for planes in read_brushes(src):
        for n, pts in faces(planes):
            if all(abs(p[0]) > view or abs(p[1]) > view for p in pts):
                continue
            if dot(n, cam) <= 0:
                continue
            shade = 0.45 + 0.55 * max(0, dot(n, light))
            if 0.3 < n[2] < 0.99:
                base = (196, 110, 86)  # toit en tuiles
            elif n[2] > 0.99 and pts[0][2] <= 2:
                base = (175, 170, 160)  # route
            else:
                base = (214, 206, 188)  # murs et toits plats
            col = "#%02x%02x%02x" % tuple(int(c * shade) for c in base)
            for i in range(1, len(pts) - 1):
                for tri in split((pts[0], pts[i], pts[i + 1])):
                    depth = sum(dot(p, cam) for p in tri) / 3
                    polys.append((depth, col, [(dot(p, right), -dot(p, up)) for p in tri]))
    polys.sort(key=lambda t: t[0])

    xs = [x for *_, pts in polys for x, _ in pts]
    ys = [y for *_, pts in polys for _, y in pts]
    pad = 40
    k = 1100 / (max(xs) - min(xs))
    w, h = 1100 + 2 * pad, (max(ys) - min(ys)) * k + 2 * pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}">',
           f'<rect width="{w:.0f}" height="{h:.0f}" fill="#9db07f"/>']
    for depth, col, pts in polys:
        d = " ".join(f"{(x - min(xs)) * k + pad:.1f},{(y - min(ys)) * k + pad:.1f}" for x, y in pts)
        out.append(f'<polygon points="{d}" fill="{col}" stroke="{col}" stroke-width="0.6"/>')
    out.append("</svg>")
    Path(dst).write_text("\n".join(out), encoding="utf-8")
    print(f"{len(polys)} faces dessinees dans {Path(dst).relative_to(ROOT)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
