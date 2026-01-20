def format_currency(value: float, show_cents: bool = False) -> str:
    if show_cents:
        return f"${value:,.2f}"
    return f"${value:,.0f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def format_delta(value: float, show_cents: bool = False) -> str:
    prefix = "+" if value > 0 else ""
    return f"{prefix}{format_currency(value, show_cents)}"


def annual_to_monthly(annual_value: float) -> float:
    return annual_value / 12


def monthly_to_annual(monthly_value: float) -> float:
    return monthly_value * 12
