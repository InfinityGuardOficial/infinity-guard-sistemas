---
name: painel-de-vendas
description: Painel de vendas da Infinity Guard. Use quando pedirem painel, relatório de vendas, faturamento, ticket médio, quanto vendeu na Black Friday, cupons usados ou resultado do WhatsApp, a partir da exportação de pedidos da Nuvemshop (CSV) e do registro de conversas do atendimento.
---

# Painel de Vendas

Transforma a exportação de pedidos da Nuvemshop num painel HTML que abre em qualquer navegador, sem internet: faturamento pago, pedidos, ticket médio, % no Pix, meta das primeiras 20 vendas, faturamento por semana, produtos mais vendidos, vendas por canal, cupons da campanha e, se houver, o resultado do atendimento no WhatsApp.

Arquivos:
- `scripts/painel.py`: lê o CSV (aceita `;` ou `,`, valores `1.234,56`), junta as linhas de cada pedido, conta só pagos (pendentes e cancelados aparecem à parte) e gera o HTML ou JSON.
- `references/modelo-conversas.csv`: cabeçalho do registro de conversas (`data;cliente;kit_indicado;resultado;canal`, resultado = venda | carrinho | recuperado | sem_resposta | em_aberto).
- `paineis/`: painéis gerados. `exemplo-ficticio.html` usa dados inventados só para mostrar o visual.

## Modos

### 1. Gerar o painel
1. Na Nuvemshop, exporte a lista de vendas em CSV (área de Vendas, opção de exportar).
2. Rode:
```bash
python3 scripts/painel.py --pedidos vendas.csv --saida paineis/painel-$(date +%F).html
```
Com o registro do atendimento: `--conversas conversas.csv`. Se o script disser que falta coluna, ele lista as colunas do arquivo: rode de novo com `--mapear total="Nome da coluna"` (campos: pedido, data, status, total, produto, qtd, pagamento, cupom, canal).

### 2. Responder perguntas
Use `--json` e responda com os números do arquivo, dizendo o período. Exemplo: "quanto vendeu com o cupom IGBLACK?" → `cupons` no JSON.

### 3. Registrar conversas
A cada conversa que a skill `atendente-infinity-guard` conduzir, acrescente uma linha em `conversas.csv` (copie o modelo). É isso que mostra quantas conversas viram venda e quantos carrinhos voltaram.

## Regras
- Os números saem só do arquivo. Nunca estime, arredonde para cima nem complete mês que falta.
- Não coloque nome, telefone ou e-mail de cliente no painel nem em lugar compartilhado.
- Testes: `python3 -m unittest discover -s tests`.
