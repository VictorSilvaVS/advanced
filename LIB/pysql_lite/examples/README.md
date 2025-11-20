# 📚 Exemplos - pysql_lite

Este diretório contém exemplos práticos de como usar o pysql_lite, desde o mais simples até o mais avançado.

## 📋 Exemplos Disponíveis

### 1. 🟢 Simple Example (`simple_example.py`)

**Nível**: Iniciante | **Tempo**: 5 minutos

Demonstra 10 operações CRUD básicas:
- ✅ Definição de modelos
- ✅ Inserção de dados (INSERT)
- ✅ Busca de todos os registros (SELECT ALL)
- ✅ Filtros simples e avançados (WHERE)
- ✅ Query Chaining com QuerySet
- ✅ Busca por ID
- ✅ Busca um único registro
- ✅ Atualização de dados (UPDATE)
- ✅ Contagem de registros
- ✅ Deleção de dados (DELETE)

**Como executar:**
```bash
cd pysql_lite
python examples/simple_example.py
```

---

### 2. 🟡 Blog Example (`blog_example.py`)

**Nível**: Intermediário | **Tempo**: 10 minutos

Demonstra um sistema de blog completo:
- ✅ Múltiplos modelos (Author, BlogPost, Comment, Tag)
- ✅ Serviço de negócio (BlogService)
- ✅ Relacionamentos entre tabelas
- ✅ Operações CRUD complexas
- ✅ Lógica de negócios (publicação, comentários)
- ✅ Queries e filtros avançados
- ✅ Manipulação de datas
- ✅ Agregações e contagens

**Como executar:**
```bash
cd pysql_lite
python examples/blog_example.py
```

---

### 3. 🔴 Advanced Example (`advanced_example.py`)

**Nível**: Avançado | **Tempo**: 15 minutos

Demonstra funcionalidades avançadas (v1.2+):
- ✅ QuerySet com Query Chaining
- ✅ Lazy Loading
- ✅ Operadores avançados de filtro (11 tipos)
- ✅ Related Lookups (acesso relacionado)
- ✅ order_by(), limit(), count()
- ✅ Iteração e indexação de QuerySet
- ✅ Representação melhorada (__repr__)
- ✅ Exemplos práticos de cada feature

**Como executar:**
```bash
cd pysql_lite
python examples/advanced_example.py
```

---

## 🚀 Como Executar

### Executar um exemplo específico:

```bash
cd pysql_lite
python examples/simple_example.py
python examples/blog_example.py
python examples/advanced_example.py
```

### Executar todos os exemplos:

```bash
cd pysql_lite
python examples/simple_example.py && python examples/blog_example.py && python examples/advanced_example.py
```

---

## 📚 Sugestão de Ordem de Aprendizado

### 1️⃣ **Comece com Simple Example**
   - Entenda os conceitos básicos
   - Aprenda CRUD operations
   - Experimente modificar o código

### 2️⃣ **Passe para Blog Example**
   - Veja como organizar código real
   - Trabalhe com múltiplos modelos
   - Implemente lógica de negócios

### 3️⃣ **Aprenda Advanced Features**
   - Domine Query Chaining
   - Use Related Lookups
   - Otimize suas queries

---

## 💡 Ideias para Experimentar

### Depois de Simple Example:

```python
# Tente diferentes filtros
usuarios = Usuario.query.filter(age__lte=30).all()
usuarios = Usuario.query.filter(name__startswith='A').all()

# Experimente order_by e limit
usuarios = Usuario.query.order_by('age', 'DESC').limit(5).all()

# Use count()
total_ativos = Usuario.query.filter(is_active=True).count()
```

### Depois de Blog Example:

```python
# Crie suas próprias classes
class Produto(Model):
    _table_name = "produtos"
    id = Field(FieldType.INTEGER, primary_key=True)
    nome = Field(FieldType.TEXT, nullable=False)
    preco = Field(FieldType.REAL)

class Categoria(Model):
    _table_name = "categorias"
    id = Field(FieldType.INTEGER, primary_key=True)
    nome = Field(FieldType.TEXT)
```

### Depois de Advanced Example:

```python
# Use QuerySet em aplicações reais
posts = (BlogPost.query
    .filter(is_published=True)
    .filter(views__gt=100)
    .filter(author__ne='Admin')
    .order_by('views', 'DESC')
    .limit(10)
    .all())

# Use first() e count()
primeiro = BlogPost.query.order_by('published_at', 'DESC').first()
total = BlogPost.query.filter(is_published=True).count()

# Itere sobre QuerySet
for post in BlogPost.query.filter(is_published=True):
    print(post)
```

---

## 🔍 Exercícios Propostos

### ✏️ Nível 1: Modificar Simple Example

1. Adicione um novo campo ao modelo `User` (ex: `phone`, `city`)
2. Insira um usuário com o novo campo
3. Filtre usuários por este novo campo
4. Modifique o exemplo para mostra os novos dados

### ✏️ Nível 2: Estender Blog Example

1. Adicione um modelo `Categoria` para posts
2. Crie relacionamentos entre Post e Categoria
3. Implemente método para contar posts por categoria
4. Filtre posts por categoria

### ✏️ Nível 3: Criar Seu Próprio Exemplo

Crie um modelo para um domínio que você conhece:

**Opções**:
- 📚 Sistema de Biblioteca (Livro, Autor, Empréstimo)
- 🏪 Sistema de Loja (Produto, Categoria, Venda)
- 🏋️ Sistema de Academia (Aluno, Plano, Pagamento)
- 🎓 Sistema de Escola (Aluno, Turma, Disciplina)

Implemente:
- CRUD completo
- Múltiplos modelos
- Relacionamentos
- QuerySet complexo

---

## 🐛 Troubleshooting

### Erro: "No module named 'database'"

**Solução**: Execute do diretório correto:

```bash
cd pysql_lite
python examples/simple_example.py
```

### Erro: "Table already exists"

**Solução**: O exemplo usa `:memory:`, nenhum arquivo será criado. Se quiser limpar:

```bash
rm -f *.db *.sqlite *.sqlite3
```

### Erro: UnicodeEncodeError (Windows)

**Solução**: No PowerShell, execute:

```powershell
$env:PYTHONIOENCODING="utf-8"
python examples/simple_example.py
```

### Erro: Permission denied

**Solução**: Verifique permissões:

```bash
chmod +x examples/*.py  # Linux/Mac
```

---

## 📖 Documentação Relacionada

- [README Principal](../README.md) - Visão geral do projeto
- [Guia de Modelos](../docs/DEFINING_MODELS.md) - Como definir modelos
- [Guia de QuerySet](../docs/QUERYSET_GUIDE.md) - Query Chaining avançado
- [Documentação Completa](../docs/README.md) - Todos os guias

---

**Divirta-se explorando pysql_lite!** 🎉

Para dúvidas ou sugestões, [abra uma issue](https://github.com/VictorSilvaVS/pysql_lite/issues)!

**Saída esperada:**
```
======================================================================
PYSQL_LITE - Sistema de Blog
======================================================================

[1] Criando autores...
  ✓ Autor criado: @alice_dev
  ...
```

---

## 🎯 Padrões Demonstrados

### Exemplo 1: Simple Example
Demonstra o padrão básico para qualquer aplicação:

```python
# 1. Definir modelo
class Model(Model):
    _table_name = "table"
    _fields = { ... }

# 2. Conectar
db = Database(":memory:")
Model.set_database(db)

# 3. Usar CRUD
obj = Model(...)
obj.save()
Model.find_all()
obj.delete()
```

### Exemplo 2: Blog Example
Demonstra um padrão mais sofisticado:

```python
# 1. Definir múltiplos modelos
class Author(Model): ...
class BlogPost(Model): ...
class Comment(Model): ...

# 2. Criar serviço
class BlogService:
    @staticmethod
    def create_post(...): ...
    @staticmethod
    def get_post_comments(...): ...

# 3. Usar serviço
BlogService.create_post(...)
BlogService.get_post_comments(...)
```

---

## 🚀 Como Usar Estes Exemplos

### Opção 1: Executar direto
```bash
cd pysql_lite
python examples/simple_example.py
python examples/blog_example.py
```

### Opção 2: Importar e modificar
```python
import sys
sys.path.insert(0, '..')

from database import Database, Model, Field, FieldType

# Seu código aqui
class MyModel(Model):
    ...
```

### Opção 3: Estudar o código
Cada exemplo está bem comentado. Leia o código para entender:
- Como estruturar modelos
- Como conectar ao banco
- Como fazer operações CRUD
- Como manipular dados

---

## 💡 Casos de Uso Reais

Estes exemplos demonstram como resolver problemas reais:

### Simple Example - Aplicação de Usuários
**Problema**: Gerenciar usuários e posts  
**Solução**: Dois modelos simples com CRUD  
**Aprendizado**: Básicos de ORM

### Blog Example - Sistema de Blog Completo
**Problema**: Sistema com múltiplas entidades e relacionamentos  
**Solução**: Múltiplos modelos + Serviço de negócio  
**Aprendizado**: Arquitetura, relacionamentos, queries

---

## 🎓 O Que Você Aprende

### Conceitos de ORM
- Mapeamento objeto-relacional
- Operações CRUD
- Queries e filtros
- Relacionamentos

### Padrões de Design
- Model-Service pattern
- Singleton pattern
- Factory pattern
- Repository pattern

### Boas Práticas Python
- Type hints
- Docstrings
- Estrutura de projetos
- Tratamento de erros

---

## ✏️ Modificar os Exemplos

### Adicionar um novo modelo ao simple_example

```python
class Comment(Model):
    _table_name = "comments"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "post_id": Field(FieldType.INTEGER),
        "author": Field(FieldType.TEXT),
        "text": Field(FieldType.TEXT),
    }

Comment.set_database(db)

# Usar
comment = Comment(post_id=1, author="Bob", text="Great post!")
comment.save()
```

### Estender o BlogService

```python
class BlogService:
    # ... métodos existentes ...
    
    @staticmethod
    def get_author_comments(author: str):
        """Todos os comentários de um autor"""
        return Comment.filter(author=author, is_approved=True)
    
    @staticmethod
    def publish_all_posts():
        """Publicar todos os posts"""
        for post in BlogPost.find_all():
            BlogService.publish_post(post.id)
```

---

## 🔧 Debugging

Se encontrar problemas, tente:

1. **Verificar a estrutura do banco**
   ```python
   cursor = db.execute("SELECT sql FROM sqlite_master WHERE type='table'")
   for row in cursor.fetchall():
       print(row['sql'])
   ```

2. **Logar queries SQL**
   ```python
   def trace(statement, bindings):
       print(f"SQL: {statement} | Params: {bindings}")
   
   db.connection.set_trace(trace)
   ```

3. **Verificar dados inseridos**
   ```python
   users = User.find_all()
   for user in users:
       print(user)
   ```

---

## 📖 Próximos Passos

Depois de estudar estes exemplos, tente:

1. **Criar seu próprio modelo**
   - Um aplicativo de tarefas (TODO)
   - Uma loja online simples
   - Um diário pessoal

2. **Adicionar funcionalidades**
   - Validadores customizados
   - Hooks de ciclo de vida
   - Queries mais complexas

3. **Estudar o core**
   - Leia `database.py`
   - Entenda como funciona
   - Estenda com novas features

---

## 🤝 Contribuir

Se você criar exemplos úteis, considere contribuir!

1. Crie um novo arquivo em `examples/`
2. Adicione comentários explicativos
3. Documente o objetivo
4. Envie um PR

---

**Happy coding! 🚀**
