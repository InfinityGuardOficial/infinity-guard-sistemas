"""Tomadas 3D do episódio 15 — Quem deixou isso na porta? (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios  # noqa: F401  (registra "varanda" e "kit_dupla")
import lib3d

TOMADAS = {
    "P1": (5.0, "varanda", {"kind": "porta_abre"}),   # 0–5 s: a porta abre, a encomenda no tapete
    "P2": (9.0, "varanda", {"kind": "etiqueta"}),     # 5–14 s: a etiqueta e o comentário do marido
    "P3": (13.0, "varanda", {"kind": "campo"}),       # 14–27 s: câmera bem posicionada, campo de visão, noite
    "P4": (12.0, "kit_dupla", {}),                    # 27–39 s: o produto
    "P5": (8.0, "varanda", {"kind": "entrega"}),      # 39–47 s: entrega ao destinatário certo
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
