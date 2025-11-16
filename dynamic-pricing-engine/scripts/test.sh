#!/bin/bash
# Script para testar os endpoints da API

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Testing Dynamic Pricing Engine APIs"
echo "=========================================="
echo ""

# Health Check
echo "1️⃣  Health Check - Pricing API"
curl -s ${BASE_URL}/health | jq .
echo ""

# Get Single Price
echo "2️⃣  Get Recommended Price for SKU001"
curl -s ${BASE_URL}/api/v1/price/SKU001 | jq .
echo ""

# Get Batch Prices
echo "3️⃣  Get Batch Prices"
curl -s -X POST ${BASE_URL}/api/v1/prices/batch \
  -H "Content-Type: application/json" \
  -d '{"skus": ["SKU001", "SKU002", "SKU003"]}' | jq .
echo ""

# Get Metrics
echo "4️⃣  Get Service Metrics"
curl -s ${BASE_URL}/api/v1/metrics | jq .
echo ""

# Scraper Service Health
echo "5️⃣  Scraper Service Health"
curl -s http://localhost:8001/health | jq .
echo ""

# Audit Service Health
echo "6️⃣  Audit Service Health"
curl -s http://localhost:8003/health | jq .
echo ""

# Get Statistics
echo "7️⃣  Get Audit Statistics"
curl -s http://localhost:8003/api/v1/statistics | jq .
echo ""

echo "=========================================="
echo "✅ Tests Completed"
echo "=========================================="
