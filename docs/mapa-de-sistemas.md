# Mapa de Sistemas — Infinity Guard · 18/10/2026

Base: Raio X de Nicho de 18/10 (`infinity-guard/raio-x-de-nicho.md`), Relatório de Posicionamento de 17/10 e o catálogo lido em infinityguard.com.br em 18/10.

Regra que guia a ordem: **primeiro a conversa que vende, depois a prova que sustenta o preço, só então o tráfego.** O Raio X mostra que seus preços estão acima da Intelbras e das ofertas de marketplace; o que justifica a diferença é orientação antes da compra e suporte que responde depois. Os sistemas abaixo existem para entregar exatamente isso, sem depender de equipe.

## Visão geral

| # | Sistema | Tipo no Claude Code | O que resolve | Prazo | Status |
|---|---|---|---|---|---|
| 1 | **Atendente de Vendas WhatsApp** | Skill `atendente-infinity-guard` (+ scripts) | Qualifica a casa em 3 a 5 perguntas, indica o kit certo com preço e Pix, responde objeções, recupera carrinho e entrega o guia "câmera entregue segura" | Agora (antes de 11/11) | **Construído** (`skills/atendente-infinity-guard/`) |
| 2 | Recuperação de carrinho e pós-venda 7 dias | Modo dentro da skill 1 + app da Nuvemshop | Sequência de mensagens D0/D1/D3 e guia dos primeiros 7 dias | Agora | **Construído** como modo da skill 1; falta ligar no app da loja |
| 3 | Auditor de Prova da Loja | Skill `prova-da-loja` | Checa site e cada produto: CNPJ, prazo de garantia, avaliações, fotos reais; gera lista de correção | Até 25/10 | **Construído** (`skills/prova-da-loja/`); 1ª auditoria em 18/10 |
| 4 | Campanha 11.11 e Black Friday | Skill `campanha-sazonal` (usa Máquina de Anúncios e Reels) | Oferta de kit, cupom, calendário de posts e mensagens de WhatsApp para 11/11 e 26 a 29/11 | Até 04/11 | **Construído** (`skills/campanha-sazonal/`); proposta com 10% em `campanhas/` |
| 5 | Conteúdo semanal no automático | Rotina agendada no Claude (trigger) + Máquina de Reels | Toda segunda: 3 roteiros com os temas quentes (câmera invadida, offline, fechadura facial) | Depois do 4 | **Construído** (`skills/conteudo-semanal/`) + agendamento às segundas |
| 6 | Painel de vendas | Artifact com dados da Nuvemshop | Conversas, kits indicados, carrinhos recuperados, vendas por canal | Depois das primeiras 20 vendas | **Construído** (`skills/painel-de-vendas/`); falta o CSV de pedidos |
| 7 | Plugin "Infinity Guard" | Plugin do Claude Code no GitHub | Junta as skills num pacote só, instalável com um comando | Thread 4 do plano | **Construído** (`.claude-plugin/` no pacote do repositório); falta publicar no GitHub |
| 8 | **Equipe Infinity Guard** | 22 agentes do plugin em 7 squads + 8 skills novas (suporte-tecnico, proposta-comercial, catalogo-e-precos, revisor-de-promessas, descricao-de-produto, plano-de-midia, radar-de-concorrentes, reuniao-semanal) | Cada trabalho tem um "funcionário" com cargo, regras e skills; o diretor-geral distribui a semana | 19/10 | **Construído** (`agents/`, organograma em `docs/organograma.md`) |

## 1. Atendente de Vendas WhatsApp (prioridade máxima)

**Por que primeiro:** 25% das mensagens chegam fora do horário e conversa com IA converte igual à humana [INDÍCIO — OmniChat]. As queixas do mercado são "WhatsApp sem resposta" [CONFIRMADO — Reclame Aqui 2026]. É a sua brecha número 1 e não exige gastar com anúncio.

**O que faz:**
- **Modo atender:** você cola a mensagem do cliente; a skill responde como atendente da Infinity Guard, faz as perguntas sobre a casa (tipo de imóvel, quantas entradas, Wi-Fi, quem fica fora, orçamento) e indica o kit com link, preço cheio, Pix e parcelas.
- **Modo recomendar:** script `recomendar_kit.py` monta o kit sempre com os preços do catálogo, sem a IA inventar valor.
- **Modo carrinho:** gera as 3 mensagens de recuperação de carrinho com o nome do cliente e o produto.
- **Modo pós-venda:** manda o guia "câmera entregue segura" (trocar senha, atualizar, rede 2,4 GHz) e o acompanhamento dos 7 dias.
- **Modo exportar:** `exportar_prompt.py` gera o prompt pronto para colar no robô de WhatsApp que você escolher (app da Nuvemshop, OmniChat, ou outro com IA), para atender sozinho 24 horas.

**Regras de segurança da skill:** nunca inventa código Anatel, prazo de garantia, CNPJ ou especificação; nunca promete câmera 4G ou instalação (a loja não vende); passa para você (humano) em reclamação, troca, defeito ou pedido acima de R$ 3.000.

**Defaults que escolhi:** preços do site em 18/10; desconto Pix de 10% (o que o site mostra); itens de home office só entram como complemento; cartão de memória fica fora porque está esgotado.

## 2. Recuperação de carrinho e pós-venda

Já vem dentro da skill 1. Para rodar sozinho, falta você instalar na Nuvemshop um app de WhatsApp com carrinho abandonado (o Raio X encontrou CloudWhats e Recupera Já [INDÍCIO]) e colar nele as mensagens que a skill gera. Ticket de referência do carrinho abandonado no setor: R$ 619 [INDÍCIO — OmniChat].

## 3. Auditor de Prova da Loja

O Raio X é claro: "não dá para ser caro e anônimo ao mesmo tempo". Antes de qualquer anúncio, a skill confere página por página o que falta (CNPJ, garantia com prazo, avaliações, política de troca legível, foto real) e devolve uma lista de correção em ordem.

## 4. Campanha 11.11 e Black Friday

11.11 com previsão de R$ 3,17 bilhões e Black Friday de 26 a 29/11 com R$ 13,3 bilhões [CONFIRMADO — Neotrust/Confi]. A skill monta a oferta de kit (por exemplo, kit 2 câmeras + fechadura com cupom), os anúncios (via Máquina de Anúncios), os Reels (via Máquina de Reels) e as mensagens de WhatsApp para a base que a skill 1 juntou.

## 5 a 7. Depois das primeiras vendas

Conteúdo semanal por rotina agendada, painel de vendas e o plugin no GitHub vêm na sequência. O plugin junta tudo para instalar com um comando (thread 4 do plano).

## O que só você pode fazer (sem isso, nenhum sistema vende)

1. Anatel: tarefa sua para as férias de novembro, só no app (Central → "Tarefa sua").
2. Colocar no rodapé do site o CNPJ e o prazo de garantia por produto.
3. Escolher e instalar o app de WhatsApp com IA na Nuvemshop (a skill gera o conteúdo; a instalação é sua).
4. Revisar o preço dos itens que não aguentam a comparação (kit 2 câmeras e fechadura facial).
