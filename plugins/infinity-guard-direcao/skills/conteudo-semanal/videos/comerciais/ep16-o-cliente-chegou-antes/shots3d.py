"""Tomadas 3D do episódio — O cliente chegou antes de todo mundo! (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_loja  # noqa: F401  (registram "varanda", "kit_dupla" e "loja")
import lib3d

TOMADAS = {
    "L1": (2.6, "loja", {"kind": "chegada"}),    # 0–2,6 s: o cliente chega, a loja fechada
    "L2": (2.4, "loja", {"kind": "relogio"}),    # 2,6–5 s: close, ele olha o relógio
    "L3": (4.0, "loja", {"kind": "abre"}),       # 5–9 s: a porta de enrolar sobe, Rosa cumprimenta
    "L4": (6.0, "loja", {"kind": "conversa"}),   # 9–15 s: Rosa e Júlia conversam no caixa
    "L5": (8.0, "loja", {"kind": "planta"}),     # 15–23 s: planejamento visto de cima
    "L6": (6.0, "loja", {"kind": "rotina"}),     # 23–29 s: câmera na parede e a equipe atendendo
    "K1": (12.0, "kit_dupla", {}),               # 29–41 s: o produto
    "L7": (5.0, "loja", {"kind": "atende"}),     # 41–46 s: atendimento normal
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
