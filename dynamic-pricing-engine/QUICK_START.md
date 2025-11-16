# 🚀 QUICK REFERENCE GUIDE

## 📍 LOCATION
```
c:\Users\victo\OneDrive\Documentos\projetos\advanced\dynamic-pricing-engine\
```

## ⚡ QUICK START (One Command)

### Windows
```powershell
cd dynamic-pricing-engine
scripts\start.bat
```

### Linux/Mac
```bash
cd dynamic-pricing-engine
chmod +x scripts/start.sh
./scripts/start.sh
```

### Docker Compose
```bash
docker-compose up -d
```

---

## 🌐 ACCESS POINTS (After Start)

| Service | URL | Purpose |
|---------|-----|---------|
| **Pricing API** | http://localhost:8000/docs | Main API + Swagger |
| **Scraper Service** | http://localhost:8001/docs | Scraper API |
| **Audit API** | http://localhost:8003/docs | Audit Endpoints |
| **Kafka** | localhost:9092 | Message Broker |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache |

---

## 🧪 QUICK TESTS

```bash
# Get price for SKU
curl http://localhost:8000/api/v1/price/SKU001

# Get batch prices
curl -X POST http://localhost:8000/api/v1/prices/batch \
  -H "Content-Type: application/json" \
  -d '{"skus": ["SKU001", "SKU002", "SKU003"]}'

# Scrape prices
curl -X POST http://localhost:8001/api/v1/scrape/single \
  -H "Content-Type: application/json" \
  -d '{"sku": "SKU001"}'

# Get statistics
curl http://localhost:8003/api/v1/statistics

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8003/health
```

---

## 📚 KEY DOCUMENTATION

| File | Purpose |
|------|---------|
| **README.md** | Complete documentation |
| **DEVELOPMENT.md** | Development setup guide |
| **EXECUTIVE_SUMMARY.md** | Business value & architecture |
| **PROJECT_MANIFEST.md** | Project overview |
| **COMPLETION_SUMMARY.txt** | What was built |

---

## 🔍 EXPLORE CODE

```
# See pricing rules with Numba optimization
src/rules_engine/engine.py

# See async scraper with I/O parallelism
src/scraper_service/scraper.py

# See API with Redis cache
src/pricing_api/cache.py
src/pricing_api/service.py

# See database persistence
src/audit_service/models.py
```

---

## 🛠️ USEFUL COMMANDS

### View Logs
```bash
docker-compose logs -f pricing_api
docker-compose logs -f rules_engine_worker
docker-compose logs -f audit_service_worker
```

### Access Databases

**PostgreSQL:**
```bash
docker-compose exec postgres psql -U pricing_user -d pricing_db
```

**Redis:**
```bash
docker-compose exec redis redis-cli
```

**Kafka Topics:**
```bash
docker-compose exec kafka kafka-topics --bootstrap-server kafka:9092 --list
```

### Stop Services
```bash
docker-compose stop           # Stop but keep data
docker-compose down           # Stop and remove containers
docker-compose down -v        # Clean everything
```

### Restart Service
```bash
docker-compose restart <service_name>
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/test_pricing_rules.py -v
```

---

## 📊 ARCHITECTURE AT A GLANCE

```
SCRAPER → KAFKA → RULES ENGINE → KAFKA → PRICING API ← CLIENTS
              ↓                        ↓
         (raw_prices)        (recommended_prices)
                                      ↓
                                  AUDIT SERVICE
                                      ↓
                               PostgreSQL
```

---

## 🎯 KEY FEATURES

✅ **Async I/O**: 1000s parallel requests  
✅ **Data Processing**: Pandas + Numba optimization  
✅ **Real-time Cache**: Redis with fallback  
✅ **Message Queue**: Kafka with Dead Letter Queue  
✅ **Auditoria**: PostgreSQL persistence  
✅ **Performance**: < 10ms latency SLA  
✅ **Production Ready**: Docker, tests, logging  

---

## 📱 POSTMAN COLLECTION

Import file: `DynamicPricingEngine.postman_collection.json`

Includes:
- Pricing API endpoints
- Scraper Service endpoints
- Audit Service endpoints
- Variable templates

---

## 🧠 LEARNING PATH

1. **Start**: Run `./scripts/start.sh`
2. **Explore**: http://localhost:8000/docs
3. **Test**: `./scripts/test.sh`
4. **Read**: README.md → DEVELOPMENT.md
5. **Study**: src/ folder code
6. **Debug**: `docker-compose logs -f`
7. **Extend**: Add new rules or features

---

## 🎓 EXPERTISE DEMONSTRATED

- ✅ Microservices architecture
- ✅ Python async programming
- ✅ Data engineering (Pandas, Numba)
- ✅ Distributed systems (Kafka)
- ✅ Database design (PostgreSQL)
- ✅ Caching strategies (Redis)
- ✅ Docker & containerization
- ✅ Performance optimization
- ✅ System design for scale

---

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Service won't start | `docker-compose logs -f <service>` |
| API not responding | `curl http://localhost:8000/health` |
| Database error | `docker-compose restart postgres` |
| Cache issue | `docker-compose restart redis` |
| Full reset | `docker-compose down -v && docker-compose up -d` |

---

## 🎉 YOU'RE READY!

Everything is set up and ready to go. Start exploring! 🚀

Questions? Check:
- README.md (full docs)
- DEVELOPMENT.md (setup guide)
- Swagger UI (API docs)
- Docker logs (debugging)
