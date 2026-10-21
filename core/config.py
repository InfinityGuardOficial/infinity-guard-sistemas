"""Lê config/orquestrador.json e sobrepõe config/orquestrador.local.json (o arquivo do computador do max)."""
import copy
import json

from core import caminhos
from core.caminhos import REPO

PADRAO = REPO / "config" / "orquestrador.json"


def _mesclar(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mesclar(base[k], v)
        else:
            base[k] = v
    return base


def carregar():
    cfg = json.loads(PADRAO.read_text(encoding="utf-8"))
    for f in (caminhos.config_dir() / "orquestrador.json", caminhos.config_dir() / "orquestrador.local.json"):
        if f.exists() and f.resolve() != PADRAO.resolve():
            _mesclar(cfg, json.loads(f.read_text(encoding="utf-8")))
    cfg.pop("_leia", None)
    return copy.deepcopy(cfg)
