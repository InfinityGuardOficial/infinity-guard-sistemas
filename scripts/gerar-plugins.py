#!/usr/bin/env python3
"""Gera um plugin por squad em plugins/ a partir de agents/ e skills/ (a fonte continua sendo a raiz).

Cada plugin leva os agentes do squad, as skills que eles carregam e sempre a atendente-infinity-guard
(catálogo único de preços, lido pelas outras skills) e o revisor-de-promessas (regra da casa).
Uso: python3 scripts/gerar-plugins.py   (rode de novo sempre que mudar um agente ou uma skill)
"""
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = ["atendente-infinity-guard", "revisor-de-promessas"]
SQUADS = {
    "Direção": ("direcao", "Squad Direção: o diretor-geral, que decide as prioridades da semana e divide as metas entre os squads."),
    "Vendas": ("vendas", "Squad Vendas: consultor de WhatsApp, recuperador de carrinho, vendedor B2B e o líder de vendas."),
    "Sucesso do Cliente": ("sucesso-cliente", "Squad Sucesso do Cliente: técnico de suporte, guardião do pós-venda e o líder do squad."),
    "Marketing e Conteúdo": ("marketing", "Squad Marketing e Conteúdo: roteirista de Reels, copywriter da loja, social media e o líder de marketing."),
    "Tráfego Pago": ("trafego", "Squad Tráfego Pago: criativos de anúncio, analista de mídia e o líder de tráfego."),
    "Operações e Loja": ("operacoes", "Squad Operações e Loja: auditor da loja, gestor de catálogo, guardião de conformidade e o líder de operações."),
    "Dados e Inteligência": ("dados", "Squad Dados e Inteligência: analista de vendas, detetive de mercado e o líder de dados."),
}
# Skills que leem o estado de outras instaladas ao lado: vão junto no mesmo plugin.
DEPENDE = {
    "reuniao-semanal": ["atendente-infinity-guard", "campanha-sazonal", "conteudo-semanal", "painel-de-vendas",
                        "prova-da-loja", "radar-de-concorrentes", "suporte-tecnico"],
}
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", "custos.json", "estoque.json")


def ler_agente(caminho):
    texto = caminho.read_text(encoding="utf-8")
    fm = re.search(r"^---\n(.*?)\n---", texto, re.S).group(1)
    skills = re.findall(r"^\s+-\s+(\S+)", fm.split("skills:", 1)[1], re.M) if "skills:" in fm else []
    squad = re.search(r"^# .* · Squad (.*)$", texto, re.M).group(1)
    return squad, skills


def main():
    raiz_manifesto = json.loads((RAIZ / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    versao = raiz_manifesto["version"]
    grupos = {}
    for ag in sorted((RAIZ / "agents").glob("*.md")):
        squad, skills = ler_agente(ag)
        g = grupos.setdefault(squad, {"agentes": [], "skills": set(BASE)})
        g["agentes"].append(ag)
        g["skills"].update(skills)
    for g in grupos.values():
        for s in list(g["skills"]):
            g["skills"].update(DEPENDE.get(s, []))

    destino = RAIZ / "plugins"
    if destino.exists():
        shutil.rmtree(destino)
    entradas = []
    for squad in [q for q in SQUADS if q in grupos]:
        g = grupos[squad]
        slug, descricao = SQUADS[squad]
        nome = f"infinity-guard-{slug}"
        p = destino / nome
        (p / ".claude-plugin").mkdir(parents=True)
        (p / "agents").mkdir()
        for ag in g["agentes"]:
            shutil.copy2(ag, p / "agents" / ag.name)
        for s in sorted(g["skills"]):
            shutil.copytree(RAIZ / "skills" / s, p / "skills" / s, ignore=IGNORAR)
        manifesto = {
            "name": nome,
            "version": versao,
            "description": descricao + " Skills: " + ", ".join(sorted(g["skills"])) + ".",
            "author": raiz_manifesto["author"],
            "homepage": raiz_manifesto.get("homepage", ""),
            "keywords": ["infinity-guard", "squad", slug],
        }
        (p / ".claude-plugin/plugin.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        agentes = ", ".join(f"`{a.stem}`" for a in g["agentes"])
        (p / "README.md").write_text(
            f"# {nome} · {versao}\n\n{descricao}\n\n- Funcionários: {agentes}\n- Skills: "
            + ", ".join(f"`{s}`" for s in sorted(g["skills"]))
            + f"\n\nInstalar:\n```\n/plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas\n/plugin install {nome}@infinity-guard-sistemas\n```\n\n"
            "Gerado por `scripts/gerar-plugins.py` a partir de `agents/` e `skills/` da raiz: edite lá, não aqui.\n",
            encoding="utf-8")
        entradas.append({"name": nome, "source": f"./plugins/{nome}", "description": descricao, "version": versao})
        print(f"{nome}: {len(g['agentes'])} funcionários, {len(g['skills'])} skills")

    mk_caminho = RAIZ / ".claude-plugin/marketplace.json"
    mk = json.loads(mk_caminho.read_text(encoding="utf-8"))
    completo = [e for e in mk["plugins"] if e["name"] == "infinity-guard"]
    mk["plugins"] = completo + entradas
    mk_caminho.write_text(json.dumps(mk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
