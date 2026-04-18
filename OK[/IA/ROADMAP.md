# Arquitetura da IA de Terminal "Causal" (Base do Porquê)

## Visão Geral
Construir uma IA de terminal que não opere via "pattern matching" clássico, mas sim através da criação de um modelo de mundo causal. Ela deve questionar, testar hipóteses, analisar causas profundas e armazenar conclusões (insight) antes de simplesmente executar o que lhe é mandado ou corrigir de maneira superficial.

## Pilares Fundamentais
1. **Curry / Causal Engine:** O motor que pergunta o "porquê".
2. **Sistema de Memória de Curto e Longo Prazo:** Consolida as "regras" descobertas (Memória Semântica) e as ações passadas (Memória Episódica).
3. **Workspace de Hipóteses (Sandbox):** Onde a IA testa comandos antes de afirmar coisas ou executar no sistema principal (se aplicável/seguro).
4. **Motor de Diálogo Socrático:** Para extrair do humano as premissas faltantes do cenário que ela não compreende nativamente.

## Etapas de Desenvolvimento

### Fase 1: Fundação do Cérebro Causal
- [ ] Configuração do projeto base (Python avançado).
- [ ] Definição das estruturas de estado (`AgentState`).
- [ ] Implementação de um `Graph Engine` (ex: usando LangGraph para fluxo e referências causais).
- [ ] Construir o nó de **Reflexão/"Por Que"** (recebe um objetivo, gera a ramificação de porquês).

### Fase 2: Motor de Aprendizado Experiencial
- [ ] Integração com sistema local (Windows OS/Powershell via subprocessos estruturados).
- [ ] Implementar a capacidade de gerar *Hipóteses* de forma controlada.
- [ ] Desenvolver mecanismo de **Avaliação de Resultado**: "A ação X causou o que eu esperava?" Se sim: cristalizar como 'regra causal' na base. Se não: disparar nó de investigação do erro.

### Fase 3: Sistema de Memória (Semântica & Episódica)
- [ ] Integração de banco de dados leve local (SQLite/TinyDB ou Vetorial local como Chroma) para persistir "Regras aprendidas".
- [ ] Criar o injetor de contexto retroativo.

### Fase 4: Integração de Personalidade (O Humanoide)
- [ ] Interface de terminal rica (usando `rich`).
- [ ] Modo autônomo (Background learning) onde ela testa coisas.
