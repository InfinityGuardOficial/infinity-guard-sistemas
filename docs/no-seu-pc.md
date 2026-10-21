# No seu PC · Infinity Guard

Tudo o que precisa das mãos do dono para o sistema rodar sozinho: ligar o orquestrador no Windows, fazer os números entrarem sem exportar CSV e decidir as aprovações em segundos.

## 1. Orquestrador ligado sozinho (uma vez, uns 5 minutos)

Precisa de: Python 3.9 ou mais novo ([python.org](https://www.python.org/downloads/), marque "Add python.exe to PATH"), Git e o Claude Code instalado e logado (`claude` funcionando no terminal).

1. Abra o PowerShell e baixe o repositório (se ainda não tiver):
   ```powershell
   git clone https://github.com/InfinityGuardOficial/infinity-guard-sistemas "$env:USERPROFILE\infinity-guard-sistemas"
   ```
   Prefira essa pasta à do OneDrive: os logs mudam a cada 30 minutos e o OneDrive fica sincronizando à toa.
2. Dois cliques em `scripts\windows\instalar-orquestrador.cmd` (dentro da pasta acima).

O instalador:
- puxa a versão nova do repositório;
- atualiza o plugin `infinity-guard` no Claude Code para a versão do repositório (feche e abra o Claude Code depois);
- cria a tarefa **Infinity Guard - Orquestrador** no Agendador de Tarefas: liga quando você entra no Windows e confere a cada 15 minutos se continua rodando;
- liga agora e espera o primeiro ciclo terminar, mostrando o `status`.

Pode rodar de novo quando quiser atualizar. Para desligar e apagar a tarefa: `.\scripts\windows\instalar-orquestrador.ps1 -Desinstalar`.

O orquestrador nunca gasta, publica, mexe na loja ou fala com cliente. O que um funcionário recomendar nesse sentido vira pedido de aprovação.

## 2. Números entrando sozinhos

Escolha um dos caminhos (pode usar os dois). Os links e a pasta ficam em `config\orquestrador.local.json`, que não vai para o GitHub.

### Pasta do Google Drive (o mais simples)

1. Instale o [Google Drive para computador](https://www.google.com/drive/download/). A pasta "Meu Drive" aparece no Explorador (normalmente `G:\Meu Drive`).
2. Crie `G:\Meu Drive\Infinity Guard` com as subpastas `nuvemshop`, `meta` e `app`.
3. Salve lá a exportação de vendas da Nuvemshop, o CSV do Gerenciador de Anúncios e o backup do app (pode ser pelo celular, direto no Drive).
4. Em `config\orquestrador.local.json`:
   ```json
   {"fontes": {"pasta_drive": "G:/Meu Drive/Infinity Guard"}}
   ```

### Planilhas do Google

1. Em cada planilha: Compartilhar → "Qualquer pessoa com o link: Leitor" (ou Arquivo → Compartilhar → Publicar na web → CSV).
2. Copie o link e cole na fonte certa:
   ```json
   {"fontes": {"planilhas": {
     "nuvemshop": "https://docs.google.com/spreadsheets/d/.../edit#gid=0",
     "conversas": "https://docs.google.com/spreadsheets/d/.../edit#gid=0",
     "meta": "https://docs.google.com/spreadsheets/d/.../edit#gid=0"}}}
   ```
   - `nuvemshop`: as mesmas colunas da exportação de vendas da Nuvemshop.
   - `conversas`: planilha do atendimento (modelo em `skills/painel-de-vendas/references/modelo-conversas.csv`).
   - `meta`: colunas `conjunto;gasto;compras;receita`.
3. Teste: `python tools\fontes_externas.py` mostra o que baixou ou por que não baixou.

Se a planilha não estiver aberta para leitura, o orquestrador avisa no log e continua com o último arquivo baixado.

### Meta Ads direto pela API (só leitura, opcional)

Com um token de leitura (permissão `ads_read`) do Gerenciador de Negócios:
```powershell
setx META_ACCESS_TOKEN "seu_token"
setx META_AD_ACCOUNT_ID "act_123456789"
```
Depois rode o instalador de novo para a tarefa pegar as variáveis. O token nunca entra no repositório.

### Conectores no Claude

Os conectores Meta, Google Sheets e Google Drive servem às conversas e rotinas na nuvem (o coordenador e as threads do projeto). O orquestrador do PC lê pelos caminhos acima, porque roda fora do Claude.

## 3. Aprovações em segundos

- **Aviso do Windows** quando chega pedido novo (desligue com `"avisar_no_windows": false`).
- **Página** `logs\aprovacoes.html`: cada pedido com o porquê, o link de onde fazer e o comando pronto. Abra com `python core\daemon_orchestrator.py pagina`.
- **Vários de uma vez:** `python core\daemon_orchestrator.py aprovar 2 5 7 feito no celular`.

Aprovar só registra a decisão. A ação (pausar, mudar preço, responder cliente) você faz no link "onde fazer". Gasto com anúncio continua fora da caixa de aprovações enquanto o teto for R$ 0 (veja `docs/mapa-da-autonomia.md`).
