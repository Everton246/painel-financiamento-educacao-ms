@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Atualizar dados - Painel Financiamento Educacao MS

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale o Python 3.11 ou mais novo em https://www.python.org/downloads/
  pause
  exit /b 1
)

echo Conferindo pacotes...
python -m pip install --user -q -r requirements.txt

echo.
echo Baixando so o que e novo, remontando a base e conferindo. Leva alguns minutos.
echo Para so verificar se as fontes publicaram algo novo, sem baixar: atualizar.bat --verificar
echo.
python atualizar.py %*
echo.
echo Registro detalhado em coleta.log; conferencia em docs\conferencia.md
pause
