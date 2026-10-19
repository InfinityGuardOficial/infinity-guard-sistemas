---
name: plano-de-midia
description: Plano de mídia e gestão do tráfego pago (Meta Ads) da Infinity Guard. Use para decidir quanto investir, qual o CPA máximo e o ROAS de equilíbrio, dividir o orçamento entre público frio, morno e quente, e avaliar resultados de campanha dizendo o que escalar, manter ou pausar.
---

# Plano de Mídia — anúncio que se paga

Tráfego pago só entra depois que a conversa vende (atendente) e a loja prova (prova-da-loja). Esta skill faz a conta antes de gastar e a régua depois: quanto uma venda pode custar sem dar prejuízo, quanto investir para a meta e o que fazer com cada conjunto de anúncios.

Arquivos:
- `scripts/midia.py`: modo `plano` (CPA máximo e alvo, ROAS de equilíbrio, orçamento ou vendas esperadas, divisão do funil) e modo `avaliar` (lê o CSV do Gerenciador de Anúncios e decide por conjunto).
- `references/estrutura-de-campanha.md`: a estrutura de campanhas, públicos e criativos da Infinity Guard e o que medir.

## Modos

### 1. Planejar
```bash
python3 scripts/midia.py plano --kit kit-casa-vigiada --margem 0.35 --meta-vendas 20 --dias 30
python3 scripts/midia.py plano --ticket 1100 --margem 0.35 --orcamento-dia 40 --prova ok
```
`--margem` é obrigatória (o dono informa: preço menos custo, frete e taxas). Sem `--prova ok` o plano sai sem público frio.

### 2. Avaliar resultados
No Gerenciador de Anúncios, exporte por conjunto as colunas valor gasto, compras e valor de conversão; renomeie para `conjunto;gasto;compras;receita`.
```bash
python3 scripts/midia.py avaliar --resultados resultados.csv --ticket 1100 --margem 0.35
```
Se o conector da Meta estiver ligado nesta sessão, leia os números de lá (só leitura) e monte o mesmo CSV.

### 3. Briefing de criativos
Mande à Máquina de Anúncios (se instalada) os ângulos da `references/estrutura-de-campanha.md` e o kit da vez. Todo criativo passa pela skill `revisor-de-promessas` antes de subir.

## Regras
- Nunca criar, ativar, pausar ou mudar orçamento de campanha real sem o "pode" do dono na conversa. A skill recomenda; o dono aperta o botão.
- Sem margem informada, não há plano: pergunte.
- Prova pendente = sem público frio. Sem pixel instalado na Nuvemshop, campanha de conversão não otimiza: avise.
- Decisão só com o número do período; não estime venda que não aconteceu.
- Testes: `python3 -m unittest discover -s tests`.
