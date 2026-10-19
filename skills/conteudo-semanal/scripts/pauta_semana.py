#!/usr/bin/env python3
"""Pauta da semana da Infinity Guard: 3 roteiros de Reels com os temas quentes, sem repetir tema recente.

Uso:
  python3 pauta_semana.py                         (semana que começa na próxima segunda)
  python3 pauta_semana.py --semana 2026-11-23     (qualquer data; usa a segunda daquela semana)
  python3 pauta_semana.py --registrar             (grava os temas escolhidos no histórico)
  python3 pauta_semana.py --anatel-publicado      (libera temas que dependem do código Anatel no site)
  ... --json | --saida pautas/2026-10-19.md

Regras: tema repetido só depois de 2 semanas; nas semanas do 11.11 e da Black Friday, o tema da campanha entra primeiro;
os 3 roteiros usam formatos diferentes.
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
TEMAS = AQUI / "references" / "temas.json"
HISTORICO = AQUI / "pautas" / "historico.json"
INTERVALO = 2  # semanas sem repetir tema
CAMPANHA = {"2026-11-09": "1111", "2026-11-23": "blackfriday"}  # segunda da semana -> evento
TEMA_CAMPANHA = {"1111": "black-friday-olhar", "blackfriday": "black-friday-olhar"}
DIAS_POST = ["segunda", "quarta", "sexta"]


def segunda(dia):
    return dia - timedelta(days=dia.weekday())


def proxima_segunda(hoje=None):
    hoje = hoje or date.today()
    return hoje + timedelta(days=(7 - hoje.weekday()) % 7 or 7)


def carregar(caminho=TEMAS):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def ler_historico(caminho=HISTORICO):
    p = Path(caminho)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def disponivel(t, semana, anatel):
    if t.get("requer") == "anatel_publicado" and not anatel:
        return False
    j = t.get("janela")
    if j and not (date.fromisoformat(j[0]) <= semana + timedelta(days=6) and semana <= date.fromisoformat(j[1])):
        return False
    return True


def escolher(semana, dados, historico, anatel=False, n=3):
    semana = segunda(semana)
    recentes = set()
    for k, ids in historico.items():
        dk = date.fromisoformat(k)
        if dk != semana and 0 < (semana - dk).days <= INTERVALO * 7:
            recentes.update(ids)
    temas = [t for t in dados["temas"] if disponivel(t, semana, anatel)]
    # ordem estável que gira a cada semana
    giro = semana.isocalendar()[1] % len(temas) if temas else 0
    temas = temas[giro:] + temas[:giro]
    escolhidos = []
    ev = CAMPANHA.get(semana.isoformat())
    if ev:
        t = next((t for t in temas if t["id"] == TEMA_CAMPANHA[ev]), None)
        if t:
            escolhidos.append(t)
    for passo in (lambda t: t["id"] not in recentes, lambda t: True):  # se faltar tema novo, aceita repetido
        for t in temas:
            if len(escolhidos) == n:
                break
            if t in escolhidos or not passo(t):
                continue
            if any(e["formato"] == t["formato"] for e in escolhidos):
                continue
            escolhidos.append(t)
    return escolhidos, ev


def roteiro(t, dados, dia):
    return {"dia": dia, "tema": t["id"], "formato": dados["formatos"][t["formato"]], "fonte": t["fonte"],
            "ganchos": t["gancho"], "fala": t["fala"], "texto_na_tela": t["tela"],
            "legenda": t["legenda"] + " " + dados["cta"], "produto": t["produto"]}


def pauta(semana=None, historico=None, anatel=False, dados=None):
    dados = dados or carregar()
    semana = segunda(semana or proxima_segunda())
    historico = ler_historico() if historico is None else historico
    escolhidos, ev = escolher(semana, dados, historico, anatel)
    idade = (date.today() - date.fromisoformat(dados["atualizado_em"])).days
    avisos = []
    if idade > 45:
        avisos.append(f"banco de temas com {idade} dias: rode o Detetive de Nicho para renovar os temas quentes")
    if ev:
        avisos.append(f"semana de campanha ({ev}): use as mensagens e o calendário da skill campanha-sazonal")
    return {"semana": semana.isoformat(), "campanha": ev, "avisos": avisos,
            "roteiros": [roteiro(t, dados, DIAS_POST[i]) for i, t in enumerate(escolhidos)]}


def para_md(p):
    s = date.fromisoformat(p["semana"])
    L = [f"# Pauta da semana · {s:%d/%m} a {s + timedelta(days=6):%d/%m/%Y}", ""]
    L += [f"- ⚠️ {a}" for a in p["avisos"]] + ([""] if p["avisos"] else [])
    for i, r in enumerate(p["roteiros"], 1):
        L += [f"## {i}. {r['dia'].capitalize()} · {r['formato']} · `{r['tema']}`", "",
              f"Base: {r['fonte']}", "",
              "**Gancho (escolha 1, nos 3 primeiros segundos):**"] + [f"- {g}" for g in r["ganchos"]] + [
              "", "**Fala (30 a 45 segundos, olhando pra câmera):**"] + [f"{n}. {f}" for n, f in enumerate(r["fala"], 1)] + [
              "", "**Texto na tela:** " + " → ".join(r["texto_na_tela"]), "",
              "**Legenda:**", "```", r["legenda"], "```", ""]
    L += ["Regras: grave com o seu celular, mostre o produto de verdade quando puder, não invente história de cliente "
          "e só cite número que tem fonte. Para variar a fala, peça à Máquina de Reels com este tema e esta base."]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semana")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--anatel-publicado", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    p = pauta(date.fromisoformat(a.semana) if a.semana else None, anatel=a.anatel_publicado)
    out = json.dumps(p, ensure_ascii=False, indent=2) if a.json else para_md(p)
    if a.saida:
        Path(a.saida).write_text(out, encoding="utf-8")
    if a.registrar:
        h = ler_historico()
        h[p["semana"]] = [r["tema"] for r in p["roteiros"]]
        HISTORICO.parent.mkdir(exist_ok=True)
        HISTORICO.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
