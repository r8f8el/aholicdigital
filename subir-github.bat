@echo off
cd /d "%~dp0"
echo ======================================================
echo    Sincronizando Aholic Sites com o GitHub...
echo ======================================================
echo.
git add .
git commit -m "feat: atualizacoes e novos sites"
echo.
echo Enviando para o repositorio remoto origin/main...
git push origin main
echo.
if %errorlevel%==0 (
    echo [SUCESSO] Atualizacoes enviadas para o GitHub!
) else (
    echo [AVISO] Houve um erro ao enviar. Verifique seu login/token do GitHub.
)
echo.
pause
