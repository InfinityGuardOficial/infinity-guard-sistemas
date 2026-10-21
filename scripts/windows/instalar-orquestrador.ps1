<#
Infinity Guard: deixa o orquestrador ligado sozinho no Windows e atualiza o plugin.

O que faz (pode rodar quantas vezes quiser, ele só atualiza):
  1. Puxa a versão nova do repositório (git pull).
  2. Atualiza o plugin infinity-guard no Claude Code.
  3. Cria a tarefa "Infinity Guard - Orquestrador" no Agendador de Tarefas: liga quando você entra no
     Windows e confere a cada 15 minutos se continua rodando (se caiu, liga de novo).
  4. Liga agora e espera o primeiro ciclo terminar.

Uso (dois cliques em instalar-orquestrador.cmd, ou no PowerShell):
  .\scripts\windows\instalar-orquestrador.ps1
  .\scripts\windows\instalar-orquestrador.ps1 -Desinstalar      # desliga e apaga a tarefa
O orquestrador nunca gasta, publica ou fala com cliente: isso vira pedido em logs\aprovacoes.html.
#>
param(
    [string]$Pasta = "",
    [string]$NomeTarefa = "Infinity Guard - Orquestrador",
    [switch]$Desinstalar,
    [switch]$SemPlugin,
    [switch]$SemAtualizarRepo,
    [switch]$ModoServico,          # roda mesmo sem ninguém logado (usado no teste automático)
    [int]$EsperarSegundos = 180
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Passo($texto) { Write-Host "`n== $texto" -ForegroundColor Cyan }
function Ok($texto) { Write-Host "   ok: $texto" -ForegroundColor Green }
function Aviso($texto) { Write-Host "   atenção: $texto" -ForegroundColor Yellow }

if (-not $Pasta) { $Pasta = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path }
$Daemon = Join-Path $Pasta "core\daemon_orchestrator.py"
if (-not (Test-Path $Daemon)) { throw "Não achei $Daemon. Rode este script de dentro da pasta do repositório infinity-guard-sistemas." }

# Python: pythonw.exe roda sem abrir janela preta.
function Achar-Python {
    $candidatos = @()
    foreach ($nome in @("python", "python3")) {
        $c = Get-Command $nome -ErrorAction SilentlyContinue
        if ($c -and $c.Source -notlike "*WindowsApps*") { $candidatos += $c.Source }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { $candidatos += (& $py.Source -3 -c "import sys; print(sys.executable)") }
    foreach ($exe in $candidatos) {
        if (-not $exe) { continue }
        $versao = & $exe -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($versao -and [version]$versao -ge [version]"3.9") {
            $w = Join-Path (Split-Path $exe) "pythonw.exe"
            return @{ python = $exe; pythonw = $(if (Test-Path $w) { $w } else { $exe }); versao = $versao }
        }
    }
    throw "Não achei o Python 3.9 ou mais novo. Instale em https://www.python.org/downloads/ (marque 'Add python.exe to PATH') e rode de novo."
}

if ($Desinstalar) {
    Passo "Desligando o orquestrador"
    $p = Achar-Python
    & $p.python $Daemon parar | Out-Host
    if (Get-ScheduledTask -TaskName $NomeTarefa -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $NomeTarefa -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $NomeTarefa -Confirm:$false
        Ok "tarefa '$NomeTarefa' apagada"
    } else { Ok "não havia tarefa '$NomeTarefa'" }
    exit 0
}

Passo "Python"
$p = Achar-Python
Ok "Python $($p.versao) em $($p.python)"

if (-not $SemAtualizarRepo) {
    Passo "Repositório"
    if ((Get-Command git -ErrorAction SilentlyContinue) -and (Test-Path (Join-Path $Pasta ".git"))) {
        & git -C $Pasta pull --ff-only
        if ($LASTEXITCODE -eq 0) { Ok "atualizado" } else { Aviso "git pull não rodou (mudança local?). Sigo com a versão que está aí." }
    } else { Aviso "sem git ou sem .git: sigo com a versão que está na pasta" }
}

if (-not $SemPlugin) {
    Passo "Plugin infinity-guard no Claude Code"
    if (Get-Command claude -ErrorAction SilentlyContinue) {
        & claude plugin marketplace update infinity-guard-sistemas
        if ($LASTEXITCODE -ne 0) {
            & claude plugin marketplace add InfinityGuardOficial/infinity-guard-sistemas
        }
        & claude plugin update infinity-guard@infinity-guard-sistemas
        if ($LASTEXITCODE -ne 0) { & claude plugin install infinity-guard@infinity-guard-sistemas }
        $versao = (Get-Content (Join-Path $Pasta ".claude-plugin\plugin.json") -Raw -Encoding UTF8 | ConvertFrom-Json).version
        if ($LASTEXITCODE -eq 0) { Ok "plugin na versão do repositório ($versao). Feche e abra o Claude Code para valer." }
        else { Aviso "o plugin não atualizou. No Claude Code, rode: /plugin e atualize 'infinity-guard'." }
    } else { Aviso "comando 'claude' não encontrado: os funcionários não vão rodar até instalar o Claude Code (https://claude.ai/download)." }
}

Passo "Tarefa no Agendador do Windows"
$acao = New-ScheduledTaskAction -Execute $p.pythonw -Argument "`"$Daemon`" rodar" -WorkingDirectory $Pasta
$gatilhos = @(
    (New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15))
)
if (-not $ModoServico) { $gatilhos = @((New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME")) + $gatilhos }
$ajustes = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$tipo = $(if ($ModoServico) { "S4U" } else { "Interactive" })
$quem = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType $tipo -RunLevel Limited
Register-ScheduledTask -TaskName $NomeTarefa -Action $acao -Trigger $gatilhos -Settings $ajustes -Principal $quem `
    -Description "Orquestrador da Infinity Guard (core\daemon_orchestrator.py). Nunca gasta nem publica: pedidos em logs\aprovacoes.html." `
    -Force | Out-Null
Ok "tarefa '$NomeTarefa' criada (liga ao entrar no Windows e confere a cada 15 min)"

Passo "Ligando agora"
$pid_ = Join-Path $Pasta "logs\daemon.pid"
if (Test-Path $pid_) {
    & $p.python $Daemon parar | Out-Null   # um daemon antigo (aberto na mão) encerra para o da tarefa assumir
    $fimParar = (Get-Date).AddSeconds(60)
    while ((Test-Path $pid_) -and (Get-Date) -lt $fimParar) { Start-Sleep -Seconds 2 }
    Remove-Item $pid_ -ErrorAction SilentlyContinue
}
$hb = Join-Path $Pasta "logs\daemon.heartbeat"
$antes = $(if (Test-Path $hb) { (Get-Item $hb).LastWriteTime } else { [datetime]::MinValue })
Start-ScheduledTask -TaskName $NomeTarefa
$fim = (Get-Date).AddSeconds($EsperarSegundos)
while ((Get-Date) -lt $fim) {
    if ((Test-Path $hb) -and (Get-Item $hb).LastWriteTime -gt $antes) { break }
    Start-Sleep -Seconds 3
}
if ((Test-Path $hb) -and (Get-Item $hb).LastWriteTime -gt $antes) {
    Ok "primeiro ciclo feito"
    & $p.python $Daemon status | Out-Host
} else {
    $info = Get-ScheduledTaskInfo -TaskName $NomeTarefa
    Write-Host "   O primeiro ciclo não terminou em $EsperarSegundos s (último resultado da tarefa: $($info.LastTaskResult)). Veja logs\errors.log." -ForegroundColor Red
    exit 1
}

Write-Host "`nPronto. O orquestrador fica ligado sozinho." -ForegroundColor Green
Write-Host "  Ver como está:   python core\daemon_orchestrator.py status"
Write-Host "  Aprovações:      python core\daemon_orchestrator.py pagina   (ou abra logs\aprovacoes.html)"
Write-Host "  Desligar tudo:   .\scripts\windows\instalar-orquestrador.ps1 -Desinstalar"
exit 0
