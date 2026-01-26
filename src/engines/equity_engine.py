from typing import Dict
from enum import Enum


class CompanyStage(Enum):
    """
    Company funding stage determines equity risk discount.

    Risk discounts reflect the probability-weighted value of equity
    based on typical outcomes at each stage.
    """
    PUBLIC = "public"           # 0% discount - liquid, tradeable stock
    PRE_IPO = "pre_ipo"         # 15% discount - filed S-1, high confidence
    LATE_STAGE = "late_stage"   # 30% discount - Series D+, Unicorn ($1B+ valuation)
    GROWTH = "growth"           # 50% discount - Series B-C
    EARLY = "early"             # 70% discount - Seed to Series A


# Risk discounts by company stage
STAGE_DISCOUNTS = {
    CompanyStage.PUBLIC: 0.0,
    CompanyStage.PRE_IPO: 0.15,
    CompanyStage.LATE_STAGE: 0.30,
    CompanyStage.GROWTH: 0.50,
    CompanyStage.EARLY: 0.70,
}

# Human-readable descriptions for each stage
STAGE_DESCRIPTIONS = {
    CompanyStage.PUBLIC: "Public stock - Can sell immediately upon vesting",
    CompanyStage.PRE_IPO: "Pre-IPO - Filed S-1, IPO expected within 12 months",
    CompanyStage.LATE_STAGE: "Late-stage private - Series D+ or Unicorn valuation",
    CompanyStage.GROWTH: "Growth stage - Series B-C, product-market fit established",
    CompanyStage.EARLY: "Early stage - Seed to Series A, high execution risk",
}


def calculate_rsu_value(
    total_grant: float,
    vesting_years: int = 4,
    current_stock_price: float = 0,
    is_public_company: bool = True,
    company_stage: CompanyStage = None
) -> Dict[str, float]:
    """
    Calculates the value of RSU (Restricted Stock Unit) grants with risk adjustments.

    Risk discounts are applied based on company stage:
    - Public: 0% (liquid stock)
    - Pre-IPO: 15% (S-1 filed, high confidence)
    - Late-stage: 30% (Series D+, Unicorn)
    - Growth: 50% (Series B-C)
    - Early: 70% (Seed-A)

    Args:
        total_grant: Total dollar value of equity grant
        vesting_years: Number of years for full vesting (default 4)
        current_stock_price: Current stock price (for display only)
        is_public_company: Whether the company is publicly traded (legacy param)
        company_stage: CompanyStage enum for precise risk adjustment

    Returns:
        Dictionary containing:
            - total_grant_value: Total equity value
            - adjusted_value: Risk-adjusted value
            - annualized_value: Yearly vesting amount (adjusted)
            - monthly_value: Monthly vesting amount (adjusted)
            - risk_discount: Percentage discount applied
            - liquidity_note: Human-readable liquidity explanation
            - company_stage: The stage used for calculation
    """
    if total_grant <= 0:
        return {
            "total_grant_value": 0,
            "adjusted_value": 0,
            "annualized_value": 0,
            "monthly_value": 0,
            "risk_discount": 0,
            "liquidity_note": "No equity grant",
            "company_stage": None
        }

    # Determine company stage (use explicit stage, or infer from legacy boolean)
    if company_stage is not None:
        stage = company_stage
    elif is_public_company:
        stage = CompanyStage.PUBLIC
    else:
        # Default private to GROWTH for backward compatibility (was 50%)
        stage = CompanyStage.GROWTH

    risk_discount = STAGE_DISCOUNTS[stage]
    adjusted_value = total_grant * (1 - risk_discount)
    liquidity_note = STAGE_DESCRIPTIONS[stage]

    # Add discount info to note for non-public
    if risk_discount > 0:
        liquidity_note += f" - {int(risk_discount * 100)}% risk discount applied"

    annualized_value = adjusted_value / vesting_years
    monthly_value = annualized_value / 12

    return {
        "total_grant_value": total_grant,
        "adjusted_value": adjusted_value,
        "annualized_value": annualized_value,
        "monthly_value": monthly_value,
        "risk_discount": risk_discount * 100,
        "liquidity_note": liquidity_note,
        "company_stage": stage.value if stage else None
    }


def calculate_vesting_schedule(
    total_grant: float,
    vesting_years: int = 4,
    cliff_months: int = 12,
    is_public_company: bool = True,
    company_stage: CompanyStage = None
) -> Dict[int, Dict[str, float]]:
    """
    Calculates a detailed vesting schedule with 1-year cliff.

    Args:
        total_grant: Total dollar value of equity grant
        vesting_years: Number of years for full vesting
        cliff_months: Months before first vesting (typically 12)
        is_public_company: Whether company is publicly traded (legacy param)
        company_stage: CompanyStage enum for precise risk adjustment

    Returns:
        Dictionary mapping year to vesting details:
            - vested_this_year: Amount vesting in this year
            - cumulative_vested: Total vested through this year
            - remaining_unvested: Amount still unvested
    """
    # Determine company stage
    if company_stage is not None:
        stage = company_stage
    elif is_public_company:
        stage = CompanyStage.PUBLIC
    else:
        stage = CompanyStage.GROWTH

    risk_discount = STAGE_DISCOUNTS[stage]
    adjusted_total = total_grant * (1 - risk_discount)
    
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
        offer_a: First offer dict with total_grant, vesting_years, is_public/company_stage
        offer_b: Second offer dict with total_grant, vesting_years, is_public/company_stage

    Returns:
        Comparison dict with analysis and recommendation
    """
    # Parse company stage from offer dict
    stage_a = offer_a.get("company_stage")
    if isinstance(stage_a, str):
        stage_a = CompanyStage(stage_a)

    stage_b = offer_b.get("company_stage")
    if isinstance(stage_b, str):
        stage_b = CompanyStage(stage_b)

    rsu_a = calculate_rsu_value(
        offer_a.get("total_grant", 0),
        offer_a.get("vesting_years", 4),
        0,
        offer_a.get("is_public", True),
        stage_a
    )

    rsu_b = calculate_rsu_value(
        offer_b.get("total_grant", 0),
        offer_b.get("vesting_years", 4),
        0,
        offer_b.get("is_public", True),
        stage_b
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
