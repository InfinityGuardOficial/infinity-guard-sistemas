#!/usr/bin/env python3
"""Auditor de Prova da Loja: confere, página por página, o que falta para o cliente confiar na loja.

Uso:
  python3 auditar.py --url https://infinityguard.com.br/ --url https://infinityguard.com.br/produtos/...
  python3 auditar.py --catalogo                  (home + páginas institucionais + todos os produtos ativos do catálogo)
  python3 auditar.py --arquivo pagina.html [--arquivo outra.txt]   (HTML salvo ou texto copiado da página)
  ... --json          (saída em JSON)
  ... --saida relatorio.md

O que confere: CNPJ (com dígito verificador), garantia com prazo, avaliações, política de troca,
contato e endereço, HTTPS e rastros de fornecedor (ex.: "plugue da UE").
Código Anatel não é cobrado (dropshipping: o fornecedor não fornece; não é pendência desde 22/10).
Se a página citar Anatel ou homologação, o auditor avisa para tirar até o código estar conferido.
O script só diz o que achou ou não achou. Nunca preenche CNPJ, código Anatel ou prazo de garantia.
Avaliações carregadas por JavaScript podem não aparecer no HTML: nesse caso, confira no navegador.
"""
import argparse
import html as htmllib
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
CATALOGOS = [AQUI.parent / "atendente-infinity-guard" / "references" / "catalogo.json",
             AQUI / "references" / "catalogo.json"]
INSTITUCIONAIS = ["", "sobre-a-infinity-guard/", "trocas-e-devolucoes/", "contato/", "perguntas-frequentes/"]

# --- leitura -------------------------------------------------------------------------------

def baixar(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (auditor prova-da-loja)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", errors="replace")


def texto_de(html):
    """HTML -> texto corrido (também aceita texto puro)."""
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", htmllib.unescape(h)).strip()


# --- CNPJ ------------------------------------------------------------------------------------

def cnpj_valido(numero):
    d = re.sub(r"\D", "", numero)
    if len(d) != 14 or d == d[0] * 14:
        return False
    def dv(base, pesos):
        s = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = dv(d[:12], p1)
    d2 = dv(d[:12] + d1, [6] + p1)
    return d[12:] == d1 + d2


RE_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
RE_ANATEL = re.compile(r"anatel|homologad|\b\d{5}-\d{2}-\d{5}\b", re.I)
RE_GARANTIA_PRAZO = re.compile(
    r"garantia[^.]{0,80}?\b(\d{1,3}|um|uma|dois|tr[eê]s|seis|doze)\s*(dias?|m[eê]s(es)?|anos?)\b"
    r"|\b(\d{1,3}|um|uma|dois|tr[eê]s|seis|doze)\s*(dias?|m[eê]s(es)?|anos?)\s*de\s*garantia", re.I)
RE_AVALIACAO = re.compile(
    r"aggregaterating|\"reviewcount\"|\b\d+\s*(avalia[cç][oõ]es|opini[oõ]es|reviews)\b|"
    r"\b[1-5][,.]\d\s*(de 5|/ ?5|estrelas)|trustvox|yotpo|lily\s*reviews|judge\.me|reclame\s*aqui", re.I)
RE_TROCA = re.compile(r"(\b7|sete)\s*dias[^.]{0,40}(troca|devolu|arrepend)|(troca|devolu|arrepend)[^.]{0,40}(\b7|sete)\s*dias", re.I)
RE_CEP = re.compile(r"\b\d{5}-\d{3}\b")
RE_TELEFONE = re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b|wa\.me/\d+")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|email-protection")
RASTROS = [  # sobras de anúncio importado que derrubam a confiança
    (re.compile(r"plugue da ue|plug(ue)? (eu|europeu)|\beu plug\b", re.I), "variante \"plugue da UE\" (Brasil usa tomada padrão NBR 14136)"),
    (re.compile(r"aliexpress|alibaba|shein|frete da china|envio da china", re.I), "menção a marketplace ou envio do exterior"),
    (re.compile(r"\bcolou?r\b\s*:|\bsize\b\s*:|\bship(s|ping)? from\b", re.I), "texto de variante em inglês"),
    (re.compile(r"empty-placeholder", re.I), "imagem vazia (placeholder) na galeria"),
]


def checar(texto, html, url):
    """Devolve a lista de itens checados para uma página."""
    t = texto
    itens = []

    def item(chave, status, achado, corrigir):
        itens.append({"chave": chave, "status": status, "achado": achado, "corrigir": corrigir})

    cnpjs = RE_CNPJ.findall(t)
    validos = [c for c in cnpjs if cnpj_valido(c)]
    if validos:
        item("cnpj", "ok", f"CNPJ {validos[0]} (dígito verificador confere)", "")
    elif cnpjs:
        item("cnpj", "erro", f"número com cara de CNPJ mas dígito não confere: {cnpjs[0]}",
             "Corrija o CNPJ copiando do cartão CNPJ da Receita.")
    else:
        item("cnpj", "falta", "nenhum CNPJ na página",
             "Coloque no rodapé: razão social, CNPJ e endereço (Decreto 7.962/2013).")

    if RE_ANATEL.search(t):  # não é cobrado; só avisa se a página afirma o que a loja ainda não conferiu
        item("anatel", "aviso", "a página cita Anatel, homologação ou código",
             "Tire a menção até o dono conferir o modelo no portal da Anatel (tarefa interna no app).")

    m = RE_GARANTIA_PRAZO.search(t)
    if m:
        item("garantia", "ok", f"garantia com prazo: \"{m.group(0)[:90]}\"", "")
    elif re.search(r"garantia", t, re.I):
        item("garantia", "aviso", "fala em garantia mas sem prazo",
             "Escreva o prazo: garantia legal de 90 dias (CDC art. 26) + garantia extra só se o fornecedor der por escrito.")
    else:
        item("garantia", "falta", "nenhuma menção a garantia", "Informe o prazo de garantia na página.")

    if RE_AVALIACAO.search(html) or RE_AVALIACAO.search(t):
        item("avaliacoes", "ok", "há avaliações ou selo de reputação", "")
    else:
        item("avaliacoes", "falta", "nenhuma avaliação de cliente visível",
             "Instale um app de avaliações da Nuvemshop e peça avaliação (com foto) a cada cliente no dia 7 do pós-venda.")

    if RE_TROCA.search(t):
        item("troca", "ok", "prazo de 7 dias para troca/devolução", "")
    elif re.search(r"troca|devolu", t, re.I):
        item("troca", "aviso", "fala de troca sem prazo", "Escreva: 7 dias corridos após o recebimento (CDC art. 49).")
    else:
        item("troca", "falta", "sem política de troca", "Link para a página de trocas no rodapé.")

    contato = []
    if RE_TELEFONE.search(t) or RE_TELEFONE.search(html):
        contato.append("telefone/WhatsApp")
    if RE_EMAIL.search(html) or RE_EMAIL.search(t):
        contato.append("e-mail")
    if RE_CEP.search(t):
        contato.append("endereço com CEP")
    if "endereço com CEP" in contato and len(contato) >= 2:
        item("contato", "ok", ", ".join(contato), "")
    else:
        item("contato", "aviso" if contato else "falta", ", ".join(contato) or "nenhum contato",
             "Mostre endereço físico com CEP (pode ser comercial) além do WhatsApp e e-mail (Decreto 7.962/2013).")

    if url and url.startswith("http://"):
        item("https", "erro", "página sem HTTPS", "Ative o certificado SSL na Nuvemshop.")

    rastros = [desc for rx, desc in RASTROS if rx.search(html) or rx.search(t)]
    if rastros:
        item("rastros", "aviso", "; ".join(rastros),
             "Limpe as variantes e textos herdados do fornecedor: renomeie para português e remova o que não se aplica ao Brasil.")
    return itens


# --- relatório -------------------------------------------------------------------------------

PESO = {"cnpj": 1, "garantia": 2, "avaliacoes": 3, "troca": 4, "anatel": 5, "contato": 6, "rastros": 7, "https": 0}
ROTULO = {"cnpj": "CNPJ e razão social", "anatel": "Menção a Anatel", "garantia": "Garantia com prazo",
          "avaliacoes": "Avaliações reais", "troca": "Troca em 7 dias", "contato": "Endereço e contato",
          "rastros": "Rastros de fornecedor", "https": "HTTPS"}
SIMBOLO = {"ok": "✅", "aviso": "⚠️", "falta": "❌", "erro": "❌"}
MANUAIS = [
    "Fotos reais: pelo menos 1 foto sua do produto na mão ou instalado (o script não distingue foto real de foto do fornecedor).",
    "Avaliações: abra a página no navegador; se o app de avaliações carrega por JavaScript, o script não vê.",
    "Página de trocas: diga quem paga o frete da devolução e para onde enviar.",
    "Rodapé: link do Twitter/X e demais redes funcionando.",
]


def auditar(paginas):
    """paginas: lista de dicts {url, html}. Devolve o relatório em dict."""
    resultado = []
    for p in paginas:
        txt = texto_de(p["html"])
        resultado.append({"url": p["url"], "itens": checar(txt, p["html"], p["url"])})
    # site inteiro: CNPJ/contato valem se aparecem em qualquer página; o resto é por página
    correcoes = {}
    for pg in resultado:
        for it in pg["itens"]:
            if it["status"] == "ok":
                continue
            c = correcoes.setdefault(it["chave"], {"chave": it["chave"], "status": it["status"],
                                                   "corrigir": it["corrigir"], "paginas": []})
            c["paginas"].append(pg["url"])
    for chave in ("cnpj", "contato"):
        if any(it["chave"] == chave and it["status"] == "ok" for pg in resultado for it in pg["itens"]):
            correcoes.pop(chave, None)
    lista = sorted(correcoes.values(), key=lambda c: PESO.get(c["chave"], 9))
    total = sum(len(pg["itens"]) for pg in resultado)
    ok = sum(1 for pg in resultado for it in pg["itens"] if it["status"] == "ok")
    return {"data": date.today().isoformat(), "paginas": resultado, "correcoes": lista,
            "nota": round(100 * ok / total) if total else 0, "manuais": MANUAIS}


def relatorio_md(r):
    linhas = [f"# Auditoria de prova da loja · {r['data']}", "",
              f"**Nota de prova: {r['nota']}/100** ({len(r['paginas'])} páginas). "
              "Regra: sem CNPJ e garantia com prazo, não ligue anúncio.", "",
              "## Lista de correção, em ordem", ""]
    if not r["correcoes"]:
        linhas.append("Nada pendente nos itens automáticos.")
    for i, c in enumerate(r["correcoes"], 1):
        pags = c["paginas"]
        onde = "todas as páginas auditadas" if len(pags) == len(r["paginas"]) and len(pags) > 1 else ", ".join(pags)
        linhas.append(f"{i}. **{ROTULO.get(c['chave'], c['chave'])}** {SIMBOLO[c['status']]}: {c['corrigir']}  ")
        linhas.append(f"   Onde: {onde}")
    linhas += ["", "## Conferir à mão", ""] + [f"- [ ] {m}" for m in r["manuais"]]
    linhas += ["", "## Página por página", ""]
    for pg in r["paginas"]:
        linhas.append(f"### {pg['url']}")
        for it in pg["itens"]:
            linhas.append(f"- {SIMBOLO[it['status']]} {ROTULO.get(it['chave'], it['chave'])}: {it['achado']}")
        linhas.append("")
    linhas.append("O auditor só registra o que encontrou. CNPJ e prazo de garantia vêm dos documentos do dono.")
    return "\n".join(linhas)


def paginas_do_catalogo():
    cat = next((c for c in CATALOGOS if c.exists()), None)
    if not cat:
        raise SystemExit("catálogo não encontrado (instale a skill atendente-infinity-guard ao lado desta)")
    dados = json.loads(cat.read_text(encoding="utf-8"))
    base = dados["site"].rstrip("/") + "/"
    alvos = [base + p for p in INSTITUCIONAIS]
    if dados.get("landing"):  # página de oferta (oferta.infinityguard.com.br)
        alvos.append(dados["landing"].rstrip("/") + "/")
    alvos += [p["url"] for p in dados["produtos"] if p.get("ativo") and p["categoria"] != "home_office"]
    return alvos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--arquivo", action="append", default=[])
    ap.add_argument("--catalogo", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()

    alvos = list(a.url)
    if a.catalogo:
        alvos += paginas_do_catalogo()
    paginas, falhas = [], []
    for u in alvos:
        try:
            paginas.append({"url": u, "html": baixar(u)})
        except Exception as e:  # noqa: BLE001
            falhas.append(f"{u}: {e}")
    for f in a.arquivo:
        paginas.append({"url": f, "html": Path(f).read_text(encoding="utf-8", errors="replace")})
    if not paginas:
        raise SystemExit("nenhuma página lida. " + " | ".join(falhas))
    r = auditar(paginas)
    r["falhas"] = falhas
    saida = json.dumps(r, ensure_ascii=False, indent=2) if a.json else relatorio_md(r)
    if falhas and not a.json:
        saida += "\n\nNão consegui abrir: " + "; ".join(falhas)
    if a.saida:
        Path(a.saida).write_text(saida, encoding="utf-8")
    print(saida)


if __name__ == "__main__":
    main()
