"""Outputs for the reverse-engineered Aarn Pace Magic 40 benchmark model.

    python3 cad/build_benchmark.py [--photos DIR]

``--photos`` is an optional folder with the official product photos
(pm40_01.jpg rear, pm40_03.jpg side, pm40_00.jpg front-angle) used for the
photo-vs-model comparison sheets. Photos are not stored in the repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

import backpack_model as ours
import benchmark_aarn_pm40 as aarn
import drawing as d

OUT = Path(__file__).resolve().parent / "out" / "benchmark_aarn_pm40"

PHOTO_VIEWS = [
    ("pm40_01.jpg", "rear", (0, -1, 0), "背面"),
    ("pm40_03.jpg", "side", (-1, 0, 0), "侧面"),
    ("pm40_00.jpg", "front_angle", (-1.0, 1.6, 0.35), "正面斜视"),
]


def export(parts):
    (OUT / "step").mkdir(parents=True, exist_ok=True)
    (OUT / "stl").mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name="aarn_pm40_benchmark")
    for k, v in parts.items():
        asm.add(v, name=k, color=cq.Color(*aarn.COLORS[k]))
    asm.export(str(OUT / "step" / "aarn_pm40_benchmark_assembly.step"))
    cq.exporters.export(aarn.x_stays(), str(OUT / "step" / "aarn_x_stays.step"))
    allc = d.compound(parts.values()).scale(0.25)
    cq.exporters.export(cq.Workplane().add(allc), str(OUT / "stl" / "aarn_pm40_scale_1to4.stl"), tolerance=0.15, angularTolerance=0.3)


def renders(parts):
    (OUT / "render").mkdir(parents=True, exist_ok=True)
    for name, direction in [("iso_front", (1.0, 1.25, 0.75)), ("iso_rear", (1.0, -1.25, 0.75)), ("rear", (0, -1, 0)), ("side", (-1, 0, 0))]:
        d.render_vtk(OUT / "render" / f"{name}.png", parts, aarn.COLORS, direction, size=(1400, 1400), zoom=1.05)
    frame = ("aarn_x_stays", "aarn_tensioners", "aarn_uflow", "aarn_lumbar")
    for name, keys in [("back_system_iso", frame), ("back_system_with_mesh_iso", frame + ("aarn_mesh_back", "aarn_mesh_dark"))]:
        back = {k: parts[k] for k in keys}
        d.render_vtk(OUT / "render" / f"{name}.png", back, aarn.COLORS, (1.0, -1.25, 0.6), size=(1400, 1400), zoom=0.95)


def line_views(parts):
    full = d.compound(parts.values())
    (OUT / "views").mkdir(parents=True, exist_ok=True)
    for v in ("front", "rear", "left", "right", "top", "bottom", "iso_front"):
        direction, label = d.VIEWS[v]
        vis, _ = d.hlr_lines(full, direction)
        d.save_view(OUT / "views" / v, vis, title=label)


def photo_comparison(parts, photos: Path):
    (OUT / "compare").mkdir(parents=True, exist_ok=True)
    for fname, tag, direction, label in PHOTO_VIEWS:
        p = photos / fname
        if not p.exists():
            continue
        rpath = OUT / "compare" / f"_model_{tag}.png"
        d.render_vtk(rpath, parts, aarn.COLORS, direction, size=(1200, 1200), zoom=1.0, parallel=tag != "front_angle")
        fig, axs = plt.subplots(1, 2, figsize=(14, 7.4))
        axs[0].imshow(Image.open(p))
        axs[0].set_title(f"官网照片（{label}）", fontsize=12)
        axs[1].imshow(Image.open(rpath))
        axs[1].set_title(f"逆向重建模型（{label}）", fontsize=12)
        for a in axs:
            a.axis("off")
        fig.tight_layout()
        fig.savefig(OUT / "compare" / f"photo_vs_model_{tag}.png", dpi=130, facecolor="white")
        plt.close(fig)
        rpath.unlink()


OVERLAY_VIEWS = [("side", (-1, 0, 0), "侧面"), ("rear", (0, -1, 0), "背面")]


def _to_photo_px(tag):
    """View coordinates (mm) -> photo pixels, from the calibration in PHOTO_CAL."""
    cal = aarn.PHOTO_CAL[tag]
    if tag == "side":
        m = cal["mm_px"]
        return lambda X, Y: (cal["x_back"] + (aarn.Y0 + X) / m, cal["row_bottom"] - Y / m)
    return lambda X, Y: (cal["x_mid"] + X / cal["mm_px_x"], cal["row_top"] + (cal["z_top"] - Y) / cal["mm_px_z"])


def _silhouette(wp, direction, to_px, size):
    im = Image.new("L", size, 0)
    dr = ImageDraw.Draw(im)
    _, xa, ya = d.view_frame(direction)
    for s in wp.vals():
        if not isinstance(s, cq.Shape):
            continue
        vs, fs = s.tessellate(0.8, 0.3)
        P = np.array([[v.x, v.y, v.z] for v in vs])
        px, py = to_px(P @ xa, P @ ya)
        for f in fs:
            dr.polygon([(px[i], py[i]) for i in f], fill=255)
    return np.asarray(im) > 0


def _photo(tag, photos: Path):
    cal = aarn.PHOTO_CAL[tag]
    img = Image.open(photos / cal["file"]).convert("RGB")
    if tag == "side":
        img = img.rotate(cal["rot_deg"], center=cal["rot_center"], fillcolor=(255, 255, 255))
    hsv = np.asarray(img.convert("HSV")).astype(int)
    fg = ~((hsv[..., 1] < 25) & (hsv[..., 2] > 235))
    return img, fg


def photo_overlay(parts, photos: Path):
    """Model silhouettes projected onto the photo with the calibration in PHOTO_CAL; returns IoU per view."""
    (OUT / "compare").mkdir(parents=True, exist_ok=True)
    scores = {}
    for tag, direction, label in OVERLAY_VIEWS:
        if not (photos / aarn.PHOTO_CAL[tag]["file"]).exists():
            continue
        img, fg = _photo(tag, photos)
        to_px = _to_photo_px(tag)
        masks = {k: _silhouette(v, direction, to_px, img.size) for k, v in parts.items()}
        model = np.logical_or.reduce(list(masks.values()))
        iou = (model & fg).sum() / (model | fg).sum()
        scores[tag] = float(iou)
        fig, ax = plt.subplots(figsize=(9, 9.4))
        ax.imshow(img, alpha=0.8)
        for k, m in masks.items():
            ax.contour(m, levels=[0.5], colors="#ff8c00", linewidths=0.6)
        ax.contour(model, levels=[0.5], colors="#d01010", linewidths=1.4)
        ax.set_xlim(0, img.width)
        ax.set_ylim(img.height, 0)
        ax.axis("off")
        ax.set_title(f"模型剪影叠加到官网照片（{label}）  红：整体外轮廓  橙：各部件轮廓  IoU = {iou:.2f}", fontsize=11)
        fig.tight_layout()
        fig.savefig(OUT / "compare" / f"photo_overlay_{tag}.png", dpi=130, facecolor="white")
        plt.close(fig)
    return scores


def vs_ours():
    """Side-by-side: benchmark vs our redesign, same scale and view."""
    (OUT / "compare").mkdir(parents=True, exist_ok=True)
    a_parts = aarn.build_parts()
    o_parts = ours.build_parts()
    for tag, direction in [("iso_rear", (1.0, -1.25, 0.75)), ("side", (-1, 0, 0))]:
        pa, po = OUT / "compare" / "_a.png", OUT / "compare" / "_o.png"
        d.render_vtk(pa, a_parts, aarn.COLORS, direction, size=(1000, 1000), zoom=1.0)
        d.render_vtk(po, o_parts, ours.COLORS, direction, size=(1000, 1000), zoom=1.0)
        fig, axs = plt.subplots(1, 2, figsize=(14, 7.4))
        axs[0].imshow(Image.open(pa))
        axs[0].set_title("对标款 Aarn Pace Magic 40（逆向重建）", fontsize=12)
        axs[1].imshow(Image.open(po))
        axs[1].set_title("我们的改版（随动背负系统）", fontsize=12)
        for a in axs:
            a.axis("off")
        fig.tight_layout()
        fig.savefig(OUT / "compare" / f"aarn_vs_ours_{tag}.png", dpi=130, facecolor="white")
        plt.close(fig)
        pa.unlink()
        po.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", type=Path, default=None)
    a = ap.parse_args()
    parts = aarn.build_parts()
    export(parts)
    renders(parts)
    line_views(parts)
    if a.photos:
        photo_comparison(parts, a.photos)
        for tag, iou in photo_overlay(parts, a.photos).items():
            print(f"silhouette IoU {tag}: {iou:.3f}")
    vs_ours()
    print("done ->", OUT)


if __name__ == "__main__":
    main()
