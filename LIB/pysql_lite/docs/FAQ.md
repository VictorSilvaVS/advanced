# FAQ - Perguntas Frequentes

## 🚀 Instalação e Setup

### P: Como instalar o pysql_lite?

**R:** Você pode instalar de três maneiras:

```bash
# 1. Via pip (quando publicado no PyPI)
pip install pysql_lite

# 2. Via clone do repositório
git clone https://github.com/VictorSilvaVS/pysql_lite.git
cd pysql_lite
pip install -e .

# 3. Sem instalação (copie o arquivo)
cp pysql_lite/database.py seu_projeto/
```

### P: Preciso instalar dependências externas?

**R:** Não! O pysql_lite usa apenas a biblioteca padrão Python (`sqlite3`). Zero dependências externas.

### P: Qual versão Python preciso?

**R:** Python 3.7 ou superior. Testado e compatível com Python 3.7 até 3.12+.

```bash
python --version  # Verifique sua versão
```

### P: Como funciona no Raspberry Pi?

**R:** Funciona perfeitamente! Desde que tenha Python 3.7+:

```bash
sudo apt-get install python3
pip install pysql_lite
```

---

## 💾 Banco de Dados e Arquivos

### P: Onde os dados são armazenados?

**R:** Em um arquivo SQLite (`.db` ou `.sqlite`):

```python
from pysql_lite import Database, Model, Field, FieldType

# Cria/abre database.db no diretório atual
Database.initialize('database.db')

class User(Model):
    __tablename__ = 'users'
    name = Field(FieldType.TEXT)

# Dados saltos em database.db
user = User(name='Alice')
user.save()
```

### P: Posso usar um banco de dados existente?

**R:** Sim! O pysql_lite funciona com qualquer arquivo SQLite:

```python
# Conecta a um banco existente
Database.initialize('caminho/para/existing.db')
```

### P: Como faço backup do banco de dados?

**R:** Simples - copie o arquivo `.db`:

```bash
cp database.db database_backup.db
```

Ou em Python:

```python
import shutil
shutil.copy('database.db', 'database_backup.db')
```

### P: Posso usar o pysql_lite em múltiplos arquivos?

**R:** Sim, via Singleton:

```python
# Arquivo 1
Database.initialize('database.db')

# Arquivo 2
db = Database.get_instance()  # Mesma instância
```

---

## 🔍 Queries e Filtros

### P: Como fazer uma busca simples?

**R:** Use o método `filter()`:

```python
# Buscar um usuário
users = User.find_all()  # Todos

user = User.find_by_id(1)  # Por ID

# Com filtro
alice = User.filter(name='Alice').first()
```

### P: Como usar operadores avançados?

**R:** O pysql_lite suporta 11 operadores:

```python
# Maior que (gt)
users = User.filter(age__gt=18).all()

# Menor ou igual (lte)
users = User.filter(age__lte=65).all()

# Contém (contains)
users = User.filter(email__contains='gmail').all()

# Começa com (startswith)
users = User.filter(name__startswith='A').all()

# Em uma lista (in)
users = User.filter(status__in=['active', 'pending']).all()

# Completa lista:
# eq, gt, gte, lt, lte, ne, like, contains, startswith, endswith, in
```

### P: Como fazer query chaining?

**R:** O QuerySet suporta chaining:

```python
users = (User
    .query
    .filter(status='active')
    .filter(age__gt=18)
    .order_by('name')
    .limit(10)
    .all())
```

### P: Como ordernar resultados?

**R:** Use `order_by()`:

```python
# Ascendente (padrão)
users = User.query.order_by('name').all()

# Descendente
users = User.query.order_by('-id').all()
```

### P: Como limitar resultados?

**R:** Use `limit()` ou indexação:

```python
# Limitar a 10
users = User.query.limit(10).all()

# Pegar apenas o primeiro
user = User.query.first()

# Indexação
user = User.query.all()[0]
```

---

## 📝 Modelos e Campos

### P: Quais tipos de campo existem?

**R:** 6 tipos de dados:

```python
from pysql_lite import Field, FieldType

class Product(Model):
    __tablename__ = 'products'
    
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT)           # Texto
    price = Field(FieldType.REAL)          # Número decimal
    quantity = Field(FieldType.INTEGER)    # Número inteiro
    active = Field(FieldType.BOOLEAN)      # Booleano (True/False)
    created = Field(FieldType.DATETIME)    # Data e hora
    data = Field(FieldType.BLOB)           # Dados binários
```

### P: Como defino uma chave primária?

**R:** Use `primary_key=True`:

```python
class User(Model):
    __tablename__ = 'users'
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT)
```

### P: Posso ter valores padrão?

**R:** Sim, com `default`:

```python
class User(Model):
    __tablename__ = 'users'
    status = Field(FieldType.TEXT, default='active')
    created = Field(FieldType.DATETIME, default=lambda: datetime.now())
```

### P: Posso ter campos obrigatórios?

**R:** Sim, com `nullable=False`:

```python
class User(Model):
    __tablename__ = 'users'
    email = Field(FieldType.TEXT, nullable=False)  # Obrigatório
    phone = Field(FieldType.TEXT)                  # Opcional
```

### P: Como crio relacionamentos entre tabelas?

**R:** Use `ForeignKey`:

```python
from pysql_lite import ForeignKey

class Post(Model):
    __tablename__ = 'posts'
    user_id = Field(FieldType.INTEGER, foreign_key=ForeignKey('users', 'id'))
    title = Field(FieldType.TEXT)
```

---

## 🔗 Relacionamentos

### P: Como faço related lookups?

**R:** Use `register_related()` e o descriptor:

```python
class Post(Model):
    __tablename__ = 'posts'
    user_id = Field(FieldType.INTEGER, foreign_key=ForeignKey('users', 'id'))

class User(Model):
    __tablename__ = 'users'

# Registrar relacionamento
User.register_related('posts', Post, 'user_id')

# Usar related lookup
user = User.find_by_id(1)
posts = user.posts.all()
published = user.posts.filter(status='published').count()
```

### P: Posso usar reverse lookups?

**R:** Sim, é automático:

```python
user = User.find_by_id(1)
posts = user.posts.all()  # Todos os posts do usuário
```

---

## 🧪 Testes

### P: Como executar os testes?

**R:** Dois métodos:

```bash
# Método 1: Python direto
python tests/test_database.py

# Método 2: pytest (se instalado)
pytest tests/

# Com verbose
pytest tests/ -v
```

### P: Todos os testes passam?

**R:** Sim! 37/37 testes passam:

```
Ran 37 tests in 0.013s
OK
```

### P: Como criar meus próprios testes?

**R:** Use `unittest` (padrão):

```python
import unittest
from pysql_lite import Database, Model, Field, FieldType

class TestMyModel(unittest.TestCase):
    def setUp(self):
        Database.initialize(':memory:')
    
    def test_create_user(self):
        # Seu teste aqui
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## 🐛 Problemas e Debugging

### P: Recebi um erro "table already exists"

**R:** A tabela já foi criada. Use `:memory:` para começar novo:

```python
# Começo fresco
Database.initialize(':memory:')

# Ou use um novo arquivo
Database.initialize('novo_banco.db')
```

### P: Como vejo as queries SQL geradas?

**R:** O pysql_lite usa SQL internamente. Para debug:

```python
# Veja o último erro
try:
    user = User.filter(invalid_field='value').first()
except Exception as e:
    print(e)  # Mostra o erro SQL
```

### P: Como limpo o banco de dados?

**R:** Delete o arquivo `.db`:

```bash
rm database.db
```

Ou em Python:

```python
import os
os.remove('database.db')
```

### P: O pysql_lite é thread-safe?

**R:** Parcialmente. Recomenda-se usar locks para operações concorrentes. SQLite tem limitações de escrita simultânea.

### P: Pode ajudar com um problema específico?

**R:** Abra uma issue no GitHub com:
- Versão Python
- Versão pysql_lite
- Código de reprodução
- Stack trace completo

---

## 📚 Documentação e Exemplos

### P: Onde encontro exemplos?

**R:** Na pasta `examples/`:
- `simple_example.py` - CRUD básico
- `blog_example.py` - Sistema blog
- `advanced_example.py` - Recursos avançados

### P: Como executo um exemplo?

**R:** 

```bash
cd examples
python simple_example.py
```

### P: Existe documentação completa?

**R:** Sim! Consulte:
- [README.md](./README.md) - Visão geral
- [DEFINING_MODELS.md](./DEFINING_MODELS.md) - Como criar modelos
- [QUERYSET_GUIDE.md](./QUERYSET_GUIDE.md) - Query chaining
- [docs/](./docs/) - Mais documentação

---

## 🤝 Contribuindo

### P: Como contribuo?

**R:** Veja [CONTRIBUTING.md](./CONTRIBUTING.md):
1. Fork o repositório
2. Crie uma branch
3. Faça suas mudanças
4. Envie um pull request

### P: Posso sugerir uma feature?

**R:** Sim! Abra uma issue com tag `enhancement`.

### P: Como reporto um bug?

**R:** Abra uma issue com tag `bug` incluindo:
- Descrição clara
- Código de reprodução
- Comportamento esperado vs real

---

## 💡 Dicas e Truques

### P: Como otimizar queries?

**R:** Use `limit()` para grandes datasets:

```python
# ❌ Lento
todos = User.find_all()

# ✅ Rápido
usuarios_ativos = User.query.filter(status='active').limit(100).all()
```

### P: Como fazer operações em batch?

**R:** Use loop com transações:

```python
users = [User(name=f'User {i}') for i in range(1000)]
for user in users:
    user.save()
```

### P: Posso usar em produção?

**R:** Sim! O pysql_lite é production-ready (v1.2.0+):
- ✅ 100% testes passando
- ✅ Zero dependências
- ✅ Documentação completa
- ✅ MIT License

---

## 📞 Ainda tem dúvidas?

1. Consulte a [documentação completa](./docs/)
2. Veja os [exemplos](./examples/)
3. Abra uma [issue no GitHub](https://github.com/VictorSilvaVS/pysql_lite/issues)
4. Participe das [discussions](https://github.com/VictorSilvaVS/pysql_lite/discussions)

---

**Última Atualização**: 2025-11-20  
**FAQ Mantido por**: Comunidade pysql_lite
