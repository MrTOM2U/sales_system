# =============================================================================
# gerenciador_pedidos.py
# Motor de regras de negócio do sistema de vendas.
# Análise crítica de QA incluída como comentários inline.
# =============================================================================

# ---------------------------------------------------------------------------
# ESTOQUE SIMULADO
# Dicionário global que representa o banco de dados de produtos em memória.
# Chave: código do produto (str). Valor: dict com nome, preço e quantidade.
# RISCO QA: estado global mutável — alterações persistem entre chamadas.
# ---------------------------------------------------------------------------
estoque_sistema = {
    "PROD01": {"nome": "Teclado Mecânico", "preco": 300.00, "quantidade": 4},
    "PROD02": {"nome": "Mouse Gamer",       "preco": 120.00, "quantidade": 10},
    "PROD03": {"nome": "Monitor UltraWide", "preco": 1500.00, "quantidade": 0},
    # PROD03 tem quantidade 0 — caso de borda importante para testes de estoque esgotado.
}

# ---------------------------------------------------------------------------
# CUPONS DE DESCONTO
# Dicionário global que mapeia código do cupom → percentual de desconto (float).
# Exemplo: "SENAC10" aplica 10% de desconto sobre o subtotal.
# ---------------------------------------------------------------------------
cupons_disponiveis = {
    "SENAC10":  0.10,   # 10% de desconto
    "FATESE20": 0.20,   # 20% de desconto
}


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL: processar_venda
# ---------------------------------------------------------------------------
def processar_venda(id_produto, quantidade, cupom_desconto=None):
    """
    Processa a venda de um produto aplicando descontos e calculando o total.

    Parâmetros:
        id_produto (str)       : Código do produto no estoque_sistema.
        quantidade (int)       : Quantidade desejada pelo cliente (deve ser > 0).
        cupom_desconto (str)   : Código de cupom opcional. Ignorado silenciosamente
                                 se inválido — comportamento documentado como risco.

    Retorna:
        dict com chaves: produto, subtotal, desconto, total, frete.

    Exceções:
        ValueError  : id_produto falsy OU quantidade <= 0 OU estoque insuficiente.
                      [BUG CORRIGIDO] O código original lançava IndexError para
                      estoque insuficiente — exceção semanticamente errada.
        KeyError    : produto não encontrado no catálogo.
        NameError   : [BUG CORRIGIDO] original retornava `descuento` (espanhol),
                      variável inexistente — causava NameError em tempo de execução.
    """

    # ------------------------------------------------------------------
    # GUARDA DE ENTRADA — validação dos parâmetros obrigatórios.
    # `not id_produto` captura None, string vazia, 0, False, etc.
    # `quantidade <= 0` rejeita zero e negativos.
    # ------------------------------------------------------------------
    if not id_produto or quantidade <= 0:
        raise ValueError("Parâmetros de entrada inválidos para a operação.")

    # ------------------------------------------------------------------
    # VERIFICAÇÃO DE EXISTÊNCIA DO PRODUTO no catálogo.
    # Lança KeyError se o código não existir — semanticamente correto
    # (acesso a chave inexistente em dicionário).
    # ------------------------------------------------------------------
    if id_produto not in estoque_sistema:
        raise KeyError("Produto solicitado inexistente no catálogo.")

    # Referência direta ao dicionário do produto (sem cópia — mutável).
    produto = estoque_sistema[id_produto]

    # ------------------------------------------------------------------
    # VERIFICAÇÃO DE ESTOQUE.
    # [BUG ORIGINAL] lançava IndexError — exceção de índice de lista,
    # semanticamente inadequada para contexto de negócio.
    # [CORRIGIDO] agora lança ValueError com mensagem clara.
    # ------------------------------------------------------------------
    if produto["quantidade"] < quantidade:
        raise ValueError("Quantidade requisitada indisponível no estoque.")

    # ------------------------------------------------------------------
    # CÁLCULO DO SUBTOTAL: preço unitário × quantidade solicitada.
    # ------------------------------------------------------------------
    subtotal = produto["preco"] * quantidade

    # ------------------------------------------------------------------
    # CÁLCULO DO DESCONTO.
    # Desconto só é aplicado se um cupom for fornecido E for válido.
    # RISCO QA: cupom inválido é silenciosamente ignorado (sem aviso).
    # ------------------------------------------------------------------
    desconto = 0.0

    if cupom_desconto:
        if cupom_desconto in cupons_disponiveis:
            # Percentual de desconto multiplicado pelo subtotal.
            desconto = subtotal * cupons_disponiveis[cupom_desconto]
        # else: cupom não encontrado → desconto permanece 0.0 (falha silenciosa)

    # ------------------------------------------------------------------
    # CÁLCULO DO TOTAL FINAL após aplicação do desconto.
    # ------------------------------------------------------------------
    total_final = subtotal - desconto

    # ------------------------------------------------------------------
    # CÁLCULO DO FRETE (nova regra de negócio — TDD Red-Green-Refactor).
    # Pedidos acima de R$ 500,00 → frete grátis.
    # Pedidos até R$ 500,00     → taxa fixa de R$ 20,00.
    # ------------------------------------------------------------------
    frete = calcular_frete(total_final)

    # ------------------------------------------------------------------
    # EFEITO COLATERAL: deduz a quantidade vendida do estoque global.
    # Necessário para testes de integração verificarem persistência.
    # ------------------------------------------------------------------
    produto["quantidade"] -= quantidade

    # ------------------------------------------------------------------
    # RETORNO: dicionário com resumo da venda.
    # [BUG ORIGINAL] chave "desconto" apontava para `descuento` (NameError).
    # [CORRIGIDO] referência correta à variável `desconto`.
    # ------------------------------------------------------------------
    return {
        "produto":   produto["nome"],
        "subtotal":  subtotal,
        "desconto":  desconto,       # BUG ORIGINAL: era `descuento` → NameError
        "total":     total_final,
        "frete":     frete,
    }                                # BUG ORIGINAL: chave `}` de fechamento ausente


# ---------------------------------------------------------------------------
# NOVA FUNÇÃO: calcular_frete
# Implementada via ciclo TDD (Red → Green → Refactor).
# Regra: total > 500.00 → frete = 0.0 / total <= 500.00 → frete = 20.0
# ---------------------------------------------------------------------------
def calcular_frete(total):
    """
    Calcula o valor do frete com base no total do pedido.

    Parâmetros:
        total (float): Valor total do pedido após descontos.

    Retorna:
        float: 0.0 se total > 500.00, caso contrário 20.0.

    Exceções:
        TypeError  : se `total` não for numérico.
        ValueError : se `total` for negativo.
    """
    if not isinstance(total, (int, float)):
        raise TypeError("O valor total deve ser numérico.")

    if total < 0:
        raise ValueError("O valor total não pode ser negativo.")

    # Regra de negócio central: limite de R$ 500,00.
    return 0.0 if total > 500.0 else 20.0
