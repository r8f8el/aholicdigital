@echo off
chcp 65001 > nul
title AHOLIC DIGITAL - Minerador Unificado de Leads
cls

echo ===================================================================
echo               AHOLIC DIGITAL — MINERADOR DE LEADS
echo   Google Maps (Sem Site) + Extracao de Instagram + Cadastro CRM
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

:: Perguntas com valores padrao
set "NICHO=estetica"
set /p "INPUT_NICHO=Digite o Nicho [padrao: estetica]: "
if not "%INPUT_NICHO%"=="" set "NICHO=%INPUT_NICHO%"

set "CIDADE=Caldas Novas"
set /p "INPUT_CIDADE=Digite a Cidade [padrao: Caldas Novas]: "
if not "%INPUT_CIDADE%"=="" set "CIDADE=%INPUT_CIDADE%"

set "LIMITE=5"
set /p "INPUT_LIMITE=Limite de leads a minerar [padrao: 5]: "
if not "%INPUT_LIMITE%"=="" set "LIMITE=%INPUT_LIMITE%"

set "VISIBLE_FLAG="
set /p "INPUT_VIS=Deseja ver a janela do navegador aberta? (s/N): "
if /i "%INPUT_VIS%"=="s" set "VISIBLE_FLAG=--visible"

echo.
echo ===================================================================
echo Iniciando mineracao para '%NICHO%' em '%CIDADE%' (Meta: %LIMITE% leads)...
echo ===================================================================
echo.

"%PYTHON_EXE%" "scripts\minerar-leads.py" --nicho "%NICHO%" --cidade "%CIDADE%" --limite %LIMITE% %VISIBLE_FLAG%

echo.
echo ===================================================================
echo Processo finalizado! Os leads minerados ja estao no prospector.db.
echo Abra o dashboard local executando: iniciar-dashboard.bat
echo ===================================================================
echo.
pause
