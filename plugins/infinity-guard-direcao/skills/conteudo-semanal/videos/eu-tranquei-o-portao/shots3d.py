"""Tomadas 3D de 'Eu tranquei o portão?' (duração em segundos, cenário, parâmetros)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anime3d"))
import lib3d

TOMADAS = {
    "A": (6.3, "aerea", {}),                          # gancho: 40 km de casa
    "B": (6.0, "casa", {"kind": "saida"}),            # fim de ano, carro cheio saindo
    "C": (9.5, "estrada", {"mood": False}),           # estrada no fim de tarde (reaproveitada)
    "M": (5.7, "estrada", {"mood": True}),            # o clima muda (e rebobina)
    "D": (4.8, "casa", {"kind": "instalada"}),        # a câmera aparece na entrada
    "E": (5.7, "casa", {"kind": "anoitecer"}),        # de dia ou de noite
    "F": (3.2, "casa", {"kind": "entrada"}),          # a primeira câmera vai na entrada
    "G": (3.4, "kit", {}),                            # kit com duas câmeras
    "FEED": (0.05, "casa", {"kind": "feed"}),         # imagem da câmera no celular (dia)
    "FEEDN": (0.05, "casa", {"kind": "feed_noite"}),  # imagem da câmera no celular (noite)
}

if __name__ == "__main__":
    lib3d.main(TOMADAS)
