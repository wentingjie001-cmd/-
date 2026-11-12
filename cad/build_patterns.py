"""Outputs for the A1 flat patterns: DXF, 1:1 PDF, markers, cut list, seam check.

    python3 cad/build_patterns.py

Writes to cad/out/production/. Exits with status 1 if the pattern set fails its
consistency checks (seam lengths, polygon validity, notch pairing).
"""

from __future__ import annotations

import csv
import math
import sys
import textwrap
from pathlib import Path

import ezdxf
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import LineString, Polygon

import drawing  # noqa: F401  (sets the CJK font)
import patterns as pt

OUT = Path(__file__).resolve().parent / "out" / "production"
GAP = 8.0
DXF_LAYERS = [("CUT", 7, "CONTINUOUS"), ("SEW", 1, "DASHED"), ("NOTCH", 3, "CONTINUOUS"), ("GRAIN", 5, "CONTINUOUS"), ("MARK", 4, "DASHED"), ("DRILL", 6, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")]


class Placed:
    """A piece instance placed on a marker: optional mirror, then translation."""

    def __init__(self, piece: pt.Piece, mirror: bool = False, x: float = 0.0, y: float = 0.0):
        self.p, self.mirror = piece, mirror
        c = self._m(piece.cut())
        self.w, self.h = np.ptp(c[:, 0]), np.ptp(c[:, 1])
        self._o = np.array([c[:, 0].min(), c[:, 1].min()])
        self.x, self.y = x, y

    def _m(self, a):
        a = np.atleast_2d(np.asarray(a, float)).copy()
        if self.mirror:
            a[:, 0] *= -1
        return a

    def t(self, a):
        return self._m(a) - self._o + np.array([self.x, self.y])

    def grain(self):
        poly = Polygon(self.t(self.p.sew()))
        c = poly.centroid if poly.contains(poly.centroid) else poly.representative_point()
        ang = math.radians(180 - self.p.grain if self.mirror else self.p.grain)
        d = np.array([math.cos(ang), math.sin(ang)])
        o = np.array([c.x, c.y])
        hit = LineString([o - d * 2000, o + d * 2000]).intersection(poly.buffer(-6))
        segs = [hit] if hit.geom_type == "LineString" else list(getattr(hit, "geoms", []))
        seg = min((s for s in segs if s.length > 0), key=lambda s: s.distance(c), default=None)
        if seg is None:
            return o - d * 10, o + d * 10
        a, b = (np.array(q) for q in seg.coords)
        m, half = (a + b) / 2, min(np.linalg.norm(b - a) * 0.35, 150.0)
        return m - d * half, m + d * half

    def label_point(self):
        poly = Polygon(self.t(self.p.sew()))
        c = poly.centroid if poly.contains(poly.centroid) else poly.representative_point()
        return np.array([c.x, c.y])

    def tag(self):
        return self.p.code + ("-R" if self.mirror else "-L" if self.p.pair else "")


def instances(piece: pt.Piece):
    if piece.pair:
        return [Placed(piece, m) for _ in range(piece.qty // 2) for m in (False, True)]
    return [Placed(piece) for _ in range(piece.qty)]


def shelf_pack(items, width):
    """Row-by-row bounding-box marker. Returns the used length."""
    items.sort(key=lambda i: (-i.h, -i.w))
    x = y = row_h = 0.0
    for it in items:
        if x > 0 and x + it.w > width:
            x, y, row_h = 0.0, y + row_h + GAP, 0.0
        it.x, it.y = x, y
        x += it.w + GAP
        row_h = max(row_h, it.h)
    return y + row_h


def markers(P):
    out = {}
    for m, (_, _, width) in pt.MATERIALS.items():
        items = [i for p in P.values() if p.material == m for i in instances(p)]
        if items:
            out[m] = (items, shelf_pack(items, width), width)
    return out


# --------------------------------------------------------------------------- drawing


def _arrow(a, b, size):
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    return [(b - d * size + n * size * 0.4, b, b - d * size - n * size * 0.4), (a + d * size + n * size * 0.4, a, a + d * size - n * size * 0.4)]


def draw(ax, it: Placed, fs=6.0, detail=True, lw=0.7):
    p = it.p
    cut, sew = it.t(p.cut()), it.t(p.sew())
    ax.plot(*np.vstack([cut, cut[:1]]).T, color="k", lw=lw)
    if np.abs(Polygon(cut).area - Polygon(sew).area) > 1.0:
        ax.plot(*np.vstack([sew, sew[:1]]).T, color="#c0392b", lw=lw * 0.6, ls=(0, (5, 3)))
    for a, b in p.notch_segments():
        ax.plot(*it.t([a, b]).T, color="k", lw=lw * 1.4)
    g0, g1 = it.grain()
    ax.plot([g0[0], g1[0]], [g0[1], g1[1]], color="#2471a3", lw=lw * 0.7)
    for tri in _arrow(g0, g1, min(10.0, np.linalg.norm(g1 - g0) * 0.15)):
        ax.plot(*np.array(tri).T, color="#2471a3", lw=lw * 0.7)
    for _, line in p.marks:
        ax.plot(*it.t(line).T, color="#1e8449", lw=lw * 0.6, ls=(0, (2, 2)))
    for name, xy in p.drills:
        q = it.t(xy)[0]
        ax.plot(q[0], q[1], marker="+", color="#7d3c98", ms=fs * 0.9, mew=lw * 0.8)
        if detail:
            ax.annotate(name, q, xytext=(3, 3), textcoords="offset points", fontsize=fs * 0.75, color="#7d3c98")
    if detail:
        for name, line in p.marks:
            q = it.t(line)
            ax.annotate(name, q[len(q) // 2], xytext=(2, 2), textcoords="offset points", fontsize=fs * 0.75, color="#1e8449")
    c = it.label_point()
    text = f"{it.tag()}\n{p.name}\n{pt.MATERIALS[p.material][0]} ×{p.qty}" if detail else it.tag()
    ax.text(c[0], c[1], text, fontsize=fs, ha="center", va="center", linespacing=1.3, bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6))


def marker_png(m, items, used, width):
    name, spec, _ = pt.MATERIALS[m]
    scale = 0.011
    fig, ax = plt.subplots(figsize=(max(width * scale, 6), max(used * scale, 2.5) + 0.8))
    ax.add_patch(plt.Rectangle((0, 0), width, used, fc="#f7f7f2", ec="#999", lw=0.8))
    for it in items:
        draw(ax, it, fs=5.5, detail=False, lw=0.6)
    area = sum(Polygon(i.t(i.p.cut())).area for i in items)
    ax.set_title(f"{m} {name}（{spec}）  幅宽 {width} mm × 用长 {used:.0f} mm，利用率 {100 * area / (width * used):.0f}%", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-20, width + 20)
    ax.set_ylim(-20, used + 20)
    ax.set_xlabel("mm", fontsize=7)
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(OUT / "markers" / f"marker_{m}.png", dpi=170, facecolor="white")
    plt.close(fig)
    return area


def body_sheet(P, info):
    """The four body panels and the bottom at one scale, with key dimensions."""
    items = [Placed(P[c]) for c in ("A01", "A03", "A02", "A04")]
    x = 0.0
    for it in items:
        it.x, it.y = x, 0.0
        x += it.w + 90
    fig, ax = plt.subplots(figsize=(15, 11.5))
    for it in items:
        draw(ax, it, fs=7.5, detail=True, lw=0.9)
        sew = it.t(it.p.sew())
        x0, x1, y0, y1 = sew[:, 0].min(), sew[:, 0].max(), sew[:, 1].min(), sew[:, 1].max()
        ax.annotate("", (x0, y0 - 28), (x1, y0 - 28), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text((x0 + x1) / 2, y0 - 40, f"净宽 {x1 - x0:.0f}", fontsize=7, ha="center", va="top")
        ax.annotate("", (x1 + 26, y0), (x1 + 26, y1), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(x1 + 32, (y0 + y1) / 2, f"净高 {y1 - y0:.0f}", fontsize=7, rotation=90, va="center")
    ax.set_title(
        f"BP40-A1 包体裁片（净线为红色虚线，裁线为黑色实线，缝份 {pt.SA:.0f} mm，卷口折边 {pt.HEM:.0f} mm）\n"
        f"主仓 {info['main_volume_l']:.1f} L（卷口线以下），卷口展平宽 {info['roll_flat_width']:.0f} mm",
        fontsize=11,
    )
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "body_panels.png", dpi=150, facecolor="white")
    plt.close(fig)


def overview(P):
    """Every piece once (one of each mirrored pair) on a single sheet."""
    items = [Placed(p) for p in P.values()]
    used = shelf_pack(items, 2300)
    fig, ax = plt.subplots(figsize=(17, 17 * (used + 60) / 2360))
    for it in items:
        draw(ax, it, fs=5.2, detail=False, lw=0.6)
        ax.text(it.x + it.w / 2, it.y - 4, f"{it.p.name}  ×{it.p.qty}", fontsize=4.6, ha="center", va="top")
    ax.set_title("BP40-A1 全部裁片一览（同一比例；成对的裁片只画一片）", fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlim(-30, 2330)
    ax.set_ylim(-45, used + 30)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "pattern_overview.png", dpi=170, facecolor="white")
    plt.close(fig)


def full_scale_pdf(P):
    with PdfPages(OUT / "pdf" / "BP40-A1_patterns_1to1.pdf") as pdf:
        for p in P.values():
            for it in instances(p)[: 2 if p.pair else 1]:
                it.x, it.y = 15.0, 15.0
                w = max(it.w + 30, 150.0)
                per_line = int((w - 30) / 2.4)
                head = [f"{it.tag()}  {p.name}", f"{pt.MATERIALS[p.material][0]}：{pt.MATERIALS[p.material][1]}", f"数量 {p.qty}，比例 1:1，单位 mm"]
                lines = [ln for text in head + ([p.note] if p.note else []) for ln in textwrap.wrap(text, per_line)]
                h = it.h + 44 + 4.2 * len(lines)
                fig = plt.figure(figsize=(w / 25.4, h / 25.4))
                ax = fig.add_axes([0, 0, 1, 1])
                draw(ax, it, fs=8, detail=True, lw=0.8)
                ax.add_patch(plt.Rectangle((15, it.h + 22), 100.0, 6, fill=False, lw=0.5))
                ax.plot([65, 65], [it.h + 22, it.h + 28], color="k", lw=0.5)
                ax.text(15, it.h + 31, "校准条 100 mm（中间刻线 50 mm），打印后先量这一条", fontsize=6)
                for k, ln in enumerate(lines):
                    ax.text(15, it.h + 38 + 4.2 * (len(lines) - 1 - k), ln, fontsize=6.5)
                ax.set_xlim(0, w)
                ax.set_ylim(0, h)
                ax.axis("off")
                pdf.savefig(fig)
                plt.close(fig)


# --------------------------------------------------------------------------- DXF


def _new_dxf():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for name, color, lt in DXF_LAYERS:
        doc.layers.add(name, color=color, linetype=lt)
    return doc


def dxf_add(msp, it: Placed):
    p = it.p
    msp.add_lwpolyline([tuple(q) for q in it.t(p.cut())], close=True, dxfattribs={"layer": "CUT"})
    msp.add_lwpolyline([tuple(q) for q in it.t(p.sew())], close=True, dxfattribs={"layer": "SEW"})
    for a, b in p.notch_segments():
        q = it.t([a, b])
        msp.add_line(tuple(q[0]), tuple(q[1]), dxfattribs={"layer": "NOTCH"})
    g0, g1 = it.grain()
    msp.add_line(tuple(g0), tuple(g1), dxfattribs={"layer": "GRAIN"})
    for tri in _arrow(g0, g1, min(10.0, np.linalg.norm(g1 - g0) * 0.15)):
        msp.add_lwpolyline([tuple(q) for q in tri], dxfattribs={"layer": "GRAIN"})
    for _, line in p.marks:
        msp.add_lwpolyline([tuple(q) for q in it.t(line)], dxfattribs={"layer": "MARK"})
    for _, xy in p.drills:
        msp.add_circle(tuple(it.t(xy)[0]), 1.5, dxfattribs={"layer": "DRILL"})
    c = it.label_point()
    for k, line in enumerate((it.tag(), p.name_en, f"{p.material} CUT {p.qty}")):
        msp.add_text(line, height=6, dxfattribs={"layer": "TEXT"}).set_placement((c[0] - 30, c[1] + 8 - 9 * k))


def dxf_out(P, marks):
    for p in P.values():
        doc = _new_dxf()
        dxf_add(doc.modelspace(), Placed(p))
        doc.saveas(OUT / "dxf" / "pieces" / f"BP40-A1_{p.code}.dxf")
    for m, (items, used, width) in marks.items():
        doc = _new_dxf()
        msp = doc.modelspace()
        msp.add_lwpolyline([(0, 0), (width, 0), (width, used), (0, used)], close=True, dxfattribs={"layer": "TEXT"})
        for it in items:
            dxf_add(msp, it)
        doc.saveas(OUT / "dxf" / f"BP40-A1_marker_{m}.dxf")


# --------------------------------------------------------------------------- tables


def _md(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]) + "\n"


def tables(P, seams, info, marks, areas):
    cut_rows, edge_rows = [], []
    for p in P.values():
        w, h = p.size()
        sas = sorted({e.sa for e in p.edges})
        cut_rows.append([p.code, p.name, f"{p.material} {pt.MATERIALS[p.material][0]}", p.qty, f"{w:.0f} × {h:.0f}", f"{p.cut_area() / 100:.0f}", " / ".join(f"{s:.0f}" for s in sas), p.note])
        for e in p.edges:
            edge_rows.append([p.code, e.name, f"{e.length():.1f}", f"{e.sa:.0f}", e.finish, len(e.notches)])
    head = ["编号", "名称", "材料", "数量", "裁片外形 宽×高 (mm)", "单片面积 (cm²)", "缝份 (mm)", "备注"]
    (OUT / "cut_list.md").write_text(_md(head, cut_rows), encoding="utf-8")
    with open(OUT / "cut_list.csv", "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([head] + cut_rows)
    (OUT / "edge_table.md").write_text(_md(["裁片", "边", "净线长 (mm)", "缝份 (mm)", "做法", "刀口数"], edge_rows), encoding="utf-8")

    rows = [[s.name, s.a, f"{s.len_a:.1f}", s.b, f"{s.len_b:.1f}", f"{s.ease:.0f}", f"{s.error:+.2f}", "合格" if s.ok else "不合格"] for s in seams]
    (OUT / "seam_check.md").write_text(_md(["缝", "边 A", "长 A (mm)", "边 B", "长 B (mm)", "设计吃量 (mm)", "误差 (mm)", "结果"], rows), encoding="utf-8")

    rows = []
    for m, (items, used, width) in marks.items():
        name, spec, _ = pt.MATERIALS[m]
        roll = width > 1000
        need = f"{used * 1.08 / 1000:.2f} m（幅宽 {width} mm）" if roll else f"{areas[m] * 1.25 / 1e6:.3f} m²（板材）"
        rows.append([m, name, spec, f"{areas[m] / 1e6:.3f}", f"{used:.0f}" if roll else "—", f"{100 * areas[m] / (width * used):.0f}%" if roll else "—", need])
    (OUT / "material_usage.md").write_text(_md(["代号", "材料", "规格", "裁片面积 (m²)", "排料用长 (mm)", "利用率", "单包用量（卷材加 8% 损耗，板材加 25%）"], rows), encoding="utf-8")

    zs, hb, dp = info["zs"], info["half_width"], info["depth"]
    body = zs <= pt.Z_TOP
    strap = P["D01"].edge("outline")
    wing = P["D04"]
    rows = [
        ["P01", "包体高度：包底缝到卷口线", f"{pt.Z_TOP:.0f}", "±8"],
        ["P02", "裁片总高：包底缝到卷口顶边", f"{zs[-1]:.0f}", "±8"],
        ["P03", "后幅最大净宽", f"{2 * hb[body].max():.0f}", "±5"],
        ["P04", "侧幅最大净宽（包体厚度方向）", f"{dp[body].max():.0f}", "±5"],
        ["P05", "包底净尺寸 宽 × 深", f"{2 * hb[0]:.0f} × {dp[0]:.0f}", "±4"],
        ["P06", "装满后外形 宽 × 厚（最大截面）", f"{max(s[1] for s in pt.SECTIONS):.0f} × {max(s[2] for s in pt.SECTIONS):.0f}", "±10"],
        ["P07", "卷口展平宽度", f"{info['roll_flat_width']:.0f}", "±5"],
        ["P08", "肩带垫长（肩轭缝线到下端）", f"{(strap.length() - math.pi * 25) / 2:.0f}", "±5"],
        ["P09", "肩带最宽处", "70", "±3"],
        ["P10", "腰带翼垫长（单侧，根部缝线到尖端）", f"{wing.size()[0] - 15:.0f}", "±5"],
        ["P11", "腰带翼根部高度", "110", "±3"],
        ["P12", "腰带垫总长（中段 210 + 两翼）", f"{210 + 2 * (wing.size()[0] - 15):.0f}", "±10"],
        ["P13", "背长调节行程（5 档，档距 25）", "100", "±3"],
        ["P14", "前弹力袋 口宽 × 高", f"{P['B01'].edge('top').length():.0f} × {P['B01'].edge('right').length():.0f}", "±5"],
        ["P15", "侧袋高度", "250", "±5"],
        ["P16", "腰带袋 长 × 高 × 厚", "160 × 88 × 35", "±3"],
        ["P17", "悬浮网 上宽 / 腰宽 / 高", f"{P['C03'].edge('top').length():.0f} / 176 / 290", "±4"],
        ["P18", "背板 宽 × 高", " × ".join(f"{v:.0f}" for v in P["C01"].size()), "±2"],
    ]
    (OUT / "pom.md").write_text(_md(["代号", "测量部位", "尺寸 (mm)", "公差 (mm)"], rows), encoding="utf-8")

    web = pt.webbing(P, info)
    (OUT / "webbing_cut_list.md").write_text(_md(["编号", "名称", "规格", "单根长 (mm)", "数量", "用途"], web), encoding="utf-8")
    (OUT / "hardware_list.md").write_text(_md(["编号", "名称", "规格 / 参考型号", "数量", "位置"], pt.HARDWARE), encoding="utf-8")

    rows, grams = [], 0.0
    for m, a in areas.items():
        g = a / 1e6 * pt.GSM[m]
        grams += g
        rows.append([f"{m} {pt.MATERIALS[m][0]}", f"{a / 1e6:.3f} m² × {pt.GSM[m]} g/m²", f"{g:.0f}"])
    for code, name, spec, ln, qty, _ in web:
        per_m = pt.BINDING_G_PER_M if "包边带" in spec else pt.G_PER_M[" ".join(spec.split(" ")[:2])]
        g = ln * qty / 1000 * per_m
        grams += g
        rows.append([f"{code} {name}", f"{ln * qty / 1000:.2f} m × {per_m:.0f} g/m", f"{g:.0f}"])
    for name, g in pt.FIXED_WEIGHTS:
        grams += g
        rows.append([name, "假定值", f"{g}"])
    rows.append(["合计", "", f"{grams:.0f}"])
    (OUT / "weight_estimate.md").write_text(_md(["项目", "计算", "重量 (g)"], rows), encoding="utf-8")
    info["weight_g"] = grams

    side = 2 * 1.3
    belt = 2 * 0.4
    total = info["main_volume_l"] + info["front_pocket_volume_l"] + side + belt
    rows = [
        ["主仓（包底到卷口线，按装满后的圆角截面积分）", f"{info['main_volume_l']:.1f}", "计算"],
        ["前弹力袋", f"{info['front_pocket_volume_l']:.1f}", "估算：定位面积 × 平均鼓起 30 mm"],
        ["侧袋 ×2", f"{side:.1f}", "估算"],
        ["腰带袋 ×2", f"{belt:.1f}", "估算"],
        ["合计（标称容积）", f"{total:.1f}", ""],
        ["卷口少卷时的扩展容积", f"+{info['extension_volume_l']:.1f}", "卷口线以上 150 mm"],
    ]
    (OUT / "volume.md").write_text(_md(["部位", "容积 (L)", "来源"], rows), encoding="utf-8")
    return total


def main():
    for d in ("dxf/pieces", "pdf", "markers"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    P, seams, info = pt.build()
    info["front_pocket_volume_l"] = Polygon(P["A02"].marks[1][1]).area * 30.0 / 1e6
    problems = pt.check(P, seams, info)
    marks = markers(P)
    areas = {m: marker_png(m, *v) for m, v in marks.items()}
    body_sheet(P, info)
    overview(P)
    full_scale_pdf(P)
    dxf_out(P, marks)
    total = tables(P, seams, info, marks, areas)
    print(f"{len(P)} pattern pieces, {sum(p.qty for p in P.values())} cut parts, {len(seams)} seam checks")
    print(f"main {info['main_volume_l']:.1f} L, nominal total {total:.1f} L, roll-top flat width {info['roll_flat_width']:.0f} mm")
    print(f"estimated weight {info['weight_g']:.0f} g (assumed areal weights)")
    for m, (_, used, width) in marks.items():
        print(f"  {m}: {width} x {used:.0f} mm")
    if problems:
        print("PATTERN CHECK FAILED:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("pattern checks passed ->", OUT)


if __name__ == "__main__":
    main()
