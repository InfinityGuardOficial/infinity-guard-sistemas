---
name: monitor-de-gestao
description: Vigia da gestão da Infinity Guard. Use para conferir o que saiu errado no ERP, CRM, WMS, TMS, EDI e VMI do app Rota do Milhão (entrega atrasada, pedido não repassado ao fornecedor, sem rastreio, margem negativa, resultado do mês no vermelho, anúncio caro, follow-up vencido, estoque esgotado ou baixo, fornecedor impontual, troca aberta) e para dizer qual funcionário cuida de cada alerta e o que fazer hoje.
---

# Monitor de Gestão — "o problema aparece antes do cliente reclamar"

O app Rota do Milhão guarda pedidos, clientes, fornecedores, estoque e despesas (Gestão). Esta skill aplica as regras de alerta a esses dados e devolve a lista por nível (crítico, alto, médio), com o funcionário responsável e a ação.

As **mesmas regras** rodam em três lugares:
1. No app: Gestão → Painel e aba Hoje (aviso sonoro quando há crítico).
2. Na rotina "Vigia da gestão" (11:43 e 16:43), que manda notificação no celular quando algo sai errado.
3. Aqui, no `scripts/monitor.py`, para a equipe no Claude Code.

Arquivos:
- `references/alertas.json`: as regras, os limites (dias, % mínimos) e quem cuida de cada uma. **Fonte da verdade dos alertas.**
- `scripts/monitor.py`: aplica as regras e imprime os alertas.

## Como rodar

1. No app: Gestão → Integrações → **Backup completo (JSON)**.
2. Rode:
```bash
python3 scripts/monitor.py --backup rota-do-milhao-backup-AAAA-MM-DD.json
python3 scripts/monitor.py --backup backup.json --json     # para outra ferramenta ler
```
Também aceita `--pasta` com os arquivos salvos pelo ArtifactData (`data/users/me/estado/...`). Código de saída: 2 se houver crítico, 1 se houver alto, 0 se não houver nada urgente.

## Quem cuida de quê

| Alerta | Nível | Responsável |
|---|---|---|
| `tms-atraso` entrega com previsão vencida | crítico | guardiao-pos-venda |
| `wms-esgotado` produto ativo sem estoque | crítico | gestor-de-catalogo |
| `erp-nao-repassado` pago e não enviado ao fornecedor | alto | lider-operacoes |
| `tms-sem-rastreio` no fornecedor sem código | alto | lider-operacoes |
| `erp-margem-negativa` pedido com prejuízo | alto | gestor-de-catalogo |
| `fin-resultado-negativo` mês no vermelho | alto | analista-de-vendas |
| `vmi-pontualidade` fornecedor abaixo de 80% no prazo | alto | gestor-de-catalogo |
| `sac-troca-aberta` troca ou devolução | alto | tecnico-de-suporte |
| `fin-anuncio-alto` anúncio acima de 30% da receita | médio | analista-de-midia |
| `crm-followup-atrasado` próxima ação vencida | médio | consultor-whatsapp (orçamento: recuperador-de-carrinho; pós-venda: guardiao-pos-venda) |
| `crm-orcamento-sem-acao` orçamento sem follow-up | médio | recuperador-de-carrinho |
| `wms-baixo`, `wms-sem-conferencia`, `erp-sem-custo` | médio | gestor-de-catalogo |
| `vmi-sem-fornecedor` produto sem fornecedor | médio | lider-operacoes |

## Como responder um alerta

- Diga o alerta, o pedido ou produto e a ação de hoje, nessa ordem, em até 3 linhas.
- Mensagem para cliente ou fornecedor: escreva pronta, mas só o dono envia.
- Nunca prometa ao cliente uma data de entrega que o fornecedor não confirmou.
- Mudou um limite em `alertas.json`? Avise o dono para replicar no app e na rotina.
