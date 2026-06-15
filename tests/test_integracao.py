# =============================================================================
# test_integracao.py
# Testes de Integração — acoplamento do fluxo de venda com o estoque simulado.
# Foco: efeitos colaterais persistentes no dicionário estoque_sistema.
# =============================================================================

import copy
import pytest
import gerenciador_pedidos as gp


# ---------------------------------------------------------------------------
# FIXTURE DE ISOLAMENTO
# Restaura o estoque ao estado original após cada teste de integração.
# Essencial porque processar_venda muta o dicionário global.
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def restaurar_estoque():
    snapshot = copy.deepcopy(gp.estoque_sistema)
    yield
    gp.estoque_sistema.clear()
    gp.estoque_sistema.update(snapshot)


# =============================================================================
# BLOCO 1 — Persistência de Estoque após uma Venda
# =============================================================================

class TestPersistenciaEstoque:

    def test_estoque_diminui_apos_venda(self):
        """
        Cenário: venda de 2 unidades do PROD01.
        Esperado: estoque cai de 4 para 2.
        """
        estoque_antes = gp.estoque_sistema["PROD01"]["quantidade"]
        gp.processar_venda("PROD01", 2)
        estoque_depois = gp.estoque_sistema["PROD01"]["quantidade"]

        assert estoque_depois == estoque_antes - 2

    def test_estoque_zera_apos_venda_total(self):
        """
        Cenário: cliente compra todas as 4 unidades disponíveis.
        Esperado: estoque vai a zero — produto esgotado.
        """
        gp.processar_venda("PROD01", 4)
        assert gp.estoque_sistema["PROD01"]["quantidade"] == 0

    def test_produto_esgotado_nao_aceita_nova_venda(self):
        """
        Cenário de integração sequencial:
          1. Vende todas as unidades do PROD01.
          2. Tenta vender mais uma unidade.
        Esperado: segunda venda falha com ValueError.
        """
        gp.processar_venda("PROD01", 4)           # esgota o estoque
        with pytest.raises(ValueError, match="indisponível"):
            gp.processar_venda("PROD01", 1)       # não há mais estoque

    def test_estoque_outros_produtos_nao_afetado(self):
        """
        Venda de PROD01 não deve alterar o estoque de PROD02.
        Verifica que o efeito colateral é cirúrgico.
        """
        estoque_prod02_antes = gp.estoque_sistema["PROD02"]["quantidade"]
        gp.processar_venda("PROD01", 1)
        assert gp.estoque_sistema["PROD02"]["quantidade"] == estoque_prod02_antes


# =============================================================================
# BLOCO 2 — Vendas Sequenciais (múltiplas transações)
# =============================================================================

class TestVendasSequenciais:

    def test_duas_vendas_sequenciais_acumulam_reducao(self):
        """
        Cenário: dois clientes compram do mesmo produto em sequência.
          Venda 1: 1 unidade → estoque: 4 → 3
          Venda 2: 2 unidades → estoque: 3 → 1
        """
        gp.processar_venda("PROD01", 1)
        gp.processar_venda("PROD01", 2)
        assert gp.estoque_sistema["PROD01"]["quantidade"] == 1

    def test_tres_vendas_diferentes_produtos(self):
        """
        Cenário: vendas simultâneas de produtos diferentes.
        Esperado: cada estoque reduzido independentemente.
        """
        gp.processar_venda("PROD01", 1)   # 4 → 3
        gp.processar_venda("PROD02", 3)   # 10 → 7
        gp.processar_venda("PROD01", 2)   # 3 → 1

        assert gp.estoque_sistema["PROD01"]["quantidade"] == 1
        assert gp.estoque_sistema["PROD02"]["quantidade"] == 7

    def test_venda_com_cupom_nao_afeta_estoque_diferente(self):
        """
        Cupom de desconto não deve causar efeito colateral no estoque.
        """
        estoque_antes = gp.estoque_sistema["PROD02"]["quantidade"]
        gp.processar_venda("PROD02", 2, cupom_desconto="SENAC10")
        assert gp.estoque_sistema["PROD02"]["quantidade"] == estoque_antes - 2


# =============================================================================
# BLOCO 3 — Consistência do Fluxo Completo
# Testa o pipeline ponta a ponta: entrada → processamento → estado persistido.
# =============================================================================

class TestFluxoCompleto:

    def test_fluxo_completo_com_desconto_e_frete(self):
        """
        Cenário end-to-end:
          - Produto: PROD01 (R$ 300,00 × 2 = R$ 600,00)
          - Cupom: SENAC10 (10% de desconto → R$ 60,00)
          - Total: R$ 540,00 > R$ 500,00 → frete grátis
          - Estoque deve reduzir de 4 para 2
        """
        resultado = gp.processar_venda("PROD01", 2, cupom_desconto="SENAC10")

        assert resultado["subtotal"] == pytest.approx(600.00)
        assert resultado["desconto"] == pytest.approx(60.00)
        assert resultado["total"]    == pytest.approx(540.00)
        assert resultado["frete"]    == 0.0
        assert gp.estoque_sistema["PROD01"]["quantidade"] == 2

    def test_fluxo_completo_sem_desconto_com_frete(self):
        """
        Cenário end-to-end:
          - Produto: PROD02 (R$ 120,00 × 1 = R$ 120,00)
          - Sem cupom
          - Total: R$ 120,00 ≤ R$ 500,00 → frete R$ 20,00
          - Estoque deve reduzir de 10 para 9
        """
        resultado = gp.processar_venda("PROD02", 1)

        assert resultado["subtotal"] == 120.00
        assert resultado["desconto"] == 0.0
        assert resultado["total"]    == 120.00
        assert resultado["frete"]    == 20.0
        assert gp.estoque_sistema["PROD02"]["quantidade"] == 9

    def test_falha_nao_altera_estoque(self):
        """
        Quando processar_venda lança exceção (estoque insuficiente),
        o estoque NÃO deve ser alterado (transação deve ser atômica).
        """
        estoque_antes = gp.estoque_sistema["PROD01"]["quantidade"]
        with pytest.raises(ValueError):
            gp.processar_venda("PROD01", 99)
        assert gp.estoque_sistema["PROD01"]["quantidade"] == estoque_antes
