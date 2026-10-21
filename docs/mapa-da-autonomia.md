# Mapa da autonomia — Infinity Guard · 21/10/2026

Tudo num lugar só: o que a equipe faz sozinha, o que espera o "pode" do dono e o que ainda está bloqueado. A Central do app Rota do Milhão (primeira aba) mostra o estado de cada item em tempo real.

## Nível de autonomia: 4

| Nível | O que significa | Situação |
|---|---|---|
| 1 · Ferramentas | Skills e scripts que o dono roda | ✓ 14 skills, servidor MCP com 9 ferramentas |
| 2 · Assistida | Equipe de IA que trabalha quando chamada | ✓ 22 funcionários, conversas por etapa no app |
| 3 · Agendada | Trabalho que roda sozinho em horário fixo | ✓ 7 rotinas (abaixo) |
| 4 · Autônoma com aprovação | A equipe planeja, produz e se vigia; o dono só aprova o que envolve dinheiro, publicação ou cliente | ✓ Central, caixa de aprovações, diretor-geral semanal e zelador diário |
| 5 · Sem humano | Gasta, publica e fala com cliente sozinha | ✗ fora de propósito: a regra da casa exige o "pode" do dono para gasto, publicação, mensagem a cliente e mudança no site |

## O que roda sozinho

| Quando | Rotina | Faz | Escreve no app |
|---|---|---|---|
| 05:17 todo dia | Radar e pauta | pesquisa o mercado, ordens do dia, pauta do Reel, **proposta de publicação** | radar, pauta, aprovações |
| 05:52 seg a sáb | Cobrança da manhã | missão do turno, ordem principal, gestão do dia | — (notificação) |
| 06:13 segunda | Diretor-geral | roda reunião, radar de preço, campanha, pauta e vigia; **plano da semana**, ordens e propostas | radar (ordens), aprovações, plano-semana |
| 07:07 todo dia | Zelador | confere pelo resultado gravado no app se cada rotina rodou; avisa só se houver problema, com o caminho para rodar de novo | rotinas |
| 11:43 e 16:43 | Vigia da gestão | alertas do ERP, CRM, WMS, TMS e VMI com o responsável | — (notificação) |
| 19:48 todo dia | Cobrança da noite | placar do dia e da semana, contrato | — (notificação) |

## O que espera o dono (um toque na Central → Aprovações)

- **Publicação** do Reel do dia (ao aprovar, o app gera o vídeo com o Kit da marca para agendar no Planejador da Meta).
- **Mensagens para clientes** (lista VIP, campanha, reativação).
- **Conteúdo** (textos de página, posts) e **mudança de preço** sugerida com motivo e fonte.
- Texto com promessa barrada pelo revisor não pode ser aprovado.

## O que ainda está bloqueado

| Item | Por quê | Quem destrava |
|---|---|---|
| Anúncio pago | Teto de gasto em R$ 0 até a loja ficar pronta | O dono define o teto semanal |
| Publicação direta no Instagram | O conector da Meta disponível só faz anúncios; post orgânico sai pelo Planejador da Meta | — |
| Instagram ligado à conta de anúncio | Nenhuma conta de anúncio tem Instagram ligado; a "Infinity Guard" está sem pagamento | O dono, no Meta Business Suite |
| Auditoria do site pela nuvem | A rede do ambiente bloqueia `infinityguard.com.br` | O dono libera o domínio no ambiente (pelo computador) |
| Margem e CPA reais | Catálogo sem custo, frete e prazo | O dono preenche no Catálogo do app |
| Rotinas lerem o repositório se ele ficar privado | O clone sem login falha | Avisar o Claude para trocar o clone por outro caminho |
| Rotina rodar outra rotina de novo sozinha | As rotinas na nuvem não têm acesso à ferramenta de rotinas; o zelador avisa e o dono toca em "Executar agora" no app Claude | — |
