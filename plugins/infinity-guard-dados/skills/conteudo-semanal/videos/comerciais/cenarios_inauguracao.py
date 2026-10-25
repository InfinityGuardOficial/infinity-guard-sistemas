"""Cenário "inauguracao": a loja de bairro de cenarios_loja.py no dia da inauguração (balões navy e dourado,
faixa, laço na porta), com mãe e filha fictícias, e a câmera dome branca modelada a partir da foto do produto
(base redonda, globo, face preta com janela da lente e dois LEDs). Também "dome_estudio" (produto girando).
"""
import math, random
import lib3d as L
from lib3d import bpy, Vector, mat, emat, box, cyl, sphere, empty, setmat, M, camera, world
import cenarios_loja as CL
from cenarios import make_person, talk, hold, look, key, vida, aim_dof, fov_cone

NAVY_IG, GOLD_IG = (14, 26, 43), (201, 162, 77)


def dome(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, parent=None):
    """câmera dome (turret) branca, montada para baixo: a base fica em z=0 e o globo abaixo dela"""
    r = empty(loc); r.rotation_euler = rot; r.scale = (s, s, s)
    if parent: r.parent = parent
    branco = mat("dome_branco", (246, 246, 244), rough=0.35)
    preto = mat("dome_preto", (14, 14, 18), rough=0.15)
    cyl((0, 0, -0.008), 0.054, 0.0165, branco, verts=64, parent=r, bev=0.004)
    sphere((0, 0, -0.03), 0.047, branco, r, 40, scale=(1, 1, 0.75))
    face = empty((0, 0, -0.044)); face.parent = r; face.rotation_euler = (math.radians(40), 0, 0)  # lente para a frente e para baixo
    sphere((0, 0, 0), 0.04, branco, face, 40)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.031, minor_radius=0.004, location=(0, -0.037, 0), rotation=(math.pi / 2, 0, 0))
    t = bpy.context.object; setmat(t, branco); t.parent = face
    cyl((0, -0.039, 0), 0.028, 0.012, preto, rot=(math.pi / 2, 0, 0), verts=48, parent=face)
    box((0, -0.0455, 0.007), (0.03, 0.002, 0.016), mat("dome_janela", (36, 36, 44), rough=0.05), 0.002, face)
    sphere((0.002, -0.047, 0.008), 0.0045, mat("dome_lente", (40, 10, 20), rough=0.05), face, 16)
    led, led_s = emat("dome_led", (255, 214, 140), 1.2)
    for x in (-0.007, 0.007):
        cyl((x, -0.0455, -0.009), 0.0048, 0.003, mat("dome_led_aro", (200, 160, 90), rough=0.3), rot=(math.pi / 2, 0, 0), verts=20, parent=face)
        cyl((x, -0.047, -0.009), 0.0028, 0.002, led, rot=(math.pi / 2, 0, 0), verts=16, parent=face)
    sphere((0, -0.033, -0.031), 0.0012, preto, face, 8)
    return r, led_s


def caixa_presente(loc, parent=None):
    g = empty(loc)
    if parent: g.parent = parent
    navy = mat("presente_navy", NAVY_IG, rough=0.5); ouro = mat("presente_ouro", GOLD_IG, rough=0.35)
    box((0, 0, 0.07), (0.26, 0.26, 0.14), navy, 0.006, g)
    sphere((0, 0, 0.12), 0.09, mat("papel_seda", (236, 220, 180), rough=0.9), g, 16, scale=(1.3, 1.3, 0.4))
    tampa = empty((0, 0.13, 0.142)); tampa.parent = g
    box((0, -0.13, 0.008), (0.27, 0.27, 0.018), navy, 0.004, tampa)
    box((0, -0.13, 0.019), (0.05, 0.272, 0.004), ouro, 0.0, tampa); box((0, -0.13, 0.019), (0.272, 0.05, 0.004), ouro, 0.0, tampa)
    bilhete = box((0.06, -0.07, 0.022), (0.09, 0.06, 0.003), mat("bilhete", (250, 246, 236)), 0.001, tampa)
    return g, tampa


def baloes(cx, cy, z, n=7, seed=1):
    rnd = random.Random(seed)
    cores = [mat("balao_navy", NAVY_IG, rough=0.25), mat("balao_ouro", GOLD_IG, rough=0.25), mat("balao_branco", (245, 242, 236), rough=0.25)]
    for i in range(n):
        x, y = cx + rnd.uniform(-0.35, 0.35), cy + rnd.uniform(-0.2, 0.2); zz = z + rnd.uniform(-0.25, 0.25)
        sphere((x, y, zz), 0.16, cores[i % 3], seg=20, scale=(1, 1, 1.18))
        cyl((x, y, zz - 0.5), 0.003, 0.7, mat("fita_balao", (220, 220, 220)), verts=4)


def inauguracao(kind):
    N, FPS = L.N, L.FPS
    f = lambda sec: 1 + sec * FPS
    CL.NOME_LOJA = "Ateliê da Bia"
    noite = kind == "flashback"
    CL.loja("vazio")
    # decoração da inauguração
    if not noite:
        baloes(-3.4, 0.7, 3.4, 8, 1); baloes(3.6, 0.7, 3.4, 8, 2); baloes(-2.6, 6.6, 3.4, 6, 3)
        ouro = mat("faixa_ouro", GOLD_IG, rough=0.4)
        box((0, 0.35, 3.3), (3.2, 0.03, 0.42), mat("faixa_navy", NAVY_IG), 0.01)
        CL.texto3d("INAUGURAÇÃO", (0, 0.32, 3.24), 0.22, ouro, rot=(math.pi / 2, 0, 0))
        for x in (-2.0, 1.0):
            box((x, -0.14, 1.2), (0.08, 0.04, 1.0), ouro, 0.0, rot=(0, math.radians(25 if x < 0 else -25), 0))
    else:  # véspera: caixas no chão e luz baixa
        for i, (x, y) in enumerate(((-1.6, 2.0), (-1.2, 2.5), (0.6, 5.2), (1.0, 5.6))):
            box((x, y, 0.2), (0.5, 0.4, 0.36), mat("caixa_papelao", (196, 150, 98)), 0.02, rot=(0, 0, 0.3 * i))
        for o in bpy.data.objects:
            if o.type == "LIGHT" and o.data.type == "AREA": o.data.energy *= 0.25
        bpy.ops.object.light_add(type="POINT", location=(-0.6, 2.8, 2.6)); lp = bpy.context.object
        lp.data.energy = 120; lp.data.color = (1, 0.72, 0.42)
    # personagens fictícios: Bia (a filha, dona da loja) e Dona Lúcia (a mãe)
    bia = make_person((30, 30, -20), skin="parda", hair="preto", style="longo", shirt=(232, 120, 96), pants=(40, 46, 70))
    mae = make_person((30, 30, -20), skin="parda", hair="grisalho", style="coque", shirt=(150, 120, 190), pants=(70, 64, 80), height=0.96)
    cliente = make_person((30, 30, -20), skin="clara", hair="castanho", style="curto", shirt=(90, 150, 120), pants=(60, 60, 70))
    for i, p in enumerate((bia, mae, cliente)): vida(p, N, i + 7)
    cam = bpy.context.scene.camera
    lens = lambda mm: setattr(cam.data, "lens", mm)
    bal = (2.55, 2.0, 1.06)  # tampo do balcão

    if kind == "abre":           # 0–5 s: ela abre a caixa no balcão, o bilhete na tampa
        bia["root"].location = (3.35, 2.0, 0.07); bia["root"].rotation_euler = (0, 0, math.radians(-90))
        g, tampa = caixa_presente((bal[0] - 0.15, bal[1], bal[2]))
        hold(bia, 1, True)
        key(tampa, "rotation_euler", f(0.8), (0, 0, 0)); key(tampa, "rotation_euler", f(1.8), (math.radians(-115), 0, 0))
        look(bia, 1, 0.35, 0); look(bia, f(2.0), 0.5, 0)
        aim_dof(cam, (1.2, 0.6, 1.7), (2.6, 2.0, 1.3), 1, 2.4)
        aim_dof(cam, (1.5, 0.9, 1.62), (2.6, 2.0, 1.3), N, 2.4)
        lens(30)
    elif kind == "flashback":    # 5–11 s: véspera, ela arruma as prateleiras de noite
        bia["root"].location = (-0.6, 3.0, 0.07); bia["root"].rotation_euler = (0, 0, math.radians(180))
        for i in range(3):
            t0 = 0.3 + i * 1.8
            key(bia["armR"], "rotation_euler", f(t0), (0, 0, 0)); key(bia["armR"], "rotation_euler", f(t0 + 0.7), (-2.0, 0, 0.1))
            key(bia["armR"], "rotation_euler", f(t0 + 1.4), (0, 0, 0))
        look(bia, f(0.2), -0.15, 0); look(bia, f(3.5), 0.2, math.radians(15))
        aim_dof(cam, (0.9, 0.6, 1.6), (-0.6, 3.2, 1.4), 1, 2.8)
        aim_dof(cam, (0.6, 1.0, 1.55), (-0.6, 3.2, 1.45), N, 2.8)
        lens(28)
    elif kind == "bilhete":      # 11–17 s: close dela lendo o bilhete; reconhece a letra da mãe; uma lágrima
        bia["root"].location = (3.35, 2.0, 0.07); bia["root"].rotation_euler = (0, 0, math.radians(-90))
        hold(bia, 1, True); key(bia["armR"], "rotation_euler", 1, (-1.4, 0, -0.1))
        look(bia, 1, 0.3, 0); look(bia, f(3.0), 0.3, math.radians(-6)); look(bia, f(5.0), 0.15, math.radians(-10))
        lag, lag_s = emat("lagrima", (180, 220, 255), 0.0)
        gota = sphere((0.075, -0.15, 0.13), 0.009, lag, bia["head"], 10, scale=(0.8, 0.8, 1.2))
        key(gota, "location", f(2.6), (0.075, -0.15, 0.13)); key(gota, "location", f(4.6), (0.08, -0.13, 0.04))
        for t_, e in ((0, 0), (2.5, 0), (2.8, 1.6), (4.6, 1.6), (4.8, 0)):
            lag_s.default_value = e; lag_s.keyframe_insert("default_value", frame=int(f(t_)))
        aim_dof(cam, (2.35, 1.95, 1.62), (3.33, 1.95, 1.62), 1, 1.8)
        aim_dof(cam, (2.5, 1.95, 1.63), (3.33, 1.95, 1.62), N, 1.8)
        lens(50)
    elif kind == "revela":       # 17–24 s: dentro da caixa, a câmera dome sobre o papel de seda
        g, tampa = caixa_presente((bal[0] - 0.15, bal[1], bal[2])); tampa.rotation_euler = (math.radians(-115), 0, 0)
        d, _ = dome((bal[0] - 0.15, bal[1], bal[2] + 0.17), rot=(math.pi, 0, math.radians(131)), s=1.0)  # deitada na base, lente para a câmera
        aim_dof(cam, (bal[0] - 0.55, bal[1] - 0.35, bal[2] + 0.42), (bal[0] - 0.15, bal[1], bal[2] + 0.17), 1, 1.6)
        aim_dof(cam, (bal[0] - 0.42, bal[1] - 0.25, bal[2] + 0.32), (bal[0] - 0.15, bal[1], bal[2] + 0.17), N, 1.6)
        lens(60)
    elif kind == "abraco":       # 24–31 s: a mãe chega e as duas se abraçam
        bia["root"].location = (1.9, 1.6, 0.07); bia["root"].rotation_euler = (0, 0, math.radians(-90))
        mae["root"].location = (0.6, 1.4, 0.07); mae["root"].rotation_euler = (0, 0, math.radians(90))
        key(mae["root"], "location", 1, (0.6, 1.4, 0.07)); key(mae["root"], "location", f(1.6), (1.45, 1.6, 0.07))
        key(bia["root"], "rotation_euler", 1, (0, 0, math.radians(-30))); key(bia["root"], "rotation_euler", f(1.0), (0, 0, math.radians(-90)))
        for p, sgn in ((bia, 1), (mae, -1)):
            key(p["armL"], "rotation_euler", f(1.6), (0, 0, 0)); key(p["armR"], "rotation_euler", f(1.6), (0, 0, 0))
            key(p["armL"], "rotation_euler", f(2.4), (-1.35, 0, 0.75)); key(p["armR"], "rotation_euler", f(2.4), (-1.35, 0, -0.75))
            look(p, f(2.4), 0.12, math.radians(12 * sgn))
            p["mouth"].scale = (1.8, 0.3, 0.42); p["mouth"].keyframe_insert("scale", frame=int(f(2.0)))
        aim_dof(cam, (1.25, 0.25, 1.6), (1.65, 1.6, 1.45), 1, 2.2)
        aim_dof(cam, (1.35, 0.45, 1.58), (1.65, 1.6, 1.45), N, 2.2)
        lens(40)
    elif kind == "instalada":    # 37–45 s: dome no teto, no canto do balcão, mirando caixa e entrada
        d, led = dome((3.75, 3.6, 4.2), rot=(0, 0, math.radians(-52)), s=1.6)  # canto do fundo, mirando caixa e entrada
        cone_o, cs = fov_cone((3.62, 3.45, 4.0), (1.4, 1.0, 0.1), spread=1.5, strength=0.0)
        for t_, e in ((0, 0), (1.5, 0), (2.5, 0.16)):
            cs.default_value = e; cs.keyframe_insert("default_value", frame=int(f(t_)))
        bia["root"].location = (3.35, 2.0, 0.07); bia["root"].rotation_euler = (0, 0, math.radians(-90))
        cliente["root"].location = (1.75, 2.0, 0.07); cliente["root"].rotation_euler = (0, 0, math.radians(90))
        talk(bia, f(3.0), f(5.0)); talk(cliente, f(5.4), f(6.4))
        aim_dof(cam, (3.1, 2.95, 3.68), (3.72, 3.56, 4.1), 1, 1.8)
        aim_dof(cam, (0.4, -0.2, 2.5), (2.6, 2.0, 1.5), int(f(3.0)), 4.0)
        aim_dof(cam, (0.2, -0.3, 2.45), (2.6, 2.0, 1.5), N, 4.0)
        lens(26)
    return cam


def dome_estudio():
    """produto girando em fundo azul-marinho com aro dourado (como a foto: base em cima)"""
    N = L.N
    world(NAVY_IG, (8, 16, 30), 0.6)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.2)); fl = bpy.context.object; setmat(fl, mat("floor_navy", (16, 30, 58), rough=0.3))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.11, minor_radius=0.003, location=(0, 0, -0.09))
    t = bpy.context.object; setmat(t, mat("aro_ouro", GOLD_IG, rough=0.3))
    d, _ = dome((0, 0, 0.0), rot=(0, 0, math.radians(-35)), s=1.0)
    key(d, "rotation_euler", 1, (0, 0, math.radians(-35))); key(d, "rotation_euler", N, (0, 0, math.radians(35)))
    L._linear(d)
    bpy.ops.object.light_add(type="AREA", location=(0, -0.6, 0.5)); k = bpy.context.object; k.data.energy = 18; k.data.size = 0.6
    k.rotation_euler = (math.radians(50), 0, 0)
    for x in (-0.5, 0.5):
        bpy.ops.object.light_add(type="AREA", location=(x, 0.3, 0.2)); r = bpy.context.object; r.data.energy = 8; r.data.size = 0.2
        r.data.color = (1, 0.8, 0.45); dd = Vector((0, 0, -0.04)) - r.location; r.rotation_euler = dd.to_track_quat("-Z", "Y").to_euler()
    cam = camera((0, 0, 0), (0, 0, 0), 60)
    aim_dof(cam, (0, -0.42, -0.02), (0, 0, -0.04), 1, 3.2)
    aim_dof(cam, (0, -0.36, -0.03), (0, 0, -0.04), N, 3.2)


L.CENARIOS["inauguracao"] = lambda kind="abre": inauguracao(kind)
L.CENARIOS["dome_estudio"] = lambda **k: dome_estudio()
