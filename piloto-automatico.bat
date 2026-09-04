@echo off
chcp 65001 > nul
title AHOLIC DIGITAL — Piloto Automatico 100% Autonomo
cls

echo ===================================================================
echo               AHOLIC DIGITAL — PILOTO AUTOMÁTICO
echo   Mineracao Maps + Fotos Reais + Sites Anti-Slop + Deploy Vercel
echo ===================================================================
echo.

:: Detectar executavel Python do sistema
set "PYTHON_EXE="
if exist "C:\Users\rafae\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=C:\Users\rafae\AppData\Local\Programs\Python\Python313\python.exe"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_EXE=py"
    ) else (
        set "PYTHON_EXE=python"
    )
)

echo Escolha o modo de operacao:
echo  [1] Minerar novos leads + Gerar sites + Subir na Vercel (1 Clique)
echo  [2] Gerar sites para todos os leads pendentes no banco
echo  [3] Modo Madrugada / Noturno (Executa fila continua de nichos e cidades)
echo  [0] Sair
echo.
set /p "MODO_ESCOLHIDO=Opcao desejada (1, 2, 3 ou 0) [padrao: 1]: "
if "%MODO_ESCOLHIDO%"=="" set "MODO_ESCOLHIDO=1"

if "%MODO_ESCOLHIDO%"=="0" exit /b

if "%MODO_ESCOLHIDO%"=="2" (
    echo.
    echo ===================================================================
    echo Gerando sites para todos os leads pendentes no prospector.db...
    echo ===================================================================
    "%PYTHON_EXE%" "scripts\piloto_automatico.py" --modo 2
    goto fim
)

if "%MODO_ESCOLHIDO%"=="3" (
    echo.
    echo ===================================================================
    echo INICIANDO MODO NOTURNO... O PC vai minerar e gerar sites em fila!
    echo ===================================================================
    "%PYTHON_EXE%" "scripts\piloto_automatico.py" --modo 3
    goto fim
)

:: Modo 1: Minerar + Gerar
echo.
set "NICHO=estetica"
set /p "INPUT_NICHO=Digite o Nicho [padrao: estetica]: "
if not "%INPUT_NICHO%"=="" set "NICHO=%INPUT_NICHO%"

set "CIDADE=Goiania"
set /p "INPUT_CIDADE=Digite a Cidade [padrao: Goiania]: "
if not "%INPUT_CIDADE%"=="" set "CIDADE=%INPUT_CIDADE%"

set "LIMITE=5"
set /p "INPUT_LIMITE=Quantos leads deseja minerar e gerar? [padrao: 5]: "
if not "%INPUT_LIMITE%"=="" set "LIMITE=%INPUT_LIMITE%"

echo.
echo ===================================================================
echo Iniciando Esteira Completa: %NICHO% em %CIDADE% (Meta: %LIMITE% sites)
echo ===================================================================
echo.

"%PYTHON_EXE%" "scripts\piloto_automatico.py" --modo 1 --nicho "%NICHO%" --cidade "%CIDADE%" --limite %LIMITE%

:fim
echo.
echo ===================================================================
echo  EXECUCAO CONCLUIDA!
echo  Os sites estao prontos e o dashboard foi sincronizado.
echo ===================================================================
echo.
pause
