# Compatibilidade - pysql_lite

## 🐍 Compatibilidade Python

### Versões Suportadas

| Versão Python | Status | Notas |
|---------------|--------|-------|
| **3.7** | ✅ Suportado | Versão mínima requerida |
| **3.8** | ✅ Suportado | Recomendado |
| **3.9** | ✅ Suportado | Recomendado |
| **3.10** | ✅ Suportado | Recomendado |
| **3.11** | ✅ Suportado | Recomendado |
| **3.12+** | ✅ Suportado | Testado |
| **2.7** | ❌ Não suportado | Fim de vida |
| **3.6** | ❌ Não suportado | Muito antigo |

### Verificar sua Versão Python

```bash
python --version
python -m sys -c "import sys; print(sys.version_info)"
```

## 🖥️ Compatibilidade de Sistema Operacional

| Sistema | Status | Notas |
|---------|--------|-------|
| **Windows** | ✅ Completo | Testado em Windows 10/11 |
| **macOS** | ✅ Completo | Testado em macOS 10.15+ |
| **Linux** | ✅ Completo | Testado em Ubuntu 20.04+ |
| **Raspberry Pi** | ✅ Suportado | Python 3.7+ necessário |

## 📦 Dependências

### Dependências de Produção

```
# NENHUMA
# Apenas biblioteca padrão Python (sqlite3)
```

### Dependências de Desenvolvimento

```
# Para testes
pytest  # Opcional, use unittest padrão

# Para documentação
mkdocs  # Opcional
```

### Compatibilidade de Bibliotecas

Testado com as seguintes versões (quando usadas com pysql_lite):

| Biblioteca | Versão | Compatível | Notas |
|-----------|--------|-----------|-------|
| pytest | 6.0+ | ✅ Sim | Opcional |
| mkdocs | 1.0+ | ✅ Sim | Opcional |
| sqlite3 | stdlib | ✅ Sim | Incluído |

## 🔄 Migração Entre Versões

### v1.0 → v1.1

**Compatibilidade**: Totalmente regressivo compatível
- Todas as APIs v1.0 continuam funcionando
- Novas APIs adicionadas

**Alterações**:
```python
# v1.0
class User(Model):
    name = Field(FieldType.TEXT)

# v1.1+ (ambas funcionam)
class User(Model):
    name = Field(FieldType.TEXT)
    # Extração automática de Field do atributo
```

### v1.1 → v1.2

**Compatibilidade**: Totalmente regressivo compatível
- Todas as APIs v1.1 continuam funcionando
- Novas APIs adicionadas (QuerySet, descriptors)

**Adições**:
```python
# Novo em v1.2 - QuerySet com chaining
User.query.filter(name='Alice').order_by('id').all()

# Novo em v1.2 - QueryProperty
user = User.find_by_id(1)
related = user.query.filter(active=True).first()

# Novo em v1.2 - Related lookups
user.posts.all()
user.posts.filter(status='published').count()
```

## 🚀 Otimização de Performance

### Requisitos Mínimos Recomendados

```
Processador:  Intel Core i3 ou equivalente
RAM:          512 MB
Disco:        50 MB
Python:       3.7+
```

### Requisitos Recomendados

```
Processador:  Intel Core i5 ou equivalente
RAM:          2 GB
Disco:        100 MB
Python:       3.10+
```

## 🔐 Segurança

### Versões com Patches de Segurança

- v1.2.0+ - Segurança SQL injection verificada
- v1.2.0+ - Validação de entrada implementada

### Atualizações de Segurança

Para receber notificações de segurança:
1. Ative "Watch" no GitHub
2. Selecione "Custom" → "Releases"
3. Você receberá notificações de releases

## 📝 Avisos de Compatibilidade

### ⚠️ Compatibilidade Quebrada

Nenhuma quebra de compatibilidade planejada para v2.0. Consulte [CHANGELOG.md](./CHANGELOG.md) para detalhes de versão.

### ⚠️ Deprecações Planejadas

Nenhuma deprecação planejada no momento.

### ⚠️ Suporte de Versão

- **LTS (Longo prazo)**: v1.2.0 (12+ meses de suporte)
- **Atual**: v1.2.0
- **Próxima**: v2.0.0 (Planejada)

## 🧪 Teste de Compatibilidade

### Executar Teste de Compatibilidade

```bash
# Clone o repositório
git clone https://github.com/VictorSilvaVS/pysql_lite.git
cd pysql_lite

# Instale (opcional)
pip install -e .

# Execute os testes
python -m pytest tests/
# ou
python tests/tests.py
```

### Resultado Esperado

```
Ran 37 tests in 0.013s
OK - All tests passing
```

## 🌍 Internacionalização

- **Interface**: Código-agnostico (sem hardcoded strings)
- **Documentação**: Português e Inglês
- **Exemplos**: Multilíngue

## 📞 Suporte a Compatibilidade

Encontrou um problema de compatibilidade?

1. Verifique a [FAQ](./docs/FAQ.md)
2. Abra uma [Issue no GitHub](https://github.com/VictorSilvaVS/pysql_lite/issues)
3. Inclua:
   - Versão Python (`python --version`)
   - Sistema Operacional
   - Versão do pysql_lite
   - Código de reprodução

---

**Última Atualização**: 2025-11-20  
**Compatibilidade Verificada Até**: Python 3.12
