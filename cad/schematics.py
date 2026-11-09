"""2D schematics: benchmark principle (report) and patent figures 6-7."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

import drawing  # noqa: F401  (sets CJK font)

OUT = Path(__file__).resolve().parent / "out" / "schematics"
OUT.mkdir(parents=True, exist_ok=True)


def _save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=250 if ext == "png" else None, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def arrow(ax, a, b, color="k", lw=1.0, style="-|>", ms=10):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=ms, lw=lw, color=color))


# --------------------------------------------------------------------------- benchmark (Aarn) principle


def benchmark_back_system():
    fig, axs = plt.subplots(1, 2, figsize=(15, 9), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axs[0]
    ax.set_title("Aarn Pace Magic 40 背负系统原理 (后视示意, 面向背板)", fontsize=12)
    # pack outline
    ax.add_patch(FancyBboxPatch((-140, 0), 280, 640, boxstyle="round,pad=0,rounding_size=60", fc="#eef3e6", ec="0.5", lw=1))
    # X-stays
    for s in (1, -1):
        ax.plot([-s * 100, s * 100], [560, 170], color="#555", lw=3, solid_capstyle="round")
    ax.text(0, 380, "X 形支撑杆\n(三维曲面成形)", ha="center", fontsize=9, color="#333", bbox=dict(fc="white", ec="none", alpha=0.8))
    # suspended mesh
    mesh = Polygon([(-115, 560), (115, 560), (95, 200), (-95, 200)], closed=True, fc=(0.4, 0.6, 0.9, 0.18), ec="#2b6cb0", lw=1.2, ls="--")
    ax.add_patch(mesh)
    ax.text(70, 470, "悬浮张紧网背板\n(蹦床式, 留通风间隙)", fontsize=9, color="#2b6cb0", ha="left")
    # top tensioners
    for s in (1, -1):
        arrow(ax, (s * 100, 565), (s * 128, 600), color="#2b6cb0")
    ax.text(0, 660, "背板张紧带: 拉紧→网面更绷, 背部间隙↑", ha="center", fontsize=8.5, color="#2b6cb0")
    # shoulder straps (seen from behind as two bands)
    for s in (1, -1):
        ax.plot([s * 45, s * 70, s * 95, s * 120], [585, 520, 380, 290], color="#777", lw=10, alpha=0.6, solid_capstyle="round")
    # U-Flow linked bottom tensioners
    ax.plot([-120, -105, -60, 0, 60, 105, 120], [290, 160, 70, 55, 70, 160, 290], color="#d9480f", lw=2.2)
    ax.add_patch(Rectangle((-70, 45), 140, 22, fc="none", ec="#d9480f", lw=1.2, ls=":"))
    ax.text(0, 20, "包底织带通道 (低摩擦)", ha="center", fontsize=9, color="#d9480f")
    arrow(ax, (-128, 250), (-128, 300), color="#d9480f")
    arrow(ax, (128, 300), (128, 250), color="#d9480f")
    ax.text(-135, 320, "左肩上提", fontsize=8.5, color="#d9480f", ha="right")
    ax.text(135, 230, "右肩随之下放", fontsize=8.5, color="#d9480f", ha="left")
    ax.text(0, 172, "U-Flow 联动下拉带: 两侧肩带下端由一根织带/绳相连\n总长不变, 肩部可自由起伏", ha="center", fontsize=8.5, color="#d9480f", bbox=dict(fc="white", ec="none", alpha=0.85))
    # load lifters, bungee stabilisers
    for s in (1, -1):
        ax.plot([s * 70, s * 125], [590, 625], color="#555", lw=1.5)
        ax.plot([s * 120, s * 150], [300, 140], color="#0f766e", lw=1.4, ls="--")
    ax.text(-185, 630, "负重调节带", fontsize=8.5, ha="center")
    ax.text(170, 150, "弹力稳定绳\n(肩带袋→腰带)", fontsize=8.5, color="#0f766e")
    # hipbelt
    ax.add_patch(FancyBboxPatch((-200, 40), 400, 90, boxstyle="round,pad=0,rounding_size=30", fc="none", ec="#444", lw=1.5))
    ax.text(0, -15, "Auto-Form 双织带腰带: 上/下两根织带分别收紧,\n让腰带包住髂嵴并把背板下部拉进腰曲", fontsize=8.5, ha="center", va="top")
    ax.set_xlim(-260, 260)
    ax.set_ylim(-70, 680)
    ax.set_aspect("equal")
    ax.axis("off")

    # side view: balance principle
    ax = axs[1]
    ax.set_title("侧视受力示意: 窄侧剖面 + 前置平衡袋", fontsize=12)
    # body
    torso = Polygon([(-60, 0), (60, 0), (70, 300), (55, 520), (20, 600), (-40, 600), (-70, 520), (-80, 300)], closed=True, fc="#f4e7da", ec="0.6")
    ax.add_patch(torso)
    ax.add_patch(Circle((-10, 660), 50, fc="#f4e7da", ec="0.6"))
    # pack
    ax.add_patch(FancyBboxPatch((-200, 60), 110, 520, boxstyle="round,pad=0,rounding_size=40", fc="#eef3e6", ec="0.4"))
    ax.text(-145, 600, "包体 (厚 20cm,\n贴背、窄侧剖面)", ha="center", fontsize=8.5)
    # front pockets
    ax.add_patch(FancyBboxPatch((70, 300), 45, 150, boxstyle="round,pad=0,rounding_size=15", fc="#e2e8f0", ec="0.4"))
    ax.add_patch(FancyBboxPatch((70, 70), 60, 80, boxstyle="round,pad=0,rounding_size=15", fc="#e2e8f0", ec="0.4"))
    ax.text(140, 380, "肩带水壶袋\n0.75L×2", fontsize=8.5)
    ax.text(140, 105, "腰带平衡袋\n1.5L×2", fontsize=8.5)
    # forces
    arrow(ax, (-145, 330), (-145, 210), color="#c92a2a", lw=1.6)
    ax.text(-140, 190, "W后", color="#c92a2a", fontsize=9)
    arrow(ax, (100, 375), (100, 290), color="#1971c2", lw=1.6)
    ax.text(105, 270, "W前", color="#1971c2", fontsize=9)
    ax.plot([-10, -10], [-20, 640], "k--", lw=0.8)
    ax.text(-5, -40, "人体重心线", fontsize=8.5, ha="center")
    ax.annotate("", xy=(-145, 20), xytext=(-10, 20), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(-78, 28, "力臂 L后", fontsize=8.5, ha="center")
    ax.text(-200, -110, "原理: 包体越薄越贴背 → 后部力臂 L后 越小; 前置袋提供反向力矩 W前·L前,\n"
            "使 合力作用线接近人体重心线 → 减少前倾代偿、肩颈与腰背肌肉负担。\n"
            "腰带承担主要载荷, 肩带只负责稳定 (可以松一点 → 肩部自由)。", fontsize=8.5, va="top")
    ax.set_xlim(-230, 260)
    ax.set_ylim(-200, 720)
    ax.set_aspect("equal")
    ax.axis("off")
    _save(fig, "benchmark_aarn_back_principle")


# --------------------------------------------------------------------------- patent figure 6: linkage principle


def fig6_linkage_principle():
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.2))
    for k, (ax, delta) in enumerate(zip(axs, (0, 28))):
        hw, zc, r = 66, 0, 7.8
        # housing outline
        t = np.linspace(-1, 1, 60)
        ax.plot(t * (hw + 12), 22 - 12 * (1 - t**2) - 2, "k-", lw=0.8)
        ax.plot(t * (hw + 12), -14 - 18 * (1 - t**2), "k-", lw=0.8)
        for s in (1, -1):
            ax.add_patch(Arc((s * (hw + 4), 2), 26, 34, theta1=-90 if s > 0 else 90, theta2=90 if s > 0 else 270, lw=0.8))
        # rollers
        for s in (1, -1):
            ax.add_patch(Circle((s * hw, zc), r, fc="white", ec="k", lw=0.8))
            ax.add_patch(Circle((s * hw, zc), 2, fc="white", ec="k", lw=0.6))
        # web: under rollers, then up and outwards to the straps
        L = 60
        ax.plot([-hw, hw], [zc - r, zc - r], "k-", lw=1.6)
        for s, dz in ((1, -delta), (-1, delta)):
            th = np.linspace(-np.pi / 2, 0.35, 20) if s > 0 else np.linspace(np.pi + 0.35 * -1, 3 * np.pi / 2, 20)[::-1]
            xs = s * hw + r * np.cos(th) if s > 0 else -hw + r * np.cos(th)
            ys = zc + r * np.sin(th)
            ax.plot(xs, ys, "k-", lw=1.6)
            x0, y0 = xs[-1], ys[-1]
            x1, y1 = s * (hw + 30), zc + L + dz
            ax.plot([x0, x1], [y0, y1], "k-", lw=1.6)
            ax.add_patch(Rectangle((x1 - 8, y1), 16, 10, fc="white", ec="k", lw=0.8))
        # centring clip and elastic
        cx = -delta * 0.9
        ax.add_patch(Rectangle((cx - 4, zc - r - 3), 8, 6, fc="white", ec="k", lw=0.8))
        for s in (1, -1):
            px = s * 24
            ax.add_patch(Circle((px, zc + 4), 3, fc="white", ec="k", lw=0.7))
            n = 9
            xs = np.linspace(cx + s * 4, px, n * 2 + 1)
            ys = np.linspace(zc - r, zc + 1, n * 2 + 1) + np.array([0, 1.2] * n + [0]) * 0.0 + np.array([(-1) ** i * 1.2 for i in range(n * 2 + 1)])
            ax.plot(xs, ys, "k-", lw=0.6)
        # stops
        for s in (1, -1):
            yy = zc + 0.4 * L + (-delta if s > 0 else delta) * 0.4
            ax.add_patch(Rectangle((s * (hw + 30 * 0.4) - 4 + s * 2, yy), 8, 5, fc="k", ec="k"))
        if delta:
            arrow(ax, (-(hw + 42), L - 5), (-(hw + 42), L + delta + 5))
            arrow(ax, ((hw + 42), L + 5), ((hw + 42), L - delta - 5))
            arrow(ax, (12, -22), (-24, -22), style="-|>")
            ax.text(-(hw + 50), L + delta / 2, "Δ", fontsize=11, ha="right", va="center")
            ax.text((hw + 50), L - delta / 2, "Δ", fontsize=11, ha="left", va="center")
        # numerals (patent figure)
        lab = [("63", (hw, -r), (hw + 30, -30)), ("7", (hw + 20, L * 0.65 - (delta if delta else 0) * 0.65), (hw + 50, 20)),
               ("72", (cx, zc - r), (cx - 10, -38)), ("68", (24, 4), (30, 36)), ("69", (12, -4), (8, 40)),
               ("71", (hw + 14, zc + 0.4 * L - delta * 0.4), (hw + 60, -6))]
        for txt, a, b in lab:
            ax.annotate(txt, xy=a, xytext=b, fontsize=9, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5))
        ax.text(0, -62, "(a)" if k == 0 else "(b)", ha="center", fontsize=11)
        ax.set_xlim(-130, 130)
        ax.set_ylim(-70, 100)
        ax.set_aspect("equal")
        ax.axis("off")
    _save(fig, "fig6_linkage_principle")


# --------------------------------------------------------------------------- patent figure 7: lock states


def fig7_lock_states():
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    for k, ax in enumerate(axs):
        locked = k == 1
        # housing section (rear wall) and web
        ax.add_patch(Rectangle((-40, -6), 80, 6, fc="white", ec="k", hatch="////", lw=0.8))
        ax.plot([-40, 40], [3, 3], "k-", lw=2.0)
        # cam pivot
        cx, cy = 0, 18
        ax.add_patch(Circle((cx, cy), 2, fc="white", ec="k", lw=0.8))
        th = np.linspace(0, 2 * np.pi, 120)
        ang = np.radians(-90 if locked else 0)
        rr = 9 + 6 * (0.5 + 0.5 * np.cos(th))
        xs, ys = cx + rr * np.cos(th + ang), cy + rr * np.sin(th + ang)
        ax.plot(xs, ys, "k-", lw=0.9)
        # lever
        la = np.radians(-90 + (0 if locked else 70))
        ax.plot([cx, cx + 40 * np.cos(la + np.pi)], [cy, cy + 40 * np.sin(la + np.pi)], "k-", lw=3)
        if not locked:
            ax.annotate("", xy=(30, 3), xytext=(-30, 3), arrowprops=dict(arrowstyle="<|-|>", lw=0.7))
        else:
            ax.plot([-6, 6], [5.5, 5.5], "k-", lw=0.6)
            ax.plot([-4, 4], [7, 7], "k-", lw=0.6)
        for txt, a, b in (("62", (30, -3), (44, -16)), ("7", (-30, 3), (-46, 12)), ("81", (cx + 8, cy + 8), (22, 40)), ("82", (cx + 25 * np.cos(la + np.pi), cy + 25 * np.sin(la + np.pi)), (-38, 40))):
            ax.annotate(txt, xy=a, xytext=b, fontsize=9, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5))
        ax.text(0, -28, "(a)" if k == 0 else "(b)", ha="center", fontsize=11)
        ax.set_xlim(-60, 60)
        ax.set_ylim(-35, 65)
        ax.set_aspect("equal")
        ax.axis("off")
    _save(fig, "fig7_lock_states")


if __name__ == "__main__":
    benchmark_back_system()
    fig6_linkage_principle()
    fig7_lock_states()
    print("schematics ->", OUT)
