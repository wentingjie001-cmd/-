"""Parametric model of the "随动背负系统" 40 L backpack concept.

Coordinate system (mm):
    X  left/right of the wearer (+X = wearer's left)
    Y  front/back; Y = 0 is the skin-contact plane of the back panel,
       +Y points away from the wearer towards the pack body
    Z  up; Z = 0 is the bottom of the pack body

Soft goods (pack body, straps, belt) are modelled as simplified surfaces so the
model can be used for appearance views and a scale mock-up. Hard parts (frame,
linkage housing, rollers, cam lever, pivot plate) are modelled to manufacturing
intent and are the parts dimensioned in the engineering drawings.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq

V = cq.Vector


@dataclass
class Params:
    body_w: float = 280.0
    body_d: float = 200.0
    body_h: float = 640.0
    body_y0: float = 52.0  # back face of the pack body (air gap + frame)

    frame_rod_d: float = 6.0
    frame_top_z: float = 560.0
    frame_top_half_w: float = 112.0
    frame_node_z: float = 190.0  # where the two upper arms meet the stem

    mesh_y: float = 6.0

    hub_w: float = 156.0
    hub_depth: float = 28.0
    hub_y0: float = 20.0
    hub_z0: float = 52.0
    roller_d: float = 14.0
    roller_len: float = 22.0
    web_w: float = 20.0

    strap_w: float = 66.0
    strap_t: float = 12.0
    belt_h: float = 110.0
    belt_t: float = 14.0

    extra: dict = field(default_factory=dict)


P = Params()


def _rrect(w: float, d: float, r: float) -> cq.Sketch:
    r = min(r, w / 2 - 0.5, d / 2 - 0.5)
    return cq.Sketch().rect(w, d).vertices().fillet(r)


def _loft_sections(sections):
    """sections: list of (z, w, d, yc, r) -> lofted solid."""
    wp = cq.Workplane("XY")
    sk = [_rrect(w, d, r).moved(cq.Location(V(0, yc, z))) for z, w, d, yc, r in sections]
    return wp.placeSketch(*sk).loft(combine=True)


def _sweep_rect(points, w, t, wdir, n_sections=14):
    """Band of section w x t following a 3D spline.

    Built as a loft through rectangular sections so the w side always stays
    as close as possible to ``wdir`` (no twisting as with Frenet sweeps).
    """
    pts = [V(*p) for p in points]
    path = cq.Edge.makeSpline(pts)
    wd = V(*wdir).normalized()
    wires = []
    for i in range(n_sections + 1):
        u = i / n_sections
        o = path.positionAt(u)
        tan = path.tangentAt(u).normalized()
        b = wd - tan * wd.dot(tan)
        b = b.normalized() if b.Length > 1e-6 else tan.cross(V(0, 0, 1)).normalized()
        plane = cq.Plane(origin=o, xDir=b, normal=tan)
        wires.append(cq.Workplane(plane).rect(w, t).val())
    return cq.Workplane().add(cq.Solid.makeLoft(wires, False))


def _sweep_circle(points, d):
    pts = [V(*p) for p in points]
    path = cq.Edge.makeSpline(pts)
    tan = path.tangentAt(0).normalized()
    plane = cq.Plane(origin=pts[0], xDir=tan.cross(V(0, 0, 1)) if abs(tan.z) < 0.95 else V(1, 0, 0), normal=tan)
    return cq.Workplane(plane).circle(d / 2).sweep(cq.Workplane().add(cq.Wire.assembleEdges([path])))


def _mirror_x(wp: cq.Workplane) -> cq.Workplane:
    return wp.mirror("YZ")


# --------------------------------------------------------------------------- body


def pack_body(p: Params = P):
    y0, d = p.body_y0, p.body_d
    secs = [
        (0, 230, 150, y0 + 75, 55),
        (60, 268, 186, y0 + 93, 70),
        (200, 282, 198, y0 + 99, 75),
        (420, 284, 200, y0 + 100, 75),
        (560, 270, 188, y0 + 94, 70),
        (610, 250, 150, y0 + 78, 55),
    ]
    body = _loft_sections(secs)

    # roll-top closure: rolled collar with two side buckles
    roll = (
        cq.Workplane("XY")
        .box(244, 140, 44)
        .edges("|X")
        .fillet(20)
        .edges("|Y or |Z")
        .fillet(6)
        .translate((0, y0 + 78, 628))
    )
    body = body.union(roll)
    for s in (1, -1):
        clip = cq.Workplane("XY").box(10, 26, 60).edges("|X").fillet(4).translate((s * 127, y0 + 78, 600))
        body = body.union(clip)
    return body


def front_pocket(p: Params = P):
    """Stretch pocket on the outer face, with an inverted-trapezoid outline."""
    yf = p.body_y0 + 199
    secs = [
        (70, 170, 26, yf + 6, 10),
        (250, 226, 34, yf + 12, 14),
        (430, 236, 24, yf + 6, 10),
    ]
    pk = _loft_sections(secs)
    return pk


def compression_bands(p: Params = P):
    """Two bungee bands forming a V across the front pocket."""
    y0 = p.body_y0
    out = cq.Workplane("XZ").center(0, 296).circle(9).extrude(-8).translate((0, y0 + 236, 0))
    for s in (1, -1):
        band = _sweep_circle([(s * 96, y0 + 196, 528), (s * 56, y0 + 222, 420), (s * 4, y0 + 234, 300)], 5)
        anchor = cq.Workplane("XY").box(16, 8, 10).edges("|Y").fillet(3).translate((s * 96, y0 + 194, 530))
        band = band.union(anchor)
        out = out.union(band)
    return out


def side_pockets(p: Params = P):
    out = None
    for s in (1, -1):
        xc = s * (p.body_w / 2 - 2)
        sk = [
            _rrect(w, d, r).moved(cq.Location(V(xc, p.body_y0 + yc, z)))
            for z, w, d, yc, r in [(40, 24, 130, 100, 10), (150, 40, 166, 104, 16), (250, 34, 158, 108, 14), (290, 20, 140, 112, 8)]
        ]
        pk = cq.Workplane("XY").placeSketch(*sk).loft()
        out = pk if out is None else out.union(pk)
    return out


# --------------------------------------------------------------------------- frame


def y_frame(p: Params = P):
    """Y-shaped frame: two upper arms converge into one lower stem.

    Horizontally the top bar is concave towards the wearer; vertically the
    arms follow an S-curve with a forward (towards the wearer) lumbar bow.
    """
    yt, hw, zt, zn = 40.0, p.frame_top_half_w, p.frame_top_z, p.frame_node_z
    top = _sweep_circle([(-hw, yt, zt), (-55, yt + 9, zt + 6), (0, yt + 12, zt + 8), (55, yt + 9, zt + 6), (hw, yt, zt)], p.frame_rod_d)
    arm_r = _sweep_circle([(hw, yt, zt), (98, 36, 470), (66, 30, 340), (22, 30, 230), (0, 34, zn)], p.frame_rod_d)
    arm_l = _mirror_x(arm_r)
    stem = _sweep_circle([(0, 34, zn), (0, 33, 150), (0, 34, p.hub_z0 + 46)], p.frame_rod_d + 1)
    node = cq.Workplane("XZ").center(0, zn).circle(9).extrude(-14).translate((0, 27, 0))
    corner_r = cq.Workplane("XY").sphere(5.5).translate((hw, yt, zt))
    corner_l = cq.Workplane("XY").sphere(5.5).translate((-hw, yt, zt))
    return top.union(arm_r).union(arm_l).union(stem).union(node).union(corner_r).union(corner_l)


def mesh_panel(p: Params = P):
    """Suspended 3D-mesh panel with an hourglass outline (upper zone)."""
    secs = [
        (250, 196, 4, p.mesh_y + 6, 1.5),
        (330, 176, 4, p.mesh_y + 9, 1.5),
        (430, 214, 4, p.mesh_y + 8, 1.5),
        (540, 236, 4, p.mesh_y + 4, 1.5),
    ]
    m = _loft_sections(secs)
    top_cap = _sweep_rect([(-118, p.mesh_y + 8, 548), (0, p.mesh_y + 12, 553), (118, p.mesh_y + 8, 548)], 16, 6, (0, 0, 1))
    return m.union(top_cap)


def lumbar_pad(p: Params = P):
    """Lower tension zone: lumbar pad split by a vertical ventilation channel."""
    half = (
        cq.Workplane("XY")
        .box(92, 22, 118)
        .edges("|Y")
        .fillet(18)
        .edges(">Y or <Y")
        .fillet(4)
    )
    r = half.translate((50, 11, 182))
    return r.union(r.mirror("YZ"))


def tension_straps(p: Params = P):
    """Independent upper (U) and lower (L) zone tension webs with cam buckles."""
    parts = cq.Workplane("XY")
    for s in (1, -1):
        upper = _sweep_rect([(s * 96, p.mesh_y + 10, 548), (s * 104, 26, 556), (s * 110, 40, 560)], 20, 1.6, (0, 0, 1))
        buckle = cq.Workplane("XY").box(26, 8, 16).edges("|Y").fillet(3).translate((s * 104, 28, 556))
        lower = _sweep_rect([(s * 100, 20, 182), (s * 118, 34, 180), (s * 128, p.body_y0 + 6, 176)], 20, 1.6, (0, 0, 1))
        lbuckle = cq.Workplane("XY").box(10, 22, 18).edges("|X").fillet(3).translate((s * 120, 36, 180))
        parts = parts.union(upper).union(buckle).union(lower).union(lbuckle)
    return parts


# --------------------------------------------------------------------------- linkage hub


def hub_profile(p: Params = P) -> cq.Workplane:
    """Front-view outline of the linkage housing ("smile" shape) in the XZ plane."""
    hw = p.hub_w / 2 - 12
    z0 = p.hub_z0
    return (
        cq.Workplane("XZ")
        .moveTo(-hw, z0 + 18)
        .threePointArc((0, z0), (hw, z0 + 18))
        .threePointArc((hw + 12, z0 + 32), (hw, z0 + 46))
        .threePointArc((0, z0 + 32), (-hw, z0 + 46))
        .threePointArc((-hw - 12, z0 + 32), (-hw, z0 + 18))
        .close()
    )


def hub_housing(p: Params = P):
    hw = p.hub_w / 2 - 12
    z0 = p.hub_z0
    body = hub_profile(p).extrude(-p.hub_depth).translate((0, p.hub_y0, 0))
    try:
        body = body.edges("|Y").fillet(2.0).faces(">Y or <Y").edges().fillet(2.5)
    except Exception:
        pass

    # roller pockets at each end (open towards the top/outside)
    for s in (1, -1):
        pocket = (
            cq.Workplane("XZ")
            .center(s * hw, z0 + 32)
            .circle(p.roller_d / 2 + 2)
            .extrude(-(p.roller_len + 2))
            .translate((0, p.hub_y0 + (p.hub_depth - p.roller_len - 2) / 2, 0))
        )
        slot = (
            cq.Workplane("XY")
            .box(14, p.roller_len + 2, 30)
            .translate((s * (hw + 6), p.hub_y0 + p.hub_depth / 2, z0 + 44))
            .rotate((s * (hw + 6), 0, z0 + 44), (s * (hw + 6), 1, z0 + 44), -s * 35)
        )
        body = body.cut(pocket).cut(slot)

    # internal webbing channel between the rollers
    chan = (
        cq.Workplane("XY")
        .box(2 * hw, p.web_w + 2, 4)
        .translate((0, p.hub_y0 + p.hub_depth / 2, z0 + 32 - p.roller_d / 2 - 1))
    )
    body = body.cut(chan)

    # rear window exposing the mid-section of the web (cam lock + centring clip)
    window = (
        cq.Workplane("XY")
        .box(64, p.hub_depth / 2 + 2, 10)
        .edges("|Y")
        .fillet(3)
        .translate((0, p.hub_y0 + p.hub_depth * 0.75 + 1, z0 + 32 - p.roller_d / 2 - 1))
    )
    body = body.cut(window)

    # socket boss for the frame stem
    boss = (
        cq.Workplane("XY")
        .circle(8)
        .circle(p.frame_rod_d / 2 + 1.2)
        .extrude(16)
        .translate((0, 34, z0 + 30))
    )
    body = body.union(boss)

    # centering-elastic anchor posts
    for s in (1, -1):
        post = cq.Workplane("XZ").center(s * 24, z0 + 30).circle(3.5).extrude(-5).translate((0, p.hub_y0 + p.hub_depth + 5, 0))
        body = body.union(post)

    # rear lever bearing lugs
    for s in (1, -1):
        lug = cq.Workplane("XY").box(6, 10, 18).edges("|X").fillet(2.5).translate((s * 15, p.hub_y0 + p.hub_depth + 3, z0 + 20))
        body = body.union(lug)
    return body


def rollers(p: Params = P):
    hw = p.hub_w / 2 - 12
    out = cq.Workplane("XY")
    for s in (1, -1):
        r = (
            cq.Workplane("XZ")
            .center(s * hw, p.hub_z0 + 32)
            .circle(p.roller_d / 2)
            .circle(2.0)
            .extrude(-p.roller_len)
            .translate((0, p.hub_y0 + (p.hub_depth - p.roller_len) / 2, 0))
        )
        axle = (
            cq.Workplane("XZ")
            .center(s * hw, p.hub_z0 + 32)
            .circle(2.0)
            .extrude(-p.hub_depth + 2)
            .translate((0, p.hub_y0 + 1, 0))
        )
        out = out.union(r).union(axle)
    return out


def cam_lever(p: Params = P):
    """Cam lock lever on the pack-side face; rotates about X to clamp the web."""
    y = p.hub_y0 + p.hub_depth + 5
    z = p.hub_z0 + 20
    cam = cq.Workplane("YZ").center(y, z).circle(7).extrude(12, both=True)
    arm = (
        cq.Workplane("XY")
        .box(22, 6, 40)
        .edges("|Y")
        .fillet(4)
        .translate((0, y + 6, z - 18))
    )
    grip = cq.Workplane("XY").box(30, 9, 8).edges("|X").fillet(3).translate((0, y + 8, z - 38))
    return cam.union(arm).union(grip)


def pivot_plate(p: Params = P):
    """Hip-belt pivot plate on the wearer side of the hub (rotates about Y)."""
    disc = cq.Workplane("XZ").center(0, p.hub_z0 + 24).circle(20).extrude(-6).translate((0, p.hub_y0 - 6, 0))
    plate = (
        cq.Workplane("XZ")
        .center(0, p.hub_z0 + 22)
        .rect(190, 64)
        .extrude(-4)
        .edges("|Y")
        .fillet(18)
        .translate((0, p.hub_y0 - 10, 0))
    )
    return disc.union(plate)


def webbing(p: Params = P):
    """Linkage web: leaves each roller and runs up to the lower shoulder-strap end."""
    hw = p.hub_w / 2 - 12
    ym = p.hub_y0 + p.hub_depth / 2
    out = cq.Workplane("XY")
    for s in (1, -1):
        w = _sweep_rect(
            [(s * (hw + 8), ym, p.hub_z0 + 40), (s * 120, ym - 20, 160), (s * 150, -60, 260), (s * 140, -180, 330)],
            p.web_w,
            1.6,
            (0, 1, 0),
        )
        stop = cq.Workplane("XY").box(10, 24, 10).edges().fillet(2).translate((s * (hw + 22), ym - 4, p.hub_z0 + 62))
        out = out.union(w).union(stop)
    return out


# --------------------------------------------------------------------------- harness


def shoulder_strap(p: Params = P, side: int = 1):
    pts = [
        (side * 62, 8, 556),
        (side * 72, -30, 612),
        (side * 92, -110, 622),
        (side * 110, -190, 560),
        (side * 124, -222, 460),
        (side * 140, -198, 338),
    ]
    strap = _sweep_rect(pts, p.strap_w, p.strap_t, (1, 0, 0))
    bottle = (
        cq.Workplane("XY")
        .box(64, 40, 150)
        .edges("|Z")
        .fillet(16)
        .edges(">Z")
        .fillet(6)
        .translate((side * 124, -250, 452))
    )
    lifter = _sweep_rect([(side * 72, -34, 612), (side * 96, 8, 628), (side * 118, p.body_y0 + 6, 610)], 20, 1.6, (1, 0, 0))
    ladder = cq.Workplane("XY").box(30, 10, 22).edges("|Y").fillet(4).translate((side * 140, -190, 330))
    return strap.union(bottle).union(lifter).union(ladder)


def sternum_strap(p: Params = P):
    band = cq.Workplane("XY").box(220, 3, 20).translate((0, -232, 500))
    buckle = cq.Workplane("XY").box(44, 10, 24).edges("|Y").fillet(5).translate((0, -236, 500))
    return band.union(buckle)


def hip_belt(p: Params = P, side: int = 1):
    zc = p.hub_z0 + 34
    pts = [(side * 80, p.hub_y0 - 14, zc), (side * 140, -20, zc), (side * 180, -110, zc), (side * 168, -210, zc), (side * 120, -268, zc)]
    wing = _sweep_rect(pts, p.belt_h, p.belt_t, (0, 0, 1))
    pocket = (
        cq.Workplane("XY")
        .box(60, 130, 86)
        .edges("|Y")
        .fillet(22)
        .edges("|Z")
        .fillet(10)
        .translate((side * 204, -150, zc + 6))
        .rotate((side * 204, -150, 0), (side * 204, -150, 1), side * 22)
    )
    belt_web = _sweep_rect([(side * 120, -268, zc + 26), (side * 60, -292, zc + 26), (side * 18, -296, zc + 26)], 22, 2, (0, 0, 1))
    belt_web2 = belt_web.translate((0, 0, -52))
    out = wing.union(pocket).union(belt_web).union(belt_web2)
    if side == 1:
        buckle = cq.Workplane("XY").box(52, 12, 74).edges("|Y").fillet(6).translate((0, -300, zc))
        out = out.union(buckle)
    return out


# --------------------------------------------------------------------------- assemblies


HARD_PARTS = ("hub_housing", "rollers", "cam_lever", "pivot_plate", "y_frame")


def build_parts(p: Params = P) -> dict[str, cq.Workplane]:
    return {
        "pack_body": pack_body(p),
        "front_pocket": front_pocket(p),
        "compression_bands": compression_bands(p),
        "side_pockets": side_pockets(p),
        "y_frame": y_frame(p),
        "mesh_panel": mesh_panel(p),
        "lumbar_pad": lumbar_pad(p),
        "tension_straps": tension_straps(p),
        "hub_housing": hub_housing(p),
        "rollers": rollers(p),
        "cam_lever": cam_lever(p),
        "pivot_plate": pivot_plate(p),
        "webbing": webbing(p),
        "shoulder_strap_l": shoulder_strap(p, 1),
        "shoulder_strap_r": shoulder_strap(p, -1),
        "sternum_strap": sternum_strap(p),
        "hip_belt_l": hip_belt(p, 1),
        "hip_belt_r": hip_belt(p, -1),
    }


COLORS = {
    "pack_body": (0.20, 0.33, 0.42),
    "front_pocket": (0.55, 0.58, 0.60),
    "compression_bands": (0.95, 0.45, 0.10),
    "side_pockets": (0.55, 0.58, 0.60),
    "y_frame": (0.70, 0.70, 0.72),
    "mesh_panel": (0.40, 0.42, 0.45),
    "lumbar_pad": (0.30, 0.32, 0.35),
    "tension_straps": (0.95, 0.45, 0.10),
    "hub_housing": (0.22, 0.23, 0.25),
    "rollers": (0.85, 0.85, 0.85),
    "cam_lever": (0.95, 0.45, 0.10),
    "pivot_plate": (0.25, 0.25, 0.27),
    "webbing": (0.95, 0.45, 0.10),
    "shoulder_strap_l": (0.40, 0.42, 0.45),
    "shoulder_strap_r": (0.40, 0.42, 0.45),
    "sternum_strap": (0.25, 0.25, 0.27),
    "hip_belt_l": (0.40, 0.42, 0.45),
    "hip_belt_r": (0.40, 0.42, 0.45),
}


def build_assembly(parts: dict[str, cq.Workplane]) -> cq.Assembly:
    asm = cq.Assembly(name="backpack_40L")
    for name, wp in parts.items():
        asm.add(wp, name=name, color=cq.Color(*COLORS.get(name, (0.6, 0.6, 0.6))))
    return asm


def hub_module(parts: dict[str, cq.Workplane]) -> dict[str, cq.Workplane]:
    return {k: parts[k] for k in ("hub_housing", "rollers", "cam_lever", "pivot_plate")}


if __name__ == "__main__":
    ps = build_parts()
    for k, v in ps.items():
        bb = v.val().BoundingBox()
        print(f"{k:20s} valid={v.val().isValid()} bb=({bb.xmin:.0f},{bb.ymin:.0f},{bb.zmin:.0f})-({bb.xmax:.0f},{bb.ymax:.0f},{bb.zmax:.0f})")
