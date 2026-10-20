# Trocas, devoluções e garantia — o que a lei garante e o que a loja promete

Fonte: Código de Defesa do Consumidor (Lei 8.078/1990) e Decreto 7.962/2013 (comércio eletrônico). Prazo de garantia contratual da loja: **ainda não documentado** (catálogo de 18/10/2026). Até o fornecedor mandar por escrito, vale só a garantia legal.

| Situação | Prazo | O que o cliente tem direito | Quem decide |
|---|---|---|---|
| Arrependimento (comprou online e não quer mais) | 7 dias corridos a partir do recebimento (CDC art. 49) | Devolução do valor total, inclusive frete, sem precisar explicar o motivo | Dono aprova e gera a etiqueta de devolução |
| Defeito (produto não funciona) | 90 dias a partir da entrega para produto durável (CDC art. 26, II) | A loja tem até 30 dias para resolver; se não resolver, o cliente escolhe troca, dinheiro de volta ou abatimento (CDC art. 18) | Dono, depois do diagnóstico desta skill |
| Defeito que aparece depois (vício oculto) | 90 dias a partir de quando o defeito aparece (CDC art. 26, §3º) | Igual ao defeito | Dono |
| Produto errado ou avariado na entrega | Na hora (pedir foto da caixa e do produto) | Troca sem custo | Dono |

## Como o suporte conduz
1. Primeiro o diagnóstico (`scripts/diagnostico.py`). Muita "câmera com defeito" é Wi-Fi 5 GHz ou sinal fraco.
2. Se o passo a passo não resolveu, peça: número do pedido, foto ou vídeo curto mostrando o problema e a data em que recebeu.
3. Rode `scripts/diagnostico.py --troca --recebido AAAA-MM-DD` para saber em qual caso a pessoa está.
4. Passe para o dono com o resumo pronto. Nunca negue troca dentro do prazo legal e nunca prometa prazo além dele.

## Mensagem de transição para o dono resolver
"Entendi, {nome}. Já separei tudo aqui: pedido {pedido}, recebido em {data}, e o vídeo que você mandou. Vou passar agora para o responsável pelas trocas e ele te responde por aqui mesmo. Seu direito está garantido."
