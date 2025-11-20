# 🚀 Getting Started - pysql_lite

Um guia passo a passo para começar com o pysql_lite.

## ⚡ 5 Minutos para Começar

### Passo 1: Preparar o Ambiente

```bash
# Navegar até o projeto
cd LIB/pysql_lite

# Nenhuma instalação necessária! Apenas Python 3.7+
python --version  # Verificar versão
```

### Passo 2: Primeiro Código

Crie um arquivo `demo.py`:

```python
from database import Database, Model, Field, FieldType

# Definir modelo
class User(Model):
    _table_name = "users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "email": Field(FieldType.TEXT, unique=True),
    }

# Conectar
db = Database(":memory:")  # Banco em memória
User.set_database(db)

# Usar
user = User(name="Alice", email="alice@example.com")
user.save()

print(f"Usuário salvo: {user}")
print(f"ID: {user.id}")

# Buscar
found = User.find_by_id(1)
print(f"Encontrado: {found.name}")

db.close()
```

### Passo 3: Executar

```bash
python demo.py
```

**Saída esperada:**
```
Usuário salvo: User({'id': 1, 'name': 'Alice', 'email': 'alice@example.com'})
ID: 1
Encontrado: Alice
```

✅ **Pronto!** Você criou seu primeiro programa com pysql_lite.

---

## 📚 Próximos Passos

### 1. Executar Exemplos

```bash
# Exemplo básico
python examples/simple_example.py

# Sistema de blog
python examples/blog_example.py
```

### 2. Estudar a Documentação

- **README.md** - Documentação completa
- **QUICK_START.md** - Referência rápida
- **DEVELOPMENT.md** - Para desenvolvedores
- **examples/README.md** - Guia dos exemplos

### 3. Rodar os Testes

```bash
python tests/test_database.py
```

Espere ver: `Ran 24 tests ... OK`

### 4. Criar seu Próprio Projeto

Use o template abaixo como ponto de partida.

---

## 📋 Template de Projeto

Crie um novo arquivo Python:

```python
from database import Database, Model, Field, FieldType
from datetime import datetime

# ============================================================================
# DEFINIR MODELOS
# ============================================================================

class MyModel(Model):
    _table_name = "my_table"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "created_at": Field(FieldType.DATETIME),
    }

# ============================================================================
# USAR MODELOS
# ============================================================================

def main():
    # Conectar
    db = Database("myapp.db")  # Arquivo local
    MyModel.set_database(db)
    
    # Criar
    obj = MyModel(name="Test", created_at=datetime.now())
    obj.save()
    print(f"Criado: {obj}")
    
    # Buscar
    found = MyModel.find_by_id(obj.id)
    print(f"Encontrado: {found}")
    
    # Atualizar
    found.name = "Updated"
    found.save()
    print(f"Atualizado: {found}")
    
    # Deletar
    found.delete()
    print("Deletado!")
    
    # Fechar
    db.close()

if __name__ == "__main__":
    main()
```

Salve como `myapp.py` e execute:

```bash
python myapp.py
```

---

## 🎯 Casos de Uso Comuns

### Use Case 1: Aplicação de Tarefas

```python
class Task(Model):
    _table_name = "tasks"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "title": Field(FieldType.TEXT, nullable=False),
        "completed": Field(FieldType.BOOLEAN, default=False),
        "created_at": Field(FieldType.DATETIME),
    }

# Usar
db = Database("tasks.db")
Task.set_database(db)

# Adicionar tarefa
task = Task(
    title="Estudar Python",
    completed=False,
    created_at=datetime.now()
)
task.save()

# Listar tarefas incompletas
incomplete = Task.filter(completed=False)
for task in incomplete:
    print(f"[ ] {task.title}")

# Marcar como completa
task.completed = True
task.save()
```

### Use Case 2: Sistema de Contatos

```python
class Contact(Model):
    _table_name = "contacts"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "email": Field(FieldType.TEXT, unique=True),
        "phone": Field(FieldType.TEXT),
        "favorite": Field(FieldType.BOOLEAN, default=False),
    }

# Usar
db = Database("contacts.db")
Contact.set_database(db)

# Adicionar contato
contact = Contact(
    name="João Silva",
    email="joao@example.com",
    phone="+55 11 98765-4321",
    favorite=True
)
contact.save()

# Buscar favoritos
favorites = Contact.filter(favorite=True)
for c in favorites:
    print(f"⭐ {c.name}: {c.email}")

# Buscar por email
found = Contact.find_one(email="joao@example.com")
if found:
    print(f"Encontrado: {found.name}")
```

### Use Case 3: Log de Eventos

```python
class Event(Model):
    _table_name = "events"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "type": Field(FieldType.TEXT),  # 'login', 'error', 'action'
        "message": Field(FieldType.TEXT),
        "timestamp": Field(FieldType.DATETIME),
        "user_id": Field(FieldType.INTEGER),
    }

# Usar
db = Database("app_log.db")
Event.set_database(db)

# Registrar evento
event = Event(
    type="login",
    message="Usuário fez login",
    timestamp=datetime.now(),
    user_id=123
)
event.save()

# Contar eventos
total_events = Event.count()
print(f"Total de eventos: {total_events}")

# Buscar eventos de um usuário
user_events = Event.filter(user_id=123)
for e in user_events:
    print(f"[{e.type}] {e.message}")
```

---

## ⚙️ Configuração Avançada

### Usar Arquivo SQLite

```python
# Salvar no arquivo
db = Database("myapp.db")

# Todos os dados persistem entre execuções
```

### Usar Banco em Memória

```python
# Para testes rápidos
db = Database(":memory:")

# Tudo é perdido ao fechar
```

### Múltiplos Bancos

```python
db1 = Database("app1.db")
db2 = Database("app2.db")

# Resete o singleton
Database._instance = None

# Limpar para novo banco
```

---

## 🐛 Solução de Problemas

### Problema: "ModuleNotFoundError: No module named 'database'"

**Solução:**
```python
import sys
sys.path.insert(0, 'caminho/para/pysql_lite')
from database import Database, Model, Field, FieldType
```

### Problema: "Database não conectado"

**Solução:**
```python
# Verificar se set_database foi chamado
db = Database("app.db")
MyModel.set_database(db)  # Importante!
```

### Problema: "Não consegue deletar porque não tem ID"

**Solução:**
```python
# Certifique-se de chamar save() antes de delete()
obj = MyModel(...)
obj.save()  # Obtém um ID
obj.delete()  # Agora funciona
```

---

## 📖 Documentação Completa

| Documento | Propósito |
|-----------|-----------|
| README.md | Documentação completa com exemplos |
| QUICK_START.md | Referência rápida de métodos |
| DEVELOPMENT.md | Guia para contribuidores |
| examples/ | Exemplos práticos |
| tests/ | Testes como documentação |

---

## ✅ Checklist para Começar

- [ ] Python 3.7+ instalado
- [ ] Projeto clonado/baixado
- [ ] Executou example simples
- [ ] Entendeu estrutura de Model
- [ ] Rodar os testes (24 OK)
- [ ] Criar seu primeiro modelo
- [ ] Adicionar dados
- [ ] Buscar dados
- [ ] Atualizar dados
- [ ] Deletar dados

---

## 🎓 Próximos Desafios

**Iniciante:**
- [ ] Criar modelo de usuário
- [ ] Inserir 5 usuários
- [ ] Listar todos os usuários
- [ ] Atualizar um usuário
- [ ] Deletar um usuário

**Intermediário:**
- [ ] Criar dois modelos relacionados
- [ ] Implementar serviço de negócio
- [ ] Fazer queries complexas com filter
- [ ] Lidar com datas
- [ ] Implementar validação

**Avançado:**
- [ ] Estender Model com métodos custom
- [ ] Adicionar índices
- [ ] Implementar caching
- [ ] Criar migrations
- [ ] Adicionar hooks

---

## 🤝 Precisa de Ajuda?

1. **Leia a documentação** - README.md, QUICK_START.md
2. **Estude os exemplos** - simple_example.py, blog_example.py
3. **Olhe os testes** - tests/test_database.py
4. **Abra uma issue** - GitHub Issues

---

## 🎉 Parabéns!

Você está pronto para usar pysql_lite!

**Próximos passos:**
1. Criar seu primeiro projeto
2. Explorar a documentação
3. Contribuir com melhorias
4. Compartilhar seu feedback

---

**Happy coding! 🚀**

*Made with ❤️ for Python developers*
