@echo off
REM Script para iniciar o projeto com Docker Compose no Windows

setlocal enabledelayedexpansion

echo ==========================================
echo Dynamic Pricing Engine - Startup Script
echo ==========================================
echo.

REM Verifica se Docker está instalado
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker nao esta instalado. Instale Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo OK - Docker encontrado
echo.

REM Limpar containers existentes se solicitado
if "%1"=="clean" (
    echo Limpando containers existentes...
    docker-compose down -v
    echo OK - Containers removidos
    echo.
)

REM Build das imagens
echo Construindo imagens Docker...
docker-compose build

echo.
echo Iniciando servicos...
docker-compose up -d

echo.
echo Aguardando servicos ficarem saudaveis...
timeout /t 10 /nobreak

REM Verifica saúde dos serviços
echo.
echo Status dos servicos:
docker-compose ps

echo.
echo ==========================================
echo OK - Dynamic Pricing Engine iniciado!
echo ==========================================
echo.
echo Endpoints disponiveis:
echo   - Scraper Service:    http://localhost:8001
echo   - Pricing API:        http://localhost:8000
echo   - Audit API:          http://localhost:8003
echo.
echo Banco de Dados:
echo   - PostgreSQL:         localhost:5432
echo   - Redis:              localhost:6379
echo   - Kafka:              localhost:9092
echo.
echo Proximos passos:
echo   1. Abra http://localhost:8000/docs para Swagger da Pricing API
echo   2. Abra http://localhost:8001/docs para Swagger da Scraper Service
echo   3. Abra http://localhost:8003/docs para Swagger da Audit API
echo.
echo Para parar os servicos:
echo   docker-compose down
echo.

pause
