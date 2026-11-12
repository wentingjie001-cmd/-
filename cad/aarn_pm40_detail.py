"""Detailed reverse-engineered model of the Aarn Pace Magic 40: hollow fabric shells,
layered straps and belt, internal parts and hardware.

Outer shapes come from the photo-measured envelope in ``benchmark_aarn_pm40``. Every
part carries a ``basis``:
  实测     measured on the calibrated photos
  照片可见  visible in the photos, size estimated
  推断     not visible; inferred from Aarn's published descriptions/patents or common
           soft-goods construction
Fabric shells are modelled 1.2 mm thick (real 100D fabric is ~0.2 mm) so that they stay
valid solids and remain visible in sections.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq
import numpy as np

import aarn_hardware as hw
import benchmark_aarn_pm40 as env
from backpack_model import _sweep_circle

V = cq.Vector
Y0 = env.Y0
T_FAB = 1.2
Z_COLLAR = 585.0


@dataclass
class Part:
    key: str
    name: str
    group: str
    material: str
    qty: int
    basis: str
    color: tuple
    wp: cq.Workplane


GREEN = (0.55, 0.64, 0.20)
GREEN_DARK = (0.38, 0.46, 0.12)
MESH = (0.66, 0.68, 0.70)
MESH_DARK = (0.36, 0.37, 0.39)
WEB = (0.78, 0.79, 0.80)
HARD = (0.20, 0.21, 0.22)
TEAL = (0.02, 0.55, 0.55)
FOAM = (0.86, 0.80, 0.52)
METAL = (0.62, 0.63, 0.68)
TUBE = (0.92, 0.92, 0.90)
RED = (0.80, 0.12, 0.12)

# ----------------------------------------------------------------------------- geometry helpers


def body_section(z, inset=0.0):
    """(cx, cy, z, a, b_back, b_front) of the body envelope at height z, optionally inset."""
    yb, yf = env._interp(env.SIDE_BACK, z), env.body_front(z)
    b = (yf - yb) / 2 - inset
    return (0, (yb + yf) / 2, z, env._interp(env.REAR_HALF_W, z) - inset, b, b)


def body_front_y(z, x):
    """Y on the front face of the body envelope at (x, z)."""
    _, yc, _, a, _, b = body_section(z)
    n = 2.6
    r = min(abs(x) / a, 0.999)
    return yc + b * (1 - r**n) ** (1 / n)


def body_side_x(z, y, side):
    """X on the side face of the body envelope at (y, z)."""
    _, yc, _, a, bb, bf = body_section(z)
    n, b = (2.6, bf) if y >= yc else (4.0, bb)
    r = min(abs(y - yc) / b, 0.999)
    return side * a * (1 - r**n) ** (1 / n)


def _loft(secs, **kw):
    return env._soft_loft(secs, **kw)


def _inset(secs, d, z_from=None, z_to=None):
    out = []
    for cx, cy, z, a, bb, bf in secs:
        out.append((cx, cy, z, a - d, bb - d, bf - d))
    if z_from is not None:
        out[0] = (*out[0][:2], z_from, *out[0][3:])
    if z_to is not None:
        out[-1] = (*out[-1][:2], z_to, *out[-1][3:])
    return out


def _band(points, w, layers, wdir, inner, n=18):
    """Layered band along a spline. layers: [(offset, thickness)], offset measured towards ``inner``."""
    path = cq.Edge.makeSpline([V(*p) for p in points])
    o, wd, t = hw.path_frame(path, 0.5, wdir)
    ly = V(*t).cross(V(*wd))
    sgn = 1 if ly.dot(V(*inner)) >= 0 else -1
    out = []
    for off, th in layers:
        secs = []
        for i in range(n + 1):
            o, wd, t = hw.path_frame(path, i / n, wdir)
            pl = cq.Plane(origin=o, xDir=wd, normal=t)
            secs.append(cq.Workplane(pl).center(0, sgn * (off + th / 2)).rect(w, th).val())
        out.append(cq.Workplane().add(cq.Solid.makeLoft(secs, False)))
    return out, path, sgn


def _edge_binding(path, w, wdir, offset, sgn, d=3.0, n=16):
    """Two binding cords along the edges of a band."""
    tubes = []
    for e in (1, -1):
        pts = []
        for i in range(n + 1):
            o, wd, t = hw.path_frame(path, i / n, wdir)
            ly = V(*t).cross(V(*wd)) * sgn
            p = V(*o) + V(*wd) * (e * w / 2) + ly * offset
            pts.append((p.x, p.y, p.z))
        tubes.append(_sweep_circle(pts, d))
    return hw.compound(*tubes)


def _rim(sec, keep, d=4.0, npts=72, n_back=4.0, n_front=2.6):
    """Elastic hem cord along part of a section outline; keep(x, y) selects the points."""
    cx, cy, z, a, bb, bf = sec
    runs, cur = [], []
    for i in range(npts + 1):
        t = 2 * math.pi * i / npts
        c, s = math.cos(t), math.sin(t)
        n, b = (n_front, bf) if s >= 0 else (n_back, bb)
        x = cx + a * math.copysign(abs(c) ** (2 / n), c)
        y = cy + b * math.copysign(abs(s) ** (2 / n), s)
        if keep(x, y):
            cur.append((x, y, z))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return hw.compound(*[_sweep_circle(r, d) for r in runs if len(r) >= 3])


def _section_point(sec, t, n):
    cx, cy, z, a, bb, bf = sec
    c, s_ = math.cos(t), math.sin(t)
    b = bf if s_ >= 0 else bb
    return (cx + a * math.copysign(abs(c) ** (2 / n), c), cy + b * math.copysign(abs(s_) ** (2 / n), s_), z)


def _hollow(secs, t, open_top=True, n_back=2.6, n_front=2.6, bottom=None):
    """Fabric shell of a lofted pocket: same section heights inside and out, so the inner
    loft can never overshoot the outer one; the opening is a straight prism above the top."""
    outer = _loft(secs, n_back=n_back, n_front=n_front)
    ins = _inset(secs, t)
    b = bottom if bottom is not None else t
    ins[0] = (*ins[0][:2], ins[0][2] + b, *ins[0][3:])
    if not open_top:
        ins[-1] = (*ins[-1][:2], ins[-1][2] - t, *ins[-1][3:])
    inner = _loft(ins, n_back=n_back, n_front=n_front)
    if open_top:
        top = ins[-1]
        w = env._superellipse(*top, n_back=n_back, n_front=n_front)
        prism = cq.Workplane().add(cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), V(0, 0, 40))).translate((0, 0, -2))
        inner = inner.union(prism)
    return outer.cut(inner)


def _surface_item(item, origin, outward, up=(0, 0, 1)):
    zdir = V(*up)
    out = V(*outward).normalized()
    zdir = (zdir - out * zdir.dot(out)).normalized()
    xdir = zdir.cross(out)
    return hw.place(item, origin, (xdir.x, xdir.y, xdir.z), (zdir.x, zdir.y, zdir.z))


# ----------------------------------------------------------------------------- pack body


def _body_secs(zs):
    return [body_section(z) for z in zs]


LOW_Z = [z for z in env.BODY_Z if z < Z_COLLAR] + [Z_COLLAR]
TOP_Z = [Z_COLLAR] + [z for z in env.BODY_Z if z > Z_COLLAR]


def body_outer_low():
    return _loft(_body_secs(LOW_Z), n_back=4.0, n_front=2.6)


def body_parts(parts):
    outer = body_outer_low()
    inner_secs = [body_section(3.5, inset=T_FAB + 0.6)] + [body_section(z, inset=T_FAB) for z in LOW_Z[1:-1] + [Z_COLLAR + 12]]
    inner = _loft(inner_secs, n_back=4.0, n_front=2.6)
    shell = outer.cut(inner)
    base_box = cq.Workplane("XY").box(400, 400, 45, centered=(True, True, False)).translate((0, 100, -1))
    parts.append(Part("A01", "主仓筒身（40 L，上口敞开）", "主包体", "100D Robic 尼龙（含 UHMWPE）", 1, "实测", GREEN, shell.cut(base_box)))
    parts.append(Part("A02", "包底（双层加强）", "主包体", "210D Duramax", 1, "实测外形 / 推断层数", GREEN_DARK, shell.intersect(base_box)))

    top = _loft(_body_secs(TOP_Z), n_back=4.0, n_front=2.6)
    top_in = _loft([body_section(z, inset=4.0) for z in [Z_COLLAR - 6] + TOP_Z[1:-1] + [655]], n_back=4.0, n_front=2.6)
    parts.append(Part("A03", "卷口收口（已卷合状态，按 3 层等效 4 mm）", "主包体", "100D Robic", 1, "实测外形 / 推断卷数", GREEN, top.cut(top_in)))

    ring = cq.Workplane("XZ").center(103, 658).circle(12).circle(8).extrude(-4).translate((0, 40, 0))
    parts.append(Part("A04", "顶部挂环", "主包体", "TPU 包胶", 1, "照片可见", TEAL, ring))
    return outer


def top_closure(parts):
    pts = [(0, 2, 556), (0, -14, 590), (0, -12, 615), (0, 8, 640), (0, 50, 656), (0, 100, 660), (0, 140, 655), (0, 172, 643), (0, 193, 623)]
    (web,), path, _ = _band(pts, 20, [(0, 1.6)], (1, 0, 0), (0, 1, 0))
    parts.append(Part("A05", "卷口压缩带", "主包体", "20 mm 尼龙织带", 1, "照片可见", WEB, web))
    o, wd, t = hw.path_frame(path, 0.16, (1, 0, 0))
    b = hw.side_release_buckle(20)
    parts.append(Part("H01", "卷口压缩带插扣（20 mm）", "五金", "POM", 1, "照片可见", HARD, hw.compound(hw.place(b["female"], o, wd, t), hw.place(b["male"], o, wd, t))))


def zips(parts):
    # (9) secured zipped pocket across the top front of the collar
    z = 646
    pts = [(x, body_front_y(z, x) + 0.8, z + 0.02 * x) for x in np.linspace(-70, 80, 7)]
    zp = hw.zipper(pts, (0, -0.7, 0.7), tape_w=20, slider_u=0.9)
    parts.append(Part("Z01", "顶部安全袋拉链（⑨，约 150 mm）", "拉链", "#3 尼龙线圈拉链", 1, "照片可见", MESH, hw.compound(zp["tape"], zp["teeth"])))
    parts.append(Part("Z02", "顶部安全袋拉头 + 拉绳", "拉链", "锌合金拉头 / 尼龙绳", 1, "照片可见", HARD, hw.compound(zp["slider"], zp["pull_cord"])))
    secs = [cq.Workplane(cq.Plane(origin=(5, body_front_y(z, 0) - 14, z), xDir=(1, 0, 0), normal=(0, 0, 1))).rect(110 - (0 if z > 530 else 16), 2).val() for z in (515, 555, 595, 628)]
    pouch = cq.Workplane().add(cq.Solid.makeLoft(secs, True))
    parts.append(Part("I01", "顶部安全袋内袋（吊在拉链下方）", "内部", "20D 尼龙", 1, "推断", (0.82, 0.86, 0.6), pouch))

    # side-access zips near the back edge, both sides
    items = []
    for side in (1, -1):
        y = Y0 + 23
        p = [(body_side_x(zz, y, side) + side * 0.8, y, zz) for zz in np.linspace(300, 482, 6)]
        items.append(hw.zipper(p, (0, 1, 0), tape_w=20, slider_u=0.95))
    parts.append(Part("Z03", "侧面竖向拉链（约 180 mm）", "拉链", "#5 尼龙线圈拉链", 2, "照片可见", MESH, hw.compound(*[i["tape"] for i in items], *[i["teeth"] for i in items])))
    parts.append(Part("Z04", "侧面拉链拉头 + 拉绳", "拉链", "锌合金拉头 / 尼龙绳", 2, "照片可见", HARD, hw.compound(*[i["slider"] for i in items], *[i["pull_cord"] for i in items])))


# ----------------------------------------------------------------------------- pockets


def front_pocket(parts, body_low):
    z0, z1 = env.FRONT_POCKET
    secs = []
    for z, a in [(z0, 86), (z0 + 40, 104), (150, 110), (260, 112), (360, 110), (z1 - 15, 104), (z1, 96)]:
        yf = env._interp(env.SIDE_FRONT, z) - (8 if z in (z0, z1) else 0)
        yb = env.body_front(z) - 12
        secs.append((0, (yb + yf) / 2, z, a, (yf - yb) / 2, (yf - yb) / 2))
    fabric = _hollow(secs, 1.0, n_back=3.0, n_front=3.0).cut(body_low)
    parts.append(Part("P01", "前部弹力网袋（上口敞开）", "外袋", "Darlington 弹力网布 240 g", 1, "实测", MESH, fabric))
    top = secs[-2]
    hem = _rim((0, top[1], z1 - 16, top[3] - 0.5, top[4], top[5] - 0.5), lambda x, y: y > env.body_front(z1 - 16) + 2, d=4, n_back=3.0, n_front=3.0)
    parts.append(Part("P02", "前网袋袋口包边松紧带", "外袋", "10 mm 松紧带", 1, "照片可见", WEB, hem))
    tab = hw.webbing_loop(16, 30, 5)
    parts.append(Part("P03", "前网袋拉手", "外袋", "16 mm 织带", 1, "照片可见", WEB, _surface_item(tab, (0, env._interp(env.SIDE_FRONT, z1 - 22), z1 - 22), (0, 1, 0))))


def side_pockets(parts, body_low):
    secs = []
    for z, a in env.SIDE_POCKET_HALF_W:
        yb, yf = Y0 + 6, env.body_front(z) - 6
        secs.append((0, (yb + yf) / 2, z, a, (yf - yb) / 2, (yf - yb) / 2))
    fabric = _hollow(secs, T_FAB, n_back=3.2, n_front=3.2).cut(body_low)
    parts.append(Part("P04", "侧袋（左右各 1，上口敞开）", "外袋", "100D Robic + 弹力包边", 2, "实测", (0.50, 0.60, 0.17), fabric))
    z = 370
    s = [x for x in secs if x[2] == 360][0]
    bw = env._interp(env.REAR_HALF_W, z)
    hem = _rim((0, s[1], z, s[3] - 1.5, s[4], s[5]), lambda x, y: abs(x) > bw + 2, d=4, n_back=3.2, n_front=3.2)
    parts.append(Part("P05", "侧袋袋口松紧包边（内衬为点缀色）", "外袋", "松紧带 / 点缀色内衬", 2, "照片可见", (0.95, 0.75, 0.15), hem))


def drawcord(parts):
    anchors = [(-112, 545), (-112, 470), (112, 470), (112, 545)]
    loops = []
    for x, z in anchors:
        y = body_front_y(z, x)
        loops.append(_surface_item(hw.webbing_loop(10, 18, 4, 1.2), (x, y, z), (x / 300, 1, 0)))
    parts.append(Part("F01", "压缩绳穿绳环 / 上部登山杖挂点", "前部", "10 mm 织带", 4, "照片可见", WEB, hw.compound(*loops)))
    cords = []
    for path in ([(-112, 545), (0, 440), (112, 545)], [(-112, 470), (0, 440), (112, 470)]):
        for (x0, z0), (x1, z1) in zip(path, path[1:]):
            xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
            cords.append(_sweep_circle([(x0, body_front_y(z0, x0) + 4, z0), (xm, body_front_y(zm, xm) + 3, zm), (x1, body_front_y(z1, x1) + 4, z1)], 3.5))
    tail = _sweep_circle([(0, body_front_y(432, 0) + 5, 432), (2, body_front_y(400, 0) + 14, 400), (0, body_front_y(370, 0) + 18, 372)], 3.5)
    parts.append(Part("F02", "前部压缩弹力绳（⑩）", "前部", "Ø3.5 mm 弹力绳", 1, "照片可见", WEB, hw.compound(*cords, tail)))
    cl = hw.cord_lock(3.5)
    y = body_front_y(440, 0) + 10
    lock = [_surface_item(cl[k], (0, y, 440), (0, 1, 0)) for k in ("barrel", "plunger")]
    parts.append(Part("H02", "压缩绳绳扣（弹簧式）", "五金", "POM / 不锈钢弹簧", 1, "照片可见", HARD, hw.compound(*lock)))
    parts.append(Part("H03", "绳扣弹簧", "五金", "不锈钢", 1, "推断", METAL, _surface_item(cl["spring"], (0, y, 440), (0, 1, 0))))
    parts.append(Part("H04", "压缩绳尾端拉扣", "五金", "POM", 1, "照片可见", HARD, hw.place(hw.cord_toggle(), (0, body_front_y(370, 0) + 18, 364), (1, 0, 0), (0, 0, 1))))

    axe = []
    for x, w in ((0, 25), (-88, 16), (88, 16)):
        z = 34
        y = body_front_y(z, x)
        axe.append(_surface_item(hw.webbing_loop(w, 44 if x == 0 else 30, 6), (x, y, z), (0, 0.8, -0.6), up=(0, 0.6, 0.8)))
    parts.append(Part("F03", "冰镐挂环 ×1 + 登山杖挂环 ×2（⑪）", "前部", "25 / 16 mm 织带", 3, "照片可见", WEB, hw.compound(*axe)))


LASSO_SPOTS = [
    ("front", -105, 500), ("front", 105, 500), ("front", -112, 300), ("front", 112, 300), ("front", -70, 30), ("front", 70, 30),
    ("side", -1, 470), ("side", 1, 470), ("pocket", -1, 300), ("pocket", 1, 300), ("side", -1, 560), ("side", 1, 560),
]


def lasso_locs(parts):
    tabs, cords, grips = [], [], []
    for kind, v, z in LASSO_SPOTS:
        if kind == "front":
            o, n = (v, body_front_y(z, v) + 0.8, z), (v / 250, 1, 0)
        elif kind == "side":
            y = Y0 + 34
            o, n = (body_side_x(z, y, v) + v * 0.8, y, z), (v, 0, 0)
        else:
            a = env._interp(env.SIDE_POCKET_HALF_W, z)
            o, n = (v * (a + 0.8), Y0 + 40, z), (v, 0, 0)
        item = hw.lasso_loc_tab()
        tabs.append(_surface_item(item["tab"], o, n))
        cords.append(_surface_item(item["cord"], o, n))
        grips.append(_surface_item(item["grip"], o, n))
    parts.append(Part("F04", "Lasso Loc 挂扣标签（⑭）", "前部", "织带标签", 12, "照片可见（位置估计）", TEAL, hw.compound(*tabs)))
    parts.append(Part("F05", "Lasso Loc 弹力绳圈", "前部", "Ø2.4 mm 弹力绳", 12, "照片可见", TEAL, hw.compound(*cords)))
    parts.append(Part("H05", "Lasso Loc 绳夹", "五金", "POM", 12, "推断", HARD, hw.compound(*grips)))


# ----------------------------------------------------------------------------- back system


def back_system(parts):
    outline = [(205, 92), (300, 100), (420, 106), (500, 110), (552, 112)]
    mesh = env._xz_plate(outline, 6, 3)
    parts.append(Part("B01", "悬浮透气网背板（⑦，外圈浅色）", "背负系统", "3D 间隔网布 3 mm", 1, "实测", MESH, mesh))
    pts = [(w, 4.5, z) for z, w in outline] + [(-w, 4.5, z) for z, w in reversed(outline)] + [(outline[0][1], 4.5, outline[0][0])]
    binding = _sweep_circle(pts[: len(outline)], 3).union(_sweep_circle(pts[len(outline) - 1 : len(outline) + 1], 3)).union(
        _sweep_circle(pts[len(outline) : 2 * len(outline)], 3)
    ).union(_sweep_circle([pts[2 * len(outline) - 1], (0, 4.5, outline[0][0] - 1.5), pts[0]], 3))
    parts.append(Part("B02", "网背板包边", "背负系统", "20 mm 包边带", 1, "照片可见", WEB, binding))
    parts.append(Part("B03", "中部深色 Y 形网", "背负系统", "六角网布", 1, "实测", MESH_DARK, env.mesh_back_dark()))

    foam = cq.Workplane("XZ").center(0, 135).rect(132, 144).extrude(-16).edges("|Y").fillet(28).translate((0, 4, 0))
    cover = cq.Workplane("XZ").center(0, 135).rect(136, 148).extrude(-22).edges("|Y").fillet(30).faces("<Y").edges().fillet(6)
    cover = cover.cut(cq.Workplane("XZ").center(0, 135).rect(133.6, 145.6).extrude(-19.6).edges("|Y").fillet(28.8).translate((0, 1.2, 0)))
    parts.append(Part("B04", "腰垫外套（网布）", "背负系统", "3D 间隔网布", 1, "实测外形", MESH_DARK, cover))
    parts.append(Part("B05", "腰垫泡棉芯（16 mm）", "内部", "EVA 泡棉", 1, "推断", FOAM, foam))

    (bar,), path, _ = _band([(-113, 14, 554), (0, 10, 556), (113, 14, 554)], 20, [(0, 1.6)], (0, 0, 1), (0, 1, 0))
    tails = []
    locks = []
    for s in (1, -1):
        (tl,), tp, _ = _band([(s * 113, 18, 556), (s * 122, 30, 560), (s * 128, Y0 + 2, 566)], 20, [(0, 1.6)], (0, 0, 1), (0, 1, 0))
        tails.append(tl)
        locks.append(hw.place(hw.ladder_lock(20), (s * 113, 16, 554), (0, 0, 1), (s, 0, 0)))
    parts.append(Part("B06", "背板张紧带（⑧，顶部横带 + 两端调节尾带）", "背负系统", "20 mm 织带", 1, "实测", WEB, hw.compound(bar, *tails)))
    parts.append(Part("H06", "背板张紧梯扣", "五金", "POM", 2, "照片可见", HARD, hw.compound(*locks)))

    ties = []
    for s in (1, -1):
        for z in (300, 450):
            w = env._interp([(p[0], p[1]) for p in outline], z)
            x_body = body_side_x(z, Y0 + 4, s)
            (t,), _, _ = _band([(s * (w - 4), 7, z), (s * (w + 8), 18, z), (s * (x_body - 2), Y0 + 3, z)], 12, [(0, 1.2)], (0, 0, 1), (0, 1, 0), n=6)
            ties.append(t)
    parts.append(Part("B07", "网背板侧边弹性拉片", "背负系统", "12 mm 松紧带", 4, "推断", WEB, hw.compound(*ties)))

    rods, caps = [], []
    for s, yc in ((1, 17), (-1, 23)):
        pts = [(s * 100, 24, 548), (s * 50, yc + 1, 455), (0, yc, 370), (-s * 50, yc + 1, 285), (-s * 92, 24, 165)]
        rods.append(_sweep_circle(pts, 5))
        for p, q in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            d = V(*p) - V(*q)
            d = d.normalized()
            c = V(*p) - d * 6
            caps.append(cq.Workplane(cq.Plane(origin=c, xDir=d.cross(V(0, 1, 0)).normalized(), normal=d)).circle(5).extrude(16).faces(">Z").fillet(2.5))
    parts.append(Part("B08", "X 形支撑杆 ×2（Ø5 mm，预弯）", "背负系统", "铝合金 / 弹簧钢（推断）", 2, "照片可见（交叉段）/ 推断（端点、截面）", METAL, hw.compound(*rods)))
    parts.append(Part("B09", "支撑杆端头保护套 + 杆袋", "内部", "加厚尼龙 + TPU 端套", 4, "推断", HARD, hw.compound(*caps)))
    hub = cq.Workplane("XZ").center(0, 370).circle(10).extrude(-8).translate((0, 10, 0))
    hub = hub.cut(cq.Workplane("XZ").center(0, 370).rect(30, 5.4).extrude(-3).translate((0, 15.2, 0)).rotate((0, 0, 370), (0, 1, 370), 40))
    hub = hub.cut(cq.Workplane("XZ").center(0, 370).rect(30, 5.4).extrude(-3).translate((0, 12.0, 0)).rotate((0, 0, 370), (0, 1, 370), -40))
    parts.append(Part("B10", "支撑杆交叉卡座", "背负系统", "尼龙 PA6", 1, "推断", HARD, hub))


# ----------------------------------------------------------------------------- harness


STRAP_LAYERS = [(0.0, 2.5), (2.5, 8.0), (10.5, 1.0)]  # inner 3D mesh, foam, outer shell (from the wearer side)


def harness(parts):
    meshes, foams, shells, bindings, rails, tacks, locks, lifters, bottles, hems, flocks, bungies = ([] for _ in range(12))
    for side in (1, -1):
        pts = [(side * x, y, z) for x, y, z in env.STRAP_PATH]
        wdir = (side * 0.75, 0.66, 0)
        (mesh, shell), path, sgn = _band(pts, 52, [STRAP_LAYERS[0], STRAP_LAYERS[2]], wdir, (0, 1, 0), n=22)
        meshes.append(mesh)
        foams.append(_band(pts, 48, [STRAP_LAYERS[1]], wdir, (0, 1, 0), n=22)[0][0])
        shells.append(shell)
        bindings.append(_edge_binding(path, 52, wdir, 5.75, sgn, d=3.2))
        # sternum rail on the inner edge (towards the body centre line)
        rail_pts = []
        for u in np.linspace(0.62, 0.92, 7):
            o, wd, t = hw.path_frame(path, u, wdir)
            ly = V(*t).cross(V(*wd)) * sgn
            p = V(*o) - V(*wd) * (18) - ly * 1.2
            rail_pts.append((p.x, p.y, p.z))
        (rail,), rpath, _ = _band(rail_pts, 15, [(0, 1.5)], wdir, (0, 1, 0), n=10)
        rails.append(rail)
        tacks.append(hw.bar_tacks(rpath, wdir, np.linspace(0.04, 0.96, 7), w=13))
        # lower adjuster where the U-Flow web joins the strap
        o, wd, t = hw.path_frame(path, 0.99, wdir)
        locks.append(hw.place(hw.ladder_lock(20), (o[0], o[1] - 2, o[2] - 10), (side, 0, 0), (0.6 * side, 0.6, -0.5)))
        # load lifter
        (lf,), lpath, _ = _band([(side * 72, -60, 508), (side * 94, -20, 530), (side * 108, 12, 548)], 20, [(0, 1.6)], (1, 0, 0), (0, 1, 0), n=8)
        lifters.append(lf)
        o, wd, t = hw.path_frame(lpath, 0.12, (1, 0, 0))
        locks.append(hw.place(hw.ladder_lock(20), o, wd, t))
        # bottle pocket (13): hollow mesh pocket, open top with drawcord
        bx, by, z0, z1 = side * env.BOTTLE["x"], env.BOTTLE["y"], env.BOTTLE["z0"], env.BOTTLE["z1"]
        secs = [(bx, by, z0, 26, 30, 30), (bx, by, z0 + 18, 35, 40, 40), (bx, by, 290, 39, 43, 43), (bx, by, z1 - 15, 39, 43, 43), (bx, by, z1, 34, 38, 38)]
        bottles.append(_hollow(secs, 1.0, n_back=2.6, n_front=2.6, bottom=1.5))
        hems.append(_rim((bx, by, z1 - 4, 34.5, 39, 39), lambda x, y, bx=bx, by=by: not (y < by - 25 and abs(x - bx) < 9), d=3.5, n_back=2.6, n_front=2.6))
        cl = hw.cord_lock(3)
        top = (bx, by - 40, z1 + 4)
        flocks.append(hw.compound(*[hw.place(cl[k], top, (side, 0, 0), (0, 0, 1)) for k in ("barrel", "plunger")]))
        bungies.append(_sweep_circle([(bx, by - 10, z0 + 4), (bx, by - 22, 160), (side * 88, -195, 146)], 3))
    parts.append(Part("S01", "肩带内层 3D 网布（贴身面）", "肩带", "3D 间隔网布 2.5 mm", 2, "照片可见", MESH, hw.compound(*meshes)))
    parts.append(Part("S02", "肩带泡棉芯（8 mm）", "内部", "EVA / PE 泡棉", 2, "推断", FOAM, hw.compound(*foams)))
    parts.append(Part("S03", "肩带外层面布", "肩带", "100D Robic", 2, "照片可见", MESH, hw.compound(*shells)))
    parts.append(Part("S04", "肩带包边", "肩带", "20 mm 包边带", 4, "照片可见", WEB, hw.compound(*bindings)))
    parts.append(Part("S05", "胸带滑轨织带 + 打结（套结）", "肩带", "15 mm 织带", 2, "照片可见（pm40_10）", WEB, hw.compound(*rails, *tacks)))
    parts.append(Part("S06", "负重调节带（②）", "肩带", "20 mm 织带", 2, "实测", WEB, hw.compound(*lifters)))
    parts.append(Part("H07", "肩带梯扣（下端 U-Flow 调节 ×2，负重调节带 ×2）", "五金", "POM", 4, "照片可见", HARD, hw.compound(*locks)))
    parts.append(Part("S07", "肩带 750 ml 弹力网袋（⑬，上口敞开）", "肩带", "弹力网布", 2, "实测", MESH, hw.compound(*bottles)))
    parts.append(Part("S08", "网袋口抽绳", "肩带", "Ø3 mm 弹力绳", 2, "照片可见", RED, hw.compound(*hems)))
    parts.append(Part("H08", "网袋口绳扣", "五金", "POM", 2, "照片可见", HARD, hw.compound(*flocks)))
    parts.append(Part("S09", "弹力稳定绳（③，网袋 → 腰包）", "肩带", "Ø3 mm 弹力绳", 2, "照片可见", TEAL, hw.compound(*bungies)))

    webs, buckles, sliders = [], [], []
    for z in (324, 214):
        y = env._strap_y(z) - 9
        (w,), _, _ = _band([(-36, y, z), (0, y - 3, z), (36, y, z)], 16, [(0, 1.4)], (0, 0, 1), (0, 1, 0), n=6)
        webs.append(w)
        b = hw.side_release_buckle(16)
        buckles.append(hw.place(b["female"], (0, y - 5, z), (0, 0, 1), (1, 0, 0)))
        buckles.append(hw.place(b["male"], (0, y - 5, z), (0, 0, 1), (1, 0, 0)))
        for s in (1, -1):
            sliders.append(hw.place(hw.sternum_slider(), (s * 38, y + 2, z), (s, 0, 0), (0, 0, 1)))
    parts.append(Part("S10", "胸带织带 ×2（①，高度可调）", "肩带", "16 mm 织带", 2, "实测", WEB, hw.compound(*webs)))
    parts.append(Part("H09", "胸带插扣（16 mm）", "五金", "POM", 2, "照片可见", HARD, hw.compound(*buckles)))
    parts.append(Part("H10", "胸带滑钩", "五金", "POM", 4, "照片可见", HARD, hw.compound(*sliders)))


def uflow(parts):
    half = [(60, -58, 182), (98, -14, 158), (124, 45, 110), (128, 95, 66), (117, 92, 58), (95, 62, 26), (0, 55, 16)]
    pts = [(-x, y, z) for x, y, z in half] + [(x, y, z) for x, y, z in reversed(half[:-1])]
    (web,), path, _ = _band(pts, 20, [(0, 1.6)], (0, 1, 0), (0, 0, 1), n=40)
    parts.append(Part("U01", "U-Flow 联动带（⑥，左右肩带下端经包底连成一根）", "U-Flow", "20 mm 低摩擦织带", 1, "照片可见（外露段）/ 推断（包内段）", WEB, web))
    tube_pts = [(-95, 62, 26), (-50, 57, 18), (0, 55, 16), (50, 57, 18), (95, 62, 26)]
    tube_path = cq.Edge.makeSpline([V(*p) for p in tube_pts])
    t0 = tube_path.tangentAt(0)
    outer = cq.Workplane(cq.Plane(origin=V(*tube_pts[0]), xDir=t0.cross(V(0, 0, 1)).normalized(), normal=t0)).rect(26, 9).sweep(cq.Workplane().add(cq.Wire.assembleEdges([tube_path])))
    inner = cq.Workplane(cq.Plane(origin=V(*tube_pts[0]) - t0 * 2, xDir=t0.cross(V(0, 0, 1)).normalized(), normal=t0)).rect(23, 5).sweep(
        cq.Workplane().add(cq.Wire.assembleEdges([cq.Edge.makeSpline([V(*tube_pts[0]) - t0 * 2] + [V(*p) for p in tube_pts[1:-1]] + [V(*tube_pts[-1]) + tube_path.tangentAt(1) * 2])]))
    )
    parts.append(Part("U02", "包底低摩擦扁管（U 形通道）", "内部", "HDPE / PTFE 涂层扁管", 1, "推断（Aarn 专利 US2006/0131355 所述“低摩擦 U 形管”）", TUBE, outer.cut(inner)))
    ports = []
    for s in (1, -1):
        y, z = 92, 60
        x = body_side_x(z, y, s)
        ports.append(_surface_item(cq.Workplane("XY").box(30, 2.0, 16).edges("|Y").fillet(6).cut(cq.Workplane("XY").box(22, 4, 4)), (x + s * 1.0, y, z), (s, 0, 0), up=(0, -0.5, 1)))
    parts.append(Part("U03", "侧面织带出口加强片", "U-Flow", "TPU 加强片", 2, "推断", HARD, hw.compound(*ports)))


def hip_belt(parts):
    tilt = (0, (env.BELT["z_front"] - env.BELT["z_back"]) / (env.BELT["y_back"] - env.BELT["y_front"]), 1)
    meshes, foams, shells, bindings, webs, locks, buckles, pockets, zips_t, zips_s = ([] for _ in range(10))
    for side in (1, -1):
        wing_pts = [env._belt_point(side, phi) for phi in np.linspace(0.18, 2.25, 9)]
        inward = (-side, 0.3, 0)
        (mesh, shell), path, sgn = _band(wing_pts, env.BELT["h"], [(0, 2.0), (10.0, 1.0)], tilt, inward, n=18)
        meshes.append(mesh)
        foams.append(_band(wing_pts, env.BELT["h"] - 6, [(2.0, 8.0)], tilt, inward, n=18)[0][0])
        shells.append(shell)
        bindings.append(_edge_binding(path, env.BELT["h"], tilt, 5.5, sgn, d=3.2))
        for dz in (28, -28):
            wp = [env._belt_point(side, phi) for phi in np.linspace(1.2, math.pi, 8)]
            wp = [(x, y, z + dz) for x, y, z in wp]
            (w,), wpath, _ = _band(wp, 20, [(0, 1.6)], tilt, inward, n=12)
            webs.append(w)
            o, wd, t = hw.path_frame(wpath, 0.55, tilt)
            locks.append(hw.place(hw.ladder_lock(20), o, wd, t))
        px, py, z0, z1 = side * env.HIP_POCKET["x"], env.HIP_POCKET["y"], env.HIP_POCKET["z0"], env.HIP_POCKET["z1"]
        secs = [(px, py, z0, 36, 58, 58), (px, py, z0 + 25, 54, 82, 82), (px, py, 45, 58, 88, 88), (px, py, 110, 53, 80, 80), (px, py, z1, 38, 60, 60)]
        pockets.append(_hollow(secs, T_FAB, open_top=False, n_back=2.4, n_front=2.4))
        zsec = (px, py, 124, 46, 70, 70)
        zpts = []
        for k, ang in enumerate(np.linspace(-62, 62, 7)):
            t = math.radians(ang) if side == 1 else math.pi - math.radians(ang)
            x, y, _ = _section_point(zsec, t, 2.4)
            zpts.append((x + side * 0.8, y, 124 + 8 * math.cos(math.radians(ang))))
        zp = hw.zipper(zpts, (0, 0, 1), tape_w=18, slider_u=0.1)
        zips_t.append(hw.compound(zp["tape"], zp["teeth"]))
        zips_s.append(hw.compound(zp["slider"], zp["pull_cord"]))
    x, y, z = env._belt_point(1, math.pi)
    for dz in (28, -28):
        b = hw.side_release_buckle(20)
        buckles.append(hw.place(b["female"], (0, y - 3, z + dz), (0, 0, 1), (1, 0, 0)))
        buckles.append(hw.place(b["male"], (0, y - 3, z + dz), (0, 0, 1), (1, 0, 0)))
    parts.append(Part("W01", "腰带翼内层网布（贴身面）", "腰带", "3D 间隔网布 2 mm", 2, "照片可见", MESH, hw.compound(*meshes)))
    parts.append(Part("W02", "腰带翼泡棉芯（8 mm）", "内部", "EVA 泡棉", 2, "推断", FOAM, hw.compound(*foams)))
    parts.append(Part("W03", "腰带翼外层面布", "腰带", "100D Robic", 2, "照片可见", GREEN, hw.compound(*shells)))
    parts.append(Part("W04", "腰带翼包边", "腰带", "20 mm 包边带", 4, "照片可见", WEB, hw.compound(*bindings)))
    parts.append(Part("W05", "Auto-Form 上下双织带（④）", "腰带", "20 mm 织带", 4, "照片可见", WEB, hw.compound(*webs)))
    parts.append(Part("H11", "腰带梯扣", "五金", "POM", 4, "照片可见", HARD, hw.compound(*locks)))
    parts.append(Part("H12", "腰带前插扣（上下各 1，20 mm）", "五金", "POM", 2, "照片可见", HARD, hw.compound(*buckles)))
    parts.append(Part("W06", "1.5 L 腰包（⑫，闭合状态）", "腰带", "100D Robic", 2, "实测", GREEN, hw.compound(*pockets)))
    parts.append(Part("Z05", "腰包拉链", "拉链", "#5 尼龙线圈拉链", 2, "照片可见", MESH, hw.compound(*zips_t)))
    parts.append(Part("Z06", "腰包拉头 + 拉绳", "拉链", "锌合金拉头 / 尼龙绳", 2, "照片可见", HARD, hw.compound(*zips_s)))


def build_detailed_parts() -> list[Part]:
    parts: list[Part] = []
    body_low = body_parts(parts)
    top_closure(parts)
    zips(parts)
    front_pocket(parts, body_low)
    side_pockets(parts, body_low)
    drawcord(parts)
    lasso_locs(parts)
    back_system(parts)
    harness(parts)
    uflow(parts)
    hip_belt(parts)
    return parts


# exploded view: offset per assembly (hardware, zips and internal parts travel with the part they belong to)
EXPLODE = {
    "body": (0, 0, 0),
    "collar": (0, 0, 150),
    "pouch": (0, 60, 90),
    "front": (0, 170, 0),
    "side": (0, 0, 0),
    "back": (0, -170, 0),
    "stays": (0, -110, 0),
    "harness": (0, -340, 60),
    "uflow": (0, -40, -140),
    "belt": (0, -340, -250),
}
EXPLODE_OF = {
    "A01": "body", "A02": "body", "A03": "collar", "A04": "collar", "A05": "collar", "H01": "collar", "Z01": "collar", "Z02": "collar",
    "I01": "pouch", "Z03": "body", "Z04": "body", "P01": "front", "P02": "front", "P03": "front", "P04": "side", "P05": "side",
    "F01": "front", "F02": "front", "H02": "front", "H03": "front", "H04": "front", "F03": "body", "F04": "body", "F05": "body", "H05": "body",
    "B01": "back", "B02": "back", "B03": "back", "B04": "back", "B05": "back", "B06": "back", "H06": "back", "B07": "back",
    "B08": "stays", "B09": "stays", "B10": "stays", "U01": "uflow", "U02": "uflow", "U03": "uflow",
}


def explode_offset(key):
    if key in EXPLODE_OF:
        return EXPLODE[EXPLODE_OF[key]]
    if key[0] == "S" or key in ("H07", "H08", "H09", "H10"):
        return EXPLODE["harness"]
    return EXPLODE["belt"]


if __name__ == "__main__":
    import time

    t = time.time()
    ps = build_detailed_parts()
    for p in ps:
        s = p.wp.val()
        bb = s.BoundingBox()
        print(f"{p.key} {p.name[:22]:24s} valid={s.isValid()} vol={s.Volume():10.0f} z[{bb.zmin:.0f},{bb.zmax:.0f}]")
    print(len(ps), "parts", f"{time.time() - t:.0f}s")
