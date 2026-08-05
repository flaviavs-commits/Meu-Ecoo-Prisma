from decimal import Decimal, ROUND_UP


_QUANTUM = Decimal("0.0001")


def custo_para_percentual(custo_bruto, *, custo_dolar_por_percentual, margem):
    """Normaliza o custo de qualquer fornecedor em percentual de uso."""
    custo_bruto = Decimal(custo_bruto)
    custo_dolar_por_percentual = Decimal(custo_dolar_por_percentual)
    margem = Decimal(margem)
    if custo_bruto < 0 or custo_dolar_por_percentual <= 0 or margem <= 0:
        raise ValueError("Custo, referencia e margem precisam ser valores positivos.")
    return ((custo_bruto * margem) / custo_dolar_por_percentual).quantize(
        _QUANTUM, rounding=ROUND_UP
    )
