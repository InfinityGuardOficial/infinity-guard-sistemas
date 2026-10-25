"""Tomadas 3D do episódio 18 — O primeiro presente da loja (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_loja, cenarios_inauguracao  # noqa: F401  (registram os cenários)
import lib3d

TOMADAS = {
    "I1": (5.0, "inauguracao", {"kind": "abre"}),        # 0–5 s: ela abre a caixa na inauguração
    "I2": (6.0, "inauguracao", {"kind": "flashback"}),   # 5–11 s: véspera, arrumando a loja
    "I3": (6.0, "inauguracao", {"kind": "bilhete"}),     # 11–17 s: reconhece a letra da mãe
    "I4": (7.0, "inauguracao", {"kind": "revela"}),      # 17–24 s: a câmera dentro da caixa
    "I5": (7.0, "inauguracao", {"kind": "abraco"}),      # 24–31 s: mãe e filha se abraçam
    "I6": (6.0, "dome_estudio", {}),                     # 31–37 s: o produto (fiel à foto)
    "I7": (8.0, "inauguracao", {"kind": "instalada"}),   # 37–45 s: instalada no teto, dentro da loja
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
