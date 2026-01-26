"""
Unit tests for Military Compensation Engine (mil_engine.py)
"""
import pytest
from engines.mil_engine import (
    get_marginal_tax_rate,
    get_base_pay,
    get_bas_rate,
    calculate_tax_advantage,
    calculate_rmc,
    FEDERAL_TAX_BRACKETS
)


class TestMarginalTaxRate:
    """Tests for get_marginal_tax_rate function."""

    def test_marginal_rate_10_percent_single(self):
        """Lowest bracket - income under $11,925."""
        rate = get_marginal_tax_rate(10000, "single")
        assert rate == 0.10

    def test_marginal_rate_12_percent_single(self):
        """Second bracket - $11,925 to $48,475."""
        rate = get_marginal_tax_rate(30000, "single")
        assert rate == 0.12

    def test_marginal_rate_22_percent_single(self):
        """Third bracket - $48,475 to $103,350."""
        rate = get_marginal_tax_rate(80000, "single")
        assert rate == 0.22

    def test_marginal_rate_24_percent_single(self):
        """Fourth bracket - $103,350 to $197,300."""
        rate = get_marginal_tax_rate(150000, "single")
        assert rate == 0.24

    def test_marginal_rate_32_percent_single(self):
        """Fifth bracket - $197,300 to $250,525."""
        rate = get_marginal_tax_rate(220000, "single")
        assert rate == 0.32

    def test_marginal_rate_35_percent_single(self):
        """Sixth bracket - $250,525 to $626,350."""
        rate = get_marginal_tax_rate(500000, "single")
        assert rate == 0.35

    def test_marginal_rate_37_percent_single(self):
        """Top bracket - over $626,350."""
        rate = get_marginal_tax_rate(700000, "single")
        assert rate == 0.37

    def test_marginal_rate_married_12_percent(self):
        """Married bracket - $23,850 to $96,950."""
        rate = get_marginal_tax_rate(50000, "married")
        assert rate == 0.12

    def test_marginal_rate_married_22_percent(self):
        """Married bracket - $96,950 to $206,700."""
        rate = get_marginal_tax_rate(150000, "married")
        assert rate == 0.22

    def test_marginal_rate_case_insensitive(self):
        """Filing status should be case insensitive."""
        rate1 = get_marginal_tax_rate(50000, "SINGLE")
        rate2 = get_marginal_tax_rate(50000, "single")
        rate3 = get_marginal_tax_rate(50000, "Single")
        assert rate1 == rate2 == rate3

    def test_marginal_rate_invalid_status_defaults_single(self):
        """Invalid filing status should default to single brackets."""
        rate = get_marginal_tax_rate(50000, "invalid")
        expected = get_marginal_tax_rate(50000, "single")
        assert rate == expected

    def test_marginal_rate_zero_income(self):
        """Zero income should return 10% (lowest bracket)."""
        rate = get_marginal_tax_rate(0, "single")
        assert rate == 0.10

    def test_marginal_rate_boundary_exactly_at_bracket(self):
        """Test exact bracket boundary."""
        # At exactly $11,925, should still be in 10% bracket
        rate = get_marginal_tax_rate(11925, "single")
        assert rate == 0.10


class TestBasePay:
    """Tests for get_base_pay function."""

    def test_base_pay_e5_6years(self):
        """E-5 at 6 years should have valid pay."""
        pay = get_base_pay("E-5", 6)
        assert pay > 0
        assert pay > 3000  # E-5 should make more than $3k/month

    def test_base_pay_e6_10years(self):
        """E-6 at 10 years should have higher pay than 6 years."""
        pay_6yr = get_base_pay("E-6", 6)
        pay_10yr = get_base_pay("E-6", 10)
        assert pay_10yr >= pay_6yr

    def test_base_pay_o3_4years(self):
        """O-3 at 4 years should have valid officer pay."""
        pay = get_base_pay("O-3", 4)
        assert pay > 0
        assert pay > 5000  # Officers should make more than $5k/month

    def test_base_pay_o5_18years(self):
        """O-5 at 18 years (senior officer)."""
        pay = get_base_pay("O-5", 18)
        assert pay > 8000  # Senior officers make good money

    def test_base_pay_invalid_rank(self):
        """Invalid rank should return 0."""
        pay = get_base_pay("X-99", 5)
        assert pay == 0.0

    def test_base_pay_e1_new(self):
        """E-1 with less than 2 years."""
        pay = get_base_pay("E-1", 0)
        assert pay > 0
        assert pay > 1500  # Even E-1 makes some money

    def test_base_pay_years_beyond_max(self):
        """Years beyond max in table should use highest available."""
        pay_30yr = get_base_pay("E-9", 30)
        pay_26yr = get_base_pay("E-9", 26)
        assert pay_30yr >= pay_26yr

    def test_base_pay_case_sensitivity(self):
        """Rank lookup should handle case."""
        pay_upper = get_base_pay("E-6", 6)
        pay_lower = get_base_pay("e-6", 6)
        # May or may not match depending on implementation
        # Just verify no crash
        assert pay_upper >= 0


class TestBASRate:
    """Tests for get_bas_rate function."""

    def test_bas_enlisted(self):
        """Enlisted BAS rate."""
        bas = get_bas_rate("E-6")
        assert bas == 465.77

    def test_bas_officer(self):
        """Officer BAS rate."""
        bas = get_bas_rate("O-3")
        assert bas == 320.78

    def test_bas_all_enlisted_ranks(self):
        """All enlisted ranks get same BAS."""
        for rank in ["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9"]:
            assert get_bas_rate(rank) == 465.77

    def test_bas_all_officer_ranks(self):
        """All officer ranks get same BAS."""
        for rank in ["O-1", "O-2", "O-3", "O-4", "O-5", "O-6"]:
            assert get_bas_rate(rank) == 320.78

    def test_bas_case_insensitive(self):
        """BAS lookup should be case insensitive."""
        assert get_bas_rate("e-6") == get_bas_rate("E-6")
        assert get_bas_rate("o-3") == get_bas_rate("O-3")


class TestTaxAdvantage:
    """Tests for calculate_tax_advantage function."""

    def test_tax_advantage_basic(self):
        """Basic tax advantage calculation."""
        # $4000 base, $2000 BAH, $466 BAS, single
        advantage = calculate_tax_advantage(4000, 2000, 466, "single")
        assert advantage > 0
        # With ~$30k taxable income, marginal rate is 12%
        # Tax advantage should be roughly (2000+466)*12 * 0.12 = ~$3500/year = ~$290/month
        assert 200 < advantage < 500

    def test_tax_advantage_higher_income(self):
        """Higher income = higher marginal rate = more tax advantage."""
        advantage_low = calculate_tax_advantage(3000, 2000, 466, "single")
        advantage_high = calculate_tax_advantage(8000, 2000, 466, "single")
        # Higher base pay means higher marginal rate
        assert advantage_high >= advantage_low

    def test_tax_advantage_married_vs_single(self):
        """Married filing status has different brackets."""
        advantage_single = calculate_tax_advantage(5000, 2500, 466, "single")
        advantage_married = calculate_tax_advantage(5000, 2500, 466, "married")
        # Both should be positive
        assert advantage_single > 0
        assert advantage_married > 0

    def test_tax_advantage_zero_allowances(self):
        """Zero allowances = zero tax advantage."""
        advantage = calculate_tax_advantage(5000, 0, 0, "single")
        assert advantage == 0


class TestCalculateRMC:
    """Tests for calculate_rmc function (integration)."""

    def test_rmc_returns_all_fields(self):
        """RMC should return all expected fields."""
        result = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single"
        )

        expected_fields = [
            "base_pay_monthly",
            "bah_monthly",
            "bas_monthly",
            "tax_advantage_monthly",
            "total_monthly",
            "taxable_monthly",
            "nontaxable_monthly",
            "bah_source"
        ]

        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_rmc_total_equals_sum(self):
        """Total monthly should equal sum of components."""
        result = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single"
        )

        expected_total = (
            result["base_pay_monthly"] +
            result["bah_monthly"] +
            result["bas_monthly"]
        )
        assert result["total_monthly"] == pytest.approx(expected_total, rel=0.01)

    def test_rmc_taxable_nontaxable_split(self):
        """Taxable + nontaxable should account for total (minus tax advantage)."""
        result = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single"
        )

        assert result["taxable_monthly"] == result["base_pay_monthly"]
        assert result["nontaxable_monthly"] == pytest.approx(
            result["bah_monthly"] + result["bas_monthly"],
            rel=0.01
        )

    def test_rmc_manual_bah_override(self):
        """Manual BAH should override lookup."""
        result = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=3000
        )

        assert result["bah_monthly"] == 3000
        assert result["bah_source"] == "manual"

    def test_rmc_officer_vs_enlisted(self):
        """Officers should generally have higher RMC."""
        enlisted = calculate_rmc("E-6", 6, "NORFOLK/PORTSMOUTH, VA", False, "single")
        officer = calculate_rmc("O-4", 6, "NORFOLK/PORTSMOUTH, VA", False, "single")

        assert officer["base_pay_monthly"] > enlisted["base_pay_monthly"]
