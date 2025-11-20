# QuerySet e Query Chaining - Guia de Uso

## O que é QuerySet?

`QuerySet` é um objeto que representa uma consulta ao banco de dados. Ele implementa **Lazy Loading** (carregamento preguiçoso), o que significa que a consulta SQL apenas é executada quando você tenta acessar os resultados.

## Query Chaining (Encadeamento)

Query Chaining permite construir consultas complexas encadeando múltiplos métodos. Cada método retorna o próprio QuerySet, permitindo continuar a construção da consulta.

### Sintaxe Básica

```python
# Usando o property 'query' do Model
usuarios = Usuario.query.filter(idade__gt=25).order_by('nome').limit(10).all()
```

## Métodos do QuerySet

### 1. `filter(**kwargs)` - Adicionar Filtros

Adiciona condições WHERE ao query. Suporta múltiplos operadores.

```python
# Filtro simples
Usuario.query.filter(is_active=True).all()

# Múltiplos filtros (AND logic)
Usuario.query.filter(age__gt=25, is_active=True).all()

# Operadores avançados
Usuario.query.filter(idade__gt=25).all()           # idade > 25
Usuario.query.filter(idade__gte=25).all()          # idade >= 25
Usuario.query.filter(idade__lt=25).all()           # idade < 25
Usuario.query.filter(idade__lte=25).all()          # idade <= 25
Usuario.query.filter(idade__ne=25).all()           # idade != 25
Usuario.query.filter(nome__like='A%').all()        # LIKE pattern
Usuario.query.filter(email__contains='gmail').all() # LIKE %gmail%
Usuario.query.filter(nome__startswith='Alice').all() # LIKE Alice%
Usuario.query.filter(nome__endswith='Silva').all()  # LIKE %Silva
Usuario.query.filter(id__in=[1, 2, 3]).all()       # IN (1, 2, 3)
```

### 2. `order_by(field_name, direction='ASC')` - Ordenação

Adiciona ORDER BY ao query.

```python
# Ordem crescente (ASC é default)
Usuario.query.order_by('nome').all()
Usuario.query.order_by('nome', 'ASC').all()

# Ordem decrescente
Usuario.query.order_by('idade', 'DESC').all()

# Múltiplas ordenações (encadeando)
Usuario.query.order_by('ativo', 'ASC').order_by('idade', 'DESC').all()
```

### 3. `limit(count)` - Limitar Registros

Limita o número de registros retornados (LIMIT).

```python
# Retorna apenas os 10 primeiros registros
Usuario.query.limit(10).all()

# Combinado com order_by (Top 5 usuários mais ativos)
Usuario.query.order_by('ativo', 'DESC').limit(5).all()
```

### 4. `all()` - Executar e Retornar Todos

Executa o query e retorna uma lista com todos os resultados.

```python
usuarios = Usuario.query.filter(idade__gt=25).all()
# usuarios é uma List[Usuario]
```

### 5. `first()` - Retornar Primeiro Resultado

Executa o query e retorna apenas o primeiro resultado ou None.

```python
primeiro_usuario = Usuario.query.order_by('idade', 'ASC').first()
# primeiro_usuario é User ou None
```

### 6. `count()` - Contar Registros

Executa o query e retorna a quantidade de registros.

```python
quantidade = Usuario.query.filter(is_active=True).count()
# quantidade é int
```

## Lazy Loading

QuerySet implementa **Lazy Loading**, o que significa que a consulta SQL apenas é executada quando necessário:

```python
# Nenhuma consulta SQL é executada aqui
qs = Usuario.query.filter(idade__gt=25).order_by('nome').limit(10)

# SQL é executado apenas aqui (ao chamar .all())
usuarios = qs.all()
```

## Iteração sobre QuerySet

Você pode iterar sobre um QuerySet diretamente:

```python
# Iteração (lazy loading - SQL é executado aqui)
for usuario in Usuario.query.filter(is_active=True):
    print(usuario.nome)

# Usando len() (executa SQL)
total = len(Usuario.query.filter(is_active=True))

# Usando indexação (executa SQL)
primeiro = Usuario.query.order_by('nome')[0]
ultimo = Usuario.query.order_by('nome')[-1]

# Slicing (executa SQL)
primeiros_5 = Usuario.query.limit(5)[:]
```

## Exemplos Práticos

### Exemplo 1: Usuários Ativos com Idade Entre 25 e 35

```python
usuarios = (Usuario.query
    .filter(is_active=True)
    .filter(idade__gte=25)
    .filter(idade__lte=35)
    .order_by('nome', 'ASC')
    .all())
```

### Exemplo 2: Top 5 Posts Mais Visualizados

```python
posts_top = (Post.query
    .order_by('views', 'DESC')
    .limit(5)
    .all())
```

### Exemplo 3: Contar Usuários por Status

```python
ativos = Usuario.query.filter(is_active=True).count()
inativos = Usuario.query.filter(is_active=False).count()
```

### Exemplo 4: Primeiro Usuário com Email Gmail

```python
usuario_gmail = (Usuario.query
    .filter(email__contains='gmail')
    .order_by('nome', 'ASC')
    .first())
```

## Acesso Relacionado (Related Lookups)

### O que é?

Acesso relacionado permite navegar entre modelos relacionados de forma intuitiva:

```python
usuario = Usuario.find_by_id(1)
posts = usuario.posts.all()  # Retorna todos os posts do usuário
```

### Como Usar?

1. **Defina o relacionamento** na inicialização:

```python
Usuario.register_related('posts', Post, 'user_id')
```

2. **Acesse os relacionados**:

```python
usuario = Usuario.find_by_id(1)

# Retorna QuerySet com todos os posts relacionados
posts_qs = usuario.posts

# Executa SQL e retorna resultados
posts = usuario.posts.all()

# Usa QuerySet chaining
posts_com_muitas_views = usuario.posts.filter(views__gt=100).order_by('views', 'DESC').all()

# Conta posts do usuário
total_posts = usuario.posts.count()
```

## Representação Melhorada (__repr__)

O método `__repr__` foi melhorado para mostrar uma representação mais concisa:

```python
usuario = Usuario(nome="Alice", email="alice@example.com")
print(repr(usuario))
# Output: <Usuario pk=novo email='alice@example.com'>

usuario.save()  # Assume ID 1
print(repr(usuario))
# Output: <Usuario pk=1 email='alice@example.com'>
```

## Resumo das Operações

| Operação | Método | Resultado |
|----------|--------|-----------|
| Todos os registros | `.all()` | List[Model] |
| Primeiro registro | `.first()` | Model \| None |
| Contar | `.count()` | int |
| Iterar | `for x in qs` | Iterador |
| Tamanho | `len(qs)` | int |
| Indexar | `qs[0]`, `qs[-1]` | Model |
| Fatiar | `qs[1:5]` | List[Model] |

## Performance

### Dicas de Otimização

1. **Use Lazy Loading**: Construa queries complexas antes de executar
2. **Filtre Cedo**: Adicione filtros mais restritivos primeiro
3. **Use limit()**: Para reduzir quantidade de dados retornados
4. **Evite Loops**: Em vez de `for x in Model.find_all()`, use QuerySet com filtros

### Bom ❌

```python
# Retorna TODOS os usuários (pode ser milhões!)
usuarios = Usuario.find_all()
for u in usuarios:
    if u.age > 25 and u.is_active:
        print(u)
```

### Melhor ✅

```python
# Retorna apenas usuários que atendem aos critérios
usuarios = Usuario.query.filter(age__gt=25, is_active=True).all()
for u in usuarios:
    print(u)
```
