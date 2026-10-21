"""Caminhos do orquestrador. IG_HOME troca a raiz (os testes usam uma pasta temporária)."""
import os
import sys
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


def terminal_utf8():
    """O terminal do Windows usa cp1252 e quebra com acento e seta: força UTF-8 na saída."""
    for fluxo in (sys.stdout, sys.stderr):
        if fluxo is not None and hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
