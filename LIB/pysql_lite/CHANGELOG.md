# Changelog - pysql_lite

## v1.2.0 - Query Chaining e Related Lookups (2025-11-20)

### Novas Funcionalidades ✨

#### 1. QuerySet com Query Chaining
- **Classe QuerySet**: Nova classe que implementa Lazy Loading e encadeamento de filtros
- **Property `query`**: Acesso via `Model.query` para construir queries complexas
- **Métodos de Encadeamento**:
  - `.filter(**kwargs)` - Adicionar filtros (AND logic)
  - `.order_by(field, direction)` - Ordenar resultados
  - `.limit(count)` - Limitar número de registros
  - `.all()` - Executar e retornar todos os resultados
  - `.first()` - Executar e retornar primeiro resultado
  - `.count()` - Contar registros

**Exemplo**:
```python
usuarios = Usuario.query.filter(age__gt=25).order_by('nome').limit(10).all()
```

#### 2. Acesso Relacionado (Related Lookups)
- **Classe RelatedManager**: Descriptor para acesso reverso entre modelos
- **Método `register_related()`**: Registrar relacionamentos entre modelos
- **Sintaxe**: `instancia.related_name.all()` ou `instancia.related_name.first()`

**Exemplo**:
```python
User.register_related('posts', Post, 'user_id')
usuario = User.find_by_id(1)
posts = usuario.posts.all()  # Retorna QuerySet dos posts do usuário
```

#### 3. Representação Melhorada (__repr__)
- **Antes**: `User({'id': 1, 'name': 'Alice', 'email': 'alice@example.com', ...})`
- **Depois**: `<User pk=1 email='alice@example.com'>`
- Mostra apenas classe, pk e primeiro campo de texto
- Mais legível e conciso

#### 4. Método Auxiliar `_get_pk_field_name()`
- Retorna o nome do campo primary key do modelo
- Útil para uso interno e extensões

### Melhorias 📈

#### Query Operators Expandidos
- `__eq`: Igualdade (padrão)
- `__gt`: Maior que (>)
- `__gte`: Maior ou igual (>=)
- `__lt`: Menor que (<)
- `__lte`: Menor ou igual (<=)
- `__ne`: Não igual (!=)
- `__like`: LIKE pattern
- `__contains`: Contém substring (LIKE %valor%)
- `__startswith`: Começa com (LIKE valor%)
- `__endswith`: Termina com (LIKE %valor)
- `__in`: IN (valor1, valor2, ...)

#### Operações de QuerySet
- Suporte a `len(qs)` - Retorna quantidade de registros
- Suporte a `for item in qs` - Iteração com lazy loading
- Suporte a `qs[index]` - Indexação
- Suporte a `qs[start:end]` - Slicing

### Mudanças Internas 🔧

#### Novas Classes
- `QuerySet`: Representa uma consulta construível
- `QueryProperty`: Descriptor para acessar query como propriedade
- `RelatedManager`: Descriptor para acesso relacionado reverso

#### Alterações na Classe Model
- Adição de propriedade `query` via descriptor
- Novo método `_get_pk_field_name()`
- Novo método `register_related()`
- __repr__ completamente reescrito

### Testes Adicionados ✅

- 12 novos testes para QuerySet
  - Filtros básicos e avançados
  - Ordenação ascendente e descendente
  - Limite de registros
  - first(), count(), len()
  - Iteração e indexação
  - Encadeamento completo
- 2 novos testes para representação (__repr__)
- **Total**: 37 testes (24 anteriores + 13 novos)
- **Status**: 100% passing

### Exemplos Adicionados 📚

- **advanced_example.py**: Novo exemplo completo demonstrando:
  - Básicos de QuerySet
  - Query Chaining
  - Operadores avançados
  - Operações com QuerySet (len, indexação)
  - Acesso relacionado
  - Representação melhorada

### Documentação 📖

- **QUERYSET_GUIDE.md**: Guia completo sobre QuerySet e Query Chaining
- Exemplos práticos de uso
- Dicas de performance
- Comparação de padrões bons e ruins

### Breaking Changes ⚠️

**Nenhum breaking change**. Todas as funcionalidades anteriores continuam funcionando:
- `.filter()` como método direto no Model ainda funciona
- `.find_all()`, `.find_by_id()`, `.find_one()` continuam disponíveis
- Sintaxe dos Models permanece compatível

### Backward Compatibility ✔️

- 100% compatível com código v1.1.0
- Novos recursos são aditivos
- Métodos existentes mantêm mesma assinatura

### Exemplo de Migração (Opcional)

```python
# v1.1.0 - Ainda funciona
usuarios = Usuario.filter(age__gt=25)

# v1.2.0 - Alternativa com mais poder
usuarios = Usuario.query.filter(age__gt=25).order_by('name').limit(10).all()
```

### Estatísticas do Release 📊

| Métrica | Valor |
|---------|-------|
| Novas Classes | 3 |
| Novos Métodos | 5+ |
| Novos Operadores | 9 |
| Testes Adicionados | 13 |
| Total de Testes | 37 |
| Exemplos | 3 (1 novo) |
| Documentação Nova | 1 guia |
| Linhas de Código Adicionadas | ~400 |

---

## v1.1.0 - Field Extraction e Advanced Filters (2025-11-20)

### Novas Funcionalidades
- Extração automática de Fields como atributos de classe
- Validação de chave primária única
- Classe ForeignKey para relacionamentos
- Operadores de filtro avançados (__gt, __lt, __in, __like, etc)

### Melhorias
- Nova sintaxe para definição de Models (Fields como atributos)
- Exemplo do blog atualizado
- Testes expandidos

---

## v1.0.0 - Initial Release (2025-11-20)

### Funcionalidades Core
- Abstração simples de SQLite
- CRUD operations (create, read, update, delete)
- 6 tipos de campo (INTEGER, TEXT, REAL, BOOLEAN, DATETIME, BLOB)
- Constraints (PK, FK, Unique, Nullable, Default)
- Type conversion automática
- Singleton Database connection
- Transaction support
- 24 testes unitários
- 2 exemplos práticos
- Documentação abrangente
