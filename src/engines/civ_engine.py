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

    Supports all 50 states + DC with accurate 2025 tax brackets.

    Args:
        gross_income: Annual gross income
        state: State abbreviation
        filing_status: "single" or "married"

    Returns:
        Annual state tax amount
    """
    state = state.upper()

    # States with no income tax (9 states)
    if state in ['TX', 'FL', 'WA', 'TN', 'NV', 'SD', 'WY', 'AK', 'NH']:
        return 0

    # Flat tax states (2025 rates) - 13 states
    flat_tax_states = {
        'AZ': 0.025,   # Arizona
        'CO': 0.044,   # Colorado
        'GA': 0.0549,  # Georgia (transitioned to flat in 2024)
        'ID': 0.058,   # Idaho
        'IL': 0.0495,  # Illinois
        'IN': 0.0305,  # Indiana (reduced in 2025)
        'KY': 0.04,    # Kentucky
        'MA': 0.05,    # Massachusetts
        'MI': 0.0425,  # Michigan
        'MS': 0.05,    # Mississippi
        'NC': 0.0475,  # North Carolina
        'ND': 0.0195,  # North Dakota (effectively flat for most)
        'PA': 0.0307,  # Pennsylvania
        'UT': 0.0465,  # Utah
    }

    if state in flat_tax_states:
        return gross_income * flat_tax_states[state]

    # Progressive tax states (2025 brackets)
    progressive_states = {
        'AL': {  # Alabama
            'single': [
                {'limit': 500, 'rate': 0.02},
                {'limit': 3000, 'rate': 0.04},
                {'limit': float('inf'), 'rate': 0.05}
            ],
            'married': [
                {'limit': 1000, 'rate': 0.02},
                {'limit': 6000, 'rate': 0.04},
                {'limit': float('inf'), 'rate': 0.05}
            ]
        },
        'AR': {  # Arkansas
            'single': [
                {'limit': 4400, 'rate': 0.02},
                {'limit': 8800, 'rate': 0.04},
                {'limit': float('inf'), 'rate': 0.039}
            ],
            'married': [
                {'limit': 4400, 'rate': 0.02},
                {'limit': 8800, 'rate': 0.04},
                {'limit': float('inf'), 'rate': 0.039}
            ]
        },
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
        'CT': {  # Connecticut
            'single': [
                {'limit': 10000, 'rate': 0.03},
                {'limit': 50000, 'rate': 0.05},
                {'limit': 100000, 'rate': 0.055},
                {'limit': 200000, 'rate': 0.06},
                {'limit': 250000, 'rate': 0.065},
                {'limit': 500000, 'rate': 0.069},
                {'limit': float('inf'), 'rate': 0.0699}
            ],
            'married': [
                {'limit': 20000, 'rate': 0.03},
                {'limit': 100000, 'rate': 0.05},
                {'limit': 200000, 'rate': 0.055},
                {'limit': 400000, 'rate': 0.06},
                {'limit': 500000, 'rate': 0.065},
                {'limit': 1000000, 'rate': 0.069},
                {'limit': float('inf'), 'rate': 0.0699}
            ]
        },
        'DE': {  # Delaware
            'single': [
                {'limit': 2000, 'rate': 0.0},
                {'limit': 5000, 'rate': 0.022},
                {'limit': 10000, 'rate': 0.039},
                {'limit': 20000, 'rate': 0.048},
                {'limit': 25000, 'rate': 0.052},
                {'limit': 60000, 'rate': 0.0555},
                {'limit': float('inf'), 'rate': 0.066}
            ],
            'married': [
                {'limit': 2000, 'rate': 0.0},
                {'limit': 5000, 'rate': 0.022},
                {'limit': 10000, 'rate': 0.039},
                {'limit': 20000, 'rate': 0.048},
                {'limit': 25000, 'rate': 0.052},
                {'limit': 60000, 'rate': 0.0555},
                {'limit': float('inf'), 'rate': 0.066}
            ]
        },
        'DC': {  # District of Columbia
            'single': [
                {'limit': 10000, 'rate': 0.04},
                {'limit': 40000, 'rate': 0.06},
                {'limit': 60000, 'rate': 0.065},
                {'limit': 250000, 'rate': 0.085},
                {'limit': 500000, 'rate': 0.0925},
                {'limit': 1000000, 'rate': 0.0975},
                {'limit': float('inf'), 'rate': 0.1075}
            ],
            'married': [
                {'limit': 10000, 'rate': 0.04},
                {'limit': 40000, 'rate': 0.06},
                {'limit': 60000, 'rate': 0.065},
                {'limit': 250000, 'rate': 0.085},
                {'limit': 500000, 'rate': 0.0925},
                {'limit': 1000000, 'rate': 0.0975},
                {'limit': float('inf'), 'rate': 0.1075}
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
        },
        'IA': {  # Iowa
            'single': [
                {'limit': 6210, 'rate': 0.044},
                {'limit': 31050, 'rate': 0.0482},
                {'limit': float('inf'), 'rate': 0.057}
            ],
            'married': [
                {'limit': 12420, 'rate': 0.044},
                {'limit': 62100, 'rate': 0.0482},
                {'limit': float('inf'), 'rate': 0.057}
            ]
        },
        'KS': {  # Kansas
            'single': [
                {'limit': 15000, 'rate': 0.031},
                {'limit': 30000, 'rate': 0.0525},
                {'limit': float('inf'), 'rate': 0.057}
            ],
            'married': [
                {'limit': 30000, 'rate': 0.031},
                {'limit': 60000, 'rate': 0.0525},
                {'limit': float('inf'), 'rate': 0.057}
            ]
        },
        'LA': {  # Louisiana
            'single': [
                {'limit': 12500, 'rate': 0.0185},
                {'limit': 50000, 'rate': 0.035},
                {'limit': float('inf'), 'rate': 0.0425}
            ],
            'married': [
                {'limit': 25000, 'rate': 0.0185},
                {'limit': 100000, 'rate': 0.035},
                {'limit': float('inf'), 'rate': 0.0425}
            ]
        },
        'ME': {  # Maine
            'single': [
                {'limit': 24500, 'rate': 0.058},
                {'limit': 58050, 'rate': 0.0675},
                {'limit': float('inf'), 'rate': 0.0715}
            ],
            'married': [
                {'limit': 49050, 'rate': 0.058},
                {'limit': 116100, 'rate': 0.0675},
                {'limit': float('inf'), 'rate': 0.0715}
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
        'MN': {  # Minnesota
            'single': [
                {'limit': 31690, 'rate': 0.0535},
                {'limit': 104090, 'rate': 0.068},
                {'limit': 193240, 'rate': 0.0785},
                {'limit': float('inf'), 'rate': 0.0985}
            ],
            'married': [
                {'limit': 46330, 'rate': 0.0535},
                {'limit': 184040, 'rate': 0.068},
                {'limit': 321450, 'rate': 0.0785},
                {'limit': float('inf'), 'rate': 0.0985}
            ]
        },
        'MO': {  # Missouri
            'single': [
                {'limit': 1207, 'rate': 0.02},
                {'limit': 2414, 'rate': 0.025},
                {'limit': 3621, 'rate': 0.03},
                {'limit': 4828, 'rate': 0.035},
                {'limit': 6035, 'rate': 0.04},
                {'limit': 7242, 'rate': 0.045},
                {'limit': 8449, 'rate': 0.05},
                {'limit': float('inf'), 'rate': 0.0495}
            ],
            'married': [
                {'limit': 1207, 'rate': 0.02},
                {'limit': 2414, 'rate': 0.025},
                {'limit': 3621, 'rate': 0.03},
                {'limit': 4828, 'rate': 0.035},
                {'limit': 6035, 'rate': 0.04},
                {'limit': 7242, 'rate': 0.045},
                {'limit': 8449, 'rate': 0.05},
                {'limit': float('inf'), 'rate': 0.0495}
            ]
        },
        'MT': {  # Montana
            'single': [
                {'limit': 20500, 'rate': 0.047},
                {'limit': float('inf'), 'rate': 0.059}
            ],
            'married': [
                {'limit': 41000, 'rate': 0.047},
                {'limit': float('inf'), 'rate': 0.059}
            ]
        },
        'NE': {  # Nebraska
            'single': [
                {'limit': 3700, 'rate': 0.0246},
                {'limit': 22170, 'rate': 0.0351},
                {'limit': 35730, 'rate': 0.0501},
                {'limit': float('inf'), 'rate': 0.0584}
            ],
            'married': [
                {'limit': 7390, 'rate': 0.0246},
                {'limit': 44350, 'rate': 0.0351},
                {'limit': 71460, 'rate': 0.0501},
                {'limit': float('inf'), 'rate': 0.0584}
            ]
        },
        'NJ': {  # New Jersey
            'single': [
                {'limit': 20000, 'rate': 0.014},
                {'limit': 35000, 'rate': 0.0175},
                {'limit': 40000, 'rate': 0.035},
                {'limit': 75000, 'rate': 0.05525},
                {'limit': 500000, 'rate': 0.0637},
                {'limit': 1000000, 'rate': 0.0897},
                {'limit': float('inf'), 'rate': 0.1075}
            ],
            'married': [
                {'limit': 20000, 'rate': 0.014},
                {'limit': 50000, 'rate': 0.0175},
                {'limit': 70000, 'rate': 0.0245},
                {'limit': 80000, 'rate': 0.035},
                {'limit': 150000, 'rate': 0.05525},
                {'limit': 500000, 'rate': 0.0637},
                {'limit': 1000000, 'rate': 0.0897},
                {'limit': float('inf'), 'rate': 0.1075}
            ]
        },
        'NM': {  # New Mexico
            'single': [
                {'limit': 5500, 'rate': 0.017},
                {'limit': 11000, 'rate': 0.032},
                {'limit': 16000, 'rate': 0.047},
                {'limit': 210000, 'rate': 0.049},
                {'limit': float('inf'), 'rate': 0.059}
            ],
            'married': [
                {'limit': 8000, 'rate': 0.017},
                {'limit': 16000, 'rate': 0.032},
                {'limit': 24000, 'rate': 0.047},
                {'limit': 315000, 'rate': 0.049},
                {'limit': float('inf'), 'rate': 0.059}
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
        'OH': {  # Ohio
            'single': [
                {'limit': 26050, 'rate': 0.0},
                {'limit': 100000, 'rate': 0.02765},
                {'limit': float('inf'), 'rate': 0.035}
            ],
            'married': [
                {'limit': 26050, 'rate': 0.0},
                {'limit': 100000, 'rate': 0.02765},
                {'limit': float('inf'), 'rate': 0.035}
            ]
        },
        'OK': {  # Oklahoma
            'single': [
                {'limit': 1000, 'rate': 0.0025},
                {'limit': 2500, 'rate': 0.0075},
                {'limit': 3750, 'rate': 0.0175},
                {'limit': 4900, 'rate': 0.0275},
                {'limit': 7200, 'rate': 0.0375},
                {'limit': float('inf'), 'rate': 0.0475}
            ],
            'married': [
                {'limit': 2000, 'rate': 0.0025},
                {'limit': 5000, 'rate': 0.0075},
                {'limit': 7500, 'rate': 0.0175},
                {'limit': 9800, 'rate': 0.0275},
                {'limit': 12200, 'rate': 0.0375},
                {'limit': float('inf'), 'rate': 0.0475}
            ]
        },
        'OR': {  # Oregon
            'single': [
                {'limit': 4050, 'rate': 0.0475},
                {'limit': 10200, 'rate': 0.0675},
                {'limit': 125000, 'rate': 0.0875},
                {'limit': float('inf'), 'rate': 0.099}
            ],
            'married': [
                {'limit': 8100, 'rate': 0.0475},
                {'limit': 20400, 'rate': 0.0675},
                {'limit': 250000, 'rate': 0.0875},
                {'limit': float('inf'), 'rate': 0.099}
            ]
        },
        'RI': {  # Rhode Island
            'single': [
                {'limit': 73450, 'rate': 0.0375},
                {'limit': 166950, 'rate': 0.0475},
                {'limit': float('inf'), 'rate': 0.0599}
            ],
            'married': [
                {'limit': 73450, 'rate': 0.0375},
                {'limit': 166950, 'rate': 0.0475},
                {'limit': float('inf'), 'rate': 0.0599}
            ]
        },
        'SC': {  # South Carolina
            'single': [
                {'limit': 3200, 'rate': 0.0},
                {'limit': 16040, 'rate': 0.03},
                {'limit': float('inf'), 'rate': 0.064}
            ],
            'married': [
                {'limit': 3200, 'rate': 0.0},
                {'limit': 16040, 'rate': 0.03},
                {'limit': float('inf'), 'rate': 0.064}
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
        'VT': {  # Vermont
            'single': [
                {'limit': 45400, 'rate': 0.0335},
                {'limit': 110050, 'rate': 0.066},
                {'limit': 229550, 'rate': 0.076},
                {'limit': float('inf'), 'rate': 0.0875}
            ],
            'married': [
                {'limit': 75850, 'rate': 0.0335},
                {'limit': 183400, 'rate': 0.066},
                {'limit': 279450, 'rate': 0.076},
                {'limit': float('inf'), 'rate': 0.0875}
            ]
        },
        'WV': {  # West Virginia
            'single': [
                {'limit': 10000, 'rate': 0.0236},
                {'limit': 25000, 'rate': 0.0315},
                {'limit': 40000, 'rate': 0.0354},
                {'limit': 60000, 'rate': 0.0472},
                {'limit': float('inf'), 'rate': 0.0512}
            ],
            'married': [
                {'limit': 10000, 'rate': 0.0236},
                {'limit': 25000, 'rate': 0.0315},
                {'limit': 40000, 'rate': 0.0354},
                {'limit': 60000, 'rate': 0.0472},
                {'limit': float('inf'), 'rate': 0.0512}
            ]
        },
        'WI': {  # Wisconsin
            'single': [
                {'limit': 14320, 'rate': 0.0354},
                {'limit': 28640, 'rate': 0.0465},
                {'limit': 315310, 'rate': 0.053},
                {'limit': float('inf'), 'rate': 0.0765}
            ],
            'married': [
                {'limit': 19090, 'rate': 0.0354},
                {'limit': 38190, 'rate': 0.0465},
                {'limit': 420420, 'rate': 0.053},
                {'limit': float('inf'), 'rate': 0.0765}
            ]
        }
    }

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

    # Default: no state tax (should not reach here with comprehensive data)
    return 0


def calculate_child_tax_credit(gross_income: float, num_children: int, filing_status: str = "single") -> float:
    """
    Calculates the Child Tax Credit (CTC) with income phase-out.

    2025 CTC rules:
    - $2,000 per qualifying child under 17
    - Phase-out begins at $200,000 (single) / $400,000 (married)
    - Reduces by $50 for each $1,000 over threshold

    Args:
        gross_income: Annual gross income (AGI)
        num_children: Number of qualifying children under 17
        filing_status: "single" or "married"

    Returns:
        Total child tax credit amount
    """
    if num_children <= 0:
        return 0

    credit_per_child = 2000
    base_credit = credit_per_child * num_children

    # Phase-out thresholds
    threshold = 400000 if filing_status.lower() == "married" else 200000

    if gross_income <= threshold:
        return base_credit

    # Reduce credit by $50 for each $1,000 over threshold
    excess_income = gross_income - threshold
    reduction = (excess_income // 1000) * 50

    return max(0, base_credit - reduction)


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


def calculate_bonus_withholding(bonus_amount: float, base_salary: float = 0, federal_rate: float = 0.22) -> Dict[str, float]:
    """
    Calculates tax withholding on bonuses (supplemental income).
    Uses flat 22% federal withholding rate for bonuses under $1M.

    Note: This is for DISPLAY PURPOSES ONLY. The actual FICA tax is calculated
    once on total compensation in calculate_civilian_net(). This function
    shows what withholding the employee would see on their bonus check.

    Args:
        bonus_amount: Annual bonus amount
        base_salary: Base salary (used to determine SS wage cap status)
        federal_rate: Federal supplemental withholding rate (default 22%)

    Returns:
        Dictionary with gross_bonus, federal_withholding, fica_withholding, and net_bonus
    """
    tax_data = load_tax_data()
    fica = tax_data['fica']
    ss_cap = fica['social_security']['wage_base_limit']
    ss_rate = fica['social_security']['rate']
    med_rate = fica['medicare']['rate']

    federal_withholding = bonus_amount * federal_rate

    # SS withholding on bonus only applies if base salary hasn't hit the cap
    if base_salary >= ss_cap:
        ss_withholding = 0
    else:
        # Only the portion of bonus that fits under the cap is subject to SS
        remaining_cap = ss_cap - base_salary
        ss_taxable = min(bonus_amount, remaining_cap)
        ss_withholding = ss_taxable * ss_rate

    medicare_withholding = bonus_amount * med_rate
    fica_withholding = ss_withholding + medicare_withholding

    net_bonus = bonus_amount - federal_withholding - fica_withholding

    return {
        "gross_bonus": bonus_amount,
        "federal_withholding": federal_withholding,
        "fica": fica_withholding,
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


def calculate_civilian_net(base_salary: float, bonus_pct: float, total_equity: float, state: str, filing_status: str = "single", annual_rsu_value: float = 0, num_children: int = 0) -> Dict[str, float]:
    """
    Calculates estimated net pay for civilian employment including RSU vesting.

    Args:
        base_salary: Annual base salary
        bonus_pct: Bonus percentage (e.g., 15 for 15%)
        total_equity: Total equity grant value (for display)
        state: State abbreviation
        filing_status: "single" or "married"
        annual_rsu_value: Annual vesting value (risk-adjusted)
        num_children: Number of qualifying children for Child Tax Credit

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
            - child_tax_credit: Child Tax Credit applied
            - total_tax: Sum of all taxes minus credits
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

    # Calculate child tax credit (reduces federal tax owed)
    child_credit = calculate_child_tax_credit(gross_annual, num_children, filing_status)
    # CTC can only reduce federal tax to $0, not create refund (simplified)
    applied_child_credit = min(child_credit, fed_tax)

    total_tax = fed_tax + state_tax + fica_tax - applied_child_credit
    net_annual = gross_annual - total_tax
    
    # Calculate withholding for display purposes (actual FICA already in fica_tax above)
    bonus_withholding = calculate_bonus_withholding(bonus_annual, base_salary)

    if annual_rsu_value > 0:
        # RSU vests after bonus, so both base + bonus count toward SS cap
        rsu_withholding = calculate_bonus_withholding(annual_rsu_value, base_salary + bonus_annual)
        rsu_net = rsu_withholding['net_bonus']
    else:
        rsu_net = 0
    
    return {
        "gross_annual": gross_annual,
        "base_salary": base_salary,
        "bonus_annual": bonus_annual,
        "bonus_federal_withholding": bonus_withholding['federal_withholding'],
        "bonus_fica_withholding": bonus_withholding['fica'],
        "bonus_net": bonus_withholding['net_bonus'],
        "rsu_annual": annual_rsu_value,
        "rsu_net": rsu_net,
        "fed_tax": fed_tax,
        "state_tax": state_tax,
        "fica_tax": fica_tax,
        "child_tax_credit": applied_child_credit,
        "total_tax": total_tax,
        "net_annual": net_annual,
        "net_monthly": net_annual / 12,
        "effective_tax_rate": (total_tax / gross_annual) if gross_annual > 0 else 0,
        "fed_effective_rate": (fed_tax / gross_annual) if gross_annual > 0 else 0,
        "state_effective_rate": (state_tax / gross_annual) if gross_annual > 0 else 0,
        "fica_effective_rate": (fica_tax / gross_annual) if gross_annual > 0 else 0
    }
