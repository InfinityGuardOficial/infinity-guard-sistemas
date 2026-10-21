#!/usr/bin/env python3
"""Métricas de vendas a partir da exportação de pedidos da Nuvemshop (reaproveita skills/painel-de-vendas).

Uso:
  python3 tools/metricas_vendas.py                    # pega o CSV mais novo em dados/nuvemshop/
  python3 tools/metricas_vendas.py --pedidos vendas.csv [--conversas conversas.csv]

Coloque em dados/nuvemshop/ a exportação de vendas (Nuvemshop → Vendas → Exportar). Se houver um arquivo
com "conversa" no nome, ele entra como planilha do atendimento (conversão das conversas).
Também lê a planilha do Google e a pasta do Drive configuradas (tools/fontes_externas.py).
Nada é estimado: sem arquivo, a resposta diz que não há dados.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos  # noqa: E402
from tools import _skills, fontes_externas  # noqa: E402


def _mais_novo(conversas):
    return fontes_externas.mais_novo("nuvemshop", lambda f: ("conversa" in f.name.lower()) == conversas)


def coletar(pedidos=None, conversas=None, hoje=None):
    pasta = caminhos.dados() / "nuvemshop"
    pedidos = Path(pedidos) if pedidos else _mais_novo(False)
    conversas = Path(conversas) if conversas else _mais_novo(True)
    if not pedidos or not pedidos.exists():
        return {"fonte": "nuvemshop_csv", "ok": False,
                "motivo": f"nenhum CSV de pedidos em {pasta}. Exporte as vendas na Nuvemshop e salve lá."}
    painel = _skills.carregar("painel-de-vendas", "painel")
    linhas = painel.ler_csv(pedidos)
    col = painel.colunas(list(linhas[0].keys()) if linhas else [])
    conv = painel.ler_csv(conversas) if conversas and conversas.exists() else None
    m = painel.metricas(painel.consolidar(linhas, col), conv, hoje)
    m.update({"fonte": "nuvemshop_csv", "ok": True, "arquivo": pedidos.name,
              "arquivo_conversas": conversas.name if conv is not None else None})
    return m


def main():
    caminhos.terminal_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pedidos")
    ap.add_argument("--conversas")
    a = ap.parse_args()
    print(json.dumps(coletar(a.pedidos, a.conversas), indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
