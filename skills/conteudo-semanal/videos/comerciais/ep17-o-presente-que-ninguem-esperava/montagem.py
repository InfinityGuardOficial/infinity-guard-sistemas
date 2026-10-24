"""Montagem do episódio 17 — O presente que ninguém esperava. Uso: python montagem.py [video|still T...|capa]"""
import os, sys
os.environ.setdefault("VIDEO_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import comercial as C

if __name__ == "__main__":
    C.main()
