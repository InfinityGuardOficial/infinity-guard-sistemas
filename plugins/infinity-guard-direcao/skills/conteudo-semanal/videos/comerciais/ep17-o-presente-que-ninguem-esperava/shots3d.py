"""Tomadas 3D do episódio 17 — O presente que ninguém esperava (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_ape  # noqa: F401  (registram "varanda", "kit_dupla" e "ape")
import lib3d

TOMADAS = {
    "A1": (5.0, "ape", {"kind": "entrega"}),   # 0–5 s: ela entrega a caixinha; o cartão preto
    "A2": (6.0, "ape", {"kind": "examina"}),   # 5–11 s: ele examina o cartão
    "A3": (7.0, "ape", {"kind": "aponta"}),    # 11–18 s: ela aponta para a porta
    "A4": (9.0, "ape", {"kind": "revela"}),    # 18–27 s: revelação da fechadura
    "A5": (10.0, "ape", {"kind": "cartao"}),   # 27–37 s: simulação do acesso por cartão
    "A6": (4.0, "ape", {"kind": "sorriso"}),   # 37–41 s: o casal sorri
    "A7": (3.0, "ape", {"kind": "close"}),     # 41–44 s: close no cartão e na fechadura
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
