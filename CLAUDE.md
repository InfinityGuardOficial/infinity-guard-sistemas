# Infinity Guard · instruções do projeto para o Claude Code

Loja online de câmeras Wi-Fi, alarmes e fechaduras inteligentes, vendida por **dropshipping** (o fornecedor envia direto ao cliente) pela Nuvemshop, Instagram e WhatsApp (31) 98667-9178. Slogan: "Segurança onde você estiver". O dono trabalha em regime CLT e usa os horários livres; meta: R$ 1 milhão por ano.

## Regras da casa (valem para toda resposta, código e texto)

- Preço, Pix e parcela só saem do catálogo (`skills/atendente-infinity-guard/references/catalogo.json`; a fonte da verdade é o Catálogo do app Rota do Milhão, ver `docs/mapa-de-dados.md`).
- Nunca invente código Anatel, prazo de garantia, CNPJ, depoimento, avaliação ou número sem fonte.
- Nunca prometa "100% seguro", instalação, câmera 4G, produto "já configurado" ou prazo de entrega menor que o do catálogo. A promessa certa: "quando chegar, a gente configura junto com você por vídeo no WhatsApp".
- Todo texto para a rua passa pelo revisor: `python3 skills/revisor-de-promessas/scripts/revisar.py --texto "..."` (ou a ferramenta MCP `revisar_texto`).
- **Gasto, publicação, mensagem para cliente real, mudança no site ou na conta de anúncios: só com o "pode" do dono.** Isso vale também para rotinas agendadas.
- Português do Brasil, frases curtas, tom de tranquilidade (nunca medo).

## Antes de mudar código

- Mudança pequena: faça e teste. Mudança grande (vários arquivos, dados do app, rotinas): escreva o plano em poucas linhas antes e confirme com o dono.
- Testes das skills: `bash scripts/empacotar-skills.sh` (roda os testes das 14 skills e só refaz os .zip se todos passarem).
- Mudou `agents/` ou `skills/`? Rode `python3 scripts/gerar-plugins.py` para atualizar os plugins de squad e `claude plugin validate .`.
- Servidor MCP: `python3 -m unittest discover -s mcp_servers/tests`.
- O app (`app/rota-do-milhao.html`) é uma página privada no claude.ai; os dados dele ficam na área privada do dono (mapa em `docs/mapa-de-dados.md`). Não grave dados do dono no Git.

## Ferramentas disponíveis

- **Equipe (plugin `infinity-guard`, já ativo neste projeto):** 22 funcionários em 7 squads e 14 skills. Chame pelo nome: "Use o gestor-de-catalogo: ...".
- **Trabalho em paralelo:** quando uma tarefa tem partes independentes (ex.: reunião geral, campanha com conteúdo + mídia + operação), dispare os funcionários de cada parte ao mesmo tempo como subagentes e junte as entregas no fim. Para orquestrações grandes, use o Workflow quando o dono pedir.
- **Servidor MCP `infinity-guard`** (`.mcp.json`, aprovar na primeira vez): `revisar_texto`, `validar_catalogo`, `comparar_concorrentes`, `recomendar_kit`, `plano_de_midia`, `montar_campanha`, `pauta_da_semana`, `reuniao_semanal`, `vigiar_gestao`. Todas só leem e calculam.
- **Rotinas agendadas** (fora do repositório, na conta do dono): 05:17 radar e pauta (com proposta de publicação), 05:52 cobrança da manhã, 06:13 de segunda diretor-geral (plano da semana, ordens e propostas), 07:07 zelador (confere e corrige as rotinas), 11:43 e 16:43 vigia da gestão, 19:48 cobrança da noite. Elas leem o app e avisam no celular.

## Autonomia (nível 4)

- A equipe planeja, produz, se vigia e se corrige; o dono decide na **Central → Aprovações** do app (`estado/aprovacoes`).
- Propostas só dos tipos `publicacao`, `mensagem`, `conteudo`, `preco` e `operacao`. **Nenhuma proposta de anúncio pago ou gasto: o teto está em R$ 0 até o dono liberar.**
- Mapa completo do que roda sozinho, do que espera o dono e do que está bloqueado: `docs/mapa-da-autonomia.md`.
