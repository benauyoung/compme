import json
import os
from typing import Dict, Optional


def load_tax_data() -> Dict:
    """
    Loads tax bracket data from JSON file.
    
    Returns:
        Dictionary containing federal and state tax data
    """
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tax_brackets_mock.json')
    with open(data_path, 'r') as f:
        return json.load(f)


def calculate_federal_tax(gross_income: float, filing_status: str = "single") -> float:
    """
    Calculates federal income tax using 2025 progressive tax brackets.
    
    Args:
        gross_income: Annual gross income
        filing_status: "single" or "married"
        
    Returns:
        Federal tax amount
    """
    tax_data = load_tax_data()
    
    standard_deduction = 15750 if filing_status.lower() == "single" else 31500
    taxable_income = max(0, gross_income - standard_deduction)
    
    brackets = tax_data['federal'][filing_status.lower()]
    
    fed_tax = 0
    previous_limit = 0
    
    for bracket in brackets:
        limit = bracket['max']
        rate = bracket['rate']
        
        if taxable_income > previous_limit:
            bracket_income = min(taxable_income, limit) - previous_limit
            fed_tax += bracket_income * rate
            previous_limit = limit
        else:
            break
            
    return fed_tax


def calculate_state_tax(gross_income: float, state: str, filing_status: str = "single") -> float:
    """
    Calculate state income tax using 2025 progressive tax tables.
    
    Supports progressive brackets for:
    - CA (California): 1% to 13.3%
    - VA (Virginia): 2% to 5.75%
    - MD (Maryland): 2% to 5.75%
    - NY (New York): 4% to 10.9%
    - NC (North Carolina): Flat 4.75%
    - HI (Hawaii): 1.4% to 11%
    - TX, FL, WA, TN, NV: 0% (no state income tax)
    
    Args:
        gross_income: Annual gross income
        state: State abbreviation
        filing_status: "single" or "married"
        
    Returns:
        Annual state tax amount
    """
    state = state.upper()
    
    # States with no income tax
    if state in ['TX', 'FL', 'WA', 'TN', 'NV', 'SD', 'WY', 'AK']:
        return 0
    
    # Progressive tax states (2025 brackets)
    progressive_states = {
        'CA': {  # California
            'single': [
                {'limit': 10412, 'rate': 0.01},
                {'limit': 24684, 'rate': 0.02},
                {'limit': 38959, 'rate': 0.04},
                {'limit': 54081, 'rate': 0.06},
                {'limit': 68350, 'rate': 0.08},
                {'limit': 349137, 'rate': 0.093},
                {'limit': 418961, 'rate': 0.103},
                {'limit': 698271, 'rate': 0.113},
                {'limit': float('inf'), 'rate': 0.133}
            ],
            'married': [
                {'limit': 20824, 'rate': 0.01},
                {'limit': 49368, 'rate': 0.02},
                {'limit': 77918, 'rate': 0.04},
                {'limit': 108162, 'rate': 0.06},
                {'limit': 136700, 'rate': 0.08},
                {'limit': 698274, 'rate': 0.093},
                {'limit': 837922, 'rate': 0.103},
                {'limit': 1396542, 'rate': 0.113},
                {'limit': float('inf'), 'rate': 0.133}
            ]
        },
        'VA': {  # Virginia
            'single': [
                {'limit': 3000, 'rate': 0.02},
                {'limit': 5000, 'rate': 0.03},
                {'limit': 17000, 'rate': 0.05},
                {'limit': float('inf'), 'rate': 0.0575}
            ],
            'married': [
                {'limit': 3000, 'rate': 0.02},
                {'limit': 5000, 'rate': 0.03},
                {'limit': 17000, 'rate': 0.05},
                {'limit': float('inf'), 'rate': 0.0575}
            ]
        },
        'MD': {  # Maryland
            'single': [
                {'limit': 1000, 'rate': 0.02},
                {'limit': 2000, 'rate': 0.03},
                {'limit': 3000, 'rate': 0.04},
                {'limit': 100000, 'rate': 0.0475},
                {'limit': 125000, 'rate': 0.05},
                {'limit': 150000, 'rate': 0.0525},
                {'limit': 250000, 'rate': 0.055},
                {'limit': float('inf'), 'rate': 0.0575}
            ],
            'married': [
                {'limit': 1000, 'rate': 0.02},
                {'limit': 2000, 'rate': 0.03},
                {'limit': 3000, 'rate': 0.04},
                {'limit': 150000, 'rate': 0.0475},
                {'limit': 175000, 'rate': 0.05},
                {'limit': 225000, 'rate': 0.0525},
                {'limit': 300000, 'rate': 0.055},
                {'limit': float('inf'), 'rate': 0.0575}
            ]
        },
        'NY': {  # New York
            'single': [
                {'limit': 8500, 'rate': 0.04},
                {'limit': 11700, 'rate': 0.045},
                {'limit': 13900, 'rate': 0.0525},
                {'limit': 80650, 'rate': 0.055},
                {'limit': 215400, 'rate': 0.06},
                {'limit': 1077550, 'rate': 0.0685},
                {'limit': 5000000, 'rate': 0.0965},
                {'limit': 25000000, 'rate': 0.103},
                {'limit': float('inf'), 'rate': 0.109}
            ],
            'married': [
                {'limit': 17150, 'rate': 0.04},
                {'limit': 23600, 'rate': 0.045},
                {'limit': 27900, 'rate': 0.0525},
                {'limit': 161550, 'rate': 0.055},
                {'limit': 323200, 'rate': 0.06},
                {'limit': 2155350, 'rate': 0.0685},
                {'limit': 5000000, 'rate': 0.0965},
                {'limit': 25000000, 'rate': 0.103},
                {'limit': float('inf'), 'rate': 0.109}
            ]
        },
        'HI': {  # Hawaii
            'single': [
                {'limit': 2400, 'rate': 0.014},
                {'limit': 4800, 'rate': 0.032},
                {'limit': 9600, 'rate': 0.055},
                {'limit': 14400, 'rate': 0.064},
                {'limit': 19200, 'rate': 0.068},
                {'limit': 24000, 'rate': 0.072},
                {'limit': 36000, 'rate': 0.076},
                {'limit': 48000, 'rate': 0.079},
                {'limit': 150000, 'rate': 0.0825},
                {'limit': 175000, 'rate': 0.09},
                {'limit': 200000, 'rate': 0.10},
                {'limit': float('inf'), 'rate': 0.11}
            ],
            'married': [
                {'limit': 4800, 'rate': 0.014},
                {'limit': 9600, 'rate': 0.032},
                {'limit': 19200, 'rate': 0.055},
                {'limit': 28800, 'rate': 0.064},
                {'limit': 38400, 'rate': 0.068},
                {'limit': 48000, 'rate': 0.072},
                {'limit': 72000, 'rate': 0.076},
                {'limit': 96000, 'rate': 0.079},
                {'limit': 300000, 'rate': 0.0825},
                {'limit': 350000, 'rate': 0.09},
                {'limit': 400000, 'rate': 0.10},
                {'limit': float('inf'), 'rate': 0.11}
            ]
        }
    }
    
    # Flat tax states (2025 rates)
    flat_tax_states = {
        'NC': 0.0475,  # North Carolina
        'CO': 0.044,   # Colorado
        'IL': 0.0495,  # Illinois
        'IN': 0.0315,  # Indiana
        'MI': 0.0425,  # Michigan
        'PA': 0.0307,  # Pennsylvania
        'UT': 0.0485,  # Utah
        'AZ': 0.025,   # Arizona
        'KY': 0.04,    # Kentucky
        'MS': 0.05,    # Mississippi
        'GA': 0.0575,  # Georgia
        'MA': 0.05,    # Massachusetts
    }
    
    if state in flat_tax_states:
        return gross_income * flat_tax_states[state]
    
    # Progressive calculation
    if state in progressive_states:
        brackets = progressive_states[state].get(filing_status.lower(), progressive_states[state]['single'])
        
        tax = 0
        prev_limit = 0
        
        for bracket in brackets:
            limit = bracket['limit']
            rate = bracket['rate']
            
            if gross_income <= prev_limit:
                break
            
            taxable_in_bracket = min(gross_income, limit) - prev_limit
            tax += taxable_in_bracket * rate
            
            prev_limit = limit
            
            if limit >= gross_income:
                break
        
        return tax
    
    # Default: no state tax
    return 0


def calculate_fica_tax(gross_income: float) -> Dict[str, float]:
    """
    Calculates FICA taxes (Social Security + Medicare).
    
    Args:
        gross_income: Annual gross income
        
    Returns:
        Dictionary with ss_tax, medicare_tax, and total_fica
    """
    tax_data = load_tax_data()
    fica = tax_data['fica']
    
    ss_cap = fica['social_security']['wage_base_limit']
    ss_rate = fica['social_security']['rate']
    med_rate = fica['medicare']['rate']
    
    ss_tax = min(gross_income, ss_cap) * ss_rate
    
    medicare_tax = gross_income * med_rate
    
    if gross_income > fica['medicare']['additional_threshold_single']:
        additional_medicare = (gross_income - fica['medicare']['additional_threshold_single']) * fica['medicare']['additional_rate']
        medicare_tax += additional_medicare
    
    return {
        "ss_tax": ss_tax,
        "medicare_tax": medicare_tax,
        "total_fica": ss_tax + medicare_tax
    }


def calculate_bonus_withholding(bonus_amount: float, federal_rate: float = 0.22) -> Dict[str, float]:
    """
    Calculates tax withholding on bonuses (supplemental income).
    Uses flat 22% federal withholding rate for bonuses under $1M.
    
    Args:
        bonus_amount: Annual bonus amount
        federal_rate: Federal supplemental withholding rate (default 22%)
        
    Returns:
        Dictionary with gross_bonus, federal_withholding, fica, and net_bonus
    """
    fica_data = calculate_fica_tax(bonus_amount)
    federal_withholding = bonus_amount * federal_rate
    
    net_bonus = bonus_amount - federal_withholding - fica_data['total_fica']
    
    return {
        "gross_bonus": bonus_amount,
        "federal_withholding": federal_withholding,
        "fica": fica_data['total_fica'],
        "net_bonus": max(0, net_bonus)
    }


def calculate_equity_vesting(total_equity: float, vesting_years: int = 4, is_public: bool = True) -> Dict[int, float]:
    """
    Calculates equity vesting schedule (typically 4 years with 1-year cliff).
    
    Args:
        total_equity: Total equity grant value
        vesting_years: Number of years to vest (default 4)
        is_public: Whether stock is public (affects liquidity)
        
    Returns:
        Dictionary mapping year to vested amount
    """
    vesting_schedule = {}
    
    annual_vest = total_equity / vesting_years
    
    for year in range(1, vesting_years + 1):
        vesting_schedule[year] = annual_vest
    
    return vesting_schedule


def calculate_civilian_net(base_salary: float, bonus_pct: float, total_equity: float, state: str, filing_status: str = "single", annual_rsu_value: float = 0) -> Dict[str, float]:
    """
    Calculates estimated net pay for civilian employment including RSU vesting.
    
    Args:
        base_salary: Annual base salary
        bonus_pct: Bonus percentage (e.g., 15 for 15%)
        total_equity: Total equity grant value (for display)
        state: State abbreviation
        filing_status: "single" or "married"
        annual_rsu_value: Annual vesting value (risk-adjusted)
        
    Returns:
        Dictionary containing:
            - gross_annual: Total gross compensation (base + bonus + RSU)
            - base_salary: Base salary
            - bonus_annual: Gross bonus amount
            - bonus_net: Net bonus after withholding
            - rsu_annual: Annual RSU vesting value
            - rsu_net: Net RSU after tax withholding
            - fed_tax: Federal income tax
            - state_tax: State income tax
            - fica_tax: FICA taxes
            - total_tax: Sum of all taxes
            - net_annual: Net annual take-home (including RSU)
            - net_monthly: Net monthly take-home (including RSU)
            - effective_tax_rate: Overall tax rate
    """
    bonus_annual = base_salary * (bonus_pct / 100)
    
    gross_annual = base_salary + bonus_annual + annual_rsu_value
    
    fed_tax = calculate_federal_tax(gross_annual, filing_status)
    state_tax = calculate_state_tax(gross_annual, state, filing_status)
    fica_data = calculate_fica_tax(gross_annual)
    fica_tax = fica_data['total_fica']
    
    total_tax = fed_tax + state_tax + fica_tax
    net_annual = gross_annual - total_tax
    
    bonus_withholding = calculate_bonus_withholding(bonus_annual)
    
    if annual_rsu_value > 0:
        rsu_withholding = calculate_bonus_withholding(annual_rsu_value)
        rsu_net = rsu_withholding['net_bonus']
    else:
        rsu_net = 0
    
    return {
        "gross_annual": gross_annual,
        "base_salary": base_salary,
        "bonus_annual": bonus_annual,
        "bonus_net": bonus_withholding['net_bonus'],
        "rsu_annual": annual_rsu_value,
        "rsu_net": rsu_net,
        "fed_tax": fed_tax,
        "state_tax": state_tax,
        "fica_tax": fica_tax,
        "total_tax": total_tax,
        "net_annual": net_annual,
        "net_monthly": net_annual / 12,
        "effective_tax_rate": (total_tax / gross_annual) if gross_annual > 0 else 0
    }
