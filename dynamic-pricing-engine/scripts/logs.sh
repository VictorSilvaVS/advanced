#!/bin/bash
# Script para visualizar logs dos containers

echo "=========================================="
echo "Dynamic Pricing Engine - Logs"
echo "=========================================="
echo ""

if [ "$1" = "" ]; then
    echo "Mostrando logs de todos os serviços:"
    docker-compose logs -f
elif [ "$1" = "scraper" ]; then
    echo "Logs - Scraper Service"
    docker-compose logs -f scraper_service
elif [ "$1" = "rules" ]; then
    echo "Logs - Rules Engine Worker"
    docker-compose logs -f rules_engine_worker
elif [ "$1" = "pricing" ]; then
    echo "Logs - Pricing API"
    docker-compose logs -f pricing_api
elif [ "$1" = "audit" ]; then
    echo "Logs - Audit Services"
    docker-compose logs -f audit_service_worker audit_api
elif [ "$1" = "kafka" ]; then
    echo "Logs - Kafka"
    docker-compose logs -f kafka zookeeper
else
    echo "Uso: $0 [scraper|rules|pricing|audit|kafka]"
    echo ""
    echo "Exemplos:"
    echo "  $0                # Todos os logs"
    echo "  $0 scraper       # Logs do Scraper"
    echo "  $0 rules         # Logs do Rules Engine"
    echo "  $0 pricing       # Logs da Pricing API"
    echo "  $0 audit         # Logs dos Audit Services"
    echo "  $0 kafka         # Logs do Kafka"
fi
