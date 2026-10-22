"""Biblioteca 3D (Blender/bpy) dos vídeos animados da Infinity Guard, estilo anime (toon + contorno).

Cada vídeo tem um `shots3d.py` que lista as tomadas e chama `lib3d.main(TOMADAS)`:

    TOMADAS = {"A": (6.3, "aerea", {}), "B": (6.0, "casa", {"kind": "saida"}), ...}

Cenários prontos: "aerea" (estrada com curvas vista de cima), "estrada" (carro na estrada, mood=True fecha o
céu), "casa" (kind: saida, instalada, anoitecer, entrada, feed, feed_noite) e "kit" (2 câmeras no pedestal).
Uso: b3d/bin/python <video>/shots3d.py TOMADA [--still QUADRO] [--samples N] [--saida PASTA]
"""
import bpy, math, sys, os, random, time
T0 = time.time()
from mathutils import Vector, Euler

FPS = 12  # animação "em dois", como em anime
RX, RY = map(int, os.environ.get("LIB3D_RES", "640x1138").split("x"))  # resolução das tomadas
DUR, N = 1.0, 1

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
random.seed(4)

# ---------------- helpers ----------------
MATS = {}
ANIME = True

def mat(name, color, rough=0.55, emit=0.0, metal=0.0, alpha=1.0):
    key = (name, color, rough, emit, metal)
    if key in MATS: return MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    c = tuple(x / 255 if max(color) > 1 else x for x in color)
    c = tuple((x ** 2.2) for x in c)  # sRGB -> linear
    if ANIME:
        nt = m.node_tree; out = nt.nodes["Material Output"]
        toon = nt.nodes.new("ShaderNodeBsdfToon"); toon.component = "DIFFUSE"
        toon.inputs["Color"].default_value = (*c, 1); toon.inputs["Size"].default_value = 0.92; toon.inputs["Smooth"].default_value = 0.03
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*c, 1)
        em.inputs["Strength"].default_value = emit if emit else 0.38
        add = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(toon.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
        if metal > 0.5 or rough < 0.15:
            gl = nt.nodes.new("ShaderNodeBsdfToon"); gl.component = "GLOSSY"
            gl.inputs["Size"].default_value = 0.2; gl.inputs["Smooth"].default_value = 0.0
            add2 = nt.nodes.new("ShaderNodeAddShader")
            nt.links.new(add.outputs[0], add2.inputs[0]); nt.links.new(gl.outputs[0], add2.inputs[1])
            add = add2
        nt.links.new(add.outputs[0], out.inputs["Surface"])
        m["em"] = em.name
        MATS[key] = m
        return m
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*c, 1)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Transmission Weight"].default_value = 1 - alpha
    MATS[key] = m
    return m

def emat(name, color, strength=0.0):
    """Pure emission material (for lights that switch on); returns (material, strength socket)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple((x / 255) ** 2.2 for x in color) + (1,)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m, em.inputs["Strength"]

def hexc(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def setmat(o, m):
    o.data.materials.clear(); o.data.materials.append(m)

def bevel(o, w=0.05, seg=3):
    md = o.modifiers.new("b", "BEVEL"); md.width = w; md.segments = seg; md.limit_method = "ANGLE"
    return o

def smooth(o):
    for p in o.data.polygons: p.use_smooth = True

def box(loc, size, m, bev=0.04, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bev: bevel(o, bev)
    setmat(o, m)
    if parent: o.parent = parent
    return o

def cyl(loc, r, depth, m, rot=(0, 0, 0), verts=32, parent=None, bev=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; setmat(o, m); smooth(o)
    if bev: bevel(o, bev)
    if parent: o.parent = parent
    return o

def sphere(loc, r, m, parent=None, seg=24, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.object; o.scale = scale; setmat(o, m); smooth(o)
    if parent: o.parent = parent
    return o

def ico(loc, r, m, sub=2, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object; o.scale = scale; setmat(o, m)
    return o

def cone(loc, r, depth, m, verts=8):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, depth=depth, location=loc)
    o = bpy.context.object; setmat(o, m); return o

def empty(loc=(0, 0, 0)):
    bpy.ops.object.empty_add(location=loc); return bpy.context.object

def mesh_from(verts, faces, m, name="m"):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); setmat(o, m); return o

# palette
C = {k: hexc(v) for k, v in dict(
    grass="#79b26a", grass2="#5e9a58", road="#4a4f5c", line="#f4efe2", wall="#f1e6d0", wall2="#e7d3b5",
    roof="#b5532f", roof2="#8f3f26", door="#6b4630", glass="#9fd0ee", gate="#9aa5b8", gate2="#7b8598",
    carbody="#dfe7f2", carblue="#2c5aa0", tire="#1b1f27", rim="#b9c1cf", trunk="#6b4a33", leaf="#4f8f55",
    leaf2="#6aa75e", suitcase1="#c0602f", suitcase2="#2f7f8f", gold="#d4aa52", navy="#13264a", cream="#f5f1e8",
    red="#c0392b", green="#2f7a4b", sidewalk="#c9c3b6", hill="#8bbf7a", pole="#8d8f96", camwhite="#f3f3f0",
    camdark="#1d2c48", fence="#ffffff").items()}
M = {k: mat(k, v) for k, v in C.items()}
M["glass"] = mat("glassg", C["glass"], rough=0.08, metal=0.2)
M["rim"] = mat("rimm", C["rim"], rough=0.25, metal=0.8)
M["gold"] = mat("goldm", C["gold"], rough=0.3, metal=0.9)
M["lens"] = mat("lens", (20, 30, 50), rough=0.05, metal=0.3)
M["head"] = mat("headl", (255, 244, 210), emit=4)
M["tail"] = mat("taill", (220, 40, 40), emit=2)
M["win_night"] = mat("winn", (255, 205, 120), emit=6)
M["bulbs"] = [mat(f"bulb{i}", c, emit=8) for i, c in enumerate([(255, 210, 90), (230, 60, 60), (80, 200, 110), (90, 160, 255)])]
M["ledg"] = mat("ledg", (60, 255, 140), emit=10)

# ---------------- assets ----------------
def make_car(loc=(0, 0, 0), luggage=True, body="carblue"):
    root = empty(loc)
    bm = M[body]
    b = box((0, 0, 0.55), (4.2, 1.8, 0.75), bm, 0.25, root)
    cab = box((-0.25, 0, 1.15), (2.3, 1.62, 0.7), bm, 0.22, root)
    # windows
    box((-0.25, 0, 1.17), (2.15, 1.66, 0.52), M["glass"], 0.12, root)
    box((0.92, 0, 1.12), (0.08, 1.5, 0.5), M["glass"], 0.03, root, rot=(0, -0.5, 0))
    for y in (0.93, -0.93):
        cyl((-1.35, y, 0.38), 0.4, 0.3, M["tire"], rot=(math.pi / 2, 0, 0), parent=root)
        cyl((1.35, y, 0.38), 0.4, 0.3, M["tire"], rot=(math.pi / 2, 0, 0), parent=root)
    wheels = []
    for x in (-1.35, 1.35):
        for y in (0.95, -0.95):
            w = cyl((x, y * 1.03, 0.38), 0.24, 0.3, M["rim"], rot=(math.pi / 2, 0, 0), verts=6, parent=root)
            wheels.append(w)
    box((2.08, 0.6, 0.62), (0.08, 0.38, 0.18), M["head"], 0.03, root)
    box((2.08, -0.6, 0.62), (0.08, 0.38, 0.18), M["head"], 0.03, root)
    box((-2.08, 0.62, 0.68), (0.08, 0.32, 0.16), M["tail"], 0.03, root)
    box((-2.08, -0.62, 0.68), (0.08, 0.32, 0.16), M["tail"], 0.03, root)
    box((0, 0, 0.32), (4.3, 1.86, 0.12), M["tire"], 0.05, root)
    if luggage:
        box((-0.25, 0, 1.56), (2.0, 1.5, 0.06), M["tire"], 0.02, root)
        box((-0.8, 0.2, 1.88), (0.9, 0.7, 0.6), M["suitcase1"], 0.1, root)
        box((0.1, -0.25, 1.82), (0.75, 0.75, 0.48), M["suitcase2"], 0.1, root)
        box((0.25, 0.42, 1.76), (0.5, 0.45, 0.36), M["gold"], 0.08, root)
        box((-0.8, 0.2, 2.22), (0.3, 0.08, 0.1), M["tire"], 0.03, root)
    return root, wheels

def make_tree(loc, s=1.0, kind=0):
    tr = cyl((loc[0], loc[1], loc[2] + 0.9 * s), 0.18 * s, 1.8 * s, M["trunk"], verts=8)
    if kind == 0:
        for i, (dz, r) in enumerate([(2.2, 1.2), (2.9, 0.95), (3.5, 0.6)]):
            ico((loc[0] + random.uniform(-.15, .15), loc[1], loc[2] + dz * s), r * s, M["leaf"] if i % 2 == 0 else M["leaf2"], 1)
    else:
        cone((loc[0], loc[1], loc[2] + 3.0 * s), 1.1 * s, 3.2 * s, M["leaf"], 8)

def make_house(loc=(0, 0, 0), rot=0, decor=False, camdev=False, gate_open=0.0, wall_color="wall", night=False):
    root = empty(loc); root.rotation_euler = (0, 0, rot)
    W_, Dp, Hh = 8.0, 6.0, 3.2
    box((0, 0, Hh / 2), (W_, Dp, Hh), M[wall_color], 0.05, root)
    # gable roof
    v = [(-W_ / 2 - .4, -Dp / 2 - .5, Hh), (W_ / 2 + .4, -Dp / 2 - .5, Hh), (W_ / 2 + .4, Dp / 2 + .5, Hh), (-W_ / 2 - .4, Dp / 2 + .5, Hh),
         (-W_ / 2 - .4, 0, Hh + 2.2), (W_ / 2 + .4, 0, Hh + 2.2)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    r = mesh_from(v, f, M["roof"], "roof"); r.parent = root
    sol = r.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.18
    # door, windows (front faces -Y)
    box((-1.2, -Dp / 2 - 0.02, 1.05), (1.0, 0.12, 2.1), M["door"], 0.03, root)
    box((-1.2 + 0.35, -Dp / 2 - 0.1, 1.05), (0.08, 0.08, 0.08), M["gold"], 0.0, root)
    wm = M["win_night"] if night else M["glass"]
    for x in (-3.0,):
        box((x, -Dp / 2 - 0.02, 1.8), (1.3, 0.1, 1.1), wm, 0.02, root)
        box((x, -Dp / 2 - 0.08, 1.8), (1.45, 0.06, 0.1), M["cream"], 0.0, root)
        box((x, -Dp / 2 - 0.08, 1.8), (0.08, 0.06, 1.2), M["cream"], 0.0, root)
        box((x, -Dp / 2 - 0.2, 1.2), (1.5, 0.3, 0.12), M["cream"], 0.03, root)
    # garage
    box((2.2, -Dp / 2 - 0.02, 1.2), (3.0, 0.1, 2.4), M["tire"], 0.02, root)
    gh = 2.3 * (1 - gate_open)
    gate = empty((2.2, -Dp / 2 - 0.1, 2.35)); gate.parent = root
    slats = []
    for k in range(9):
        z = -0.13 - k * 0.255
        s = box((2.2, -Dp / 2 - 0.12, 2.35 + z), (2.9, 0.08, 0.24), M["gate"] if k % 2 == 0 else M["gate2"], 0.02, root)
        slats.append(s)
    # front wall + sidewalk + grass
    box((-2.5, -Dp / 2 - 3.6, 0.45), (5.0, 0.3, 0.9), M["wall2"], 0.04, root)
    box((5.6, -Dp / 2 - 3.6, 0.45), (1.6, 0.3, 0.9), M["wall2"], 0.04, root)
    box((0, -Dp / 2 - 1.9, 0.02), (W_ + 4, 3.4, 0.04), M["grass"], 0.0, root)
    box((2.2, -Dp / 2 - 1.9, 0.04), (3.0, 3.6, 0.06), M["sidewalk"], 0.0, root)
    # porch lamp
    box((0.2, -Dp / 2 - 0.08, 2.3), (0.2, 0.16, 0.3), M["win_night"] if night else M["cream"], 0.03, root)
    if decor:
        # wreath on door + string lights under roof
        bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.09, location=(-1.2, -Dp / 2 - 0.12, 1.65), rotation=(math.pi / 2, 0, 0))
        t = bpy.context.object; setmat(t, M["green"]); t.parent = root
        sphere((-1.2, -Dp / 2 - 0.2, 1.38), 0.08, M["red"], root)
        for i in range(26):
            x = -W_ / 2 + i * W_ / 25
            sphere((x, -Dp / 2 - 0.55, Hh - 0.15 - 0.12 * math.sin(i * 1.3) ** 2), 0.07, M["bulbs"][i % 4], root, seg=10)
    cam = None
    if camdev:
        cam = empty((2.2, -Dp / 2 - 0.15, 2.85)); cam.parent = root
        box((0, -0.25, 0), (0.35, 0.55, 0.3), M["camwhite"], 0.12, cam)
        cyl((0, -0.53, 0), 0.11, 0.06, M["lens"], rot=(math.pi / 2, 0, 0), parent=cam)
        sphere((0.12, -0.5, 0.1), 0.025, M["ledg"], cam, seg=8)
        box((0, 0.02, 0), (0.2, 0.1, 0.2), M["camwhite"], 0.03, cam)
    return root, cam, slats

def ground(size=400, m="grass"):
    bpy.ops.mesh.primitive_plane_add(size=size); g = bpy.context.object; setmat(g, M[m]); return g

def straight_road(x0, x1, y=0, w=7.0):
    box(((x0 + x1) / 2, y, 0.02), (x1 - x0, w, 0.04), M["road"], 0.0)
    box(((x0 + x1) / 2, y - w / 2 - 0.7, 0.06), (x1 - x0, 1.4, 0.1), M["sidewalk"], 0.0)
    x = x0
    while x < x1:
        box((x, y, 0.05), (2.4, 0.18, 0.02), M["line"], 0.0); x += 6

def world(top, bottom, strength=1.0):
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Window"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], ramp.inputs[0])
    lin = lambda c: tuple((x / 255) ** 2.2 for x in c) + (1,)
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = lin(bottom)
    ramp.color_ramp.elements[1].position = 0.95; ramp.color_ramp.elements[1].color = lin(top)
    nt.links.new(ramp.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = strength
    return ramp, bg

def sun(rot, energy=3.5, color=(1, 0.93, 0.8), angle=0.15):
    bpy.ops.object.light_add(type="SUN", rotation=rot); l = bpy.context.object
    l.data.energy = energy; l.data.color = color; l.data.angle = angle; return l

def camera(loc, look, lens=35):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; c.data.lens = lens
    d = Vector(look) - Vector(loc); c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = c; return c

def aim(c, loc, look, frame):
    c.location = loc; d = Vector(look) - Vector(loc)
    c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=frame); c.keyframe_insert("rotation_euler", frame=frame)

def spin_wheels(wheels, dist_fn, nframes, r=0.4):
    for f in range(1, nframes + 1):
        a = -dist_fn(f) / r
        for w in wheels:
            w.rotation_euler = (math.pi / 2, a, 0); w.keyframe_insert("rotation_euler", frame=f)

def scatter_trees(xr, yr, n, avoid=None, s=(0.8, 1.4)):
    for i in range(n):
        x, y = random.uniform(*xr), random.uniform(*yr)
        if avoid and avoid(x, y): continue
        make_tree((x, y, 0), random.uniform(*s), random.randint(0, 3) // 3)

def hills(cx=0, cy=120, n=10, spread=260):
    for i in range(n):
        ico((cx + random.uniform(-spread / 2, spread / 2), cy + random.uniform(-10, 40), -6), random.uniform(18, 35),
            M["hill"] if i % 2 else M["grass2"], 3, scale=(1.6, 1, 0.55))

def anime_clouds(cx=0, cy=150, n=7, spread=260, zr=(30, 55), tint=(255, 255, 255)):
    cm = mat("cloudA", tint, emit=1.0)
    for i in range(n):
        g = empty((cx + random.uniform(-spread / 2, spread / 2), cy + random.uniform(-20, 30), random.uniform(*zr)))
        for j in range(6):
            sphere((j * 5 - 12 + random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(0, 4) if j % 2 else 0), random.uniform(4, 7.5), cm, g, 14, scale=(1, 0.7, 0.8))
    return cm

def lerp(a, b, k): return a + (b - a) * k
def ease(k): k = max(0, min(1, k)); return k * k * (3 - 2 * k)

def anim_value(sock, vals):  # [(frame, value)]
    for f, v in vals:
        sock.default_value = v; sock.keyframe_insert("default_value", frame=f)

# ---------------- cenários reutilizáveis ----------------

def shot_road(mood_anim=False):
    """estrada: car on straight road, tracking 3/4 camera, golden hour (M -> overcast)."""
    v = 11.0
    ground()
    straight_road(-40, v * DUR + 80)
    # far side fields, fences, poles, trees
    for x in range(-40, int(v * DUR + 80), 14):
        make_tree((x + random.uniform(-3, 3), random.uniform(9, 16), 0), random.uniform(0.9, 1.5), random.randint(0, 2) // 2)
        if random.random() < 0.6:
            make_tree((x + 7 + random.uniform(-3, 3), random.uniform(-30, -40), 0), random.uniform(0.8, 1.2))
    for x in range(-40, int(v * DUR + 80), 22):
        cyl((x, 8.0, 2.5), 0.1, 5, M["pole"], verts=8)
    hills(v * DUR / 2, 90, 14, 300)
    for x in range(-40, int(v * DUR + 80), 5):
        ico((x + random.uniform(-1.5, 1.5), random.uniform(-5.6, -6.6), 0.2), random.uniform(0.3, 0.5), M["leaf2"] if x % 2 else M["grass2"], 1, scale=(1.3, 1, 0.8))
        if random.random() < 0.5:
            sphere((x + random.uniform(-2, 2), random.uniform(-5.0, -5.4), 0.12), 0.12, random.choice(M["bulbs"][:1] + [M["red"], M["cream"]]), seg=8)
    car, wheels = make_car((0, -1.7, 0))
    for f in (1, N):
        car.location.x = v * (f - 1) / FPS; car.keyframe_insert("location", frame=f)
    for fc in car.animation_data.action.fcurves if hasattr(car.animation_data.action, "fcurves") else []:
        for k in fc.keyframe_points: k.interpolation = "LINEAR"
    _linear(car)
    spin_wheels(wheels, lambda f: v * (f - 1) / FPS, N)
    cam = camera((0, 0, 0), (0, 0, 0), 32)
    for f in (1, N):
        x = v * (f - 1) / FPS
        aim(cam, (x + 7.5 - 1.5 * f / N, -13.5, 3.0), (x + 0.6, -1.7, -0.6), f)
    _linear(cam)
    ramp, bg = world((246, 140, 120), (255, 214, 160), 1.0)
    anime_clouds(v * DUR / 2, 150, 9, 320, (35, 60), (255, 228, 215))
    s = sun((math.radians(78), 0, math.radians(-35)), 4.0, (1, 0.82, 0.62), 0.12)
    if mood_anim:
        lin = lambda c: tuple((x / 255) ** 2.2 for x in c) + (1,)
        for f, top, bot, e in [(1, (246, 140, 120), (255, 214, 160), 4.0), (int(N * 0.5), (96, 104, 120), (150, 156, 168), 1.2), (N, (90, 98, 114), (140, 146, 160), 1.0)]:
            ramp.color_ramp.elements[1].color = lin(top); ramp.color_ramp.elements[1].keyframe_insert("color", frame=f)
            ramp.color_ramp.elements[0].color = lin(bot); ramp.color_ramp.elements[0].keyframe_insert("color", frame=f)
            s.data.energy = e; s.data.keyframe_insert("energy", frame=f)
        # dark clouds drifting in
        mc = mat("cloud", (110, 116, 128), rough=1)
        for i in range(9):
            g = empty((random.uniform(10, 90), random.uniform(25, 45), random.uniform(16, 22)))
            for j in range(4):
                sphere((j * 2.4 - 3.6, random.uniform(-1, 1), random.uniform(-.6, .8)), random.uniform(2.0, 3.2), mc, g, 16)
            g.location.x += 0; g.keyframe_insert("location", frame=1)
            g.scale = (0.01, 0.01, 0.01); g.keyframe_insert("scale", frame=1)
            g.scale = (1, 1, 1); g.keyframe_insert("scale", frame=int(N * 0.45))

def _linear(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    try:
        fcs = ad.action.fcurves
    except AttributeError:
        fcs = [fc for layer in ad.action.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for k in fc.keyframe_points: k.interpolation = "LINEAR"

def shot_aerial():
    """A: aerial over winding road, car driving away from a tiny house; camera rises."""
    ground()
    pts = []
    for i in range(240):
        t = i / 239
        x = lerp(-60, 140, t); y = 22 * math.sin(t * 5.0) + 10 * math.sin(t * 11)
        pts.append((x, y))
    w = 3.2
    verts, faces = [], []
    for i, (x, y) in enumerate(pts):
        nx, ny = (pts[min(i + 1, len(pts) - 1)][0] - pts[max(i - 1, 0)][0], pts[min(i + 1, len(pts) - 1)][1] - pts[max(i - 1, 0)][1])
        L = math.hypot(nx, ny); px, py = -ny / L, nx / L
        verts += [(x + px * w, y + py * w, 0.03), (x - px * w, y - py * w, 0.03)]
        if i: faces.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
    mesh_from(verts, faces, M["road"], "road")
    for i in range(0, len(pts) - 2, 3):
        x, y = pts[i]; x2, y2 = pts[i + 1]
        box((x, y, 0.06), (1.0, 0.2, 0.02), M["line"], 0.0, rot=(0, 0, math.atan2(y2 - y, x2 - x)))
    def near(x, y): return min(math.hypot(x - a, y - b) for a, b in pts[::4]) < 6
    scatter_trees((-60, 150), (-50, 90), 140, near, (1.2, 2.2))
    make_house((-58, 12, 0), rot=math.radians(90), decor=True)
    for hx, hy in [(-48, -14), (-70, 30)]:
        make_house((hx, hy, 0), rot=math.radians(random.choice([0, 90, 180])), wall_color="wall2")
    hills(40, 140, 16, 400)
    car, wheels = make_car((0, 0, 0))
    car.scale = (1.6, 1.6, 1.6)
    # drive along path segment
    i0, i1 = 70, 120
    for f in range(1, N + 1):
        k = (f - 1) / (N - 1); idx = lerp(i0, i1, k); i = int(idx); fr = idx - i
        x = lerp(pts[i][0], pts[i + 1][0], fr); y = lerp(pts[i][1], pts[i + 1][1], fr)
        car.location = (x, y, 0); car.rotation_euler = (0, 0, math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
        car.keyframe_insert("location", frame=f); car.keyframe_insert("rotation_euler", frame=f)
    spin_wheels(wheels, lambda f: f * 0.6, N)
    cam = camera((0, 0, 0), (0, 0, 0), 30)
    cx, cy = pts[i0][0], pts[i0][1]
    aim(cam, (cx - 10, cy - 16, 6), (cx + 3, cy, 1), 1)
    ce, cye = pts[i1][0], pts[i1][1]
    aim(cam, (ce - 30, cye - 48, 34), (ce - 2, cye + 4, 0), N)
    world((70, 140, 230), (190, 226, 250), 1.0)
    anime_clouds(40, 220, 9, 400, (40, 70))
    sun((math.radians(50), 0, math.radians(-40)), 4.0, (1, 0.95, 0.85))

def shot_house(kind):
    """B: departure, D: camera installed, E: day->night, F: push in to entrance, FEED: camera POV."""
    ground()
    night = kind == "feed_noite"
    house, camdev, slats = make_house((0, 0, 0), decor=kind in ("saida",), camdev=kind in ("instalada", "anoitecer", "entrada", "feed", "feed_noite"), night=False)
    # street in front
    straight_road(-60, 60, y=-12.5, w=7)
    make_house((-14, 1, 0), wall_color="wall2"); make_house((14, 1, 0), wall_color="wall2")
    for x in (-21, -7.5, 7.5, 21):
        make_tree((x, -9.2, 0), 0.9)
    scatter_trees((-60, 60), (8, 40), 40, s=(1.0, 1.6))
    hills(0, 110, 12, 300)
    world((70, 140, 230), (190, 226, 250), 1.0)
    if kind != "anoitecer": anime_clouds(0, 160, 7, 300, (30, 55))
    s = sun((math.radians(55), 0, math.radians(-25)), 4.0, (1, 0.95, 0.85))
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    if kind == "saida":
        car, wheels = make_car((2.2, -6.0, 0), luggage=True)
        car.rotation_euler = (0, 0, math.radians(90))
        # car backs out then drives right
        keys = [(1, (2.2, -6.0)), (int(N * 0.35), (2.2, -6.0)), (int(N * 0.6), (2.2, -11.0)), (N, (30, -13.5))]
        for f, (x, y) in keys:
            car.location = (x, y, 0); car.keyframe_insert("location", frame=f)
        car.rotation_euler = (0, 0, math.radians(90)); car.keyframe_insert("rotation_euler", frame=int(N * 0.6))
        car.rotation_euler = (0, 0, 0); car.keyframe_insert("rotation_euler", frame=int(N * 0.8))
        spin_wheels(wheels, lambda f: max(0, f - N * 0.35) * 0.5, N)
        aim(cam, (-9, -24, 4.2), (1.5, -4, 1.8), 1)
        aim(cam, (-6, -21, 3.6), (2.5, -5, 1.8), N)
    elif kind == "instalada":
        camdev.scale = (0.01, 0.01, 0.01); camdev.keyframe_insert("scale", frame=1)
        camdev.keyframe_insert("scale", frame=int(N * 0.12))
        camdev.scale = (1.25, 1.25, 1.25); camdev.keyframe_insert("scale", frame=int(N * 0.25))
        camdev.scale = (1, 1, 1); camdev.keyframe_insert("scale", frame=int(N * 0.32))
        aim(cam, (-11, -22, 3.5), (1.5, -3, 2.0), 1)
        aim(cam, (7, -21, 3.8), (1.5, -3, 2.0), N)
    elif kind == "anoitecer":
        # day -> night
        ramp, bg = world((70, 140, 230), (190, 226, 250), 1.0)
        lin = lambda c: tuple((x / 255) ** 2.2 for x in c) + (1,)
        for f, top, bot, e, st in [(1, (70, 140, 230), (190, 226, 250), 4.0, 1.0), (int(N * 0.25), (70, 140, 230), (190, 226, 250), 4.0, 1.0),
                                   (int(N * 0.55), (40, 50, 100), (240, 150, 110), 0.8, 0.6), (int(N * 0.8), (22, 36, 84), (48, 62, 110), 0.05, 0.6), (N, (22, 36, 84), (48, 62, 110), 0.05, 0.6)]:
            ramp.color_ramp.elements[1].color = lin(top); ramp.color_ramp.elements[1].keyframe_insert("color", frame=f)
            ramp.color_ramp.elements[0].color = lin(bot); ramp.color_ramp.elements[0].keyframe_insert("color", frame=f)
            bg.inputs[1].default_value = st; bg.inputs[1].keyframe_insert("default_value", frame=f)
            s.data.energy = e; s.data.keyframe_insert("energy", frame=f)
        # moon light + street lamps + windows glow on
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(60), 0, math.radians(30))); mn = bpy.context.object
        mn.data.color = (0.6, 0.7, 1.0)
        for f, e in [(1, 0), (int(N * 0.55), 0), (int(N * 0.8), 0.6)]:
            mn.data.energy = e; mn.data.keyframe_insert("energy", frame=f)
        wn = M["win_night"]; bsdf = wn.node_tree.nodes["Principled BSDF"]
        for o in house.children_recursive:
            if o.type == "MESH" and o.data.materials and o.data.materials[0] in (M["glass"], M["cream"]) and o.dimensions.z > 0.25 and o.dimensions.z < 1.2:
                pass
        # glowing windows: add emissive panes slightly in front
        glow, gbs = emat("glow", (255, 205, 120))
        box((-3.0, -3.13, 1.8), (1.25, 0.04, 1.05), glow, 0.0)
        box((0.2, -3.16, 2.3), (0.18, 0.04, 0.26), glow, 0.0)
        for f, e in [(1, 0), (int(N * 0.5), 0), (int(N * 0.65), 2.5)]:
            gbs.default_value = e; gbs.keyframe_insert("default_value", frame=f)
        for x in (-12, 12):
            cyl((x, -9.6, 2.5), 0.08, 5, M["pole"], verts=8)
            bpy.ops.object.light_add(type="POINT", location=(x, -10.2, 4.8)); pl = bpy.context.object
            pl.data.color = (1, 0.8, 0.55); pl.data.shadow_soft_size = 0.3
            for f, e in [(1, 0), (int(N * 0.55), 0), (int(N * 0.7), 900)]:
                pl.data.energy = e; pl.data.keyframe_insert("energy", frame=f)
        star, sbs = emat("star", (255, 255, 240))
        for i in range(70):
            sphere((random.uniform(-90, 90), random.uniform(70, 110), random.uniform(25, 70)), random.uniform(0.12, 0.28), star, seg=6)
        for f, e in [(1, 0), (int(N * 0.6), 0), (int(N * 0.85), 12)]:
            sbs.default_value = e; sbs.keyframe_insert("default_value", frame=f)
        bpy.ops.object.light_add(type="POINT", location=(0.2, -3.8, 2.3)); por = bpy.context.object
        por.data.color = (1, 0.8, 0.55)
        for f, e in [(1, 0), (int(N * 0.5), 0), (int(N * 0.65), 120)]:
            por.data.energy = e; por.data.keyframe_insert("energy", frame=f)
        aim(cam, (-4, -24, 3.2), (1.0, -3, 2.4), 1)
        aim(cam, (-2, -19, 2.8), (1.2, -3, 2.4), N)
    elif kind == "entrada":
        aim(cam, (-2, -24, 3.5), (2.2, -3.5, 2.0), 1)
        aim(cam, (1.0, -11, 2.6), (2.2, -3.4, 2.4), N)
    elif kind in ("feed", "feed_noite"):
        # security camera POV from the opposite side of the street looking at the gate
        cam.data.lens = 18
        aim(cam, (2.2, -17.5, 4.2), (2.2, -3, 1.0), 1)
        if night:
            world((8, 14, 36), (25, 36, 70), 0.3); s.data.energy = 0.05
            for x in (-12, 12):
                bpy.ops.object.light_add(type="POINT", location=(x, -10.2, 4.8)); pl = bpy.context.object
                pl.data.energy = 900; pl.data.color = (1, 0.8, 0.55)
    if kind != "anoitecer":
        pass

def shot_kit():
    """G: two cameras on a pedestal, turntable, gold rim lights, dark navy studio."""
    world((14, 26, 50), (10, 20, 40), 0.6)
    bpy.ops.mesh.primitive_plane_add(size=60); fl = bpy.context.object; setmat(fl, mat("floor", (16, 30, 58), rough=0.25))
    ped = cyl((0, 0, 0.3), 2.6, 0.6, mat("ped", (24, 42, 78), rough=0.3), verts=64, bev=0.05)
    cyl((0, 0, 0.61), 2.62, 0.04, M["gold"], verts=64)
    root = empty((0, 0, 0.62))
    for i, x in enumerate((-1.1, 1.1)):
        c = empty((x, 0, 0)); c.parent = root
        box((0, 0, 0.12), (0.7, 0.7, 0.12), M["camwhite"], 0.05, c)
        cyl((0, 0, 0.45), 0.08, 0.6, M["camwhite"], parent=c)
        sphere((0, 0, 0.95), 0.55, M["camwhite"], c, 32, scale=(1, 1, 0.95))
        sphere((0, -0.42, 0.98), 0.24, M["camdark"], c, 24, scale=(1, 0.6, 1))
        sphere((0, -0.52, 0.98), 0.12, M["lens"], c, 24)
        sphere((0.16, -0.48, 1.18), 0.03, M["ledg"], c, 8)
        c.rotation_euler = (0, 0, math.radians(-20 if i == 0 else 20))
    root.rotation_euler = (0, 0, math.radians(-25)); root.keyframe_insert("rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.radians(25)); root.keyframe_insert("rotation_euler", frame=N)
    _linear(root)
    bpy.ops.object.light_add(type="AREA", location=(0, -6, 6)); k = bpy.context.object; k.data.energy = 900; k.data.size = 5
    k.rotation_euler = (math.radians(45), 0, 0)
    for x in (-5, 5):
        bpy.ops.object.light_add(type="AREA", location=(x, 3, 3)); r = bpy.context.object; r.data.energy = 600; r.data.size = 2
        r.data.color = (1, 0.8, 0.45); d = Vector((0, 0, 1)) - r.location; r.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam = camera((0, 0, 0), (0, 0, 0), 50)
    aim(cam, (0, -9.5, 3.0), (0, 0, 1.0), 1)
    aim(cam, (0, -8.0, 2.6), (0, 0, 1.0), N)


CENARIOS = {"aerea": lambda **k: shot_aerial(), "estrada": lambda mood=False: shot_road(mood),
            "casa": lambda kind: shot_house(kind), "kit": lambda **k: shot_kit()}

def main(tomadas):
    global DUR, N
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    nome = argv[0]
    still = int(argv[argv.index("--still") + 1]) if "--still" in argv else None
    samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 10
    saida = argv[argv.index("--saida") + 1] if "--saida" in argv else os.path.join(os.getcwd(), "build", "shots")
    dur, cenario, params = tomadas[nome]
    DUR = dur; N = max(1, round(dur * FPS))
    CENARIOS[cenario](**params)
    res = (640, 480) if cenario == "casa" and params.get("kind", "").startswith("feed") else (RX, RY)
    r = sc.render
    r.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 2
    sc.cycles.use_adaptive_sampling = True
    r.use_persistent_data = True
    r.resolution_x, r.resolution_y = res
    r.fps = FPS
    sc.frame_start, sc.frame_end = 1, N
    sc.view_settings.view_transform = "Standard" if ANIME else "AgX"
    if ANIME:
        r.use_freestyle = True; r.line_thickness_mode = "ABSOLUTE"; r.line_thickness = 1.3
        vl = sc.view_layers[0]; vl.use_freestyle = True
        fs = vl.freestyle_settings
        ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("L")
        ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
        if ls.linestyle is None: ls.linestyle = bpy.data.linestyles.new("LS")
        ls.linestyle.color = (0.04, 0.05, 0.09); ls.linestyle.thickness = 1.6
        fs.crease_angle = math.radians(120)
    for lk in (() if ANIME else ("AgX - Punchy", "Punchy")):
        try:
            sc.view_settings.look = lk; break
        except TypeError:
            pass
    r.image_settings.file_format = "PNG"
    out = os.path.join(saida, nome) + "/"
    os.makedirs(out, exist_ok=True)
    print("BUILD", round(time.time() - T0, 1)); T1 = time.time()
    if still is not None:
        sc.frame_set(still); r.filepath = os.path.join(saida, f"teste_{nome}_{still}.png")
        bpy.ops.render.render(write_still=True); print("RENDER", round(time.time() - T1, 1))
    else:
        r.filepath = out + "####"
        bpy.ops.render.render(animation=True)

