"""Reverse-engineered benchmark model of the Aarn Pace Magic 40 (approximate).

Rebuilt from the official product photos and published specs
(W 27 x D 20 x H 66 cm, back length 42-56 cm). The soft shapes are lofted
through cross-sections measured row by row on the photo silhouettes; see
docs/05_reverse_engineering_pm40.md for the calibration and accuracy notes,
and ``PHOTO_CAL`` below for the pixel <-> mm mapping used by the overlay check.

Internal construction (stay section, web routing inside the base) is not
visible in photos and is inferred from Aarn's published descriptions and
patents. This model is for benchmarking only and is not Aarn's original CAD.

Coordinate system is the same as backpack_model.py:
X left/right, Y = 0 at the back-panel skin plane (+Y towards the pack,
-Y towards the wearer), Z up from the pack bottom.
"""

from __future__ import annotations

import math

import cadquery as cq
import numpy as np

from backpack_model import _sweep_circle, _sweep_rect

V = cq.Vector
Y0 = 36.0  # back face of the pack body

# Photo calibration (official images, 1200 x 1200 px).
# side  = pm40_03.jpg, rotated by ``rot_deg`` about ``rot_center`` so the back panel is vertical;
#         y = Y0 - (px - x_back) * mm_px,  z = (row_bottom - row) * mm_px
# rear  = pm40_01.jpg; x = (px - x_mid) * mm_px_x,  z = z_top - (row - row_top) * mm_px_z
PHOTO_CAL = {
    "side": {"file": "pm40_03.jpg", "rot_deg": -5.6, "rot_center": (540, 600), "x_back": 535, "row_bottom": 1085, "mm_px": 0.609},
    "rear": {"file": "pm40_01.jpg", "x_mid": 595, "mm_px_x": 0.53, "row_top": 40, "z_top": 660, "mm_px_z": 0.625},
}

# Side-photo silhouette of the pack (front pocket included): z -> y of the outer face
SIDE_FRONT = [
    (0, 60), (15, 118), (27, 132), (40, 146), (52, 158), (76, 183), (100, 194), (125, 205), (149, 213),
    (174, 219), (198, 225), (234, 234), (295, 238), (356, 241), (417, 245), (478, 238), (515, 238),
    (539, 236), (563, 229), (588, 214), (612, 200), (624, 191), (636, 181), (648, 164), (657, 143), (662, 120),
]
# z -> y of the back face (the top of the pack overhangs the back panel)
SIDE_BACK = [(0, 52), (15, 40), (30, 36), (520, 36), (540, 26), (563, 2), (588, -10), (612, -8), (624, 0), (636, 14), (648, 40), (657, 75), (662, 100)]
# Rear photo: z -> half width of the body (below z 400 the side pockets hide it; values there are interpolated)
REAR_HALF_W = [
    (0, 85), (15, 100), (40, 112), (76, 118), (150, 122), (300, 126), (404, 126), (435, 128), (497, 133),
    (560, 135), (591, 133), (607, 130), (622, 120), (638, 97), (650, 72), (662, 45),
]
# Rear photo: z -> half width over the side pockets
SIDE_POCKET_HALF_W = [(25, 116), (60, 124), (120, 130), (185, 134), (247, 149), (310, 155), (360, 157), (375, 150)]
FRONT_POCKET = (45, 425)  # z range of the stretch-mesh front pocket (side photo)
FRONT_POCKET_T = 10  # its bulge in front of the body fabric


def _interp(table, z):
    zs, vs = zip(*table)
    return float(np.interp(z, zs, vs))


def _superellipse(cx, cy, z, a, b_back, b_front, n_back=4.0, n_front=2.4, npts=40):
    """Closed spline section: flatter towards -Y (back), rounder towards +Y (front)."""
    pts = []
    for i in range(npts):
        t = 2 * math.pi * i / npts
        c, s = math.cos(t), math.sin(t)
        n = n_front if s >= 0 else n_back
        b = b_front if s >= 0 else b_back
        x = a * math.copysign(abs(c) ** (2 / n), c)
        y = b * math.copysign(abs(s) ** (2 / n), s)
        pts.append(V(cx + x, cy + y, z))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def _soft_loft(sections, **kw):
    """sections: (cx, cy, z, a, b_back, b_front) -> lofted solid."""
    wires = [_superellipse(*s, **kw) for s in sections]
    return cq.Workplane().add(cq.Solid.makeLoft(wires, False))


def body_front(z):
    """Front face of the pack fabric (silhouette minus the front pocket where it sits)."""
    f = _interp(SIDE_FRONT, z)
    z0, z1 = FRONT_POCKET
    if z0 - 20 < z < z1 + 20:
        k = min(1.0, (z - (z0 - 20)) / 40, ((z1 + 20) - z) / 40)
        f -= FRONT_POCKET_T * k
    return f


BODY_Z = [2, 15, 30, 52, 76, 110, 150, 200, 260, 330, 400, 450, 500, 540, 575, 605, 625, 640, 652, 660]


def body():
    secs = []
    for z in BODY_Z:
        yb, yf = _interp(SIDE_BACK, z), body_front(z)
        yc = (yb + yf) / 2
        secs.append((0, yc, z, _interp(REAR_HALF_W, z), (yf - yb) / 2, (yf - yb) / 2))
    b = _soft_loft(secs, n_back=4.0, n_front=2.6)
    hang_loop = cq.Workplane("XZ").center(103, 658).circle(12).circle(8).extrude(-4).translate((0, 40, 0))
    return b.union(hang_loop)


def top_strap():
    """Compression strap over the domed top (the roll-top closure is rolled inside the dome)."""
    strap = _sweep_rect(
        [(0, 2, 556), (0, -14, 590), (0, -12, 615), (0, 8, 640), (0, 50, 656), (0, 100, 660), (0, 140, 655), (0, 172, 643), (0, 193, 623)],
        20,
        2,
        (1, 0, 0),
    )
    buckle = cq.Workplane("XY").box(30, 10, 24).edges("|Y").fillet(4).translate((0, -15, 598))
    return strap.union(buckle)


def front_mesh_pocket():
    """Large grey stretch-mesh pocket on the outer face."""
    z0, z1 = FRONT_POCKET
    secs = []
    for z, a in [(z0, 86), (z0 + 40, 104), (150, 110), (260, 112), (360, 110), (z1 - 15, 104), (z1, 96)]:
        yf = _interp(SIDE_FRONT, z) - (8 if z in (z0, z1) else 0)
        yb = body_front(z) - 12
        secs.append((0, (yb + yf) / 2, z, a, (yf - yb) / 2, (yf - yb) / 2))
    return _soft_loft(secs, n_back=3.0, n_front=3.0)


def drawcord():
    """Front compression shock-cord: zig-zag lacing above the mesh pocket with a cord lock."""
    out = cq.Workplane("XY")
    anchors = [(-112, 545), (-112, 470), (112, 470), (112, 545)]
    lace = [(-112, 545), (0, 440), (112, 545)], [(-112, 470), (0, 440), (112, 470)]
    for path in lace:
        for (x0, z0), (x1, z1) in zip(path, path[1:]):
            zm = (z0 + z1) / 2
            out = out.union(
                _sweep_circle([(x0, _interp(SIDE_FRONT, z0) - 6, z0), ((x0 + x1) / 2, _interp(SIDE_FRONT, zm) + 2, zm), (x1, _interp(SIDE_FRONT, z1), z1)], 4)
            )
    for x, z in anchors:
        out = out.union(cq.Workplane("XY").box(12, 8, 12).edges().fillet(2).translate((x, _interp(SIDE_FRONT, z) - 8, z)))
    y = _interp(SIDE_FRONT, 430)
    lock = cq.Workplane("XY").box(16, 12, 26).edges("|Z").fillet(5).translate((0, y + 2, 425))
    return out.union(lock)


def side_pockets():
    """Stretch side pockets, read as the wider lower body in the rear photo."""
    secs = []
    for z, a in SIDE_POCKET_HALF_W:
        yb = Y0 + 6
        yf = body_front(z) - 6
        secs.append((0, (yb + yf) / 2, z, a, (yf - yb) / 2, (yf - yb) / 2))
    return _soft_loft(secs, n_back=3.2, n_front=3.2)


def x_stays():
    """Two curved stays crossing behind the mesh (inferred ends; crossing seen through the mesh)."""
    out = cq.Workplane("XY")
    for s, yc in ((1, 17), (-1, 23)):
        out = out.union(_sweep_circle([(s * 100, 24, 548), (s * 50, yc + 1, 455), (0, yc, 370), (-s * 50, yc + 1, 285), (-s * 92, 24, 165)], 5))
    hub = cq.Workplane("XZ").center(0, 370).circle(10).extrude(-8).translate((0, 10, 0))
    return out.union(hub)


def _xz_plate(half_outline, y0, t):
    """Symmetric plate in the XZ plane from a list of (z, half-width), from y0 towards +Y."""
    right = [(w, z) for z, w in half_outline]
    left = [(-w, z) for z, w in reversed(half_outline)]
    return cq.Workplane("XZ").polyline(right + left).close().extrude(-t).translate((0, y0, 0))


def mesh_back_panel():
    """Suspended light outer mesh (the dark central Y mesh and the lumbar pad are separate parts)."""
    return _xz_plate([(205, 92), (300, 100), (420, 106), (500, 110), (552, 112)], 6, 3)


def lumbar_pad():
    return cq.Workplane("XZ").center(0, 135).rect(136, 148).extrude(-22).edges("|Y").fillet(30).faces("<Y").edges().fillet(6)


def mesh_back_dark():
    """Dark Y-shaped central mesh (rear photo); the notch between the arms closes at z 470."""
    return _xz_plate([(209, 44), (300, 40), (440, 42), (480, 64), (508, 84), (512, 64), (470, 24)], 4, 2.5)


def back_tensioners():
    """Top tension bar across the panel with a buckle at each end."""
    out = _sweep_rect([(-113, 14, 554), (0, 10, 556), (113, 14, 554)], 20, 1.6, (0, 0, 1))
    for s in (1, -1):
        buckle = cq.Workplane("XY").box(24, 8, 22).edges("|Y").fillet(3).translate((s * 113, 16, 554))
        tail = _sweep_rect([(s * 113, 18, 556), (s * 122, 30, 560), (s * 128, Y0 + 2, 566)], 20, 1.6, (0, 0, 1))
        out = out.union(buckle).union(tail)
    return out


# inverted-U over the shoulder: the inner end enters the mesh top at z 470, the arch peaks at z ~520
STRAP_PATH = [(34, 10, 470), (44, -8, 500), (52, -40, 519), (54, -80, 505), (55, -110, 475), (56, -126, 432), (56, -127, 380), (56, -110, 320), (57, -84, 262), (58, -63, 210), (60, -58, 182)]


def _strap_y(z):
    zs = [p[2] for p in STRAP_PATH[3:]][::-1]
    ys = [p[1] for p in STRAP_PATH[3:]][::-1]
    return float(np.interp(z, zs, ys))


BOTTLE = {"x": 86, "y": -168, "z0": 180, "z1": 365}


def shoulder_strap(side: int):
    # vest-style: the outer edge wraps back around the chest (~40 deg), as seen in the side photo
    strap = _sweep_rect([(side * x, y, z) for x, y, z in STRAP_PATH], 52, 12, (side * 0.75, 0.66, 0), n_sections=20)
    bx, by, z0, z1 = side * BOTTLE["x"], BOTTLE["y"], BOTTLE["z0"], BOTTLE["z1"]
    bottle = _soft_loft(
        [(bx, by, z0, 26, 30, 30), (bx, by, z0 + 18, 35, 40, 40), (bx, by, 290, 39, 43, 43), (bx, by, z1 - 15, 39, 43, 43), (bx, by, z1, 34, 38, 38)],
        n_back=2.6,
        n_front=2.6,
    )
    toggle = cq.Workplane("XZ").center(bx, z1 + 14).circle(11).circle(7).extrude(-4).translate((0, by - 30, 0))
    lifter = _sweep_rect([(side * 72, -60, 508), (side * 94, -20, 530), (side * 108, 12, 548)], 20, 1.6, (1, 0, 0))
    bungy = _sweep_circle([(bx, by - 10, z0 + 4), (bx, by - 22, 160), (side * 88, -195, 146)], 3)
    return strap.union(bottle).union(toggle).union(lifter).union(bungy)


def sternum_straps():
    out = cq.Workplane("XY")
    for z in (324, 214):
        y = _strap_y(z) - 9
        out = out.union(cq.Workplane("XY").box(112, 3, 16).translate((0, y, z)))
        out = out.union(cq.Workplane("XY").box(34, 9, 20).edges("|Y").fillet(4).translate((0, y - 3, z)))
    return out


def uflow_linkage():
    """Linked lower tensioners: one web from each strap end, down the pack sides and through a base sleeve."""
    # visible part (side photo): strap end -> diagonally down to mid-depth of the pack side at z ~65
    half = [(60, -58, 182), (98, -14, 158), (124, 45, 110), (128, 95, 66), (100, 62, 18), (0, 54, 12)]
    pts = [(-x, y, z) for x, y, z in half] + [(x, y, z) for x, y, z in reversed(half[:-1])]
    web = _sweep_rect(pts, 20, 1.6, (0, 1, 0), n_sections=30)
    sleeve = cq.Workplane("XY").box(200, 24, 14).edges("|X").fillet(5).translate((0, 54, 14))
    buckles = cq.Workplane("XY")
    for s in (1, -1):
        buckles = buckles.union(cq.Workplane("XY").box(26, 10, 20).edges("|Y").fillet(4).translate((s * 98, -14, 158)))
    return web.union(sleeve).union(buckles)


# Hip belt as photographed: a closed loop hanging slightly forward-down from the base.
BELT = {"a": 105, "y_back": 20, "y_front": -290, "z_back": 50, "z_front": 10, "h": 96}
HIP_POCKET = {"x": 88, "y": -190, "z0": -50, "z1": 143}


def _belt_point(side, phi):
    a, yb, yf = BELT["a"], BELT["y_back"], BELT["y_front"]
    r = (yb - yf) / 2
    x = side * a * math.sin(phi)
    y = yb - r * (1 - math.cos(phi))
    z = BELT["z_back"] + (BELT["z_front"] - BELT["z_back"]) * (yb - y) / (yb - yf)
    return (x, y, z)


def hip_belt(side: int):
    tilt = (0, (BELT["z_front"] - BELT["z_back"]) / (BELT["y_back"] - BELT["y_front"]), 1)
    wing_pts = [_belt_point(side, phi) for phi in np.linspace(0.18, 2.25, 9)]
    wing = _sweep_rect(wing_pts, BELT["h"], 12, tilt, n_sections=18)
    webs = cq.Workplane("XY")
    for dz in (28, -28):
        pts = [_belt_point(side, phi) for phi in np.linspace(2.2, math.pi, 6)]
        pts = [(x, y, z + dz) for x, y, z in pts]
        webs = webs.union(_sweep_rect(pts, 20, 2, tilt, n_sections=10))
    px, py, z0, z1 = side * HIP_POCKET["x"], HIP_POCKET["y"], HIP_POCKET["z0"], HIP_POCKET["z1"]
    pocket = _soft_loft(
        [(px, py, z0, 36, 58, 58), (px, py, z0 + 25, 54, 82, 82), (px, py, 45, 58, 88, 88), (px, py, 110, 53, 80, 80), (px, py, z1, 38, 60, 60)],
        n_back=2.4,
        n_front=2.4,
    )
    out = wing.union(webs).union(pocket)
    if side == 1:
        x, y, z = _belt_point(1, math.pi)
        for dz in (28, -28):
            out = out.union(cq.Workplane("XY").box(40, 12, 26).edges("|Y").fillet(5).translate((0, y - 4, z + dz)))
    return out


def build_parts():
    return {
        "aarn_body": body(),
        "aarn_top_strap": top_strap(),
        "aarn_front_mesh": front_mesh_pocket(),
        "aarn_drawcord": drawcord(),
        "aarn_side_pockets": side_pockets(),
        "aarn_x_stays": x_stays(),
        "aarn_mesh_back": mesh_back_panel(),
        "aarn_mesh_dark": mesh_back_dark(),
        "aarn_lumbar": lumbar_pad(),
        "aarn_tensioners": back_tensioners(),
        "aarn_strap_l": shoulder_strap(1),
        "aarn_strap_r": shoulder_strap(-1),
        "aarn_sternum": sternum_straps(),
        "aarn_uflow": uflow_linkage(),
        "aarn_hipbelt_l": hip_belt(1),
        "aarn_hipbelt_r": hip_belt(-1),
    }


GREEN = (0.55, 0.64, 0.20)
GREY = (0.66, 0.68, 0.70)
LIGHT = (0.78, 0.79, 0.80)
COLORS = {
    "aarn_body": GREEN,
    "aarn_top_strap": LIGHT,
    "aarn_front_mesh": GREY,
    "aarn_drawcord": LIGHT,
    "aarn_side_pockets": (0.50, 0.60, 0.17),
    "aarn_x_stays": (0.30, 0.30, 0.32),
    "aarn_mesh_back": GREY,
    "aarn_mesh_dark": (0.36, 0.37, 0.39),
    "aarn_lumbar": (0.36, 0.37, 0.39),
    "aarn_tensioners": LIGHT,
    "aarn_strap_l": GREY,
    "aarn_strap_r": GREY,
    "aarn_sternum": LIGHT,
    "aarn_uflow": (0.72, 0.74, 0.75),
    "aarn_hipbelt_l": GREEN,
    "aarn_hipbelt_r": GREEN,
}


if __name__ == "__main__":
    for k, v in build_parts().items():
        s = v.val()
        bb = s.BoundingBox()
        print(f"{k:18s} valid={s.isValid()} vol={s.Volume():9.0f} x[{bb.xmin:.0f},{bb.xmax:.0f}] y[{bb.ymin:.0f},{bb.ymax:.0f}] z[{bb.zmin:.0f},{bb.zmax:.0f}]")
