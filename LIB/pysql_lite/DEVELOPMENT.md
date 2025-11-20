# Desenvolvimento e Manutenção do pysql_lite

## 📁 Estrutura do Projeto

```
pysql_lite/
├── __init__.py              # Exportações principais
├── database.py              # Core da ORM (main file)
├── setup.py                 # Configuração para pip install
├── pyproject.toml           # Configuração moderna (PEP 517)
├── LICENSE                  # MIT License
├── README.md                # Documentação completa
├── QUICK_START.md          # Guia rápido de início
├── DEVELOPMENT.md          # Este arquivo
├── examples/
│   ├── simple_example.py    # Exemplo básico de uso
│   └── blog_example.py      # Exemplo de sistema de blog
└── tests/
    ├── __init__.py
    └── test_database.py     # Suite de 24 testes unitários
```

## 🧪 Testando

### Executar todos os testes
```bash
python tests/test_database.py
```

### Resultado esperado
```
Ran 24 tests in 0.008s
OK
```

### Cobertura de testes
- **TestField**: Testes de definição de campos (4 testes)
- **TestDatabase**: Testes de conexão e gerenciamento (3 testes)
- **TestModel**: Testes de CRUD e operações (17 testes)
- **TestIntegration**: Testes de fluxo completo (1 teste)

## 🚀 Exemplos de Uso

### Executar exemplo simples
```bash
python examples/simple_example.py
```

### Executar exemplo do blog
```bash
python examples/blog_example.py
```

## 🏗️ Arquitetura da ORM

### Camadas

```
┌─────────────────────────────────────────────────┐
│           Aplicação do Usuário                  │
├─────────────────────────────────────────────────┤
│           Model Classes (Usuário, Post, etc)    │
├─────────────────────────────────────────────────┤
│    Model Base Class (CRUD Operations)           │
├─────────────────────────────────────────────────┤
│    Database (Connection Management)             │
├─────────────────────────────────────────────────┤
│    sqlite3 Library (SQLite Driver)              │
└─────────────────────────────────────────────────┘
```

### Classes Principais

#### FieldType (Enum)
Define tipos de dados suportados:
- INTEGER
- TEXT
- REAL
- BOOLEAN (armazenado como INTEGER)
- DATETIME (armazenado como TEXT em ISO format)
- BLOB

#### Field
Representa um campo na tabela:
- `field_type`: Tipo do campo
- `primary_key`: Se é chave primária
- `nullable`: Se pode ser NULL
- `unique`: Se deve ser único
- `default`: Valor padrão

#### Database
Gerencia conexões SQLite:
- Singleton pattern (uma instância por aplicação)
- `execute()`: Executar queries
- `commit()`: Confirmar transação
- `create_table()`: Criar tabela
- `close()`: Fechar conexão

#### Model
Classe base para modelos:
- CRUD: `save()`, `find_all()`, `filter()`, `delete()`
- Queries: `find_by_id()`, `find_one()`, `count()`
- Conversão: `to_dict()`, `_from_row()`

## 📝 Adicionando Novos Tipos de Campo

Para adicionar um novo tipo de campo:

1. Adicionar ao `FieldType` enum:
```python
class FieldType(Enum):
    NOVO_TIPO = "SQL_TYPE"
```

2. Adicionar mapeamento em `Field.get_sql_definition()`:
```python
type_map = {
    # ...
    FieldType.NOVO_TIPO: "SQL_TYPE",
}
```

3. Adicionar conversão em `Model._from_row()` se necessário:
```python
elif field.field_type == FieldType.NOVO_TIPO:
    data[field_name] = convert_from_db(value)
```

4. Adicionar conversão em `Model.save()` se necessário:
```python
if isinstance(value, CustomType):
    values.append(convert_to_db(value))
```

5. Adicionar testes em `tests/test_database.py`

## 🔧 Estendendo a ORM

### Adicionar um método de query mais complexo

```python
@classmethod
def filter_advanced(cls, **kwargs):
    """Exemplo de filtro mais complexo"""
    # Construir query dinamicamente
    # Executar com cls._database.execute()
    # Converter resultados com cls._from_row()
    pass
```

### Adicionar validação de campo

```python
def validate(self):
    """Validar instância antes de salvar"""
    for field_name, field in self._fields.items():
        value = getattr(self, field_name)
        if field.nullable is False and value is None:
            raise ValueError(f"{field_name} não pode ser NULL")
```

### Adicionar hooks de ciclo de vida

```python
def before_save(self):
    """Executado antes de salvar"""
    pass

def after_save(self):
    """Executado após salvar"""
    pass

def before_delete(self):
    """Executado antes de deletar"""
    pass

def after_delete(self):
    """Executado após deletar"""
    pass
```

## 📊 Métricas de Performance

Testes executados em :memory: database:

- **24 testes**: ~8ms
- **Média por teste**: ~0.33ms
- **Operações por segundo**: ~3000

Nota: Performance real depende do hardware e tamanho do banco de dados.

## 🐛 Debugging

### Habilitar SQL logging

```python
import sqlite3

def trace_sql(statement, bindings):
    print(f"SQL: {statement}")
    print(f"Params: {bindings}")
    return statement

db.connection.set_trace(trace_sql)
```

### Inspecionar esquema

```python
cursor = db.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(row['sql'])
```

## 📚 Referências SQLite

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Data Types](https://www.sqlite.org/datatype3.html)
- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)

## 🔐 Segurança

### SQL Injection Prevention
Todos os parâmetros são passados via placeholders `?`, protegendo contra SQL injection:

```python
# ✅ Seguro
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))

# ❌ Inseguro
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
```

## 🤝 Contribuindo

1. Fazer fork do repositório
2. Criar uma branch para a feature (`git checkout -b feature/AmazingFeature`)
3. Commit das mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

### Checklist antes de submeter PR

- [ ] Código segue o estilo do projeto
- [ ] Todos os testes passam
- [ ] Adicionados testes para nova funcionalidade
- [ ] Documentação atualizada
- [ ] Sem breaking changes

## 📋 Versioning

Segue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: Novas funcionalidades (retrocompatível)
- **PATCH**: Bug fixes

Versão atual: 1.0.0 (Beta)

## 🗓️ Roadmap

### v1.1.0 (próximo)
- [ ] Relações (OneToMany, ManyToMany)
- [ ] Validadores de campo
- [ ] Migrations básicas
- [ ] Índices

### v1.2.0
- [ ] Suporte a transactions
- [ ] Suporte a views
- [ ] Query builder mais avançado
- [ ] Caching simples

### v2.0.0
- [ ] Suporte a múltiplos bancos de dados
- [ ] ORM totalmente assíncrono
- [ ] GraphQL support

---

**Última atualização**: Novembro 2025
**Mantido por**: Victor Silva
