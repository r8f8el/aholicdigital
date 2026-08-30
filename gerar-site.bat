@echo off
chcp 65001 > nul
title AHOLIC DIGITAL - Gerador Automatico de Sites Anti-Slop
cls

echo ===================================================================
echo             AHOLIC DIGITAL — GERADOR DE SITES ANTI-SLOP
echo   Design Editorial + Fotos Reais + Transicoes + Editor Inline
echo ===================================================================
echo.

:: Detectar executavel Python
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

:: Exibir lista de leads disponiveis
"%PYTHON_EXE%" "scripts\gerar-site-lead.py" --list

set /p "LEAD_SLUG=Digite o SLUG do lead acima para gerar (ex: clinica-anielly-vilela): "
if "%LEAD_SLUG%"=="" (
    echo Nenhum slug digitado. Encerrando.
    pause
    exit /b
)

echo.
echo Presets disponiveis:
echo  1. auto (Detecta automaticamente pelo nicho do lead)
echo  2. quiet-luxury (Estetica, Dermatologia, Cirurgia, Luxo)
echo  3. swiss-precision (Odontologia, Implantes, Alta Tecnologia)
echo.
set "PRESET=auto"
set /p "INPUT_PRESET=Escolha o Preset [padrao: auto]: "
if not "%INPUT_PRESET%"=="" set "PRESET=%INPUT_PRESET%"

echo.
echo ===================================================================
echo Compilando site de alta conversao para '%LEAD_SLUG%'...
echo ===================================================================
echo.

"%PYTHON_EXE%" "scripts\gerar-site-lead.py" --slug "%LEAD_SLUG%" --preset "%PRESET%"

echo.
echo Deseja abrir a pagina gerada no navegador?
echo 1. Abrir Versao Final (index.html)
echo 2. Abrir Modo Edicao Visual ([slug]-editor.html)
echo 3. Nao abrir agora
set /p "OPEN_CHOICE=Escolha (1, 2 ou 3): "

if "%OPEN_CHOICE%"=="1" (
    start "" "sites\%LEAD_SLUG%\index.html"
)
if "%OPEN_CHOICE%"=="2" (
    start "" "sites\%LEAD_SLUG%\%LEAD_SLUG%-editor.html"
)

echo.
echo ===================================================================
echo Concluido! Status atualizado para 'redesenhado' no CRM.
echo ===================================================================
echo.
pause
