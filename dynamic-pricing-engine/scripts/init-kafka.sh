#!/bin/bash
# Script para inicializar tópicos do Kafka

set -e

KAFKA_BROKER=${KAFKA_BROKER:-"kafka:9092"}
BOOTSTRAP_SERVERS="--bootstrap-server ${KAFKA_BROKER}"

echo "=========================================="
echo "Inicializando Tópicos Kafka"
echo "=========================================="
echo ""

# Aguarda Kafka estar disponível
echo "⏳ Aguardando Kafka estar disponível..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if kafka-broker-api-versions.sh $BOOTSTRAP_SERVERS >/dev/null 2>&1; then
    echo "✓ Kafka disponível"
    break
  fi
  attempt=$((attempt + 1))
  echo "Tentativa $attempt/$max_attempts..."
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ Timeout aguardando Kafka"
  exit 1
fi

echo ""
echo "📝 Criando tópicos..."

# Tópico: raw_prices (Scraper → Rules)
echo "  • raw_prices (10 partições, replication=1)"
kafka-topics.sh $BOOTSTRAP_SERVERS --create \
  --topic raw_prices \
  --partitions 10 \
  --replication-factor 1 \
  --config retention.ms=86400000 \
  --if-not-exists 2>/dev/null || true

# Tópico: recommended_prices (Rules → Audit + API)
echo "  • recommended_prices (10 partições, replication=1)"
kafka-topics.sh $BOOTSTRAP_SERVERS --create \
  --topic recommended_prices \
  --partitions 10 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --if-not-exists 2>/dev/null || true

# Tópico: dead_letter_queue (Error handling)
echo "  • dead_letter_queue (1 partição, replication=1)"
kafka-topics.sh $BOOTSTRAP_SERVERS --create \
  --topic dead_letter_queue \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists 2>/dev/null || true

echo ""
echo "📊 Tópicos criados:"
kafka-topics.sh $BOOTSTRAP_SERVERS --list

echo ""
echo "✅ Inicialização concluída"
