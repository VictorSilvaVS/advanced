# 🎯 Dynamic Pricing Engine - Orquestrador de Preços Dinâmicos

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Apache-Kafka-red.svg)](https://kafka.apache.org/)

Um sistema de **precificação dinâmica em tempo real** altamente escalável e resiliente, implementado como **arquitetura de microsserviços em Python**. Demonstra aplicação prática de arquitetura avançada, processamento assíncrono, e orquestração distribuída.

---

## 🚀 Quick Start

**Inicie com um único comando:**

```bash
# Linux/Mac
chmod +x scripts/start.sh
./scripts/start.sh

# Windows
scripts\start.bat

# Ou com Docker Compose direto
docker-compose up -d
```

**Acesse os endpoints:**
- 🔗 **Pricing API** (Swagger): http://localhost:8000/docs
- 🔗 **Scraper Service** (Swagger): http://localhost:8001/docs  
- 🔗 **Audit API** (Swagger): http://localhost:8003/docs

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura](#-arquitetura)
3. [Componentes](#-componentes)
4. [API Endpoints](#-endpoints-da-api)
5. [Exemplos de Uso](#-exemplos-de-uso)
6. [Monitoramento](#-monitoramento)
7. [Performance](#-performance)

---

## 🎯 Visão Geral

### O Problema Resolvido

Empresas de e-commerce, companhias aéreas e marketplaces enfrentam desafios de precificação:
- 📊 Necessidade de ajustar preços dinamicamente em tempo real
- 🏪 Competição acirrada com concorrentes
- 📦 Inventário com alto custo de manutenção
- 📋 Requisitos de compliance e auditoria

### A Solução

Um **engine de preços inteligente** que:
- ✅ Coleta preços da concorrência em paralelo (1000s requisições)
- ✅ Aplica regras de negócio complexas (Pandas + Numba)
- ✅ Recomenda preços otimizados (< 10ms latência)
- ✅ Registra auditoria completa (PostgreSQL + SLA)

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│        DYNAMIC PRICING ENGINE - MICROSSERVIÇOS           │
└──────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│   SCRAPER SERVICE       │     Coleta preços da concorrência
│   (FastAPI + aiohttp)   │     • Async I/O paralelo (asyncio)
│   Port: 8001            │     • 1000s requisições simultâneas
└──────────────────────────┘     • Simula scraping real
         │
         │ Publica: raw_prices
         ↓
┌──────────────────────────────────────────────┐
│     APACHE KAFKA (Message Broker)            │
│     Port: 9092                               │
│                                              │
│  Topics:                                     │
│  • raw_prices          (Scraper → Rules)   │
│  • recommended_prices  (Rules → Cache)     │
│  • dead_letter_queue   (Error handling)    │
└──────────────────────────────────────────────┘
         ↑                        │
         │                        │ Consome: raw_prices
         │                        ↓
         │         ┌──────────────────────────────┐
         │         │   RULES ENGINE WORKER        │
         │         │   (Async + Pandas + Numba)   │
         │         │                              │
         │         │  • Análise competitiva       │
         │         │  • Elasticidade de demanda   │
         │         │  • Otimização de margin      │
         │         │  • Ajuste por inventário     │
         │         │  • Dead Letter Queue         │
         │         └──────────────────────────────┘
         │                        │
         │ Publica: recommended   │
         │          _prices       ↓
         │                ┌────────────────────┐
         │                │  PRICING API       │
         │                │ (FastAPI + Redis)  │
         │                │ Port: 8000         │
         │                │                    │
         │                │ • Cache Redis      │
         │                │ • < 10ms latência  │
         │                │ • Fallback auto    │
         │                └────────────────────┘
         │                        │
         │ Atualiza Cache         │ GET /api/v1/price/{sku}
         │                        ↓
         │                   (Clientes)
         │
         │ Publica: recommended_prices
         ↓
┌──────────────────────────────┐
│   AUDIT SERVICE WORKER       │
│   (Async + PostgreSQL)       │
│                              │
│ • Persiste decisões         │
│ • Registra falhas (DLQ)     │
│ • Compliance & auditoria    │
└──────────────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│   AUDIT API (FastAPI)        │
│   Port: 8003                 │
│                              │
│ GET /api/v1/decisions/sku    │
│ GET /api/v1/failures         │
│ GET /api/v1/statistics       │
└──────────────────────────────┘

External Services:
├─ Redis (Cache) - Port: 6379
├─ PostgreSQL (Audit DB) - Port: 5432
├─ Zookeeper (Kafka) - Port: 2181
└─ Kafka Broker - Port: 9092
```

---

## ⚙️ Componentes

### 1. Scraper Service 🕷️

**Arquivo:** `src/scraper_service/`

**Stack:** FastAPI + aiohttp + asyncio

**Responsabilidades:**
- Coleta preços de múltiplos concorrentes
- Implementa I/O assíncrono (asyncio.gather)
- Trata timeouts e retries automaticamente
- Publica dados brutos no Kafka

**Endpoints:**
```bash
GET  /health
POST /api/v1/scrape/single      # Um SKU
POST /api/v1/scrape/batch       # Múltiplos SKUs
GET  /api/v1/competitors        # Lista concorrentes
```

**Exemplo:**
```python
# Simula scraping paralelo de 1000 requisições
prices = await scraper.scrape_prices_batch(
    skus=["SKU001", "SKU002", "SKU003"],
    competitor_ids=["amazon", "ebay", "mercado_livre", "shopee"]
)
```

---

### 2. Rules Engine Worker ⚙️

**Arquivo:** `src/rules_engine/`

**Stack:** asyncio + Pandas + Numba + aiokafka

**Responsabilidades:**
- Processa regras complexas de negócio
- Análise competitiva e elasticidade
- Otimização de margem e inventário
- Implementa Dead Letter Queue para erros

**Regras Aplicadas:**

```python
# 1. Preço mínimo garantido
min_price = cost * (1 + 0.10)

# 2. Análise competitiva
competitive_price = median(competitor_prices) * 0.98

# 3. Elasticidade (demanda alta = preço alto)
# Otimizada com Numba JIT
if demand > 0.5:
    price *= 1.0 + (demand - 0.5) * factor

# 4. Ajuste por inventário (excesso = desconto)
if inventory > 5000:
    price *= 0.90  # -10%

# 5. Enforce margens (10-50%)
price = clamp(price, min_price, max_price)
```

**Dead Letter Queue:**
- Mensagens com erro são enviadas para `dead_letter_queue`
- Permite auditoria e retry manual
- Registrado em PostgreSQL

---

### 3. Pricing API 💰

**Arquivo:** `src/pricing_api/`

**Stack:** FastAPI + Redis + asyncio

**Responsabilidades:**
- API de baixa latência para consulta de preços
- Cache distribuído com Redis
- Fallback automático
- Circuit breaker pattern

**Endpoints:**
```bash
GET  /health
GET  /api/v1/price/{sku}              # Preço recomendado
POST /api/v1/prices/batch             # Batch de preços
POST /api/v1/price/{sku}/update       # Update cache
GET  /api/v1/metrics                  # Métricas cache
```

**Estratégia de Retrieval:**
```
1. Cache Redis           → ~1ms      ✓ Hit
                         → N/A       ✗ Miss
2. PostgreSQL Query      → ~100ms
3. Fallback Default      → ~0ms      (garantido)
```

---

### 4. Audit Service 📊

**Arquivo:** `src/audit_service/`

**Stack:** SQLAlchemy + PostgreSQL + aiokafka

**Responsabilidades:**
- Persiste todas as decisões de preço
- Registra falhas e erros (DLQ)
- Fornece analytics e reportes
- Atende requisitos de compliance

**Tabelas:**
```sql
pricing_decisions
├─ id, sku, current_price, recommended_price
├─ margin_pct, confidence, reason
├─ competitor_prices (JSON)
└─ created_at, applied_at (auditoria temporal)

pricing_failures
├─ id, error_message, original_message
├─ processing_service, sku
└─ created_at (rastreamento de problemas)
```

**Endpoints:**
```bash
GET /health
GET /api/v1/decisions/sku/{sku}       # Histórico completo
GET /api/v1/failures                  # Falhas recentes
GET /api/v1/statistics                # KPIs gerais
```

---

## 📡 Endpoints da API

### Pricing API - http://localhost:8000

#### GET /health
```bash
curl http://localhost:8000/health
```
**Response:** `{"status":"ok", "cache_healthy":true}`

---

#### GET /api/v1/price/{sku}
Obtém preço recomendado com cache automático

```bash
curl http://localhost:8000/api/v1/price/SKU001
```

**Response:**
```json
{
  "sku": "SKU001",
  "current_price": 100.00,
  "recommended_price": 98.50,
  "margin_pct": 0.325,
  "confidence": 0.85,
  "reason": "DESCONTO: Inventário alto (5000 unidades)",
  "source": "cache",
  "retrieved_at": "2025-11-15T10:30:45.123456"
}
```

---

#### POST /api/v1/prices/batch
Obtém múltiplos preços em paralelo

```bash
curl -X POST http://localhost:8000/api/v1/prices/batch \
  -H "Content-Type: application/json" \
  -d '{
    "skus": ["SKU001", "SKU002", "SKU003"]
  }'
```

**Response:**
```json
{
  "prices": {
    "SKU001": {...},
    "SKU002": {...},
    "SKU003": {...}
  },
  "total_requested": 3,
  "total_found": 3
}
```

---

#### GET /api/v1/metrics
Métricas de cache e performance

```bash
curl http://localhost:8000/api/v1/metrics
```

**Response:**
```json
{
  "cache_metrics": {
    "cache_hits": 1250,
    "cache_misses": 145,
    "fallback_uses": 5
  }
}
```

---

### Audit API - http://localhost:8003

#### GET /api/v1/decisions/sku/{sku}
Histórico completo de decisões

```bash
curl http://localhost:8003/api/v1/decisions/sku/SKU001?limit=10
```

---

#### GET /api/v1/statistics
Estatísticas gerais de KPIs

```bash
curl http://localhost:8003/api/v1/statistics
```

**Response:**
```json
{
  "statistics": {
    "total_decisions": 15420,
    "total_failures": 23,
    "avg_confidence": 0.82,
    "avg_margin": 0.28
  }
}
```

---

## 💡 Exemplos de Uso

### Python - Async

```python
import asyncio
import aiohttp

async def get_dynamic_prices(skus: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get(f"http://localhost:8000/api/v1/price/{sku}")
            for sku in skus
        ]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

# Uso
prices = asyncio.run(get_dynamic_prices(["SKU001", "SKU002"]))
for price in prices:
    print(f"SKU: {price['sku']}, Recomendado: R${price['recommended_price']}")
```

---

### Shell Script - Batch

```bash
#!/bin/bash

SKUS=("SKU001" "SKU002" "SKU003")

for sku in "${SKUS[@]}"; do
  price=$(curl -s http://localhost:8000/api/v1/price/$sku | jq '.recommended_price')
  echo "$sku: R$$price"
done
```

---

### Docker - Query PostgreSQL

```bash
# Acessar PostgreSQL
docker-compose exec postgres psql -U pricing_user -d pricing_db

# Query histórico de um SKU
SELECT * FROM pricing_decisions 
WHERE sku='SKU001' 
ORDER BY created_at DESC 
LIMIT 10;

# Estatísticas
SELECT 
  COUNT(*) as total,
  AVG(margin_pct) as avg_margin,
  AVG(confidence) as avg_confidence
FROM pricing_decisions;
```

---

## 🔍 Monitoramento

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f pricing_api
docker-compose logs -f rules_engine_worker

# Apenas erros
docker-compose logs -f | grep ERROR
```

---

### Redis CLI

```bash
# Acessar Redis
docker-compose exec redis redis-cli

# Ver preços em cache
redis> KEYS price:*

# Ver preço específico
redis> GET price:SKU001

# Limpar cache
redis> FLUSHDB
```

---

### Kafka Topics

```bash
# Listar topics
docker-compose exec kafka kafka-topics \
  --bootstrap-server kafka:9092 \
  --list

# Consumir messages
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic recommended_prices \
  --from-beginning
```

---

## 📈 Performance

### Latência Alvo

| Componente | Latência | Método |
|-----------|----------|--------|
| **Pricing API (cache)** | < 1ms | Redis |
| **Pricing API (miss)** | < 10ms | PostgreSQL + Redis |
| **Scraper (100 SKUs)** | ~500ms | Async I/O |
| **Rules Engine (1000 SKUs)** | ~50ms | Pandas + Numba |

---

### Escalabilidade

```yaml
Kafka Partitioning:
  raw_prices: 10 partitions          (10 workers paralelos)
  recommended_prices: 10 partitions  (10 instances API)
  dead_letter_queue: 1 partition     (centralizado)

Horizontal Scaling:
  • Scraper: +1 instância/máquina
  • Rules Engine: +1 worker/máquina
  • Pricing API: +1 instância/máquina
  • Audit Service: +1 worker/máquina
```

---

## 🛑 Parar Serviços

```bash
# Parar sem remover dados
docker-compose stop

# Parar e remover containers
docker-compose down

# Limpeza completa (remove volumes)
docker-compose down -v
```

---

## 📦 Estrutura do Projeto

```
dynamic-pricing-engine/
├── src/
│   ├── scraper_service/
│   │   ├── scraper.py          (Web scraper async)
│   │   └── main.py             (FastAPI app)
│   │
│   ├── rules_engine/
│   │   ├── engine.py           (Regras + Numba)
│   │   └── worker.py           (Kafka consumer)
│   │
│   ├── pricing_api/
│   │   ├── cache.py            (Redis client)
│   │   ├── service.py          (Service layer)
│   │   └── main.py             (FastAPI app)
│   │
│   ├── audit_service/
│   │   ├── models.py           (SQLAlchemy ORM)
│   │   ├── worker.py           (Kafka consumer)
│   │   └── main.py             (FastAPI app)
│   │
│   └── common.py               (Utilitários compartilhados)
│
├── config/
│   └── settings.py             (Configurações centralizadas)
│
├── scripts/
│   ├── start.sh                (Iniciar Linux/Mac)
│   ├── start.bat               (Iniciar Windows)
│   ├── test.sh                 (Testar endpoints)
│   └── logs.sh                 (Visualizar logs)
│
├── docker-compose.yml          (Orquestração)
├── Dockerfile.*                (5 Dockerfiles)
├── requirements.txt            (Dependências)
├── .env                        (Variáveis ambiente)
└── README.md                   (Documentação)
```

---

## 🎓 Conceitos Demonstrados

✅ **Arquitetura de Microsserviços**
- Decomposição por domínio
- Comunicação assíncrona
- Padrões de integração (Kafka)

✅ **Python Avançado**
- asyncio para concorrência
- Type hints e Pydantic
- SQLAlchemy ORM
- Numba JIT compilation

✅ **Data Engineering**
- Pandas para processamento em lote
- Análise de dados
- Agregações complexas

✅ **DevOps & Infrastructure**
- Docker e Docker Compose
- Orquestração de containers
- Persistência de volumes

✅ **System Design**
- Sistemas distribuídos
- Caching strategies
- Dead Letter Queues
- Circuit breaker pattern

✅ **Performance**
- API de baixa latência
- Cache distribuído
- Processamento paralelo
- Índices de banco de dados

---

## 📚 Stack Tecnológico

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **API** | FastAPI | 0.104.1 |
| **Async** | asyncio, aiohttp | 3.9.1 |
| **Data** | Pandas, NumPy, Numba | 2.1.3, 1.26.2, 0.58.1 |
| **Database** | PostgreSQL, SQLAlchemy | 16, 2.0.23 |
| **Cache** | Redis | 7 |
| **Message Queue** | Apache Kafka | 7.5.0 |
| **Containerization** | Docker, Docker Compose | Latest |

---

## 📞 Suporte

Para dúvidas ou issues:
1. Verifique os logs: `docker-compose logs -f`
2. Tente restart: `docker-compose restart <service>`
3. Limpe e recrie: `docker-compose down -v && docker-compose up -d`

---

**Desenvolvido como demonstração de arquitetura Python avançada para desenvolvedores sênior.**

Última atualização: Novembro 2025
