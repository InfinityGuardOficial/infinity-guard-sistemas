"""Rotinas automáticas que só leem e geram relatórios: nenhuma gasta, publica, muda a loja ou fala com cliente.

Cada rotina roda o script de uma skill direto (sem Claude), guarda a saída em logs/rotinas/<rotina>/ e, quando
acha algo para resolver, devolve um evento para a fila chamar o funcionário responsável.

| rotina    | quando (config "rotinas") | script                                   | chama quando acha algo |
|-----------|---------------------------|------------------------------------------|------------------------|
| catalogo  | todo dia                  | catalogo-e-precos/catalogo.py validar    | gestor-de-catalogo     |
| gestao    | todo dia                  | monitor-de-gestao/monitor.py (backup do app em dados/app/) | lider-operacoes |
| conteudo  | segunda                   | conteudo-semanal/pauta_semana.py         | roteirista-de-reels (sempre) |
| radar     | quarta                    | radar-de-concorrentes/radar.py velhas    | detetive-de-mercado    |
| auditoria | quinta                    | prova-da-loja/auditar.py --catalogo      | auditor-da-loja        |
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from core import caminhos
from core.caminhos import REPO

SKILLS = REPO / "skills"


def _script(skill, nome, *args, timeout=180):
    r = subprocess.run([sys.executable, str(SKILLS / skill / "scripts" / nome), *args], capture_output=True,
                       text=True, encoding="utf-8", timeout=timeout, cwd=str(SKILLS / skill))
    return r.returncode, r.stdout, r.stderr


def _pasta(rotina):
    p = caminhos.logs() / "rotinas" / rotina
    p.mkdir(parents=True, exist_ok=True)
    return p


def _salvar(rotina, hoje, conteudo, ext="json"):
    f = _pasta(rotina) / f"{hoje}.{ext}"
    f.write_text(conteudo, encoding="utf-8")
    return f


def _evento(tipo, agente, tarefa):
    return {"type": tipo, "details": {"agente": agente, "tarefa": tarefa}}


def catalogo(hoje):
    rc, out, err = _script("catalogo-e-precos", "catalogo.py", "--json", "validar")
    r = json.loads(out)
    f = _salvar("catalogo", hoje, out)
    resumo = f"{r['ativos']} produtos ativos, catálogo com {r['idade_dias']} dias, {len(r['erros'])} erro(s), {len(r['avisos'])} aviso(s)"
    if r["erros"] or r["avisos"] or r["idade_dias"] > 30:
        return resumo, _evento("catalogo_com_problema", "gestor-de-catalogo",
                               f"A validação do catálogo de hoje ({f}) achou: {resumo}. Diga o que corrigir, produto "
                               "por produto, e o comando de atualização (sem --gravar).")
    return resumo, None


def gestao(hoje):
    backups = sorted((caminhos.dados() / "app").glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not backups:
        return "sem backup do app em dados/app/ (Gestão → Integrações → Backup completo)", None
    rc, out, err = _script("monitor-de-gestao", "monitor.py", "--backup", str(backups[-1]), "--json")
    if rc not in (0, 1, 2):
        raise RuntimeError(err.strip() or f"monitor.py saiu com {rc}")
    alertas = json.loads(out)
    f = _salvar("gestao", hoje, out)
    graves = [a for a in alertas if a["nivel"] in ("critico", "alto")]
    resumo = f"{len(alertas)} alerta(s), {len(graves)} crítico(s) ou alto(s), backup {backups[-1].name}"
    if graves:
        linhas = "; ".join(f"{a['regra']} ({a['nivel']}, {a['qtd']}x, cuida: {a['responsavel']})" for a in graves)
        return resumo, _evento("alertas_da_gestao", "lider-operacoes",
                               f"O vigia da gestão ({f}) achou: {linhas}. Diga, para cada alerta, quem faz o quê hoje.")
    return resumo, None


def conteudo(hoje):
    d = datetime.fromisoformat(hoje).date()
    semana = (d + timedelta(days=(7 - d.weekday()) % 7)).isoformat()
    f = _pasta("conteudo") / f"pauta-{semana}.md"
    rc, out, err = _script("conteudo-semanal", "pauta_semana.py", "--semana", semana, "--saida", str(f))
    if rc != 0:
        raise RuntimeError(err.strip() or f"pauta_semana.py saiu com {rc}")
    return f"pauta da semana de {semana} em {f.name}", _evento(
        "pauta_de_conteudo", "roteirista-de-reels",
        f"A pauta da semana de {semana} está em {f}. Revise os 3 roteiros, passe cada texto pelo "
        "revisor-de-promessas e devolva a versão pronta para gravar. Não publique e não registre no histórico.")


def radar(hoje):
    rc, out, err = _script("radar-de-concorrentes", "radar.py", "--json", "velhas")
    velhas = json.loads(out)
    _salvar("radar", hoje, out)
    if velhas:
        nomes = "; ".join(f"{v.get('concorrente')} {v.get('produto')}" for v in velhas[:10])
        return f"{len(velhas)} preço(s) de concorrente com mais de 30 dias", _evento(
            "radar_desatualizado", "detetive-de-mercado",
            f"Estes preços de concorrentes estão velhos: {nomes}. Diga onde conferir cada um e o comando "
            "radar.py registrar para quando o dono confirmar (não registre).")
    return "preços dos concorrentes em dia", None


def auditoria(hoje):
    rc, out, err = _script("prova-da-loja", "auditar.py", "--catalogo", "--json", timeout=300)
    if rc != 0:
        raise RuntimeError(err.strip()[-300:] or f"auditar.py saiu com {rc}")
    r = json.loads(out)
    f = _salvar("auditoria", hoje, out)
    faltas = sorted({i["chave"] for p in r["paginas"] for i in p["itens"] if i["status"] == "falta"})
    resumo = f"{len(r['paginas'])} página(s) lidas, faltando: {', '.join(faltas) or 'nada'}"
    if faltas:
        return resumo, _evento("auditoria_da_loja", "auditor-da-loja",
                               f"A auditoria do site de hoje ({f}) mostra faltando: {', '.join(faltas)}. "
                               "Liste a correção de cada item na ordem que mais destrava venda.")
    return resumo, None


ROTINAS = {"catalogo": catalogo, "gestao": gestao, "conteudo": conteudo, "radar": radar, "auditoria": auditoria}


def devidas(cfg, estado, agora, disponiveis=ROTINAS):
    hoje = agora.date().isoformat()
    feitas = estado.get("rotinas", {})
    saida = []
    for nome, r in cfg.get("rotinas", {}).items():
        if not r.get("ativa") or nome not in disponiveis or feitas.get(nome) == hoje:
            continue
        if agora.hour < cfg["hora_relatorio_diario"]:
            continue
        if r["frequencia"] == "semanal" and agora.weekday() != r.get("dia", 0):
            continue
        saida.append(nome)
    return saida


def rodar(cfg, estado, agora=None, rotinas=None):
    """Roda as rotinas devidas. Devolve (resultados, eventos, novo_estado)."""
    agora = agora or datetime.now()
    hoje = agora.date().isoformat()
    estado = dict(estado)
    estado["rotinas"] = dict(estado.get("rotinas", {}))
    rotinas = ROTINAS if rotinas is None else rotinas
    resultados, eventos = [], []
    for nome in devidas(cfg, estado, agora, rotinas):
        try:
            resumo, evento = rotinas[nome](hoje)
            resultados.append({"rotina": nome, "ok": True, "resumo": resumo})
            if evento:
                eventos.append(evento)
        except Exception as e:
            resultados.append({"rotina": nome, "ok": False, "resumo": f"{type(e).__name__}: {e}"})
        estado["rotinas"][nome] = hoje  # não repete no mesmo dia, nem quando falha (o erro fica no resumo)
    return resultados, eventos, estado
