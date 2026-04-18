# 🚀 Publicar no PyPI - Guia Completo

## 📋 Checklist Pré-Publicação

- [ ] Versão atualizada no `setup.py` e `pyproject.toml`
- [ ] `__init__.py` com `__version__` correto
- [ ] README.md atualizado e formatado
- [ ] CHANGELOG.md com mudanças da versão
- [ ] LICENSE presente (MIT)
- [ ] Testes passando (37/37)
- [ ] .gitignore correto
- [ ] Conta no PyPI criada
- [ ] Token de autenticação gerado

---

## 1️⃣ Preparação Local

### 1.1 Atualizar Versão

**Em `setup.py`:**
```python
setup(
    name="pysql_lite",
    version="1.2.0",  # ← Atualizar
    author="Victor Silva",
    author_email="seu_email@example.com",
    description="Mini-ORM leve para SQLite sem dependências externas",
    ...
)
```

**Em `pyproject.toml`:**
```toml
[project]
name = "pysql_lite"
version = "1.2.0"  # ← Atualizar
```

**Em `__init__.py`:**
```python
__version__ = "1.2.0"  # ← Adicionar/atualizar
```

### 1.2 Validar Arquivos Necessários

```bash
# Verificar que todos os arquivos existem
ls setup.py                    # ✅ Setup
ls pyproject.toml             # ✅ Project config
ls MANIFEST.in                # ✅ Manifest
ls README.md                  # ✅ Documentação
ls LICENSE                    # ✅ Licença (MIT)
ls pysql_lite/               # ✅ Código
ls pysql_lite/__init__.py    # ✅ Package init
```

### 1.3 Limpar Caches

```bash
# Remover build artifacts
rm -r build/
rm -r dist/
rm -r *.egg-info
rm -r __pycache__

# Ou no Windows PowerShell:
Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force *.egg-info
```

### 1.4 Verificar Testes

```bash
# Executar todos os testes
python -m pytest tests/
# ou
python tests/test_database.py

# Esperado:
# Ran 37 tests in 0.013s
# OK
```

---

## 2️⃣ Instalar Ferramentas Necessárias

### 2.1 Instalar Build Tools

```bash
# Build (recomendado)
pip install build

# Ou setuptools + wheel (método antigo)
pip install setuptools wheel

# Twine (para upload)
pip install twine

# Versão completa
pip install build twine
```

### 2.2 Verificar Instalação

```bash
# Verificar que estão instalados
python -m build --version
python -m twine --version
```

---

## 3️⃣ Criar Distribuição

### 3.1 Build da Distribuição

```bash
# Usar build (recomendado)
python -m build

# Ou método antigo
python setup.py sdist bdist_wheel
```

**Esperado:**
```
Successfully built pysql_lite-1.2.0.tar.gz
Successfully built pysql_lite-1.2.0-py3-none-any.whl
```

### 3.2 Verificar Arquivo Gerado

```bash
# Listar arquivos criados
ls dist/

# Esperado:
# pysql_lite-1.2.0.tar.gz
# pysql_lite-1.2.0-py3-none-any.whl
```

### 3.3 Validar Distribuição

```bash
# Verificar com Twine (IMPORTANTE!)
python -m twine check dist/*

# Esperado:
# Checking distribution dist/pysql_lite-1.2.0.tar.gz: Passed
# Checking distribution dist/pysql_lite-1.2.0-py3-none-any.whl: Passed
```

---

## 4️⃣ Criar Conta no PyPI

### 4.1 Registrar no PyPI

1. Acesse: https://pypi.org/account/register/
2. Preencha:
   - **Username**: seu_usuario (ex: `victorsilvavs`)
   - **Email**: seu_email@example.com
   - **Password**: Senha forte (16+ caracteres)
3. Confirme o email
4. Ative 2FA (recomendado)

### 4.2 Gerar Token de Autenticação

1. Acesse: https://pypi.org/account/
2. Clique em "Account settings"
3. Role até "API tokens"
4. Clique em "Add API token"
5. Nome: `pysql_lite` ou deixe automático
6. **Scope**: "Entire account" (para upload de packages)
7. Copie o token completo (será a única vez que aparece!)

**Token Exemplo:**
```
pypi-AgEIcHlwaS5vcmc...VERY_LONG_STRING...
```

### 4.3 Guardar Token com Segurança

**Opção 1: .pypirc (Local)**
```bash
# Criar arquivo ~/.pypirc
# Linux/Mac: ~/.pypirc
# Windows: %APPDATA%\pip\pip.ini ou C:\Users\[USER]\.pypirc

[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

**Opção 2: Variável de Ambiente**
```bash
# Linux/Mac
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...
export TWINE_USERNAME=__token__

# Windows PowerShell
$env:TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."
$env:TWINE_USERNAME="__token__"
```

**Opção 3: Prompt (Menos seguro)**
```bash
# Twine vai pedir a senha ao executar
python -m twine upload dist/*
```

---

## 5️⃣ Upload para PyPI

### 5.1 Teste com PyPI Test

(Opcional, mas recomendado para primeira vez)

```bash
# Registrar conta em https://test.pypi.org/

# Fazer upload de teste
python -m twine upload --repository testpypi dist/*

# Esperado:
# Uploading pysql_lite-1.2.0.tar.gz
# Uploading pysql_lite-1.2.0-py3-none-any.whl
# View at:
# https://test.pypi.org/project/pysql_lite/
```

### 5.2 Testar Instalação de Teste

```bash
# Instalar do test PyPI
pip install --index-url https://test.pypi.org/simple/ pysql_lite

# Testar
python -c "import pysql_lite; print(pysql_lite.__version__)"

# Desinstalar
pip uninstall pysql_lite
```

### 5.3 Upload para PyPI Oficial

```bash
# Upload final
python -m twine upload dist/*

# Ou com opções
python -m twine upload dist/* --skip-existing

# Esperado:
# Uploading pysql_lite-1.2.0.tar.gz
# Uploading pysql_lite-1.2.0-py3-none-any.whl
# View at:
# https://pypi.org/project/pysql_lite/
```

---

## 6️⃣ Verificação Pós-Upload

### 6.1 Acessar Página no PyPI

```
https://pypi.org/project/pysql_lite/
```

Deve mostrar:
- ✅ Nome do projeto
- ✅ Versão 1.2.0
- ✅ README formatado
- ✅ Instruções de instalação
- ✅ Links para documentação
- ✅ History de versões

### 6.2 Instalar do PyPI

```bash
# Instalar versão fresh do PyPI
pip install pysql_lite

# Ou versão específica
pip install pysql_lite==1.2.0

# Verificar versão
pip show pysql_lite

# Testar import
python -c "from pysql_lite import Database, Model, Field, FieldType; print('✅ OK')"
```

### 6.3 Criar Release no GitHub

```bash
# Criar tag
git tag -a v1.2.0 -m "Release 1.2.0"

# Push tag
git push origin v1.2.0

# Ou via GitHub UI:
# 1. Vá para Releases
# 2. "Create a new release"
# 3. Tag: v1.2.0
# 4. Title: pysql_lite 1.2.0
# 5. Description: (cole CHANGELOG.md)
# 6. Publish
```

---

## 🔄 Atualizar Versão Futura

### Para v1.2.1 (Patch)

```bash
# 1. Atualizar versão em 3 arquivos
# setup.py: version="1.2.1"
# pyproject.toml: version = "1.2.1"
# __init__.py: __version__ = "1.2.1"

# 2. Atualizar CHANGELOG.md
# Adicionar seção para 1.2.1

# 3. Commit e tag
git add .
git commit -m "Bump version to 1.2.1"
git tag -a v1.2.1 -m "Release 1.2.1"

# 4. Build
rm -r dist build *.egg-info
python -m build

# 5. Upload
python -m twine upload dist/*
```

### Para v1.3.0 (Minor)

```bash
# 1. Atualizar versão: 1.3.0
# 2. Adicionar features no CHANGELOG.md
# 3. Repetir processo acima
```

### Para v2.0.0 (Major)

```bash
# 1. Atualizar versão: 2.0.0
# 2. Documentar breaking changes
# 3. Atualizar README.md
# 4. Repetir processo acima
```

---

## 🛡️ Segurança

### ✅ Boas Práticas

1. **Token Seguro**
   - ✅ Gere novo token
   - ✅ Use scope limitado se possível
   - ❌ Nunca compartilhe
   - ❌ Nunca commite no git

2. **MANIFEST.in**
   ```
   include README.md
   include CHANGELOG.md
   include LICENSE
   include MANIFEST.in
   recursive-include docs *.md
   recursive-include examples *.py
   ```

3. **.gitignore**
   ```
   # Não commitar:
   dist/
   build/
   *.egg-info/
   .pypirc
   .env
   ```

### ✅ Verificações Finais

```bash
# 1. Verificar que não há secrets
grep -r "pypi-" .gitignore  # ✅ Deve estar em .gitignore

# 2. Verificar MANIFEST.in
cat MANIFEST.in

# 3. Verificar setup.py
cat setup.py | grep -E "name=|version=|url="

# 4. Verificar PyPI
pip install pysql_lite
python -c "import pysql_lite; print(pysql_lite.__version__)"
```

---

## 🚨 Troubleshooting

### Erro: "Invalid distribution"

**Solução:**
```bash
# Validar com Twine
python -m twine check dist/*

# Corrigir README.md (formato)
# - Não usar headers muito complexos
# - Verificar sintaxe markdown
# - Testar com: pip install readme_renderer
```

### Erro: "File already exists"

**Solução:**
```bash
# PyPI não permite overwrite de versão
# Você deve fazer upload com novo número de versão

# Opção 1: Incrementar versão
# setup.py: 1.2.0 → 1.2.1

# Opção 2: Usar --skip-existing
python -m twine upload dist/* --skip-existing
```

### Erro: "Invalid authentication"

**Solução:**
```bash
# Verificar token:
# 1. Regenere token no PyPI
# 2. Verifique username: __token__
# 3. Verifique .pypirc ou variáveis de ambiente
# 4. Teste com: python -m twine upload --help
```

### Erro: "Repository does not support this package"

**Solução:**
```bash
# Verificar classificadores em setup.py
# Devem ser válidos de: https://pypi.org/pypi?%3Aaction=list_classifiers

# Revisar classifiers:
# "License :: OSI Approved :: MIT License" ✅
# "Programming Language :: Python :: 3" ✅
```

---

## 📊 Checklist Final

### Antes de Upload

- [ ] Versão 1.2.0 em setup.py, pyproject.toml, __init__.py
- [ ] CHANGELOG.md atualizado
- [ ] README.md com badge PyPI
- [ ] LICENSE (MIT)
- [ ] Testes passando (37/37)
- [ ] Build testado localmente
- [ ] Twine validation passou
- [ ] Conta PyPI criada
- [ ] Token gerado e guardado
- [ ] .pypirc ou env vars configuradas

### Depois de Upload

- [ ] Página PyPI accessible
- [ ] `pip install pysql_lite` funciona
- [ ] Versão correta: `pip show pysql_lite`
- [ ] Import funciona
- [ ] GitHub release criado
- [ ] Badge PyPI adicionado ao README.md

---

## 🎯 Links Úteis

| Recurso | URL |
|---------|-----|
| **PyPI** | https://pypi.org |
| **PyPI Account** | https://pypi.org/account/ |
| **Token Management** | https://pypi.org/account/ → API tokens |
| **Test PyPI** | https://test.pypi.org |
| **Twine Docs** | https://twine.readthedocs.io |
| **Setuptools** | https://setuptools.pypa.io |
| **Build** | https://python-poetry.org/docs/cli/#build |

---

## ⏱️ Tempo Estimado

| Etapa | Tempo |
|-------|-------|
| Preparação | 15 min |
| Build | 2 min |
| Upload (primeiro) | 5 min |
| Verificação | 5 min |
| **Total** | **~30 min** |

---

## 📝 Exemplo Completo (Quick Script)

```bash
#!/bin/bash
# publish.sh

# 1. Verificar versão
VERSION="1.2.0"
echo "Publishing pysql_lite v$VERSION..."

# 2. Limpar
rm -rf build dist *.egg-info

# 3. Build
python -m build
echo "✅ Build OK"

# 4. Validar
python -m twine check dist/*
echo "✅ Validation OK"

# 5. Upload
read -p "Ready to upload to PyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python -m twine upload dist/*
    echo "✅ Upload complete!"
    echo "View at: https://pypi.org/project/pysql_lite/"
fi
```

**Uso:**
```bash
chmod +x publish.sh
./publish.sh
```

---

## 🎉 Sucesso!

Você publicou **pysql_lite** no PyPI! 🚀

Agora pode:
- ✅ `pip install pysql_lite`
- ✅ Compartilhar com comunidade
- ✅ Receber feedback
- ✅ Evoluir o projeto

---

**Última Atualização**: 2025-11-20  
**Status**: Pronto para Publicação  
**Versão**: 1.2.0
