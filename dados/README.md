# dados/

Coloque aqui os arquivos que o orquestrador lê (eles ficam fora do Git):

- `nuvemshop/`: exportação de vendas da Nuvemshop (Vendas → Exportar, CSV). O mais novo é o usado. Se quiser a conversão do WhatsApp, salve também a planilha do atendimento com "conversa" no nome (modelo em `skills/painel-de-vendas/references/modelo-conversas.csv`).
- `meta/`: CSV do Gerenciador de Anúncios com as colunas `conjunto;gasto;compras;receita`. Não precisa se `META_ACCESS_TOKEN` e `META_AD_ACCOUNT_ID` estiverem configurados.
- `app/`: backup do app Rota do Milhão (Gestão → Integrações → Backup completo, arquivo .json). A rotina `gestao` usa o mais novo.
