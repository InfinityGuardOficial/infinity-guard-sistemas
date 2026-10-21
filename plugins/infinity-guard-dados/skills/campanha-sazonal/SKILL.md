---
name: campanha-sazonal
description: Campanha 11.11 e Black Friday (26 a 29/11) da Infinity Guard. Use para montar as ofertas de kit com preço e Pix calculados do catálogo, o cupom, o calendário de posts, Stories, Reels e WhatsApp dia a dia, as mensagens prontas para a lista VIP e o briefing para a Máquina de Anúncios e a Máquina de Reels.
---

# Campanha Sazonal — 11.11 e Black Friday

O Raio X (18/10/2026) mostra que a Infinity Guard é mais cara que a Intelbras e que os kits de marketplace (2 câmeras por R$ 162 a R$ 180 em oferta). **Não dá para ganhar a Black Friday no preço.** A campanha vende kit montado para cada tipo de casa e suporte que responde as dúvidas, com um desconto honesto em cima do preço atual.

Arquivos:
- `scripts/montar_campanha.py`: calcula os kits (preço "de" = soma dos preços atuais, "por" com o desconto, Pix, parcelas), gera o calendário com as datas reais de 2026 e as mensagens de WhatsApp.
- `references/ofertas.json`: os 4 kits (Apartamento Tranquilo, Casa Vigiada, Porta Inteligente, Casa Completa), os eventos e os cupons sugeridos.
- `campanhas/`: campanhas já geradas. `2026-proposta.md` é a proposta de 18/10 com 10% de desconto.
- Preços: lidos do `catalogo.json` da skill `atendente-infinity-guard` instalada ao lado (fonte única).

## Modos

### 1. Montar a campanha
```bash
python3 scripts/montar_campanha.py --desconto 0.10 --saida campanhas/$(date +%F).md
```
Opções: `--evento 1111|blackfriday|ambos`, `--cupom CODIGO` (o que o dono criou na Nuvemshop), `--custos custos.json --margem-minima 0.25` (tira da campanha o kit que ficar abaixo da margem), `--prova ok` (libera anúncio pago), `--json`.
Nunca calcule preço de kit de cabeça: sempre o script.

### 2. Antes de lançar (portão de prova)
Rode a skill `prova-da-loja`. Enquanto CNPJ e garantia com prazo não estiverem no site, use `--prova pendente` (o padrão): a campanha fica em orgânico e WhatsApp, sem anúncio pago. Diga isso ao dono em uma linha.

### 3. Anúncios e Reels
Passe para a Máquina de Anúncios e a Máquina de Reels (se instaladas) este briefing, com a tabela de ofertas do modo 1:
- Público: dono de casa ou apartamento que quer ver a casa de longe e tem medo de câmera invadida ou offline.
- Promessa: kit certo para a sua casa, manual de instruções na caixa e dúvidas respondidas no WhatsApp. Nada de "o mais barato". A loja não configura o produto por WhatsApp nem por vídeo.
- Prova: só cite garantia e avaliações que já estejam no site. Anatel não entra em campanha (dropshipping: a loja não publica código).
- Ângulos: senha de fábrica (câmera invadida), o que olhar antes de comprar câmera na Black Friday, casa vazia durante o dia.

### 4. Durante a campanha
Para cada cliente que responder, use a skill `atendente-infinity-guard` (modo atender e recomendar). Carrinho abandonado: modo carrinho com `--cupom` do evento. Depois do evento: pós-venda de 7 dias e pedido de avaliação (alimenta a prova da loja).

## Regras
- Desconto só sobre o preço atual. Nunca suba preço antes da campanha nem use o "preço de" riscado da vitrine como base.
- Desconto acima de 25% o script recusa. Sem custos informados, avise o dono para conferir a margem.
- Cupom: só fale de cupom que o dono confirmou ter criado. O sugerido aparece marcado como sugestão.
- WhatsApp só para quem já falou com a loja ou respondeu SIM; mensagem em massa no máximo 1 por dia por pessoa, entre 8h e 21h; SAIR tira da lista na hora.
- Nunca prometa instalação, câmera 4G, prazo de entrega, código Anatel ou prazo de garantia que não estejam no catálogo ou no site.
- Testes: `python3 -m unittest discover -s tests`.
