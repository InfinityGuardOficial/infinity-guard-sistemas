"""Cenários e personagens 3D dos comerciais (estende ../anime3d/lib3d.py).

Personagens fictícios, estilizados (sem rosto de pessoa real): make_person(...).
Cenários registrados em lib3d.CENARIOS: "varanda" (casa brasileira com porta, encomenda e vizinho) e
"kit_dupla" (kit de 2 câmeras de lente dupla no pedestal).
"""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anime3d"))
import lib3d as L
from lib3d import (bpy, Vector, mat, emat, box, cyl, sphere, ico, cone, empty, setmat, smooth, M, make_tree,
                   ground, world, sun, camera, aim, anime_clouds, hills, lerp, ease)

SKIN = {"morena": (176, 120, 86), "parda": (150, 98, 66), "negra": (98, 62, 42), "clara": (232, 190, 160)}
HAIR = {"preto": (28, 22, 20), "castanho": (82, 50, 30), "grisalho": (175, 172, 168)}


def key(o, prop, f, v):
    setattr(o, prop, v); o.keyframe_insert(prop, frame=max(1, int(round(f))))


def make_person(loc, skin="morena", hair="preto", style="curto", shirt=(40, 110, 170), pants=(40, 50, 70),
                height=1.0, rot=0.0):
    """Personagem estilizado de frente para -Y. Retorna dict com root, head, armL, armR, mouth, hand_l, hand_r."""
    s = height
    root = empty(loc); root.rotation_euler = (0, 0, rot); root.scale = (s, s, s)
    ms, mh = mat("skin_" + skin, SKIN[skin]), mat("hair_" + hair, HAIR[hair])
    mshirt, mpants = mat("shirt%d%d%d" % shirt, shirt), mat("pants%d%d%d" % pants, pants)
    shoe = mat("shoe", (30, 30, 36))
    for x in (-0.11, 0.11):
        cyl((x, 0, 0.47), 0.085, 0.86, mpants, verts=12, parent=root)
        box((x, -0.05, 0.05), (0.14, 0.26, 0.1), shoe, 0.04, root)
    torso = box((0, 0, 1.17), (0.48, 0.28, 0.62), mshirt, 0.12, root)
    cyl((0, 0, 1.52), 0.06, 0.12, ms, verts=12, parent=root)
    head = empty((0, 0, 1.56)); head.parent = root
    sphere((0, 0, 0.16), 0.17, ms, head, 24, scale=(1, 0.95, 1.08))
    # hair
    sphere((0, 0.02, 0.21), 0.178, mh, head, 24, scale=(1.03, 1.0, 0.8))
    if style == "longo":
        box((0, 0.1, 0.0), (0.36, 0.14, 0.46), mh, 0.06, head)
        for x in (-0.15, 0.15):  # mechas dos lados, até o ombro
            box((x, -0.02, -0.02), (0.07, 0.2, 0.42), mh, 0.03, head)
    elif style == "coque":
        sphere((0, 0.14, 0.3), 0.08, mh, head, 16)
    # face: anime eyes, brows, mouth
    eye = mat("eye", (25, 25, 30), rough=0.2); white = mat("eyewhite", (255, 255, 255), emit=1.5)
    for x in (-0.06, 0.06):
        sphere((x, -0.155, 0.17), 0.028, eye, head, 12, scale=(0.8, 0.4, 1.25))
        sphere((x + 0.01, -0.168, 0.185), 0.008, white, head, 8)
        box((x, -0.16, 0.235), (0.06, 0.01, 0.012), mh, 0.0, head)
    mouth = sphere((0, -0.158, 0.075), 0.022, mat("mouth", (120, 40, 40)), head, 12, scale=(1.3, 0.3, 0.35))
    arms = []
    for side in (-1, 1):
        pv = empty((side * 0.3, 0, 1.4)); pv.parent = root
        sphere((0, 0, 0), 0.085, mshirt, pv, 12)
        cyl((0, 0, -0.2), 0.072, 0.36, mshirt, verts=12, parent=pv)
        cyl((0, 0, -0.44), 0.058, 0.2, ms, verts=12, parent=pv)
        hand = sphere((0, 0, -0.56), 0.065, ms, pv, 12)
        arms.append((pv, hand))
    return {"root": root, "head": head, "armL": arms[0][0], "armR": arms[1][0], "mouth": mouth,
            "hand_l": arms[0][1], "hand_r": arms[1][1]}


def talk(p, f0, f1, fps=12):
    """boca abrindo e fechando entre os quadros f0 e f1"""
    m = p["mouth"]
    for f in range(int(f0), int(f1) + 1, 1):
        k = 0.35 + (0.9 if (f - f0) % 3 == 1 else 0.25 if (f - f0) % 3 == 2 else 0.5)
        m.scale = (1.3, 0.3, k); m.keyframe_insert("scale", frame=f)
    m.scale = (1.3, 0.3, 0.35); m.keyframe_insert("scale", frame=int(f1) + 1)


def walk(p, f0, f1, a, b, arms=True):
    """anda do ponto a ao ponto b (x, y); balança os braços se não estiver carregando nada"""
    r = p["root"]
    key(r, "location", f0, (a[0], a[1], r.location.z)); key(r, "location", f1, (b[0], b[1], r.location.z))
    if not arms: return
    for f in range(int(f0), int(f1) + 1, 2):
        sw = 0.5 * math.sin((f - f0) * 1.3)
        key(p["armL"], "rotation_euler", f, (sw, 0, 0)); key(p["armR"], "rotation_euler", f, (-sw, 0, 0))
    key(p["armL"], "rotation_euler", f1 + 2, (0, 0, 0)); key(p["armR"], "rotation_euler", f1 + 2, (0, 0, 0))


def hold(p, f, on=True):
    """braços para frente segurando algo"""
    v = (-1.15, 0, 0.12) if on else (0, 0, 0)
    key(p["armL"], "rotation_euler", f, (v[0], 0, v[2])); key(p["armR"], "rotation_euler", f, (v[0], 0, -v[2]))


def look(p, f, down=0.0, turn=0.0):
    key(p["head"], "rotation_euler", f, (down, 0, turn))


def package(loc, label=True):
    root = empty(loc)
    card = mat("papelao", (196, 150, 98))
    box((0, 0, 0.16), (0.46, 0.34, 0.32), card, 0.02, root)
    box((0, 0, 0.32), (0.47, 0.08, 0.005), mat("fita", (210, 190, 150), rough=0.2), 0.0, root)
    if label:
        box((0.08, -0.171, 0.17), (0.2, 0.004, 0.13), mat("etiqueta", (250, 250, 245)), 0.0, root)
        for i in range(3):
            box((0.06, -0.174, 0.21 - i * 0.035), (0.14 - i * 0.03, 0.002, 0.012), mat("tinta", (40, 40, 50)), 0.0, root)
    return root


def dual_cam(loc, parent=None, s=1.0, rot=(0, 0, 0)):
    """câmera Wi-Fi de lente dupla (ilustrativa): corpo branco, duas lentes empilhadas, suporte de parede"""
    root = empty(loc); root.rotation_euler = rot; root.scale = (s, s, s)
    if parent: root.parent = parent
    w = M["camwhite"]
    box((0, 0, 0), (0.22, 0.2, 0.46), w, 0.08, root)
    for z in (0.11, -0.1):
        cyl((0, -0.105, z), 0.07, 0.03, M["camdark"], rot=(math.pi / 2, 0, 0), parent=root)
        cyl((0, -0.12, z), 0.04, 0.02, M["lens"], rot=(math.pi / 2, 0, 0), parent=root)
    sphere((0.07, -0.105, 0.2), 0.012, M["ledg"], root, 8)
    box((0, 0.17, 0.0), (0.08, 0.16, 0.08), w, 0.02, root)
    return root


def fov_cone(apex, target, spread=2.4, strength=0.35):
    """volume de luz que mostra o campo de visão da câmera (só a entrada)"""
    m, s = emat("fov", (120, 200, 255), strength)
    d = Vector(target) - Vector(apex); L_ = d.length
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=spread, radius2=0.02, depth=L_,
                                    location=(Vector(apex) + d / 2))
    c = bpy.context.object; setmat(c, m)
    c.rotation_euler = (-d).to_track_quat("Z", "Y").to_euler()
    c.scale = (1.0, 0.62, 1.0)
    return c, s


# ---------------- cenário: varanda brasileira ----------------
def varanda(kind="porta_abre"):
    """Casa térrea de bairro com varanda, porta, grade e portão; casa do vizinho à direita (x=+9)."""
    N, FPS = L.N, L.FPS
    ground(400, "grass")
    pal = {"muro": mat("muroamarelo", (236, 200, 120)), "muro2": mat("muroverde", (150, 196, 170)),
           "piso": mat("cer_verm", (168, 72, 52)), "piso2": mat("cer_verm2", (150, 62, 46)),
           "porta": mat("porta_mad", (120, 78, 46)), "grade": mat("grade", (40, 44, 52)),
           "telha": mat("telha", (186, 92, 52)), "calcada": mat("calcada", (200, 196, 186))}
    # rua e calçada
    box((0, -9.5, 0.02), (80, 7, 0.04), M["road"], 0.0)
    box((0, -5.2, 0.07), (80, 1.8, 0.12), pal["calcada"], 0.0)
    for x in range(-40, 40, 6): box((x, -9.5, 0.05), (2.4, 0.18, 0.02), M["line"], 0.0)

    def casa(x0, muro, numero_cor):
        # fachada (porta em x0, varanda até y=-1.9, muro com portão em y=-4.2)
        box((x0, 0.5, 1.5), (7.0, 3.0, 3.0), muro, 0.04)
        box((x0, -0.2, 3.15), (7.6, 4.6, 0.25), pal["telha"], 0.08)
        for i in range(12):
            box((x0 - 3.6 + i * 0.66, -0.2, 3.3), (0.3, 4.6, 0.12), pal["telha"], 0.06)
        for i in range(6):          # piso cerâmico quadriculado
            for j in range(3):
                box((x0 - 2.5 + i * 1.0, -0.6 - j * 1.0 - 0.0, 0.04), (0.98, 0.98, 0.06), pal["piso"] if (i + j) % 2 else pal["piso2"], 0.0)
        for xx in (x0 - 3.2, x0 + 3.2):
            box((xx, -2.2, 1.55), (0.25, 0.25, 3.1), pal["calcada"], 0.03)   # pilares da varanda
        # janela com grade
        box((x0 + 2.0, -1.02, 1.6), (1.4, 0.06, 1.1), M["glass"], 0.02)
        for k in range(6):
            box((x0 + 1.4 + k * 0.24, -1.08, 1.6), (0.04, 0.04, 1.2), pal["grade"], 0.0)
        # muro baixo + portão de grade
        for xx, w in ((x0 - 2.4, 2.4), (x0 + 2.4, 2.4)):
            box((xx, -4.2, 0.6), (w, 0.25, 1.2), muro, 0.04)
        for k in range(10):
            box((x0 - 1.08 + k * 0.24, -4.2, 0.85), (0.05, 0.05, 1.7), pal["grade"], 0.0)
        box((x0, -4.2, 1.72), (2.5, 0.07, 0.07), pal["grade"], 0.0)
        box((x0 + 3.0, -4.34, 1.0), (0.3, 0.02, 0.2), mat("numplaca", numero_cor), 0.01)
        for xx in (x0 - 2.8, x0 + 2.8):          # vasos de planta
            cyl((xx, -1.6, 0.25), 0.28, 0.5, mat("vaso", (170, 90, 60)), verts=16)
            ico((xx, -1.6, 0.85), 0.45, M["leaf"], 1, scale=(1, 1, 1.3))
        # porta com dobradiça
        box((x0, -1.0, 1.1), (1.2, 0.1, 2.25), mat("batente", (240, 236, 228)), 0.02)
        hinge = empty((x0 - 0.5, -1.06, 0.0))
        box((0.5, 0, 1.08), (1.0, 0.08, 2.1), pal["porta"], 0.03, hinge)
        sphere((0.88, -0.06, 1.05), 0.04, M["gold"], hinge, 10)
        box((x0, -1.65, 0.075), (1.1, 0.6, 0.03), mat("tapete", (120, 60, 50)), 0.0)
        return hinge

    hinge = casa(0, pal["muro"], (40, 90, 160))
    hinge2 = casa(9, pal["muro2"], (160, 60, 50))
    for x in (-12, 4.5, 13.5, 20):
        make_tree((x, 3.5, 0), 1.1)
    hills(0, 90, 10, 200)
    world((70, 140, 230), (190, 226, 250), 1.0)
    anime_clouds(0, 140, 6, 260, (28, 50))
    s = sun((math.radians(55), 0, math.radians(-30)), 3.6, (1, 0.95, 0.85))
    bpy.ops.object.light_add(type="POINT", location=(0, -1.8, 2.8)); porch = bpy.context.object
    porch.data.energy = 0; porch.data.color = (1, 0.82, 0.55)
    cam = camera((0, 0, 0), (0, 0, 0), 35)
    ana = make_person((0.0, -0.4, 0.07), skin="parda", hair="preto", style="longo", shirt=(230, 120, 90), pants=(60, 70, 110))
    pkg = package((0.15, -1.75, 0.09))
    f = lambda sec: 1 + sec * FPS

    if kind == "porta_abre":
        key(hinge, "rotation_euler", 1, (0, 0, 0)); key(hinge, "rotation_euler", f(0.6), (0, 0, 0))
        key(hinge, "rotation_euler", f(1.6), (0, 0, math.radians(-100)))
        key(ana["root"], "location", 1, (0, 0.2, 0.07)); key(ana["root"], "location", f(1.4), (0, 0.2, 0.07))
        key(ana["root"], "location", f(2.4), (0, -1.0, 0.07))
        look(ana, 1, 0, 0); look(ana, f(2.6), 0.0, 0); look(ana, f(3.2), 0.45, 0)
        aim(cam, (1.3, -3.6, 0.7), (0.1, -1.5, 0.75), 1)
        aim(cam, (0.9, -3.3, 1.1), (0.0, -1.2, 1.25), N)
    elif kind == "etiqueta":
        marcos = make_person((0.0, 0.4, 0.07), skin="negra", hair="preto", style="curto", shirt=(60, 120, 90), pants=(50, 50, 60), height=1.06)
        hinge.rotation_euler = (0, 0, math.radians(-100))
        ana["root"].location = (0.65, -1.45, 0.07)
        pkg.parent = ana["root"]; pkg.location = (0, -0.42, 0.95)
        hold(ana, 1, True); look(ana, 1, 0.5, 0)
        look(ana, f(3.6), 0.5, 0); look(ana, f(4.3), 0.1, math.radians(35))
        key(marcos["root"], "location", 1, (-0.2, 0.6, 0.07)); key(marcos["root"], "location", f(3.0), (-0.2, 0.6, 0.07))
        key(marcos["root"], "location", f(4.2), (-0.05, -0.95, 0.07))
        look(marcos, f(4.2), 0.05, math.radians(-25))
        talk(ana, f(0.8), f(3.2)); talk(marcos, f(4.4), f(8.0))
        key(marcos["armR"], "rotation_euler", f(5.0), (0, 0, 0)); key(marcos["armR"], "rotation_euler", f(5.6), (-0.9, 0, -0.3))
        key(marcos["armR"], "rotation_euler", f(7.4), (-0.9, 0, -0.3)); key(marcos["armR"], "rotation_euler", f(8.0), (0, 0, 0))
        aim(cam, (2.0, -4.3, 1.55), (0.3, -1.2, 1.35), 1)
        aim(cam, (1.6, -3.9, 1.5), (0.25, -1.2, 1.4), N)
    elif kind == "campo":
        ana["root"].location = (30, 30, -10)   # fora de cena
        pkg.location = (0.15, -1.75, 0.09)
        camdev = dual_cam((0.9, -1.12, 2.55), rot=(math.radians(-28), 0, math.radians(8)))
        camdev.scale = (0.01, 0.01, 0.01); camdev.keyframe_insert("scale", frame=1)
        camdev.keyframe_insert("scale", frame=int(f(0.6)))
        camdev.scale = (1.15, 1.15, 1.15); camdev.keyframe_insert("scale", frame=int(f(1.2)))
        camdev.scale = (1, 1, 1); camdev.keyframe_insert("scale", frame=int(f(1.5)))
        cone_o, cs = fov_cone((0.9, -1.35, 2.45), (0.3, -3.4, 0.1), spread=1.5, strength=0.0)
        for t_, e in [(0, 0), (1.8, 0), (2.8, 0.18)]:
            cs.default_value = e; cs.keyframe_insert("default_value", frame=int(f(t_)))
        # dia -> noite a partir de 7,5 s
        ramp_nodes = [n for n in bpy.context.scene.world.node_tree.nodes if n.type == "VALTORGB"]
        ramp = ramp_nodes[0]; bg = bpy.context.scene.world.node_tree.nodes["Background"]
        lin = lambda c: tuple((x / 255) ** 2.2 for x in c) + (1,)
        for t_, top, bot, e, st in [(0, (70, 140, 230), (190, 226, 250), 3.6, 1.0), (7.5, (70, 140, 230), (190, 226, 250), 3.6, 1.0),
                                    (9.5, (22, 36, 84), (48, 62, 110), 0.04, 0.6), (13, (22, 36, 84), (48, 62, 110), 0.04, 0.6)]:
            fr = int(f(t_))
            ramp.color_ramp.elements[1].color = lin(top); ramp.color_ramp.elements[1].keyframe_insert("color", frame=fr)
            ramp.color_ramp.elements[0].color = lin(bot); ramp.color_ramp.elements[0].keyframe_insert("color", frame=fr)
            bg.inputs[1].default_value = st; bg.inputs[1].keyframe_insert("default_value", frame=fr)
            s.data.energy = e; s.data.keyframe_insert("energy", frame=fr)
        for t_, e in [(0, 0), (8.5, 0), (9.5, 160)]:
            porch.data.energy = e; porch.data.keyframe_insert("energy", frame=int(f(t_)))
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(60), 0, math.radians(30))); mn = bpy.context.object
        mn.data.color = (0.6, 0.7, 1.0)
        for t_, e in [(0, 0), (8.5, 0), (10, 0.5)]:
            mn.data.energy = e; mn.data.keyframe_insert("energy", frame=int(f(t_)))
        aim(cam, (-5.0, -11.0, 4.6), (0.5, -1.8, 1.4), 1)
        aim(cam, (-3.2, -9.6, 4.2), (0.5, -1.8, 1.4), int(f(7.0)))
        aim(cam, (-2.8, -9.2, 4.0), (0.5, -1.9, 1.3), N)
    elif kind == "entrega":
        joaquim = make_person((9.15, -4.95, 0.13), skin="clara", hair="grisalho", style="curto", shirt=(200, 200, 215), pants=(90, 80, 70), rot=math.radians(-90))
        key(hinge2, "rotation_euler", 1, (0, 0, 0))
        pkg.parent = ana["root"]; pkg.location = (0, -0.42, 0.95)
        hold(ana, 1, True)
        walk(ana, 1, f(3.0), (1.5, -4.95), (8.1, -4.95), arms=False)
        key(ana["root"], "rotation_euler", 1, (0, 0, math.radians(90))); key(ana["root"], "rotation_euler", f(3.0), (0, 0, math.radians(90)))
        hold(ana, f(3.1), True)
        talk(ana, f(1.0), f(3.2))
        look(joaquim, f(3.4), 0.1, 0)
        hold(joaquim, f(3.6), False); hold(joaquim, f(4.4), True)
        talk(joaquim, f(4.4), f(6.4))
        # a caixa passa para o vizinho
        pkg2 = package((0, 0, 0))
        pkg2.parent = joaquim["root"]; pkg2.location = (0, -0.42, 0.95)
        pkg2.scale = (0.001, 0.001, 0.001); pkg2.keyframe_insert("scale", frame=int(f(4.5)))
        pkg2.scale = (1, 1, 1); pkg2.keyframe_insert("scale", frame=int(f(4.6)))
        pkg.scale = (1, 1, 1); pkg.keyframe_insert("scale", frame=int(f(4.5)))
        pkg.scale = (0.001, 0.001, 0.001); pkg.keyframe_insert("scale", frame=int(f(4.6)))
        hold(ana, f(4.6), True); hold(ana, f(5.2), False)
        key(ana["armR"], "rotation_euler", f(6.0), (0, 0, 0)); key(ana["armR"], "rotation_euler", f(6.5), (-2.6, 0, -0.2))
        key(ana["armR"], "rotation_euler", f(7.6), (-2.6, 0, -0.2))
        aim(cam, (3.5, -10.5, 1.9), (4.5, -4.9, 1.2), 1)
        aim(cam, (8.4, -9.0, 1.7), (8.6, -4.9, 1.25), int(f(3.4)))
        aim(cam, (8.6, -8.2, 1.65), (8.6, -4.9, 1.3), N)
    return cam


def kit_dupla():
    """kit com 2 câmeras de lente dupla girando no pedestal (fundo azul-marinho)"""
    N = L.N
    world((14, 26, 50), (10, 20, 40), 0.6)
    bpy.ops.mesh.primitive_plane_add(size=60); fl = bpy.context.object; setmat(fl, mat("floor", (16, 30, 58), rough=0.25))
    cyl((0, 0, 0.3), 2.6, 0.6, mat("ped", (24, 42, 78), rough=0.3), verts=64, bev=0.05)
    cyl((0, 0, 0.61), 2.62, 0.04, M["gold"], verts=64)
    root = empty((0, 0, 0.62))
    for i, x in enumerate((-1.0, 1.0)):
        c = dual_cam((x, 0, 1.0), parent=root, s=2.2, rot=(0, 0, math.radians(-15 if i == 0 else 15)))
        cyl((x, 0.25, 0.25), 0.06, 0.5, M["camwhite"], parent=root)
    root.rotation_euler = (0, 0, math.radians(-30)); root.keyframe_insert("rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.radians(30)); root.keyframe_insert("rotation_euler", frame=N)
    L._linear(root)
    bpy.ops.object.light_add(type="AREA", location=(0, -6, 6)); k = bpy.context.object; k.data.energy = 500; k.data.size = 5
    k.rotation_euler = (math.radians(45), 0, 0)
    for x in (-5, 5):
        bpy.ops.object.light_add(type="AREA", location=(x, 3, 3)); r = bpy.context.object; r.data.energy = 250; r.data.size = 2
        r.data.color = (1, 0.8, 0.45); d = Vector((0, 0, 1)) - r.location; r.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam = camera((0, 0, 0), (0, 0, 0), 50)
    aim(cam, (0, -8.0, 2.6), (0, 0, 2.0), 1)
    aim(cam, (0, -7.0, 2.4), (0, 0, 2.0), N)


L.CENARIOS["varanda"] = lambda kind="porta_abre": varanda(kind)
L.CENARIOS["kit_dupla"] = lambda **k: kit_dupla()
