"""Tomadas 3D do episódio 19 — O mistério das plantas (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_jardim  # noqa: F401  (registram os cenários)
import lib3d

TOMADAS = {
    "J1": (5.0, "jardim", {"kind": "descoberta"}),     # 0–5 s: três vasos no chão; ele olha para o muro
    "J2": (6.0, "jardim", {"kind": "recolhe"}),        # 5–11 s: recolhe a terra; ela chega com o café
    "J3": (6.0, "jardim", {"kind": "ideia"}),          # 11–17 s: ela sugere observar antes de acusar
    "J4": (9.0, "jardim", {"kind": "instala"}),        # 17–26 s: a câmera PTZ na quina da casa
    "J5": (9.0, "jardim", {"kind": "pov"}),            # 26–35 s: visão da câmera no app (simulação)
    "J6": (6.0, "jardim", {"kind": "gato"}),           # 35–41 s: o gato, a borboleta e o vaso
    "J7": (4.0, "jardim", {"kind": "constrangido"}),   # 41–45 s: ele sem graça, ela ri
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
