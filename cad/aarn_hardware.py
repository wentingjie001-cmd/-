"""Hardware library for the Aarn PM40 benchmark model.

Generic outdoor-pack hardware at typical commercial sizes (20 mm webbing). These are
stand-ins drawn from common practice, not measurements of Aarn's parts.

Local frame of every part: X = across the webbing, Y = thickness (towards the
wearer is -Y once placed), Z = along the webbing. ``place`` maps it into the pack.
"""

from __future__ import annotations

import math

import cadquery as cq

V = cq.Vector


def place(wp: cq.Workplane, origin, xdir, zdir) -> cq.Workplane:
    """Move a part built in the local frame so local X -> xdir and local Z -> zdir at origin."""
    z = V(*zdir).normalized()
    x = V(*xdir)
    x = (x - z * x.dot(z)).normalized()
    loc = cq.Location(cq.Plane(origin=V(*origin), xDir=x, normal=z))
    return cq.Workplane().add([s.moved(loc) for s in wp.vals() if isinstance(s, cq.Shape)])


def _tube(path_wire, start, tangent, r) -> cq.Workplane:
    prof = cq.Wire.assembleEdges([cq.Edge.makeCircle(r, start, tangent)])
    return cq.Workplane().add(cq.Solid.sweep(prof, [], path_wire, isFrenet=True))


def compound(*wps) -> cq.Workplane:
    out = []
    for wp in wps:
        out += [s for s in wp.vals() if isinstance(s, cq.Shape)]
    return cq.Workplane().add(cq.Compound.makeCompound(out))


def path_frame(path: cq.Edge, u: float, wdir):
    """Origin, width direction and tangent on a spline path at parameter u (0..1)."""
    o = path.positionAt(u)
    t = path.tangentAt(u).normalized()
    w = V(*wdir)
    w = w - t * w.dot(t)
    w = w.normalized() if w.Length > 1e-6 else t.cross(V(0, 0, 1)).normalized()
    return (o.x, o.y, o.z), (w.x, w.y, w.z), (t.x, t.y, t.z)


# ----------------------------------------------------------------------------- buckles


def side_release_buckle(w: float = 20.0):
    """Female housing (z < 0) and male tongue (z > -18) of a side-release buckle, engaged."""
    W, T, L = w + 9, 8.5, 30
    female = cq.Workplane("XY").box(W, T, L).translate((0, 0, -L / 2)).edges("|Y").fillet(3).edges("|Z").fillet(1.5)
    female = female.cut(cq.Workplane("XY").box(W - 3, T - 2.4, L - 6).translate((0, 0, -(L - 6) / 2 + 0.01)))
    for s in (1, -1):  # prong release windows on both sides
        female = female.cut(cq.Workplane("XY").box(4, T + 2, 9).translate((s * (W / 2 - 1), 0, -12)))
    female = female.cut(cq.Workplane("XY").box(w + 1, T + 2, 3.2).translate((0, 0, -L + 3.5)))  # webbing bar slot

    tongue = cq.Workplane("XY").box(7, T - 3, 20).translate((0, 0, -9))
    prongs = cq.Workplane("XY")
    for s in (1, -1):
        prong = cq.Workplane("XY").box(2.6, T - 3, 20).translate((s * (W / 2 - 4.2), 0, -9))
        catch = cq.Workplane("XY").box(2.2, T - 3, 4).translate((s * (W / 2 - 2.2), 0, -12))
        prongs = prongs.union(prong).union(catch)
    frame = cq.Workplane("XY").box(W, T - 2, 14).translate((0, 0, 7)).edges("|Y").fillet(3)
    frame = frame.cut(cq.Workplane("XY").box(w + 1, T + 2, 3.2).translate((0, 0, 9)))
    male = frame.union(tongue).union(prongs)
    return {"female": female, "male": male}


def ladder_lock(w: float = 20.0):
    """Ladder-lock adjuster with a pull tab (webbing runs along Z through the two slots)."""
    W, T, L = w + 8, 3.2, 20
    body = cq.Workplane("XY").box(W, T, L).edges("|Y").fillet(2.5)
    for z in (-4.5, 4.5):
        body = body.cut(cq.Workplane("XY").box(w + 1, T + 2, 3.6).translate((0, 0, z)))
    tab = cq.Workplane("XY").box(W - 4, T, 10).translate((0, -2.2, L / 2 + 3)).edges("|Y").fillet(2)
    tab = tab.rotate((0, 0, L / 2), (1, 0, L / 2), -18)
    return body.union(tab)


def tri_glide(w: float = 20.0):
    W, T, L = w + 6, 3.0, 14
    body = cq.Workplane("XY").box(W, T, L).edges("|Y").fillet(2)
    for z in (-3.2, 3.2):
        body = body.cut(cq.Workplane("XY").box(w + 1, T + 2, 3.0).translate((0, 0, z)))
    return body


def sternum_slider():
    """Hook that rides on the sternum rail webbing (rail along local Z)."""
    plate = cq.Workplane("XY").box(24, 3, 14).edges("|Y").fillet(2.5)
    hook = cq.Workplane("XY").box(24, 6, 3).translate((0, 3, 5.5))
    lip = cq.Workplane("XY").box(24, 2, 6).translate((0, 6, 3))
    slot = cq.Workplane("XY").box(21, 5, 3.6).translate((0, 0, -3))
    return plate.union(hook).union(lip).cut(slot)


# ----------------------------------------------------------------------------- cord hardware


def cord_lock(hole: float = 4.0):
    """Spring cord lock: barrel, plunger with cross hole, coil spring inside (cord along local X)."""
    barrel = cq.Workplane("XY").circle(7).extrude(18).faces(">Z").workplane().hole(11, 15)
    barrel = barrel.cut(cq.Workplane("YZ").circle(hole / 2 + 0.4).extrude(20, both=True).translate((0, 0, 9)))
    plunger = cq.Workplane("XY").circle(5.2).extrude(14).translate((0, 0, 6))
    plunger = plunger.cut(cq.Workplane("YZ").circle(hole / 2 + 0.4).extrude(20, both=True).translate((0, 0, 10.5)))
    button = cq.Workplane("XY").circle(6).extrude(3).translate((0, 0, 20)).edges(">Z").fillet(1.2)
    helix = cq.Wire.makeHelix(pitch=1.6, height=4.4, radius=3.6, center=V(0, 0, 3.2))
    spring = _tube(helix, helix.startPoint(), helix.tangentAt(0), 0.35)
    return {"barrel": barrel.translate((0, 0, -9)), "plunger": plunger.union(button).translate((0, 0, -9)), "spring": spring.translate((0, 0, -9))}


def cord_toggle():
    """Pull toggle on the end of a shock cord."""
    return cq.Workplane("XY").ellipse(5, 3.5).extrude(16).translate((0, 0, -8)).edges().fillet(1.2)


def cord_end_clip():
    """Small cord grip used on the Lasso Loc loops."""
    b = cq.Workplane("XY").box(9, 6, 12).edges("|Z").fillet(2.5).edges(">Z or <Z").fillet(1)
    return b.cut(cq.Workplane("XZ").circle(1.6).extrude(10, both=True))


# ----------------------------------------------------------------------------- zip


def zipper(path_pts, wdir, tape_w=24.0, teeth_pitch=2.6, slider_u=0.92):
    """Coil zip on a 3D path: tape, chain teeth, slider and pull tab with a cord loop."""
    pts = [V(*p) for p in path_pts]
    path = cq.Edge.makeSpline(pts)
    L = path.Length()
    tape_secs, teeth = [], []
    n = max(8, int(L / 12))
    for i in range(n + 1):
        o, w, t = path_frame(path, i / n, wdir)
        tape_secs.append(cq.Workplane(cq.Plane(origin=o, xDir=w, normal=t)).rect(tape_w, 0.8).val())
    tape = cq.Workplane().add(cq.Solid.makeLoft(tape_secs, False))
    k = int(L / teeth_pitch)
    for i in range(k):
        o, w, t = path_frame(path, (i + 0.5) / k, wdir)
        side = 1 if i % 2 else -1
        tooth = cq.Workplane("XY").box(3.4, 1.8, 1.5).translate((side * 1.0, 0.6, 0))
        teeth.append(place(tooth, o, w, t))
    o, w, t = path_frame(path, slider_u, wdir)
    slider = cq.Workplane("XY").box(8, 4.6, 12).edges("|Z").fillet(1.8).edges(">Z").fillet(1.2).translate((0, 1.2, 0))
    slider = slider.cut(cq.Workplane("XY").box(5, 1.6, 14).translate((0, 1.2, 0)))
    tab = cq.Workplane("XY").box(5.5, 1.4, 16).translate((0, 4.6, -7)).edges("|Y").fillet(2)
    tab = tab.cut(cq.Workplane("XZ").center(0, -12).rect(2.6, 4).extrude(5, both=True).translate((0, 4.6, 0)))
    lp = cq.Edge.makeSpline([V(0, 4.6, -13), V(3, 5.6, -22), V(0, 6, -30), V(-3, 5.6, -21), V(-0.5, 4.8, -14)])
    loop = _tube(cq.Wire.assembleEdges([lp]), lp.startPoint(), lp.tangentAt(0), 1.1)
    puller = place(slider.union(tab), o, w, t)
    return {"tape": tape, "teeth": compound(*teeth), "slider": puller, "pull_cord": place(loop, o, w, t)}


# ----------------------------------------------------------------------------- webbing items


def webbing_loop(w=20.0, length=40.0, gap=6.0, t=1.6):
    """Webbing folded into a loop and bar-tacked to a panel (panel face at y = 0, loop towards -Y)."""
    pts = [V(0, 0, -length / 2), V(0, -gap, -length / 2 + 6), V(0, -gap - 1, 0), V(0, -gap, length / 2 - 6), V(0, 0, length / 2)]
    path = cq.Edge.makeSpline(pts)
    secs = []
    for i in range(13):
        o, wd, tg = path_frame(path, i / 12, (1, 0, 0))
        secs.append(cq.Workplane(cq.Plane(origin=o, xDir=wd, normal=tg)).rect(w, t).val())
    loop = cq.Workplane().add(cq.Solid.makeLoft(secs, False))
    tacks = cq.Workplane("XY")
    for z in (-length / 2 + 2, length / 2 - 2):
        tacks = tacks.union(cq.Workplane("XY").box(w - 4, 0.8, 3).translate((0, -0.6, z)))
    return loop.union(tacks)


def lasso_loc_tab():
    """Aarn 'Lasso Loc' tab: short webbing tab carrying an elastic cord loop with a grip."""
    tab = cq.Workplane("XY").box(14, 1.6, 24).edges("|Y").fillet(1.5)
    cord_path = cq.Edge.makeSpline([V(-3, -1.5, 10), V(-9, -4, -6), V(0, -6, -22), V(9, -4, -6), V(3, -1.5, 10)])
    cord = _tube(cq.Wire.assembleEdges([cord_path]), cord_path.startPoint(), cord_path.tangentAt(0), 1.2)
    grip = cord_end_clip().translate((0, -3.5, 4))
    return {"tab": tab, "cord": cord, "grip": grip}


def bar_tacks(path: cq.Edge, wdir, us, w=16.0):
    tacks = []
    for u in us:
        o, wd, t = path_frame(path, u, wdir)
        tacks.append(place(cq.Workplane("XY").box(w, 0.8, 3), o, wd, t))
    return compound(*tacks)


if __name__ == "__main__":
    items = {"srb": side_release_buckle(), "ladder": ladder_lock(), "tri": tri_glide(), "slider": sternum_slider(), "toggle": cord_toggle()}
    items.update({f"cord_{k}": v for k, v in cord_lock().items()})
    items.update({f"lasso_{k}": v for k, v in lasso_loc_tab().items()})
    items["loop"] = webbing_loop()
    for k, v in items.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(k, kk, vv.val().isValid(), round(vv.val().Volume(), 1))
        else:
            print(k, v.val().isValid(), round(v.val().Volume(), 1))
    z = zipper([(0, 0, 0), (60, 5, 0), (120, 0, 0)], (0, 0, 1))
    for k, v in z.items():
        print("zip", k, v.val().isValid(), round(v.val().Volume(), 1))
