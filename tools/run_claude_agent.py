#!/usr/bin/env python3
"""Dispara um funcionário (agente) do plugin infinity-guard pelo Claude Code, sem interação, e guarda a resposta.

Uso:
  python3 tools/run_claude_agent.py --agente analista-de-vendas --tarefa "Resuma as vendas da semana" [--evento relatorio_diario]
  IG_DRY_RUN=1 python3 tools/run_claude_agent.py ...   # só mostra o comando, não chama o Claude

O agente roda em modo de leitura: lê arquivos e roda os scripts das skills, mas não edita arquivos e não
usa conectores (Meta, etc.). Tudo o que ele sugerir que gaste dinheiro, mexa em anúncio, preço, loja ou fale
com cliente vira pedido de aprovação em logs/aprovacoes.json; quem executa é o max.
A resposta fica em logs/agentes/AAAA-MM-DD_HHMM_<evento>_<agente>.md.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos  # noqa: E402
from core.caminhos import REPO  # noqa: E402

AGENTES = sorted(p.stem for p in (REPO / "agents").glob("*.md"))
REGRAS = (
    "Regras deste disparo automático (orquestrador da Infinity Guard, ver .claude/CLAUDE.md): "
    "você está em modo de leitura. Não edite arquivos e não grave nada (nenhum --gravar). "
    "Não gaste dinheiro, não altere anúncios, preços nem a loja e não envie mensagem a cliente. "
    "Se recomendar alguma dessas ações, escreva no fim uma seção exatamente com o título "
    "'## Pedidos de aprovação' e uma linha por ação, começando com '- '. Responda em português."
)
# Bash só para os scripts das skills (no Windows o caminho pode vir com \ ou com /).
FERRAMENTAS = ["Read", "Glob", "Grep", "Task"] + sorted({f"Bash({py} {raiz}{sep}skills{sep}*)"
                                                       for py in ("python3", "python", "py")
                                                       for raiz, sep in ((str(REPO), os.sep), (REPO.as_posix(), "/"))})
PROIBIDAS = ["Write", "Edit", "NotebookEdit", "WebFetch", "mcp__Meta"]


def comando(agente, tarefa, max_turnos=30):
    """Devolve (comando, prompt). O prompt vai pela entrada padrão: no Windows o claude.cmd estraga argumento
    com quebra de linha ou aspas."""
    if agente not in AGENTES:
        raise ValueError(f"agente '{agente}' não existe. Opções: {', '.join(AGENTES)}")
    claude = os.environ.get("IG_CLAUDE_BIN") or shutil.which("claude") or "claude"
    prompt = (f"Use o subagente infinity-guard:{agente} (ferramenta Task) para esta tarefa e devolva a resposta dele "
              f"completa.\n\nTarefa: {tarefa}\n\n{REGRAS}")
    return [claude, "-p", "--plugin-dir", str(REPO), "--output-format", "text",
            "--max-turns", str(max_turnos), "--allowedTools", *FERRAMENTAS, "--disallowedTools", *PROIBIDAS], prompt


def pedidos_de_aprovacao(texto):
    m = re.search(r"^##\s*Pedidos de aprova[çc][ãa]o\s*$(.*?)(?=^##\s|\Z)", texto, re.M | re.S | re.I)
    if not m:
        return []
    return [l.strip()[2:].strip() for l in m.group(1).splitlines() if l.strip().startswith(("- ", "* "))]


def registrar_aprovacoes(agente, evento, pedidos, relatorio):
    if not pedidos:
        return 0
    f = caminhos.logs() / "aprovacoes.json"
    lista = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    agora = datetime.now().isoformat(timespec="seconds")
    for p in pedidos:
        lista.append({"criado_em": agora, "agente": agente, "evento": evento, "acao": p,
                      "relatorio": relatorio, "status": "aguardando_max"})
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(lista, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)
    return len(pedidos)


def rodar(agente, tarefa, evento="manual", timeout_min=15, max_turnos=30, executar=subprocess.run):
    cmd, prompt = comando(agente, tarefa, max_turnos)
    pasta = caminhos.logs() / "agentes"
    pasta.mkdir(parents=True, exist_ok=True)
    saida = pasta / f"{datetime.now():%Y-%m-%d_%H%M%S}_{evento}_{agente}.md"
    seco = os.environ.get("IG_DRY_RUN") == "1" or (not os.environ.get("IG_CLAUDE_BIN") and not shutil.which("claude"))
    if seco:
        texto = "(simulação: Claude não chamado)\n\n```\n" + " ".join(repr(c) if " " in c else c for c in cmd) + "\n```\n\nPrompt:\n\n" + prompt + "\n"
        codigo = 0
    else:
        extra = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        r = executar(cmd, input=prompt, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
                     timeout=timeout_min * 60, **extra)
        texto, codigo = r.stdout or "", r.returncode
        if codigo != 0:
            texto += f"\n\n[erro {codigo}]\n{r.stderr or ''}"
    saida.write_text(f"# {agente} · {evento} · {datetime.now():%d/%m/%Y %H:%M}\n\n**Tarefa:** {tarefa}\n\n{texto}",
                     encoding="utf-8")
    n = registrar_aprovacoes(agente, evento, pedidos_de_aprovacao(texto), saida.name)
    return {"ok": codigo == 0, "simulacao": seco, "arquivo": str(saida), "aprovacoes": n, "codigo": codigo}


def main():
    caminhos.terminal_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agente", required=True, choices=AGENTES)
    ap.add_argument("--tarefa", required=True)
    ap.add_argument("--evento", default="manual")
    a = ap.parse_args()
    r = rodar(a.agente, a.tarefa, a.evento)
    print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
