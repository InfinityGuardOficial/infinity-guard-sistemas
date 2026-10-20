---
name: proposta-comercial
description: Proposta comercial da Infinity Guard para comércio, escritório, condomínio ou compra em quantidade. Use quando um cliente pedir orçamento formal, cotação para empresa, preço para várias unidades ou proposta em PDF/documento, com preços, Pix e parcelas calculados do catálogo e limites de desconto e margem.
---

# Proposta Comercial — vender para quem compra mais de um

Comércio, escritório e condomínio compram em quantidade e pedem orçamento por escrito. Esta skill monta a proposta com os preços do catálogo (fonte única: `catalogo.json` da skill `atendente-infinity-guard`), o que está e o que não está incluso, e os avisos para o dono antes de enviar.

Arquivos:
- `scripts/proposta.py`: monta a proposta em Markdown (ou JSON), com total, Pix, parcelas, validade e avisos (desconto, margem, valor alto, catálogo velho).
- `references/qualificacao-b2b.md`: as perguntas para entender o espaço e os kits de referência por tipo de negócio.

## Modos

### 1. Qualificar
Use `references/qualificacao-b2b.md`: 5 perguntas, uma por vez, no WhatsApp. Com as respostas, escolha os itens.

### 2. Montar a proposta
```bash
python3 scripts/proposta.py --listar
python3 scripts/proposta.py --cliente "Padaria do Zé" --tipo comercio --itens kit-cam-2:2,alarme-ikerui:1 --saida propostas/padaria-do-ze.md
```
`--tipo`: comercio | escritorio | condominio | home_office | residencia. `--desconto 0.05` (máximo 15%) só com ok do dono; com `--custos custos.json --margem-minima 0.25` o script confere a margem.
Linhas `[para o dono]` não vão para o cliente.

### 3. Entregar
Passe a proposta pela skill `revisor-de-promessas`. Para mandar como documento, converta o Markdown em PDF (skill de PDF, se instalada) ou cole no WhatsApp a parte "Investimento".

### 4. Acompanhar
Sem resposta em 2 dias: "Oi, {nome}! Ficou alguma dúvida na proposta? Posso ajustar a quantidade se precisar." Antes de vencer a validade, avise uma vez. Registre no `conversas.csv` do `painel-de-vendas` com canal `b2b`.

## Regras
- Preço só do script. Nunca prometa instalação, prazo de entrega ou prazo de garantia.
- Proposta acima de R$ 3.000 o dono revisa antes de sair.
- Condomínio: câmera em área comum exige aviso visível e decisão em assembleia; diga isso ao síndico, sem dar parecer jurídico.
- Testes: `python3 -m unittest discover -s tests`.
