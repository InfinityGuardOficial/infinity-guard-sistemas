#!/usr/bin/env python3
"""Fontes automáticas de dados: Google Planilhas e pasta do Google Drive (sem exportar CSV na mão).

1. Planilhas (config "fontes.planilhas" em config/orquestrador.local.json): um link por fonte.
   - "nuvemshop": pedidos (mesmas colunas da exportação da Nuvemshop)
   - "conversas": planilha do atendimento (modelo em skills/painel-de-vendas/references/modelo-conversas.csv)
   - "meta": resultados dos anúncios (colunas conjunto;gasto;compras;receita)
   Vale o link de "Arquivo → Compartilhar → Publicar na web (CSV)" ou o link normal da planilha com
   "Qualquer pessoa com o link: Leitor". A cada ciclo o arquivo é baixado para dados/<pasta>/planilha-*.csv.
   Se o download falhar, o arquivo anterior continua valendo.
2. Pasta do Drive (config "fontes.pasta_drive", ex.: "G:/Meu Drive/Infinity Guard"): com o Google Drive para
   computador, a pasta fica sincronizada no PC. As subpastas nuvemshop/, meta/ e app/ dela são lidas junto
   com as de dados/ (vale o arquivo mais novo).

Uso:
  python3 tools/fontes_externas.py     # baixa as planilhas agora e mostra o que achou
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos, config  # noqa: E402

DESTINO = {"nuvemshop": ("nuvemshop", "planilha-pedidos.csv"),
           "conversas": ("nuvemshop", "planilha-conversas.csv"),
           "meta": ("meta", "planilha-meta.csv")}
PLANILHA = re.compile(r"https://docs\.google\.com/spreadsheets/d/([\w-]+)")


def url_csv(url):
    """Converte o link normal da planilha no link de download em CSV (mantém a aba do #gid=)."""
    if "output=csv" in url or "format=csv" in url:
        return url
    m = PLANILHA.match(url)
    if not m or "/d/e/" in url:
        return url
    gid = re.search(r"[#&?]gid=(\d+)", url)
    return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv" + (f"&gid={gid.group(1)}" if gid else "")


def _fontes(cfg):
    return (cfg or config.carregar()).get("fontes") or {}


def sincronizar(cfg=None, abrir=urllib.request.urlopen):
    """Baixa cada planilha configurada. Devolve uma linha por fonte: {nome, ok, arquivo | motivo}."""
    saida = []
    for nome, url in (_fontes(cfg).get("planilhas") or {}).items():
        if not url or nome not in DESTINO:
            continue
        pasta, arquivo = DESTINO[nome]
        destino = caminhos.dados() / pasta / arquivo
        try:
            with abrir(urllib.request.Request(url_csv(url), headers={"User-Agent": "infinity-guard"}), timeout=30) as r:
                texto = r.read().decode("utf-8-sig")
            if texto.lstrip().startswith("<"):
                raise ValueError("a planilha não está aberta para leitura: em Compartilhar, ponha "
                                 "'Qualquer pessoa com o link: Leitor' (ou use Publicar na web → CSV)")
            if len(texto.strip().splitlines()) < 2:
                raise ValueError("a planilha veio sem linhas de dados")
            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp = destino.with_suffix(".tmp")
            tmp.write_text(texto, encoding="utf-8")
            tmp.replace(destino)
            saida.append({"nome": nome, "ok": True, "arquivo": str(destino)})
        except Exception as e:  # uma planilha quebrada não derruba as outras
            saida.append({"nome": nome, "ok": False, "motivo": f"{type(e).__name__}: {e}"})
    return saida


def pastas(sub, cfg=None):
    """Onde procurar os arquivos de uma fonte: dados/<sub> e, se configurada, <pasta do Drive>/<sub>."""
    lista = [caminhos.dados() / sub]
    drive = _fontes(cfg).get("pasta_drive")
    if drive and (Path(drive) / sub).is_dir():
        lista.append(Path(drive) / sub)
    return lista


def mais_novo(sub, filtro=lambda f: True, padrao="*.csv", cfg=None):
    arquivos = [f for p in pastas(sub, cfg) for f in p.glob(padrao) if filtro(f)]
    return max(arquivos, key=lambda f: f.stat().st_mtime) if arquivos else None


if __name__ == "__main__":
    caminhos.terminal_utf8()
    print(json.dumps({"planilhas": sincronizar(), "pastas": {s: [str(p) for p in pastas(s)] for s in ("nuvemshop", "meta", "app")}},
                     indent=2, ensure_ascii=False))
