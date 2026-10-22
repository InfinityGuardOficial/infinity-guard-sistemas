---
name: revisor-de-promessas
description: Revisor de promessas e conformidade da Infinity Guard. Use antes de publicar ou mandar qualquer anúncio, post, roteiro, legenda, página de produto, proposta ou mensagem de WhatsApp, para barrar promessa enganosa (100% seguro, instalação, 4G, garantia ou Anatel sem documento, preço "de" maquiado, depoimento inventado) e pedido de dado sensível, além de promessa de configurar o produto por WhatsApp ou vídeo ou de dar suporte de conexão ao Wi-Fi pela loja.
---

# Revisor de Promessas — o último olhar antes de publicar

A Infinity Guard vende confiança. Uma promessa que a loja não cumpre (ou não consegue provar) derruba anúncio na Meta, gera reclamação e vai contra o CDC. Esta skill é o portão de saída de todos os squads: nada sai sem passar por ela.

Arquivos:
- `scripts/revisar.py`: lê o texto (arquivo, `--texto` ou entrada padrão) e aponta cada trecho arriscado com a linha, a gravidade, o porquê e como reescrever.
- `references/regras.json`: as regras (segurança absoluta, medo exagerado, garantia e Anatel sem documento, instalação, 4G/sem Wi-Fi, superlativo, "de/por" maquiado, urgência falsa, prazo de frete, depoimento inventado, dado de cartão/senha, falar mal de concorrente, produto já configurado, prazo de entrega e **configuração pela loja**: a loja não configura o produto por WhatsApp nem por vídeo, ela tira dúvidas, porque o manual de instruções acompanha o produto; e **Wi-Fi pela loja**: a loja não ajuda a conectar ou configurar o Wi-Fi nem promete suporte de Wi-Fi, a conexão está no manual. Citar Wi-Fi como especificação do produto pode). Base: CDC arts. 26, 30, 31 e 37, Decreto 7.962/2013, regras de anúncio da Meta, LGPD e o que a loja oferece de fato.

## Modos

### 1. Revisar um texto
```bash
python3 scripts/revisar.py --arquivo anuncio.md
python3 scripts/revisar.py --texto "mensagem curta"
```
Veredito: **LIBERADO**, **AJUSTAR** (pode sair depois de reescrever os ⚠️) ou **BLOQUEADO** (não sai com os ❌). Entregue o texto já reescrito, não só a lista.
Quando a promessa aparece negada ("sem instalação", seção "O que não está incluso") ou é a pergunta do cliente, o script rebaixa para ⚠️: confira se fica claro que a loja não promete aquilo.

### 2. Revisar em lote
```bash
for f in pautas/*.md; do python3 scripts/revisar.py --arquivo "$f" --estrito || echo "BLOQUEADO: $f"; done
```

### 3. Quando a loja resolver uma pendência
Com o prazo de garantia documentado pelo fornecedor e publicado, `--liberar garantia-sem-prazo-documentado`. A regra `anatel-sem-codigo` fica sempre ligada: a loja vende por dropshipping e não publica código Anatel. Melhor ainda: atualize `references/regras.json` e o `catalogo.json` da atendente no mesmo dia.

### 4. Revisão de contexto (o que o script não vê)
Depois do script, leia o texto e confira:
- Todo preço, Pix e parcela batem com o `catalogo.json` da skill `atendente-infinity-guard` (data em `atualizado_em`).
- Cupom citado existe na Nuvemshop (o dono confirma).
- Foto ou vídeo mostra o produto real vendido, não imagem do fornecedor com outra marca.
- Anúncio com dado pessoal de cliente (nome, rosto, casa) só com autorização por escrito.

## Regras
- O script acha padrões; ele não substitui o bom senso. Na dúvida, tire a promessa.
- Nunca "resolva" um achado escondendo a palavra (ex.: "100 por cento seguro"). Reescreva a ideia.
- Testes: `python3 -m unittest discover -s tests`.
