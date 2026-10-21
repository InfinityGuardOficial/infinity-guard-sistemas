"""Pedidos de aprovação (logs/aprovacoes.json): listar, aprovar e recusar pelo terminal.

Aprovar só registra a sua decisão; quem executa a ação é você (no Gerenciador, na Nuvemshop ou no WhatsApp).
O número de cada pedido é a posição dele no arquivo e não muda.
Para decidir rápido: logs/aprovacoes.html (abre no navegador, com o link de onde fazer cada ação e o comando
pronto para copiar), vários números de uma vez ("aprovar 2 5 7") e aviso do Windows quando chega pedido novo.
"""
import html
import json
import os
import re
import subprocess
import sys
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


def decidir_varios(numeros, aprovar, nota=""):
    """Decide vários pedidos de uma vez. Devolve [(número, pedido ou mensagem de erro)]."""
    saida = []
    for n in numeros:
        try:
            saida.append((n, decidir(n, aprovar, nota)))
        except ValueError as e:
            saida.append((n, str(e)))
    salvar_pagina()
    return saida


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


def salvar_pagina(agora=None):
    """logs/aprovacoes.html: uma página para decidir em segundos (abre com dois cliques)."""
    itens = pendentes()
    esc = html.escape
    py = "python core/daemon_orchestrator.py"
    blocos = []
    for n, p in itens:
        onde = link(p)
        blocos.append(
            f"<li><p><b>{n}.</b> <span class=ag>{esc(p['agente'])}</span> {esc(p['acao'])}</p>"
            + (f"<p><a href='agentes/{esc(p['relatorio'])}'>por quê (relatório)</a></p>" if p.get("relatorio") else "")
            + (f"<p><a href='{esc(onde)}' target=_blank>onde fazer</a></p>" if onde else "")
            + f"<p><code>{py} aprovar {n}</code> &nbsp; <code>{py} recusar {n}</code></p></li>")
    corpo = f"<ol>{''.join(blocos)}</ol>" if blocos else "<p>Nenhum pedido esperando você.</p>"
    todos = " ".join(str(n) for n, _ in itens)
    pagina = f"""<!doctype html><html lang=pt-BR><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Aprovações</title><style>
:root{{--bg:#F6F2EA;--fg:#001121;--muted:#55606F;--line:#D9CDB5;--acc:#0B2240}}
@media (prefers-color-scheme:dark){{:root{{--bg:#000E1C;--fg:#F3EFEA;--muted:#A5AEBD;--line:#1C3354;--acc:#D4AF5F}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;max-width:760px;margin:0 auto;padding:16px}}
li{{border-bottom:1px solid var(--line);padding:10px 0}} p{{margin:4px 0}} a{{color:var(--acc)}} .ag{{color:var(--muted)}}
code{{background:var(--line);padding:2px 6px;border-radius:4px;overflow-wrap:anywhere}}</style></head><body>
<h1>Aprovações · {len(itens)} esperando você</h1>
<p class=ag>Atualizado em {(agora or datetime.now()):%d/%m %H:%M}. Aprovar só registra a decisão: a ação você faz no link "onde fazer". Gasto com anúncio continua só com você.</p>
{corpo}
{f"<p>Vários de uma vez: <code>{py} aprovar {todos}</code></p>" if len(itens) > 1 else ""}
</body></html>"""
    f = caminhos.logs() / "aprovacoes.html"
    f.write_text(pagina, encoding="utf-8")
    return f


def avisar(novos, cfg):
    """Aviso do Windows quando chegam pedidos novos. Fora do Windows (ou em teste) só devolve o texto."""
    if novos <= 0:
        return None
    texto = f"{novos} pedido(s) novo(s) esperando o seu ok. Abra logs/aprovacoes.html"
    if sys.platform != "win32" or not cfg.get("avisar_no_windows", True) or os.environ.get("IG_DRY_RUN") == "1":
        return texto
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
        "$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
        "$x = $t.GetElementsByTagName('text');"
        "$x.Item(0).AppendChild($t.CreateTextNode('Infinity Guard')) > $null;"
        "$x.Item(1).AppendChild($t.CreateTextNode($env:IG_AVISO)) > $null;"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
        "'{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe').Show("
        "[Windows.UI.Notifications.ToastNotification]::new($t))")
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], timeout=30,
                       env={**os.environ, "IG_AVISO": texto}, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        pass  # o aviso é um extra: a página e o comando continuam valendo
    return texto
