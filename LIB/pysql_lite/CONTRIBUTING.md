# Contribuindo para pysql_lite

Obrigado por considerar contribuir para o pysql_lite! Este documento fornece diretrizes e instruções para contribuir.

## Como Contribuir

### Reportar Bugs

Se você encontrou um bug:

1. **Use o título descritivo** para descrever o problema
2. **Forneça um exemplo específico** para reproduzir o problema
3. **Descreva o comportamento observado** e o esperado
4. **Inclua screenshots** se possível

### Sugerir Enhancements

Se você tem uma ideia para melhorar o pysql_lite:

1. **Use um título claro e descritivo** para a sugestão
2. **Forneça uma descrição detalhada** do enhancement sugerido
3. **Liste alguns exemplos** de como o enhancement seria usado
4. **Explique por que** isso seria útil

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/pysql_lite.git`
3. **Crie uma branch** para sua feature: `git checkout -b feature/sua-feature`
4. **Faça suas mudanças**
5. **Rode os testes** para garantir que tudo funciona: `python tests/test_database.py`
6. **Commit** suas mudanças: `git commit -am 'Adiciona nova feature'`
7. **Push** para a branch: `git push origin feature/sua-feature`
8. **Abra um Pull Request** no GitHub

## Diretrizes de Desenvolvimento

### Código Python

- Siga o [PEP 8](https://pep8.org/)
- Use type hints onde apropriado
- Mantenha funções pequenas e focadas
- Adicione docstrings em português para classes e métodos públicos

### Testes

- Todo novo código deve ter testes
- Execute os testes antes de fazer commit: `python tests/test_database.py`
- Mantenha a cobertura de testes em 100%

### Commits

- Use mensagens de commit claras e descritivas
- Faça commits atômicos (uma feature por commit)
- Prefira commits pequenos a commits grandes

### Documentação

- Atualize o README se necessário
- Adicione exemplos para novas features
- Mantenha a documentação em português

## Estrutura do Projeto

```
pysql_lite/
├── database.py          # Core ORM
├── __init__.py          # Package initialization
├── examples/            # Exemplos de uso
├── tests/               # Testes unitários
├── docs/                # Documentação adicional
├── .github/workflows/   # CI/CD configuration
├── setup.py             # Configuração de instalação
└── README.md            # Documentação principal
```

## Roadmap

Veja [DEVELOPMENT.md](DEVELOPMENT.md) para o roadmap completo de features planejadas.

## Código de Conduta

### Nossa Promessa

No interesse de promover um ambiente aberto e acolhedor, nós, como colaboradores e mantenedores, nos comprometemos a tornar a participação em nosso projeto e comunidade uma experiência livre de assédio para todos.

### Nossos Padrões

Exemplos de comportamento que contribuem para criar um ambiente positivo incluem:

- Usar linguagem acolhedora e inclusiva
- Ser respeitoso com os pontos de vista e experiências diferentes
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

## Perguntas?

Sinta-se livre para abrir uma issue ou entrar em contato.

---

**Obrigado por contribuir! 🎉**
