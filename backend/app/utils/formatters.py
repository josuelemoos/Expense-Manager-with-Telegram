from decimal import Decimal


def format_brl(value: Decimal | int | float) -> str:
    amount = Decimal(str(value)).quantize(Decimal("0.01"))
    formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"
