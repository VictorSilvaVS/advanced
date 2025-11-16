#!/bin/bash
# Script para iniciar o projeto com Docker Compose

set -e

echo "=========================================="
echo "Dynamic Pricing Engine - Startup Script"
echo "=========================================="
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale Docker e tente novamente."
    exit 1
fi

# Verifica se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale Docker Compose e tente novamente."
    exit 1
fi

echo "✓ Docker e Docker Compose encontrados"
echo ""

# Para containers existentes (opcional)
if [ "$1" = "clean" ]; then
    echo "🧹 Limpando containers existentes..."
    docker-compose down -v
    echo "✓ Containers removidos"
    echo ""
fi

# Build das imagens
echo "🏗️  Construindo imagens Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando serviços..."
docker-compose up -d

echo ""
echo "⏳ Aguardando serviços ficarem saudáveis..."
sleep 10

# Verifica saúde dos serviços
echo ""
echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Dynamic Pricing Engine iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📍 Endpoints disponíveis:"
echo "  - Scraper Service:    http://localhost:8001"
echo "  - Pricing API:        http://localhost:8000"
echo "  - Audit API:          http://localhost:8003"
echo ""
echo "🗄️  Banco de Dados:"
echo "  - PostgreSQL:         localhost:5432"
echo "  - Redis:              localhost:6379"
echo "  - Kafka:              localhost:9092"
echo ""
echo "📚 Próximos passos:"
echo "  1. Abra http://localhost:8000/docs para documentação Swagger da Pricing API"
echo "  2. Abra http://localhost:8001/docs para documentação da Scraper Service"
echo "  3. Abra http://localhost:8003/docs para documentação da Audit API"
echo ""
echo "🛑 Para parar os serviços:"
echo "  docker-compose down"
echo ""
