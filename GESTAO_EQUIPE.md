# Gestão de Equipe — Sistema de Gerenciamento de Pedidos
## Papéis, Histórias de Usuário, Critérios de Aceitação e Definition of Done

**Projeto:** Sales System — `gerenciador_pedidos.py`  
**Equipe:** 6 integrantes  
**Metodologia:** Scrum + Kanban  
**Data:** 27/05/2026

---

## 1. Estrutura de Papéis

A equipe de 6 pessoas é distribuída em papéis com responsabilidades distintas e complementares. Nenhum papel é hierárquico — todos contribuem para a entrega; o que diferencia é o foco de atuação.

---

### Pessoa 1 — Product Owner (PO)

**Responsabilidade central:** É a voz do cliente dentro do time. Garante que o backlog reflita o que tem mais valor de negócio e que as histórias de usuário cheguem ao time prontas para desenvolvimento.

| Atividade | Descrição |
|-----------|-----------|
| Manter o backlog priorizado | Ordena as histórias por valor de negócio antes de cada sprint |
| Escrever histórias de usuário | Redige no formato padrão com critérios de aceitação claros |
| Refinamento (Backlog Grooming) | Conduz reuniões semanais de refinamento com o time para detalhar histórias |
| Aceitar ou rejeitar entrega | Valida se o que foi entregue satisfaz os critérios de aceitação |
| Gerenciar a coluna "Backlog" no Kanban | Toda nova demanda entra pelo PO — ninguém cria card sem passar por ele/ela |

**Não é responsabilidade do PO:** como o código funciona, quais testes cobrem o quê.

---

### Pessoa 2 — Scrum Master / Facilitador Ágil

**Responsabilidade central:** Remove impedimentos e garante que o processo funcione. É o guardião das cerimônias e do Kanban.

| Atividade | Descrição |
|-----------|-----------|
| Facilitar as cerimônias | Daily (15 min), Planning, Review e Retrospectiva |
| Manter o Kanban atualizado | Verifica diariamente se os cards estão nas colunas corretas e sem travamento |
| Monitorar métricas de fluxo | Lead time, cycle time, WIP (work in progress) por coluna |
| Remover bloqueios | Quando um card fica parado, aciona a pessoa responsável ou escala |
| Registrar impedimentos | Documenta bloqueios com data de abertura e resolução |

**Ferramenta de Kanban sugerida:** Trello, GitHub Projects ou quadro físico com 5 colunas (ver Seção 4).

---

### Pessoa 3 — Tech Lead / Arquiteto de Software

**Responsabilidade central:** Garante a coerência técnica do código. Define padrões, faz code review e toma decisões de arquitetura.

| Atividade | Descrição |
|-----------|-----------|
| Code review obrigatório | Nenhum código entra em `main` sem revisão do Tech Lead |
| Definir padrões de código | Nomenclatura, estrutura de módulos, tratamento de exceções |
| Apoiar o ciclo TDD | Orienta a equipe nas fases Red/Green/Refactor |
| Documentar decisões técnicas | ADR (Architecture Decision Records) para escolhas não óbvias |
| Validar critério técnico da DoD | Confirma que o código passou em linting, cobertura e review |

---

### Pessoa 4 — QA Lead / Engenheiro de Qualidade

**Responsabilidade central:** Define e mantém a estratégia de testes. Garante que a DoD técnica de qualidade seja cumprida em cada entrega.

| Atividade | Descrição |
|-----------|-----------|
| Criar e manter o Plano de Testes | Atualiza o `RELATORIO_QUALIDADE.md` a cada sprint |
| Escrever testes de aceitação | Converte os critérios de aceitação do PO em casos de teste |
| Monitorar cobertura | Executa `pytest --cov` e garante que o percentual acordado seja mantido |
| Identificar e reportar defeitos | Abre cards de bug com reprodução, severidade e impacto |
| Gerenciar a Matriz de Rastreabilidade | Mantém a tabela RN × Casos de Teste atualizada |

---

### Pessoa 5 — Desenvolvedor(a) Backend A

**Responsabilidade central:** Implementa funcionalidades seguindo TDD. Escreve código de produção e testes unitários da história que está desenvolvendo.

| Atividade | Descrição |
|-----------|-----------|
| Desenvolver features do backlog | Pega cards da coluna "Em Desenvolvimento" no Kanban |
| Seguir ciclo TDD | Escreve o teste Red antes de qualquer código de produção |
| Atualizar testes unitários | Cada nova função tem teste unitário antes do merge |
| Participar do refinamento | Contribui com estimativas de esforço (story points ou horas) |
| Mover cards no Kanban | Mantém o status do próprio card atualizado diariamente |

---

### Pessoa 6 — Desenvolvedor(a) Backend B

**Responsabilidade central:** Foco em testes de integração e validação ponta a ponta. Trabalha em par com Dev A quando necessário.

| Atividade | Descrição |
|-----------|-----------|
| Implementar testes de integração | Escreve e mantém `test_integracao.py` para cada nova feature |
| Pair programming com Dev A | Sessões de programação em par para histórias complexas |
| Validar efeitos colaterais | Garante que novas features não quebram estoque, cupons, frete |
| Apoiar QA Lead na cobertura | Identifica lacunas de teste e preenche com novos casos |
| Revisar PRs | Segunda revisão técnica além do Tech Lead |

---

## 2. Histórias de Usuário Refinadas

As histórias seguem o template padrão:

```
Como [papel/ator],
quero [ação ou funcionalidade],
para que [benefício ou valor de negócio].
```

Cada história tem critérios de aceitação no formato **Given / When / Then** (Gherkin simplificado).

---

### US-01 — Processar Venda Simples

> **Como** cliente,  
> **quero** finalizar a compra de um produto disponível em estoque,  
> **para que** minha compra seja registrada e o estoque atualizado automaticamente.

**Estimativa:** 3 story points  
**Responsável:** Dev A (código) + QA Lead (testes de aceitação)  
**Prioridade:** Alta

#### Critérios de Aceitação

| # | Given (Dado que) | When (Quando) | Then (Então) |
|---|-----------------|---------------|--------------|
| CA-01 | o produto `PROD02` tem 10 unidades em estoque | o cliente solicita 2 unidades | o sistema retorna `subtotal=240.00`, `desconto=0.0`, `total=240.00` |
| CA-02 | o produto existe no catálogo | a venda é processada com sucesso | o estoque do produto é decrementado na quantidade vendida |
| CA-03 | o produto `PROD01` tem 4 unidades | o cliente solicita exatamente 4 | a venda é aceita e o estoque vai a zero |
| CA-04 | o produto `PROD01` tem 4 unidades | o cliente solicita 5 | o sistema lança `ValueError` com mensagem "indisponível" |
| CA-05 | `id_produto` é `None` ou string vazia | qualquer quantidade é solicitada | o sistema lança `ValueError` com mensagem "inválidos" |

---

### US-02 — Aplicar Cupom de Desconto

> **Como** cliente,  
> **quero** informar um código de cupom no momento da compra,  
> **para que** eu obtenha um desconto percentual sobre o valor total do pedido.

**Estimativa:** 2 story points  
**Responsável:** Dev A (código) + Dev B (testes de integração)  
**Prioridade:** Média

#### Critérios de Aceitação

| # | Given | When | Then |
|---|-------|------|------|
| CA-01 | o cupom `SENAC10` está cadastrado com 10% | o cliente aplica `SENAC10` em um pedido de R$ 300,00 | o sistema retorna `desconto=30.00` e `total=270.00` |
| CA-02 | o cupom `FATESE20` está cadastrado com 20% | o cliente aplica `FATESE20` em um pedido de R$ 120,00 | o sistema retorna `desconto=24.00` e `total=96.00` |
| CA-03 | o cliente informa um cupom inexistente (`CUPOM_FALSO`) | a venda é processada | o desconto permanece `0.0` e nenhuma exceção é lançada |
| CA-04 | o cliente não informa nenhum cupom (`None`) | a venda é processada | o desconto é `0.0` |
| CA-05 | o cliente informa string vazia como cupom | a venda é processada | o desconto é `0.0` |

---

### US-03 — Calcular Frete Automático

> **Como** cliente,  
> **quero** que o frete seja calculado automaticamente com base no valor do meu pedido,  
> **para que** eu seja incentivado a comprar mais e saiba o custo total da entrega.

**Estimativa:** 2 story points  
**Responsável:** Dev B (código + TDD) + QA Lead (plano de testes)  
**Prioridade:** Alta

#### Critérios de Aceitação

| # | Given | When | Then |
|---|-------|------|------|
| CA-01 | o total do pedido após descontos é R$ 600,00 | o frete é calculado | o frete retornado é `0.0` (grátis) |
| CA-02 | o total do pedido é exatamente R$ 500,00 | o frete é calculado | o frete retornado é `20.0` |
| CA-03 | o total do pedido é R$ 499,99 | o frete é calculado | o frete retornado é `20.0` |
| CA-04 | o total do pedido é R$ 500,01 | o frete é calculado | o frete retornado é `0.0` |
| CA-05 | um valor não numérico é passado | `calcular_frete` é chamada | `TypeError` é lançado |
| CA-06 | um valor negativo é passado | `calcular_frete` é chamada | `ValueError` é lançado |

---

### US-04 — Garantir Atomicidade das Vendas

> **Como** sistema,  
> **quero** que o estoque só seja alterado quando uma venda for concluída com sucesso,  
> **para que** falhas no processamento não causem inconsistência nos dados de estoque.

**Estimativa:** 1 story point  
**Responsável:** Dev B (testes de integração) + Tech Lead (revisão)  
**Prioridade:** Alta

#### Critérios de Aceitação

| # | Given | When | Then |
|---|-------|------|------|
| CA-01 | `PROD01` tem 4 unidades e o cliente solicita 99 | `processar_venda` lança `ValueError` | o estoque de `PROD01` permanece 4 |
| CA-02 | o cliente solicita produto inexistente | `processar_venda` lança `KeyError` | nenhum estoque é alterado |

---

## 3. Definition of Done (DoD)

A DoD define o contrato de qualidade que toda entrega deve cumprir antes de ser considerada concluída. Um card só sai da coluna "Em Revisão" e vai para "Concluído" quando **todos** os critérios abaixo forem atendidos.

### 3.1 DoD — Nível de Código

- [ ] O código foi escrito seguindo o ciclo TDD (evidência: commits separados para Red, Green e Refactor)
- [ ] Todos os testes unitários da funcionalidade passam (`pytest` com exit code 0)
- [ ] Todos os testes de integração passam
- [ ] Cobertura de testes do módulo mantida em **≥ 95%** (meta: 100%)
- [ ] Nenhum `print()`, `breakpoint()` ou código de debug no código de produção
- [ ] Variáveis, funções e classes nomeadas em português (padrão do projeto)
- [ ] Tratamento de exceções semanticamente correto (`ValueError` para regras de negócio, `KeyError` para chaves ausentes, `TypeError` para tipos inválidos)

### 3.2 DoD — Nível de Testes

- [ ] Todos os critérios de aceitação da história de usuário têm pelo menos um caso de teste correspondente
- [ ] A Matriz de Rastreabilidade foi atualizada com os novos IDs de teste
- [ ] Nenhum teste duplicado (mesmo assert com mesmo argumento em dois métodos distintos)
- [ ] Fixtures de isolamento (`autouse=True`) aplicadas onde há estado global mutável

### 3.3 DoD — Nível de Revisão

- [ ] Pull Request aberto com descrição clara do que foi implementado
- [ ] Code review aprovado pelo **Tech Lead** (Pessoa 3)
- [ ] Segunda revisão aprovada por pelo menos mais **1 desenvolvedor**
- [ ] QA Lead validou que os critérios de aceitação da história foram cobertos por testes

### 3.4 DoD — Nível de Documentação

- [ ] `RELATORIO_QUALIDADE.md` atualizado com métricas da sprint atual
- [ ] Histórias de usuário marcadas como "Aceitas" pelo PO no Kanban
- [ ] Qualquer comportamento não óbvio documentado com comentário inline (apenas o "porquê", não o "o quê")

---

## 4. Estrutura do Kanban

O quadro tem **5 colunas**. Cada card representa uma história de usuário ou tarefa derivada.

```
┌──────────────┬──────────────┬──────────────────┬──────────────┬─────────────┐
│   BACKLOG    │  SELECIONADO │  EM              │  EM          │  CONCLUÍDO  │
│              │  (Sprint)    │  DESENVOLVIMENTO │  REVISÃO     │             │
├──────────────┼──────────────┼──────────────────┼──────────────┼─────────────┤
│ US-xx novas  │ US-01        │ US-03 (Dev B)    │ US-02        │ US-04 ✓     │
│ refinadas    │ US-02        │                  │              │             │
│ pelo PO      │ US-03        │ WIP limit: 2     │ WIP limit: 3 │             │
│              │              │                  │              │             │
│ Bugs         │              │                  │              │             │
│ reportados   │              │                  │              │             │
└──────────────┴──────────────┴──────────────────┴──────────────┴─────────────┘
```

### Regras do Kanban

| Regra | Detalhe |
|-------|---------|
| **WIP limit em Desenvolvimento** | Máximo 2 cards simultâneos — evita dispersão |
| **WIP limit em Revisão** | Máximo 3 cards — revisão acumulada trava o fluxo |
| **Quem move o card** | O responsável pela tarefa move quando muda de etapa |
| **Card parado > 2 dias** | Scrum Master aciona a pessoa responsável |
| **Bug novo** | Entra no Backlog com label `[BUG]` e severidade (Alta/Média/Baixa) |
| **Bloqueio** | Card recebe label `[BLOQUEADO]` e o Scrum Master registra o impedimento |

### Campos obrigatórios de cada card

```
Título      : [US-XX] Nome curto da história
Responsável : Pessoa X (papel)
Estimativa  : X story points
Sprint      : Sprint N
Critérios   : link ou lista dos CA cobertos
Status DoD  : checklist inline
```

---

## 5. Cerimônias Ágeis Resumidas

| Cerimônia | Frequência | Duração | Quem participa | Facilitador |
|-----------|-----------|---------|---------------|-------------|
| **Daily Standup** | Diária | 15 min | Todos | Scrum Master |
| **Sprint Planning** | Início de cada sprint | 1h | Todos | Scrum Master + PO |
| **Backlog Grooming** | Meio da sprint | 30 min | PO + Tech Lead + QA Lead | PO |
| **Sprint Review** | Fim da sprint | 30 min | Todos | PO apresenta |
| **Retrospectiva** | Fim da sprint | 30 min | Todos | Scrum Master |

### Perguntas da Daily (cada pessoa responde em 1–2 frases)

1. O que fiz desde a última daily?
2. O que farei até a próxima?
3. Tenho algum bloqueio?

---

## 6. Fluxo de Trabalho de uma História

```
PO escreve US com CA claros
        ↓
Grooming: time refina, estima e tira dúvidas
        ↓
Planning: US entra em "Selecionado (Sprint)"
        ↓
Dev A ou B pega o card → move para "Em Desenvolvimento"
        ↓
TDD: escreve teste Red → commit → implementa Green → commit → Refactor → commit
        ↓
Dev abre Pull Request → move card para "Em Revisão"
        ↓
Tech Lead faz code review (obrigatório)
QA Lead verifica cobertura e rastreabilidade
        ↓
PO valida critérios de aceitação
        ↓
Card move para "Concluído" ✓
        ↓
QA Lead atualiza RELATORIO_QUALIDADE.md
```

---

## 7. Tabela Resumo — Quem faz o quê

| Atividade | PO | Scrum Master | Tech Lead | QA Lead | Dev A | Dev B |
|-----------|:--:|:------------:|:---------:|:-------:|:-----:|:-----:|
| Escrever histórias de usuário | ✅ | | | | | |
| Definir critérios de aceitação | ✅ | | | 🔍 | | |
| Priorizar backlog | ✅ | | | | | |
| Facilitar cerimônias | | ✅ | | | | |
| Manter Kanban | | ✅ | | | ✅ | ✅ |
| Remover bloqueios | | ✅ | | | | |
| Code review | | | ✅ | | | ✅ |
| Definir padrões técnicos | | | ✅ | | | |
| Escrever testes unitários | | | | | ✅ | ✅ |
| Escrever testes de integração | | | | 🔍 | | ✅ |
| Monitorar cobertura | | | | ✅ | | |
| Atualizar matriz de rastreabilidade | | | | ✅ | | |
| Implementar funcionalidades (TDD) | | | | | ✅ | ✅ |
| Aceitar entrega (validar CA) | ✅ | | | 🔍 | | |
| Atualizar relatório de qualidade | | | | ✅ | | |

> ✅ = responsável principal · 🔍 = participa / apoia
