# =============================================================================
# test_unitarios.py
# Testes Unitários do motor de regras de negócio.
# Cobertura: todos os branches if/else, caminho feliz e fluxos de exceção.
# =============================================================================

import copy
import pytest
import gerenciador_pedidos as gp


# ---------------------------------------------------------------------------
# FIXTURES
# Garante isolamento: cada teste recebe cópias limpas do estado global,
# evitando que efeitos colaterais de uma venda contaminem outros testes.
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def restaurar_estoque():
    """Snapshot do estoque antes de cada teste; restaura após o término."""
    snapshot = copy.deepcopy(gp.estoque_sistema)
    yield
    gp.estoque_sistema.clear()
    gp.estoque_sistema.update(snapshot)


# =============================================================================
# BLOCO 1 — Caminho Feliz (Happy Path)
# Fluxos que devem funcionar corretamente sem exceções.
# =============================================================================

class TestCaminhoFeliz:

    def test_venda_simples_sem_cupom(self):
        """Venda válida sem cupom: subtotal, desconto zero e total corretos."""
        resultado = gp.processar_venda("PROD02", 2)

        assert resultado["produto"]  == "Mouse Gamer"
        assert resultado["subtotal"] == 240.00   # 120.00 × 2
        assert resultado["desconto"] == 0.0
        assert resultado["total"]    == 240.00

    def test_venda_com_cupom_senac10(self):
        """Cupom SENAC10 aplica 10% de desconto sobre o subtotal."""
        resultado = gp.processar_venda("PROD01", 1, cupom_desconto="SENAC10")

        assert resultado["subtotal"] == 300.00
        assert resultado["desconto"] == pytest.approx(30.00)   # 10% de 300
        assert resultado["total"]    == pytest.approx(270.00)

    def test_venda_com_cupom_fatese20(self):
        """Cupom FATESE20 aplica 20% de desconto sobre o subtotal."""
        resultado = gp.processar_venda("PROD02", 1, cupom_desconto="FATESE20")

        assert resultado["subtotal"] == 120.00
        assert resultado["desconto"] == pytest.approx(24.00)   # 20% de 120
        assert resultado["total"]    == pytest.approx(96.00)

    def test_retorno_contem_chaves_obrigatorias(self):
        """O dicionário retornado deve conter todas as chaves esperadas."""
        resultado = gp.processar_venda("PROD02", 1)
        chaves_esperadas = {"produto", "subtotal", "desconto", "total", "frete"}
        assert chaves_esperadas.issubset(resultado.keys())

    def test_quantidade_maxima_disponivel(self):
        """Venda de toda a quantidade em estoque deve funcionar."""
        resultado = gp.processar_venda("PROD01", 4)   # estoque exato = 4
        assert resultado["subtotal"] == 1200.00        # 300.00 × 4


# =============================================================================
# BLOCO 2 — Fluxos de Exceção
# Garantem que erros são lançados com o tipo correto.
# =============================================================================

class TestExcecoes:

    def test_id_produto_nulo_lanca_valueerror(self):
        """id_produto None deve lançar ValueError."""
        with pytest.raises(ValueError, match="inválidos"):
            gp.processar_venda(None, 1)

    def test_id_produto_vazio_lanca_valueerror(self):
        """String vazia é falsy — deve lançar ValueError."""
        with pytest.raises(ValueError):
            gp.processar_venda("", 1)

    def test_quantidade_zero_lanca_valueerror(self):
        """Quantidade zero não faz sentido de negócio — deve lançar ValueError."""
        with pytest.raises(ValueError):
            gp.processar_venda("PROD01", 0)

    def test_quantidade_negativa_lanca_valueerror(self):
        """Quantidade negativa é inválida — deve lançar ValueError."""
        with pytest.raises(ValueError):
            gp.processar_venda("PROD01", -5)

    def test_produto_inexistente_lanca_keyerror(self):
        """Código de produto fora do catálogo deve lançar KeyError."""
        with pytest.raises(KeyError, match="inexistente"):
            gp.processar_venda("PROD_INVALIDO", 1)

    def test_estoque_insuficiente_lanca_valueerror(self):
        """
        Quantidade acima do estoque deve lançar ValueError.
        [ANÁLISE DE BUG] Código original lançava IndexError — tipo inadequado.
        Corrigido para ValueError, que representa violação de regra de negócio.
        """
        with pytest.raises(ValueError, match="indisponível"):
            gp.processar_venda("PROD01", 99)   # estoque tem apenas 4

    def test_produto_sem_estoque_lanca_valueerror(self):
        """PROD03 tem quantidade 0 — qualquer venda deve falhar."""
        with pytest.raises(ValueError):
            gp.processar_venda("PROD03", 1)


# =============================================================================
# BLOCO 3 — Branches de Cupom
# Cobre os dois ramos do if/else de desconto.
# =============================================================================

class TestBranchesCupom:

    def test_cupom_invalido_nao_aplica_desconto(self):
        """
        Cupom inexistente deve ser ignorado silenciosamente (desconto = 0).
        RISCO documentado: ausência de feedback ao usuário sobre cupom inválido.
        """
        resultado = gp.processar_venda("PROD02", 1, cupom_desconto="CUPOM_FALSO")
        assert resultado["desconto"] == 0.0
        assert resultado["total"]    == 120.00

    def test_sem_cupom_desconto_zero(self):
        """Ausência de cupom (None) deve resultar em desconto zero."""
        resultado = gp.processar_venda("PROD02", 1, cupom_desconto=None)
        assert resultado["desconto"] == 0.0

    def test_cupom_vazio_desconto_zero(self):
        """String vazia como cupom é falsy — não entra no branch de desconto."""
        resultado = gp.processar_venda("PROD02", 1, cupom_desconto="")
        assert resultado["desconto"] == 0.0


# =============================================================================
# BLOCO 4 — Regra de Frete (unitária)
# Testa calcular_frete de forma isolada, sem passar por processar_venda.
# =============================================================================

class TestCalcularFreteUnitario:

    def test_frete_gratis_acima_500(self):
        assert gp.calcular_frete(500.01) == 0.0

    def test_frete_gratis_exatamente_500_01(self):
        assert gp.calcular_frete(500.01) == 0.0

    def test_frete_cobrado_exatamente_500(self):
        """Limite: exatamente R$ 500,00 paga frete."""
        assert gp.calcular_frete(500.00) == 20.0

    def test_frete_cobrado_abaixo_500(self):
        assert gp.calcular_frete(100.00) == 20.0

    def test_frete_total_zero_paga_frete(self):
        assert gp.calcular_frete(0.0) == 20.0

    def test_frete_tipo_invalido_lanca_typeerror(self):
        with pytest.raises(TypeError):
            gp.calcular_frete("quinhentos")

    def test_frete_negativo_lanca_valueerror(self):
        with pytest.raises(ValueError):
            gp.calcular_frete(-1.0)
