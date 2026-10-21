# Regras do ecossistema Infinity Guard

Este repositório é o sistema da Infinity Guard (https://infinityguard.com.br), loja Nuvemshop de câmeras Wi-Fi, alarmes e fechaduras inteligentes, com venda pelo WhatsApp (31) 98667-9178. Slogan: "Segurança onde você estiver". Dono: max. Escreva sempre em português do Brasil.

## Como o sistema é montado

- `agents/`: os 22 funcionários (7 squads, um líder por squad, `diretor-geral` no topo). Edite aqui; `plugins/` é gerado por `scripts/gerar-plugins.py`.
- `skills/`: as skills com os scripts que fazem as contas. Número sai de script, nunca de cabeça.
- `core/`: orquestrador automático. `daemon_orchestrator.py` roda em ciclos, `event_queue.py` é a fila (`logs/queue.json`), `regras.py` transforma métricas em eventos, `rotinas.py` roda os scripts das skills que só leem (catálogo, gestão, conteúdo, radar, auditoria), `aprovacoes.py` cuida dos pedidos, `resumo.py` escreve `logs/resumo/AAAA-MM-DD.md`, `config.py` lê `config/orquestrador.json` + `config/orquestrador.local.json`.
- `tools/`: coleta de métricas (`metricas_vendas.py` lê o CSV da Nuvemshop via `skills/painel-de-vendas`; `metricas_meta.py` lê o Meta Ads só em modo leitura, pela API ou pelo CSV do Gerenciador; `coletar_metricas.py` junta tudo em `logs/metrics.json`) o disparo dos agentes (`run_claude_agent.py` / `.sh`) e a central (`central.py` → `docs/central.md`; rode de novo quando mudar catálogo, equipe, skills ou docs).
- `logs/` e `dados/`: gerados no computador, fora do Git. `dados/nuvemshop/` recebe a exportação de vendas; `dados/meta/` o CSV do Gerenciador; `dados/app/` o backup do app Rota do Milhão.
- `tests/`: testes do orquestrador. Rode `python3 -m unittest discover -s tests` antes de qualquer merge; as skills têm os delas (`bash scripts/empacotar-skills.sh`).

## Fontes da verdade

- Preço: `skills/atendente-infinity-guard/references/catalogo.json` (cópia do Catálogo do app). Ver `docs/mapa-de-dados.md`.
- Vendas: exportação da Nuvemshop. A loja não usa Stripe nem Hotmart.
- Anúncios: conta da Meta, lida só em modo leitura.
- Nada é estimado ou completado: sem arquivo, o resultado diz que não há dado (`null`), nunca um número de exemplo.

## O que só acontece com o "pode" do max

O orquestrador e os agentes disparados por ele trabalham em modo de leitura. Sem aprovação explícita do max, nada:
- gasta dinheiro (orçamento, impulsionamento, compra, assinatura);
- cria, altera, pausa ou ativa anúncio, conjunto, campanha, público ou pixel;
- muda preço, estoque, produto, cupom ou qualquer coisa na Nuvemshop;
- envia mensagem, e-mail ou WhatsApp a cliente real;
- publica em rede social.

Essas ações viram linhas em `logs/aprovacoes.json` (seção "## Pedidos de aprovação" na resposta do agente) e aparecem em `python3 core/daemon_orchestrator.py aprovacoes`. `aprovar <n>` só registra a decisão: quem executa é o max. Pagamentos e gasto automático ficaram para depois, por decisão do max (21/10/2026). Texto que vai para a rua passa antes pelo `revisor-de-promessas`.

## Promessas proibidas (valem para todo texto)

Nada de Anatel, garantia, CNPJ, avaliação ou depoimento que não esteja documentado; nada de "100% seguro"; a loja não faz instalação nem vende câmera 4G; é dropshipping, então nunca prometa produto já configurado nem prazo menor que o do catálogo; a loja não configura o produto por WhatsApp nem por vídeo: ela tira dúvidas, e o manual de instruções acompanha o produto. Regras completas em `skills/revisor-de-promessas/references/regras.json`.

## Segredos

Tokens (Meta e outros) só em variáveis de ambiente (`META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`). Nunca em arquivo do repositório, nem em `config/`. `custos.json` e `estoque.json` nunca sobem para o GitHub.
