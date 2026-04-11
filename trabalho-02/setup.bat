@echo off
:: =============================================================================
:: setup.bat — Trabalho 02 FAED/PPGIA/PUC-PR
:: Configura o ambiente, gera o banco e executa os experimentos.
:: Requer: Python 3.10+ no PATH
:: =============================================================================

setlocal EnableDelayedExpansion
set PYTHONIOENCODING=utf-8

echo.
echo  ============================================================
echo   Trabalho 02 - FAED / PPGIA / PUC-PR
echo   Analise de Algoritmos de Busca em Grafos
echo  ============================================================
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ e adicione ao PATH.
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v encontrado

:: Cria e ativa venv se nao existir
if not exist ".venv\" (
    echo [INFO] Criando ambiente virtual...
    python -m venv .venv
)

echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

:: Instala dependencias
echo [INFO] Instalando dependencias...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
echo [OK] Dependencias instaladas.

:: Gera banco SQLite
echo [INFO] Gerando banco de dados sintetico...
python -m db.seed
if errorlevel 1 (
    echo [ERRO] Falha ao gerar banco de dados.
    exit /b 1
)

:: Executa experimentos
echo [INFO] Executando experimentos...
python -m src.runner
if errorlevel 1 (
    echo [ERRO] Falha na execucao dos experimentos.
    exit /b 1
)

echo.
echo  ============================================================
echo   Concluido com sucesso!
echo   Resultados: results\metrics\sumario.csv
echo   Grafos:     results\graphs\*.html
echo  ============================================================
echo.

endlocal
