"""Model data for the interactive 3D viewer in ``../viewer``.

    python3 build_viewer.py

Builds the A1 preview in five poses (rest, linkage web run fully to either side, yoke on the top and
bottom rung) and writes ``viewer/model.js``: a manifest plus one base64 block with quantised vertices
and triangle indices. Parts that do not move are stored once; the harness parts are stored once per
pose and the page blends between them.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np

import backpack_model as m
import preview_a1 as pv

OUT = Path(__file__).resolve().parents[1] / "viewer" / "model.js"

TORSO_MAX = pv.TORSO_STEP * (pv.TORSO_RUNGS // 2)
POSES = {
    "rest": (0.0, 0.0),
    "sway_pos": (pv.SWAY_MAX, 0.0),
    "sway_neg": (-pv.SWAY_MAX, 0.0),
    "torso_pos": (0.0, TORSO_MAX),
    "torso_neg": (0.0, -TORSO_MAX),
}

# Layers in the order they come apart, from the pack towards the wearer; ``explode`` is the Y offset in mm.
LAYERS = [
    ("bag", "包体、卷口、口袋", 250.0, None),
    ("panel", "后幅附件、背长调节", 175.0, ("hub_patch", "ladder", "patches", "yoke", "g_hook", "handle")),
    ("frame", "Y 型背架", 115.0, ("y_frame",)),
    ("hub", "联动座", 60.0, ("hub", "rollers", "cam_lever")),
    ("pad", "悬浮网、腰垫", 0.0, ("mesh", "mesh_binding", "lumbar", "tension", "tension_hw")),
    ("linkage", "联动带", -60.0, ("linkage_web", "stops")),
    ("belt", "腰带", -120.0, ("pivot", "belt_centre", "wing_inner", "wing_outer", "belt_pockets", "belt_zips", "belt_web", "belt_buckle")),
    ("shoulder", "肩带", -190.0, ("strap_inner", "strap_outer", "load_lifters", "sternum", "strap_hw")),
]
SHINY = ("y_frame", "g_hook", "rollers")


def layer_of(part):
    for key, _, _, members in LAYERS:
        if members and part.key in members:
            return key
    if part.group == "bag":
        return "bag"
    raise KeyError(part.key)


def split_creases(v, f, angle=50.0):
    """Weld coincident vertices, then duplicate them along creases so that plain per-vertex normals look right.

    Returns (source vertex index for every output vertex, triangles).
    """
    import vtk
    from vtk.util import numpy_support as ns

    pd = vtk.vtkPolyData()
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.ascontiguousarray(v, dtype=np.float64), deep=True))
    pd.SetPoints(pts)
    cells = vtk.vtkCellArray()
    cells.SetData(3, ns.numpy_to_vtkIdTypeArray(np.ascontiguousarray(f, dtype=np.int64).ravel(), deep=True))
    pd.SetPolys(cells)
    src = ns.numpy_to_vtkIdTypeArray(np.arange(len(v), dtype=np.int64), deep=True)
    src.SetName("src")
    pd.GetPointData().AddArray(src)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd)
    nf = vtk.vtkPolyDataNormals()
    nf.SetInputConnection(clean.GetOutputPort())
    nf.SetFeatureAngle(angle)
    nf.SplittingOn()
    nf.ConsistencyOn()
    nf.Update()
    out = nf.GetOutput()
    ids = ns.vtk_to_numpy(out.GetPointData().GetArray("src")).astype(np.int64)
    polys = out.GetPolys()
    conn = ns.vtk_to_numpy(polys.GetConnectivityArray())
    assert polys.GetNumberOfCells() * 3 == len(conn), "non-triangle cells"
    return ids, conn.reshape(-1, 3).astype(np.int64)


def main():
    built = {name: {p.key: p for p in pv.build(sway, torso)[0]} for name, (sway, torso) in POSES.items()}
    rest = built["rest"]
    lo = np.min([p.v.min(axis=0) for ps in built.values() for p in ps.values()], axis=0) - 1.0
    hi = np.max([p.v.max(axis=0) for ps in built.values() for p in ps.values()], axis=0) + 1.0

    blob = bytearray()

    def put(arr):
        while len(blob) % 4:
            blob.append(0)
        off = len(blob)
        blob.extend(np.ascontiguousarray(arr).tobytes())
        return off

    def quant(v):
        return np.round((v - lo) / (hi - lo) * 65535.0).astype("<u2")

    parts = []
    for key, p in rest.items():
        ids, f = split_creases(p.v, p.f)
        moving = {}
        for name in list(POSES)[1:]:
            q = built[name][key]
            assert q.v.shape == p.v.shape and np.array_equal(q.f, p.f), f"{key}: topology differs in pose {name}"
            if np.abs(q.v - p.v).max() > 0.02:
                moving[name] = put(quant(q.v[ids]))
        wide = len(ids) > 65535
        parts.append(
            {
                "key": key,
                "name": p.name,
                "layer": layer_of(p),
                "color": [round(c, 3) for c in p.color],
                "shiny": key in SHINY,
                "nv": int(len(ids)),
                "nt": int(len(f)),
                "pos": put(quant(p.v[ids])),
                "idx": put(f.astype("<u4" if wide else "<u2")),
                "wide": wide,
                "poses": moving,
            }
        )

    manifest = {
        "title": "BP40-A1",
        "lo": [round(float(x), 3) for x in lo],
        "hi": [round(float(x), 3) for x in hi],
        "swayMax": pv.SWAY_MAX,
        "torsoStep": pv.TORSO_STEP,
        "torsoRungs": pv.TORSO_RUNGS,
        "leverPivot": [0.0, m.P.hub_y0 + m.P.hub_depth + 5.0, m.P.hub_z0 + 20.0],
        # The A0 lever hangs down the pack-side face, which the bag covers. The preview swings it up
        # onto the wearer side of the hub so the lock action can be seen; the real lever needs a new
        # position (see docs/08).
        "leverShow": [0.0, m.P.hub_y0 + m.P.hub_depth + 6.0, m.P.hub_z0 + 46.0],
        "layers": [{"key": k, "name": n, "explode": e} for k, n, e, _ in LAYERS],
        "parts": parts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = "window.BP40_MODEL = " + json.dumps({"manifest": manifest, "data": base64.b64encode(bytes(blob)).decode("ascii")}, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT.write_text(text, encoding="utf-8")
    nv, nt = sum(p["nv"] for p in parts), sum(p["nt"] for p in parts)
    moving = [p["key"] for p in parts if p["poses"]]
    print(f"{len(parts)} parts, {nv} vertices, {nt} triangles; {len(moving)} posed parts: {', '.join(moving)}")
    print(f"wrote {OUT} ({len(text) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
