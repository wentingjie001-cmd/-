"""Reverse-engineered benchmark model of the Aarn Pace Magic 40 (approximate).

Rebuilt from the official product photos and published specs
(W 27 x D 20 x H 66 cm, back length 42-56 cm). Photo scale was calibrated
on the published height; see docs/05_reverse_engineering_pm40.md for the
measurement table and accuracy notes.

Internal construction (stay section, web routing inside the base) is not
visible in photos and is inferred from Aarn's published descriptions and
patents. This model is for benchmarking only and is not Aarn's original CAD.

Coordinate system is the same as backpack_model.py:
X left/right, Y = 0 at the back-panel skin plane (+Y towards the pack),
Z up from the pack bottom.
"""

from __future__ import annotations

import cadquery as cq

from backpack_model import _loft_sections, _sweep_circle, _sweep_rect

Y0 = 36.0  # back face of the pack body (slim air gap)

# body sections measured from the side and rear photos:
# (z, width, depth, y-centre, corner radius)
BODY_SECTIONS = [
    (0, 215, 150, Y0 + 80, 55),
    (50, 255, 182, Y0 + 92, 70),
    (200, 266, 188, Y0 + 95, 75),
    (380, 270, 192, Y0 + 97, 75),
    (520, 276, 214, Y0 + 106, 78),
    (600, 272, 222, Y0 + 110, 78),
    (640, 236, 190, Y0 + 98, 65),
]


def body():
    b = _loft_sections(BODY_SECTIONS)
    roll = (
        cq.Workplane("XY")
        .box(200, 150, 34)
        .edges("|X")
        .fillet(16)
        .edges("|Y or |Z")
        .fillet(8)
        .translate((0, Y0 + 98, 650))
    )
    zip_strip = _sweep_rect([(-80, Y0 + 205, 610), (0, Y0 + 222, 618), (80, Y0 + 205, 610)], 8, 3, (0, 0, 1))
    hang_loop = cq.Workplane("XZ").center(110, 680).circle(12).circle(8).extrude(-4).translate((0, Y0 + 40, 0))
    return b.union(roll).union(zip_strip).union(hang_loop)


def front_mesh_pocket():
    """Large grey stretch-mesh pocket on the outer face."""
    secs = [
        (40, 190, 16, Y0 + 186, 8),
        (200, 214, 26, Y0 + 197, 12),
        (380, 212, 20, Y0 + 198, 10),
        (430, 196, 10, Y0 + 196, 4),
    ]
    return _loft_sections(secs)


def drawcord():
    """Front compression shock-cord: X lacing above the mesh pocket with a cord lock."""
    y = Y0 + 214
    out = cq.Workplane("XY")
    pts = [(-118, 540), (-40, 470), (40, 540), (118, 470)]
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        out = out.union(_sweep_circle([(x0, y - 8, z0), ((x0 + x1) / 2, y + 2, (z0 + z1) / 2), (x1, y - 8, z1)], 4))
    for x, z in pts:
        out = out.union(cq.Workplane("XY").box(12, 8, 12).edges().fillet(2).translate((x, y - 10, z)))
    lock = cq.Workplane("XY").box(16, 12, 28).edges("|Z").fillet(5).translate((-30, y + 2, 440))
    tail = _sweep_circle([(-40, y, 470), (-32, y + 4, 452), (-30, y + 2, 430), (-28, y + 2, 400)], 4)
    return out.union(lock).union(tail)


def side_pockets():
    out = None
    for s in (1, -1):
        xc = s * 128
        secs = [(30, 30, 150, 96, 12), (160, 52, 170, 100, 18), (300, 46, 165, 104, 16), (330, 26, 150, 104, 8)]
        sk = [
            cq.Sketch().rect(w, d).vertices().fillet(min(r, w / 2 - 0.5)).moved(cq.Location(cq.Vector(xc + s * w / 4, Y0 + yc, z)))
            for z, w, d, yc, r in secs
        ]
        pk = cq.Workplane("XY").placeSketch(*sk).loft()
        out = pk if out is None else out.union(pk)
    return out


def x_stays():
    """Two curved stays crossing behind the mesh (S-curve vertically)."""
    out = cq.Workplane("XY")
    for s in (1, -1):
        out = out.union(
            _sweep_circle([(s * 108, 30, 560), (s * 50, 22, 420), (0, 20, 370), (-s * 50, 22, 300), (-s * 100, 26, 190)], 5)
        )
    hub = cq.Workplane("XZ").center(0, 370).circle(10).extrude(-8).translate((0, 14, 0))
    return out.union(hub)


def mesh_back_panel():
    upper = _loft_sections([(250, 176, 5, 8, 2), (360, 168, 5, 10, 2), (470, 196, 5, 8, 2), (560, 212, 5, 5, 2)])
    lumbar = (
        cq.Workplane("XY")
        .box(168, 20, 140)
        .edges("|Y")
        .fillet(30)
        .edges(">Y or <Y")
        .fillet(4)
        .translate((0, 10, 175))
    )
    return upper.union(lumbar)


def back_tensioners():
    out = cq.Workplane("XY")
    for s in (1, -1):
        web = _sweep_rect([(s * 100, 8, 556), (s * 112, 22, 566), (s * 120, Y0 + 4, 572)], 20, 1.6, (0, 0, 1))
        buckle = cq.Workplane("XY").box(24, 8, 20).edges("|Y").fillet(3).translate((s * 114, 24, 568))
        out = out.union(web).union(buckle)
    return out


def shoulder_strap(side: int):
    pts = [
        (side * 52, 6, 520),
        (side * 62, -30, 568),
        (side * 82, -110, 574),
        (side * 100, -180, 510),
        (side * 112, -205, 400),
        (side * 122, -170, 240),
    ]
    strap = _sweep_rect(pts, 60, 10, (1, 0, 0))
    bottle = (
        cq.Workplane("XY")
        .box(80, 56, 200)
        .edges("|Z")
        .fillet(24)
        .edges("<Z")
        .fillet(20)
        .translate((side * 98, -238, 360))
    )
    toggle = cq.Workplane("XZ").center(side * 98, 480).circle(11).circle(7).extrude(-4).translate((0, -238, 0))
    lifter = _sweep_rect([(side * 62, -34, 568), (side * 90, 4, 596), (side * 112, Y0 + 4, 590)], 20, 1.6, (1, 0, 0))
    bungy = _sweep_circle([(side * 98, -238, 260), (side * 130, -200, 170), (side * 160, -150, 120)], 3)
    return strap.union(bottle).union(lifter).union(bungy).union(toggle)


def sternum_straps():
    out = cq.Workplane("XY")
    for z in (480, 380):
        out = out.union(cq.Workplane("XY").box(150, 3, 16).translate((0, -214, z)))
        out = out.union(cq.Workplane("XY").box(36, 9, 20).edges("|Y").fillet(4).translate((0, -218, z)))
    return out


def uflow_linkage():
    """Linked lower tensioners: one web joining both strap ends through the base."""
    pts = [(-122, -170, 236), (-140, -60, 160), (-110, Y0 - 6, 70), (0, Y0 + 6, 30), (110, Y0 - 6, 70), (140, -60, 160), (122, -170, 236)]
    web = _sweep_rect(pts, 20, 1.6, (0, 1, 0), n_sections=24)
    sleeve = cq.Workplane("XY").box(200, 14, 30).edges("|X").fillet(6).translate((0, Y0 + 6, 32))
    buckles = cq.Workplane("XY")
    for s in (1, -1):
        buckles = buckles.union(cq.Workplane("XY").box(28, 10, 20).edges("|Y").fillet(4).translate((s * 122, -170, 236)))
    return web.union(sleeve).union(buckles)


def hip_belt(side: int):
    zc = 110
    pts = [(side * 70, 4, zc), (side * 140, -30, zc), (side * 175, -110, zc), (side * 160, -200, zc), (side * 115, -250, zc)]
    wing = _sweep_rect(pts, 120, 14, (0, 0, 1))
    pocket = (
        cq.Workplane("XY")
        .box(80, 135, 170)
        .edges("|Y")
        .fillet(34)
        .edges("|Z")
        .fillet(16)
        .translate((side * 150, -205, zc - 10))
        .rotate((side * 150, -205, 0), (side * 150, -205, 1), side * 52)
    )
    webs = cq.Workplane("XY")
    for dz in (34, -34):
        webs = webs.union(_sweep_rect([(side * 115, -250, zc + dz), (side * 60, -276, zc + dz), (side * 16, -282, zc + dz)], 20, 2, (0, 0, 1)))
    out = wing.union(pocket).union(webs)
    if side == 1:
        for dz in (34, -34):
            out = out.union(cq.Workplane("XY").box(40, 12, 26).edges("|Y").fillet(5).translate((0, -284, zc + dz)))
    return out


def build_parts():
    return {
        "aarn_body": body(),
        "aarn_front_mesh": front_mesh_pocket(),
        "aarn_drawcord": drawcord(),
        "aarn_side_pockets": side_pockets(),
        "aarn_x_stays": x_stays(),
        "aarn_mesh_back": mesh_back_panel(),
        "aarn_tensioners": back_tensioners(),
        "aarn_strap_l": shoulder_strap(1),
        "aarn_strap_r": shoulder_strap(-1),
        "aarn_sternum": sternum_straps(),
        "aarn_uflow": uflow_linkage(),
        "aarn_hipbelt_l": hip_belt(1),
        "aarn_hipbelt_r": hip_belt(-1),
    }


GREEN = (0.52, 0.62, 0.20)
GREY = (0.62, 0.64, 0.66)
COLORS = {
    "aarn_body": GREEN,
    "aarn_front_mesh": GREY,
    "aarn_drawcord": (0.75, 0.76, 0.78),
    "aarn_side_pockets": (0.48, 0.58, 0.18),
    "aarn_x_stays": (0.30, 0.30, 0.32),
    "aarn_mesh_back": GREY,
    "aarn_tensioners": (0.75, 0.76, 0.78),
    "aarn_strap_l": GREY,
    "aarn_strap_r": GREY,
    "aarn_sternum": (0.75, 0.76, 0.78),
    "aarn_uflow": (0.05, 0.50, 0.50),
    "aarn_hipbelt_l": GREEN,
    "aarn_hipbelt_r": GREEN,
}


if __name__ == "__main__":
    for k, v in build_parts().items():
        s = v.val()
        bb = s.BoundingBox()
        print(f"{k:18s} valid={s.isValid()} vol={s.Volume():9.0f} x[{bb.xmin:.0f},{bb.xmax:.0f}] y[{bb.ymin:.0f},{bb.ymax:.0f}] z[{bb.zmin:.0f},{bb.zmax:.0f}]")
