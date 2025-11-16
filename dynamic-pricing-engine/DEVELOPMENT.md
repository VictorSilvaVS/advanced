# Development Guide

## Local Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- PostgreSQL Client (psql) - Optional for direct DB access
- Redis Client (redis-cli) - Optional
- Postman - Optional for API testing

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repo>
cd dynamic-pricing-engine

# Start all services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Local Python Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services individually
# Terminal 1: Pricing API
python -m src.pricing_api.main

# Terminal 2: Scraper Service
python -m src.scraper_service.main

# Terminal 3: Rules Engine Worker
python -m src.rules_engine.worker

# Terminal 4: Audit Service Worker
python -m src.audit_service.worker

# Terminal 5: Audit API
python -m src.audit_service.main
```

This requires:
- PostgreSQL running locally on port 5432
- Redis running locally on port 6379
- Kafka running locally on port 9092

### Environment Variables

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

---

## Development Workflow

### Making Code Changes

1. **Edit source files**
   ```bash
   # Example: Modifying pricing rules
   vim src/rules_engine/engine.py
   ```

2. **Test locally**
   ```bash
   # With Docker Compose
   docker-compose restart rules_engine_worker
   
   # Or with local Python (restart terminal)
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   
   # Specific test
   pytest tests/test_pricing_rules.py::test_margin_calculation -v
   
   # With coverage
   pytest tests/ --cov=src --cov-report=html
   ```

### Testing APIs

**Using curl:**
```bash
# Test Pricing API
curl http://localhost:8000/api/v1/price/SKU001

# Test Scraper Service
curl -X POST http://localhost:8001/api/v1/scrape/single \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU001"}'
```

**Using Postman:**
1. Import `DynamicPricingEngine.postman_collection.json`
2. Set variables in Postman environment
3. Run requests

**Using Python:**
```python
import asyncio
import aiohttp

async def test_api():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/v1/price/SKU001") as resp:
            print(await resp.json())

asyncio.run(test_api())
```

---

## Database Access

### PostgreSQL

```bash
# Connect to database
docker-compose exec postgres psql -U pricing_user -d pricing_db

# View pricing decisions
SELECT * FROM pricing_decisions LIMIT 5;

# View failures
SELECT * FROM pricing_failures LIMIT 5;

# Statistics
SELECT COUNT(*), AVG(margin_pct), AVG(confidence) 
FROM pricing_decisions;
```

### Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View keys
KEYS *

# View cached price
GET price:SKU001

# Clear cache
FLUSHALL
```

---

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs -f <service_name>

# Restart service
docker-compose restart <service_name>

# Full restart
docker-compose down
docker-compose up -d
```

### Kafka connection issues

```bash
# Check Kafka health
docker-compose exec kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092

# View topics
docker-compose exec kafka kafka-topics \
  --bootstrap-server kafka:9092 --list
```

### Cache not working

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL

# Restart Pricing API
docker-compose restart pricing_api
```

---

## Performance Profiling

### CPU Profiling

```python
import cProfile
import pstats
from src.rules_engine.engine import PricingRulesEngine

pr = cProfile.Profile()
pr.enable()

# Run code to profile
engine = PricingRulesEngine()
# ... execute operations ...

pr.disable()
ps = pstats.Stats(pr).sort_stats('cumulative')
ps.print_stats(20)  # Top 20 functions
```

### Memory Profiling

```bash
pip install memory-profiler

python -m memory_profiler src/rules_engine/worker.py
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/v1/price/SKU001

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/v1/price/SKU001
```

---

## Adding New Features

### Add a new pricing rule

1. **Edit `src/rules_engine/engine.py`:**
   ```python
   def _apply_new_rule(self, price: float, param: float) -> float:
       """New rule logic"""
       return price * (1 + param)
   ```

2. **Update `calculate_price()` method:**
   ```python
   # Add to rule chain
   new_rule_price = self._apply_new_rule(inventory_adjusted_price, new_param)
   ```

3. **Test the rule:**
   ```bash
   pytest tests/test_pricing_rules.py::test_new_rule -v
   ```

4. **Update Docker Compose if needed** for configuration changes

### Add a new API endpoint

1. **Edit service main file** (e.g., `src/pricing_api/main.py`):
   ```python
   @app.post("/api/v1/new_endpoint")
   async def new_endpoint(request: NewRequest) -> NewResponse:
       """New endpoint logic"""
       return NewResponse(...)
   ```

2. **Restart service:**
   ```bash
   docker-compose restart pricing_api
   ```

3. **Test endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/new_endpoint
   ```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src
```

---

## Documentation

### Generate API documentation

```bash
# FastAPI auto-generates Swagger docs
# Available at: http://localhost:8000/docs

# For Python docstrings
pip install sphinx
sphinx-build -b html docs/ build/docs/
```

### Code Style

```bash
# Format code
pip install black
black src/

# Lint code
pip install flake8
flake8 src/

# Type checking
pip install mypy
mypy src/
```

---

## Deployment

### Build Docker images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build pricing_api
```

### Push to registry

```bash
docker tag pricing-engine:latest myregistry/pricing-engine:latest
docker push myregistry/pricing-engine:latest
```

### Deploy to Kubernetes

```bash
# Convert docker-compose to Kubernetes manifests
docker-compose convert > kubernetes.yaml

# Apply to cluster
kubectl apply -f kubernetes.yaml
```

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

For more help, check the main [README.md](README.md)
