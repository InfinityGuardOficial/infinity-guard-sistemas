# Infinity Guard — Sistemas

**Segurança onde você estiver.** Sistemas da Infinity Guard (https://infinityguard.com.br) para usar dentro do Claude Code: skills prontas, estudos de mercado e o mapa do que vem a seguir.

## O que tem aqui

| Pasta | O que é |
|---|---|
| `skills/atendente-infinity-guard/` | Atendente de vendas do WhatsApp: indica o kit certo para a casa do cliente, quebra objeções, recupera carrinho abandonado, manda o pós-venda de 7 dias e gera o prompt do robô de WhatsApp. |
| `skills/atendente-infinity-guard.zip` | A mesma skill compactada, para enviar no claude.ai. |
| `skills/prova-da-loja/` | Auditor de prova da loja: confere CNPJ, código Anatel, garantia com prazo, avaliações, troca e contato em cada página e devolve a lista de correção em ordem. |
| `skills/campanha-sazonal/` | Campanha 11.11 e Black Friday (26 a 29/11): kits com preço e Pix do catálogo, calendário dia a dia e mensagens de WhatsApp. |
| `skills/conteudo-semanal/` | 3 roteiros de Reels por semana com os temas quentes, sem repetir tema. |
| `skills/painel-de-vendas/` | Painel HTML a partir da exportação de pedidos da Nuvemshop: faturamento, ticket, Pix, cupons e WhatsApp. |
| `skills/*.zip` | Cada skill compactada, para enviar no claude.ai. |
| `.claude-plugin/` | Plugin "infinity-guard" com todas as skills (instala com um comando, veja abaixo). |
| `docs/raio-x-de-nicho.md` / `.html` | Raio X do mercado de segurança residencial (18/10/2026): concorrentes, preços, brechas. |
| `docs/mapa-de-sistemas.md` | A ordem dos sistemas que serão construídos. |

## Instalar tudo de uma vez (plugin)

No Claude Code, depois que o repositório estiver no GitHub:
```
/plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas
/plugin install infinity-guard@infinity-guard-sistemas
```

## Como instalar a skill no Claude Code

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

## Atualizar preços

Os preços e links ficam em `skills/atendente-infinity-guard/references/catalogo.json` (campo `atualizado_em` mostra a data). Mudou o preço na Nuvemshop, mude aqui, rode os testes e copie a skill de novo para a pasta de skills.

```bash
cd skills/atendente-infinity-guard
python3 -m unittest discover -s tests
```

## Próximos sistemas

Veja `docs/mapa-de-sistemas.md`. As outras skills seguem a mesma instalação da atendente: troque o nome da pasta nos comandos acima.

---
Infinity Guard · WhatsApp (31) 98667-9178 · https://infinityguard.com.br
