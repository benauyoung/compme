import json
import os
from typing import Dict, Optional, Tuple
from engines.bah_engine import bah_fetcher


def load_data(filename: str) -> Dict:
    """
    Utility to load JSON data from the data directory.
    
    Args:
        filename: Name of the JSON file to load
        
    Returns:
        Dictionary containing the JSON data, empty dict if file not found
    """
    base_path = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_path, 'data', filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_base_pay(rank: str, years_of_service: int) -> float:
    """
    Fetches monthly base pay from 2025 military pay tables.
    Falls back to closest year if exact match not found.
    
    Args:
        rank: Military rank (e.g., "E-6", "O-3")
        years_of_service: Total years of service
        
    Returns:
        Monthly base pay amount
    """
    data = load_data('base_pay_2025.json')
    if rank not in data:
        return 0.0
    
    pay_scale = data[rank]
    
    sorted_years = sorted(pay_scale.keys(), key=lambda x: 0 if x == "<2" else int(x))
    
    best_match = "<2"
    for y_key in sorted_years:
        y_val = 0 if y_key == "<2" else int(y_key)
        if years_of_service >= y_val:
            best_match = y_key
        else:
            break
            
    return float(pay_scale.get(best_match, 0))


def get_bah_rate(location: str, rank: str, has_dependents: bool) -> Tuple[float, str]:
    """
    Fetches BAH (Basic Allowance for Housing) rate from official 2026 data.
    Returns both the rate and the source of the data.
    
    Args:
        location: Duty station name (e.g., "SAN DIEGO, CA")
        rank: Military rank (e.g., "E-6", "O-3")
        has_dependents: Whether service member has dependents
        
    Returns:
        Tuple of (monthly BAH amount, source)
        Source is: "official_2026", "manual", or "not_found"
    """
    rate, source = bah_fetcher.get_rate(location, rank, has_dependents)
    return rate, source


def get_bas_rate(rank: str) -> float:
    """
    Returns BAS (Basic Allowance for Subsistence) rate for 2025.
    
    Args:
        rank: Military rank (e.g., "E-6", "O-3")
        
    Returns:
        Monthly BAS amount (Officers: $320.78, Enlisted: $465.77)
    """
    is_officer = rank.upper().startswith('O')
    return 320.78 if is_officer else 465.77


def calculate_tax_advantage(base_pay: float, bah: float, bas: float, filing_status: str) -> float:
    """
    Calculates the tax advantage value of non-taxable military allowances.
    This represents how much additional taxable income a civilian would need
    to match the military member's after-tax purchasing power.
    
    Args:
        base_pay: Monthly base pay (taxable)
        bah: Monthly BAH (non-taxable)
        bas: Monthly BAS (non-taxable)
        filing_status: "single" or "married"
        
    Returns:
        Tax advantage value in dollars
    """
    annual_base = base_pay * 12
    annual_allowances = (bah + bas) * 12
    
    standard_deduction = 15750 if filing_status.lower() == "single" else 31500
    
    taxable_income = max(0, annual_base - standard_deduction)
    
    effective_rate = 0.15 if taxable_income < 50000 else 0.22
    
    tax_advantage_annual = annual_allowances * effective_rate
    
    return tax_advantage_annual / 12


def calculate_rmc(rank: str, years_of_service: int, location: str, has_dependents: bool, filing_status: str = "single", manual_bah: Optional[float] = None) -> Dict[str, float]:
    """
    Calculates Regular Military Compensation (RMC).
    Returns dictionary with breakdown of taxable vs non-taxable components.
    
    Args:
        rank: Military rank (e.g., "E-6", "O-3")
        years_of_service: Total years of service
        location: Duty station name (e.g., "SAN DIEGO, CA")
        has_dependents: Whether service member has dependents
        filing_status: "single" or "married"
        manual_bah: Optional manual BAH override
        
    Returns:
        Dictionary containing:
            - base_pay_monthly: Monthly base pay (taxable)
            - bah_monthly: Monthly BAH (non-taxable)
            - bas_monthly: Monthly BAS (non-taxable)
            - tax_advantage_monthly: Tax advantage value
            - total_monthly: Total monthly compensation
            - taxable_monthly: Only base pay
            - nontaxable_monthly: BAH + BAS
            - bah_source: Source of BAH data
    """
    base_pay_monthly = get_base_pay(rank, years_of_service)
    
    # Handle manual BAH override
    if manual_bah is not None and manual_bah > 0:
        bah_monthly = manual_bah
        bah_source = "manual"
    else:
        bah_monthly, bah_source = get_bah_rate(location, rank, has_dependents)
    
    bas_monthly = get_bas_rate(rank)
    
    tax_advantage = calculate_tax_advantage(base_pay_monthly, bah_monthly, bas_monthly, filing_status)
    
    total_monthly = base_pay_monthly + bah_monthly + bas_monthly
    
    return {
        "base_pay_monthly": base_pay_monthly,
        "bah_monthly": bah_monthly,
        "bas_monthly": bas_monthly,
        "tax_advantage_monthly": tax_advantage,
        "total_monthly": total_monthly,
        "taxable_monthly": base_pay_monthly,
        "nontaxable_monthly": bah_monthly + bas_monthly,
        "bah_source": bah_source
    }
