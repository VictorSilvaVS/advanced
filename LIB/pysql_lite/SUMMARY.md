# 🎯 pysql_lite - Resumo Executivo

## O Que É?

**pysql_lite** é um Mini-ORM (Object-Relational Mapper) simples e leve para SQLite que permite trabalhar com bancos de dados sem escrever SQL.

## Por Que Usar?

✅ **Simples** - Interface mínima e intuitiva  
✅ **Leve** - Apenas ~500 linhas de código  
✅ **Rápido** - Sem dependências externas  
✅ **Educacional** - Código bem comentado  
✅ **Completo** - CRUD total com queries  

## Como Começar em 5 Minutos?

### 1. Criar um modelo

```python
from database import Database, Model, Field, FieldType

class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT),
        "email": Field(FieldType.TEXT, unique=True),
    }
```

### 2. Conectar

```python
db = Database("app.db")
User.set_database(db)
```

### 3. Usar CRUD

```python
# CREATE
user = User(name="Alice", email="alice@example.com")
user.save()

# READ
users = User.find_all()
user = User.find_by_id(1)

# UPDATE
user.name = "Alicia"
user.save()

# DELETE
user.delete()
```

**Pronto! Nenhuma linha de SQL! 🎉**

## O Que Você Ganha?

| Recurso | Descrição |
|---------|-----------|
| **CRUD Completo** | Create, Read, Update, Delete |
| **Queries** | find_all(), find_by_id(), filter(), find_one() |
| **Agregações** | count(), delete_all() |
| **6 Tipos de Dados** | INTEGER, TEXT, REAL, BOOLEAN, DATETIME, BLOB |
| **Restrições** | Primary Key, Nullable, Unique, Default |
| **Sem SQL** | Escreva código Python apenas |
| **Sem Dependências** | Usa apenas sqlite3 nativa |

## Estrutura do Projeto

```
pysql_lite/
├── database.py          ← Core da ORM
├── examples/
│   ├── simple_example.py    ← Básico
│   └── blog_example.py      ← Avançado
├── tests/
│   └── test_database.py     ← 24 testes
└── docs/ (7 arquivos)
    ├── README.md
    ├── QUICK_START.md
    ├── GETTING_STARTED.md
    ├── DEVELOPMENT.md
    └── ... mais documentação
```

## Exemplos Rápidos

### Aplicação de Tarefas

```python
class Task(Model):
    _table_name = "tasks"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "title": Field(FieldType.TEXT, nullable=False),
        "completed": Field(FieldType.BOOLEAN, default=False),
    }

db = Database("tasks.db")
Task.set_database(db)

# Adicionar tarefa
task = Task(title="Estudar Python")
task.save()

# Listar pendentes
pending = Task.filter(completed=False)
```

### Aplicação de Contatos

```python
class Contact(Model):
    _table_name = "contacts"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "phone": Field(FieldType.TEXT),
    }

db = Database("contacts.db")
Contact.set_database(db)

# Adicionar contato
contact = Contact(name="João", phone="+55 11 98765-4321")
contact.save()

# Buscar
contacts = Contact.find_all()
```

## Métodos Disponíveis

### Instância
```python
obj.save()      # Inserir ou atualizar
obj.delete()    # Deletar
obj.to_dict()   # Converter para dict
```

### Classe
```python
Model.find_all()              # Todos
Model.find_by_id(1)           # Por ID
Model.find_one(name="John")   # Um
Model.filter(active=True)     # Múltiplos
Model.count()                 # Contar
Model.delete_by_id(1)         # Deletar por ID
Model.delete_all()            # Deletar tudo
```

## Tipos de Campo

```python
Field(FieldType.INTEGER)      # Números inteiros
Field(FieldType.TEXT)         # Texto
Field(FieldType.REAL)         # Decimais
Field(FieldType.BOOLEAN)      # Verdadeiro/Falso
Field(FieldType.DATETIME)     # Data/Hora
Field(FieldType.BLOB)         # Binário
```

## Opções de Campo

```python
Field(
    field_type=FieldType.TEXT,
    primary_key=False,    # Chave primária?
    nullable=True,        # Pode ser NULL?
    unique=False,         # Valor único?
    default="value"       # Valor padrão
)
```

## Testes

✅ **24 testes** passando (100%)

```bash
python tests/test_database.py
# Ran 24 tests ... OK
```

## Documentação

| Documento | Para |
|-----------|------|
| README.md | Documentação completa |
| QUICK_START.md | Referência rápida |
| GETTING_STARTED.md | Tutorial iniciantes |
| DEVELOPMENT.md | Contribuidores |
| examples/simple_example.py | Usar básico |
| examples/blog_example.py | Sistema completo |

## Limitações (Intencionais)

❌ Sem joins automáticos  
❌ Sem migrations  
❌ Sem validações complexas  
❌ SQLite apenas  
❌ Sem lazy loading  

*Simpleza é o objetivo!*

## Instalação

### Opção 1: Clonar
```bash
git clone https://github.com/VictorSilvaVS/advanced.git
cd LIB/pysql_lite
python examples/simple_example.py
```

### Opção 2: Usar como módulo
```python
import sys
sys.path.insert(0, 'caminho/para/pysql_lite')
from database import Database, Model, Field, FieldType
```

### Opção 3: Instalar
```bash
pip install -e .
# ou
pip install .
```

## Próximas Ações

1. **5 min:** Leia GETTING_STARTED.md
2. **5 min:** Execute examples/simple_example.py
3. **10 min:** Crie seu primeiro modelo
4. **30 min:** Explore a documentação
5. **Sempre:** Use para seus projetos!

## Comparação

| Aspecto | pysql_lite | SQLAlchemy |
|---------|-----------|-----------|
| Linhas | ~500 | 10,000+ |
| Aprendizado | Fácil | Difícil |
| Funcionalidade | Básica | Completa |
| Dependências | 0 | 2+ |
| Ideal para | Pequenos | Grande escala |

## Por Que Este Projeto?

1. **Educação** - Entender como ORMs funcionam
2. **Prototipagem** - Desenvolvimento rápido
3. **Projetos Pequenos** - Alternativa leve
4. **Diversão** - Programação Pythônica

## Estatísticas

- **500+** linhas de código
- **24** testes unitários
- **30+** métodos disponíveis
- **7** arquivos de documentação
- **2** exemplos práticos
- **6** tipos de dados
- **0** dependências externas
- **100%** de cobertura de testes

## Licença

MIT License - Livre para usar em qualquer projeto!

## Autor

Victor Silva - 2025

---

## 🚀 Comece Agora!

```python
from database import Database, Model, Field, FieldType

# 1. Definir modelo
class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT),
    }

# 2. Conectar
db = Database(":memory:")
User.set_database(db)

# 3. Usar
user = User(name="Você!")
user.save()
print(f"Olá, {user.name}!")
```

**Execute agora e divirta-se! 🎉**

---

**Para mais:** Leia os arquivos .md na pasta do projeto!
