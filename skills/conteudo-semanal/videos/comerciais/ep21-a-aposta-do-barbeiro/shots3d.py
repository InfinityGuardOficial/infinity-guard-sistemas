"""Tomadas 3D do episódio 21 — A aposta do barbeiro (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_barbearia  # noqa: F401  (registra "barbearia")
import lib3d

TOMADAS = {
    "R1": (5.0, "barbearia", {"kind": "aposta"}),    # 0–5 s: os dois discutem diante da cadeira deslocada
    "R2": (6.0, "barbearia", {"kind": "manha"}),     # 5–11 s: de manhã, a cadeira fora do lugar outra vez
    "R3": (7.0, "barbearia", {"kind": "insiste"}),   # 11–18 s: Toninho jura que não mexeu
    "R4": (3.0, "barbearia", {"kind": "camera"}),    # 18–21 s: a câmera bullet na parede
    "R4B": (3.0, "barbearia", {"kind": "balcao"}),   # 21–24 s: Lucas vai ao monitor do balcão
    "R5": (7.0, "barbearia", {"kind": "pov"}),       # 24–31 s: imagem ao vivo: Toninho empurra a cadeira varrendo
    "R6": (5.0, "barbearia", {"kind": "flagra"}),    # 31–36 s: Lucas se vira e flagra Toninho
    "R7": (6.0, "barbearia", {"kind": "risos"}),     # 36–42 s: os dois riem; a aposta é paga
    "R8": (4.0, "barbearia", {"kind": "final"}),     # 42–46 s: a cadeira volta ao lugar; plano aberto com a dome
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
