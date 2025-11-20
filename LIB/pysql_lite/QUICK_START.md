# Quick Start - pysql_lite

## 1️⃣ Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/VictorSilvaVS/advanced.git
cd LIB/pysql_lite

# Ou usar como módulo
import sys
sys.path.insert(0, 'caminho/para/pysql_lite')
```

## 2️⃣ Seu Primeiro Modelo

```python
from database import Database, Model, Field, FieldType

class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "email": Field(FieldType.TEXT, unique=True),
        "age": Field(FieldType.INTEGER),
    }

# Conectar
db = Database("app.db")
User.set_database(db)
```

## 3️⃣ Operações Básicas

```python
# CREATE - Inserir
user = User(name="Alice", email="alice@example.com", age=28)
user_id = user.save()

# READ - Buscar
user = User.find_by_id(1)
all_users = User.find_all()
active_users = User.filter(name="Alice")

# UPDATE - Atualizar
user.age = 29
user.save()

# DELETE - Deletar
user.delete()
# ou
User.delete_by_id(1)
```

## 4️⃣ Tipos de Campos

```python
Field(FieldType.INTEGER)      # Números inteiros
Field(FieldType.TEXT)         # Texto
Field(FieldType.REAL)         # Números decimais
Field(FieldType.BOOLEAN)      # Booleanos (True/False)
Field(FieldType.DATETIME)     # Data/hora
Field(FieldType.BLOB)         # Dados binários
```

## 5️⃣ Opções de Campo

```python
Field(
    field_type=FieldType.TEXT,
    primary_key=False,    # Chave primária?
    nullable=True,        # Pode ser NULL?
    unique=False,         # Valor único?
    default="value"       # Valor padrão
)
```

## 6️⃣ Exemplos Completos

### Exemplo 1: Aplicação de Notas

```python
from database import Database, Model, Field, FieldType
from datetime import datetime

class Note(Model):
    _table_name = "notes"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "title": Field(FieldType.TEXT, nullable=False),
        "content": Field(FieldType.TEXT),
        "created_at": Field(FieldType.DATETIME),
        "is_archived": Field(FieldType.BOOLEAN, default=False),
    }

# Usar
db = Database("notes.db")
Note.set_database(db)

# Criar
note = Note(
    title="Meu Projeto",
    content="Fazer X, Y, Z",
    created_at=datetime.now()
)
note.save()

# Buscar
all_notes = Note.find_all()
active_notes = Note.filter(is_archived=False)

# Fechar
db.close()
```

### Exemplo 2: Loja Online

```python
class Product(Model):
    _table_name = "products"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "price": Field(FieldType.REAL),
        "stock": Field(FieldType.INTEGER, default=0),
        "in_stock": Field(FieldType.BOOLEAN, default=True),
    }

class Order(Model):
    _table_name = "orders"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "product_id": Field(FieldType.INTEGER),
        "quantity": Field(FieldType.INTEGER),
        "total": Field(FieldType.REAL),
        "created_at": Field(FieldType.DATETIME),
    }

# Usar
db = Database("shop.db")
Product.set_database(db)
Order.set_database(db)

# Adicionar produtos
p1 = Product(name="Notebook", price=2500.00, stock=10)
p1.save()

# Criar ordem
order = Order(product_id=p1.id, quantity=2, total=5000.00, created_at=datetime.now())
order.save()
```

## 7️⃣ Métodos Disponíveis

### Instância
- `save()` - Inserir ou atualizar
- `delete()` - Deletar registro
- `to_dict()` - Converter para dicionário

### Classe
- `find_all()` - Todos os registros
- `find_by_id(pk)` - Por chave primária
- `find_one(**kwargs)` - Um registro com filtro
- `filter(**kwargs)` - Múltiplos registros com filtro
- `count()` - Total de registros
- `delete_by_id(pk)` - Deletar por ID
- `delete_all()` - Deletar tudo
- `set_database(db)` - Definir banco de dados

## 8️⃣ Executar Testes

```bash
python tests/test_database.py
```

Todos os 24 testes devem passar ✅

## 9️⃣ Dicas Importantes

✅ **Use :memory: para testes**
```python
db = Database(":memory:")
```

✅ **Sempre feche a conexão**
```python
db.close()
```

✅ **Defina chave primária sempre**
```python
"id": Field(FieldType.INTEGER, primary_key=True)
```

✅ **Use valores padrão**
```python
Field(FieldType.BOOLEAN, default=True)
```

## 🔟 Limitações Conhecidas

- Sem joins automáticos (gerenciar relacionamentos manualmente)
- Sem migrations
- Sem validações complexas
- SQLite apenas
- Sem lazy loading

Essas limitações são intencionais para manter a ORM simples! 🎯

---

Para mais exemplos, veja a pasta `examples/`:
- `simple_example.py` - Exemplo básico
- `blog_example.py` - Sistema de blog completo
