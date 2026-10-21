"""Pedidos de aprovação (logs/aprovacoes.json): listar, aprovar e recusar pelo terminal.

Aprovar só registra a sua decisão; quem executa a ação é você (no Gerenciador, na Nuvemshop ou no WhatsApp).
O número de cada pedido é a posição dele no arquivo e não muda.
"""
import json
import os
import re
from datetime import datetime

from core import caminhos

PENDENTE = "aguardando_max"
EVENTOS_DE_ANUNCIO = ("revisar_conjuntos", "roas_abaixo_do_equilibrio")


def _arquivo():
    return caminhos.logs() / "aprovacoes.json"


def carregar():
    f = _arquivo()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def _gravar(lista):
    f = _arquivo()
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(lista, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)


def link(pedido):
    """Atalho para onde a ação é feita, quando dá para saber."""
    conta = re.sub(r"\D", "", os.environ.get("META_AD_ACCOUNT_ID", ""))
    texto = pedido["acao"].lower()
    if pedido.get("evento") in EVENTOS_DE_ANUNCIO or any(p in texto for p in ("conjunto", "orçamento", "anúncio", "campanha")):
        return f"https://adsmanager.facebook.com/adsmanager/manage/adsets?act={conta}" if conta \
            else "https://adsmanager.facebook.com/adsmanager/manage/adsets"
    if any(p in texto for p in ("preço", "cupom", "produto", "boleto", "pedido")):
        return "https://www.nuvemshop.com.br/login"
    return None


def pendentes():
    return [(i, p) for i, p in enumerate(carregar(), 1) if p["status"] == PENDENTE]


def decidir(numero, aprovar, nota=""):
    lista = carregar()
    if not 1 <= numero <= len(lista):
        raise ValueError(f"não existe o pedido {numero} (há {len(lista)})")
    p = lista[numero - 1]
    if p["status"] != PENDENTE:
        raise ValueError(f"o pedido {numero} já foi decidido: {p['status']}")
    p["status"] = "aprovado_por_max" if aprovar else "recusado_por_max"
    p["decidido_em"] = datetime.now().isoformat(timespec="seconds")
    if nota:
        p["nota"] = nota
    _gravar(lista)
    return p


def texto_lista():
    itens = pendentes()
    if not itens:
        return "Nenhum pedido esperando você."
    linhas = [f"{len(itens)} pedido(s) esperando você:"]
    for n, p in itens:
        linhas.append(f"  {n}. [{p['agente']}] {p['acao']}")
        if p.get("relatorio"):
            linhas.append(f"     por quê: logs/agentes/{p['relatorio']}")
        if link(p):
            linhas.append(f"     onde fazer: {link(p)}")
    linhas.append("Aprovar: ... aprovar <número> [nota]   Recusar: ... recusar <número> [nota]")
    return "\n".join(linhas)
