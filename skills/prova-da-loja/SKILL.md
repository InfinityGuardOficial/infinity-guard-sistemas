---
name: prova-da-loja
description: Auditor de prova da loja Infinity Guard. Use para conferir se o site infinityguard.com.br (ou qualquer loja) mostra CNPJ, código Anatel, garantia com prazo, avaliações, troca em 7 dias, endereço e contato, e para gerar a lista de correção em ordem e os textos prontos para o rodapé e as páginas de produto.
---

# Prova da Loja — "não dá para ser caro e anônimo ao mesmo tempo"

A Infinity Guard cobra acima da Intelbras e das ofertas de marketplace. O que paga essa diferença é prova: quem é a loja, que o produto é homologado, quanto tempo de garantia, quem já comprou. Esta skill confere isso página por página e devolve o que corrigir primeiro.

Arquivos:
- `scripts/auditar.py`: o auditor. Lê páginas (URL ou arquivo salvo) e checa CNPJ com dígito verificador, código Anatel no formato `00000-00-00000`, garantia com prazo, avaliações, troca em 7 dias, endereço/contato, HTTPS e rastros de fornecedor ("plugue da UE", placeholder, variante em inglês).
- `references/checklist.md`: o que cada item é, onde vai e a base (Decreto 7.962/2013, CDC arts. 26 e 49, Anatel).
- `references/modelos.md`: rodapé, bloco "Compra segura", texto da página de trocas, mensagem ao fornecedor pedindo o código Anatel, pedido de avaliação.
- `auditorias/`: relatórios já feitos (o primeiro é de 18/10/2026). Compare o novo com o último.

## Modos

### 1. Auditar a loja inteira
```bash
python3 scripts/auditar.py --catalogo --saida auditorias/$(date +%F).md
```
`--catalogo` usa o catálogo da skill `atendente-infinity-guard` (instalada ao lado): início, Sobre, Trocas, Contato, Perguntas e todos os produtos de segurança ativos. Anatel só é exigida em câmera, alarme e fechadura.

### 2. Auditar páginas soltas
```bash
python3 scripts/auditar.py --url https://infinityguard.com.br/produtos/sistema-alarme-kerui/
python3 scripts/auditar.py --arquivo pagina-salva.html --sem-anatel
```
Se a internet do script for bloqueada, salve a página no navegador (Ctrl+S) e use `--arquivo`. Se você (Claude) só consegue ler a página por uma ferramenta de leitura web, pergunte literalmente por CNPJ, Anatel, garantia, avaliações, troca, endereço e variantes, e monte o relatório no formato de `auditorias/2026-10-18-infinityguard.md`.

### 3. Escrever as correções
Use `references/modelos.md`. Preencha só com dado que o dono deu. O que faltar fica `[A PREENCHER]` e entra numa lista "o que só você pode fazer".

### 4. Conferir antes de campanha
Antes de 11/11 e da Black Friday, rode o modo 1. Se CNPJ, Anatel ou garantia estiverem ❌ ou ⚠️, diga ao dono em uma linha que o anúncio deve esperar, e por quê.

## Regras
- Nunca invente CNPJ, código Anatel, prazo de garantia, endereço ou avaliação. Nunca sugira avaliação falsa.
- Código no formato certo não basta: só vale depois de conferido no portal de produtos homologados da Anatel com o modelo exato.
- A garantia legal de 90 dias (CDC art. 26) vale sempre; qualquer prazo além disso só com documento do fornecedor.
- Avaliação carregada por JavaScript pode não aparecer para o script: confira no navegador antes de dizer que não existe.
- Testes: `python3 -m unittest discover -s tests`.
