"""A1 flat patterns (first-sample grade) for the 40 L pack.

Units: mm. Body coordinates: X left-right, Y from the back face of the bag
towards its front, Z up from the bottom seam. Every piece is described by its
stitch line; the cut line is derived from per-edge seam allowances.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

SA = 10.0  # body seams, closed with binding tape
SA_S = 8.0  # small turned parts
HEM = 50.0  # roll-top hem, folded 25 + 25
STEP = 10.0

# Packed cross-sections of the bag: (z, width, depth, corner radius).
SECTIONS = [(0, 240, 160, 55), (60, 284, 204, 70), (200, 298, 218, 75), (420, 300, 220, 75), (560, 288, 208, 70), (640, 270, 180, 60)]
Z_TOP = 640.0  # roll line
EXT = 250.0  # roll-top extension above the roll line
K_CORNER = 2.0 - math.pi / 2.0  # panel width lost per unit corner radius when seams sit mid-corner

MATERIALS = {
    "M1": ("主面料", "210D 高强尼龙格子布（Robic 或同级），PU 内涂，无氟防泼水", 1450),
    "M2": ("底料", "420D 高强尼龙，PU 内涂", 1450),
    "M3": ("弹力料", "四面弹尼龙/氨纶网布，约 200 g/m²", 1450),
    "M4": ("间隔网布", "3 mm 三明治网布（3D spacer mesh）", 1450),
    "M5": ("肩带泡棉", "EVA 8 mm，约 60 kg/m³（密度打样时确认）", 1000),
    "M6": ("腰带泡棉", "EVA 10 mm，约 90 kg/m³（密度打样时确认）", 1000),
    "M7": ("腰垫泡棉", "EVA 22 mm（10 + 12 贴合）", 1000),
    "M8": ("背板", "HDPE 板 1.5 mm", 1000),
    "M9": ("加强板", "HDPE 板 1.0 mm", 1000),
    "M10": ("里料", "70D 尼龙塔夫，PU 内涂", 1450),
    "M11": ("耐磨加强料", "TPU 复合加强料 0.8 mm（Hypalon 类）", 1000),
}

# Assumed areal weights (g/m2) for the weight estimate; replace with supplier data.
GSM = {"M1": 120, "M2": 220, "M3": 200, "M4": 260, "M5": 480, "M6": 900, "M7": 1320, "M8": 1425, "M9": 950, "M10": 70, "M11": 900}
# Assumed linear weights (g/m) keyed by the first two words of a webbing spec.
G_PER_M = {"20 mm": 11.0, "15 mm": 8.0, "25 mm": 14.0, "3 mm": 6.0, "10 mm": 5.0}
BINDING_G_PER_M = 4.0
FIXED_WEIGHTS = [("塑料扣具、拉链、G 钩、螺钉", 90), ("联动座总成（概念值，见 docs/03）", 70), ("Y 型背架（概念值，见 docs/03）", 120), ("缝线、标签、胶帽等", 20)]

_z = np.array([s[0] for s in SECTIONS], float)
_W = PchipInterpolator(_z, [s[1] for s in SECTIONS])
_D = PchipInterpolator(_z, [s[2] for s in SECTIONS])
_R = PchipInterpolator(_z, [s[3] for s in SECTIONS])


def section(z: float):
    z = min(max(z, 0.0), Z_TOP)
    return float(_W(z)), float(_D(z)), float(_R(z))


def half_width(z: float) -> float:
    w, _, r = section(z)
    return (w - K_CORNER * r) / 2.0


def depth(z: float) -> float:
    _, d, r = section(z)
    return d - K_CORNER * r


def section_area(z: float) -> float:
    w, d, r = section(z)
    return w * d - (4.0 - math.pi) * r * r


def main_volume_l(z0: float = 0.0, z1: float = Z_TOP) -> float:
    zz = np.linspace(z0, z1, 1001)
    return float(np.trapezoid([section_area(z) for z in zz], zz)) / 1e6


# --------------------------------------------------------------------------- geometry helpers


def cum(pts) -> np.ndarray:
    p = np.asarray(pts, float)
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])


def length(pts) -> float:
    return float(cum(pts)[-1])


def rrect(w: float, h: float, r: float, n: int = 8):
    """Counter-clockwise rounded rectangle centred on the origin (closed: first == last)."""
    r = min(r, w / 2, h / 2)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return pts


def rounded(points, r: float):
    """Round the convex corners of a polygon; returns a closed CCW point list."""
    poly = Polygon(points).buffer(-r, join_style="mitre").buffer(r, quad_segs=8)
    return list(orient(poly, 1.0).exterior.coords)


def inset(points, d: float, r: float = 0.0):
    poly = Polygon(points).buffer(-d, join_style="mitre")
    if r:
        poly = poly.buffer(-r, join_style="mitre").buffer(r, quad_segs=8)
    return list(orient(poly, 1.0).exterior.coords)


def _third(p, q, dp: float, dq: float):
    """Point at distance dp from p and dq from q, on the left of p -> q."""
    d = float(np.linalg.norm(q - p))
    ex = (q - p) / d
    ey = np.array([-ex[1], ex[0]])
    x = (dp * dp - dq * dq + d * d) / (2.0 * d)
    y = math.sqrt(max(dp * dp - x * x, 0.0))
    return p + x * ex + y * ey


def unroll(a3, b3):
    """Flatten the triangle strip between two 3D polylines without stretching it."""
    a3, b3 = np.asarray(a3, float), np.asarray(b3, float)
    a = [np.zeros(2)]
    b = [np.array([np.linalg.norm(b3[0] - a3[0]), 0.0])]
    for i in range(len(a3) - 1):
        an = _third(a[-1], b[-1], np.linalg.norm(a3[i + 1] - a3[i]), np.linalg.norm(a3[i + 1] - b3[i]))
        bn = _third(an, b[-1], np.linalg.norm(b3[i + 1] - a3[i + 1]), np.linalg.norm(b3[i + 1] - b3[i]))
        a.append(an)
        b.append(bn)
    return np.array(a), np.array(b)


# --------------------------------------------------------------------------- piece model


@dataclass
class Edge:
    name: str
    pts: list
    sa: float
    finish: str = "缝合"
    notches: list = field(default_factory=list)  # distances from the edge start

    def length(self) -> float:
        return length(self.pts)


@dataclass
class Piece:
    code: str
    name: str
    name_en: str
    material: str
    qty: int
    edges: list
    pair: bool = False  # qty is split into left / right mirrored halves
    grain: float = 90.0  # warp direction, degrees from +X
    marks: list = field(default_factory=list)  # (label, polyline)
    drills: list = field(default_factory=list)  # (label, (x, y))
    note: str = ""

    def __post_init__(self):
        for e in self.edges:
            e.pts = [tuple(map(float, p)) for p in e.pts]
        if _signed_area(self.sew()) < 0:
            for e in self.edges:
                total = e.length()
                e.pts = e.pts[::-1]
                e.notches = [total - s for s in e.notches]
            self.edges = self.edges[::-1]

    def _segments(self):
        pts, sas = [], []
        for e in self.edges:
            for p, q in zip(e.pts[:-1], e.pts[1:]):
                if math.dist(p, q) > 1e-6:
                    pts.append(p)
                    sas.append(e.sa)
        return np.array(pts), np.array(sas)

    def sew(self) -> np.ndarray:
        return self._segments()[0]

    def cut(self) -> np.ndarray:
        return offset_polygon(*self._segments())

    def edge(self, name: str) -> Edge:
        return next(e for e in self.edges if e.name == name)

    def notch_segments(self):
        out = []
        for e in self.edges:
            c = cum(e.pts)
            p = np.asarray(e.pts)
            for s in e.notches:
                i = int(np.clip(np.searchsorted(c, s, side="right") - 1, 0, len(p) - 2))
                t = (p[i + 1] - p[i]) / (c[i + 1] - c[i])
                o = p[i] + t * (s - c[i])
                n = np.array([t[1], -t[0]])
                if e.sa > 0:
                    out.append((o + n * e.sa, o + n * (e.sa - min(5.0, 0.5 * e.sa))))
                else:
                    out.append((o, o - n * 3.0))
        return out

    def bbox(self):
        c = self.cut()
        return float(c[:, 0].min()), float(c[:, 1].min()), float(c[:, 0].max()), float(c[:, 1].max())

    def size(self):
        x0, y0, x1, y1 = self.bbox()
        return x1 - x0, y1 - y0

    def cut_area(self) -> float:
        return abs(_signed_area(self.cut()))

    def perimeter(self) -> float:
        s = self.sew()
        return length(np.vstack([s, s[:1]]))


def _signed_area(p) -> float:
    p = np.asarray(p)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def offset_polygon(pts: np.ndarray, sas: np.ndarray, mitre_limit: float = 3.0) -> np.ndarray:
    """Offset a CCW polygon outwards, segment i (pts[i] -> pts[i+1]) by sas[i]."""
    n = len(pts)
    out = []
    for i in range(n):
        p_prev, p, p_next = pts[i - 1], pts[i], pts[(i + 1) % n]
        t0 = (p - p_prev) / np.linalg.norm(p - p_prev)
        t1 = (p_next - p) / np.linalg.norm(p_next - p)
        d0, d1 = sas[i - 1], sas[i]
        a0 = p + np.array([t0[1], -t0[0]]) * d0
        a1 = p + np.array([t1[1], -t1[0]]) * d1
        cross = t0[0] * t1[1] - t0[1] * t1[0]
        if abs(cross) < 1e-9:
            out.append(a0)
            if abs(d0 - d1) > 1e-9:
                out.append(a1)
            continue
        u = ((a1[0] - a0[0]) * t1[1] - (a1[1] - a0[1]) * t1[0]) / cross
        x = a0 + u * t0
        if np.linalg.norm(x - p) > mitre_limit * max(d0, d1, 1.0):
            out.extend([a0, a1])
        else:
            out.append(x)
    return np.array(out)


@dataclass
class Seam:
    name: str
    a: str
    len_a: float
    b: str
    len_b: float
    ease: float = 0.0  # designed difference len_a - len_b (gathers, pleats)
    tol: float = 0.5

    @property
    def error(self) -> float:
        return self.len_a - self.len_b - self.ease

    @property
    def ok(self) -> bool:
        return abs(self.error) <= self.tol


def _closed(name, pts, sa, finish="缝合"):
    pts = list(pts)
    if math.dist(pts[0], pts[-1]) > 1e-6:
        pts.append(pts[0])
    return [Edge(name, pts, sa, finish)]


def _at(c: np.ndarray, zs) -> list:
    return [float(c[int(round(z / STEP))]) for z in zs]


# --------------------------------------------------------------------------- pattern set


# Centre height of the linkage hub on the back panel (matches hub_z0 = 52 in backpack_model.py) and the
# bottom seam of the frame-sheet sleeve, which has to clear the hub backing plate.
HUB_Z = 74.0
SLEEVE_Z0 = 120.0
NOTCH_Z = (40, 200, 290, 330, 480, 560, 640)


def build():
    """Return (pieces, seams, info)."""
    zs = np.arange(0.0, Z_TOP + EXT + 0.1, STEP)
    hb = np.array([half_width(z) for z in zs])
    dp = np.array([depth(z) for z in zs])
    top = zs[-1]
    P: dict[str, Piece] = {}
    seams: list[Seam] = []

    def add(piece: Piece):
        P[piece.code] = piece
        return piece

    def idx(z):
        return int(round(z / STEP))

    # ---- A01 back panel ---------------------------------------------------
    right = [(hb[i], zs[i]) for i in range(len(zs))]
    cr = cum(right)
    add(
        Piece(
            "A01",
            "后幅（贴背片）",
            "BACK PANEL",
            "M1",
            1,
            [
                Edge("bottom", [(-hb[0], 0), (hb[0], 0)], SA, "缝合 + 包边", [hb[0]]),
                Edge("right", right, SA, "缝合 + 包边", _at(cr, NOTCH_Z)),
                Edge("top", [(hb[-1], top), (-hb[-1], top)], HEM, "卷口折边 25 + 25，内夹加强带", [hb[-1]]),
                Edge("left", [(-x, z) for x, z in right[::-1]], SA, "缝合 + 包边", [cr[-1] - s for s in _at(cr, NOTCH_Z)]),
            ],
            marks=[
                ("卷口起始线", [(-hb[idx(640)], 640), (hb[idx(640)], 640)]),
                ("背板套下缝线", [(-hb[idx(SLEEVE_Z0)], SLEEVE_Z0), (hb[idx(SLEEVE_Z0)], SLEEVE_Z0)]),
                ("背板套上口", [(-hb[idx(610)], 610), (hb[idx(610)], 610)]),
                ("联动座加强片 E01", [(-95, HUB_Z - 40), (95, HUB_Z - 40), (95, HUB_Z + 40), (-95, HUB_Z + 40), (-95, HUB_Z - 40)]),
                ("背长调节梯带 W11", [(-13, 430), (13, 430), (13, 600), (-13, 600), (-13, 430)]),
            ],
            drills=[(f"背长档 {k + 1}", (0.0, 450.0 + 25.0 * k)) for k in range(5)]
            + [("上拉带锚点", (s * 105.0, 585.0)) for s in (-1, 1)]
            + [("背架上角袋 E03", (s * 112.0, 560.0)) for s in (-1, 1)]
            + [("下区张紧带锚点", (s * 118.0, 180.0)) for s in (-1, 1)]
            + [("上区张紧带凸轮扣锚点", (s * 112.0, 255.0)) for s in (-1, 1)]
            + [("提手", (s * 35.0, 636.0)) for s in (-1, 1)]
            + [("水袋管出口", (75.0, 600.0))],
            note="面朝人体一侧为正面。联动座用 4 颗螺钉穿过 E01 加强片、后幅和 E04 内衬板固定。",
        )
    )

    # ---- A02 front panel --------------------------------------------------
    sf = cum(np.column_stack([dp, zs]))
    fr = [(hb[i], sf[i]) for i in range(len(zs))]
    cf = cum(fr)
    zp = np.arange(70.0, 430.1, STEP)
    hp = PchipInterpolator([70, 250, 430], [85, 113, 118])(zp)
    place = [(hp[k], sf[idx(z)]) for k, z in enumerate(zp)]
    add(
        Piece(
            "A02",
            "前幅",
            "FRONT PANEL",
            "M1",
            1,
            [
                Edge("bottom", [(-hb[0], 0), (hb[0], 0)], SA, "缝合 + 包边", [hb[0]]),
                Edge("right", fr, SA, "缝合 + 包边", _at(cf, NOTCH_Z)),
                Edge("top", [(hb[-1], sf[-1]), (-hb[-1], sf[-1])], HEM, "卷口折边 25 + 25，内夹加强带", [hb[-1]]),
                Edge("left", [(-x, s) for x, s in fr[::-1]], SA, "缝合 + 包边", [cf[-1] - s for s in _at(cf, NOTCH_Z)]),
            ],
            marks=[
                ("卷口起始线", [(-hb[idx(640)], sf[idx(640)]), (hb[idx(640)], sf[idx(640)])]),
                ("前弹力袋 B01 定位线", [(-x, s) for x, s in place[::-1]] + place),
            ],
            drills=[("V 形压缩绳锚点", (s * 96.0, sf[idx(530)])) for s in (-1, 1)] + [("压缩绳中心挂扣", (0.0, sf[idx(300)]))],
        )
    )

    # ---- A03 side panels --------------------------------------------------
    a3 = np.column_stack([hb, np.zeros_like(zs), zs])
    b3 = np.column_stack([hb, dp, zs])
    a2, b2 = unroll(a3, b3)
    ca, cb = cum(a2), cum(b2)
    strip_err = max(abs(ca[-1] - length(a3)), abs(cb[-1] - length(b3)))
    add(
        Piece(
            "A03",
            "侧幅（左右各一，镜像）",
            "SIDE PANEL",
            "M1",
            2,
            [
                Edge("bottom", [a2[0], b2[0]], SA, "缝合 + 包边"),
                Edge("front", list(b2), SA, "缝合 + 包边", _at(cb, NOTCH_Z)),
                Edge("top", [b2[-1], a2[-1]], HEM, "卷口折边 25 + 25"),
                Edge("back", list(a2[::-1]), SA, "缝合 + 包边", [ca[-1] - s for s in _at(ca, NOTCH_Z)]),
            ],
            pair=True,
            marks=[
                ("卷口起始线", [a2[idx(640)], b2[idx(640)]]),
                ("侧袋口位置", [a2[idx(290)], b2[idx(290)]]),
                ("侧袋底缝线", [a2[idx(40)], b2[idx(40)]]),
            ],
            drills=[("卷口侧扣带 W07", tuple((a2[idx(600)] + b2[idx(600)]) / 2))],
            note="后边与后幅缝合，前边与前幅缝合。侧压缩带在 z = 330 和 480 的刀口处夹入前、后两条缝。",
        )
    )

    # ---- A04 bottom -------------------------------------------------------
    w0, d0 = 2 * hb[0], dp[0]
    add(
        Piece(
            "A04",
            "包底",
            "BOTTOM PANEL",
            "M2",
            1,
            [
                Edge("back", [(-w0 / 2, 0), (w0 / 2, 0)], SA, "缝合 + 包边", [w0 / 2]),
                Edge("right", [(w0 / 2, 0), (w0 / 2, d0)], SA, "缝合 + 包边"),
                Edge("front", [(w0 / 2, d0), (-w0 / 2, d0)], SA, "缝合 + 包边", [w0 / 2]),
                Edge("left", [(-w0 / 2, d0), (-w0 / 2, 0)], SA, "缝合 + 包边"),
            ],
            grain=0.0,
        )
    )
    seams += [
        Seam("后幅侧边 ↔ 侧幅后边（左右各一条）", "A01.right", P["A01"].edge("right").length(), "A03.back", P["A03"].edge("back").length()),
        Seam("前幅侧边 ↔ 侧幅前边（左右各一条）", "A02.right", P["A02"].edge("right").length(), "A03.front", P["A03"].edge("front").length()),
        Seam("后幅下边 ↔ 包底后边", "A01.bottom", P["A01"].edge("bottom").length(), "A04.back", P["A04"].edge("back").length()),
        Seam("前幅下边 ↔ 包底前边", "A02.bottom", P["A02"].edge("bottom").length(), "A04.front", P["A04"].edge("front").length()),
        Seam("侧幅下边 ↔ 包底侧边", "A03.bottom", P["A03"].edge("bottom").length(), "A04.right", P["A04"].edge("right").length()),
        Seam("卷口：后幅上边 ↔ 前幅上边（卷口两半等宽）", "A01.top", P["A01"].edge("top").length(), "A02.top", P["A02"].edge("top").length()),
    ]

    # ---- B01 front stretch pocket ----------------------------------------
    ease = 8.0
    s0 = sf[idx(70)]
    pk = [(x + ease, s - s0) for x, s in place]
    add(
        Piece(
            "B01",
            "前弹力袋",
            "FRONT STRETCH POCKET",
            "M3",
            1,
            [
                Edge("bottom", [(-pk[0][0], 0), (pk[0][0], 0)], SA, "折入 10 车明线", [pk[0][0]]),
                Edge("right", pk, SA, "折入 10 车明线"),
                Edge("top", [pk[-1], (-pk[-1][0], pk[-1][1])], 0.0, "弹力包边带（预拉伸约 10%）", [pk[-1][0]]),
                Edge("left", [(-x, s) for x, s in pk[::-1]], SA, "折入 10 车明线"),
            ],
            note="袋身每侧比定位线宽 8 mm，缝合时把余量均匀吃进。",
        )
    )
    seams += [
        Seam("前袋侧边 ↔ 前幅定位线", "B01.right", P["B01"].edge("right").length(), "A02 定位线", length(place)),
        Seam("前袋下边 ↔ 前幅定位线下边（两侧各吃 8）", "B01.bottom", P["B01"].edge("bottom").length(), "A02 定位线", 2 * place[0][0], ease=2 * ease),
    ]

    # ---- B02 side pockets --------------------------------------------------
    i0, i1 = idx(40), idx(290)
    pa, pb = a2[i0 : i1 + 1], b2[i0 : i1 + 1]
    u = pb.mean(axis=0) - pa.mean(axis=0)
    u /= np.linalg.norm(u)
    spread = 60.0
    pbs = pb + spread * u
    wb = float(np.linalg.norm(pbs[0] - pa[0]))
    add(
        Piece(
            "B02",
            "侧袋（左右各一，镜像）",
            "SIDE POCKET",
            "M3",
            2,
            [
                Edge("bottom", [pa[0], pbs[0]], SA, "打两个 15 mm 对褶后缝合", [wb / 3, 2 * wb / 3]),
                Edge("front", list(pbs), SA, "夹入前侧缝"),
                Edge("top", [pbs[-1], pa[-1]], 25.0, "卷边 25，内穿 10 mm 松紧带"),
                Edge("back", list(pa[::-1]), SA, "夹入后侧缝"),
            ],
            pair=True,
            marks=[(f"对褶 {k + 1}", [pa[0] + (pbs[0] - pa[0]) * f, pa[0] + (pbs[0] - pa[0]) * f + np.array([0.0, 40.0])]) for k, f in enumerate((1 / 3, 2 / 3))],
            note="袋口松紧带净长取侧幅该处宽度的 85%。",
        )
    )
    seams += [
        Seam("侧袋后边 ↔ 侧幅后边 z40–290", "B02.back", P["B02"].edge("back").length(), "A03.back 段", ca[i1] - ca[i0]),
        Seam("侧袋前边 ↔ 侧幅前边 z40–290", "B02.front", P["B02"].edge("front").length(), "A03.front 段", cb[i1] - cb[i0]),
        Seam("侧袋下边 ↔ 侧幅 z40 横线（两个对褶共收 60）", "B02.bottom", wb, "A03 z40 横线", float(np.linalg.norm(pb[0] - pa[0])), ease=spread, tol=1.0),
    ]

    # ---- B03-B05 hip-belt pockets -----------------------------------------
    face = rrect(160, 88, 26)
    zip_len = 150.0
    add(Piece("B03", "腰带袋面片", "HIPBELT POCKET FACE", "M1", 2, _closed("outline", face, SA_S), grain=0.0))
    g_len = length(face) - zip_len
    add(Piece("B04", "腰带袋围条", "HIPBELT POCKET GUSSET", "M1", 2, _closed("outline", rrect(g_len, 35, 0), SA_S), grain=0.0))
    add(Piece("B05", "腰带袋拉链贴条", "HIPBELT POCKET ZIP STRIP", "M1", 4, _closed("outline", rrect(zip_len, 12, 0), SA_S), grain=0.0, note="两条夹 5 号尼龙拉链，合计净宽 35。"))
    seams.append(Seam("腰带袋面片周长 ↔ 围条 + 拉链段", "B03 周长", length(face), "B04 + 拉链", g_len + zip_len))

    # ---- B06 hydration sleeve ---------------------------------------------
    add(
        Piece(
            "B06",
            "水袋仓",
            "HYDRATION SLEEVE",
            "M10",
            1,
            [
                Edge("bottom", [(-120, 0), (120, 0)], SA, "缝在背板套上"),
                Edge("right", [(120, 0), (120, 380)], SA, "缝在背板套上"),
                Edge("top", [(120, 380), (-120, 380)], 20.0, "卷边 10 + 10"),
                Edge("left", [(-120, 380), (-120, 0)], SA, "缝在背板套上"),
            ],
        )
    )

    # ---- C01 frame sheet, C02 sleeve --------------------------------------
    j0, j1 = idx(SLEEVE_Z0 + 10), idx(590)
    sheet = [(hb[i] - 14, zs[i]) for i in range(j0, j1 + 1)] + [(-(hb[i] - 14), zs[i]) for i in range(j1, j0 - 1, -1)]
    add(Piece("C01", "背板（防鼓包）", "FRAME SHEET", "M8", 1, _closed("outline", rounded(sheet, 25), 0.0, "净裁，边缘去毛刺"), note="插入背板套，可抽出。"))
    k0, k1 = idx(SLEEVE_Z0), idx(610)
    sl = [(hb[i], zs[i]) for i in range(k0, k1 + 1)]
    add(
        Piece(
            "C02",
            "背板套",
            "FRAME SHEET SLEEVE",
            "M10",
            1,
            [
                Edge("bottom", [(-sl[0][0], sl[0][1]), sl[0]], SA, f"缝在后幅 z = {SLEEVE_Z0:.0f}"),
                Edge("right", sl, SA, "夹入后侧缝"),
                Edge("top", [sl[-1], (-sl[-1][0], sl[-1][1])], 20.0, "卷边 10 + 10，中间缝 25 mm 魔术贴"),
                Edge("left", [(-x, z) for x, z in sl[::-1]], SA, "夹入后侧缝"),
            ],
        )
    )
    seams.append(Seam(f"背板套侧边 ↔ 后幅侧边 z{SLEEVE_Z0:.0f}–610", "C02.right", P["C02"].edge("right").length(), "A01.right 段", cr[k1] - cr[k0]))

    # ---- C03 suspended mesh ------------------------------------------------
    zm = np.arange(250.0, 540.1, STEP)
    hm = PchipInterpolator([250, 330, 430, 540], [98, 88, 107, 118])(zm)
    mr = [(hm[k], z - 250.0) for k, z in enumerate(zm)]
    add(
        Piece(
            "C03",
            "上区悬浮网",
            "SUSPENDED MESH PANEL",
            "M4",
            1,
            [
                Edge("bottom", [(-mr[0][0], 0), mr[0]], 0.0, "包边"),
                Edge("right", mr, 0.0, "包边"),
                Edge("top", [mr[-1], (-mr[-1][0], mr[-1][1])], 35.0, "折 35 做横梁套管"),
                Edge("left", [(-x, z) for x, z in mr[::-1]], 0.0, "包边"),
            ],
            drills=[("下角张紧带 W09", (s * (mr[0][0] - 12), 12.0)) for s in (-1, 1)],
        )
    )

    # ---- C04-C07 lumbar pads ----------------------------------------------
    lum = rrect(92, 118, 18)
    add(Piece("C04", "腰垫面片", "LUMBAR PAD FACE", "M4", 2, _closed("outline", lum, SA_S)))
    add(Piece("C05", "腰垫围条", "LUMBAR PAD GUSSET", "M4", 2, _closed("outline", rrect(length(lum), 22, 0), SA_S), grain=0.0))
    add(Piece("C06", "腰垫底片", "LUMBAR PAD BACK", "M1", 2, _closed("outline", lum, SA_S)))
    add(Piece("C07", "腰垫泡棉芯", "LUMBAR PAD FOAM", "M7", 2, _closed("outline", rrect(90, 116, 17), 0.0, "净裁")))
    seams.append(Seam("腰垫面片周长 ↔ 围条长", "C04 周长", length(lum), "C05 长", length(lum)))

    # ---- C08-C09 shoulder yoke (torso-length adjustment) -------------------
    yoke = rounded([(-75, 0), (75, 0), (100, 110), (-100, 110)], 15)
    add(
        Piece(
            "C08",
            "肩轭（内外两层）",
            "SHOULDER YOKE",
            "M1",
            2,
            _closed("outline", yoke, SA_S),
            drills=[("G 钩织带", (0.0, 30.0))] + [("肩带插入位", (s * 62.0, 100.0)) for s in (-1, 1)],
            note="两层夹 C09 加强板。背面中线缝一条带 G 钩的 25 mm 织带，挂入后幅梯带调背长。",
        )
    )
    add(Piece("C09", "肩轭加强板", "YOKE STIFFENER", "M9", 1, _closed("outline", inset(yoke, 6, 8), 0.0, "净裁")))

    # ---- D01-D03 shoulder straps ------------------------------------------
    ctrl = np.array([(0, 0), (6, -70), (22, -160), (40, -250), (48, -340), (40, -420), (28, -480)], float)
    t = cum(ctrl)
    spl = CubicSpline(t, ctrl)
    ts = np.linspace(0, t[-1], 81)
    c = spl(ts)
    tan = spl(ts, 1)
    tan /= np.linalg.norm(tan, axis=1)[:, None]
    nrm = np.column_stack([-tan[:, 1], tan[:, 0]])
    wdt = PchipInterpolator([0, 0.25, 0.6, 1.0], [60, 70, 66, 50])(ts / t[-1])
    lft = c + nrm * wdt[:, None] / 2
    rgt = c - nrm * wdt[:, None] / 2
    ang0 = math.atan2(nrm[-1, 1], nrm[-1, 0])
    tip = [c[-1] + wdt[-1] / 2 * np.array([math.cos(ang0 - math.pi * k / 12), math.sin(ang0 - math.pi * k / 12)]) for k in range(1, 12)]
    strap_outline = list(lft) + tip + list(rgt[::-1])
    strap_poly = strap_outline + [strap_outline[0]]

    def strap_edges(points):
        return [Edge("top", [points[-1], points[0]], 20.0, "插入肩轭 20 车缝"), Edge("outline", points, 0.0, "三层合缝后包边")]

    for code, name, en, mat in (("D01", "肩带外层", "SHOULDER STRAP OUTER", "M1"), ("D02", "肩带内层（贴身）", "SHOULDER STRAP INNER", "M4")):
        add(
            Piece(
                code,
                name + "（左右各一，镜像）",
                en,
                mat,
                2,
                strap_edges(strap_outline),
                pair=True,
                drills=[("胸带滑轨起点", tuple(c[20])), ("胸带滑轨终点", tuple(c[40])), ("下调节梯扣", tuple(c[-3]))] if code == "D01" else [],
                grain=math.degrees(math.atan2(c[-1][1] - c[0][1], c[-1][0] - c[0][0])),
            )
        )
    add(Piece("D03", "肩带泡棉（左右各一，镜像）", "SHOULDER STRAP FOAM", "M5", 2, _closed("outline", inset(strap_poly, 4), 0.0, "净裁"), pair=True))
    seams.append(Seam("肩带外层周长 ↔ 内层周长", "D01", P["D01"].perimeter(), "D02", P["D02"].perimeter()))

    # ---- D04-D07 hip-belt wings -------------------------------------------
    wing_l = 185.0
    us = np.linspace(0, wing_l, 38)
    yc = 35.0 * (us / wing_l) ** 2
    hh = PchipInterpolator([0, 70, 140, 185], [110, 106, 98, 86])(us)
    upper = np.column_stack([us, yc + hh / 2])
    lower = np.column_stack([us, yc - hh / 2])
    tipc = np.array([wing_l, yc[-1]])
    wtip = [tipc + hh[-1] / 2 * np.array([math.cos(math.pi / 2 - math.pi * k / 12), math.sin(math.pi / 2 - math.pi * k / 12)]) for k in range(1, 12)]
    wing_outline = list(upper) + wtip + list(lower[::-1])
    wing_poly = wing_outline + [wing_outline[0]]

    def wing_edges(points):
        return [Edge("root", [points[-1], points[0]], 15.0, "插入腰带中段 15 车缝"), Edge("outline", points, 0.0, "三层合缝后包边")]

    pocket_c = (108.0, float(np.interp(108.0, us, yc)))
    add(
        Piece(
            "D04",
            "腰带翼外层（左右各一，镜像）",
            "HIPBELT WING OUTER",
            "M1",
            2,
            wing_edges(wing_outline),
            pair=True,
            grain=0.0,
            marks=[("腰带袋 B03 定位", [(pocket_c[0] + x, pocket_c[1] + y) for x, y in face])],
            drills=[("收紧带回折环（上）", (wing_l - 8.0, float(yc[-1]) + 16.0)), ("收紧带回折环（下）", (wing_l - 8.0, float(yc[-1]) - 16.0))],
        )
    )
    add(Piece("D05", "腰带翼内层（贴身，左右各一，镜像）", "HIPBELT WING INNER", "M4", 2, wing_edges(wing_outline), pair=True, grain=0.0))
    add(Piece("D06", "腰带翼泡棉（左右各一，镜像）", "HIPBELT WING FOAM", "M6", 2, _closed("outline", inset(wing_poly, 4), 0.0, "净裁"), pair=True, grain=0.0))
    stiff = Polygon(wing_poly).buffer(-12, join_style="mitre").intersection(box(-50, -200, 130, 300))
    add(Piece("D07", "腰带翼加强板（左右各一，镜像）", "HIPBELT WING STIFFENER", "M9", 2, _closed("outline", rounded(list(orient(stiff, 1.0).exterior.coords), 8), 0.0, "净裁"), pair=True, grain=0.0))
    seams.append(Seam("腰带翼外层周长 ↔ 内层周长", "D04", P["D04"].perimeter(), "D05", P["D05"].perimeter()))

    # ---- D08-D09 belt centre section --------------------------------------
    add(
        Piece(
            "D08",
            "腰带中段套片（前后两层）",
            "HIPBELT CENTRE COVER",
            "M1",
            2,
            _closed("outline", rrect(210, 84, 22), SA_S),
            grain=0.0,
            drills=[("枢转盘中心", (0.0, 0.0))],
            note="两层夹 D09 腰带背板。左右两端开口，插入腰带翼根部后车缝。",
        )
    )
    add(Piece("D09", "腰带背板", "HIPBELT BACK PLATE", "M9", 1, _closed("outline", rrect(190, 64, 18), 0.0, "净裁"), grain=0.0, drills=[("枢转盘中心孔", (0.0, 0.0))]))

    # ---- E reinforcements --------------------------------------------------
    add(Piece("E01", "联动座安装加强片", "HUB MOUNT PATCH", "M2", 1, _closed("outline", rrect(190, 80, 8), 0.0, "热切净裁"), grain=0.0, drills=[("联动座螺钉孔", (sx * 62.0, sy * 14.0)) for sx in (-1, 1) for sy in (-1, 1)]))
    add(Piece("E04", "联动座内衬板", "HUB BACKING PLATE", "M8", 1, _closed("outline", rrect(180, 70, 8), 0.0, "净裁"), grain=0.0, drills=[("联动座螺钉孔", (sx * 62.0, sy * 14.0)) for sx in (-1, 1) for sy in (-1, 1)], note="放在后幅内侧、背板套下方，与 E01 一起夹住后幅。孔位为占位，以联动座定稿图为准。"))
    add(Piece("E02", "织带锚点加强片", "ANCHOR PATCH", "M11", 6, _closed("outline", rrect(60, 45, 5), 0.0, "净裁"), grain=0.0, note="上拉带锚点 ×2、上区张紧带锚点 ×2、下区张紧带锚点 ×2。"))
    add(Piece("E03", "背架上角袋", "FRAME CORNER POCKET", "M11", 2, _closed("outline", rrect(56, 72, 6), 0.0, "净裁，三边车缝"), note="套住 Y 型背架上横梁两端，杆端先套胶帽防异响。"))

    top_perimeter = 2 * (2 * hb[-1]) + 2 * dp[-1]
    info = {
        "zs": zs,
        "half_width": hb,
        "depth": dp,
        "strip_error": strip_err,
        "main_volume_l": main_volume_l(),
        "extension_volume_l": section_area(Z_TOP) * 150.0 / 1e6,
        "front_pocket_volume_l": 2.4,
        "top_perimeter": top_perimeter,
        "roll_flat_width": top_perimeter / 2,
        "body_seam_length": 2 * (P["A01"].edge("right").length() + P["A02"].edge("right").length()) + P["A04"].perimeter(),
    }
    return P, seams, info


# --------------------------------------------------------------------------- trims


def webbing(P, info):
    """(code, name, spec, cut length mm, qty, use)."""
    roll = info["roll_flat_width"]
    bound = sum(p.edge("outline").length() * p.qty for p in (P["D01"], P["D04"]))
    bound += sum(P["C03"].edge(n).length() for n in ("bottom", "right", "left")) + P["B01"].edge("top").length()
    return [
        ("W01", "联动带", "20 mm UHMWPE 扁织带，表面压光", 900, 1, "穿过联动座，两端接 W02"),
        ("W02", "肩带下调节带", "20 mm 尼龙织带", 420, 2, "联动带端头 → 肩带下端梯扣"),
        ("W03", "上拉带（load lifter）", "15 mm 尼龙织带", 330, 2, "肩带顶 → 后幅上拉带锚点"),
        ("W04", "胸带", "15 mm 尼龙织带（含 60 mm 弹力段）", 380, 1, "分 260 + 120 两段，配滑轨扣"),
        ("W05", "腰带收紧带", "25 mm 尼龙织带", 650, 2, "前拉式：从中扣回折到腰带翼"),
        ("W06", "卷口加强带", "20 mm 硬挺尼龙织带", round(roll), 2, "夹在前、后幅卷口折边内"),
        ("W07", "卷口侧扣带", "20 mm 尼龙织带", 200, 2, "侧幅上部，接卷口插扣"),
        ("W08", "侧压缩带", "15 mm 尼龙织带", 420, 4, "每侧两条，侧幅 z = 330 和 480 处"),
        ("W09", "上区张紧带", "20 mm 尼龙织带", 260, 2, "悬浮网下角 → 后幅上的凸轮扣（z = 255）"),
        ("W10", "下区张紧带", "20 mm 尼龙织带", 300, 2, "腰垫 → 后幅下锚点"),
        ("W11", "背长调节梯带", "25 mm 尼龙织带", 330, 1, "后幅中线，5 档，档距 25 mm"),
        ("W12", "提手", "20 mm 尼龙织带（中段包管）", 260, 1, "后幅顶部"),
        ("W13", "V 形压缩绳", "3 mm 弹力绳", 340, 2, "前幅"),
        ("W14", "回中弹性绳", "3 mm 弹力绳", 120, 2, "联动座内"),
        ("W15", "内缝包边带", "20 mm 涤纶罗纹包边带", round(info["body_seam_length"] * 1.05), 1, "包住全部包体内缝"),
        ("W16", "外露包边带", "20 mm 弹力包边带", round(bound * 1.05), 1, "肩带、腰带翼、悬浮网、前袋口"),
        ("W17", "侧袋口松紧带", "10 mm 松紧带", round(0.85 * float(np.linalg.norm(P["A03"].marks[1][1][1] - P["A03"].marks[1][1][0]))), 2, "侧袋口卷边内"),
    ]


HARDWARE = [
    ("H01", "卷口插扣 20 mm", "侧开插扣，YKK LB20R 或同级（Duraflex、Woojin）", 2, "卷口两端"),
    ("H02", "腰带中扣 25 mm 双调", "双调侧开插扣，YKK LB25RD 或同级", 1, "腰带，前拉式"),
    ("H03", "梯扣 20 mm", "YKK LK20GV 或同级", 4, "肩带下调节 ×2、下区张紧 ×2"),
    ("H04", "梯扣 15 mm", "同系列 15 mm", 6, "上拉带 ×2、侧压缩 ×4"),
    ("H05", "凸轮扣 20 mm", "YKK LA20CB 或同级", 2, "上区张紧带，缝在后幅 z = 255 的锚点上"),
    ("H06", "胸带滑轨扣 15 mm（带哨）", "滑轨式胸带扣一套", 1, "肩带滑轨"),
    ("H07", "G 钩 25 mm", "铝或不锈钢 G 钩", 1, "背长调节，挂入梯带"),
    ("H08", "日字扣 25 mm", "YKK LA25S 或同级", 2, "腰带收紧带回折"),
    ("H09", "5 号尼龙拉链 + 拉头", "YKK 5CN 或同级，净长 150 mm", 2, "腰带袋"),
    ("H10", "绳扣", "单孔弹簧绳扣", 1, "V 形压缩绳"),
    ("H11", "魔术贴 25 mm", "勾面 + 毛面各 200 mm", 1, "背板套上口"),
    ("H12", "杆端胶帽", "Ø6 硅胶或 TPU 帽", 2, "Y 型背架上横梁两端，防异响"),
    ("H13", "联动座总成", "见 BP40-HUB-001（前/后壳、滚轮 ×2、凸轮扳手、枢转盘）", 1, "后幅下部"),
    ("H14", "Y 型背架", "见 BP40-FRM-001（7075-T6 Ø6，下立杆 Ø7）", 1, "背负系统"),
    ("H15", "联动座安装螺钉", "M4×12 不锈钢盘头 + 防松螺母", 4, "穿过 E01、后幅和 E04 内衬板"),
    ("H16", "防雨罩（选配）", "40–50 L 通用防雨罩，外购", 1, "放前弹力袋"),
]


def check(P, seams, info):
    """Return a list of problems (empty when the pattern set is consistent)."""
    problems = []
    for p in P.values():
        sew, cut = Polygon(p.sew()), Polygon(p.cut())
        if not sew.is_valid or not cut.is_valid:
            problems.append(f"{p.code}: invalid polygon")
        elif not cut.buffer(1e-6).contains(sew):
            problems.append(f"{p.code}: cut line does not enclose the stitch line")
        if p.material not in MATERIALS:
            problems.append(f"{p.code}: unknown material {p.material}")
        if p.pair and p.qty % 2:
            problems.append(f"{p.code}: mirrored pair with odd quantity")
    problems += [f"seam {s.name}: {s.a} {s.len_a:.1f} vs {s.b} {s.len_b:.1f} (ease {s.ease:.0f})" for s in seams if not s.ok]
    if info["strip_error"] > 0.01:
        problems.append(f"side panel unroll stretched by {info['strip_error']:.3f} mm")
    for a, b in (("A01", "A03"), ("A02", "A03")):
        na = len(P[a].edge("right").notches)
        nb = len(P[b].edge("back" if a == "A01" else "front").notches)
        if na != nb:
            problems.append(f"notch count differs on {a}/{b}")
    return problems
