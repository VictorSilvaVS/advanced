# pysql_lite - Mini-ORM para SQLite

Uma camada de abstração simples e leve para interagir com SQLite sem escrever SQL complexo. Perfeito para pequenos projetos e aprendizado de conceitos de ORM.

## 🎯 Características

✅ **Simples e intuitivo** - Interface mínima sem complexidade desnecessária  
✅ **CRUD completo** - Operações de criar, ler, atualizar e deletar  
✅ **Query Chaining** - Construa queries complexas com encadeamento de filtros (v1.2+)  
✅ **Lazy Loading** - Queries são executadas apenas quando necessário (v1.2+)  
✅ **Tipos de campos flexíveis** - Suporte a INTEGER, TEXT, REAL, BOOLEAN, DATETIME  
✅ **Relações de banco de dados** - Chaves primárias, valores únicos, padrões  
✅ **Acesso Relacionado** - Navegue entre modelos com `usuario.posts` (v1.2+)  
✅ **Queries flexíveis** - Múltiplos operadores de filtro (>, <, IN, LIKE, etc)  
✅ **Sem dependências externas** - Usa apenas a biblioteca padrão `sqlite3`  
✅ **Bem testado** - 37 testes unitários com 100% de aprovação  
✅ **Documentado** - Exemplos, guias e comentários claros

## 📝 Versão

**v1.2.0** - Query Chaining, Related Lookups e Repr Melhorado


## 📦 Instalação

### Opção 1: Clonar o repositório
```bash
git clone https://github.com/VictorSilvaVS/advanced.git
cd LIB/pysql_lite
```

### Opção 2: Usar como módulo
```python
import sys
sys.path.insert(0, 'caminho/para/pysql_lite')
from database import Database, Model, Field, FieldType
```

## 🚀 Uso Rápido

### 1. Definir um Modelo

```python
from database import Database, Model, Field, FieldType
from datetime import datetime

class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "email": Field(FieldType.TEXT, unique=True),
        "age": Field(FieldType.INTEGER),
        "is_active": Field(FieldType.BOOLEAN, default=True),
    }
```

### 2. Conectar ao Banco de Dados

```python
# Criar/conectar ao banco de dados
db = Database("myapp.db")  # Arquivo local
# ou
db = Database(":memory:")  # Banco em memória para testes

# Inicializar o modelo
User.set_database(db)
```

### 3. Criar Registros (CREATE)

```python
user = User(name="Alice Silva", email="alice@example.com", age=28)
user_id = user.save()
print(f"Usuário criado com ID: {user_id}")
```

### 4. Buscar Registros (READ)

```python
# Buscar todos
all_users = User.find_all()

# Buscar por ID
user = User.find_by_id(1)

# Buscar um único registro
user = User.find_one(name="Alice Silva")

# Filtrar por múltiplos critérios
active_users = User.filter(is_active=True)
```

### 5. Atualizar Registros (UPDATE)

```python
user = User.find_by_id(1)
user.age = 29
user.save()
```

### 6. Deletar Registros (DELETE)

```python
# Deletar por ID
User.delete_by_id(1)

# Deletar instância
user = User.find_by_id(1)
user.delete()

# Deletar todos
User.delete_all()
```

### 7. Outras Operações

```python
# Contar registros
total = User.count()

# Converter para dicionário
user_dict = user.to_dict()
```

## 📚 Tipos de Campos

| Tipo | Descrição | Uso |
|------|-----------|-----|
| `FieldType.INTEGER` | Número inteiro | `Field(FieldType.INTEGER)` |
| `FieldType.TEXT` | Texto | `Field(FieldType.TEXT)` |
| `FieldType.REAL` | Número decimal | `Field(FieldType.REAL)` |
| `FieldType.BOOLEAN` | Booleano (0/1) | `Field(FieldType.BOOLEAN)` |
| `FieldType.DATETIME` | Data/Hora (ISO format) | `Field(FieldType.DATETIME)` |
| `FieldType.BLOB` | Dados binários | `Field(FieldType.BLOB)` |

## 🛠️ Opções de Campo

```python
Field(
    field_type=FieldType.TEXT,      # Tipo do campo
    primary_key=False,               # É chave primária?
    nullable=True,                   # Pode ser NULL?
    unique=False,                    # Valor único?
    default=None                     # Valor padrão
)
```

## 📖 Exemplos

### Exemplo 1: Sistema Simples de Usuários

```python
from database import Database, Model, Field, FieldType

class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "username": Field(FieldType.TEXT, nullable=False, unique=True),
        "email": Field(FieldType.TEXT, nullable=False),
        "is_premium": Field(FieldType.BOOLEAN, default=False),
    }

# Usar
db = Database("app.db")
User.set_database(db)

# Criar
user = User(username="alice", email="alice@example.com", is_premium=True)
user.save()

# Buscar
premium_users = User.filter(is_premium=True)
for user in premium_users:
    print(f"{user.username}: {user.email}")
```

### Exemplo 2: Blog com Posts e Comentários

```python
class Post(Model):
    _table_name = "posts"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "title": Field(FieldType.TEXT, nullable=False),
        "content": Field(FieldType.TEXT),
        "author": Field(FieldType.TEXT),
        "published_at": Field(FieldType.DATETIME),
        "views": Field(FieldType.INTEGER, default=0),
    }

class Comment(Model):
    _table_name = "comments"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "post_id": Field(FieldType.INTEGER),
        "author": Field(FieldType.TEXT),
        "text": Field(FieldType.TEXT),
        "created_at": Field(FieldType.DATETIME),
    }

# Inicializar
db = Database("blog.db")
Post.set_database(db)
Comment.set_database(db)

# Usar
post = Post(title="Meu Post", content="...", author="Alice", views=0)
post.save()

Comment(post_id=post.id, author="Bob", text="Ótimo post!", created_at=datetime.now()).save()
```

Veja mais exemplos em `examples/`:
- `simple_example.py` - Exemplo básico
- `blog_example.py` - Sistema de blog completo

## 🧪 Executar Testes

```bash
cd pysql_lite
python -m pytest tests/test_database.py -v
# ou
python tests/test_database.py
```

## 📋 Limitações

- **Sem joins automáticos** - Você gerencia relacionamentos manualmente
- **Sem migrations** - Não há sistema de versionamento de banco
- **Sem validações complexas** - Validações básicas apenas
- **SQLite apenas** - Não suporta outros bancos de dados
- **Sem lazy loading** - Todos os dados são carregados

Essas limitações são intencionais para manter a ORM simples e leve.

## 🔧 Métodos da Classe Model

### Métodos de Instância

| Método | Descrição |
|--------|-----------|
| `save()` | Insere ou atualiza o registro |
| `delete()` | Deleta a instância do banco |
| `to_dict()` | Converte para dicionário |

### Métodos de Classe

| Método | Descrição |
|--------|-----------|
| `find_all()` | Retorna todos os registros |
| `find_by_id(pk)` | Encontra por chave primária |
| `find_one(**kwargs)` | Encontra um registro por filtro |
| `filter(**kwargs)` | Filtra múltiplos registros |
| `count()` | Conta registros totais |
| `delete_by_id(pk)` | Deleta por ID |
| `delete_all()` | Deleta todos os registros |
| `set_database(db)` | Define o banco de dados |

## 🏗️ Estrutura do Projeto

```
pysql_lite/
├── __init__.py           # Exporta classes principais
├── database.py           # Core da ORM
├── examples/
│   ├── simple_example.py # Exemplo básico
│   └── blog_example.py   # Sistema de blog
├── tests/
│   ├── __init__.py
│   └── test_database.py  # Suite de testes
└── README.md            # Este arquivo
```

## 💡 Dicas de Uso

1. **Use :memory: para testes**: Mais rápido e não deixa arquivos
   ```python
   db = Database(":memory:")
   ```

2. **Sempre feche a conexão**: Libera recursos
   ```python
   db.close()
   ```

3. **Use valores padrão**: Simplifica criação de registros
   ```python
   Field(FieldType.BOOLEAN, default=True)
   Field(FieldType.INTEGER, default=0)
   ```

4. **Normalize nomes de tabelas**: Use nomes descritivos
   ```python
   _table_name = "users"  # ✓ Bom
   _table_name = "u"      # ✗ Ruim
   ```

5. **Defina chave primária**: Necessária para operações completas
   ```python
   "id": Field(FieldType.INTEGER, primary_key=True)
   ```

## 📝 Licença

MIT License - Veja LICENSE para detalhes

## 👨‍💻 Autor

Desenvolvido como exemplo educacional de Mini-ORM - by Victor Silva

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Submeter pull requests

---

**Made with ❤️ for Python developers**
