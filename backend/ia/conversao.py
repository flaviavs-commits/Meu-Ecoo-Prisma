from decimal import Decimal, ROUND_UP


_QUANTUM = Decimal("0.0001")


def custo_para_creditos(custo_bruto, *, custo_por_credito, margem):
    """Converte custo monetario em creditos e sempre arredonda a favor do sistema."""
    custo_bruto = Decimal(custo_bruto)
    custo_por_credito = Decimal(custo_por_credito)
    margem = Decimal(margem)
    if custo_bruto < 0 or custo_por_credito <= 0 or margem <= 0:
        raise ValueError("Custo, taxa e margem precisam ser valores positivos.")
    return ((custo_bruto * margem) / custo_por_credito).quantize(
        _QUANTUM, rounding=ROUND_UP
    )
