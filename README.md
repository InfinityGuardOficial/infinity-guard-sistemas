# Infinity Guard — Sistemas

**Segurança onde você estiver.** Sistemas da Infinity Guard (https://infinityguard.com.br) para usar dentro do Claude Code: skills prontas, estudos de mercado e o mapa do que vem a seguir.

## A equipe (22 funcionários em 7 squads)

Cada funcionário é um agente do Claude Code (pasta `agents/`) com cargo, missão, regras e as skills do trabalho dele já carregadas. Quem lidera cada squad distribui o trabalho; o `diretor-geral` decide as prioridades da semana. Organograma completo: [`docs/organograma.md`](docs/organograma.md).

| Squad | Líder | Funcionários |
|---|---|---|
| Direção | `diretor-geral` | coordena os 6 líderes |
| Vendas | `lider-vendas` | `consultor-whatsapp`, `recuperador-de-carrinho`, `vendedor-b2b` |
| Sucesso do Cliente | `lider-sucesso-cliente` | `tecnico-de-suporte`, `guardiao-pos-venda` |
| Marketing e Conteúdo | `lider-marketing` | `roteirista-de-reels`, `copywriter-de-loja`, `social-media` |
| Tráfego Pago | `lider-trafego` | `criativos-de-anuncio`, `analista-de-midia` |
| Operações e Loja | `lider-operacoes` | `auditor-da-loja`, `gestor-de-catalogo`, `guardiao-de-conformidade` |
| Dados e Inteligência | `lider-dados` | `analista-de-vendas`, `detetive-de-mercado` |

**Como usar:** depois de instalar o plugin, peça em português normal. O Claude escolhe o funcionário pela descrição, ou você chama pelo nome:

> Use o diretor-geral: quais as 3 prioridades desta semana?
> Use o tecnico-de-suporte: a cliente diz que a câmera não conecta no Wi-Fi.
> Use o vendedor-b2b: a padaria do bairro quer 2 kits de câmera e um alarme.

Digite `/agents` no Claude Code para ver a equipe instalada.

**Regras que valem para todos:** preço só sai de script (catálogo único), nada de Anatel, garantia, CNPJ ou depoimento inventado, nada de instalação ou câmera 4G, todo texto para a rua passa pelo `revisor-de-promessas`, e gasto, publicação ou mensagem para cliente real só com o seu "pode".

## As skills (14)

| Pasta | O que é | Quem usa |
|---|---|---|
| `skills/atendente-infinity-guard/` | Atendente do WhatsApp: indica o kit certo, quebra objeções, recupera carrinho, pós-venda de 7 dias e prompt do robô. **Guarda o catálogo único de preços.** | Vendas, Sucesso |
| `skills/suporte-tecnico/` | Diagnóstico de câmera, alarme e fechadura com passo a passo para o WhatsApp; trocas e garantia pelo CDC. | Sucesso, Conformidade |
| `skills/proposta-comercial/` | Proposta para comércio, escritório e condomínio com preço, Pix, parcelas, validade e limite de desconto. | Vendas B2B |
| `skills/prova-da-loja/` | Auditor do site: CNPJ, Anatel, garantia, avaliações, troca, contato e rastros de fornecedor. | Operações |
| `skills/catalogo-e-precos/` | Valida e atualiza o catálogo (Pix, parcelas, data), margem por produto e estoque. | Operações |
| `skills/revisor-de-promessas/` | Barra promessa enganosa antes de publicar (100% seguro, instalação, 4G, Anatel ou garantia sem documento, "de/por" maquiado). | Todos |
| `skills/descricao-de-produto/` | Página de produto para a Nuvemshop: título SEO, meta, descrição curta e HTML. | Marketing, Operações |
| `skills/campanha-sazonal/` | Campanha 11.11 e Black Friday: kits, preço, calendário e mensagens. | Marketing, Tráfego |
| `skills/conteudo-semanal/` | 3 roteiros de Reels por semana sem repetir tema. | Marketing |
| `skills/plano-de-midia/` | CPA máximo, ROAS de equilíbrio, orçamento, divisão do funil e régua escalar/manter/pausar. | Tráfego |
| `skills/painel-de-vendas/` | Painel HTML da exportação de pedidos da Nuvemshop. | Dados, Vendas |
| `skills/radar-de-concorrentes/` | Preços de concorrentes com fonte e a nossa posição por produto. | Dados |
| `skills/monitor-de-gestao/` | Vigia da gestão: aplica as regras de alerta aos dados do app (entrega atrasada, pedido não repassado, sem rastreio, margem negativa, mês no vermelho, follow-up vencido, estoque esgotado, fornecedor impontual) e diz quem cuida. As mesmas regras rodam no app e na notificação "Vigia da gestão". | Todos os líderes, Operações, Sucesso, Vendas, Dados |
| `skills/reuniao-semanal/` | Pauta da semana por squad, com top 3 e a fonte de cada linha. | Direção |
| `skills/*.zip` | Cada skill compactada, para enviar no claude.ai. | |

## Outras pastas

| Pasta | O que é |
|---|---|
| `agents/` | Os 22 funcionários. |
| `.claude-plugin/` | Plugin "infinity-guard" com a equipe e as skills (instala com um comando, veja abaixo). |
| `app/rota-do-milhao.html` | **Rota do Milhão**: app pessoal nas cores da marca, com Gestão (ERP, CRM, WMS, TMS, EDI e VMI integrados), os 22 funcionários (IA), radar e pauta diária, contrato sem volta, Kit da marca, estúdio de Reels e artes de anúncio, aba Publicar, trilha de 48 semanas e placar até R$ 1 milhão/ano. Página privada no claude.ai. |
| `desktop/` | App do Windows x64 (Electron): abre o Rota do Milhão com o seu login e avisa nos turnos pela bandeja. |
| `android/` | App Android (APK): abre o Rota do Milhão e avisa nos turnos. |
| `.github/workflows/apps.yml` | Gera o instalador do Windows e o APK a cada mudança em `desktop/` ou `android/` (Actions → Apps). |
| `docs/organograma.md` | Quem é quem e quando chamar cada funcionário. |
| `docs/raio-x-de-nicho.md` / `.html` | Raio X do mercado de segurança residencial (18/10/2026): concorrentes, preços, brechas. |
| `core/`, `tools/`, `config/` | Orquestrador automático (veja a seção abaixo). |
| `docs/mapa-de-sistemas.md` | A ordem dos sistemas. |
| `docs/mapa-da-autonomia.md` | O que roda sozinho, o que espera o "pode" do dono e o que está bloqueado (nível 4). |
| `docs/mapa-de-dados.md` | Onde mora cada dado, qual é a fonte da verdade, quem cuida e como atualizar. |
| `scripts/empacotar-skills.sh` | Testa todas as skills e refaz os .zip. |
| `plugins/` e `scripts/gerar-plugins.py` | Um plugin por squad, gerado a partir de `agents/` e `skills/`. |

## Já ativado neste projeto

O arquivo `.claude/settings.json` ativa o plugin `infinity-guard` (22 funcionários e 14 skills) para quem abrir esta pasta no Claude Code, no computador ou na nuvem. Na primeira vez, o Claude Code pergunta se você confia no projeto e se quer instalar o plugin: responda que sim. Confira com `/agents` e `/skills`.

## Servidor MCP

`mcp_servers/infinity_guard_mcp.py` é um servidor MCP (Model Context Protocol, stdio, sem dependências) que expõe 9 ferramentas das skills para o Claude Code ou o Claude Desktop: `revisar_texto`, `validar_catalogo`, `comparar_concorrentes`, `recomendar_kit`, `plano_de_midia`, `montar_campanha`, `pauta_da_semana`, `reuniao_semanal` e `vigiar_gestao`. Todas só leem e calculam.

Neste projeto ele já está em `.mcp.json`: na primeira vez, o Claude Code pede para aprovar o servidor `infinity-guard`. Para usar em outro lugar:
```
claude mcp add infinity-guard -- python3 /caminho/infinity-guard-sistemas/mcp_servers/infinity_guard_mcp.py
```
No Claude Desktop: Configurações → Desenvolvedor → Editar configuração, e adicione o mesmo comando em `mcpServers`.

As regras do projeto para o Claude Code ficam em `CLAUDE.md`.

## Instalar tudo de uma vez (plugin, recomendado)

No Claude Code, em qualquer pasta (por exemplo a pasta do projeto "Workshop IA autônoma"):
```
/plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas
/plugin install infinity-guard@infinity-guard-sistemas
```
Isso instala os 22 funcionários e as 14 skills. Se o repositório estiver privado, o Claude Code precisa estar logado no GitHub com uma conta que tenha acesso (`gh auth login`). Para atualizar depois: `/plugin marketplace update infinity-guard-sistemas`.

Para instalar só num projeto (e quem abrir a pasta também ter), rode os comandos acima e escolha "project" quando o Claude Code perguntar o escopo.

### Um plugin por squad

Prefere levar só uma parte da equipe? Cada squad é um plugin separado, com os funcionários dele, as skills que eles usam, o catálogo de preços (`atendente-infinity-guard`) e o `revisor-de-promessas`:

| Plugin | Funcionários |
|---|---|
| `infinity-guard-direcao` | diretor-geral (com as skills que a reunião semanal lê) |
| `infinity-guard-vendas` | lider-vendas, consultor-whatsapp, recuperador-de-carrinho, vendedor-b2b |
| `infinity-guard-sucesso-cliente` | lider-sucesso-cliente, tecnico-de-suporte, guardiao-pos-venda |
| `infinity-guard-marketing` | lider-marketing, roteirista-de-reels, copywriter-de-loja, social-media |
| `infinity-guard-trafego` | lider-trafego, criativos-de-anuncio, analista-de-midia |
| `infinity-guard-operacoes` | lider-operacoes, auditor-da-loja, gestor-de-catalogo, guardiao-de-conformidade |
| `infinity-guard-dados` | lider-dados, analista-de-vendas, detetive-de-mercado |

```
/plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas
/plugin install infinity-guard-vendas@infinity-guard-sistemas
```
Troque `vendas` pelo squad que quiser; dá para instalar vários. Não instale o `infinity-guard` completo junto com os de squad no mesmo projeto, para não ter funcionário repetido.

As pastas `plugins/` são geradas: edite sempre `agents/` e `skills/` da raiz e rode `python3 scripts/gerar-plugins.py`.

## Como instalar uma skill solta no Claude Code

Você precisa do Claude Code instalado e do Python 3 (os scripts da skill usam Python).

### Opção 1: para você, em qualquer projeto (recomendada)

A skill fica disponível em todas as pastas onde você abrir o Claude Code.

**Mac / Linux**
```bash
git clone https://github.com/InfinityGuardOficial/infinity-guard-sistemas.git
mkdir -p ~/.claude/skills
cp -r infinity-guard-sistemas/skills/atendente-infinity-guard ~/.claude/skills/
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/InfinityGuardOficial/infinity-guard-sistemas.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills"
Copy-Item -Recurse infinity-guard-sistemas\skills\atendente-infinity-guard "$HOME\.claude\skills\"
```

### Opção 2: só dentro de um projeto

Use quando quiser a skill só numa pasta (por exemplo, a pasta da loja), e para que quem trabalhar nessa pasta também tenha.

```bash
cd caminho/da/sua/pasta
mkdir -p .claude/skills
cp -r /caminho/para/infinity-guard-sistemas/skills/atendente-infinity-guard .claude/skills/
```

### Opção 3: pelo arquivo .zip

- **No claude.ai (navegador ou app):** Configurações → Capacidades → Skills → enviar `skills/atendente-infinity-guard.zip`.
- **No Claude Code:** descompacte o zip dentro de `~/.claude/skills/` (opção 1) ou de `.claude/skills/` no seu projeto (opção 2):
  ```bash
  unzip skills/atendente-infinity-guard.zip -d ~/.claude/skills/
  ```

### Conferir se funcionou

Abra o Claude Code de novo (as skills são lidas ao iniciar) e digite:

```
/skills
```

`atendente-infinity-guard` deve aparecer na lista. Depois é só pedir em português normal, por exemplo:

> Cliente mora em casa, quer 3 câmeras, tem Wi-Fi e viaja muito. Monta o kit pra Ana.

A estrutura instalada fica assim:
```
~/.claude/skills/atendente-infinity-guard/
├── SKILL.md
├── prompt-atendente.txt
├── references/   (catálogo, roteiro, objeções, pós-venda)
├── scripts/      (recomendar_kit.py, carrinho.py, exportar_prompt.py)
└── tests/
```

Os funcionários (agentes) também podem ser copiados soltos: `cp infinity-guard-sistemas/agents/*.md ~/.claude/agents/`. Copie junto as skills, porque cada funcionário carrega as dele.

As skills que usam preço leem o catálogo da `atendente-infinity-guard` instalada ao lado: instale sempre a atendente junto.

## Atualizar preços

A fonte da verdade dos preços é o Catálogo do app Rota do Milhão (Mais → Catálogo e preços). O botão "Copiar comando para o gestor-de-catalogo" gera o pedido que atualiza `skills/atendente-infinity-guard/references/catalogo.json`, que as skills leem. Também dá para rodar a skill `catalogo-e-precos` direto (ela recalcula Pix, parcelas e a data):

```bash
cd skills/catalogo-e-precos
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90           # simula
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90 --gravar  # grava
python3 scripts/catalogo.py validar
```

## Rodar todos os testes e refazer os .zip

```bash
bash scripts/empacotar-skills.sh
```

## Orquestrador automático (core/ e tools/)

Um programa que fica rodando no seu computador e, a cada 30 minutos, lê os números da loja e chama o funcionário certo:

| Quando | Quem é chamado | O que entrega |
|---|---|---|
| Todo dia, a partir das 8h | `analista-de-vendas` | painel em `logs/paineis/` e 3 números + 1 ação |
| Entrou pedido pago novo no CSV | `guardiao-pos-venda` | rascunho do pós-venda (não envia) |
| A régua do `plano-de-midia` mandou pausar ou escalar um conjunto | `analista-de-midia` | o porquê de cada decisão |
| ROAS abaixo do equilíbrio | `lider-trafego` | causa provável e plano de 3 dias |
| Segunda-feira | `diretor-geral` | pauta da reunião e as 3 prioridades |

**De onde vêm os números:** a exportação de vendas da Nuvemshop que você salva em `dados/nuvemshop/` (o mais novo vale) e o Meta Ads só em modo leitura: pela API, se as variáveis `META_ACCESS_TOKEN` e `META_AD_ACCOUNT_ID` existirem, ou pelo CSV do Gerenciador em `dados/meta/`. Sem arquivo, o número fica vazio: nada é inventado.

**O que ele não faz sozinho:** gastar, mexer em anúncio, preço ou loja, falar com cliente ou publicar. Quando um funcionário recomenda isso, a recomendação vira um pedido em `logs/aprovacoes.json`, e quem executa é você. As regras estão em `.claude/CLAUDE.md`.

**Antes de ligar:** Python 3.10+ e o Claude Code instalado e logado (`claude` funcionando no terminal). Rode tudo da pasta do repositório.

### Windows (PowerShell)

```powershell
cd C:\caminho\infinity-guard-sistemas
python core\daemon_orchestrator.py uma-vez        # um ciclo para testar
Start-Process pythonw -ArgumentList "core\daemon_orchestrator.py" -WorkingDirectory (Get-Location) -WindowStyle Hidden   # liga em segundo plano
python core\daemon_orchestrator.py status         # fila, últimas tarefas e o que espera o seu "pode"
python core\daemon_orchestrator.py parar          # desliga
```

Para ligar sozinho quando você entrar no Windows (Agendador de Tarefas):
```powershell
schtasks /Create /TN "Infinity Guard Orquestrador" /SC ONLOGON /TR "pythonw `"$PWD\core\daemon_orchestrator.py`""
```
Para tirar: `schtasks /Delete /TN "Infinity Guard Orquestrador" /F`. Token da Meta (opcional, só leitura): `setx META_ACCESS_TOKEN "seu_token"` e `setx META_AD_ACCOUNT_ID "act_123..."`, depois abra um terminal novo.

### Mac / Linux

```bash
cd caminho/infinity-guard-sistemas
python3 core/daemon_orchestrator.py uma-vez
nohup python3 core/daemon_orchestrator.py > /dev/null 2>&1 &
python3 core/daemon_orchestrator.py status
python3 core/daemon_orchestrator.py parar
```

### Ajustes e ferramentas

- Mudar intervalo, hora do relatório, margem ou desligar os agentes: crie `config/orquestrador.local.json` só com as chaves que mudam, por exemplo `{"intervalo_minutos": 60, "margem_bruta": 0.3}`. Os padrões estão em `config/orquestrador.json`.
- Chamar um funcionário na mão: `tools/run_claude_agent.sh analista-de-vendas "Resuma a semana"` (no PowerShell: `python tools\run_claude_agent.py --agente analista-de-vendas --tarefa "Resuma a semana"`).
- Ver só as métricas: `python3 tools/coletar_metricas.py` (grava `logs/metrics.json`).
- Logs: `logs/system.log`, `logs/errors.log`; respostas dos funcionários em `logs/agentes/`.
- Testes: `python3 -m unittest discover -s tests`.

## Próximos sistemas

Veja `docs/mapa-de-sistemas.md`. As outras skills seguem a mesma instalação da atendente: troque o nome da pasta nos comandos acima.

---
Infinity Guard · WhatsApp (31) 98667-9178 · https://infinityguard.com.br
