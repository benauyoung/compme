"""
Shared pytest fixtures for CompMe test suite.
"""
import sys
import os
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =============================================================================
# Military Fixtures
# =============================================================================

@pytest.fixture
def e5_6yrs():
    """Standard E-5 at 6 years for testing."""
    return {
        "rank": "E-5",
        "years_of_service": 6,
    }


@pytest.fixture
def e6_norfolk():
    """Standard E-6 at Norfolk for testing."""
    return {
        "rank": "E-6",
        "years_of_service": 6,
        "location": "NORFOLK/PORTSMOUTH, VA",
        "has_dependents": False,
        "filing_status": "single"
    }


@pytest.fixture
def o3_sandiego():
    """Standard O-3 at San Diego for testing."""
    return {
        "rank": "O-3",
        "years_of_service": 4,
        "location": "SAN DIEGO, CA",
        "has_dependents": True,
        "filing_status": "married"
    }


# =============================================================================
# Civilian Fixtures
# =============================================================================

@pytest.fixture
def civilian_offer_100k():
    """Standard $100k civilian offer."""
    return {
        "base_salary": 100000,
        "bonus_pct": 15,
        "total_equity": 50000,
        "state": "VA",
        "filing_status": "single",
        "annual_rsu_value": 12500,
        "num_children": 0
    }


@pytest.fixture
def civilian_offer_150k_equity():
    """$150k offer with significant equity."""
    return {
        "base_salary": 150000,
        "bonus_pct": 20,
        "total_equity": 200000,
        "state": "CA",
        "filing_status": "single",
        "annual_rsu_value": 50000,
        "num_children": 0
    }


@pytest.fixture
def civilian_offer_with_kids():
    """Civilian offer for family with children."""
    return {
        "base_salary": 120000,
        "bonus_pct": 15,
        "total_equity": 0,
        "state": "TX",
        "filing_status": "married",
        "annual_rsu_value": 0,
        "num_children": 2
    }


# =============================================================================
# State Lists
# =============================================================================

@pytest.fixture
def all_states():
    """List of all 50 states + DC."""
    return [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
        "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
        "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
        "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
        "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]


@pytest.fixture
def no_income_tax_states():
    """States with no income tax."""
    return ["TX", "FL", "WA", "TN", "NV", "SD", "WY", "AK", "NH"]


@pytest.fixture
def flat_tax_states():
    """States with flat income tax."""
    return ["AZ", "CO", "GA", "ID", "IL", "IN", "KY", "MA", "MI", "MS", "NC", "ND", "PA", "UT"]


@pytest.fixture
def progressive_tax_states():
    """States with progressive income tax."""
    return ["AL", "AR", "CA", "CT", "DE", "DC", "HI", "IA", "KS", "LA", "ME", "MD",
            "MN", "MO", "MT", "NE", "NJ", "NM", "NY", "OH", "OK", "OR", "RI", "SC",
            "VA", "VT", "WV", "WI"]


# =============================================================================
# Equity Fixtures
# =============================================================================

@pytest.fixture
def public_equity_grant():
    """Public company equity grant."""
    return {
        "total_grant": 100000,
        "vesting_years": 4,
        "is_public": True,
        "company_stage": None
    }


@pytest.fixture
def private_equity_grant():
    """Private company equity grant."""
    return {
        "total_grant": 100000,
        "vesting_years": 4,
        "is_public": False,
        "company_stage": None
    }


# =============================================================================
# Offer Letter Fixtures
# =============================================================================

@pytest.fixture
def sample_offer_letter_basic():
    """Basic offer letter text."""
    return """
    Dear Candidate,

    We are pleased to offer you the position of Software Engineer.

    Base Salary: $120,000 per year
    Annual Bonus: 15% target

    Sincerely,
    HR Team
    """


@pytest.fixture
def sample_offer_letter_full():
    """Full offer letter with all components."""
    return """
    Dear Candidate,

    We are excited to extend an offer for the role of Senior Engineer.

    Compensation Package:
    - Base Salary: $150,000 annually
    - Sign-on Bonus: $25,000
    - Annual Bonus Target: 20%
    - Equity Grant: 5,000 RSUs vesting over 4 years

    We are a publicly traded company (NASDAQ: ACME).

    Best regards,
    Talent Team
    """
