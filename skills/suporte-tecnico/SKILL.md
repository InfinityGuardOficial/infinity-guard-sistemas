---
name: suporte-tecnico
description: Suporte técnico e trocas da Infinity Guard. Use quando um cliente disser que a câmera não conecta, fica offline, não grava, não avisa, imagem ruim à noite, medo de câmera invadida, problema no alarme (chip, sensor, sirene) ou na fechadura (não abre, pilha, digital), e para saber se é caso de troca, devolução ou garantia pelo CDC.
---

# Suporte Técnico — "o suporte que responde"

O Raio X de 18/10/2026 mostra que a maior queixa do mercado é câmera offline e SAC que some. A promessa da Infinity Guard é o contrário: suporte no WhatsApp que responde as dúvidas. A loja **não configura o produto por WhatsApp nem por vídeo**: o manual de instruções acompanha o produto, e o suporte tira as dúvidas por mensagem. Esta skill transforma a mensagem do cliente numa resposta pronta para colar, e diz quando passar para o dono.

Arquivos:
- `scripts/diagnostico.py`: reconhece o problema pela fala do cliente (com ou sem acento) e devolve a mensagem numerada para o WhatsApp + quando escalar. Modo `--troca` diz o caso pelo CDC.
- `references/problemas.json`: 8 problemas (não conecta, offline, senha/invasão, visão noturna, gravação, notificação, alarme GSM, fechadura) com passos e critério de escalar.
- `references/trocas-e-garantia.md`: arrependimento em 7 dias (CDC art. 49), defeito em 90 dias (art. 26), 30 dias para resolver (art. 18) e a mensagem de transição.

## Modos

### 1. Resolver o problema
```bash
python3 scripts/diagnostico.py --mensagem "<o que o cliente escreveu>" --nome Ana [--categoria camera]
```
Mande ao cliente **só a mensagem**. Um problema por vez. Se o script não reconhecer, faça as 3 perguntas que ele sugere.

### 2. Troca, devolução ou garantia
```bash
python3 scripts/diagnostico.py --troca --recebido 2026-10-15 [--defeito]
```
Peça número do pedido, foto ou vídeo e a data de recebimento. Entregue ao dono o caso e o resumo; o dono decide.

### 3. Pós-venda que evita chamado
Na entrega, a skill `atendente-infinity-guard` (modo pós-venda) lembra que o manual acompanha o produto e manda por escrito os 3 cuidados: rede 2,4 GHz, trocar a senha, atualizar. Metade dos chamados some aqui.

### 4. Aprender com cada chamado
Problema novo resolvido? Acrescente em `references/problemas.json` (id, produtos, palavras, titulo, passos, escalar_se) e rode os testes. Registre a conversa no `conversas.csv` da skill `painel-de-vendas` com resultado `em_aberto` até fechar.

## Regras
- A loja tira dúvidas, não configura: nunca ofereça configurar o produto pelo cliente, por WhatsApp ou por chamada de vídeo. Responda por mensagem e indique o manual de instruções que acompanha o produto. O cliente pode mandar foto ou vídeo do problema para a gente entender a dúvida.
- Nunca mande abrir o aparelho, mexer na fiação da casa ou usar fonte diferente da original.
- Nunca negue troca dentro do prazo legal nem prometa prazo de garantia além dos 90 dias até o fornecedor documentar.
- Cliente dizendo que alguém controlou o aparelho, reclamação, Procon ou Reclame Aqui: passe para o dono na hora.
- Não peça senha do Wi-Fi nem da conta do app. Nunca.
- Testes: `python3 -m unittest discover -s tests`.
