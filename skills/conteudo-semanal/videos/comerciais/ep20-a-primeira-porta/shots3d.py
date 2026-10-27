"""Tomadas 3D do episódio 20 — A primeira porta (duração em s, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cenarios, cenarios_porta  # noqa: F401  (registram "porta" e "lembranca")
import lib3d

TOMADAS = {
    "Q1": (5.0, "porta", {"kind": "corredor"}),      # 0–5 s: ela chega diante da porta 302
    "Q2": (4.5, "lembranca", {"kind": "estudo"}),    # 5–9,5 s: lembrança: estudo à noite
    "Q3": (4.0, "lembranca", {"kind": "trabalho"}),  # 9,5–13,5 s: lembrança: trabalho
    "Q4": (2.5, "lembranca", {"kind": "planos"}),    # 13,5–16 s: lembrança: planos e economias
    "Q5": (2.0, "porta", {"kind": "chaves"}),        # 16–18 s: as chaves do 302
    "Q6": (6.0, "porta", {"kind": "medir"}),         # 18–24 s: ela mede a porta antes de escolher
    "Q7": (6.0, "porta", {"kind": "instala"}),       # 24–30 s: a fechadura nova no lugar da maçaneta
    "Q8": (8.0, "porta", {"kind": "demo"}),          # 30–38 s: simulação: cartão e senha
    "Q9": (6.0, "porta", {"kind": "senha"}),         # 38–44 s: ela digita a senha e abre
    "Q10": (4.0, "porta", {"kind": "entra"}),        # 44–48 s: ela entra no apartamento
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
