@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Publicar - Painel Financiamento Educacao MS

where git >nul 2>nul
if errorlevel 1 (
  echo Git nao encontrado. Instale em https://git-scm.com/download/win
  pause
  exit /b 1
)

git remote get-url origin >nul 2>nul
if errorlevel 1 (
  echo Ainda nao ha repositorio no GitHub ligado a esta pasta.
  echo Veja o passo a passo em LEIAME.md, secao "Como publicar".
  pause
  exit /b 1
)

echo Conferindo a base antes de publicar...
python tratamento\conferir.py
if errorlevel 1 (
  echo A conferencia encontrou divergencias ^(ver docs\conferencia.md^). Publicacao cancelada.
  pause
  exit /b 1
)

echo Enviando a base e o codigo para o GitHub...
git add -A
git commit -m "Atualizacao da base %date%"
git pull --rebase
git push
echo.
pause
