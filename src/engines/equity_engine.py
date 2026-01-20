from typing import Dict


def calculate_rsu_value(
    total_grant: float,
    vesting_years: int = 4,
    current_stock_price: float = 0,
    is_public_company: bool = True
) -> Dict[str, float]:
    """
    Calculates the value of RSU (Restricted Stock Unit) grants with risk adjustments.
    
    Args:
        total_grant: Total dollar value of equity grant
        vesting_years: Number of years for full vesting (default 4)
        current_stock_price: Current stock price (for display only)
        is_public_company: Whether the company is publicly traded
        
    Returns:
        Dictionary containing:
            - total_grant_value: Total equity value
            - adjusted_value: Risk-adjusted value (50% discount for private)
            - annualized_value: Yearly vesting amount (adjusted)
            - monthly_value: Monthly vesting amount (adjusted)
            - risk_discount: Percentage discount applied
            - liquidity_note: Human-readable liquidity explanation
    """
    if total_grant <= 0:
        return {
            "total_grant_value": 0,
            "adjusted_value": 0,
            "annualized_value": 0,
            "monthly_value": 0,
            "risk_discount": 0,
            "liquidity_note": "No equity grant"
        }
    
    if is_public_company:
        risk_discount = 0.0
        adjusted_value = total_grant
        liquidity_note = "Public stock - Can sell immediately upon vesting"
    else:
        risk_discount = 0.50
        adjusted_value = total_grant * (1 - risk_discount)
        liquidity_note = "Private stock - 50% risk discount applied (illiquid until IPO/acquisition)"
    
    annualized_value = adjusted_value / vesting_years
    monthly_value = annualized_value / 12
    
    return {
        "total_grant_value": total_grant,
        "adjusted_value": adjusted_value,
        "annualized_value": annualized_value,
        "monthly_value": monthly_value,
        "risk_discount": risk_discount * 100,
        "liquidity_note": liquidity_note
    }


def calculate_vesting_schedule(
    total_grant: float,
    vesting_years: int = 4,
    cliff_months: int = 12,
    is_public_company: bool = True
) -> Dict[int, Dict[str, float]]:
    """
    Calculates a detailed vesting schedule with 1-year cliff.
    
    Args:
        total_grant: Total dollar value of equity grant
        vesting_years: Number of years for full vesting
        cliff_months: Months before first vesting (typically 12)
        is_public_company: Whether company is publicly traded
        
    Returns:
        Dictionary mapping year to vesting details:
            - vested_this_year: Amount vesting in this year
            - cumulative_vested: Total vested through this year
            - remaining_unvested: Amount still unvested
    """
    risk_adjustment = 1.0 if is_public_company else 0.5
    adjusted_total = total_grant * risk_adjustment
    
    schedule = {}
    annual_vest = adjusted_total / vesting_years
    
    for year in range(1, vesting_years + 1):
        if year == 1:
            if cliff_months >= 12:
                vested_this_year = annual_vest
            else:
                vested_this_year = annual_vest * (cliff_months / 12)
        else:
            vested_this_year = annual_vest
        
        cumulative = sum(schedule[y]["vested_this_year"] for y in range(1, year)) + vested_this_year if year > 1 else vested_this_year
        
        schedule[year] = {
            "vested_this_year": vested_this_year,
            "cumulative_vested": cumulative,
            "remaining_unvested": adjusted_total - cumulative
        }
    
    return schedule


def compare_equity_offers(
    offer_a: Dict[str, float],
    offer_b: Dict[str, float]
) -> Dict[str, any]:
    """
    Compares two equity offers side-by-side.
    
    Args:
        offer_a: First offer dict with total_grant, vesting_years, is_public
        offer_b: Second offer dict with total_grant, vesting_years, is_public
        
    Returns:
        Comparison dict with analysis and recommendation
    """
    rsu_a = calculate_rsu_value(
        offer_a.get("total_grant", 0),
        offer_a.get("vesting_years", 4),
        0,
        offer_a.get("is_public", True)
    )
    
    rsu_b = calculate_rsu_value(
        offer_b.get("total_grant", 0),
        offer_b.get("vesting_years", 4),
        0,
        offer_b.get("is_public", True)
    )
    
    monthly_diff = rsu_a["monthly_value"] - rsu_b["monthly_value"]
    
    winner = "Offer A" if monthly_diff > 0 else "Offer B" if monthly_diff < 0 else "Tie"
    
    return {
        "offer_a_monthly": rsu_a["monthly_value"],
        "offer_b_monthly": rsu_b["monthly_value"],
        "monthly_difference": abs(monthly_diff),
        "winner": winner,
        "note": f"{winner} provides ${abs(monthly_diff):,.0f} more per month in adjusted equity value"
    }
