# Roadmap - Mapa de Estrada

## 🎯 Visão Geral

Este documento descreve o plano de desenvolvimento do pysql_lite para as próximas versões.

## 📊 Status Atual

**Versão**: 1.2.0  
**Status**: Production Ready ✅  
**Testes**: 37/37 Passing  
**Documentação**: Completa  

## 🚀 Versão 2.0 - Próximos Passos

### Planejado para 2025 Q2

#### 1. Migrations & Schema Management

```python
# Novo em v2.0
from pysql_lite import Migration

class CreateUsersTable(Migration):
    version = 1
    
    def up(self):
        # Criar tabela
        pass
    
    def down(self):
        # Reverter
        pass

# Auto-executar migrações
Database.initialize('database.db', auto_migrate=True)
```

**Features**:
- ✅ Sistema de migrações automáticas
- ✅ Rollback de mudanças
- ✅ Histórico de migrações
- ✅ CLI para migrações

#### 2. Bulk Operations

```python
# Novo em v2.0
users = [User(name=f'User {i}') for i in range(10000)]

# Bulk insert
User.bulk_create(users)

# Bulk update
User.bulk_update(users, fields=['status', 'updated_at'])

# Bulk delete
User.filter(status='deleted').bulk_delete()
```

**Benefícios**:
- 10-100x mais rápido
- Melhor performance em grandes volumes

#### 3. Aggregation Functions

```python
# Novo em v2.0
from pysql_lite import Count, Sum, Avg, Max, Min

# Contagem
total = User.query.count()

# Soma
revenue = Order.query.aggregate(
    total=Sum('amount'),
    avg_order=Avg('amount')
)

# Agrupamento
by_status = Order.query.group_by('status').aggregate(
    count=Count('id'),
    total=Sum('amount')
)
```

#### 4. Full-Text Search

```python
# Novo em v2.0
from pysql_lite import SearchManager

# Criar índice
Post.search_index('title', 'content')

# Buscar
results = Post.search('python orm')

# Com ranking
results = Post.search('python orm', ranked=True)
```

---

## 📋 Versão 2.1 - Q3 2025

### Conexões Múltiplas

```python
# Novo em v2.1
Database.initialize('db1.db', alias='db1')
Database.initialize('db2.db', alias='db2')

class User(Model):
    __database__ = 'db1'

class Product(Model):
    __database__ = 'db2'

# Funciona automaticamente
user = User.find_by_id(1)  # de db1
product = Product.find_by_id(1)  # de db2
```

### JSON Field Support

```python
# Novo em v2.1
class User(Model):
    settings = Field(FieldType.JSON)
    metadata = Field(FieldType.JSON_ARRAY)

# Usar naturalmente
user.settings = {'theme': 'dark', 'language': 'pt'}
user.save()

# Queryar
users = User.filter(settings__theme='dark').all()
```

### Soft Deletes

```python
# Novo em v2.1
class User(Model):
    deleted_at = Field(FieldType.DATETIME, nullable=True)
    
    class Meta:
        soft_delete = True

# Delete suave
user.delete()  # Define deleted_at, não remove

# Ver deletados
users = User.query.with_deleted().all()

# Apenas deletados
deleted = User.query.only_deleted().all()
```

---

## 🔮 Versão 3.0 - Q4 2025

### Query Optimization Layer

```python
# Novo em v3.0
from pysql_lite import QueryOptimizer

# Auto-otimizar queries
User.query.optimize().filter(...).all()

# Explainrar plan
plan = User.query.explain()
print(plan.cost)
print(plan.steps)
```

### Caching Layer

```python
# Novo em v3.0
from pysql_lite import CacheManager

# Cache automático
users = User.query.cache(timeout=300).filter(...).all()

# Cache personalizado
cache = CacheManager(backend='redis')
Database.set_cache(cache)
```

### Async Support

```python
# Novo em v3.0
async def get_users():
    users = await User.query.afilter(status='active').aall()
    return users

# Uso
import asyncio
users = asyncio.run(get_users())
```

---

## 📚 Documento de Pesquisa: Features em Análise

### Database-Level Features

- [ ] **Connection Pooling** - Múltiplas conexões
- [ ] **Replication** - Sincronizar múltiplos arquivos
- [ ] **Backup Automático** - Snapshots periódicos
- [ ] **Compression** - Compactar banco de dados

### Query Features

- [ ] **Subqueries** - Queries aninhadas
- [ ] **Union Queries** - Combinar resultados
- [ ] **Raw SQL Support** - Queries SQL puras
- [ ] **Query Analysis** - Analisar performance

### Performance

- [ ] **Query Caching** - Cache de resultados
- [ ] **Index Management** - Criar/deletar índices
- [ ] **Statistics** - Coletar stats de query
- [ ] **Profiling** - Profile de performance

---

## 🛣️ Roadmap Visual

```
v1.2.0 ──────────┐
  (Current)       │ (Production Ready)
                  │
                  ├─── v2.0 ─── Migrations
                  │          └── Bulk Ops
                  │          └── Aggregation
                  │          └── Full-Text Search
                  │
                  ├─── v2.1 ─── Multi-DB
                  │          └── JSON Fields
                  │          └── Soft Deletes
                  │
                  └─── v3.0 ─── Query Optimizer
                             └── Caching
                             └── Async/Await
```

---

## 📈 Métricas de Progresso

| Versão | Status | ETA | Features | Testes |
|--------|--------|-----|----------|--------|
| **1.0** | ✅ Completo | - | 6 | 24 |
| **1.1** | ✅ Completo | - | 3 | 33 |
| **1.2** | ✅ Completo | - | 6 | 37 |
| **2.0** | 📋 Planejado | Q2 2025 | 4 | ~50 |
| **2.1** | 📋 Planejado | Q3 2025 | 3 | ~60 |
| **3.0** | 🔍 Pesquisa | Q4 2025 | 3 | ~70 |

---

## 🎯 Metas de Curto Prazo (Próximos 3 Meses)

- [ ] Publicar no PyPI
- [ ] Atingir 500+ stars no GitHub
- [ ] Criar comunidade Discord
- [ ] Escribir blog posts
- [ ] Apresentar em conferências

## 🎯 Metas de Médio Prazo (6-12 Meses)

- [ ] Versão 2.0 com migrações
- [ ] Suporte a múltiplos bancos
- [ ] Full-text search
- [ ] Performance análisis
- [ ] 1000+ usuários ativos

## 🎯 Metas de Longo Prazo (1-2 Anos)

- [ ] Versão 3.0 com async
- [ ] Suporte a outras databases
- [ ] IDE plugins
- [ ] Cloud dashboard
- [ ] Enterprise support

---

## 💡 Ideias em Aberto (Community Input Needed)

1. **GraphQL Support** - Expor dados via GraphQL
2. **REST API Generator** - Gerar APIs automaticamente
3. **Admin Panel** - Interface web de admin
4. **Data Validation** - Validadores customizados
5. **Webhooks** - Trigger eventos automáticos

---

## 🤝 Como Contribuir para o Roadmap

### 1. Votação em Features
Acesse as [Discussions](https://github.com/VictorSilvaVS/pysql_lite/discussions) e vote em suas features favoritas.

### 2. Propostas
Tem uma ideia? Abra uma issue com tag `proposal`:
- Descreva a feature
- Explique o benefício
- Forneça exemplos

### 3. Implementação
Quer implementar? Veja [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 📞 Feedback & Sugestões

- **Issues**: [GitHub Issues](https://github.com/VictorSilvaVS/pysql_lite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VictorSilvaVS/pysql_lite/discussions)
- **Email**: [Seu email aqui]
- **Discord**: [Link do servidor quando criado]

---

**Última Atualização**: 2025-11-20  
**Próxima Revisão**: 2025-12-20  
**Mantido por**: Comunidade pysql_lite
