"""Caminhos do orquestrador. IG_HOME troca a raiz (os testes usam uma pasta temporária)."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def raiz():
    return Path(os.environ.get("IG_HOME") or REPO)


def logs():
    p = raiz() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def dados():
    return raiz() / "dados"


def config_dir():
    return raiz() / "config"
