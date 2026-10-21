@echo off
rem Dois cliques: atualiza o plugin e deixa o orquestrador da Infinity Guard ligado sozinho.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar-orquestrador.ps1" %*
pause
