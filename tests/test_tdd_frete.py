# =============================================================================
# test_tdd_frete.py
# Ciclo TDD — Red → Green → Refactor para a regra de frete.
#
# HISTÓRIA DE USUÁRIO (Sprint 1):
#   Como cliente, quero que pedidos acima de R$ 500,00 tenham frete grátis
#   automático, para que eu seja incentivado a comprar mais itens.
#
# CRITÉRIOS DE ACEITAÇÃO:
#   - total > R$ 500,00  → frete = R$ 0,00
#   - total <= R$ 500,00 → frete = R$ 20,00
#   - total negativo     → ValueError
#   - total não numérico → TypeError
#
# DEFINITION OF DONE (DoD):
#   [ ] Todos os testes deste arquivo passam (pytest -v)
#   [ ] Cobertura da função calcular_frete >= 100%
#   [ ] Função integrada ao retorno de processar_venda
#   [ ] Code review aprovado
# =============================================================================

import copy
import pytest
import gerenciador_pedidos as gp


@pytest.fixture(autouse=True)
def restaurar_estoque():
    snapshot = copy.deepcopy(gp.estoque_sistema)
    yield
    gp.estoque_sistema.clear()
    gp.estoque_sistema.update(snapshot)


# =============================================================================
# FASE RED — Testes escritos ANTES da implementação.
# Neste estágio, todos falhariam caso calcular_frete não existisse.
# Os comentários documentam a intenção original do ciclo TDD.
# =============================================================================

class TestTDD_Red_FreteGratis:
    """
    RED: estes testes foram escritos primeiro, antes de calcular_frete existir.
    Cada assert documenta o comportamento ESPERADO que deve ser implementado.
    """

    def test_red_frete_zero_quando_total_acima_500(self):
        # Comportamento esperado: nenhum frete para compras altas.
        assert gp.calcular_frete(501.00) == 0.0

    def test_red_frete_zero_quando_total_igual_a_501(self):
        assert gp.calcular_frete(501.00) == 0.0

    def test_red_frete_cobrado_quando_total_igual_500(self):
        # Limite exato de R$ 500,00 → ainda paga frete.
        assert gp.calcular_frete(500.00) == 20.0

    def test_red_frete_cobrado_quando_total_abaixo_500(self):
        assert gp.calcular_frete(200.00) == 20.0

    def test_red_frete_cobrado_quando_total_zero(self):
        assert gp.calcular_frete(0.0) == 20.0


# =============================================================================
# FASE GREEN — Implementação mínima para fazer os testes passarem.
# O código final de calcular_frete em gerenciador_pedidos.py representa
# a versão GREEN: `return 0.0 if total > 500.0 else 20.0`
# =============================================================================

class TestTDD_Green_Verificacao:
    """
    GREEN: validação de que a implementação mínima satisfaz todos os critérios
    de aceitação definidos na história de usuário.
    """

    def test_green_retorno_float_frete_gratis(self):
        """O retorno deve ser float, não int."""
        resultado = gp.calcular_frete(1000.0)
        assert isinstance(resultado, float)
        assert resultado == 0.0

    def test_green_retorno_float_frete_cobrado(self):
        resultado = gp.calcular_frete(50.0)
        assert isinstance(resultado, float)
        assert resultado == 20.0

    def test_green_limite_exato_500_paga_frete(self):
        """Caso de borda crítico: exatamente 500.00 NÃO é acima de 500."""
        assert gp.calcular_frete(500.00) == 20.0

    def test_green_um_centavo_acima_do_limite(self):
        """Um centavo acima garante frete grátis."""
        assert gp.calcular_frete(500.01) == 0.0


# =============================================================================
# FASE REFACTOR — Testes de robustez adicionados após a implementação inicial.
# O refactor não muda o comportamento, mas melhora a qualidade da função:
# validações de tipo e valor foram adicionadas a calcular_frete.
# =============================================================================

class TestTDD_Refactor_Robustez:
    """
    REFACTOR: testes que validam as melhorias feitas após o GREEN.
    Nenhum comportamento existente foi quebrado (regressão zero).
    """

    def test_refactor_tipo_string_lanca_typeerror(self):
        """Entradas não numéricas devem ser rejeitadas explicitamente."""
        with pytest.raises(TypeError, match="numérico"):
            gp.calcular_frete("500")

    def test_refactor_tipo_none_lanca_typeerror(self):
        with pytest.raises(TypeError):
            gp.calcular_frete(None)

    def test_refactor_tipo_lista_lanca_typeerror(self):
        with pytest.raises(TypeError):
            gp.calcular_frete([500])

    def test_refactor_valor_negativo_lanca_valueerror(self):
        """Totais negativos são impossíveis no domínio de negócio."""
        with pytest.raises(ValueError, match="negativo"):
            gp.calcular_frete(-0.01)

    def test_refactor_inteiro_aceito_como_total(self):
        """int é subconjunto numérico válido — deve ser aceito."""
        assert gp.calcular_frete(600) == 0.0
        assert gp.calcular_frete(100) == 20.0


# =============================================================================
# INTEGRAÇÃO SUPERFICIAL — frete retornado por processar_venda
# =============================================================================

class TestFreteIntegradoAoProcessarVenda:
    """
    Garante que a chave 'frete' aparece corretamente no retorno de processar_venda.
    """

    def test_processar_venda_retorna_frete_gratis_monitor(self):
        """Monitor UltraWide custa R$ 1500 → frete grátis (mas sem estoque)."""
        # PROD03 tem estoque 0; usa PROD01 (300×2 = 600 > 500 → frete grátis)
        resultado = gp.processar_venda("PROD01", 2)
        assert resultado["total"] == 600.00
        assert resultado["frete"] == 0.0

    def test_processar_venda_retorna_frete_cobrado_mouse(self):
        """Mouse Gamer custa R$ 120 × 1 = R$ 120 ≤ 500 → paga frete."""
        resultado = gp.processar_venda("PROD02", 1)
        assert resultado["total"] == 120.00
        assert resultado["frete"] == 20.0
