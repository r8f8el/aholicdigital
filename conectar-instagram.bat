@echo off
chcp 65001 > nul
title Conectar Instagram - Prospector
echo =======================================================
echo Iniciando conexao com o Instagram...
echo =======================================================
"C:\Users\rafae\AppData\Local\Programs\Python\Python313\python.exe" "scripts\conectar-instagram.py"
echo.
echo Pressione qualquer tecla para fechar esta janela.
pause > nul
