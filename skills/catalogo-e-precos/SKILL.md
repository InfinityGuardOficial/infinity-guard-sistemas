---
name: catalogo-e-precos
description: Gestão do catálogo, preços, margem e estoque da Infinity Guard. Use quando o dono mudar um preço, ativar ou desativar produto, quiser saber a margem por produto no Pix e no cartão, conferir estoque baixo, ou antes de campanha para validar que Pix, parcelas e links do catálogo estão certos.
---

# Catálogo e Preços — um preço só, certo em todo lugar

O `catalogo.json` da skill `atendente-infinity-guard` é a fonte de preço de todas as skills (atendente, campanha, proposta, página de produto, plano de mídia). Esta skill é a única que mexe nele, sempre recalculando Pix (preço × 0,90), parcelas (até 12, parcela mínima de R$ 30) e a data.

Arquivos:
- `scripts/catalogo.py`: `validar`, `atualizar` (simula; grava só com `--gravar`), `margem` e `estoque`.

## Modos

### 1. Validar (toda segunda e antes de campanha)
```bash
python3 scripts/catalogo.py validar
```

### 2. Mudar preço ou status
```bash
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90 --gravar
python3 scripts/catalogo.py atualizar --produto cartao-64 --ativo sim --gravar
```
Primeiro mostre a simulação ao dono; grave quando ele confirmar que o preço já está assim na Nuvemshop. Depois: `python3 ../atendente-infinity-guard/scripts/exportar_prompt.py > ../atendente-infinity-guard/prompt-atendente.txt` para o robô de WhatsApp usar o preço novo, e rode os testes das skills.

### 3. Margem
O dono passa o custo de compra por produto num `custos.json` (fica só no computador dele, não vai para o GitHub).
```bash
python3 scripts/catalogo.py margem --custos custos.json --taxa 0.05 --minima 0.25
```
A margem no Pix é a que importa para campanha e plano de mídia.

### 4. Estoque
```bash
python3 scripts/catalogo.py estoque --estoque estoque.json --minimo 3
```
Esgotou: desative no catálogo e no site no mesmo dia (a atendente nunca oferece produto inativo).

### 5. Preço frente ao mercado
Para comparar com concorrentes, use a skill `radar-de-concorrentes`.

## Regras
- Nunca invente preço: o número vem do dono ou do site.
- Nunca suba o preço antes de campanha para dar desconto em cima (a `campanha-sazonal` usa o preço atual como "de").
- Não grave `custos.json` nem `estoque.json` no repositório.
- Testes: `python3 -m unittest discover -s tests`.
