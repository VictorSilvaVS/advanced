# Definindo Models com pysql_lite v1.2.0

## Nova Sintaxe (v1.2.0) - Fields como Atributos de Classe

A forma recomendada de definir Models é usando Fields como atributos de classe:

```python
from database import Database, Model, Field, FieldType
from datetime import datetime

class User(Model):
    """Modelo de usuário com nova sintaxe"""
    _table_name = "users"
    
    # Defina os campos como atributos de classe
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT, nullable=False, unique=True)
    age = Field(FieldType.INTEGER)
    is_active = Field(FieldType.BOOLEAN, default=True)
    created_at = Field(FieldType.DATETIME)
```

### Por que esta sintaxe?

✅ **Mais intuitiva** - Fields são declarados onde são usados  
✅ **Mais pythônica** - Segue padrões do Django ORM e SQLAlchemy  
✅ **Autocompletar** - IDEs conseguem oferecer sugestões melhor  
✅ **Validação automática** - Apenas uma chave primária por modelo  

## Tipos de Campo (FieldType)

### INTEGER

```python
age = Field(FieldType.INTEGER)
quantity = Field(FieldType.INTEGER, default=0)
views = Field(FieldType.INTEGER, nullable=True)
```

### TEXT

```python
name = Field(FieldType.TEXT, nullable=False)
email = Field(FieldType.TEXT, unique=True)
bio = Field(FieldType.TEXT)
```

### REAL

```python
price = Field(FieldType.REAL)
rating = Field(FieldType.REAL)
percentage = Field(FieldType.REAL, default=0.0)
```

### BOOLEAN

Armazenado como INTEGER (0 ou 1) no SQLite, mas convertido automaticamente:

```python
is_active = Field(FieldType.BOOLEAN, default=True)
is_premium = Field(FieldType.BOOLEAN, default=False)
is_deleted = Field(FieldType.BOOLEAN)
```

### DATETIME

Armazenado como TEXT em formato ISO no SQLite, convertido automaticamente:

```python
created_at = Field(FieldType.DATETIME)
updated_at = Field(FieldType.DATETIME)
published_at = Field(FieldType.DATETIME, nullable=True)
```

### BLOB

Para dados binários:

```python
avatar = Field(FieldType.BLOB)
file_data = Field(FieldType.BLOB, nullable=True)
```

## Constraints (Restrições)

### Primary Key (Chave Primária)

```python
class User(Model):
    _table_name = "users"
    
    id = Field(FieldType.INTEGER, primary_key=True)  # Auto-incrementado
    # ... outros campos
```

**Notas**:
- Apenas uma chave primária por modelo (validado automaticamente)
- Auto-incremento é ativado automaticamente
- Se não houver PK definida, uma será criada automaticamente

### Unique (Valor Único)

```python
email = Field(FieldType.TEXT, unique=True)
username = Field(FieldType.TEXT, unique=True)
```

### Nullable

```python
# Permite valores NULL no banco (padrão)
bio = Field(FieldType.TEXT)

# Não permite valores NULL
name = Field(FieldType.TEXT, nullable=False)

# Explicitamente permitindo NULL
age = Field(FieldType.INTEGER, nullable=True)
```

### Default (Valor Padrão)

```python
is_active = Field(FieldType.BOOLEAN, default=True)
role = Field(FieldType.TEXT, default="user")
created_count = Field(FieldType.INTEGER, default=0)
```

## Foreign Key (Chave Estrangeira)

### Definir uma FK simples

```python
from database import ForeignKey

class Post(Model):
    _table_name = "posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    user_id = Field(FieldType.INTEGER)  # FK para User
    title = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT)
```

### Com Constraint de FK (v1.1+)

```python
class Post(Model):
    _table_name = "posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    user_id = Field(
        FieldType.INTEGER,
        foreign_key=ForeignKey(User, on_delete="CASCADE")
    )
    title = Field(FieldType.TEXT, nullable=False)
```

### Opções de ON DELETE

- `CASCADE` - Deleta relacionados (padrão)
- `SET NULL` - Define NULL nos relacionados
- `RESTRICT` - Impede deleção se houver relacionados

## Exemplo Completo

```python
from database import Database, Model, Field, FieldType, ForeignKey
from datetime import datetime

# Definir modelos
class Author(Model):
    _table_name = "authors"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT, unique=True)
    bio = Field(FieldType.TEXT)
    is_verified = Field(FieldType.BOOLEAN, default=False)
    created_at = Field(FieldType.DATETIME)


class BlogPost(Model):
    _table_name = "blog_posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    author_id = Field(
        FieldType.INTEGER,
        foreign_key=ForeignKey(Author, on_delete="CASCADE")
    )
    title = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT, nullable=False)
    is_published = Field(FieldType.BOOLEAN, default=False)
    views = Field(FieldType.INTEGER, default=0)
    created_at = Field(FieldType.DATETIME)
    updated_at = Field(FieldType.DATETIME)


class Comment(Model):
    _table_name = "comments"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    post_id = Field(FieldType.INTEGER)
    author_name = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT, nullable=False)
    is_approved = Field(FieldType.BOOLEAN, default=False)
    created_at = Field(FieldType.DATETIME)


# Conectar ao banco
db = Database("blog.db")

# Registrar modelos
Author.set_database(db)
BlogPost.set_database(db)
Comment.set_database(db)

# Registrar relacionamentos
Author.register_related('posts', BlogPost, 'author_id')
BlogPost.register_related('comments', Comment, 'post_id')

# Usar os modelos
author = Author(
    name="Alice Silva",
    email="alice@example.com",
    bio="Escritora e desenvolvedora",
    is_verified=True,
    created_at=datetime.now()
)
author_id = author.save()

post = BlogPost(
    author_id=author_id,
    title="Introdução ao ORM",
    content="...",
    is_published=True,
    created_at=datetime.now()
)
post.save()

# Usar QuerySet com Query Chaining
posts = (Author.query
    .filter(is_verified=True)
    .all())

# Acessar relacionados
author = Author.find_by_id(author_id)
author_posts = author.posts.all()  # Retorna QuerySet dos posts
published_posts = author.posts.filter(is_published=True).all()
```

## Validações Automáticas

✅ **Chave primária única** - Apenas uma por modelo  
✅ **Chaves primárias auto-incrementadas** - Geradas automaticamente  
✅ **Tipos de campo validados** - Apenas 6 tipos válidos  
✅ **Constraints respeitados** - NOT NULL, UNIQUE, DEFAULT  

## Boas Práticas

1. **Sempre defina `_table_name`** para evitar confusões
2. **Use nomes descritivos** para campos e modelos
3. **Defina chaves primárias** explicitamente
4. **Use `nullable=False`** para campos obrigatórios
5. **Registre relacionamentos** para acesso reverso
6. **Use QuerySet** para queries complexas
