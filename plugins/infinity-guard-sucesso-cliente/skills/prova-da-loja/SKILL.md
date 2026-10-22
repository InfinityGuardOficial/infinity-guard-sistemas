---
name: prova-da-loja
description: Auditor de prova da loja Infinity Guard. Use para conferir se o site infinityguard.com.br (ou qualquer loja) mostra CNPJ, garantia com prazo, avaliações, troca em 7 dias, endereço e contato, e para gerar a lista de correção em ordem e os textos prontos para o rodapé e as páginas de produto.
---

# Prova da Loja — "não dá para ser caro e anônimo ao mesmo tempo"

A Infinity Guard cobra acima da Intelbras e das ofertas de marketplace. O que paga essa diferença é prova: quem é a loja, quanto tempo de garantia, em quanto tempo chega, quem já comprou. Esta skill confere isso página por página e devolve o que corrigir primeiro.

Arquivos:
- `scripts/auditar.py`: o auditor. Lê páginas (URL ou arquivo salvo) e checa CNPJ com dígito verificador, garantia com prazo, avaliações, troca em 7 dias, endereço/contato, HTTPS e rastros de fornecedor ("plugue da UE", placeholder, variante em inglês). Código Anatel não é cobrado (dropshipping); se a página citar Anatel ou homologação, vira aviso para tirar.
- `references/checklist.md`: o que cada item é, onde vai e a base (Decreto 7.962/2013, CDC arts. 26 e 49).
- `references/modelos.md`: rodapé, bloco "Compra segura", texto da página de trocas, mensagem ao fornecedor pedindo garantia e prazo por escrito, pedido de avaliação.
- `auditorias/`: relatórios já feitos (o primeiro é de 18/10/2026). Compare o novo com o último.

## Modos

### 1. Auditar a loja inteira
```bash
python3 scripts/auditar.py --catalogo --saida auditorias/$(date +%F).md
```
`--catalogo` usa o catálogo da skill `atendente-infinity-guard` (instalada ao lado): início, Sobre, Trocas, Contato, Perguntas, a página de oferta (`landing`, hoje oferta.infinityguard.com.br) e todos os produtos de segurança ativos.

### 2. Auditar páginas soltas
```bash
python3 scripts/auditar.py --url https://infinityguard.com.br/produtos/sistema-alarme-kerui/
python3 scripts/auditar.py --arquivo pagina-salva.html
```
Se a internet do script for bloqueada, salve a página no navegador (Ctrl+S) e use `--arquivo`. Se você (Claude) só consegue ler a página por uma ferramenta de leitura web, pergunte literalmente por CNPJ, garantia, avaliações, troca, endereço e variantes, e monte o relatório no formato de `auditorias/2026-10-18-infinityguard.md`.

### 3. Escrever as correções
Use `references/modelos.md`. Preencha só com dado que o dono deu. O que faltar fica `[A PREENCHER]` e entra numa lista "o que só você pode fazer".

### 4. Conferir antes de campanha
Antes de 11/11 e da Black Friday, rode o modo 1. Se CNPJ ou garantia estiverem ❌ ou ⚠️, diga ao dono em uma linha que o anúncio deve esperar, e por quê.

## Regras
- Nunca invente CNPJ, código Anatel, prazo de garantia, endereço ou avaliação. Nunca sugira avaliação falsa.
- Anatel: a loja vende por dropshipping e não publica código. Desde 22/10 não é pendência do dono (o fornecedor não fornece os códigos). Não cobre do fornecedor nem sugira publicar.
- A garantia legal de 90 dias (CDC art. 26) vale sempre; qualquer prazo além disso só com documento do fornecedor.
- Avaliação carregada por JavaScript pode não aparecer para o script: confira no navegador antes de dizer que não existe.
- Testes: `python3 -m unittest discover -s tests`.
