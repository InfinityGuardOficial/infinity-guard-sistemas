#!/usr/bin/env python3
"""Central da Infinity Guard: junta num arquivo só onde está cada coisa e como ela está hoje.

Uso:
  python3 tools/central.py                       # escreve docs/central.md (a versão do repositório)
  python3 tools/central.py --saida logs/central.md --com-orquestrador
  python3 tools/central.py --projeto /mnt/project-files --saida .../central.md   (inclui os arquivos do projeto)

Tudo sai dos arquivos: catálogo, organograma, skills, última auditoria, reunião, pauta, campanha e, com
--com-orquestrador, o resumo do dia e as aprovações do computador onde o daemon roda. Nada é estimado.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import caminhos  # noqa: E402
from core.caminhos import REPO  # noqa: E402

SEGURANCA = ("camera", "alarme", "fechadura", "sensor")
GITHUB = "https://github.com/InfinityGuardOficial/infinity-guard-sistemas/blob/main/"
_github = False  # --github: links do repositório viram links do GitHub (para a cópia fora do repositório)


def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mais_novo(pasta, padrao="*.md"):
    arquivos = sorted(Path(pasta).glob(padrao)) if Path(pasta).exists() else []
    return arquivos[-1] if arquivos else None


def _rel(p, base):
    try:
        return Path(os.path.relpath(Path(p).resolve(), Path(base).resolve())).as_posix()
    except ValueError:  # Windows: outro disco
        return Path(p).resolve().as_posix()


def _link(p, base, texto=None):
    if _github and Path(p).resolve().is_relative_to(REPO):
        r = Path(p).resolve().relative_to(REPO).as_posix()
        return f"[{texto or r}]({GITHUB}{r.replace(' ', '%20')})"
    r = _rel(p, base)
    return f"[{texto or r}]({r.replace(' ', '%20')})"


def _nome_curto(p, todos):
    curto = p["nome"].split(" — ")[0]
    if sum(1 for q in todos if q["nome"].split(" — ")[0] == curto) > 1 and " — " in p["nome"]:
        curto += f" ({p['nome'].split(' — ')[1].split(',')[0].strip()})"
    return curto


def _skills():
    saida = []
    for s in sorted((REPO / "skills").glob("*/SKILL.md")):
        m = re.search(r"^description:\s*(.+)$", s.read_text(encoding="utf-8"), re.M)
        desc = (m.group(1) if m else "").strip().strip('"')
        saida.append((s.parent.name, desc.split(". ")[0].rstrip(".")))
    return saida


def _squads():
    texto = (REPO / "docs" / "organograma.md").read_text(encoding="utf-8")
    squads = []
    for bloco in re.split(r"^## ", texto, flags=re.M)[1:]:
        titulo, _, corpo = bloco.partition("\n")
        nomes = [n for n in re.findall(r"^\|\s*\**([a-z0-9-]+)\**", corpo, re.M) if (REPO / "agents" / f"{n}.md").exists()]
        if nomes:
            squads.append((titulo.strip(), nomes))
    return squads


def gerar(base, projeto=None, com_orquestrador=False, agora=None):
    agora = agora or datetime.now()
    cat = json.loads((REPO / "skills/atendente-infinity-guard/references/catalogo.json").read_text(encoding="utf-8"))
    ativos = [p for p in cat["produtos"] if p.get("ativo")]
    seg = [p for p in ativos if any(k in (p.get("categoria", "") + p["id"]).lower() for k in SEGURANCA)]
    squads = _squads()
    skills = _skills()
    auditoria = _mais_novo(REPO / "skills/prova-da-loja/auditorias")
    nota = re.search(r"\*\*Nota de prova: ([^*]+)\*\*", auditoria.read_text(encoding="utf-8")) if auditoria else None
    reuniao = _mais_novo(REPO / "docs/reunioes")
    pauta = _mais_novo(REPO / "skills/conteudo-semanal/pautas")
    campanha = _mais_novo(REPO / "skills/campanha-sazonal/campanhas")
    L = [f"# Central Infinity Guard",
         f"_Gerada em {agora:%d/%m/%Y %H:%M} por `tools/central.py`. Para atualizar: `python3 tools/central.py`._", "",
         "**Segurança onde você estiver.** Tudo do sistema num lugar só: o que existe, onde está e como está hoje.", "",
         "## Comece aqui", "",
         f"- Instalar a equipe e as skills: {_link(REPO / 'README.md', base, 'README')} (seção \"Instalar tudo de uma vez\").",
         f"- Ligar o orquestrador no seu computador: {_link(REPO / 'README.md', base, 'README')} (seção \"Orquestrador automático\").",
         f"- Regras da casa para o Claude: {_link(REPO / '.claude/CLAUDE.md', base, '.claude/CLAUDE.md')} e {_link(REPO / 'CLAUDE.md', base, 'CLAUDE.md')}.",
         "- Regra de suporte (21/10/2026): a loja tira dúvidas no WhatsApp e o manual de instruções acompanha o produto; "
         "ela não configura o produto por WhatsApp nem por vídeo (o revisor barra essa promessa).",
         f"- Onde mora cada dado e quem cuida: {_link(REPO / 'docs/mapa-de-dados.md', base)}.",
         f"- O que roda sozinho e o que espera você: {_link(REPO / 'docs/mapa-da-autonomia.md', base)}. "
         "No celular, a aba Central do app Rota do Milhão mostra o mesmo em tempo real.",
         f"- Hábitos e decisões dos milionários que começaram do zero (pesquisa com fontes, aba Mente do app): {_link(REPO / 'docs/mente-de-milionario.md', base)}.", "",
         "## Como está hoje", "",
         f"- **Catálogo** ({cat.get('atualizado_em', 's/ data')}): {len(ativos)} produtos ativos, {len(seg)} de segurança: "
         + "; ".join(f"{_nome_curto(p, seg)} {_brl(p['preco'])}" for p in seg) + ".",
         f"- **Equipe:** {sum(len(n) for _, n in squads)} funcionários em {len(squads)} squads; {len(skills)} skills.",
         (f"- **Prova da loja:** nota {nota.group(1).rstrip('.')} na auditoria {_link(auditoria, base, auditoria.stem)}." if nota
          else "- **Prova da loja:** nenhuma auditoria salva."),
         (f"- **Última reunião:** {_link(reuniao, base, reuniao.stem)}." if reuniao else "- **Última reunião:** nenhuma."),
         (f"- **Pauta de conteúdo mais nova:** {_link(pauta, base, pauta.stem)}." if pauta else ""),
         (f"- **Campanha:** {_link(campanha, base, campanha.stem)}." if campanha else "")]
    if com_orquestrador:
        logs = caminhos.logs()
        resumo = _mais_novo(logs / "resumo")
        aprov = json.loads((logs / "aprovacoes.json").read_text(encoding="utf-8")) if (logs / "aprovacoes.json").exists() else []
        pend = [a for a in aprov if a["status"] == "aguardando_max"]
        hb = logs / "daemon.heartbeat"
        L += ["", "## Orquestrador neste computador", "",
              f"- Último ciclo: {hb.read_text(encoding='utf-8') if hb.exists() else 'nunca rodou'}.",
              f"- Resumo do dia: {_link(resumo, base) if resumo else 'ainda não há'}.",
              f"- Esperando o seu \"pode\": {len(pend)} pedido(s). Veja com `python core/daemon_orchestrator.py aprovacoes`."]
        L += [f"  - [{a['agente']}] {a['acao']}" for a in pend[-10:]]
    else:
        L += ["- **Orquestrador:** roda no seu computador. Lá, `python core/daemon_orchestrator.py status` mostra o estado, "
              "e `logs/central.md` é esta mesma página com o resumo do dia e as aprovações."]

    L += ["", "## A equipe", "", "| Squad | Funcionários |", "|---|---|"]
    L += [f"| {t} | " + ", ".join(_link(REPO / 'agents' / f'{n}.md', base, n) for n in nomes) + " |" for t, nomes in squads]
    L += ["", f"Quem é quem e quando chamar: {_link(REPO / 'docs/organograma.md', base)}.", "",
          "## As skills", "", "| Skill | Para quê |", "|---|---|"]
    L += [f"| {_link(REPO / 'skills' / n / 'SKILL.md', base, n)} | {d} |" for n, d in skills]

    L += ["", "## Índice de tudo", "", "| Onde | O que é |", "|---|---|"]
    indice = [
        ("docs/raio-x-de-nicho.md", "Raio X do mercado de segurança residencial (18/10/2026): concorrentes, preços e brechas"),
        ("docs/raio-x-de-nicho.html", "O mesmo Raio X, versão visual"),
        ("docs/mapa-de-sistemas.md", "A ordem dos sistemas e o status de cada um"),
        ("docs/mapa-de-dados.md", "Fonte da verdade de cada dado"),
        ("docs/mapa-da-autonomia.md", "Nível de autonomia: o que roda sozinho, o que espera o seu \"pode\" e o que está bloqueado"),
        ("docs/organograma.md", "Os 23 funcionários e quando chamar cada um"),
        ("docs/reunioes", "Atas das reuniões da equipe"),
        ("skills/prova-da-loja/auditorias", "Auditorias do site"),
        ("skills/campanha-sazonal/campanhas", "Propostas de campanha (11.11 e Black Friday)"),
        ("skills/conteudo-semanal/pautas", "Pautas de Reels já geradas"),
        ("skills/atendente-infinity-guard/references/catalogo.json", "Catálogo único de preços"),
        ("app/rota-do-milhao.html", "App Rota do Milhão (gestão, equipe, publicar, placar)"),
        ("desktop", "App do Windows (Electron)"),
        ("android", "App Android"),
        ("mcp_servers", "Servidor MCP com as ferramentas das skills"),
        ("core", "Orquestrador: daemon, fila, regras, rotinas, aprovações e resumo"),
        ("tools", "Coleta de métricas (Nuvemshop e Meta, só leitura), disparo dos agentes e esta central"),
        ("config/orquestrador.json", "Padrões do orquestrador (o seu ajuste vai em orquestrador.local.json)"),
        ("plugins", "Um plugin por squad (gerado)"),
        ("dados", "Onde você coloca os CSVs da Nuvemshop e da Meta e o backup do app (fora do Git)"),
    ]
    L += [f"| {_link(REPO / c, base, c)} | {d} |" for c, d in indice if (REPO / c).exists()]

    if projeto:
        projeto = Path(projeto)
        extras = [
            ("Raio X de Nicho — Infinity Guard.md", "Raio X de 17/10 (primeira versão)"),
            ("infinity-guard/raio-x-de-nicho.md", "Raio X ampliado de 18/10"),
            ("Relatório de Posicionamento — Maximiliano Silva.md", "Seu posicionamento (17/10): quem você é, tese, o que vender primeiro"),
            ("infinity-guard/mapa-de-sistemas.md", "Mapa de sistemas (cópia do projeto)"),
            ("infinity-guard/verificacao/2026-10-19-verificacao-geral.md", "Verificação geral de 19/10 (testes, agentes, correções)"),
            ("infinity-guard/equipe/README.md", "A equipe por squad (cópia do projeto)"),
            ("infinity-guard/skills", "Skills e .zip para enviar no claude.ai"),
            ("infinity-guard/repo-infinity-guard-sistemas", "Cópia antiga do pacote do repositório (18 e 19/10)"),
        ]
        extras += [(f.name, "Mapa da Clareza") for f in projeto.glob("mapa-da-clareza*.md")]
        L += ["", "## Arquivos do projeto", "", "| Arquivo | O que é |", "|---|---|"]
        L += [f"| {_link(projeto / c, base, c)} | {d} |" for c, d in extras if (projeto / c).exists()]
        L += ["", "Repositório: https://github.com/InfinityGuardOficial/infinity-guard-sistemas (privado)."]
    return "\n".join(l for l in L if l is not None) + "\n"


def salvar(saida, projeto=None, com_orquestrador=False, agora=None):
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(gerar(saida.parent, projeto, com_orquestrador, agora), encoding="utf-8")
    return saida


def main():
    caminhos.terminal_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=str(REPO / "docs" / "central.md"))
    ap.add_argument("--projeto")
    ap.add_argument("--com-orquestrador", action="store_true")
    ap.add_argument("--github", action="store_true", help="links do repositório apontam para o GitHub")
    a = ap.parse_args()
    global _github
    _github = a.github
    print(f"central salva em {salvar(a.saida, a.projeto, a.com_orquestrador)}")


if __name__ == "__main__":
    main()
