---
name: reuniao-semanal
description: Reunião semanal e direção da Infinity Guard. Use toda segunda (ou quando pedirem "o que fazer essa semana", "prioridades", "status da empresa", "reunião", "plano da semana") para ler o estado de todas as skills e montar a pauta por squad com o top 3 da semana, prazos de campanha e pendências de prova da loja.
---

# Reunião Semanal — a empresa inteira numa página

A Infinity Guard funciona com 7 squads de funcionários (agentes do plugin `infinity-guard`). Toda segunda, o Diretor Geral roda esta skill, decide as 3 prioridades e passa cada uma para o líder do squad certo.

Arquivos:
- `scripts/reuniao.py`: lê catálogo, ofertas e datas de campanha, auditorias da prova da loja, histórico de pautas, banco de temas, radar de concorrentes e painéis, e monta a pauta com prioridade (P1 a P3) e a fonte de cada linha.
- `references/organograma.md`: quem é quem nos squads e qual funcionário chamar para cada tipo de trabalho.

## Modos

### 1. Pauta da semana
```bash
python3 scripts/reuniao.py --saida reunioes/$(date +%F).md
```
Entregue ao dono o top 3 e uma linha por squad. Pergunte só o que o script lista em "trazer".

### 2. Distribuir o trabalho
Para cada prioridade, chame o funcionário do `references/organograma.md` (no Claude Code: "use o agente lider-vendas para ...", ou deixe o Claude escolher pelo pedido). Trabalho que atravessa squads começa no líder do squad dono do resultado.

### 3. Fechar a semana
Na sexta, peça a cada líder o que entregou e o que travou. O que trava por algo que só o dono pode fazer (documento, senha, aprovação de gasto) vai numa lista única para ele.

### 4. Rodar sozinho
No Claude Code ou num projeto do Claude: "agende toda segunda às 8h: rode a reuniao-semanal e me mande o top 3".

## Regras
- O script só lê arquivos. Venda, conversa e chamado da semana o dono traz (ou o painel-de-vendas mostra).
- Prioridade 1 é o que trava venda ou expõe a loja (prova, campanha em menos de 14 dias, catálogo errado).
- Nada de gasto, publicação ou mensagem para cliente sem o "pode" do dono.
- Testes: `python3 -m unittest discover -s tests`.
