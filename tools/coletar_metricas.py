#!/usr/bin/env python3
"""Junta vendas (Nuvemshop) e anúncios (Meta, só leitura) em logs/metrics.json.

Uso: python3 tools/coletar_metricas.py
Antes de ler, baixa as planilhas do Google configuradas (tools/fontes_externas.py).
current_roas e conversion_rate ficam null quando não há dado: nada é inventado.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos  # noqa: E402
from tools import fontes_externas, metricas_meta, metricas_vendas  # noqa: E402


def _seguro(fn):
    try:
        return fn()
    except Exception as e:  # uma fonte quebrada não derruba a outra
        return {"ok": False, "motivo": f"{type(e).__name__}: {e}"}


def coletar(gravar=True, api_meta=None, abrir=None):
    planilhas = _seguro(lambda: fontes_externas.sincronizar(**({"abrir": abrir} if abrir else {})))
    vendas = _seguro(metricas_vendas.coletar)
    meta = _seguro(lambda: metricas_meta.coletar(api=api_meta))
    conv = vendas.get("conversas") if vendas.get("ok") else None
    m = {"gerado_em": datetime.now().isoformat(timespec="seconds"),
         "current_roas": meta.get("roas") if meta.get("ok") else None,
         "conversion_rate": conv["conversao"] if conv else None,
         "vendas": vendas, "meta": meta, "planilhas": planilhas}
    if gravar:
        f = caminhos.logs() / "metrics.json"
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(m, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        tmp.replace(f)
    return m


if __name__ == "__main__":
    caminhos.terminal_utf8()
    print(json.dumps(coletar(), indent=2, ensure_ascii=False, default=str))
