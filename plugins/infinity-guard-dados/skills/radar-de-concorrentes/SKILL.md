---
name: radar-de-concorrentes
description: Radar de concorrentes da Infinity Guard. Use para registrar e comparar preços de Intelbras, Tapo, Kerui, Pado e kits de marketplace com o nosso catálogo, ver onde estamos acima ou abaixo do mercado, o que os concorrentes mostram (garantia, Anatel, instalação) e quais leituras estão velhas.
---

# Radar de Concorrentes — saber onde a gente está, com fonte

O Raio X de 18/10/2026 mostrou que a Infinity Guard está acima do mercado em câmera, alarme e fechadura facial. O radar mantém isso atualizado, com fonte em cada número, para o dono decidir preço e para o marketing saber o que destacar.

Arquivos:
- `scripts/radar.py`: `comparar` (nossa posição por produto contra a mediana do mercado), `registrar` (nova leitura com fonte) e `velhas` (o que refazer).
- `references/concorrentes.json`: as leituras. As 8 primeiras vêm do Raio X de 18/10/2026.

## Modos

### 1. Onde estamos
```bash
python3 scripts/radar.py comparar
```
Entregue ao dono: produto, nossa diferença para a mediana e a leitura (acima, na faixa, abaixo). Acima de 25%: ou a página mostra prova e serviço (garantia, prazo de entrega, suporte), ou o preço é revisto com a skill `catalogo-e-precos`.

### 2. Nova leitura
Pesquise na web (busca e leitura de página) e registre só o que leu de verdade:
```bash
python3 scripts/radar.py registrar --concorrente Intelbras --produto "iM4 C" --equivale cam-asecam-ptz --preco 579.90 --fonte "Extra, 20/10" --anatel sim
```
`--oferta` para preço promocional de marketplace; `--pix` se o preço é o do Pix.

### 3. Rotina mensal
```bash
python3 scripts/radar.py velhas --dias 30
```
Refaça as leituras velhas. Para análise maior de mercado (temas, dores, brechas), rode o Detetive de Nicho e atualize `docs/raio-x-de-nicho.md`.

## Regras
- Número sem fonte não entra. Marque oferta como oferta.
- Compare produto equivalente (mesma categoria e uso), não o mais barato que achar.
- O radar informa; preço quem decide é o dono.
- Não fale mal de concorrente em conteúdo: use o radar para mostrar critério ("confira a garantia e o prazo de entrega").
- Testes: `python3 -m unittest discover -s tests`.
