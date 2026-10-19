# Auditoria de prova da loja · 18/10/2026 · infinityguard.com.br

Páginas lidas em 18/10/2026: início, Sobre, Trocas e Devoluções, Kit 2 câmeras, Alarme IKerui, Fechadura facial. Leitura feita pelo leitor de páginas do Claude (o script `auditar.py` roda no seu computador com `--catalogo` para repetir em todas as páginas).

**Nota de prova: 2 de 6 itens.** Tem troca em 7 dias e WhatsApp visível. Falta todo o resto. Regra: sem os itens 1 a 3, não ligue anúncio de Black Friday.

## Lista de correção, em ordem

1. **CNPJ e razão social** ❌ Não aparecem em nenhuma página (rodapé, Sobre, Trocas). Coloque razão social, CNPJ e endereço no rodapé (modelo em `references/modelos.md`).
2. **Código Anatel** ❌ Nenhuma menção a Anatel nas páginas da câmera, do alarme e da fechadura. Peça ao fornecedor (mensagem pronta em `modelos.md`), confira no portal da Anatel e publique o bloco "Compra segura" em cada produto.
3. **Garantia com prazo** ⚠️ "Garantia em todos os produtos" aparece até 5 vezes por página, mas sem prazo, nem na página de trocas. Escreva no mínimo os 90 dias da garantia legal; prazo maior só com documento do fornecedor.
4. **Avaliações** ❌ Nenhuma avaliação ou estrela em nenhum produto. Instale um app de avaliações e peça no dia 7 do pós-venda.
5. **Rastros de fornecedor** ⚠️
   - Kit 2 câmeras e Alarme IKerui: variante **"plugue da UE"** à venda. Ou o produto vem com tomada europeia (então avise e inclua adaptador), ou é texto herdado do fornecedor (então apague).
   - Kit 2 câmeras: a galeria tem imagens vazias (placeholder).
   - Fechadura facial: variante de cor **"D14P 24240 SC DH DB"** e seletor "Tamanho da fechadura" com as opções "Versão do aplicativo Wishhome / Tuya". Renomeie para algo que o cliente entenda (por exemplo "App Tuya Smart Life").
   - Alarme: variantes "kit de alarme 1, 2, 3, 4" sem dizer o que muda em cada uma.
6. **Página de trocas** ⚠️ Tem os 7 dias corridos, mas não diz quem paga o frete da devolução nem para onde enviar.
7. **Endereço e contato** ⚠️ Sem endereço nem cidade. No rodapé, o texto do WhatsApp aparece como "53 3186679178", enquanto o link e o resto do site usam (31) 98667-9178: corrija o texto. O link do Twitter está quebrado (tem espaço no endereço).
8. **Sobre a Infinity Guard** ⚠️ Sem nome de quem está por trás, cidade ou foto. Uma foto sua e "loja de Belo Horizonte/MG" (se for o caso) já mudam a confiança.

## Conferir à mão
- [ ] Foto real sua com cada produto (o leitor não distingue foto sua de foto do fornecedor).
- [ ] Código Anatel de cada modelo conferido no portal da Anatel, com print guardado.
- [ ] Depois de corrigir, rodar `python3 scripts/auditar.py --catalogo` e comparar com este relatório.

O auditor só registra o que encontrou. CNPJ, código Anatel e prazo de garantia vêm dos seus documentos.
