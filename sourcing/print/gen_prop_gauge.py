#!/usr/bin/env python3
"""Printable size gauge for the Starling 2 Max propeller (7 × 3.7 × 3).

Not a flyable prop: a flat 3-blade outline at the stock diameter, a ring whose
outer edge is exactly that diameter, and a hub with the stock thickness and an M5
bore. Lay a shop prop on it to compare diameter, blade count and hub; push the hub
onto a motor shaft (prop nut off) to check the bore.

Dimensions: 7 in tri-blade, 7 mm hub (Gemfan 7037 published spec; ModalAI publishes
none). Blade planform is approximate. Pitch can't be gauged flat: read it off the
prop's label ("7037" = 7 in, 3.7 pitch).

Needs trimesh + shapely + mapbox-earcut + manifold3d.
Usage: gen_prop_gauge.py OUT_DIR      (writes prop-gauge-7037.stl and .svg)
"""
import math, os, sys

import manifold3d as m3d
import numpy as np
import trimesh
from shapely.affinity import rotate
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

DIAMETER = 178.0      # mm; 7 in = 177.8, Gemfan 7037 = 178.8
HUB_OD = 14.0         # mm
HUB_HEIGHT = 7.0      # mm, Gemfan 7037 centre thickness
BORE = 5.2            # mm: M5 shaft + 0.2 print clearance
PLATE = 2.0           # mm, blade and ring thickness
RING_WIDTH = 2.5      # mm
BLADES = 3

R = DIAMETER / 2


def chord(r):
    """Approximate blade width (mm) at radius r: widest ~18.5 mm at r≈30, ~9 mm near the tip."""
    if r < 30:
        return 12 + 6.5 * math.sin(math.pi / 2 * (r - 6) / 24)
    return 18.5 - 9.5 * ((r - 30) / (R - 4.5 - 30)) ** 1.5


def blade():
    rs = np.linspace(6, R - 4.5, 60)
    lead = [(r, +chord(r) * 0.58) for r in rs]           # leading edge slightly fuller
    trail = [(r, -chord(r) * 0.42) for r in rs[::-1]]
    body = Polygon(lead + trail)
    tip_w = chord(R - 4.5)
    tip = Point(R - 4.5, (0.58 - 0.42) / 2 * tip_w).buffer(tip_w / 2, resolution=32)
    return unary_union([body, tip])


def outline():
    b = blade()
    parts = [rotate(b, 360 / BLADES * i, origin=(0, 0)) for i in range(BLADES)]
    parts.append(Point(0, 0).buffer(HUB_OD / 2 + 2, resolution=64))   # wider than the hub: no shared edges
    parts.append(Point(0, 0).buffer(R, resolution=256).difference(Point(0, 0).buffer(R - RING_WIDTH, resolution=256)))
    shape = unary_union(parts)
    shape = shape.intersection(Point(0, 0).buffer(R, resolution=256))      # nothing past the stated diameter
    return shape.difference(Point(0, 0).buffer(BORE / 2, resolution=64))


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    plate2d = outline()
    hub2d = Point(0, 0).buffer(HUB_OD / 2, resolution=64).difference(Point(0, 0).buffer(BORE / 2, resolution=64))

    def section(poly):          # shapely polygon(s) -> manifold3d CrossSection (even-odd fill)
        loops = []
        for g in getattr(poly, "geoms", [poly]):
            loops += [np.asarray(g.exterior.coords)[:-1]] + [np.asarray(i.coords)[:-1] for i in g.interiors]
        return m3d.CrossSection(loops, m3d.FillRule.EvenOdd)

    solid = (m3d.Manifold.extrude(section(plate2d), PLATE)
             + m3d.Manifold.extrude(section(hub2d), HUB_HEIGHT - PLATE).translate([0, 0, PLATE]))  # union
    gl = solid.to_mesh()
    mesh = trimesh.Trimesh(vertices=np.asarray(gl.vert_properties)[:, :3], faces=np.asarray(gl.tri_verts), process=False)
    stl = os.path.join(outdir, "prop-gauge-7037.stl")
    mesh.export(stl)

    # top-view SVG for the docs / a paper check
    s = 2.0
    def path(poly):
        ring = lambda c: "M" + " L".join(f"{x*s + R*s + 10:.2f},{-y*s + R*s + 10:.2f}" for x, y in c.coords) + " Z"
        return ring(poly.exterior) + "".join(" " + ring(i) for i in poly.interiors)
    geoms = getattr(plate2d, "geoms", [plate2d])
    size = 2 * R * s + 20
    svg = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {size:.0f} {size + 40:.0f}' width='{size:.0f}' height='{size + 40:.0f}'>",
           f"<rect width='100%' height='100%' fill='#fff'/>",
           "<path fill-rule='evenodd' fill='#f2b134' stroke='#7a5200' stroke-width='1' d='" + " ".join(path(g) for g in geoms) + "'/>",
           f"<circle cx='{R*s+10:.1f}' cy='{R*s+10:.1f}' r='{HUB_OD/2*s:.1f}' fill='#c98a10' stroke='#7a5200'/>",
           f"<circle cx='{R*s+10:.1f}' cy='{R*s+10:.1f}' r='{BORE/2*s:.1f}' fill='#fff' stroke='#7a5200'/>",
           f"<text x='{size/2:.0f}' y='{size + 26:.0f}' font-family='Helvetica, Arial' font-size='11' text-anchor='middle'>"
           f"Prop gauge 7037 · Ø {DIAMETER:.0f} mm · hub Ø {HUB_OD:.0f} × {HUB_HEIGHT:.0f} mm · bore {BORE} mm (M5)</text>",
           "</svg>"]
    open(os.path.join(outdir, "prop-gauge-7037.svg"), "w").write("\n".join(svg))
    ext = mesh.bounds[1] - mesh.bounds[0]
    print(f"{stl}: {ext[0]:.1f} × {ext[1]:.1f} × {ext[2]:.1f} mm, watertight={mesh.is_watertight}, "
          f"volume {mesh.volume/1000:.1f} cm³")


if __name__ == "__main__":
    main(sys.argv[1])
