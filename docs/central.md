# Central Infinity Guard
_Gerada em 23/10/2026 10:13 por `tools/central.py`. Para atualizar: `python3 tools/central.py`._

**Segurança onde você estiver.** Tudo do sistema num lugar só: o que existe, onde está e como está hoje.

## Comece aqui

- Instalar a equipe e as skills: [README](../README.md) (seção "Instalar tudo de uma vez").
- Ligar o orquestrador no seu computador: [README](../README.md) (seção "Orquestrador automático").
- Regras da casa para o Claude: [.claude/CLAUDE.md](../.claude/CLAUDE.md) e [CLAUDE.md](../CLAUDE.md).
- Regra de suporte (21/10/2026): a loja tira dúvidas no WhatsApp e o manual de instruções acompanha o produto; ela não configura o produto por WhatsApp nem por vídeo (o revisor barra essa promessa).
- Onde mora cada dado e quem cuida: [mapa-de-dados.md](mapa-de-dados.md).
- O que roda sozinho e o que espera você: [mapa-da-autonomia.md](mapa-da-autonomia.md). No celular, a aba Central do app Rota do Milhão mostra o mesmo em tempo real.
- Hábitos e decisões dos milionários que começaram do zero (pesquisa com fontes, aba Mente do app): [mente-de-milionario.md](mente-de-milionario.md).

## Como está hoje

- **Catálogo** (2026-10-18): 14 produtos ativos, 6 de segurança: Câmera Wi-Fi Infinity Guard R$ 392,35; Câmera de Segurança Wi-Fi ASECAM R$ 407,17; Sistema de Alarme IKerui R$ 875,50; Fechadura Inteligente Infinity Guard (Reconhecimento Facial 3D e Biometria App Tuya Smart Life) R$ 2.173,27; Fechadura Inteligente Infinity Guard (Bluetooth) R$ 1.218,54; Sensor de Presença Infinity Guard R$ 71,98.
- **Equipe:** 23 funcionários em 7 squads; 15 skills.
- **Prova da loja:** nota 2 de 6 itens na auditoria [2026-10-18-infinityguard](../skills/prova-da-loja/auditorias/2026-10-18-infinityguard.md).
- **Última reunião:** [2026-10-21-reuniao-geral](reunioes/2026-10-21-reuniao-geral.md).
- **Pauta de conteúdo mais nova:** [2026-10-19](../skills/conteudo-semanal/pautas/2026-10-19.md).
- **Campanha:** [2026-proposta](../skills/campanha-sazonal/campanhas/2026-proposta.md).
- **Orquestrador:** roda no seu computador. Lá, `python core/daemon_orchestrator.py status` mostra o estado, e `logs/central.md` é esta mesma página com o resumo do dia e as aprovações.

## A equipe

| Squad | Funcionários |
|---|---|
| Direção | [diretor-geral](../agents/diretor-geral.md) |
| Vendas | [lider-vendas](../agents/lider-vendas.md), [estrategista-de-vendas](../agents/estrategista-de-vendas.md), [consultor-whatsapp](../agents/consultor-whatsapp.md), [recuperador-de-carrinho](../agents/recuperador-de-carrinho.md), [vendedor-b2b](../agents/vendedor-b2b.md) |
| Sucesso do Cliente | [lider-sucesso-cliente](../agents/lider-sucesso-cliente.md), [tecnico-de-suporte](../agents/tecnico-de-suporte.md), [guardiao-pos-venda](../agents/guardiao-pos-venda.md) |
| Marketing e Conteúdo | [lider-marketing](../agents/lider-marketing.md), [roteirista-de-reels](../agents/roteirista-de-reels.md), [copywriter-de-loja](../agents/copywriter-de-loja.md), [social-media](../agents/social-media.md) |
| Tráfego Pago | [lider-trafego](../agents/lider-trafego.md), [criativos-de-anuncio](../agents/criativos-de-anuncio.md), [analista-de-midia](../agents/analista-de-midia.md) |
| Operações e Loja | [lider-operacoes](../agents/lider-operacoes.md), [auditor-da-loja](../agents/auditor-da-loja.md), [gestor-de-catalogo](../agents/gestor-de-catalogo.md), [guardiao-de-conformidade](../agents/guardiao-de-conformidade.md) |
| Dados e Inteligência | [lider-dados](../agents/lider-dados.md), [analista-de-vendas](../agents/analista-de-vendas.md), [detetive-de-mercado](../agents/detetive-de-mercado.md) |

Quem é quem e quando chamar: [organograma.md](organograma.md).

## As skills

| Skill | Para quê |
|---|---|
| [atendente-infinity-guard](../skills/atendente-infinity-guard/SKILL.md) | Atendente de vendas da Infinity Guard no WhatsApp |
| [campanha-sazonal](../skills/campanha-sazonal/SKILL.md) | Campanha 11.11 e Black Friday (26 a 29/11) da Infinity Guard |
| [catalogo-e-precos](../skills/catalogo-e-precos/SKILL.md) | Gestão do catálogo, preços, margem e estoque da Infinity Guard |
| [conteudo-semanal](../skills/conteudo-semanal/SKILL.md) | Pauta semanal de conteúdo da Infinity Guard |
| [descricao-de-produto](../skills/descricao-de-produto/SKILL.md) | Páginas de produto e SEO da Infinity Guard na Nuvemshop |
| [estrategista-de-vendas](../skills/estrategista-de-vendas/SKILL.md) | Estrategista de vendas da Infinity Guard, com o método das marcas de luxo (experiência de boutique, curadoria, narrativa, escassez honesta, preço que não cai, clienteling, pós-venda e comunidade) adaptado a uma loja online honesta |
| [monitor-de-gestao](../skills/monitor-de-gestao/SKILL.md) | Vigia da gestão da Infinity Guard |
| [painel-de-vendas](../skills/painel-de-vendas/SKILL.md) | Painel de vendas da Infinity Guard |
| [plano-de-midia](../skills/plano-de-midia/SKILL.md) | Plano de mídia e gestão do tráfego pago (Meta Ads) da Infinity Guard |
| [proposta-comercial](../skills/proposta-comercial/SKILL.md) | Proposta comercial da Infinity Guard para comércio, escritório, condomínio ou compra em quantidade |
| [prova-da-loja](../skills/prova-da-loja/SKILL.md) | Auditor de prova da loja Infinity Guard |
| [radar-de-concorrentes](../skills/radar-de-concorrentes/SKILL.md) | Radar de concorrentes da Infinity Guard |
| [reuniao-semanal](../skills/reuniao-semanal/SKILL.md) | Reunião semanal e direção da Infinity Guard |
| [revisor-de-promessas](../skills/revisor-de-promessas/SKILL.md) | Revisor de promessas e conformidade da Infinity Guard |
| [suporte-tecnico](../skills/suporte-tecnico/SKILL.md) | Suporte técnico e trocas da Infinity Guard |

## Índice de tudo

| Onde | O que é |
|---|---|
| [docs/raio-x-de-nicho.md](raio-x-de-nicho.md) | Raio X do mercado de segurança residencial (18/10/2026): concorrentes, preços e brechas |
| [docs/raio-x-de-nicho.html](raio-x-de-nicho.html) | O mesmo Raio X, versão visual |
| [docs/mapa-de-sistemas.md](mapa-de-sistemas.md) | A ordem dos sistemas e o status de cada um |
| [docs/mapa-de-dados.md](mapa-de-dados.md) | Fonte da verdade de cada dado |
| [docs/mapa-da-autonomia.md](mapa-da-autonomia.md) | Nível de autonomia: o que roda sozinho, o que espera o seu "pode" e o que está bloqueado |
| [docs/organograma.md](organograma.md) | Os 23 funcionários e quando chamar cada um |
| [docs/reunioes](reunioes) | Atas das reuniões da equipe |
| [skills/prova-da-loja/auditorias](../skills/prova-da-loja/auditorias) | Auditorias do site |
| [skills/campanha-sazonal/campanhas](../skills/campanha-sazonal/campanhas) | Propostas de campanha (11.11 e Black Friday) |
| [skills/conteudo-semanal/pautas](../skills/conteudo-semanal/pautas) | Pautas de Reels já geradas |
| [skills/atendente-infinity-guard/references/catalogo.json](../skills/atendente-infinity-guard/references/catalogo.json) | Catálogo único de preços |
| [app/rota-do-milhao.html](../app/rota-do-milhao.html) | App Rota do Milhão (gestão, equipe, publicar, placar) |
| [desktop](../desktop) | App do Windows (Electron) |
| [android](../android) | App Android |
| [mcp_servers](../mcp_servers) | Servidor MCP com as ferramentas das skills |
| [core](../core) | Orquestrador: daemon, fila, regras, rotinas, aprovações e resumo |
| [tools](../tools) | Coleta de métricas (Nuvemshop e Meta, só leitura), disparo dos agentes e esta central |
| [config/orquestrador.json](../config/orquestrador.json) | Padrões do orquestrador (o seu ajuste vai em orquestrador.local.json) |
| [plugins](../plugins) | Um plugin por squad (gerado) |
| [dados](../dados) | Onde você coloca os CSVs da Nuvemshop e da Meta e o backup do app (fora do Git) |
