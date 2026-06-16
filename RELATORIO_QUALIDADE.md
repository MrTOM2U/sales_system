# Relatório Técnico de Qualidade e Plano de Testes
## Sistema de Gerenciamento de Pedidos — `gerenciador_pedidos.py`

**Data de emissão:** 27/05/2026  
**Iteração:** Sprint 1  
**Autor:** Equipe QA  
**Versão do documento:** 1.0

---

## 1. Estratégia e Escopo

### 1.1 Descrição do Ambiente de Testes

| Item | Detalhe |
|------|---------|
| Sistema Operacional | macOS Darwin 25.5.0 (arm64) |
| Linguagem | Python 3.12.9 |
| Framework de testes | pytest 8.3.3 + pytest-cov 5.0.0 |
| Módulo sob teste | `gerenciador_pedidos.py` |
| Diretório de testes | `tests/` |
| Modo de execução | `pytest tests/ -v --cov=gerenciador_pedidos --cov-report=term-missing` |

### 1.2 Ferramentas Configuradas

- **pytest** — runner de testes, coleta automática de classes `Test*` e funções `test_*`
- **pytest-cov** — instrumentação de cobertura via `coverage.py`, relatório `term-missing`
- **copy.deepcopy** — isolamento de estado global por fixture `autouse=True` em todos os módulos de teste

### 1.3 Limites da Iteração

A iteração cobre exclusivamente a camada de lógica de negócio implementada em `gerenciador_pedidos.py`. Estão **fora de escopo**:

- Interface de usuário ou API REST
- Persistência em banco de dados real (o estoque é simulado em dicionário em memória)
- Autenticação e controle de acesso
- Testes de carga ou desempenho

### 1.4 Tipos de Teste Executados

| Tipo | Arquivo | Responsabilidade |
|------|---------|-----------------|
| Unitário | `tests/test_unitarios.py` | Funções isoladas, todos os branches |
| TDD (ciclo documentado) | `tests/test_tdd_frete.py` | Red → Green → Refactor de `calcular_frete` |
| Integração | `tests/test_integracao.py` | Persistência de estado no `estoque_sistema` global |

---

## 2. Matriz de Rastreabilidade de Requisitos

A tabela abaixo relaciona cada requisito de negócio identificado ao(s) identificador(es) dos casos de teste que o verificam.

| ID Req. | Descrição do Requisito / Regra de Negócio | Casos de Teste Associados |
|---------|-------------------------------------------|--------------------------|
| **RN-01** | `id_produto` nulo, vazio ou falsy → `ValueError` | `test_id_produto_nulo_lanca_valueerror` · `test_id_produto_vazio_lanca_valueerror` |
| **RN-02** | `quantidade <= 0` → `ValueError` | `test_quantidade_zero_lanca_valueerror` · `test_quantidade_negativa_lanca_valueerror` |
| **RN-03** | Produto inexistente no catálogo → `KeyError` | `test_produto_inexistente_lanca_keyerror` |
| **RN-04** | Estoque insuficiente → `ValueError` (não `IndexError`) | `test_estoque_insuficiente_lanca_valueerror` · `test_produto_sem_estoque_lanca_valueerror` |
| **RN-05** | Subtotal = preço × quantidade | `test_venda_simples_sem_cupom` · `test_quantidade_maxima_disponivel` |
| **RN-06** | Cupom válido aplica percentual de desconto sobre subtotal | `test_venda_com_cupom_senac10` · `test_venda_com_cupom_fatese20` |
| **RN-07** | Cupom inválido é ignorado silenciosamente (desconto = 0) | `test_cupom_invalido_nao_aplica_desconto` · `test_cupom_vazio_desconto_zero` |
| **RN-08** | Ausência de cupom resulta em desconto zero | `test_sem_cupom_desconto_zero` |
| **RN-09** | Total final = subtotal − desconto | `test_venda_com_cupom_senac10` · `test_venda_com_cupom_fatese20` · `test_fluxo_completo_com_desconto_e_frete` |
| **RN-10** | Retorno deve conter as chaves: `produto`, `subtotal`, `desconto`, `total`, `frete` | `test_retorno_contem_chaves_obrigatorias` |
| **RN-11** | Venda decrementa o estoque do produto vendido | `test_estoque_diminui_apos_venda` · `test_estoque_zera_apos_venda_total` · `test_duas_vendas_sequenciais_acumulam_reducao` |
| **RN-12** | Venda de um produto não altera estoque de outro | `test_estoque_outros_produtos_nao_afetado` · `test_tres_vendas_diferentes_produtos` |
| **RN-13** | Falha na venda não altera o estoque (atomicidade) | `test_falha_nao_altera_estoque` · `test_produto_esgotado_nao_aceita_nova_venda` |
| **RN-14** | Total > R$ 500,00 → frete = R$ 0,00 | `test_frete_gratis_acima_500` · `test_red_frete_zero_quando_total_acima_500` · `test_green_um_centavo_acima_do_limite` · `test_processar_venda_retorna_frete_gratis_monitor` |
| **RN-15** | Total ≤ R$ 500,00 → frete = R$ 20,00 | `test_frete_cobrado_exatamente_500` · `test_frete_cobrado_abaixo_500` · `test_green_limite_exato_500_paga_frete` · `test_processar_venda_retorna_frete_cobrado_mouse` |
| **RN-16** | `calcular_frete` rejeita tipo não numérico → `TypeError` | `test_frete_tipo_invalido_lanca_typeerror` · `test_refactor_tipo_string_lanca_typeerror` · `test_refactor_tipo_none_lanca_typeerror` · `test_refactor_tipo_lista_lanca_typeerror` |
| **RN-17** | `calcular_frete` rejeita valor negativo → `ValueError` | `test_frete_negativo_lanca_valueerror` · `test_refactor_valor_negativo_lanca_valueerror` |

**Cobertura de requisitos:** 17 requisitos mapeados, 17 cobertos por pelo menos um caso de teste (**100% de rastreabilidade**).

---

## 3. Evidências do Ciclo TDD — Regra de Frete

O desenvolvimento da função `calcular_frete` seguiu estritamente o ciclo **Red → Green → Refactor**, documentado abaixo.

### 3.1 Fase RED — Testes escritos antes da implementação

Os casos de teste foram redigidos a partir dos critérios de aceitação da história de usuário antes de qualquer código de produção. Para reproduzir e evidenciar esta fase, o corpo da função `calcular_frete` foi substituído por `pass` — simulando o estado inicial onde a função existe mas não possui implementação. Neste estado todos os testes de comportamento falharam, pois `pass` retorna `None` implicitamente.

**Log real da Fase RED** (`pytest tests/test_tdd_frete.py::TestTDD_Red_FreteGratis -v`):

```
============================= test session starts ==============================
platform darwin -- Python 3.12.9, pytest-8.3.3, pluggy-1.6.0
rootdir: /Users/jpbertoldo/Downloads/sales_system
collected 5 items

tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_acima_500  FAILED [ 20%]
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_igual_a_501 FAILED [ 40%]
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_igual_500 FAILED [ 60%]
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_abaixo_500 FAILED [ 80%]
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_zero    FAILED [100%]

================================= FAILURES ====================================
_ TestTDD_Red_FreteGratis.test_red_frete_zero_quando_total_acima_500 _

    def test_red_frete_zero_quando_total_acima_500(self):
>       assert gp.calcular_frete(501.00) == 0.0
E       assert None == 0.0
E        +  where None = <function calcular_frete at 0x108f5f740>(501.0)

_ TestTDD_Red_FreteGratis.test_red_frete_cobrado_quando_total_igual_500 _

    def test_red_frete_cobrado_quando_total_igual_500(self):
>       assert gp.calcular_frete(500.00) == 20.0
E       assert None == 20.0
E        +  where None = <function calcular_frete at 0x108f5f740>(500.0)

_ TestTDD_Red_FreteGratis.test_red_frete_cobrado_quando_total_abaixo_500 _

    def test_red_frete_cobrado_quando_total_abaixo_500(self):
>       assert gp.calcular_frete(200.00) == 20.0
E       assert None == 20.0

_ TestTDD_Red_FreteGratis.test_red_frete_cobrado_quando_total_zero _

    def test_red_frete_cobrado_quando_total_zero(self):
>       assert gp.calcular_frete(0.0) == 20.0
E       assert None == 20.0

FAILED tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_acima_500
FAILED tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_igual_a_501
FAILED tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_igual_500
FAILED tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_abaixo_500
FAILED tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_zero

========================== 5 failed in 0.05s ==================================
```

**Critérios de aceitação que guiaram a escrita:**

| Condição | Resultado esperado |
|----------|--------------------|
| total > R$ 500,00 | frete = R$ 0,00 |
| total ≤ R$ 500,00 | frete = R$ 20,00 |
| total negativo | `ValueError` |
| total não numérico | `TypeError` |

### 3.2 Fase GREEN — Implementação mínima

Implementação inserida em `gerenciador_pedidos.py` para fazer os testes passarem com o menor código possível:

```python
def calcular_frete(total):
    return 0.0 if total > 500.0 else 20.0
```

**Resultado após GREEN:**

```
PASSED  test_red_frete_zero_quando_total_acima_500
PASSED  test_red_frete_cobrado_quando_total_igual_500
PASSED  test_red_frete_cobrado_quando_total_abaixo_500
PASSED  test_red_frete_cobrado_quando_total_zero
PASSED  test_green_retorno_float_frete_gratis
PASSED  test_green_retorno_float_frete_cobrado
PASSED  test_green_limite_exato_500_paga_frete
PASSED  test_green_um_centavo_acima_do_limite
```

### 3.3 Fase REFACTOR — Robustez sem alterar comportamento

Validações de guarda foram adicionadas para rejeitar entradas inválidas, mantendo 100% de regressão zero nos testes existentes:

```python
def calcular_frete(total):
    if not isinstance(total, (int, float)):
        raise TypeError("O valor total deve ser numérico.")
    if total < 0:
        raise ValueError("O valor total não pode ser negativo.")
    return 0.0 if total > 500.0 else 20.0
```

**Resultado após REFACTOR:**

```
PASSED  test_refactor_tipo_string_lanca_typeerror
PASSED  test_refactor_tipo_none_lanca_typeerror
PASSED  test_refactor_tipo_lista_lanca_typeerror
PASSED  test_refactor_valor_negativo_lanca_valueerror
PASSED  test_refactor_inteiro_aceito_como_total
```

Nenhum teste anterior foi quebrado — regressão zero confirmada.

### 3.4 Log de Execução Final (evidência de 48 testes passando)

```
============================= test session starts ==============================
platform darwin -- Python 3.12.9, pytest-8.3.3, pluggy-1.6.0
rootdir: /Users/jpbertoldo/Downloads/sales_system
collected 48 items

tests/test_integracao.py::TestPersistenciaEstoque::test_estoque_diminui_apos_venda       PASSED
tests/test_integracao.py::TestPersistenciaEstoque::test_estoque_zera_apos_venda_total     PASSED
tests/test_integracao.py::TestPersistenciaEstoque::test_produto_esgotado_nao_aceita_nova_venda PASSED
tests/test_integracao.py::TestPersistenciaEstoque::test_estoque_outros_produtos_nao_afetado   PASSED
tests/test_integracao.py::TestVendasSequenciais::test_duas_vendas_sequenciais_acumulam_reducao PASSED
tests/test_integracao.py::TestVendasSequenciais::test_tres_vendas_diferentes_produtos         PASSED
tests/test_integracao.py::TestVendasSequenciais::test_venda_com_cupom_nao_afeta_estoque_diferente PASSED
tests/test_integracao.py::TestFluxoCompleto::test_fluxo_completo_com_desconto_e_frete         PASSED
tests/test_integracao.py::TestFluxoCompleto::test_fluxo_completo_sem_desconto_com_frete       PASSED
tests/test_integracao.py::TestFluxoCompleto::test_falha_nao_altera_estoque                    PASSED
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_acima_500  PASSED
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_zero_quando_total_igual_a_501 PASSED
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_igual_500 PASSED
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_abaixo_500 PASSED
tests/test_tdd_frete.py::TestTDD_Red_FreteGratis::test_red_frete_cobrado_quando_total_zero    PASSED
tests/test_tdd_frete.py::TestTDD_Green_Verificacao::test_green_retorno_float_frete_gratis     PASSED
tests/test_tdd_frete.py::TestTDD_Green_Verificacao::test_green_retorno_float_frete_cobrado    PASSED
tests/test_tdd_frete.py::TestTDD_Green_Verificacao::test_green_limite_exato_500_paga_frete    PASSED
tests/test_tdd_frete.py::TestTDD_Green_Verificacao::test_green_um_centavo_acima_do_limite     PASSED
tests/test_tdd_frete.py::TestTDD_Refactor_Robustez::test_refactor_tipo_string_lanca_typeerror PASSED
tests/test_tdd_frete.py::TestTDD_Refactor_Robustez::test_refactor_tipo_none_lanca_typeerror   PASSED
tests/test_tdd_frete.py::TestTDD_Refactor_Robustez::test_refactor_tipo_lista_lanca_typeerror  PASSED
tests/test_tdd_frete.py::TestTDD_Refactor_Robustez::test_refactor_valor_negativo_lanca_valueerror PASSED
tests/test_tdd_frete.py::TestTDD_Refactor_Robustez::test_refactor_inteiro_aceito_como_total   PASSED
tests/test_tdd_frete.py::TestFreteIntegradoAoProcessarVenda::test_processar_venda_retorna_frete_gratis_monitor PASSED
tests/test_tdd_frete.py::TestFreteIntegradoAoProcessarVenda::test_processar_venda_retorna_frete_cobrado_mouse  PASSED
tests/test_unitarios.py::TestCaminhoFeliz::test_venda_simples_sem_cupom                       PASSED
tests/test_unitarios.py::TestCaminhoFeliz::test_venda_com_cupom_senac10                       PASSED
tests/test_unitarios.py::TestCaminhoFeliz::test_venda_com_cupom_fatese20                      PASSED
tests/test_unitarios.py::TestCaminhoFeliz::test_retorno_contem_chaves_obrigatorias            PASSED
tests/test_unitarios.py::TestCaminhoFeliz::test_quantidade_maxima_disponivel                  PASSED
tests/test_unitarios.py::TestExcecoes::test_id_produto_nulo_lanca_valueerror                  PASSED
tests/test_unitarios.py::TestExcecoes::test_id_produto_vazio_lanca_valueerror                 PASSED
tests/test_unitarios.py::TestExcecoes::test_quantidade_zero_lanca_valueerror                  PASSED
tests/test_unitarios.py::TestExcecoes::test_quantidade_negativa_lanca_valueerror              PASSED
tests/test_unitarios.py::TestExcecoes::test_produto_inexistente_lanca_keyerror                PASSED
tests/test_unitarios.py::TestExcecoes::test_estoque_insuficiente_lanca_valueerror             PASSED
tests/test_unitarios.py::TestExcecoes::test_produto_sem_estoque_lanca_valueerror              PASSED
tests/test_unitarios.py::TestBranchesCupom::test_cupom_invalido_nao_aplica_desconto          PASSED
tests/test_unitarios.py::TestBranchesCupom::test_sem_cupom_desconto_zero                     PASSED
tests/test_unitarios.py::TestBranchesCupom::test_cupom_vazio_desconto_zero                   PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_gratis_acima_500              PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_gratis_exatamente_500_01      PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_cobrado_exatamente_500        PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_cobrado_abaixo_500            PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_total_zero_paga_frete         PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_tipo_invalido_lanca_typeerror PASSED
tests/test_unitarios.py::TestCalcularFreteUnitario::test_frete_negativo_lanca_valueerror     PASSED

============================== 48 passed in 0.09s ==============================
```

### 3.5 Artefato Visual de Gestão — Kanban (Trello)

Como evidência do uso ativo da metodologia ágil, o time utilizou um quadro Kanban no **Trello** (board: *Sales System — Gerenciador Pedidos*) com as seguintes colunas e WIP limits:

| Coluna | WIP Limit | Finalidade |
| ------ | --------- | ---------- |
| Backlog | — | Histórias priorizadas pelo PO (US-01 a US-04 + 2 bugs) |
| Selecionado (Sprint) | — | Itens comprometidos para a sprint corrente |
| Em Desenvolvimento | 2 | Implementação ativa — limita trabalho paralelo |
| Em Revisão | 3 | Code review (Tech Lead) + validação QA |
| Concluído | — | Histórias aceitas pelo PO com DoD cumprida |

**Cards criados no Sprint 1:**

| Card | Etiquetas | Checklists |
| ---- | --------- | ---------- |
| [US-01] Processar Venda Simples | Dev A · QA Lead | 5 CA + 6 itens DoD = 11 itens |
| [US-02] Aplicar Cupom de Desconto | Dev A · Dev B | 5 CA + 6 itens DoD = 11 itens |
| [US-03] Calcular Frete Automático | QA Lead · Dev B | 6 CA + 6 itens DoD = 12 itens |
| [US-04] Atomicidade das Vendas | Tech Lead · Dev B | 2 CA + 4 itens DoD = 6 itens |
| [BUG] RED-01 — teste duplicado test_unitarios.py | QA Lead · BUG | 3 itens DoD |
| [BUG] RED-02 — teste duplicado test_tdd_frete.py | QA Lead · BUG | 3 itens DoD |

A estrutura completa de papéis, histórias de usuário, critérios de aceitação e Definition of Done está documentada no artefato complementar `GESTAO_EQUIPE.md`.

---

## 4. Métricas de Software

### 4.1 Cobertura de Testes (Test Coverage)

Saída do `pytest-cov` com `--cov-report=term-missing`:

```
---------- coverage: platform darwin, python 3.12.9-final-0 ----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
gerenciador_pedidos.py      25      0   100%
------------------------------------------------------
TOTAL                       25      0   100%
```

| Métrica | Valor |
|---------|-------|
| Statements instrumentados | 25 |
| Statements não cobertos | 0 |
| **Cobertura de testes (Statement Coverage)** | **100%** |
| Branches testados | Todos (if/elif/else de todas as funções) |

A cobertura de 100% foi atingida pelo conjunto combinado dos três arquivos de teste, garantindo que nenhuma linha executável do módulo permaneceu sem exercício durante a suíte.

### 4.2 Densidade de Defeitos (Defect Density)

#### 4.2.1 Defeitos identificados no código original

Três defeitos foram mapeados por análise estática e documentados nos comentários inline do código:

| ID Defeito | Localização | Descrição | Severidade |
|------------|-------------|-----------|------------|
| **D-01** | `processar_venda`, linha retorno — chave `"desconto"` | Variável `descuento` (espanhol) referenciada no lugar de `desconto` — causava `NameError` em tempo de execução em qualquer venda | Alta |
| **D-02** | `processar_venda`, verificação de estoque | Lançava `IndexError` para estoque insuficiente — exceção semanticamente incorreta para uma violação de regra de negócio | Média |
| **D-03** | `processar_venda`, dicionário de retorno | Chave `}` de fechamento ausente — causava `SyntaxError` impedindo qualquer importação do módulo | Alta |

#### 4.2.2 Cálculo da Densidade de Defeitos

A métrica padrão IEEE é calculada sobre o total de linhas de código executáveis (statements):

```
Densidade de Defeitos = Número de defeitos / Tamanho do módulo (KLOC)

Onde:
  - Defeitos encontrados  = 3
  - Statements totais     = 25  →  0,025 KSLOC (Kilo Statements Lines of Code)
  - Linhas físicas totais = 160  →  0,160 KLOC  (incluindo comentários e espaços)
```

**Calculando sobre statements executáveis (métrica mais precisa):**

```
Densidade = 3 / 0,025 = 120 defeitos / KSLOC
```

**Calculando sobre linhas físicas (métrica conservadora):**

```
Densidade = 3 / 0,160 = 18,75 defeitos / KLOC
```

| Métrica | Valor |
|---------|-------|
| Total de defeitos mapeados | 3 |
| Statements do módulo | 25 |
| Linhas físicas do módulo | 160 |
| **Densidade (sobre statements)** | **120 defeitos/KSLOC** |
| **Densidade (sobre linhas físicas)** | **18,75 defeitos/KLOC** |

> O valor elevado na métrica por KSLOC reflete o tamanho reduzido do módulo (25 statements). Em projetos de pequena escala, a densidade por linhas físicas (18,75/KLOC) é a referência mais representativa para comparação com benchmarks industriais, onde a faixa típica para código novo varia de 10 a 50 defeitos/KLOC.

---

## 5. Registro de Redundâncias nos Testes

Durante a revisão da suíte, foram identificados dois pares de testes com **assert idêntico** — mesma função chamada com o mesmo argumento, mesmo valor esperado — diferindo apenas no nome do método. Estes casos não causam falha, mas constituem **redundância técnica** que reduz a eficiência da suíte.

### 5.1 Redundância 1 — `tests/test_unitarios.py`

**Localização:** classe `TestCalcularFreteUnitario`, linhas 151–155

```python
# Linha 151
def test_frete_gratis_acima_500(self):
    assert gp.calcular_frete(500.01) == 0.0   # ← argumento: 500.01

# Linha 154
def test_frete_gratis_exatamente_500_01(self):
    assert gp.calcular_frete(500.01) == 0.0   # ← argumento: 500.01 (IDÊNTICO)
```

**Diagnóstico:** O nome `test_frete_gratis_acima_500` sugere intenção de testar um valor genérico acima do limite (ex.: `600.00`). O valor `500.01` foi replicado sem perceber que já era o objeto do segundo teste. Nenhum dos dois cobre o cenário "valor genérico alto" como pretendido pelo primeiro nome.

**Correção recomendada:**

```python
def test_frete_gratis_acima_500(self):
    assert gp.calcular_frete(600.00) == 0.0   # valor genérico acima do limite

def test_frete_gratis_exatamente_500_01(self):
    assert gp.calcular_frete(500.01) == 0.0   # caso de borda: 1 centavo acima
```

---

### 5.2 Redundância 2 — `tests/test_tdd_frete.py`

**Localização:** classe `TestTDD_Red_FreteGratis`, linhas 47–53

```python
# Linha 47
def test_red_frete_zero_quando_total_acima_500(self):
    assert gp.calcular_frete(501.00) == 0.0   # ← argumento: 501.00

# Linha 51
def test_red_frete_zero_quando_total_igual_a_501(self):
    assert gp.calcular_frete(501.00) == 0.0   # ← argumento: 501.00 (IDÊNTICO)
```

**Diagnóstico:** O segundo nome `...igual_a_501` é descritivo do valor usado, mas o primeiro `...acima_500` deveria cobrir um cenário diferente (ex.: `800.00` ou `999.99`) para justificar sua existência como caso independente. Ambos exercitam o mesmo caminho de código.

**Correção recomendada:**

```python
def test_red_frete_zero_quando_total_acima_500(self):
    assert gp.calcular_frete(800.00) == 0.0   # valor genérico acima do limite

def test_red_frete_zero_quando_total_igual_a_501(self):
    assert gp.calcular_frete(501.00) == 0.0   # caso de borda próximo ao limite
```

---

### 5.3 Impacto e Classificação

| ID | Arquivo | Classe | Testes envolvidos | Tipo | Impacto em CI |
|----|---------|--------|-------------------|------|---------------|
| **RED-01** | `test_unitarios.py` | `TestCalcularFreteUnitario` | `test_frete_gratis_acima_500` × `test_frete_gratis_exatamente_500_01` | Redundância de assert | Nenhum (ambos passam) |
| **RED-02** | `test_tdd_frete.py` | `TestTDD_Red_FreteGratis` | `test_red_frete_zero_quando_total_acima_500` × `test_red_frete_zero_quando_total_igual_a_501` | Redundância de assert | Nenhum (ambos passam) |

Ambas as redundâncias são classificadas como **severity: Low / priority: Low** — não comprometem a confiabilidade da suíte, mas reduzem a clareza da intenção de teste e ocupam slots de cobertura sem acrescentar risco diferente.

---

## 6. Resumo Executivo

| Indicador | Resultado |
|-----------|-----------|
| Total de casos de teste | 48 |
| Testes passando | 48 (100%) |
| Testes falhando | 0 |
| Cobertura de código | **100%** (25/25 statements) |
| Requisitos rastreados | 17 |
| Requisitos cobertos | 17 (100%) |
| Defeitos no código original | 3 |
| Densidade de defeitos | 18,75 defeitos/KLOC |
| Redundâncias identificadas | 2 pares |
| Regressão após TDD Refactor | Zero |
