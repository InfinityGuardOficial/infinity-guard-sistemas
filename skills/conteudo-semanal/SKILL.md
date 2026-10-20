---
name: conteudo-semanal
description: Pauta semanal de conteúdo da Infinity Guard. Use toda segunda (ou quando pedirem "conteúdo da semana", "roteiros", "o que postar") para gerar 3 roteiros de Reels com os temas quentes do nicho, sem repetir tema recente, com gancho, fala, texto na tela e legenda com chamada para o WhatsApp.
---

# Conteúdo Semanal — 3 Reels toda segunda

O conteúdo existe para levar gente ao WhatsApp, onde a skill `atendente-infinity-guard` vende. Todo roteiro fala da tese "segurança boa começa pela casa de quem vai usar, não pela vitrine" e termina chamando para o WhatsApp.

Arquivos:
- `scripts/pauta_semana.py`: escolhe 3 temas para a semana (segunda, quarta e sexta), em formatos diferentes, sem repetir tema das últimas 2 semanas. Nas semanas do 11.11 (09/11) e da Black Friday (23/11), o tema da campanha entra primeiro.
- `references/temas.json`: banco de temas com fonte (Raio X de 18/10/2026): senha de fábrica, câmera offline, casa certa, Anatel, fechadura facial, casa vazia, app chinês, qual casa, Black Friday, suporte que responde, 4G solar.
- `pautas/`: pautas geradas e `historico.json` (o que já foi usado).

## Modos

### 1. Pauta da semana
```bash
python3 scripts/pauta_semana.py --registrar --saida pautas/$(date +%F).md
```
`--semana AAAA-MM-DD` para outra semana. `--registrar` grava no histórico (use só na pauta que vai ser gravada). Entregue ao dono a pauta inteira e uma linha dizendo qual gravar primeiro.

### 2. Variar a fala
Se o dono pedir outra versão, passe o tema, a base e o formato para a Máquina de Reels (se instalada) ou reescreva mantendo os fatos da `fonte` e a chamada do WhatsApp.

### 3. Renovar os temas
O script avisa quando o banco tem mais de 45 dias. Rode o Detetive de Nicho e acrescente temas novos em `temas.json` no mesmo formato (id, formato, produto, fonte, gancho, fala, tela, legenda). Tema com prazo leva `janela`; tema que depende de algo publicado no site leva `requer`.

### 4. Rodar sozinho toda segunda
No Claude Code, peça: "agende toda segunda às 8h: rode a skill conteudo-semanal e me mande a pauta". Num projeto do Claude, a tarefa agendada roda a skill e posta a pauta na conversa.

## Regras
- Nunca invente história de cliente, depoimento ou número sem fonte.
- O tema `anatel` só entra com `--anatel-publicado`, depois que o código estiver no site (não dá para dizer "eu confiro" antes).
- Não prometa instalação, câmera 4G ou sem Wi-Fi.
- Testes: `python3 -m unittest discover -s tests`.

## Vídeos com IA (Reels 9:16)
`videos/gerar_video.py` monta um Reel a partir de `videos/<nome>/cenas.json` (exemplo: `eu-tranquei-o-portao`).
- `FAL_KEY=... python3 videos/gerar_video.py eu-tranquei-o-portao gerar`: gera as cenas de IA no fal.ai (imagem com o rosto de `videos/ref-maximiliano.jpg`, depois animação Kling). Precisa da chave `FAL_KEY` no ambiente e do domínio `queue.fal.run` liberado na rede.
- `python3 videos/gerar_video.py eu-tranquei-o-portao montar`: junta as cenas com texto na tela, legenda, aviso "Cena ilustrativa criada com IA" e cartela final. Gravações reais (`cena7.mp4`, `cena8.mp4`) e `narracao.mp3` colocadas na pasta entram automaticamente.
- Antes de publicar: conferir o rosto cena a cena e passar pelo `revisor-de-promessas`.
