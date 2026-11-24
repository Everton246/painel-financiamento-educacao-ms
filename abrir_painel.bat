@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Painel Financiamento Educacao MS

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale o Python 3.11 ou mais novo em https://www.python.org/downloads/
  echo e marque a opcao "Add python.exe to PATH" na instalacao.
  pause
  exit /b 1
)

python -c "import streamlit, plotly, pandas, pyarrow, openpyxl, fpdf" >nul 2>nul
if errorlevel 1 (
  echo Instalando os pacotes necessarios ^(so na primeira vez^)...
  python -m pip install --user -r requirements.txt
)

if not exist "dados\base\indicadores.parquet" (
  echo A base ainda nao foi montada. Rode primeiro atualizar.bat.
  pause
  exit /b 1
)

echo Abrindo o painel no navegador... ^(para fechar, feche esta janela^)
python -m streamlit run painel\app.py --server.headless false --browser.gatherUsageStats false --server.port 8502
pause
