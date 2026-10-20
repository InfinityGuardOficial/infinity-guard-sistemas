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

## As skills (13)

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
| `skills/reuniao-semanal/` | Pauta da semana por squad, com top 3 e a fonte de cada linha. | Direção |
| `skills/*.zip` | Cada skill compactada, para enviar no claude.ai. | |

## Outras pastas

| Pasta | O que é |
|---|---|
| `agents/` | Os 22 funcionários. |
| `.claude-plugin/` | Plugin "infinity-guard" com a equipe e as skills (instala com um comando, veja abaixo). |
| `app/rota-do-milhao.html` | **Rota do Milhão**: app pessoal com a trilha de 48 semanas até R$ 1 milhão/ano, missões nos horários livres do CLT com prova, cobrança, placar, Estúdio IA e agenda com alarmes (.ics). Publicado como página privada no claude.ai. |
| `docs/organograma.md` | Quem é quem e quando chamar cada funcionário. |
| `docs/raio-x-de-nicho.md` / `.html` | Raio X do mercado de segurança residencial (18/10/2026): concorrentes, preços, brechas. |
| `docs/mapa-de-sistemas.md` | A ordem dos sistemas. |

## Instalar tudo de uma vez (plugin, recomendado)

No Claude Code, em qualquer pasta (por exemplo a pasta do projeto "Workshop IA autônoma"):
```
/plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas
/plugin install infinity-guard@infinity-guard-sistemas
```
Isso instala os 22 funcionários e as 13 skills. Como o repositório é privado, o Claude Code precisa estar logado no GitHub com uma conta que tenha acesso (`gh auth login`). Para atualizar depois: `/plugin marketplace update infinity-guard-sistemas`.

Para instalar só num projeto (e quem abrir a pasta também ter), rode os comandos acima e escolha "project" quando o Claude Code perguntar o escopo.

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

Os preços e links ficam em `skills/atendente-infinity-guard/references/catalogo.json` (campo `atualizado_em` mostra a data). Mudou o preço na Nuvemshop? Peça ao `gestor-de-catalogo`, ou rode a skill `catalogo-e-precos` (ela recalcula Pix, parcelas e a data):

```bash
cd skills/catalogo-e-precos
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90           # simula
python3 scripts/catalogo.py atualizar --produto kit-cam-2 --preco 379.90 --gravar  # grava
python3 scripts/catalogo.py validar
```

## Rodar todos os testes

```bash
for d in skills/*/; do (cd "$d" && python3 -m unittest discover -s tests -q) || echo "falhou: $d"; done
```

## Próximos sistemas

Veja `docs/mapa-de-sistemas.md`. As outras skills seguem a mesma instalação da atendente: troque o nome da pasta nos comandos acima.

---
Infinity Guard · WhatsApp (31) 98667-9178 · https://infinityguard.com.br
