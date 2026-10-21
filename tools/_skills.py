"""Carrega os scripts das skills (painel.py, midia.py) sem copiar código: o cálculo continua num lugar só."""
import importlib.util
import sys

from core.caminhos import REPO


def carregar(skill, script):
    nome = f"ig_skill_{skill.replace('-', '_')}_{script}"
    if nome in sys.modules:
        return sys.modules[nome]
    caminho = REPO / "skills" / skill / "scripts" / f"{script}.py"
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod
