# Troubleshooting - Resolução de Problemas

## 🔍 Problemas Comuns

### 1. "ModuleNotFoundError: No module named 'pysql_lite'"

**Erro:**
```
ModuleNotFoundError: No module named 'pysql_lite'
```

**Causas Possíveis:**
1. ❌ pysql_lite não está instalado
2. ❌ Ambientel Python errado
3. ❌ PYTHONPATH não configurado

**Soluções:**

```bash
# Verificar se está instalado
pip list | grep pysql_lite

# Instalar
pip install pysql_lite

# Ou clone e instale
git clone https://github.com/VictorSilvaVS/pysql_lite.git
cd pysql_lite
pip install -e .

# Verificar Python correto
which python
python --version
```

### 2. "sqlite3.OperationalError: table already exists"

**Erro:**
```
sqlite3.OperationalError: table already exists
```

**Causas:**
- ❌ Criando tabela que já existe
- ❌ Banco de dados não foi limpado

**Soluções:**

```python
# Opção 1: Usar banco em memória para testes
Database.initialize(':memory:')

# Opção 2: Usar arquivo novo
import os
if os.path.exists('database.db'):
    os.remove('database.db')
Database.initialize('database.db')

# Opção 3: Verificar antes de criar
# (Mais seguro em produção)
```

### 3. "sqlite3.IntegrityError: UNIQUE constraint failed"

**Erro:**
```
sqlite3.IntegrityError: UNIQUE constraint failed: users.email
```

**Causas:**
- ❌ Tentando inserir email duplicado
- ❌ Não validando entrada antes de save

**Soluções:**

```python
# Verificar antes de inserir
class User(Model):
    __tablename__ = 'users'
    email = Field(FieldType.TEXT, unique=True)

# Validar antes de save
existing = User.filter(email='alice@example.com').first()
if existing:
    print("Email já existe!")
else:
    user = User(email='alice@example.com')
    user.save()

# Ou use try-except
try:
    user.save()
except Exception as e:
    print(f"Erro ao salvar: {e}")
```

### 4. "sqlite3.OperationalError: no such table"

**Erro:**
```
sqlite3.OperationalError: no such table: users
```

**Causas:**
- ❌ Tabela nunca foi criada
- ❌ Database não foi inicializado
- ❌ Nome da tabela errado (case-sensitive)

**Soluções:**

```python
# Verificar se Database está inicializado
from pysql_lite import Database
db = Database.get_instance()
print(db)  # Deve mostrar conexão

# Verificar nome da tabela
class User(Model):
    __tablename__ = 'users'  # Verifique se está correto!

# Garantir que criou a tabela
Database.initialize('database.db')
User.create_table()  # Cria a tabela

# Verificar tabelas existentes
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

### 5. "TypeError: unsupported operand type(s)"

**Erro:**
```
TypeError: unsupported operand type(s) for -: 'str' and 'int'
```

**Causas:**
- ❌ Tipo de dados incompatível
- ❌ Campo DATETIME não convertido
- ❌ Boolean não convertido

**Soluções:**

```python
# Verificar tipos
from pysql_lite import FieldType

class User(Model):
    name = Field(FieldType.TEXT)        # ✅ String
    age = Field(FieldType.INTEGER)      # ✅ Int
    created = Field(FieldType.DATETIME) # ✅ Datetime
    active = Field(FieldType.BOOLEAN)   # ✅ Bool

# Converter ao carregar
user = User.find_by_id(1)
print(type(user.age))      # <class 'int'>
print(type(user.active))   # <class 'bool'>
print(type(user.created))  # <class 'datetime.datetime'>
```

---

## 🐛 Problemas de Conexão

### 6. "Database is locked"

**Erro:**
```
sqlite3.OperationalError: database is locked
```

**Causas:**
- ❌ Múltiplas conexões simultâneas
- ❌ Transação não finalizada
- ❌ Outro processo usando o banco

**Soluções:**

```python
# Verificar se há processos usando o banco
import os
os.system('lsof database.db')  # Linux/Mac
# ou
os.system('openfiles.exe | find "database.db"')  # Windows

# Fechar conexões
from pysql_lite import Database
db = Database.get_instance()
# db.close()  # Se implementado

# Usar :memory: para testes
Database.initialize(':memory:')

# Para produção, considere WAL mode
# (Planejado para v2.0)
```

### 7. "Connection Already Established"

**Erro:**
```
Exception: Database already initialized
```

**Causas:**
- ❌ Chamando `initialize()` duas vezes
- ❌ Múltiplas chamadas em diferentes módulos

**Soluções:**

```python
# Verificar inicialização
from pysql_lite import Database

try:
    Database.initialize('database.db')
except Exception:
    pass  # Já inicializado

# Ou pegar instância existente
db = Database.get_instance()

# Melhor: inicializar uma vez (ex: app.py)
# Depois apenas usar em outros módulos
```

---

## 🔧 Problemas de Desenvolvimento

### 8. "Field not recognized"

**Erro:**
```
KeyError: 'unknown_field'
```

**Causas:**
- ❌ Nome do campo errado
- ❌ Typo no nome
- ❌ Field não foi definido

**Soluções:**

```python
# Verificar nome do campo
class User(Model):
    __tablename__ = 'users'
    name = Field(FieldType.TEXT)
    email = Field(FieldType.TEXT)

# Correto
user = User(name='Alice', email='alice@example.com')

# Errado - vai falhar
# user = User(full_name='Alice')  # unknown_field

# Verificar campos disponíveis
print(User.__dict__.keys())
```

### 9. "Foreign Key Not Found"

**Erro:**
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Causas:**
- ❌ Referência de FK não existe
- ❌ Deletou o pai sem cascata
- ❌ Tipo de dado incompatível

**Soluções:**

```python
# Verificar que o pai existe
user = User.find_by_id(user_id)
if not user:
    raise ValueError("User não existe!")

# Depois criar child
post = Post(user_id=user.id, title='...')
post.save()

# Definir corretamente
from pysql_lite import ForeignKey

class Post(Model):
    user_id = Field(
        FieldType.INTEGER,
        foreign_key=ForeignKey('users', 'id')
    )

# Registrar relacionamento
Post.register_related('posts', Post, 'user_id')
```

### 10. "QuerySet object is not callable"

**Erro:**
```
TypeError: 'QuerySet' object is not callable
```

**Causas:**
- ❌ Usar `.query()` ao invés de `.query` (v1.2+)
- ❌ Chamar resultado final como função

**Soluções:**

```python
# ✅ Correto (v1.2+)
users = User.query.filter(status='active').all()

# ❌ Errado
# users = User.query().filter(status='active').all()

# ✅ Correto (v1.0)
users = User.find_all()

# Sempre pode usar métodos de Model
users = User.filter(status='active').all()
```

---

## 📊 Problemas de Performance

### 11. "Aplicação muito lenta"

**Sintomas:**
- ❌ Queries levam muitos segundos
- ❌ 100% CPU durante queries
- ❌ Memória crescendo

**Diagnóstico:**

```python
import time

# Medir tempo
start = time.time()
users = User.find_all()
print(f"Levou {time.time() - start:.2f}s")

# Medir tamanho
import sys
print(f"Size: {sys.getsizeof(users) / 1024 / 1024:.2f} MB")

# Contar registros
print(f"Registros: {len(users)}")
```

**Soluções:**

```python
# 1. Use limit
users = User.query.limit(100).all()  # ✅ Rápido

# 2. Filtre antes
users = User.filter(status='active').all()  # ✅ Rápido

# 3. Evite load de tudo
# ❌ Lento
for u in User.find_all():
    print(u.name)

# ✅ Rápido (futuro v2.0)
# for u in User.query.iterator():
#     print(u.name)
```

### 12. "Out of Memory"

**Sintomas:**
- ❌ Erro: "MemoryError"
- ❌ Sistema fica muito lento
- ❌ Swap disso começa a usar

**Soluções:**

```python
# ❌ Carrega tudo
users = User.find_all()  # 1M registros = muita RAM

# ✅ Processa em lotes
BATCH_SIZE = 1000
for i in range(0, total, BATCH_SIZE):
    users = User.query.limit(BATCH_SIZE).all()  # Process

# ✅ Usa generator (futuro v2.0)
# for user in User.query.iterator(batch_size=1000):
#     process(user)
```

---

## 🚨 Erros em Produção

### 13. "Corrupted Database File"

**Sintomas:**
- ❌ Erro ao abrir banco
- ❌ Dados inconsistentes
- ❌ Arquivo corrompido

**Prevenção:**

```python
# 1. Fazer backup regular
import shutil
import datetime

def backup_database():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy('database.db', f'backup_{timestamp}.db')

# 2. Usar transações corretamente
# (v1.2+ tem suporte)

# 3. Monitorar integridade
import sqlite3
try:
    conn = sqlite3.connect('database.db')
    conn.execute('PRAGMA integrity_check')
except Exception as e:
    print(f"Banco corrompido: {e}")
```

### 14. "Too Many Connections"

**Erro:**
```
sqlite3.OperationalError: too many connections
```

**Causas:**
- ❌ Não fechando conexões
- ❌ Pool sem limite
- ❌ Memory leaks

**Soluções:**

```python
# Fechar conexões corretamente
from pysql_lite import Database

db = Database.get_instance()
# Implementar close() em v2.0

# Usar context manager
# with Database.connection() as db:  # Futuro
#     users = User.find_all()
```

---

## 📝 Debug e Logging

### Configurar Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('pysql_lite')

# Usar em seu código
logger.debug(f"Querying users: {query}")
logger.error(f"Error: {error}")
```

### Inspetuar Objetos

```python
from pysql_lite import Database, Model, Field, FieldType

# Ver atributos de Model
print(User.__dict__)
print(vars(user))

# Ver campos
for name, field in User.__dict__.items():
    if isinstance(field, Field):
        print(f"{name}: {field.field_type}")

# Ver dados
user = User.find_by_id(1)
print(user.__dict__)
print(repr(user))
```

---

## 🆘 Quando Pedir Ajuda

### Checklist Antes de Reportar Bug

- [ ] Reproduzi o erro em um script simples?
- [ ] Tentei em um banco :memory:?
- [ ] Verificei a versão do Python?
- [ ] Limpei o pycache?
- [ ] Reinstalei pysql_lite?
- [ ] Consultei FAQ.md?
- [ ] Pesquisei issues existentes?

### Reportar um Bug

Abra uma issue no GitHub com:

```markdown
## Descrição
Descrição clara do problema

## Código de Reprodução
```python
# Código mínimo para reproduzir
```

## Resultado Esperado
O que deveria acontecer

## Resultado Atual
O que está acontecendo

## Ambiente
- Python: 3.10
- pysql_lite: 1.2.0
- SO: Windows 10
```

---

## 📞 Recursos de Ajuda

| Canal | Uso | Resposta |
|-------|-----|----------|
| **Issues** | Bugs, Features | 24-48h |
| **Discussions** | Questões, Ideias | 48-72h |
| **FAQ.md** | Questões comuns | Imediato |
| **Docs** | Como usar | Imediato |

---

**Última Atualização**: 2025-11-20  
**Problemas Documentados**: 14  
