# Mapa de dados — Infinity Guard · 20/10/2026

Onde cada dado mora, qual é a fonte da verdade, quem cuida e como atualizar. Regra: **cada dado tem um único dono**. Quando dois lugares guardam o mesmo dado, um deles é cópia e diz de onde copia.

## 1. Fontes da verdade

| Dado | Fonte da verdade | Cópias | Responsável | Como atualizar |
|---|---|---|---|---|
| Preço, custo, frete, margem, prazo de entrega, produto ativo (e o código Anatel, que fica só no app) | **App Rota do Milhão → Mais → Catálogo e preços** | `skills/atendente-infinity-guard/references/catalogo.json` (o atendente e as skills leem daqui); página da Nuvemshop | `gestor-de-catalogo` | 1. Edite no app. 2. Toque em "Copiar comando para o gestor-de-catalogo" e cole no Claude Code. 3. Ajuste o preço na Nuvemshop. |
| Preço que o cliente vê | **Nuvemshop** | as duas acima | `gestor-de-catalogo` | Sempre igual ao app. Se divergir, vale o que está na Nuvemshop até corrigir. |
| Cores, fonte, logo, slogan, WhatsApp, @ do Instagram | **App → Publicar → Kit da marca** (trava depois de aprovado) | — | `lider-marketing` | Só antes de travar. Depois, só com rescisão do contrato. |
| Contrato, missões, provas, motivos, números do dia, módulos entregues | **App** (área privada do dono) | — | o dono | Pelo app. As cobranças das 05:52 e 19:48 só leem. |
| Radar do mercado e ordens do dia | **App** (gravado pela rotina das 05:17) | notificação no celular | `detetive-de-mercado`, `lider-dados` | Automático, todo dia. |
| Pauta de publicação (roteiro, legenda, anúncio) | **App** (rotina das 05:17 ou "Produzir pauta" no app) | vídeos baixados, Planejador da Meta | `roteirista-de-reels`, `social-media` | Automático. Vídeo e agendamento: bloco de sábado. |
| Conexões das redes | **App → Publicar → Conexões** | — | cada responsável indicado na tela | Verificar a Meta pelo app; o resto, marcar como feito. |
| Regras de alerta da gestão (o que é "algo errado" e quem cuida) | `skills/monitor-de-gestao/references/alertas.json` | cópia no app (Gestão → Painel) e na rotina "Vigia da gestão" | `diretor-geral` | Mudou um limite? Peça para replicar no app e na rotina. |
| Regras de promessa (o que nunca pode ser dito) | `skills/revisor-de-promessas/references/regras.json` | lista resumida dentro do app e na rotina das 05:17 | `guardiao-de-conformidade` | Mudou uma regra no JSON? Peça para replicar no app e na rotina. |
| Preços dos concorrentes | `skills/radar-de-concorrentes/references/concorrentes.json` | `docs/raio-x-de-nicho.md` (foto de 18/10) | `detetive-de-mercado` | `radar.py registrar`, sempre com fonte. |
| Temas de conteúdo | `skills/conteudo-semanal/references/temas.json` | — | `roteirista-de-reels` | Renovar a cada 45 dias. |
| Ofertas de campanha | `skills/campanha-sazonal/references/ofertas.json` | `skills/campanha-sazonal/campanhas/*.md` (propostas datadas) | `lider-marketing` | Por campanha. |
| Custos e estoque reais | `custos.json` e `estoque.json` na pasta da skill `catalogo-e-precos`, **fora do Git** (estão no `.gitignore`) | custo e frete no Catálogo do app | `gestor-de-catalogo` | Nunca suba esses arquivos para o GitHub. |
| Pedidos e vendas | **Nuvemshop** (exportação CSV) | **App → Gestão → Pedidos** (importado pelo EDI ou lançado à mão) e o Placar | `analista-de-vendas` | Importar o CSV em Gestão → Integrações; Placar com "Puxar do ERP". |
| Clientes e funil | **App → Gestão → Clientes (CRM)** | — | `lider-vendas`, `consultor-whatsapp` | Toda conversa nova vira contato com próxima ação e data. |
| Fornecedores, prazo e pontualidade | **App → Gestão → Fornecedores (VMI)** | prazo no Catálogo | `gestor-de-catalogo` | Prazo do fornecedor alimenta a previsão de entrega. |
| Estoque | **App → Gestão → Estoque (WMS)** | — | `gestor-de-catalogo` | Planilha do fornecedor (sku;estoque) toda segunda em Integrações. |
| Despesas | **App → Gestão → Financeiro (ERP)** | — | `analista-de-vendas` | Lançar anúncios, apps e taxas no dia em que pagar. |
| Campanhas, públicos, pixel e catálogo de anúncios | **Meta (Business "Infinity Guard - Segurança onde você estiver")** | — | `lider-trafego`, `analista-de-midia` | Gerenciador de Anúncios ou o conector da Meta no Claude. |

## 2. Fotos datadas (não atualize, faça uma nova)

- `docs/raio-x-de-nicho.md` e `.html`: pesquisa de mercado de 18/10/2026. Os preços citados ali são daquela data.
- `skills/campanha-sazonal/campanhas/2026-proposta.md`: proposta de 11.11 e Black Friday com os preços de 18/10.
- `docs/mapa-de-sistemas.md`: ordem dos sistemas em 18/10.

## 3. Onde fica cada coisa do app

Tudo na área privada `data/users/<dono>/` do app (ninguém mais lê, nem quem receber o link):

| Caminho | Conteúdo |
|---|---|
| `estado` | configurações, contrato, módulos entregues, conexões, ideias, status das pautas, aba Mente (`mente`: hábitos, diário de erros, planos se-então, gatilhos) |
| `estado/dias/AAAA-MM-DD` | missões com prova, motivos e números de cada dia |
| `estado/radar/AAAA-MM-DD` | radar e ordens do dia |
| `estado/pauta/AAAA-MM-DD` | pauta de publicação do dia |
| `estado/extra/catalogo` | catálogo e preços |
| `estado/extra/marca` | Kit da marca |
| `estado/extra/equipe` | entregas guardadas dos funcionários |
| `estado/pedidos/<id>` | ERP e TMS: pedido, itens, total, custo, taxa, status, fornecedor, envio e rastreio |
| `estado/clientes/<id>` | CRM: contato, etapa do funil, próxima ação e data, notas, consentimento, pedidos |
| `estado/fornecedores/<id>` | VMI: fornecedor, prazos, política de troca, reserva |
| `estado/lancamentos/<id>` | ERP financeiro: despesas e outras receitas do mês |
| `estado/aprovacoes/<id>` | Caixa de aprovações: propostas da equipe e das rotinas (publicação, mensagem, conteúdo, preço, operação) com status pendente, aprovado, ajustar ou recusado |
| `estado/extra/rotinas` | Situação das rotinas, gravada pelo zelador às 07:07 |
| `estado/extra/plano-semana` | Plano da semana do diretor-geral (top 3, ordens, propostas, alertas) |
| `estado/conversas/<funcionário>__<etapa>` | Conversas com a equipe: uma por funcionário e por etapa (ordem do dia, tarefa, alerta ou conversa livre), com as mensagens trocadas e o status |

Estoque (WMS) fica junto do produto no `estado/extra/catalogo` (fornecedor, SKU do fornecedor, estoque do fornecedor, estoque próprio, mínimo, data da conferência).

## 4. Meta: contas encontradas em 20/10/2026

| Conta de anúncio | Business | Situação |
|---|---|---|
| 4288583104787413 "Infinity Guard" | Infinity Guard | ativa, **sem forma de pagamento** |
| 932424506118458 | Infinity Guard | ativa, com pagamento, acesso só leitura |
| 1036925376056610 | Infinity Guard | ativa, com pagamento, acesso só leitura |
| 2347611305997851 | sem Business | ativa, com pagamento |

Página: "Infinity Guard - Segurança onde você estiver". Catálogo de anúncios: "Infinity Guard". Nenhum Instagram ligado às contas de anúncio.
Recomendação: usar **uma** conta dentro do Business, com pagamento e com o Instagram ligado; deixar as outras paradas.

## 5. Rotinas que mexem nos dados

| Quando | O que faz | Escreve em |
|---|---|---|
| 05:17 todo dia | radar, ordens, pauta e proposta de publicação | `estado/radar`, `estado/pauta`, `estado/aprovacoes` |
| 05:52 seg–sáb | cobrança da manhã no celular | só lê |
| 19:48 todo dia | cobrança da noite no celular | só lê |
| 06:13 segunda | diretor-geral: plano da semana, ordens e propostas | `estado/radar`, `estado/aprovacoes`, `estado/extra/plano-semana` |
| 07:07 todo dia | zelador: confere as rotinas e roda o radar de novo se falhou | `estado/extra/rotinas` |
| 11:43 e 16:43 todo dia | vigia da gestão: alertas do ERP, CRM, WMS, TMS e VMI no celular, com o funcionário responsável | só lê |
| push em `desktop/` ou `android/` | gera os instaladores (Actions → Apps) | GitHub Actions |
| `bash scripts/empacotar-skills.sh` | testa as skills e refaz os .zip | `skills/*.zip` |
| `python3 scripts/gerar-plugins.py` | refaz os 7 plugins de squad a partir de `agents/` e `skills/` | `plugins/`, `.claude-plugin/marketplace.json` |
