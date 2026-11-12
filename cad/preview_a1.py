"""3D preview of the A1 pack, assembled from the pattern data in ``patterns.py``.

    python3 preview_a1.py            # stills, callout sheets, turntable GIF, GLB, consistency table
    python3 preview_a1.py --fast     # stills only, lower resolution

The soft parts are surface meshes whose sizes come from the flat patterns (packed sections, pocket
placement lines, strap and belt outlines, anchor points). The hard parts (linkage hub, rollers, cam
lever, pivot plate) are the CadQuery solids from ``backpack_model.py``. This is a visual check of how
the pattern pieces go together; it is not a cloth simulation and not a manufacturing model.

Coordinates as in ``backpack_model.py``: X left/right, Y = 0 at the wearer's back with +Y towards the
pack, Z up with Z = 0 at the bottom seam.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import cadquery as cq
import numpy as np
from scipy.interpolate import CubicSpline

import aarn_hardware as hw  # generic buckle library
import backpack_model as m
import patterns as pt

OUT = Path(__file__).resolve().parent / "out" / "preview_a1"
Y0 = m.P.body_y0
R_BACK = 30.0  # the frame sheet keeps the back panel flat, so the back corners stay tight
WAIST = (0.0, -112.0)  # axis of the wearer's waist used to wrap the belt

BODY = (0.17, 0.30, 0.40)
BASE = (0.10, 0.16, 0.21)
SEAM = (0.10, 0.19, 0.26)
STRETCH = (0.47, 0.51, 0.55)
SPACER = (0.23, 0.25, 0.28)
WEB = (0.13, 0.13, 0.15)
ORANGE = (0.93, 0.42, 0.08)
HARD = (0.07, 0.07, 0.08)
ALU = (0.74, 0.75, 0.78)
TPU = (0.15, 0.16, 0.18)
ROLLER = (0.86, 0.86, 0.86)
YOKE = (0.30, 0.46, 0.58)  # same fabric as the body; drawn lighter so it can be told apart


@dataclass
class Part:
    key: str
    name: str
    group: str
    color: tuple
    v: np.ndarray
    f: np.ndarray


# --------------------------------------------------------------------------- mesh helpers


def merge(*meshes):
    vs, fs, off = [], [], 0
    for v, f in meshes:
        vs.append(np.asarray(v, float))
        fs.append(np.asarray(f, int) + off)
        off += len(v)
    return np.vstack(vs), np.vstack(fs)


def grid(G, close_u=False):
    """Triangles for a grid of points G[i, j]; the i direction can be closed."""
    nu, nv = G.shape[:2]
    idx = np.arange(nu * nv).reshape(nu, nv)
    iu = np.arange(nu if close_u else nu - 1)
    a, b = idx[iu][:, :-1], idx[(iu + 1) % nu][:, :-1]
    c, d = idx[(iu + 1) % nu][:, 1:], idx[iu][:, 1:]
    f = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    return G.reshape(-1, 3), f


def fan(ring):
    ring = np.asarray(ring, float)
    n = len(ring)
    i = np.arange(n)
    return np.vstack([ring, ring.mean(axis=0)]), np.column_stack([i, (i + 1) % n, np.full(n, n)])


def _unit(a):
    a = np.asarray(a, float)
    return a / np.linalg.norm(a, axis=-1, keepdims=True)


def sweep(points, wdir=None, axis=None, away=None, n=None):
    """Frames along a spline: position, tangent, width direction, face normal, parameter 0..1.

    ``wdir`` fixes the width direction; ``axis`` (x, y) makes the band face away from a vertical axis.
    ``away`` is a point the face normal should point away from.
    """
    p = np.asarray(points, float)
    s = pt.cum(p)
    n = n or max(10, int(s[-1] / 7))
    cs = CubicSpline(s, p)
    u = np.linspace(0, s[-1], n)
    P, T = cs(u), _unit(cs(u, 1))
    ref = None
    if axis is not None:
        ref = P - np.array([axis[0], axis[1], 0.0])
        ref[:, 2] = 0.0
        B = _unit(np.cross(T, ref))
    else:
        W = np.broadcast_to(np.asarray(wdir, float), P.shape)
        B = _unit(W - (W * T).sum(1)[:, None] * T)
        if away is not None:
            ref = P - np.asarray(away, float)
    N = np.cross(B, T)
    if ref is not None and N[n // 2] @ ref[n // 2] < 0:
        N = -N
    return P, T, B, N, u / s[-1]


def _val(x, u):
    return np.asarray(x(u), float) if callable(x) else np.full(len(u), float(x))


def band(fr, w, t, off=0.0, e=0.45, m_=18, i0=0, i1=None):
    """Soft band on sweep frames; w, t, off are numbers or functions of the local parameter 0..1."""
    P, _, B, N, u = (a[i0:i1] for a in fr)
    ul = (u - u[0]) / (u[-1] - u[0])
    w, t, off = _val(w, ul), _val(t, ul), _val(off, ul)
    th = np.linspace(0, 2 * math.pi, m_, endpoint=False)
    c = np.sign(np.cos(th)) * np.abs(np.cos(th)) ** e
    s = np.sign(np.sin(th)) * np.abs(np.sin(th)) ** e
    G = P[None] + B[None] * (w[None, :, None] / 2 * c[:, None, None]) + N[None] * (off[None, :, None] + t[None, :, None] / 2 * s[:, None, None])
    return merge(grid(G, close_u=True), fan(G[:, 0]), fan(G[:, -1]))


def tube(points, r, smooth=True, m_=10, n=None):
    p = np.asarray(points, float)
    if smooth and len(p) > 2:
        s = pt.cum(p)
        cs = CubicSpline(s, p)
        u = np.linspace(0, s[-1], n or max(8, int(s[-1] / 6)))
        P, T = cs(u), _unit(cs(u, 1))
    else:
        P = p
        T = _unit(np.gradient(p, axis=0))
    nrm = np.cross(T[0], [0.0, 0.0, 1.0])
    nrm = _unit(nrm if np.linalg.norm(nrm) > 1e-6 else np.cross(T[0], [1.0, 0.0, 0.0]))
    rings = []
    th = np.linspace(0, 2 * math.pi, m_, endpoint=False)
    for o, t in zip(P, T):
        nrm = _unit(nrm - (nrm @ t) * t)
        b = np.cross(t, nrm)
        rings.append(o + r * (np.cos(th)[:, None] * nrm + np.sin(th)[:, None] * b))
    G = np.stack(rings, 1)
    return merge(grid(G, close_u=True), fan(G[:, 0]), fan(G[:, -1]))


def plate(poly, origin, t, xdir=(1, 0, 0), ydir=(0, 0, 1)):
    """Flat outline (local x, y) extruded by t along xdir × ydir."""
    poly = np.asarray(poly, float)[:, :2]
    if np.allclose(poly[0], poly[-1]):
        poly = poly[:-1]
    x, y = _unit(xdir), _unit(ydir)
    a = np.asarray(origin, float) + poly[:, :1] * x + poly[:, 1:] * y
    b = a + np.cross(x, y) * t
    return merge(grid(np.stack([a, b], 1), close_u=True), fan(a), fan(b))


def cq_mesh(wp, tol=0.2):
    out = []
    for s in wp.vals():
        if isinstance(s, cq.Shape):
            vs, fs = s.tessellate(tol, 0.2)
            out.append((np.array([v.toTuple() for v in vs]), np.array(fs)))
    return merge(*out)


@lru_cache(maxsize=None)
def a0_mesh(name, tol=0.2):
    """Hard part from ``backpack_model.py``, tessellated once."""
    return cq_mesh(getattr(m, name)(), tol)


@lru_cache(maxsize=None)
def hw_mesh(kind, w, piece=None):
    """Buckle from the hardware library, tessellated once in its local frame."""
    part = getattr(hw, kind)(w)
    return cq_mesh(part[piece] if piece else part)


def placed(mesh, origin, xdir, zdir):
    """Put a local-frame mesh at origin with local X -> xdir and local Z -> zdir (same rule as ``hw.place``)."""
    z = _unit(zdir)
    x = np.asarray(xdir, float)
    x = _unit(x - (x @ z) * z)
    v, f = mesh
    return np.asarray(origin, float) + v @ np.array([x, np.cross(z, x), z]), f


def subframe(fr, s0, s1, k):
    """Frames between arc lengths s0 and s1 of an existing sweep, resampled to k stations."""
    arc = pt.cum(fr[0])
    u = np.linspace(s0, s1, k)
    out = [np.column_stack([np.interp(u, arc, a[:, i]) for i in range(3)]) for a in fr[:4]]
    return out[0], _unit(out[1]), _unit(out[2]), _unit(out[3]), (u - s0) / (s1 - s0)


# --------------------------------------------------------------------------- body surface

NS, N1, N2, NF = 8, 3, 7, 10
NRING = 2 * (3 * NS + N1 + N2 + NF)
SEAM_BR, SEAM_FR = NS + N1, 2 * NS + N1 + N2 + NF // 2
SEAM_FL, SEAM_BL = NRING - SEAM_FR, NRING - SEAM_BR


def shape(z):
    """Packed section with a flat back: same panel widths as the patterns, tighter back corners."""
    w, d, r = pt.section(z)
    rb = min(r, R_BACK)
    return w, d - pt.K_CORNER * (r - rb), rb, r


def shape_area(z):
    w, d, rb, rf = shape(z)
    return w * d - (1 - math.pi / 4) * 2 * (rb * rb + rf * rf)


def ring(z, grow=0.0):
    """Section outline at height z from the back centre towards +X: points and outward normals."""
    w, d, rb, rf = shape(z)
    ab, af = w / 2 - rb, w / 2 - rf
    phi = (pt.half_width(z) - ab) / rb  # where the back/side seam sits on the back corner
    h = [(ab * t, 0.0, 0.0, -1.0) for t in np.linspace(0, 1, NS, endpoint=False)]
    for a in np.concatenate([np.linspace(0, phi, N1, endpoint=False), np.linspace(phi, math.pi / 2, N2, endpoint=False)]):
        h.append((ab + rb * math.sin(a), rb * (1 - math.cos(a)), math.sin(a), -math.cos(a)))
    h += [(w / 2, rb + (d - rb - rf) * t, 1.0, 0.0) for t in np.linspace(0, 1, NS, endpoint=False)]
    for a in np.linspace(0, math.pi / 2, NF, endpoint=False):
        h.append((af + rf * math.cos(a), d - rf + rf * math.sin(a), math.cos(a), math.sin(a)))
    h += [(af * (1 - t), d, 0.0, 1.0) for t in np.linspace(0, 1, NS, endpoint=False)]
    h = np.array(h)
    full = np.vstack([h, [[0.0, d, 0.0, 1.0]], h[:0:-1] * [-1, 1, -1, 1]])
    nrm = np.column_stack([full[:, 2], full[:, 3], np.zeros(len(full))])
    pts = np.column_stack([full[:, 0], Y0 + full[:, 1], np.full(len(full), float(z))]) + grow * nrm
    return pts, nrm


def front_pt(s, z, grow=0.0):
    """Point on the front panel at surface distance s from the centre line."""
    w, d, _, rf = shape(z)
    af = w / 2 - rf
    a = max(abs(s) - af, 0.0) / rf
    sg = 1.0 if s >= 0 else -1.0
    n = np.array([sg * math.sin(a), math.cos(a), 0.0])
    p = np.array([sg * (min(abs(s), af) + rf * math.sin(a)), Y0 + d - rf * (1 - math.cos(a)), z])
    return p + grow * n, n


def back_pt(x, z, lift=0.0):
    return np.array([x, Y0 - lift, z])


# --------------------------------------------------------------------------- harness poses

SWAY_MAX = 35.0  # travel of the linkage web through the hub, each way, set by the stops
TORSO_STEP, TORSO_RUNGS = 25.0, 5
STRAP_N, LINK_N = 70, 50
STOP_ARC = (43.0, 69.0)  # where the stop sits on the web at rest, measured from the hub exit
STRAP_REST = np.array([(62, Y0 - 4, 570), (64, 40, 600), (72, -30, 619), (92, -110, 624), (110, -190, 562), (124, -222, 462), (138, -201, 357)], float)
_TORSO_K = np.array([1.0, 1.0, 1.0, 1.0, 0.7, 0.4, 0.4])  # how far each control point follows the yoke
_SWAY_K = np.array([0.0, 0.0, 0.25, 0.6, 1.0, 1.0, 1.0])  # how far each control point follows the shoulder
_SWAY_DIR = np.array([0.0, -0.5, 0.866])  # a shoulder that swings forward also rises
_LINK_MID = np.array([150.0, -52.0, 250.0])


def _strap_frames(s, torso, a, t):
    p = STRAP_REST + np.outer(_TORSO_K, [0.0, 0.0, torso]) + np.outer(_SWAY_K, a * _SWAY_DIR)
    p[6] = p[5] + (p[6] - p[5]) * t
    return sweep(p * [s, 1, 1], wdir=(1, 0, 0), away=(0, -100, 450), n=STRAP_N)


def _link_points(s, fr, end0):
    end = fr[0][-1] + fr[1][-1] * 14.0
    ym = m.P.hub_y0 + m.P.hub_depth / 2
    mid = (_LINK_MID + 0.5 * (end * [s, 1, 1] - end0)) * [s, 1, 1]
    return [(s * 74, ym, m.P.hub_z0 + 40), (s * 112, 20, 150), tuple(mid), tuple(end)]


@lru_cache(maxsize=None)
def _rest():
    fr = _strap_frames(1, 0.0, 0.0, 1.0)
    end0 = fr[0][-1] + fr[1][-1] * 14.0
    chest = int(np.argmin(np.abs(fr[0][35:, 2] - 500.0))) + 35
    return pt.length(fr[0]), end0, chest


@lru_cache(maxsize=None)
def harness_frames(s, sway=0.0, torso=0.0):
    """Strap and linkage-web frames for one side.

    The strap keeps its pattern length. ``torso`` moves the yoke (and the shoulder with it); the lower
    adjuster takes up the difference. ``sway`` is the length of web that has run through the hub towards
    the right-hand strap: that side gets longer by ``sway`` and the other side shorter by the same amount.
    """
    from scipy.optimize import brentq

    strap_len, end0, _ = _rest()

    def strap(a):
        t = brentq(lambda t: pt.length(_strap_frames(s, torso, a, t)[0]) - strap_len, 0.2, 3.0, xtol=1e-4)
        return _strap_frames(s, torso, a, t)

    def link(fr):
        return sweep(_link_points(s, fr, end0), axis=(0.0, -100.0), n=LINK_N)

    fr = strap(0.0)
    if sway:
        target = pt.length(link(fr)[0]) + s * sway
        a = brentq(lambda a: pt.length(link(strap(a))[0]) - target, -90.0, 90.0, xtol=1e-3)
        fr = strap(a)
    return fr, link(fr)


# --------------------------------------------------------------------------- model


def build(sway=0.0, torso=0.0):
    """All parts. ``sway`` (mm, ± SWAY_MAX) and ``torso`` (mm, ± 2 rungs) pose the harness; see ``harness_frames``."""
    P, _, info = pt.build()
    parts: list[Part] = []
    meas: dict[str, float] = {}
    tags: dict[str, np.ndarray] = {}

    def add(key, name, group, color, *meshes):
        v, f = merge(*meshes)
        parts.append(Part(key, name, group, color, v, f))

    # ---- body, base, seams ---------------------------------------------
    zs = np.arange(0.0, pt.Z_TOP + 0.1, 10.0)
    rings = [ring(z)[0] for z in zs]
    add("body", "包体（A01 后幅、A02 前幅、A03 侧幅）", "bag", BODY, grid(np.stack(rings, 1), close_u=True))
    c0 = rings[0].mean(axis=0)
    base = [c0 + (rings[0] - c0) * k + [0, 0, dz] for k, dz in ((1.0, 0.0), (0.9, -5.0), (0.6, -8.0), (0.2, -9.0))]
    add("base", "包底（A04，420D）", "bag", BASE, grid(np.stack(base, 1), close_u=True), fan(base[-1]))
    seam_lines = [tube([ring(z, 0.4)[0][i] for z in zs[::2]], 1.1) for i in (SEAM_BR, SEAM_FR, SEAM_FL, SEAM_BL)]
    seam_lines.append(tube(np.vstack([ring(0.0, 0.4)[0], ring(0.0, 0.4)[0][:1]]), 1.3, smooth=False))
    add("seams", "包体缝（四条竖缝 + 包底缝）", "bag", SEAM, *seam_lines)

    # ---- roll-top --------------------------------------------------------
    w_top, d_top = shape(pt.Z_TOP)[:2]
    yc = Y0 + d_top / 2
    half_roll = [(0, 690), (70, 688), (125, 673), (158, 646), (171, 620)]
    roll_pts = [(-x, yc, z) for x, z in half_roll[:0:-1]] + [(x, yc, z) for x, z in half_roll]
    fr = sweep(roll_pts, wdir=(0, 1, 0), n=60)
    meas["roll"] = pt.length(roll_pts)
    add("roll", "卷口（卷起后的状态）", "bag", BODY, band(fr, 46, 30, e=0.6, m_=20))

    def roll_z(x):
        return np.interp(x, fr[0][:, 0], fr[0][:, 2])

    top = rings[-1]
    tx = top[:, 0] / (w_top / 2) * 150.0
    target = np.column_stack([tx, yc + (top[:, 1] - yc) * 0.2, roll_z(tx) - 11.0])
    collar = []
    for t in np.linspace(0, 1, 9):
        e = t * t * (3 - 2 * t)
        k = np.array([e, t**0.8, t])
        collar.append(top + (target - top) * k)
    add("collar", "卷口筒（卷口线以上）", "bag", BODY, grid(np.stack(collar, 1), close_u=True))
    clips, straps = [], []
    for s in (1, -1):
        x600 = shape(600.0)[0] / 2
        strap = [(s * (shape(540.0)[0] / 2 + 1.5), yc, 540.0), (s * (x600 + 1.5), yc, 590.0), (s * 160.0, yc, 609.0)]
        straps.append(band(sweep(strap, wdir=(0, 1, 0)), 20, 1.6))
        zdir = (s * 0.72, 0.0, 0.69)
        for k in ("female", "male"):
            clips.append(placed(hw_mesh("side_release_buckle", 20, k), (s * 165.0, yc, 613.0), (0, 1, 0), zdir))
    add("roll_straps", "卷口侧扣带（W07）", "bag", WEB, *straps)
    add("roll_buckles", "卷口插扣（H01）", "bag", HARD, *clips)
    tags["卷口：卷起后两端扣在侧幅"] = np.array([60.0, yc + 20, 696.0])

    # ---- front stretch pocket and V cords ------------------------------
    place = np.array(P["A02"].marks[1][1][-37:])  # (half width on the panel, arc length) at z = 70 … 430
    zp = np.arange(70.0, 430.1, 10.0)
    us = np.linspace(-1, 1, 33)

    def pocket_pt(u, k, extra=0.0):
        tau = (zp[k] - 70.0) / 360.0
        bulge = 1.5 + 20.0 * (1 - u * u) ** 0.8 * (0.25 + 0.75 * math.sin(math.pi * tau**0.8) ** 0.7)
        return front_pt(u * place[k, 0], zp[k], bulge + extra)[0]

    G = np.array([[pocket_pt(u, k) for k in range(len(zp))] for u in us])
    add("front_pocket", "前弹力袋（B01）", "bag", STRETCH, grid(G))
    add("front_pocket_hem", "前袋口弹力包边", "bag", WEB, tube(G[:, -1] + [0, 0.8, 0], 2.2))
    hook = pocket_pt(0.0, 23, 5.0)
    cords, anchors = [], []
    for s in (1, -1):
        a = front_pt(s * 96.0, 530.0, 2.5)[0]
        mid = front_pt(s * 52.0, 440.0, 9.0)[0]
        cords.append(tube([a, mid, hook], 1.8))
        anchors.append(plate(pt.rrect(16, 12, 3), a - [8 * 0, 1.5, 0], 3.0, xdir=(1, 0, 0), ydir=(0, 0, 1)))
        meas.setdefault("v_cord", pt.length([a, mid, hook]))
    add("v_cords", "V 形压缩绳（W13）", "bag", ORANGE, *cords)
    add("v_hook", "压缩绳挂扣和锚点", "bag", HARD, tube([hook - [0, 3, 0], hook + [0, 3, 0]], 9.0, smooth=False, m_=24), *anchors)
    tags["前弹力袋"] = pocket_pt(0.55, 12, 2.0)
    tags["V 形压缩绳"] = front_pt(60.0, 455.0, 12.0)[0]

    # ---- side pockets and compression straps ----------------------------
    zq = np.arange(40.0, 290.1, 10.0)
    pockets, hems, comps, locks = [], [], [], []
    for lo, hi in ((SEAM_BR, SEAM_FR), (SEAM_FL, SEAM_BL)):
        cols = []
        for z in zq:
            pts_, nrm = ring(z)
            v = np.linspace(0, 1, hi - lo + 1)
            g = np.interp(z, [40, 120, 230, 290], [0.45, 1.0, 0.9, 0.45])
            cols.append(pts_[lo : hi + 1] + nrm[lo : hi + 1] * (1.5 + 22.0 * np.sin(math.pi * v) ** 0.7 * g)[:, None])
        G = np.stack(cols, 1)
        pockets.append(grid(G))
        hems.append(tube(G[:, -1], 2.6))
        for z in (330.0, 480.0):
            pts_ = ring(z, 1.2)[0][lo - 1 : hi + 2]
            f2 = sweep(pts_, wdir=(0, 0, 1))
            comps.append(band(f2, 15, 1.4))
            meas.setdefault("side_comp", pt.length(pts_))
            k = int(len(f2[0]) * (0.8 if lo == SEAM_BR else 0.2))
            locks.append(placed(hw_mesh("ladder_lock", 15), f2[0][k] + f2[3][k] * 2.5 * np.sign(f2[3][k] @ (f2[0][k] - [0, yc, z])), (0, 0, 1), f2[1][k]))
    add("side_pockets", "侧袋（B02）", "bag", STRETCH, *pockets)
    add("side_pocket_hems", "侧袋口松紧带", "bag", WEB, *hems)
    add("side_comp", "侧压缩带（W08，每侧两条）", "bag", WEB, *comps)
    add("side_comp_locks", "侧压缩带梯扣（H04）", "bag", HARD, *locks)
    tags["侧袋"] = ring(170.0, 24.0)[0][(SEAM_BR + SEAM_FR) // 2]
    tags["侧压缩带"] = ring(480.0, 3.0)[0][(SEAM_BR + SEAM_FR) // 2]

    # ---- back panel: hub patch, torso ladder, anchors, yoke --------------
    add("hub_patch", "联动座加强片（E01，420D）", "back", BASE, plate(pt.rrect(190, 80, 8), back_pt(0, pt.HUB_Z), 1.2))
    ladder = [plate(pt.rrect(26, 170, 1), back_pt(0, 515.0), 2.0)]
    ladder += [plate(pt.rrect(30, 5, 1), back_pt(0, 450.0 + 25.0 * k), 3.0) for k in range(5)]
    add("ladder", "背长调节梯带（W11，5 档）", "back", WEB, *ladder)
    patches = [plate(pt.rrect(60, 45, 5), back_pt(s * x, z), 1.0) for s in (1, -1) for x, z in ((105.0, 585.0), (118.0, 180.0), (112.0, 255.0))]
    patches += [plate(pt.rrect(44, 72, 6), back_pt(s * 106.0, 560.0), 14.0) for s in (1, -1)]
    add("patches", "锚点加强片（E02）和背架上角袋（E03）", "back", TPU, *patches)
    yoke = np.array(P["C08"].sew())
    yoke_z = 500.0 - 30.0 + torso  # G-hook on the middle rung when torso = 0
    add("yoke", "肩轭（C08，挂在梯带中间一档）", "back", YOKE, plate(yoke, back_pt(0, yoke_z, 2.0), 3.5))
    add("g_hook", "G 钩（H07）", "back", ALU, plate(pt.rrect(30, 14, 3), back_pt(0, 500.0 + torso, 5.5), 2.0))
    add("handle", "提手（W12）", "back", WEB, tube([(-35, Y0 - 1, 634), (-24, Y0 - 16, 664), (0, Y0 - 20, 672), (24, Y0 - 16, 664), (35, Y0 - 1, 634)], 4.0))
    tags["背长调节：肩轭 + 梯带 + G 钩，5 档"] = back_pt(0, 562.0, 6.0)

    # ---- Y frame ----------------------------------------------------------
    def bar_y(x):
        return 38.0 + 4.0 * (1 - (np.asarray(x, float) / 112.0) ** 2)

    top_bar = [(x, float(bar_y(x)), 560.0 + 6.0 * (1 - (x / 112.0) ** 2)) for x in (-112, -56, 0, 56, 112)]
    frame = [tube(top_bar, 3.0)]
    for s in (1, -1):
        frame.append(tube([(s * 112, 38, 560), (s * 98, 35, 470), (s * 66, 30, 340), (s * 22, 30, 230), (0, 34, 190)], 3.0))
    frame.append(tube([(0, 34, 190), (0, 33, 150), (0, 34, m.P.hub_z0 + 44)], 3.5))
    frame.append(tube([(0, 27, 190), (0, 41, 190)], 9.0, smooth=False, m_=20))
    add("y_frame", "Y 型背架（H14）", "back", ALU, *frame)
    tags["Y 型背架"] = np.array([40.0, 27.0, 262.0])

    # ---- suspended mesh, lumbar pads, tension straps ---------------------
    edge = np.array(sorted(P["C03"].edge("right").pts, key=lambda q: q[1]))
    zm = np.linspace(272.0, 562.0, 30)
    hm = np.interp(zm - 272.0, edge[:, 1], edge[:, 0])
    um = np.linspace(-1, 1, 25)
    k = np.clip((zm - 500.0) / 62.0, 0, 1)
    k = k * k * (3 - 2 * k)
    G = np.array([[(u * h, 9.0 + (float(bar_y(u * h)) - 9.0) * kk, z) for h, kk, z in zip(hm, k, zm)] for u in um])
    add("mesh", "上区悬浮网（C03）", "mesh", SPACER, grid(G), tube([(q[0], q[1], q[2] + 1.0) for q in top_bar], 5.0))
    add("mesh_binding", "悬浮网包边", "mesh", WEB, tube(G[0], 1.8), tube(G[-1], 1.8), tube(G[:, 0], 1.8))
    tags["上区悬浮网（与后幅之间留通风间隙）"] = np.array([40.0, 8.0, 420.0])
    upper, cams = [], []
    for s in (1, -1):
        a = np.array([s * (hm[0] - 12.0), 9.5, 284.0])
        b = back_pt(s * 112.0, 255.0, 4.0)
        upper.append(band(sweep([a, (a + b) / 2 + [s * 3, -3, 0], b], wdir=(1, 0, 0)), 20, 1.5))
        cams.append(plate(pt.rrect(28, 20, 3), back_pt(s * 112.0, 255.0, 1.0), 7.0))
        meas.setdefault("upper_tension", float(np.linalg.norm(b - a)))
    add("lumbar", "下区腰垫（C04–C07，左右分体）", "back", SPACER, a0_mesh("lumbar_pad"))
    lower = []
    for s in (1, -1):
        a, b = np.array([s * 96.0, 13.0, 182.0]), back_pt(s * 118.0, 180.0, 2.0)
        lower.append(band(sweep([a, (a + b) / 2 + [s * 6, 0, 0], b], wdir=(0, 0, 1)), 20, 1.5))
        cams.append(placed(hw_mesh("ladder_lock", 20), (a + b) / 2 + [s * 8, 0, 0], (0, 0, 1), b - a))
        meas.setdefault("lower_tension", float(np.linalg.norm(b - a)))
    add("tension", "上区、下区张紧带（W09、W10）", "back", ORANGE, *upper, *lower)
    add("tension_hw", "凸轮扣、梯扣（H05、H03）", "back", HARD, *cams)
    tags["下区腰垫"] = np.array([50.0, 0.0, 200.0])
    tags["上区张紧带（凸轮扣）"] = back_pt(-112.0, 255.0, 8.0)
    tags["联动座加强片（内侧有内衬板）"] = back_pt(-82.0, pt.HUB_Z - 30.0, 1.5)

    # ---- linkage hub, rollers, lock, pivot --------------------------------
    add("hub", "联动座（H13）", "back", (0.38, 0.39, 0.42), a0_mesh("hub_housing", 0.1))
    add("rollers", "滚轮", "back", ROLLER, a0_mesh("rollers", 0.1))
    add("cam_lever", "锁止扳手", "back", ORANGE, a0_mesh("cam_lever", 0.1))
    add("pivot", "腰带枢转盘", "pivot", HARD, a0_mesh("pivot_plate", 0.1))
    tags["联动座：滚轮 + 锁止扳手"] = np.array([40.0, m.P.hub_y0, m.P.hub_z0 + 22.0])

    # ---- shoulder straps ---------------------------------------------------
    strap_w = lambda u: np.interp(u, [0, 0.25, 0.6, 1.0], [60, 70, 66, 50])  # noqa: E731
    inner, outer, link, hwp, lifters, stops, chest = [], [], [], [], [], [], {}
    jc = _rest()[2]
    for s in (1, -1):
        fr, fw = harness_frames(s, float(sway), float(torso))
        meas.setdefault("strap", pt.length(fr[0]))
        inner.append(band(fr, strap_w, 7.0, off=-3.0))
        outer.append(band(fr, lambda u: strap_w(u) - 3, 5.0, off=3.0))
        tip, tdir = fr[0][-1], fr[1][-1]
        hwp.append(placed(hw_mesh("ladder_lock", 20), tip + tdir * 8.0, fr[2][-1], tdir))
        meas.setdefault("link_half", pt.length(fw[0]))
        link.append(band(fw, 20, 1.6))
        stops.append(band(subframe(fw, STOP_ARC[0] + s * sway, STOP_ARC[1] + s * sway, 4), 26, 9, e=0.6))
        top = fr[0][16] + fr[3][16] * 6.0
        anchor = back_pt(s * 105.0, 585.0, 1.5)
        fl = sweep([top, (top + anchor) / 2 + [0, 0, 10], anchor], wdir=(1, 0, 0), n=16)
        meas.setdefault("lifter", pt.length(fl[0]))
        lifters.append(band(fl, 15, 1.5))
        hwp.append(placed(hw_mesh("ladder_lock", 15), fl[0][4] + fl[3][4] * 2.0, fl[2][4], -fl[1][4]))
        chest[s] = fr[0][jc] + fr[3][jc] * 7.0
        if s == 1:
            j = int(np.argmax(fr[0][:, 2])) + 3
            tags["肩带（S 形，泡棉 + 间隔网布）"] = fr[0][j] + fr[3][j] * 5.5
            tags["肩带内层（间隔网布）"] = fr[0][52] - fr[3][52] * 6.5
    add("strap_inner", "肩带内层（D02，间隔网布）", "harness", SPACER, *inner)
    add("strap_outer", "肩带外层（D01）", "harness", BODY, *outer)
    add("load_lifters", "上拉带（W03）", "harness", WEB, *lifters)
    add("linkage_web", "联动带 + 肩带下调节带（W01、W02）", "linkage", ORANGE, *link)
    add("stops", "限位块", "linkage", HARD, *stops)
    cl, cr = chest[-1], chest[1]
    cm = (cl + cr) / 2
    fs = sweep([cl + [22, -2, 0], cm + [0, -10, 0], cr + [-22, -2, 0]], wdir=(0, 0, 1), n=25)
    add("sternum", "胸带（W04）", "harness", WEB, band(fs, 15, 1.4))
    hwp += [placed(hw_mesh("side_release_buckle", 15, k), cm + [0, -13, 0], (0, 0, 1), cr - cl) for k in ("female", "male")]
    add("strap_hw", "肩带梯扣、上拉带梯扣、胸带扣", "harness", HARD, *hwp)
    tags["联动带：左右肩带下端经联动座相连"] = np.array([150.0, -60.0, 252.0])
    tags["上拉带"] = np.array([92.0, 10.0, 612.0])

    # ---- hip belt ----------------------------------------------------------
    zb = m.P.hub_z0 + 22.0
    add("belt_centre", "腰带中段（D08，内夹腰带背板 D09）", "harness", BODY, plate(pt.rrect(210, 84, 22), (0, 15.0, zb), 10.0))
    wing_h = lambda u: np.interp(u * 243.0, [0, 70, 140, 185, 225, 243], [110, 106, 98, 86, 70, 44])  # noqa: E731
    wi, wo, pk, zipl, bw = [], [], [], [], []
    for s in (1, -1):
        path = [(s * 90, 10, zb), (s * 138, -8, zb + 4), (s * 163, -58, zb + 9), (s * 168, -116, zb + 14), (s * 158, -170, zb + 18), (s * 150, -190, zb + 20)]
        fr = sweep(path, axis=WAIST, n=60)
        meas.setdefault("wing", pt.length(fr[0]))
        wi.append(band(fr, wing_h, 8.0, off=-3.0))
        wo.append(band(fr, lambda u: wing_h(u) - 4, 6.0, off=4.0))
        i0, i1 = 9, 48
        pk.append(band(fr, lambda u: 84 * (1 - 0.3 * np.abs(2 * u - 1) ** 3), lambda u: 4 + 30 * (1 - np.abs(2 * u - 1) ** 2.5) ** 0.5, off=lambda u: 7 + (4 + 30 * (1 - np.abs(2 * u - 1) ** 2.5) ** 0.5) / 2, e=0.55, i0=i0, i1=i1))
        ul = np.linspace(0, 1, i1 - i0)
        zo = 7 + 0.93 * (4 + 30 * (1 - np.abs(2 * ul - 1) ** 2.5) ** 0.5)
        zipl.append(tube((fr[0][i0:i1] + fr[3][i0:i1] * zo[:, None] + fr[2][i0:i1] * 22.0 * np.sign(fr[2][i0, 2]))[3:-3], 1.5))
        if s == 1:
            tags["预成型腰带翼 + 腰带袋"] = fr[0][28] + fr[3][28] * 41.0
        front = [tuple(fr[0][-1]), (s * 128, -216, zb + 21), (s * 80, -231, zb + 21), (s * 20, -233, zb + 21)]
        meas.setdefault("belt_web", pt.length(front))
        bw.append(band(sweep(front, axis=WAIST), 25, 1.6))
    add("wing_inner", "腰带翼内层（D05，间隔网布）", "harness", SPACER, *wi)
    add("wing_outer", "腰带翼外层（D04）", "harness", BODY, *wo)
    add("belt_pockets", "腰带袋（B03–B05）", "harness", BODY, *pk)
    add("belt_zips", "腰带袋拉链（H09）", "harness", HARD, *zipl)
    add("belt_web", "腰带收紧带（W05）", "harness", WEB, *bw)
    add("belt_buckle", "腰带中扣（H02）", "harness", HARD, *[placed(hw_mesh("side_release_buckle", 25, k), (0, -236, zb + 21), (0, 0, 1), (1, 0, 0)) for k in ("female", "male")])
    tags["腰带中段：经枢转盘接联动座"] = np.array([-45.0, 4.5, zb + 30.0])

    meas["volume_flat_back"] = float(np.trapezoid([shape_area(z) for z in np.linspace(0, pt.Z_TOP, 641)], np.linspace(0, pt.Z_TOP, 641))) / 1e6
    meas["volume_ideal"] = info["main_volume_l"]
    return parts, meas, tags, P, info


# --------------------------------------------------------------------------- rendering


def _polydata(part):
    import vtk
    from vtk.util import numpy_support as ns

    pd = vtk.vtkPolyData()
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.ascontiguousarray(part.v, dtype=np.float64), deep=True))
    pd.SetPoints(pts)
    cells = vtk.vtkCellArray()
    cells.SetData(3, ns.numpy_to_vtkIdTypeArray(np.ascontiguousarray(part.f, dtype=np.int64).ravel(), deep=True))
    pd.SetPolys(cells)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd)
    nf = vtk.vtkPolyDataNormals()
    nf.SetInputConnection(clean.GetOutputPort())
    nf.SetFeatureAngle(50)
    nf.SplittingOn()
    nf.ConsistencyOn()
    nf.Update()
    return nf.GetOutput()


class Scene:
    def __init__(self, parts):
        import vtk

        self.vtk = vtk
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.ren.AutomaticLightCreationOff()
        self.ren.TwoSidedLightingOn()
        kit = vtk.vtkLightKit()
        kit.SetKeyLightIntensity(0.95)
        kit.SetKeyToFillRatio(2.2)
        kit.SetKeyToHeadRatio(3.5)
        kit.SetKeyToBackRatio(3.0)
        kit.AddLightsToRenderer(self.ren)
        self.actors = {}
        for p in parts:
            mp = vtk.vtkPolyDataMapper()
            mp.SetInputData(_polydata(p))
            act = vtk.vtkActor()
            act.SetMapper(mp)
            pr = act.GetProperty()
            pr.SetColor(*p.color)
            pr.SetAmbient(0.22)
            pr.SetDiffuse(0.80)
            pr.SetSpecular(0.25 if p.color in (ALU, ROLLER) else 0.06)
            pr.SetSpecularPower(25)
            pr.SetInterpolationToPhong()
            self.ren.AddActor(act)
            self.actors[p.key] = (act, p.group)
        self.rw = vtk.vtkRenderWindow()
        self.rw.SetOffScreenRendering(1)
        self.rw.SetMultiSamples(0)
        self.rw.AddRenderer(self.ren)
        basic = vtk.vtkRenderStepsPass()
        ssao = vtk.vtkSSAOPass()
        ssao.SetRadius(45.0)
        ssao.SetBias(1.5)
        ssao.SetKernelSize(128)
        ssao.BlurOn()
        ssao.SetDelegatePass(basic)
        self.ren.SetPass(ssao)

    def shot(self, path, direction, size=(1500, 1500), hide=(), zoom=1.0, ss=2, tags=None):
        """Render to ``path``; returns the pixel positions of ``tags`` (top-left origin, final image size)."""
        from PIL import Image

        vtk = self.vtk
        for act, group in self.actors.values():
            act.SetVisibility(group not in hide)
        n = _unit(direction)
        cam = self.ren.GetActiveCamera()
        cam.SetViewAngle(18)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetPosition(*(n * 3000))
        cam.SetViewUp(0, 0, 1)
        self.rw.SetSize(size[0] * ss, size[1] * ss)
        self.ren.ResetCamera()
        cam.Zoom(zoom)
        self.ren.ResetCameraClippingRange()
        self.rw.Render()
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(self.rw)
        w2i.ReadFrontBufferOff()
        w2i.Update()
        from vtk.util import numpy_support as ns

        img = w2i.GetOutput()
        arr = ns.vtk_to_numpy(img.GetPointData().GetScalars()).reshape(size[1] * ss, size[0] * ss, -1)[::-1, :, :3]
        im = Image.fromarray(np.ascontiguousarray(arr)).resize(size, Image.LANCZOS)
        if path is not None:
            im.save(path)
        out = {}
        for label, p in (tags or {}).items():
            c = vtk.vtkCoordinate()
            c.SetCoordinateSystemToWorld()
            c.SetValue(*p)
            x, y = c.GetComputedDoubleDisplayValue(self.ren)
            out[label] = (x / ss, size[1] - y / ss)
            pick = vtk.vtkWorldPointPicker()
            pick.Pick(x, y, 0, self.ren)
            if np.linalg.norm(np.array(pick.GetPickPosition()) - p) > 20.0:
                print(f"  callout hidden in this view: {label}")
        return im, out


def callouts(im, pix, path, title):
    """Image with leader lines to labels in the left and right margins."""
    import matplotlib.patheffects as pe
    import matplotlib.pyplot as plt

    import drawing  # noqa: F401  (sets the CJK font)

    w, h = im.size
    pad = 0.34 * w
    fig = plt.figure(figsize=((w + 2 * pad) / 200, h / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(im, extent=(0, w, h, 0))
    ax.set_xlim(-pad, w + pad)
    ax.set_ylim(h, 0)
    ax.axis("off")
    split = float(np.median([x for x, _ in pix.values()]))
    halo = [pe.Stroke(linewidth=2.2, foreground="white"), pe.Normal()]
    for side in (-1, 1):
        items = sorted(((y, x, lab) for lab, (x, y) in pix.items() if (x > split) == (side > 0)), key=lambda q: q[0])
        if not items:
            continue
        ys = np.linspace(0.14 * h, 0.90 * h, len(items)) if len(items) > 1 else [items[0][0]]
        for (y, x, lab), yl in zip(items, ys):
            xl = w + 0.02 * w if side > 0 else -0.02 * w
            ax.plot([x, xl], [y, yl], color="0.15", lw=0.7, path_effects=halo)
            ax.plot([x], [y], "o", color=ORANGE, ms=3.5, mec="white", mew=0.5)
            ax.text(xl + side * 6, yl, lab, fontsize=8.5, ha="left" if side > 0 else "right", va="center")
    ax.text(w / 2, 0.035 * h, title, fontsize=12, ha="center", va="center")
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def export_glb(parts, path):
    import trimesh

    scene = trimesh.Scene()
    to_gltf = np.array([[0.001, 0, 0, 0], [0, 0, 0.001, 0], [0, -0.001, 0, 0], [0, 0, 0, 1]])  # mm, Z up -> m, Y up
    for p in parts:
        mesh = trimesh.Trimesh(p.v, p.f, process=False)
        mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(name=p.key, baseColorFactor=[*p.color, 1.0], roughnessFactor=0.85, metallicFactor=0.0, doubleSided=True))
        mesh.apply_transform(to_gltf)
        scene.add_geometry(mesh, node_name=p.key, geom_name=p.key)
    scene.export(str(path))


def consistency(meas, P, info, path):
    web = {c: (ln, q) for c, _, _, ln, q, _ in pt.webbing(P, info)}
    wing = P["D04"].size()[0] - 15
    strap = (P["D01"].edge("outline").length() - math.pi * 25) / 2 + 25
    rows = [
        ("主仓容积：四角等圆的理想截面（裁片的设计依据）", f"{meas['volume_ideal']:.1f} L", "—", ""),
        ("主仓容积：背板把后幅撑平后的截面（本模型，裁片宽度不变）", f"{meas['volume_flat_back']:.1f} L", "—", "两个数都是几何估算，实际容积以样包灌装实测为准"),
        ("肩带：3D 路径长（肩轭缝线到下端）", f"{meas['strap']:.0f}", f"{strap:.0f}", "裁片沿中线量"),
        ("腰带翼：3D 路径长（含插入中段 15）", f"{meas['wing']:.0f}", f"{wing + 15:.0f}", ""),
        ("卷口展平宽度：3D 卷口中线长", f"{meas['roll']:.0f}", f"{info['roll_flat_width']:.0f}", ""),
    ]
    need = [
        ("W01 + W02 联动带和下调节带（半边：联动座出口到肩带下端）", meas["link_half"], web["W01"][0] / 2 - 80 + web["W02"][0], "W01 的一半扣掉座内约 80，再加一根 W02"),
        ("W03 上拉带", meas["lifter"], web["W03"][0], ""),
        ("W05 腰带收紧带（腰带翼尖到中扣，前拉式要回折一次）", 2 * meas["belt_web"], web["W05"][0], "路径长按两倍算"),
        ("W08 侧压缩带", meas["side_comp"], web["W08"][0], ""),
        ("W09 上区张紧带", meas["upper_tension"], web["W09"][0], ""),
        ("W10 下区张紧带", meas["lower_tension"], web["W10"][0], ""),
        ("W13 V 形压缩绳（单根）", meas["v_cord"], web["W13"][0], "弹力绳，装配时略拉伸"),
    ]
    for name, used, cut, note in need:
        spare = cut - used
        flag = "够" if spare >= 60 else "**不够，需加长**"
        rows.append((name, f"{used:.0f}", f"{cut:.0f}", f"余量 {spare:.0f}，{flag}。{note}"))
    lines = ["| 项目 | 3D 模型里的长度 (mm) | 裁片或下料长度 (mm) | 说明 |", "|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


VIEWS = {
    "iso_front": ((0.95, 1.45, 0.50), 1.0),
    "iso_rear": ((1.0, -1.30, 0.45), 1.0),
    "front": ((0.0, 1.0, 0.04), 1.0),
    "rear": ((0.0, -1.0, 0.04), 1.0),
    "side": ((1.0, 0.0, 0.04), 1.0),
}
FRONT_TAGS = ("卷口：卷起后两端扣在侧幅", "前弹力袋", "V 形压缩绳", "侧袋", "侧压缩带", "预成型腰带翼 + 腰带袋", "肩带内层（间隔网布）")
REAR_TAGS = ("肩带（S 形，泡棉 + 间隔网布）", "上拉带", "上区悬浮网（与后幅之间留通风间隙）", "下区腰垫", "联动带：左右肩带下端经联动座相连", "预成型腰带翼 + 腰带袋", "腰带中段：经枢转盘接联动座")
SYSTEM_TAGS = ("背长调节：肩轭 + 梯带 + G 钩，5 档", "Y 型背架", "上区张紧带（凸轮扣）", "下区腰垫", "联动座：滚轮 + 锁止扳手", "联动带：左右肩带下端经联动座相连", "联动座加强片（内侧有内衬板）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    parts, meas, tags, P, info = build()
    print(f"{len(parts)} parts, {sum(len(p.f) for p in parts)} triangles")
    rows = consistency(meas, P, info, OUT / "consistency.md")
    for r in rows:
        print("  ", " | ".join(r))
    sc = Scene(parts)
    size = (900, 900) if args.fast else (1400, 1400)
    ims = {}
    for name, (direction, zoom) in VIEWS.items():
        ims[name], _ = sc.shot(OUT / f"a1_{name}.png", direction, size=size, zoom=zoom)
    if args.fast:
        return
    from PIL import Image

    from PIL import ImageChops

    crops = []
    for name in ("front", "side", "rear"):
        box = ImageChops.difference(ims[name], Image.new("RGB", size, "white")).getbbox()
        crops.append(ims[name].crop((box[0] - 40, 0, box[2] + 40, size[1])))
    sheet = Image.new("RGB", (sum(c.width for c in crops), size[1]), "white")
    x = 0
    for c in crops:
        sheet.paste(c, (x, 0))
        x += c.width
    sheet.save(OUT / "a1_three_views.png")

    im, pix = sc.shot(None, VIEWS["iso_front"][0], size=size, tags={k: tags[k] for k in FRONT_TAGS})
    callouts(im, pix, OUT / "a1_callouts_front.png", "BP40-A1 预览：正面")
    im, pix = sc.shot(None, VIEWS["iso_rear"][0], size=size, tags={k: tags[k] for k in REAR_TAGS})
    callouts(im, pix, OUT / "a1_callouts_rear.png", "BP40-A1 预览：背负面")
    hide = ("harness", "mesh", "pivot")
    im, pix = sc.shot(OUT / "a1_back_system.png", (0.62, -1.5, 0.35), size=size, hide=hide, tags={k: tags[k] for k in SYSTEM_TAGS})
    callouts(im, pix, OUT / "a1_callouts_back_system.png", "BP40-A1 预览：背负系统（隐藏肩带、腰带翼和悬浮网）")

    frames = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        frames.append(sc.shot(None, (math.sin(a), math.cos(a), 0.38), size=(560, 560))[0].quantize(96, method=Image.MEDIANCUT, dither=Image.NONE))
    frames[0].save(OUT / "a1_turntable.gif", save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
    export_glb(parts, OUT / "BP40-A1_preview.glb")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
