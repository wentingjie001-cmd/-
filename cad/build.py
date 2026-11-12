"""Generate every CAD deliverable from the parametric model.

    python3 cad/build.py            # everything
    python3 cad/build.py --fast     # skip high-resolution renders

Outputs go to cad/out/.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq
import ezdxf
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

import backpack_model as m
import drawing as d

OUT = Path(__file__).resolve().parent / "out"

BACK_SYSTEM = ("y_frame", "mesh_panel", "lumbar_pad", "tension_straps", "hub_housing", "rollers", "cam_lever", "pivot_plate", "webbing")


def ensure(*names):
    for n in names:
        (OUT / n).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- 3D exports


def export_3d(parts):
    ensure("step", "stl")
    asm = m.build_assembly(parts)
    asm.export(str(OUT / "step" / "backpack_40L_assembly.step"))
    hub = cq.Assembly(name="linkage_hub")
    for k, v in m.hub_module(parts).items():
        hub.add(v, name=k, color=cq.Color(*m.COLORS[k]))
    hub.export(str(OUT / "step" / "linkage_hub_assembly.step"))
    for k in m.HARD_PARTS:
        cq.exporters.export(parts[k], str(OUT / "step" / f"{k}.step"))
        tol = 0.15 if k == "y_frame" else 0.05
        cq.exporters.export(parts[k], str(OUT / "stl" / f"{k}_1to1.stl"), tolerance=tol, angularTolerance=0.2)
    # printable housing halves so the rollers can be inserted before closing
    front, rear = split_housing(parts)
    cq.exporters.export(front, str(OUT / "stl" / "hub_front_shell_1to1.stl"), tolerance=0.05, angularTolerance=0.2)
    cq.exporters.export(rear, str(OUT / "stl" / "hub_rear_shell_1to1.stl"), tolerance=0.05, angularTolerance=0.2)
    # scale model (手办): whole pack at 1:4
    allc = d.compound(parts.values()).scale(0.25)
    cq.exporters.export(cq.Workplane().add(allc), str(OUT / "stl" / "backpack_scale_1to4.stl"), tolerance=0.15, angularTolerance=0.3)


# --------------------------------------------------------------------------- renders


def renders(parts, size):
    ensure("render")
    for v in ("iso_front", "iso_rear", "left", "rear", "front"):
        d.render_vtk(OUT / "render" / f"backpack_{v}.png", parts, m.COLORS, d.VIEWS[v][0], size=size)
    back = {k: parts[k] for k in BACK_SYSTEM}
    d.render_vtk(OUT / "render" / "back_system_iso.png", back, m.COLORS, (1.0, -1.25, 0.6), size=size, zoom=0.95)
    hub = m.hub_module(parts)
    d.render_vtk(OUT / "render" / "hub_iso_pack_side.png", hub, m.COLORS, (0.8, 1.4, 0.9), size=(size[0], int(size[1] * 0.75)))
    d.render_vtk(OUT / "render" / "hub_iso_body_side.png", hub, m.COLORS, (0.6, -1.4, 0.7), size=(size[0], int(size[1] * 0.75)))
    d.render_vtk(OUT / "render" / "hub_exploded.png", exploded_hub(parts), m.COLORS | EXPLODE_COLORS, (1.0, 1.1, 0.8), size=size)


# --------------------------------------------------------------------------- exploded hub


EXPLODE_COLORS = {"hub_front_shell": (0.30, 0.31, 0.33), "hub_rear_shell": (0.22, 0.23, 0.25)}


def split_housing(parts):
    p = m.P
    ymid = p.hub_y0 + p.hub_depth / 2
    h = parts["hub_housing"]
    big = 400
    front = h.intersect(cq.Workplane("XY").box(big, big, big).translate((0, ymid - big / 2, 0)))
    rear = h.intersect(cq.Workplane("XY").box(big, big, big).translate((0, ymid + big / 2, 0)))
    return front, rear


def exploded_hub(parts, gap=40):
    front, rear = split_housing(parts)
    return {
        "pivot_plate": parts["pivot_plate"].translate((0, -2.2 * gap, 0)),
        "hub_front_shell": front.translate((0, -gap, 0)),
        "rollers": parts["rollers"],
        "hub_rear_shell": rear.translate((0, gap, 0)),
        "cam_lever": parts["cam_lever"].translate((0, 2.2 * gap, 0)),
    }


# --------------------------------------------------------------------------- design-patent views


def design_views(name, shapes, views=("front", "rear", "left", "right", "top", "bottom", "iso_front"), lw=0.6, figsize=(8, 10)):
    ensure(f"design/{name}")
    for v in views:
        direction, label = d.VIEWS[v]
        vis, _ = d.hlr_lines(shapes, direction)
        d.save_view(OUT / "design" / name / f"{v}", vis, title=label, lw=lw, figsize=figsize)


def partial_design_views(name, claimed, rest, views=("front", "rear", "left", "right", "top", "bottom", "iso_rear")):
    """局部外观设计: claimed part solid, remainder dashed."""
    ensure(f"design/{name}")
    for v in views:
        direction, label = d.VIEWS[v]
        g_claim, g_rest = d.hlr_lines_groups([claimed, rest], direction)
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.add_collection(LineCollection(g_rest, colors="k", linewidths=0.45, linestyles=(0, (4, 3))))
        ax.add_collection(LineCollection(g_claim, colors="k", linewidths=0.7))
        x0, x1, y0, y1 = d.bounds(g_claim + g_rest)
        pad = 0.05 * max(x1 - x0, y1 - y0)
        ax.set_xlim(x0 - pad, x1 + pad)
        ax.set_ylim(y0 - pad, y1 + pad)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(label, fontsize=12, y=-0.06)
        fig.tight_layout()
        for ext in ("png", "pdf", "svg"):
            fig.savefig(OUT / "design" / name / f"{v}.{ext}", dpi=300 if ext == "png" else None, facecolor="white")
        plt.close(fig)


# --------------------------------------------------------------------------- invention figures


def _column_labels(anchors2d, bbox, spacing, margin):
    """Place numerals in two columns (left/right of the drawing), no overlaps."""
    x0, x1, y0, y1 = bbox
    cx = (x0 + x1) / 2
    left = sorted([a for a in anchors2d if a[1][0] < cx], key=lambda a: -a[1][1])
    right = sorted([a for a in anchors2d if a[1][0] >= cx], key=lambda a: -a[1][1])
    out = []
    for col, xs in ((left, x0 - margin), (right, x1 + margin)):
        last = None
        for text, a in col:
            ty = a[1]
            if last is not None and ty > last - spacing:
                ty = last - spacing
            last = ty
            out.append((text, tuple(a), (xs, ty)))
    return out


def figure(path, shape, direction, anchors3d, hidden=False, figsize=(8, 10), spacing=None, margin=None, extra_lines=None, lw=0.6):
    vis, hid = d.hlr_lines(shape, direction, hidden=hidden)
    bb = d.bounds(vis)
    size = max(bb[1] - bb[0], bb[3] - bb[2])
    spacing = spacing or size * 0.035
    margin = margin or size * 0.09
    a2 = [(t, d.project_point(p, direction)) for t, p in anchors3d]
    labels = _column_labels(a2, bb, spacing, margin)
    if extra_lines:
        vis = vis + extra_lines
    d.save_view(path, vis, hid, labels=labels, lw=lw, figsize=figsize)


def invention_figures(parts):
    ensure("invention")
    p = m.P
    hw = p.hub_w / 2 - 12
    full = d.compound(parts.values())
    A = {
        "1": (141, p.body_y0 + 120, 420),
        "16": (60, p.body_y0 + 70, 640),
        "21": (40, 52, 568),
        "22": (-86, 32, 400),
        "23": (0, 27, p.frame_node_z),
        "24": (0, 33, 140),
        "3": (-40, p.mesh_y + 6, 470),
        "4": (60, 0, 200),
        "41": (0, 0, 160),
        "51": (100, 20, 552),
        "52": (-104, 24, 556),
        "53": (112, 30, 180),
        "54": (-120, 32, 180),
        "6": (-40, p.hub_y0 + 14, p.hub_z0 + 6),
        "7": (130, -40, 220),
        "71": (-(hw + 22), p.hub_y0 + 10, p.hub_z0 + 62),
        "81": (12, p.hub_y0 + p.hub_depth + 5, p.hub_z0 + 20),
        "82": (0, 64, 18 + p.hub_z0 - 40),
        "9": (-88, p.hub_y0 - 10, p.hub_z0 + 22),
        "10": (-90, -110, 622),
        "101": (124, -270, 452),
        "102": (-100, 10, 628),
        "11": (40, -232, 500),
        "12": (180, -110, p.hub_z0 + 70),
        "121": (-210, -150, p.hub_z0 + 50),
        "122": (0, -306, p.hub_z0 + 34),
        "13": (-60, p.body_y0 + 228, 250),
        "14": (40, p.body_y0 + 222, 380),
        "15": (p.body_w / 2 + 14, p.body_y0 + 100, 150),
    }

    def pick(*keys):
        return [(k, A[k]) for k in keys]

    figure(OUT / "invention" / "fig1_rear_iso", full, d.VIEWS["iso_rear"][0], pick("1", "16", "3", "4", "6", "7", "10", "101", "102", "11", "12", "121", "122", "15"))
    figure(OUT / "invention" / "fig2_side", full, d.VIEWS["left"][0], pick("1", "16", "22", "3", "4", "6", "7", "10", "101", "12", "13", "14", "15"))
    back = d.compound([parts[k] for k in BACK_SYSTEM])
    figure(OUT / "invention" / "fig3_back_system_pack_side", back, (0, 1, 0), pick("21", "22", "23", "24", "3", "4", "51", "52", "53", "54", "6", "7", "71", "82", "9"))

    # exploded hub
    ex = exploded_hub(parts)
    gap = 40
    ymid = p.hub_y0 + p.hub_depth / 2
    E = [
        ("92", (60, p.hub_y0 - 10 - 2.2 * gap, p.hub_z0 + 40)),
        ("91", (0, p.hub_y0 - 8 - 2.2 * gap, p.hub_z0 + 6)),
        ("61", (-40, p.hub_y0 - gap, p.hub_z0 + 10)),
        ("66", (hw + 8, ymid - gap, p.hub_z0 + 46)),
        ("63", (-hw, p.hub_y0 + 10, p.hub_z0 + 32 + p.roller_d / 2)),
        ("64", (hw, p.hub_y0 + 1, p.hub_z0 + 32)),
        ("65", (20, ymid, p.hub_z0 + 32 - p.roller_d / 2 - 1)),
        ("62", (40, ymid + gap + 8, p.hub_z0 + 8)),
        ("67", (0, 34 + gap, p.hub_z0 + 46)),
        ("68", (-24, p.hub_y0 + p.hub_depth + 5 + gap, p.hub_z0 + 30)),
        ("83", (15, p.hub_y0 + p.hub_depth + 3 + gap, p.hub_z0 + 29)),
        ("81", (12, p.hub_y0 + p.hub_depth + 5 + 2.2 * gap, p.hub_z0 + 20)),
        ("82", (0, p.hub_y0 + p.hub_depth + 15 + 2.2 * gap, p.hub_z0 - 18)),
    ]
    figure(OUT / "invention" / "fig4_hub_exploded", d.compound(ex.values()), (1.0, 1.1, 0.8), E, figsize=(10, 8))

    # hub front view (from pack side) with hidden lines + webbing
    hub_and_web = d.compound([parts[k] for k in ("hub_housing", "rollers", "cam_lever")] + [webbing_inside(p)])
    F = [
        ("6", (40, 60, p.hub_z0 + 6)),
        ("63", (hw, 60, p.hub_z0 + 32 + p.roller_d / 2)),
        ("65", (-10, 60, p.hub_z0 + 32 - p.roller_d / 2 - 1)),
        ("7", (-(hw + 16), 60, p.hub_z0 + 58)),
        ("67", (0, 60, p.hub_z0 + 46)),
        ("68", (-24, 60, p.hub_z0 + 30)),
        ("82", (0, 60, p.hub_z0 - 10)),
    ]
    figure(OUT / "invention" / "fig5_hub_front_hidden", hub_and_web, (0, 1, 0), F, hidden=True, figsize=(10, 6))


def webbing_inside(p):
    """Linkage web path inside the housing (for the hidden-line figure)."""
    hw = p.hub_w / 2 - 12
    ym = p.hub_y0 + p.hub_depth / 2
    zc = p.hub_z0 + 32
    r = p.roller_d / 2 + 0.8
    w = (
        cq.Workplane("XZ")
        .moveTo(-hw - 22, zc + 30)
        .lineTo(-hw - r, zc + 2)
        .threePointArc((-hw, zc - r), (-hw + r * 0.7, zc - r * 0.7))
        .lineTo(hw - r * 0.7, zc - r * 0.7)
        .threePointArc((hw, zc - r), (hw + r, zc + 2))
        .lineTo(hw + 22, zc + 30)
    )
    path = w.wire().val()
    prof = cq.Workplane(cq.Plane(origin=path.startPoint(), xDir=(0, 1, 0), normal=path.tangentAt(0))).rect(p.web_w, 1.4)
    return prof.sweep(cq.Workplane().add(path)).translate((0, ym - 0, 0)).translate((0, 0, 0))


# --------------------------------------------------------------------------- engineering drawing


def hub_drawing(parts):
    """A3 landscape sheet: linkage housing, 3 views, key dimensions, title block."""
    ensure("drawings")
    p = m.P
    hw = p.hub_w / 2 - 12
    housing = d.compound([parts["hub_housing"], parts["rollers"]])
    fv, fh = d.hlr_lines(housing, (0, 1, 0), hidden=True)  # front (from pack side)
    tv, th = d.hlr_lines(housing, (0, 0, 1), hidden=True)  # top
    sv, sh = d.hlr_lines(housing, (-1, 0, 0), hidden=True)  # right side

    fig = plt.figure(figsize=(16.54, 11.69))  # A3
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.axis("off")
    ax.plot([10, 410, 410, 10, 10], [10, 10, 287, 287, 10], "k-", lw=1.2)

    def place(lines, hidden, ox, oy, s=1.0):
        tr = lambda L: [np.column_stack([q[:, 0] * s + ox, q[:, 1] * s + oy]) for q in L]
        ax.add_collection(LineCollection(tr(hidden), colors="0.4", linewidths=0.35, linestyles=(0, (2.5, 1.5))))
        ax.add_collection(LineCollection(tr(lines), colors="k", linewidths=0.6))
        return lambda x, y: (x * s + ox, y * s + oy)

    s = 1.0
    # front view: drawing x = -X, y = Z.  centre it at (140, 190)
    F = place(fv, fh, 140, 190 - (p.hub_z0 + 23), s)
    # top view below front: drawing x = -X, y = -Y
    T = place(tv, th, 140, 105 + (p.hub_y0 + p.hub_depth / 2), s)
    # side view right of front: viewer at -X: drawing x = -Y, y = Z
    S = place(sv, sh, 300 + (p.hub_y0 + p.hub_depth / 2), 190 - (p.hub_z0 + 23), s)

    z0 = p.hub_z0
    # front view dims
    d.dim_linear(ax, F(-(hw + 12), z0 + 32), F(hw + 12, z0 + 32), 34, f"{p.hub_w:.0f}")
    d.dim_linear(ax, F(-hw, z0 + 32), F(hw, z0 + 32), 24, f"{2 * hw:.0f}")
    d.dim_linear(ax, F(hw + 12, z0), F(hw + 12, z0 + 46), 12, "46", horizontal=False)
    d.dim_linear(ax, F(hw, z0), F(hw, z0 + 18), -(2 * hw + 40), "18", horizontal=False)
    d.dim_diameter(ax, F(-hw, z0 + 32), p.roller_d / 2, 135, f"Ø{p.roller_d:.0f} 滚轮")
    d.dim_diameter(ax, F(0, z0 + 54), 8, 45, "Ø16/Ø8.4 插座")
    ax.text(*F(0, z0 - 26), "主视图 (自包体侧)", ha="center", fontsize=9)
    # top view dims
    d.dim_linear(ax, T(-(hw + 12), -p.hub_y0), T(-(hw + 12), -(p.hub_y0 + p.hub_depth)), -14, f"{p.hub_depth:.0f}", horizontal=False)
    ax.text(*T(0, -(p.hub_y0 + p.hub_depth + 30)), "俯视图", ha="center", fontsize=9)
    # side view dims
    d.dim_linear(ax, S(-p.hub_y0, z0 + 70), S(-(p.hub_y0 + p.hub_depth + 8), z0 + 70), 4, f"{p.hub_depth + 8:.0f}")
    d.dim_linear(ax, S(-p.hub_y0, z0 + 46), S(-p.hub_y0, z0 + 62), -14, "16", horizontal=False)
    ax.text(*S(-(p.hub_y0 + p.hub_depth / 2), z0 - 26), "右视图", ha="center", fontsize=9)

    # technical notes
    notes = [
        "技术要求:",
        "1. 壳体材料 PA66+30%GF，前后壳分体注塑，超声波焊接或 4×M3 自攻螺钉连接；",
        "2. 滚轮材料 POM，内嵌 Ø4 不锈钢轴，滚轮外圆 Ra≤0.8，转动无卡滞；",
        "3. 联动带通道内表面拔模 1°，棱边倒圆 R≥1，避免磨损织带；",
        "4. 未注圆角 R2，未注公差按 GB/T 1804-m；",
        "5. 插座孔与 Ø6 背架杆过盈 0.05~0.1，或以 M3 横销固定；",
        "6. 本图为概念设计图，量产前须经打样与负载/疲劳测试修正。",
    ]
    for i, t in enumerate(notes):
        ax.text(250, 105 - i * 7, t, fontsize=8, va="top")

    # title block
    tb_x, tb_y, tb_w, tb_h = 250, 10, 160, 40
    ax.plot([tb_x, tb_x + tb_w, tb_x + tb_w, tb_x, tb_x], [tb_y, tb_y, tb_y + tb_h, tb_y + tb_h, tb_y], "k-", lw=0.9)
    for yy in (tb_y + 10, tb_y + 20, tb_y + 30):
        ax.plot([tb_x, tb_x + tb_w], [yy, yy], "k-", lw=0.5)
    ax.plot([tb_x + 80, tb_x + 80], [tb_y, tb_y + tb_h], "k-", lw=0.5)
    rows = [
        ("名称: 背负系统联动座 (壳体+滚轮)", "图号: BP40-HUB-001"),
        ("材料: PA66-GF30 / POM / SUS304", "比例: 1:1   单位: mm"),
        ("投影: 第一角画法", "版本: A0 概念"),
        ("项目: 40L 随动背负系统背包", "日期: 2026-11"),
    ]
    for i, (a, b) in enumerate(rows):
        yy = tb_y + tb_h - 5 - i * 10
        ax.text(tb_x + 3, yy, a, fontsize=7.5, va="center")
        ax.text(tb_x + 83, yy, b, fontsize=7.5, va="center")

    for ext in ("pdf", "png", "svg"):
        fig.savefig(OUT / "drawings" / f"BP40-HUB-001_linkage_hub.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    plt.close(fig)

    # DXF of the three views (true scale, mm)
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.layers.add("VISIBLE", color=7)
    doc.layers.add("HIDDEN", color=8, linetype="DASHED")
    msp = doc.modelspace()
    for lines, hidden, off in ((fv, fh, (0, 0)), (tv, th, (0, -120)), (sv, sh, (220, 0))):
        for L, layer in ((lines, "VISIBLE"), (hidden, "HIDDEN")):
            for q in L:
                msp.add_lwpolyline([(x + off[0], y + off[1]) for x, y in q], dxfattribs={"layer": layer})
    doc.saveas(OUT / "drawings" / "BP40-HUB-001_linkage_hub.dxf")


def frame_drawing(parts):
    """Y-frame: rear + side views with bend-point table."""
    ensure("drawings")
    p = m.P
    frame = d.compound([parts["y_frame"]])
    rv, _ = d.hlr_lines(frame, (0, -1, 0))
    sv, _ = d.hlr_lines(frame, (1, 0, 0))
    fig = plt.figure(figsize=(11.69, 16.54))  # A3 portrait
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 297)
    ax.set_ylim(0, 420)
    ax.axis("off")
    ax.plot([10, 287, 287, 10, 10], [10, 10, 410, 410, 10], "k-", lw=1.2)
    s = 0.5
    tr = lambda L, ox, oy: [np.column_stack([q[:, 0] * s + ox, q[:, 1] * s + oy]) for q in L]
    ax.add_collection(LineCollection(tr(rv, 110, 50), colors="k", linewidths=0.6))
    ax.add_collection(LineCollection(tr(sv, 235 - 40 * s, 50), colors="k", linewidths=0.6))
    R = lambda x, z: (x * s + 110, z * s + 50)
    d.dim_linear(ax, R(-p.frame_top_half_w, p.frame_top_z), R(p.frame_top_half_w, p.frame_top_z), 20, f"{2 * p.frame_top_half_w:.0f}")
    d.dim_linear(ax, R(-p.frame_top_half_w, p.hub_z0 + 46), R(-p.frame_top_half_w, p.frame_top_z), -20, f"{p.frame_top_z - p.hub_z0 - 46:.0f}", horizontal=False)
    d.dim_linear(ax, R(30, p.hub_z0 + 46), R(30, p.frame_node_z), 40, f"{p.frame_node_z - p.hub_z0 - 46:.0f}", horizontal=False)
    ax.text(110, 70, "后视图 (面向使用者背部)", ha="center", fontsize=9)
    ax.text(235, 70, "左视图", ha="center", fontsize=9)
    table = [
        "折弯点坐标 (mm, 原点=包底中心, X 左右, Y 离背方向, Z 向上)",
        f"上横梁: (±{p.frame_top_half_w:.0f},40,{p.frame_top_z:.0f}) (±55,49,{p.frame_top_z + 6:.0f}) (0,52,{p.frame_top_z + 8:.0f})",
        f"侧臂:   (±{p.frame_top_half_w:.0f},40,{p.frame_top_z:.0f}) (±98,36,470) (±66,30,340) (±22,30,230) (0,34,{p.frame_node_z:.0f})",
        f"下立杆: (0,34,{p.frame_node_z:.0f}) (0,33,150) (0,34,{p.hub_z0 + 46:.0f})  插入联动座插座",
        "材料: 7075-T6 铝合金 Ø6 实心杆 (下立杆 Ø7)，或 Ø6.5 玻纤/碳纤杆 + 铝接头",
        "汇合节点: 铝合金 Y 型三通接头，与杆胶接+铆接；上转角为 R12 弯管接头",
        "腰部前凸 (S 曲线) 最大 10 mm，可用手冷弯微调以适配个人背型",
    ]
    for i, t in enumerate(table):
        ax.text(20, 404 - i * 6, t, fontsize=7.5, va="top")
    tb_x, tb_y = 127, 10
    ax.plot([tb_x, 287, 287, tb_x, tb_x], [tb_y, tb_y, tb_y + 30, tb_y + 30, tb_y], "k-", lw=0.9)
    ax.text(tb_x + 4, tb_y + 22, "名称: Y 型背架    图号: BP40-FRM-001", fontsize=8)
    ax.text(tb_x + 4, tb_y + 13, "比例: 1:2   单位: mm   第一角画法", fontsize=8)
    ax.text(tb_x + 4, tb_y + 4, "项目: 40L 随动背负系统背包   版本: A0 概念", fontsize=8)
    for ext in ("pdf", "png", "svg"):
        fig.savefig(OUT / "drawings" / f"BP40-FRM-001_y_frame.{ext}", dpi=200 if ext == "png" else None, facecolor="white")
    plt.close(fig)


def bom(parts):
    rows = []
    for k, v in parts.items():
        s = v.val()
        bb = s.BoundingBox()
        rows.append({"part": k, "volume_mm3": round(s.Volume()), "bbox_mm": [round(bb.xlen), round(bb.ylen), round(bb.zlen)]})
    (OUT / "parts_summary.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    parts = m.build_parts()
    bom(parts)
    export_3d(parts)
    renders(parts, (900, 900) if a.fast else (1800, 1800))

    full = d.compound(parts.values())
    design_views("01_backpack_whole", full)
    hub = d.compound(m.hub_module(parts).values())
    design_views("03_linkage_hub", hub, views=("front", "rear", "left", "right", "top", "bottom", "iso_front"), figsize=(10, 6))
    claimed = d.compound([parts[k] for k in BACK_SYSTEM])
    rest = d.compound([v for k, v in parts.items() if k not in BACK_SYSTEM])
    partial_design_views("02_backpack_partial_back_system", claimed, rest)

    invention_figures(parts)
    hub_drawing(parts)
    frame_drawing(parts)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
