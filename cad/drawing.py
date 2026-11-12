"""Hidden-line projection, patent-style line views and shaded previews."""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.collections import LineCollection, PolyCollection
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

import cadquery as cq

for _f in ("Noto Sans CJK SC", "WenQuanYi Micro Hei", "Droid Sans Fallback"):
    if any(_f in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_f, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False


def view_frame(direction):
    """Return (N, X, Y) unit vectors for a view looking *from* ``direction``."""
    n = np.asarray(direction, float)
    n /= np.linalg.norm(n)
    z = np.array([0.0, 0.0, 1.0])
    if abs(n @ z) > 0.999:
        x = np.array([-1.0, 0.0, 0.0])
    else:
        x = np.cross(z, n)
        x /= np.linalg.norm(x)
    y = np.cross(n, x)
    return n, x, y


# Views of the product. Front = outer face of the pack (away from the wearer).
VIEWS = {
    "front": ((0, 1, 0), "主视图"),
    "rear": ((0, -1, 0), "后视图"),
    "left": ((1, 0, 0), "左视图"),
    "right": ((-1, 0, 0), "右视图"),
    "top": ((0, 0, 1), "俯视图"),
    "bottom": ((0, 0, -1), "仰视图"),
    "iso_front": ((1.0, 1.25, 0.75), "立体图"),
    "iso_rear": ((1.0, -1.25, 0.75), "立体图(背面)"),
}


def _edges_to_polylines(shape, deflection=0.15):
    lines = []
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    while exp.More():
        e = TopoDS.Edge_s(exp.Current())
        try:
            c = BRepAdaptor_Curve(e)
            d = GCPnts_QuasiUniformDeflection(c, deflection)
            if d.IsDone() and d.NbPoints() > 1:
                pts = [d.Value(i) for i in range(1, d.NbPoints() + 1)]
                lines.append(np.array([[p.X(), p.Y()] for p in pts]))
        except Exception:
            pass
        exp.Next()
    return lines


def hlr_lines(shape: cq.Shape, direction, hidden=False, deflection=0.15):
    """Project ``shape`` with hidden-line removal.

    Returns (visible, hidden) lists of Nx2 arrays in view coordinates where
    +x is the view's right and +y is up (see :func:`view_frame`).
    """
    n, x, _ = view_frame(direction)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*x))
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)

    def collect(getters):
        out = []
        for g in getters:
            s = g()
            if s.IsNull():
                continue
            BRepLib.BuildCurves3d_s(s, 1e-6)
            out += _edges_to_polylines(s, deflection)
        return out

    vis = collect([h.VCompound, h.OutLineVCompound])
    hid = collect([h.HCompound, h.OutLineHCompound]) if hidden else []
    return vis, hid


def hlr_lines_groups(shapes, direction, deflection=0.15):
    """Hidden-line removal over several shapes; visible lines returned per shape.

    Every shape occludes every other one, so the result can be drawn with a
    different line style per group (e.g. claimed part solid, rest dashed).
    """
    n, x, _ = view_frame(direction)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*x))
    algo = HLRBRep_Algo()
    for s in shapes:
        algo.Add(s.wrapped)
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    out = []
    for i in range(1, len(shapes) + 1):
        algo.Select(i)
        h = HLRBRep_HLRToShape(algo)
        lines = []
        for g in (h.VCompound, h.OutLineVCompound):
            s = g()
            if s.IsNull():
                continue
            BRepLib.BuildCurves3d_s(s, 1e-6)
            lines += _edges_to_polylines(s, deflection)
        out.append(lines)
    return out


def project_point(p, direction):
    _, x, y = view_frame(direction)
    p = np.asarray(p, float)
    return np.array([p @ x, p @ y])


def compound(parts) -> cq.Shape:
    shapes = []
    for wp in parts:
        shapes += [o for o in wp.vals() if isinstance(o, cq.Shape)]
    return cq.Compound.makeCompound(shapes)


def plot_lines(ax, vis, hid=(), lw=0.6, color="k"):
    if hid:
        ax.add_collection(LineCollection(hid, colors="0.45", linewidths=lw * 0.7, linestyles=(0, (3, 2))))
    ax.add_collection(LineCollection(vis, colors=color, linewidths=lw))


def bounds(lines):
    a = np.vstack(lines)
    return a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max()


def save_view(path_base, vis, hid=(), labels=(), title=None, lw=0.6, figsize=(8, 10), dpi=300, pad=0.06):
    """labels: iterable of (text, anchor_xy, text_xy)."""
    fig, ax = plt.subplots(figsize=figsize)
    plot_lines(ax, vis, hid, lw=lw)
    x0, x1, y0, y1 = bounds(vis)
    pts = [np.array(t) for _, _, t in labels]
    if pts:
        pa = np.vstack(pts)
        x0, x1 = min(x0, pa[:, 0].min()), max(x1, pa[:, 0].max())
        y0, y1 = min(y0, pa[:, 1].min()), max(y1, pa[:, 1].max())
    for text, a, t in labels:
        ax.annotate(
            text,
            xy=a,
            xytext=t,
            fontsize=9,
            ha="center",
            va="center",
            arrowprops=dict(arrowstyle="-", lw=0.5, color="k", shrinkA=4, shrinkB=0),
        )
    dx, dy = (x1 - x0) * pad + 5, (y1 - y0) * pad + 5
    ax.set_xlim(x0 - dx, x1 + dx)
    ax.set_ylim(y0 - dy, y1 + dy)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, y=-0.06)
    fig.tight_layout()
    for ext in ("png", "svg", "pdf"):
        fig.savefig(f"{path_base}.{ext}", dpi=dpi if ext == "png" else None, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------- shaded preview


def _tess(wp, tol=0.8):
    tris = []
    for s in wp.vals():
        if not isinstance(s, cq.Shape):
            continue
        vs, fs = s.tessellate(tol, 0.3)
        v = np.array([[p.x, p.y, p.z] for p in vs])
        if len(fs):
            tris.append(v[np.array(fs)])
    return np.concatenate(tris) if tris else np.zeros((0, 3, 3))


def shaded(path, parts: dict, colors: dict, direction, figsize=(8, 9), dpi=200, title=None, light=(0.4, 0.6, 0.9)):
    n, x, y = view_frame(direction)
    L = np.asarray(light, float)
    L = L / np.linalg.norm(L)
    polys, cols, depth = [], [], []
    for name, wp in parts.items():
        t = _tess(wp)
        if not len(t):
            continue
        nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        ln = np.linalg.norm(nrm, axis=1)
        ok = ln > 1e-9
        t, nrm = t[ok], nrm[ok] / ln[ok, None]
        facing = nrm @ n > 0
        t, nrm = t[facing], nrm[facing]
        base = np.array(colors.get(name, (0.6, 0.6, 0.6)))
        inten = 0.35 + 0.65 * np.clip(nrm @ L, 0, 1)
        c = np.clip(base[None, :] * inten[:, None] + 0.08, 0, 1)
        p2 = np.stack([t @ x, t @ y], axis=-1)
        polys.append(p2)
        cols.append(c)
        depth.append((t @ n).mean(axis=1))
    P = np.concatenate(polys)
    C = np.concatenate(cols)
    D = np.concatenate(depth)
    order = np.argsort(D)
    fig, ax = plt.subplots(figsize=figsize)
    ax.add_collection(PolyCollection(P[order], facecolors=C[order], edgecolors=C[order], linewidths=0.2))
    a = P.reshape(-1, 2)
    m = 20
    ax.set_xlim(a[:, 0].min() - m, a[:, 0].max() + m)
    ax.set_ylim(a[:, 1].min() - m, a[:, 1].max() + m)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)


def render_vtk(path, parts: dict, colors: dict, direction, size=(1600, 1600), tol=0.4, edges=True, parallel=True, zoom=1.15):
    """Depth-buffered shaded render (VTK offscreen)."""
    import vtk

    n, _, up = view_frame(direction)
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for name, wp in parts.items():
        pts = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        off = 0
        for s in wp.vals():
            if not isinstance(s, cq.Shape):
                continue
            vs, fs = s.tessellate(tol, 0.2)
            for v in vs:
                pts.InsertNextPoint(v.x, v.y, v.z)
            for f in fs:
                polys.InsertNextCell(3)
                for i in f:
                    polys.InsertCellPoint(i + off)
            off += len(vs)
        pd = vtk.vtkPolyData()
        pd.SetPoints(pts)
        pd.SetPolys(polys)
        nf = vtk.vtkPolyDataNormals()
        nf.SetInputData(pd)
        nf.SetFeatureAngle(35)
        nf.SplittingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nf.GetOutputPort())
        act = vtk.vtkActor()
        act.SetMapper(mp)
        pr = act.GetProperty()
        pr.SetColor(*colors.get(name, (0.6, 0.6, 0.6)))
        pr.SetAmbient(0.25)
        pr.SetDiffuse(0.75)
        pr.SetSpecular(0.15)
        pr.SetSpecularPower(20)
        ren.AddActor(act)
        if edges:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputConnection(nf.GetOutputPort())
            fe.BoundaryEdgesOn()
            fe.FeatureEdgesOn()
            fe.SetFeatureAngle(35)
            fe.ManifoldEdgesOff()
            fe.NonManifoldEdgesOff()
            em = vtk.vtkPolyDataMapper()
            em.SetInputConnection(fe.GetOutputPort())
            em.ScalarVisibilityOff()
            ea = vtk.vtkActor()
            ea.SetMapper(em)
            ea.GetProperty().SetColor(0.1, 0.1, 0.1)
            ea.GetProperty().SetLineWidth(1.2)
            ren.AddActor(ea)
    ren.ResetCamera()
    cam = ren.GetActiveCamera()
    fp = np.array(cam.GetFocalPoint())
    cam.SetPosition(*(fp + n * 3000))
    cam.SetViewUp(*up)
    if parallel:
        cam.ParallelProjectionOn()
    ren.ResetCamera()
    cam.Zoom(zoom)
    light = vtk.vtkLight()
    light.SetLightTypeToCameraLight()
    light.SetPosition(-0.4, 0.8, 1)
    light.SetIntensity(0.9)
    ren.AddLight(light)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(*size)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    rw.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(str(path))
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    rw.Finalize()


# --------------------------------------------------------------------------- dimensions


def dim_linear(ax, p1, p2, offset, text=None, horizontal=True, fs=7):
    """Draw a linear dimension between p1 and p2 offset perpendicular by ``offset``."""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    if horizontal:
        yv = max(p1[1], p2[1]) + offset if offset > 0 else min(p1[1], p2[1]) + offset
        a, b = np.array([p1[0], yv]), np.array([p2[0], yv])
        ax.plot([p1[0], p1[0]], [p1[1], yv + math.copysign(2, offset)], "k-", lw=0.35)
        ax.plot([p2[0], p2[0]], [p2[1], yv + math.copysign(2, offset)], "k-", lw=0.35)
        val = abs(p2[0] - p1[0])
        rot = 0
        tp = (a + b) / 2 + np.array([0, 1.5 if offset > 0 else -1.5])
        va = "bottom" if offset > 0 else "top"
        ha = "center"
    else:
        xv = max(p1[0], p2[0]) + offset if offset > 0 else min(p1[0], p2[0]) + offset
        a, b = np.array([xv, p1[1]]), np.array([xv, p2[1]])
        ax.plot([p1[0], xv + math.copysign(2, offset)], [p1[1], p1[1]], "k-", lw=0.35)
        ax.plot([p2[0], xv + math.copysign(2, offset)], [p2[1], p2[1]], "k-", lw=0.35)
        val = abs(p2[1] - p1[1])
        rot = 90
        tp = (a + b) / 2 + np.array([-1.5 if offset < 0 else 1.5, 0])
        va = "center"
        ha = "right" if offset < 0 else "left"
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<|-|>", lw=0.4, color="k", mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.text(*tp, text or f"{val:.0f}", fontsize=fs, rotation=rot, ha=ha, va=va)


def dim_diameter(ax, center, r, angle_deg, text, fs=7):
    c = np.asarray(center, float)
    u = np.array([math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))])
    a, b = c - u * r, c + u * r
    tail = b + u * r * 1.6
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<|-|>", lw=0.4, color="k", mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.plot([b[0], tail[0], tail[0] + 10 * np.sign(u[0] or 1)], [b[1], tail[1], tail[1]], "k-", lw=0.35)
    ax.text(tail[0] + 11 * np.sign(u[0] or 1), tail[1], text, fontsize=fs, ha="left" if u[0] >= 0 else "right", va="center")
