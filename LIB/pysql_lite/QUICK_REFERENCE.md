# Quick Reference - Guia Rápido

## ⚡ Uso Rápido

### Instalação (3 segundos)
```bash
pip install pysql_lite
# ou
git clone https://github.com/VictorSilvaVS/pysql_lite.git
cd pysql_lite && pip install -e .
```

### Primeiro Modelo (30 segundos)
```python
from pysql_lite import Database, Model, Field, FieldType

Database.initialize('database.db')

class User(Model):
    __tablename__ = 'users'
    name = Field(FieldType.TEXT)
    email = Field(FieldType.TEXT, unique=True)

User.create_table()
```

### CRUD Completo (1 minuto)
```python
# CREATE
user = User(name='Alice', email='alice@example.com')
user.save()

# READ
alice = User.find_by_id(1)
users = User.find_all()

# UPDATE
alice.name = 'Alicia'
alice.save()

# DELETE
alice.delete()
```

### Query Chaining (2 minutos)
```python
# Filtrar
active = User.query.filter(status='active').all()

# Ordenar
sorted = User.query.order_by('name').all()

# Limitar
first_10 = User.query.limit(10).all()

# Combinar
results = (User
    .query
    .filter(status='active')
    .order_by('-created_at')
    .limit(5)
    .all())
```

## 📋 Tipos de Campos

```python
from pysql_lite import FieldType

class Model(Model):
    id = Field(FieldType.INTEGER, primary_key=True)    # Int
    name = Field(FieldType.TEXT)                         # String
    price = Field(FieldType.REAL)                        # Float
    active = Field(FieldType.BOOLEAN)                    # Bool
    created = Field(FieldType.DATETIME)                  # DateTime
    data = Field(FieldType.BLOB)                         # Binary
```

## 🔍 11 Operadores de Query

| Operador | Símbolo | Exemplo |
|----------|---------|---------|
| Igual | `__eq` ou sem | `User.filter(status='active')` |
| Maior que | `__gt` | `User.filter(age__gt=18)` |
| Maior ou igual | `__gte` | `User.filter(age__gte=18)` |
| Menor que | `__lt` | `User.filter(age__lt=65)` |
| Menor ou igual | `__lte` | `User.filter(age__lte=65)` |
| Não igual | `__ne` | `User.filter(status__ne='inactive')` |
| Like (SQL) | `__like` | `User.filter(name__like='A%')` |
| Contém | `__contains` | `User.filter(email__contains='gmail')` |
| Começa com | `__startswith` | `User.filter(name__startswith='A')` |
| Termina com | `__endswith` | `User.filter(email__endswith='@example.com')` |
| Em lista | `__in` | `User.filter(status__in=['active', 'pending'])` |

## 🔗 Relacionamentos

### Definir Foreign Key
```python
from pysql_lite import ForeignKey

class Post(Model):
    __tablename__ = 'posts'
    user_id = Field(FieldType.INTEGER, foreign_key=ForeignKey('users', 'id'))
    title = Field(FieldType.TEXT)
```

### Registrar Relacionamento
```python
User.register_related('posts', Post, 'user_id')
```

### Usar Related Lookup
```python
user = User.find_by_id(1)
posts = user.posts.all()                    # Todos os posts
published = user.posts.filter(status='published').all()
count = user.posts.count()
```

## ✅ QuerySet Methods

```python
users = User.query

.filter(status='active')        # Filtrar (chainable)
.order_by('name')               # Ordenar (chainable)
.order_by('-id')                # Descendente (chainable)
.limit(10)                       # Limitar (chainable)
.all()                           # Executar → lista
.first()                         # Primeiro ou None
.count()                         # Contar registros
len(users)                       # Tamanho
users[0]                         # Indexação
for u in users:                  # Iteração
    print(u.name)
```

## 🎯 Padrões Comuns

### Buscar ou Criar
```python
user = User.filter(email='alice@example.com').first()
if not user:
    user = User(email='alice@example.com', name='Alice')
    user.save()
```

### Atualizar Múltiplos
```python
users = User.filter(status='old').all()
for user in users:
    user.status = 'active'
    user.save()
```

### Contar por Tipo
```python
active_count = User.filter(status='active').count()
inactive_count = User.filter(status='inactive').count()
```

### Deletar com Filtro
```python
User.filter(status='deleted').delete()
```

### Top 10
```python
top_10 = User.query.order_by('-created_at').limit(10).all()
```

## 📊 Comparação: Operações Comuns

| Tarefa | pysql_lite | SQLAlchemy | Raw SQL |
|--------|-----------|-----------|---------|
| Criar modelo | 5 linhas | 10 linhas | 15 linhas |
| Insert | `user.save()` | `session.add()` | `cursor.execute()` |
| Query simples | `.filter()` | `.filter()` | `WHERE` |
| Relacionamento | `register_related()` | `relationship()` | `JOIN` |
| Dependências | 0 | Muitas | 0 |

## 🚀 Performance Tips

### ✅ Rápido
```python
users = User.query.filter(status='active').limit(10).all()
```

### ❌ Lento
```python
all_users = User.find_all()
active = [u for u in all_users if u.status == 'active'][:10]
```

**Diferença**: 100-1000x mais rápido ⚡

## 📝 Estrutura Mínima

```python
from pysql_lite import Database, Model, Field, FieldType

# 1. Inicializar
Database.initialize('app.db')

# 2. Definir Modelo
class User(Model):
    __tablename__ = 'users'
    name = Field(FieldType.TEXT)
    email = Field(FieldType.TEXT, unique=True)

# 3. Criar tabela
User.create_table()

# 4. Usar
user = User(name='Alice', email='alice@example.com')
user.save()

users = User.query.filter(name='Alice').all()
print(users[0].email)
```

**Total**: ~15 linhas de código ✨

## 🔍 Debug

### Ver que dados
```python
user = User.find_by_id(1)
print(repr(user))  # <User pk=1 name='Alice'>
```

### Ver que campos
```python
print(User.__dict__.keys())
```

### Ver todas as tabelas
```python
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

## 📖 Documentação Rápida

| Preciso de... | Arquivo | Tempo |
|-------------|---------|-------|
| Overview | README.md | 5 min |
| Modelos | DEFINING_MODELS.md | 15 min |
| Queries | QUERYSET_GUIDE.md | 20 min |
| Problemas | TROUBLESHOOTING.md | as needed |
| Performance | PERFORMANCE.md | 15 min |
| Versões | COMPATIBILITY.md | 5 min |
| Contribuir | CONTRIBUTING.md | 20 min |
| FAQ | docs/FAQ.md | as needed |

## 🆘 Erros Comuns

| Erro | Solução |
|------|---------|
| `table already exists` | Use `:memory:` ou delete `.db` |
| `no such table` | Chame `Model.create_table()` |
| `UNIQUE constraint failed` | Verifique antes de inserir |
| `database is locked` | Feche conexões pendentes |
| `ModuleNotFoundError` | `pip install pysql_lite` |

## 🎓 Aprender Mais

```
Iniciante (30 min)    → README.md + simples_example.py
Intermediário (2h)    → DEFINING_MODELS.md + QUERYSET_GUIDE.md
Avançado (4h)         → Todos os guias + PERFORMANCE.md
Especialista (∞)      → Contribuir ao projeto!
```

## 🌟 Features

✅ CRUD completo  
✅ 11 operadores de query  
✅ Query Chaining  
✅ Lazy Loading  
✅ Relacionamentos  
✅ Zero dependências  
✅ 100% testes  
✅ Documentação completa  

## 📊 Números

```
37 testes passing
950 linhas de código
6000+ linhas de documentação
3 exemplos prontos
0 dependências externas
```

## 🎯 Comece Agora!

```bash
# 1. Clone
git clone https://github.com/VictorSilvaVS/pysql_lite.git
cd pysql_lite

# 2. Execute exemplo
python examples/simple_example.py

# 3. Execute testes
python tests/test_database.py

# 4. Leia docs
cat README.md

# 5. Estude código
cat pysql_lite/database.py
```

## 🔗 Links

- [GitHub](https://github.com/VictorSilvaVS/pysql_lite)
- [Issues](https://github.com/VictorSilvaVS/pysql_lite/issues)
- [Discussions](https://github.com/VictorSilvaVS/pysql_lite/discussions)
- [Docs](./docs/README.md)
- [Examples](./examples/)

---

**Última Atualização**: 2025-11-20  
**Versão**: 1.2.0  
**Status**: Production Ready ✅
