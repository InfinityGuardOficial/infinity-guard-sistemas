#!/usr/bin/env python3
"""Servidor MCP da Infinity Guard: expõe as ferramentas das skills para qualquer cliente MCP
(Claude Code, Claude Desktop) via stdio, no protocolo Model Context Protocol (JSON-RPC 2.0).

Cada ferramenta roda o script da skill correspondente em skills/ e devolve a saída em texto.
Nada aqui gasta dinheiro, publica ou manda mensagem: as ferramentas só leem e calculam.

Registrar no Claude Code (já vem no .mcp.json deste repositório):
  claude mcp add infinity-guard -- python3 mcp_servers/infinity_guard_mcp.py
Sem dependências além do Python 3.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
VERSAO = "1.0.0"
PROTOCOLOS = ("2025-06-18", "2025-03-26", "2024-11-05")


def _txt(desc):
    return {"type": "string", "description": desc}


def _num(desc):
    return {"type": "number", "description": desc}


# nome -> (descrição, schema de entrada, função que monta o comando)
FERRAMENTAS = {
    "revisar_texto": (
        "Revisa um texto da Infinity Guard (anúncio, post, roteiro, legenda, mensagem) contra as regras do revisor de promessas: 100% seguro, instalação, 4G, Anatel ou garantia sem documento, de/por, produto já configurado, prazo de entrega, promessa de configurar o produto por WhatsApp ou vídeo. Devolve o veredito e como reescrever.",
        {"type": "object", "properties": {"texto": _txt("Texto a revisar.")}, "required": ["texto"]},
        lambda a: ["revisor-de-promessas/scripts/revisar.py", "--texto", str(a["texto"])],
    ),
    "validar_catalogo": (
        "Confere o catálogo único de preços (Pix, parcelas, links, ids, idade dos dados).",
        {"type": "object", "properties": {}},
        lambda a: ["catalogo-e-precos/scripts/catalogo.py", "validar"],
    ),
    "comparar_concorrentes": (
        "Compara o preço de cada produto da Infinity Guard com as leituras registradas de concorrentes (Intelbras, Tapo, Kerui, Pado, marketplace), com fonte.",
        {"type": "object", "properties": {}},
        lambda a: ["radar-de-concorrentes/scripts/radar.py", "comparar"],
    ),
    "recomendar_kit": (
        "Monta o kit certo para a casa do cliente com os preços do catálogo.",
        {"type": "object", "properties": {
            "imovel": {"type": "string", "enum": ["apartamento", "casa", "sitio", "comercio", "home_office"]},
            "pontos": _num("Quantos lugares quer ver."), "wifi": {"type": "string", "enum": ["sim", "nao"]},
            "viaja": {"type": "string", "enum": ["sim", "nao"]}, "porta": {"type": "string", "enum": ["nao", "digital", "facial"]},
            "orcamento": _num("Orçamento em reais (opcional)."), "nome": _txt("Nome do cliente (opcional).")},
         "required": ["imovel"]},
        lambda a: ["atendente-infinity-guard/scripts/recomendar_kit.py"] + [x for k in ("imovel", "pontos", "wifi", "viaja", "porta", "orcamento", "nome") if a.get(k) not in (None, "") for x in ("--" + k, str(a[k]))],
    ),
    "plano_de_midia": (
        "Calcula CPA máximo, CPA alvo, ROAS de equilíbrio e orçamento para uma meta de vendas no Meta Ads, com a régua escalar/manter/pausar.",
        {"type": "object", "properties": {
            "ticket": _num("Ticket médio em reais."), "margem": _num("Margem de 0 a 1 (ex.: 0.30)."),
            "meta_vendas": _num("Vendas desejadas no período."), "dias": _num("Dias do período (padrão 30)."),
            "prova": {"type": "string", "enum": ["pendente", "ok"], "description": "Prova da loja (CNPJ, garantia) no site."}},
         "required": ["ticket", "margem", "meta_vendas"]},
        lambda a: ["plano-de-midia/scripts/midia.py", "plano", "--ticket", str(a["ticket"]), "--margem", str(a["margem"]),
                   "--meta-vendas", str(int(a["meta_vendas"])), "--dias", str(int(a.get("dias") or 30)), "--prova", a.get("prova") or "pendente"],
    ),
    "montar_campanha": (
        "Monta a campanha 11.11 e/ou Black Friday: kits com preço e Pix do catálogo, cupom, calendário e mensagens.",
        {"type": "object", "properties": {
            "evento": {"type": "string", "enum": ["1111", "blackfriday", "ambos"]}, "desconto": _num("Desconto de 0 a 1 (padrão 0.10)."),
            "prova": {"type": "string", "enum": ["pendente", "ok"]}}},
        lambda a: ["campanha-sazonal/scripts/montar_campanha.py", "--evento", a.get("evento") or "ambos", "--desconto", str(a.get("desconto") or 0.10), "--prova", a.get("prova") or "pendente"],
    ),
    "pauta_da_semana": (
        "Gera 3 roteiros de Reels da semana com os temas quentes, sem repetir tema recente.",
        {"type": "object", "properties": {"semana": _txt("Qualquer data AAAA-MM-DD da semana (opcional).")}},
        lambda a: ["conteudo-semanal/scripts/pauta_semana.py"] + (["--semana", a["semana"]] if a.get("semana") else []),
    ),
    "reuniao_semanal": (
        "Monta a pauta da semana por squad, com o top 3 e a fonte de cada item, lendo o estado de todas as skills.",
        {"type": "object", "properties": {"hoje": _txt("Data AAAA-MM-DD (opcional).")}},
        lambda a: ["reuniao-semanal/scripts/reuniao.py"] + (["--hoje", a["hoje"]] if a.get("hoje") else []),
    ),
    "vigiar_gestao": (
        "Aplica as regras de alerta (ERP, CRM, WMS, TMS, VMI) ao backup do app Rota do Milhão e lista o que saiu errado, com o funcionário responsável.",
        {"type": "object", "properties": {"backup": _txt("Caminho do arquivo de backup JSON exportado no app (Gestão → Integrações).")}, "required": ["backup"]},
        lambda a: ["monitor-de-gestao/scripts/monitor.py", "--backup", str(a["backup"])],
    ),
}


def chamar(nome, args):
    desc, schema, montar = FERRAMENTAS[nome]
    faltando = [k for k in schema.get("required", []) if args.get(k) in (None, "")]
    if faltando:
        return "Faltou informar: " + ", ".join(faltando), True
    cmd = montar(args)
    script = SKILLS / cmd[0]
    try:
        r = subprocess.run([sys.executable, str(script)] + cmd[1:], cwd=str(script.parent.parent), capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return "A ferramenta passou de 90 segundos e foi interrompida.", True
    saida = (r.stdout or "").strip()
    if r.stderr.strip() and r.returncode not in (0, 1, 2):
        saida = (saida + "\n" + r.stderr.strip()).strip()
    # os scripts usam 1 e 2 para sinalizar alerta/bloqueio, não erro de execução
    return saida or "(sem saída)", r.returncode not in (0, 1, 2)


def responder(msg):
    metodo, mid = msg.get("method"), msg.get("id")
    if mid is None:  # notificação (ex.: notifications/initialized): não responde
        return None
    if metodo == "initialize":
        pedida = (msg.get("params") or {}).get("protocolVersion")
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": pedida if pedida in PROTOCOLOS else PROTOCOLOS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "infinity-guard", "version": VERSAO},
            "instructions": "Ferramentas da Infinity Guard (dropshipping de câmeras, alarmes e fechaduras). Só leem e calculam: nada publica, gasta ou envia mensagem."}}
    if metodo == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if metodo == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": [
            {"name": n, "description": d, "inputSchema": s, "annotations": {"readOnlyHint": True, "openWorldHint": False}}
            for n, (d, s, _) in FERRAMENTAS.items()]}}
    if metodo == "tools/call":
        p = msg.get("params") or {}
        nome = p.get("name")
        if nome not in FERRAMENTAS:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"Ferramenta desconhecida: {nome}"}}
        texto, erro = chamar(nome, p.get("arguments") or {})
        return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": texto}], "isError": erro}}
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Método não suportado: {metodo}"}}


def main():
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError:
            out = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}
        else:
            out = responder(msg)
        if out is not None:
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
