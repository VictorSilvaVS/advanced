# Testes - pysql_lite

Este diretório contém todos os testes unitários do pysql_lite.

## 📊 Cobertura de Testes

- **Total de Testes**: 37
- **Taxa de Aprovação**: 100% ✅
- **Tempo de Execução**: ~13ms
- **Cobertura**: Todas as funcionalidades principais

## 🧪 Estrutura de Testes

### test_database.py

O arquivo principal com 37 testes organizados em 5 classes:

#### 1. TestField (4 testes)
Testa a classe `Field` e suas funcionalidades:
- ✅ Criação de um campo
- ✅ Campo com chave primária
- ✅ Geração de definição SQL
- ✅ Campo com valor padrão

#### 2. TestDatabase (3 testes)
Testa a classe `Database`:
- ✅ Conexão com banco de dados
- ✅ Padrão Singleton
- ✅ Execução de query

#### 3. TestModel (16 testes)
Testa a classe `Model` e CRUD operations:
- ✅ Criação de instância
- ✅ Inserção de registro
- ✅ Atualização de registro
- ✅ Busca de todos os registros
- ✅ Busca por ID
- ✅ Busca de um registro específico
- ✅ Filtro de registros
- ✅ Contagem de registros
- ✅ Deleção de registro
- ✅ Deleção por ID
- ✅ Deleção de todos os registros
- ✅ Campo booleano
- ✅ Campo de data/hora
- ✅ Valores padrão
- ✅ Conversão para dicionário
- ✅ Fluxo completo (CRUD)

#### 4. TestQuerySet (12 testes) 🆕
Testa a nova classe `QuerySet` e Query Chaining:
- ✅ Obtenção de todos os registros
- ✅ Filtro com QuerySet
- ✅ Ordenação (ASC)
- ✅ Ordenação (DESC)
- ✅ Limite de registros
- ✅ Primeiro registro
- ✅ Contagem de registros
- ✅ Encadeamento completo
- ✅ Iteração
- ✅ len()
- ✅ Indexação
- ✅ Getitem

#### 5. TestModelRepresentation (2 testes) 🆕
Testa a representação melhorada:
- ✅ __repr__ para instância nova
- ✅ __repr__ para instância salva

---

## 🚀 Como Executar os Testes

### Executar todos os testes:

```bash
cd pysql_lite
python tests/test_database.py
```

### Executar com verbosidade:

```bash
cd pysql_lite
python tests/test_database.py -v
```

### Executar uma classe de testes específica:

```bash
cd pysql_lite
python -m unittest tests.test_database.TestQuerySet -v
```

### Executar um teste específico:

```bash
cd pysql_lite
python -m unittest tests.test_database.TestQuerySet.test_queryset_chaining -v
```

---

## ✅ Resultado Esperado

```
test_connection (__main__.TestDatabase.test_connection)
Testa conexão com banco de dados ... ok
test_singleton (__main__.TestDatabase.test_singleton)
Testa padrão singleton ... ok
...
Ran 37 tests in 0.013s

OK
```

---

## 📝 Como Adicionar Novos Testes

### 1. Estrutura Básica

```python
import unittest
from database import Database, Model, Field, FieldType

class TestMeuModulo(unittest.TestCase):
    
    def setUp(self):
        """Executado antes de cada teste"""
        self.db = Database(":memory:")
        # Configurar dados de teste
    
    def tearDown(self):
        """Executado após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_minha_feature(self):
        """Testa uma feature específica"""
        # Arrange (preparar)
        usuario = User(name="Test", email="test@example.com")
        
        # Act (agir)
        usuario_id = usuario.save()
        
        # Assert (verificar)
        self.assertIsNotNone(usuario_id)
```

### 2. Adicionar ao final de test_database.py:

```python
class TestMeuModulo(unittest.TestCase):
    # ... seu código
    pass

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

### 3. Rodas os testes:

```bash
python tests/test_database.py
```

---

## 🔍 Boas Práticas de Teste

### 1. Use o padrão AAA

- **Arrange**: Preparar dados
- **Act**: Executar a ação
- **Assert**: Verificar resultado

### 2. Nomes descritivos

```python
# ❌ Ruim
def test_1(self):
    pass

# ✅ Bom
def test_queryset_filter_with_multiple_conditions(self):
    pass
```

### 3. Teste um conceito por teste

```python
# ❌ Ruim - Testa muitas coisas
def test_model(self):
    user = User(name="Test")
    user.save()
    found = User.find_by_id(1)
    found.age = 30
    found.save()
    User.delete_all()

# ✅ Bom - Testa uma coisa
def test_model_save_insert(self):
    user = User(name="Test", email="test@example.com")
    user_id = user.save()
    self.assertIsNotNone(user_id)
```

### 4. Use setUp e tearDown

```python
def setUp(self):
    """Executado antes de cada teste"""
    self.db = Database(":memory:")
    User.set_database(self.db)

def tearDown(self):
    """Executado após cada teste"""
    self.db.close()
    Database._instance = None
```

---

## 📊 Cobertura por Feature

| Feature | Status | Testes |
|---------|--------|--------|
| Field | ✅ | 4 |
| Database | ✅ | 3 |
| CRUD Operations | ✅ | 10 |
| Advanced Filters | ✅ | 3 |
| QuerySet | ✅ | 12 |
| Representação | ✅ | 2 |
| **TOTAL** | **✅** | **37** |

---

## 🎯 Checklist de Teste

Antes de fazer commit/PR, verifique:

- [ ] Todos os testes passam: `python tests/test_database.py`
- [ ] Nenhum aviso/erro
- [ ] Novos testes para novas features
- [ ] Cobertura de casos especiais
- [ ] Dados de teste limpos após cada teste

---

## 🔗 Documentação Relacionada

- [README Principal](../README.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Diretrizes de contribuição
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Desenvolvimento

---

**Obrigado por contribuir com testes!** 🙏
