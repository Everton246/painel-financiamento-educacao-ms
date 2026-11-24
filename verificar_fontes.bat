@echo off
rem Usado pela tarefa agendada mensal: so verifica as fontes (nao baixa nada) e grava docserificacoes\AAAA-MM-DD.md
chcp 65001 >nul
cd /d "%~dp0"
python atualizar.py --verificar
