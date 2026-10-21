#!/usr/bin/env python3
"""Métricas do Meta Ads, SÓ LEITURA. Duas fontes, nesta ordem:

1. API de Marketing da Meta (GET /insights), quando existirem as variáveis de ambiente
   META_ACCESS_TOKEN e META_AD_ACCOUNT_ID (ex.: act_123456789). Este adaptador só faz GET.
2. CSV exportado do Gerenciador de Anúncios em dados/meta/ (colunas conjunto;gasto;compras;receita,
   o mesmo formato de skills/plano-de-midia), o mais novo da pasta. Também vale a planilha do Google e a
   pasta do Drive configuradas (tools/fontes_externas.py).

Uso:
  python3 tools/metricas_meta.py [--csv resultados.csv] [--dias 7]
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos  # noqa: E402
from tools import _skills, fontes_externas  # noqa: E402

API = "https://graph.facebook.com/v21.0"
COMPRA = ("purchase", "offsite_conversion.fb_pixel_purchase", "omni_purchase")


class MetaAdsLeitura:
    """Adaptador da API da Meta. Só leitura: não existe método que crie, altere ou pause nada."""

    def __init__(self, token, conta, abrir=urllib.request.urlopen):
        self.token, self.conta, self._abrir = token, conta if conta.startswith("act_") else f"act_{conta}", abrir

    @classmethod
    def do_ambiente(cls):
        token, conta = os.environ.get("META_ACCESS_TOKEN"), os.environ.get("META_AD_ACCOUNT_ID")
        return cls(token, conta) if token and conta else None

    def _get(self, caminho, **params):
        params["access_token"] = self.token
        req = urllib.request.Request(f"{API}/{caminho}?{urllib.parse.urlencode(params)}", method="GET")
        with self._abrir(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def conjuntos(self, dias=7):
        """Uma linha por conjunto de anúncios: conjunto, gasto, compras, receita (mesmo formato do CSV)."""
        dados = self._get(f"{self.conta}/insights", level="adset", date_preset=f"last_{dias}d",
                          fields="adset_name,adset_id,spend,actions,action_values", limit=200)
        saida = []
        for r in dados.get("data", []):
            soma = lambda campo: sum(float(a.get("value", 0)) for a in r.get(campo, []) if a.get("action_type") in COMPRA)  # noqa: E731
            saida.append({"conjunto": r.get("adset_name") or r.get("adset_id"), "id": r.get("adset_id"),
                          "gasto": float(r.get("spend", 0)), "compras": int(soma("actions")),
                          "receita": round(soma("action_values"), 2)})
        return saida


def _csv_mais_novo():
    return fontes_externas.mais_novo("meta")


def coletar(csv=None, dias=7, api=None):
    api = api if api is not None else MetaAdsLeitura.do_ambiente()
    if api:
        conjuntos, fonte, arquivo = api.conjuntos(dias), "meta_api", None
    else:
        arquivo = Path(csv) if csv else _csv_mais_novo()
        if not arquivo or not arquivo.exists():
            return {"fonte": "meta", "ok": False,
                    "motivo": "sem META_ACCESS_TOKEN/META_AD_ACCOUNT_ID e sem CSV do Gerenciador em dados/meta/."}
        conjuntos = _skills.carregar("plano-de-midia", "midia").ler_resultados(arquivo)
        fonte, arquivo = "meta_csv", arquivo.name
    gasto = round(sum(c["gasto"] for c in conjuntos), 2)
    compras = sum(c["compras"] for c in conjuntos)
    receita = round(sum(c["receita"] for c in conjuntos), 2)
    return {"fonte": fonte, "ok": True, "arquivo": arquivo, "dias": dias if fonte == "meta_api" else None,
            "gasto": gasto, "compras": compras, "receita": receita,
            "roas": round(receita / gasto, 2) if gasto else None,
            "cpa": round(gasto / compras, 2) if compras else None, "conjuntos": conjuntos}


def main():
    caminhos.terminal_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--dias", type=int, default=7)
    a = ap.parse_args()
    print(json.dumps(coletar(a.csv, a.dias), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
