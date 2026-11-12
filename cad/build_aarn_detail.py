"""Outputs for the detailed Aarn PM40 benchmark model (hollow shells, layers, internals, hardware).

    python3 cad/build_aarn_detail.py [--photos DIR]

Writes to cad/out/benchmark_aarn_pm40/detail/.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
from PIL import Image

import aarn_hardware as hw
import aarn_pm40_detail as D
import build_benchmark as bb
import drawing as d

OUT = Path(__file__).resolve().parent / "out" / "benchmark_aarn_pm40" / "detail"


def _dicts(parts):
    return {p.key: p.wp for p in parts}, {p.key: p.color for p in parts}


def export(parts):
    (OUT / "step").mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name="aarn_pm40_detail")
    for p in parts:
        asm.add(p.wp, name=p.key, color=cq.Color(*p.color))
    asm.export(str(OUT / "step" / "aarn_pm40_detail_assembly.step"))
    hard = [p for p in parts if p.key[0] == "H"]
    asm = cq.Assembly(name="aarn_pm40_hardware_in_place")
    for p in hard:
        asm.add(p.wp, name=p.key, color=cq.Color(*p.color))
    asm.export(str(OUT / "step" / "aarn_pm40_hardware_in_place.step"))


def bom(parts):
    rows = []
    for p in parts:
        b = p.wp.val().BoundingBox()
        rows.append([p.key, p.name, p.group, p.material, p.qty, p.basis, f"{b.xlen:.0f}×{b.ylen:.0f}×{b.zlen:.0f}"])
    head = ["编号", "名称", "分组", "材料", "数量", "依据", "包络尺寸 X×Y×Z (mm)"]
    with open(OUT / "bom_detail.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    (OUT / "bom_detail.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def renders(parts):
    (OUT / "render").mkdir(parents=True, exist_ok=True)
    P, C = _dicts(parts)
    for name, direction, par in [
        ("iso_rear", (1.0, -1.25, 0.75), True),
        ("iso_front", (-1.0, 1.6, 0.35), False),
        ("side", (-1, 0, 0), True),
        ("rear", (0, -1, 0), True),
        ("front", (0, 1, 0), True),
    ]:
        d.render_vtk(OUT / "render" / f"{name}.png", P, C, direction, size=(1600, 1600), zoom=1.05, parallel=par, tol=0.25)


def _clip(parts, box):
    out = {}
    for p in parts:
        try:
            r = p.wp.intersect(box)
            if r.vals() and r.val().Volume() > 1e-3:
                out[p.key] = r
        except Exception:
            pass
    return out


def sections(parts):
    (OUT / "section").mkdir(parents=True, exist_ok=True)
    C = {p.key: p.color for p in parts}
    half = cq.Workplane("XY").box(600, 1200, 1200).translate((300, 0, 300))
    cut = _clip(parts, half)
    d.render_vtk(OUT / "section" / "section_x0_side.png", cut, C, (-1, 0, 0), size=(1600, 1600), zoom=1.05, tol=0.25)
    d.render_vtk(OUT / "section" / "section_x0_iso.png", cut, C, (-1.0, -0.55, 0.45), size=(1600, 1600), zoom=1.05, tol=0.25)
    strap = cq.Workplane("XY").box(600, 1200, 1200).translate((300 + 56, 0, 300))
    cut = _clip(parts, strap)
    d.render_vtk(OUT / "section" / "section_x56_strap_side.png", cut, C, (-1, 0, 0), size=(1600, 1600), zoom=1.05, tol=0.25)
    for z, tag in ((300, "z300"), (60, "z60_base"), (125, "z125_belt")):
        low = cq.Workplane("XY").box(1200, 1200, 600).translate((0, 0, z - 300))
        cut = _clip(parts, low)
        d.render_vtk(OUT / "section" / f"section_{tag}_top.png", cut, C, (0, 0, 1), size=(1600, 1600), zoom=1.05, tol=0.25)


def exploded(parts):
    (OUT / "render").mkdir(parents=True, exist_ok=True)
    P = {p.key: p.wp.translate(D.explode_offset(p.key)) for p in parts}
    C = {p.key: p.color for p in parts}
    d.render_vtk(OUT / "render" / "exploded_iso.png", P, C, (1.0, -1.25, 0.6), size=(1800, 1800), zoom=1.0, tol=0.3)
    d.render_vtk(OUT / "render" / "exploded_side.png", P, C, (-1, 0, 0), size=(1800, 1800), zoom=1.0, tol=0.3)


def hardware_sheet():
    (OUT / "hardware").mkdir(parents=True, exist_ok=True)
    srb = hw.side_release_buckle(20)
    cl = hw.cord_lock(4)
    la = hw.lasso_loc_tab()
    zp = hw.zipper([(0, 0, 0), (40, 0, 3), (80, 0, 0)], (0, 0, 1), tape_w=20, slider_u=0.5)
    items = [
        ("20 mm 插扣（扣合）", {"f": srb["female"], "m": srb["male"]}, {"f": (0.25, 0.25, 0.27), "m": (0.45, 0.45, 0.48)}, (1, -1.4, 0.8)),
        ("20 mm 插扣（分开）", {"f": srb["female"], "m": srb["male"].translate((0, 0, 22))}, {"f": (0.25, 0.25, 0.27), "m": (0.45, 0.45, 0.48)}, (1, -1.4, 0.8)),
        ("梯扣", {"a": hw.ladder_lock(20)}, {"a": D.HARD}, (0.8, -1.4, 0.6)),
        ("胸带滑钩", {"a": hw.sternum_slider()}, {"a": D.HARD}, (1, 1.2, 0.8)),
        ("弹簧绳扣（剖开）", {k: v.intersect(cq.Workplane("XY").box(40, 40, 60).translate((0, 20, 0))) for k, v in cl.items()}, {"barrel": D.HARD, "plunger": (0.45, 0.45, 0.48), "spring": D.METAL}, (0.2, -1, 0.4)),
        ("Lasso Loc 挂扣标签", la, {"tab": D.TEAL, "cord": (0.0, 0.4, 0.4), "grip": D.HARD}, (0.6, -1.4, 0.4)),
        ("线圈拉链 + 拉头", zp, {"tape": D.MESH, "teeth": (0.3, 0.3, 0.32), "slider": D.HARD, "pull_cord": D.HARD}, (0.3, -1, 0.9)),
        ("织带挂环", {"a": hw.webbing_loop(20, 40, 6)}, {"a": D.WEB}, (1, -1.2, 0.5)),
    ]
    fig, axs = plt.subplots(2, 4, figsize=(16, 8.6))
    for ax, (label, P, C, direction) in zip(axs.flat, items):
        tmp = OUT / "hardware" / "_tmp.png"
        d.render_vtk(tmp, P, C, direction, size=(700, 700), zoom=1.1, tol=0.05)
        ax.imshow(Image.open(tmp))
        ax.set_title(label, fontsize=12)
        ax.axis("off")
        tmp.unlink()
    fig.suptitle("五金件库（通用规格示意，非 Aarn 实测）", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "hardware" / "hardware_sheet.png", dpi=120, facecolor="white")
    plt.close(fig)
    for name, wp in [("side_release_buckle_20mm_female", srb["female"]), ("side_release_buckle_20mm_male", srb["male"]), ("ladder_lock_20mm", hw.ladder_lock(20)), ("sternum_slider", hw.sternum_slider())]:
        cq.exporters.export(wp, str(OUT / "hardware" / f"{name}.step"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", type=Path, default=None)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    parts = D.build_detailed_parts()
    bad = [p.key for p in parts if not p.wp.val().isValid()]
    if bad:
        print("invalid:", bad)
    export(parts)
    rows = bom(parts)
    renders(parts)
    sections(parts)
    exploded(parts)
    hardware_sheet()
    if a.photos:
        P, _ = _dicts(parts)
        bb.OUT = OUT
        for tag, iou in bb.photo_overlay(P, a.photos).items():
            print(f"silhouette IoU {tag}: {iou:.3f}")
    print(f"{len(rows)} BOM lines, {sum(r[4] for r in rows)} pieces ->", OUT)


if __name__ == "__main__":
    main()
