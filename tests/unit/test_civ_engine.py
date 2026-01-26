"""
Unit tests for Civilian Compensation Engine (civ_engine.py)
"""
import pytest
from engines.civ_engine import (
    calculate_federal_tax,
    calculate_state_tax,
    calculate_fica_tax,
    calculate_child_tax_credit,
    calculate_bonus_withholding,
    calculate_civilian_net
)


class TestFederalTax:
    """Tests for calculate_federal_tax function."""

    def test_federal_tax_zero_income(self):
        """Zero income = zero tax."""
        tax = calculate_federal_tax(0, "single")
        assert tax == 0

    def test_federal_tax_below_standard_deduction(self):
        """Income below standard deduction = zero tax."""
        tax = calculate_federal_tax(10000, "single")
        assert tax == 0

    def test_federal_tax_single_50k(self):
        """$50k single income tax calculation."""
        tax = calculate_federal_tax(50000, "single")
        # Taxable = 50000 - 15750 = 34250
        # 10% on first 11925 = 1192.50
        # 12% on remaining 22325 = 2679
        # Total ~ 3871.50
        assert 3500 < tax < 4500

    def test_federal_tax_single_100k(self):
        """$100k single income tax calculation."""
        tax = calculate_federal_tax(100000, "single")
        # Should be in 22% bracket
        assert 10000 < tax < 15000

    def test_federal_tax_single_200k(self):
        """$200k single income tax calculation."""
        tax = calculate_federal_tax(200000, "single")
        # Should be in 32% bracket
        assert 35000 < tax < 45000

    def test_federal_tax_married_100k(self):
        """$100k married filing jointly."""
        tax = calculate_federal_tax(100000, "married")
        # Married has larger brackets, so less tax
        single_tax = calculate_federal_tax(100000, "single")
        assert tax < single_tax

    def test_federal_tax_married_200k(self):
        """$200k married filing jointly."""
        tax = calculate_federal_tax(200000, "married")
        # Should be in 22% bracket for married
        assert 20000 < tax < 35000

    def test_federal_tax_progressive(self):
        """Tax should increase with income."""
        tax_50k = calculate_federal_tax(50000, "single")
        tax_100k = calculate_federal_tax(100000, "single")
        tax_200k = calculate_federal_tax(200000, "single")

        assert tax_50k < tax_100k < tax_200k


class TestStateTax:
    """Tests for calculate_state_tax function."""

    @pytest.mark.parametrize("state", ["TX", "FL", "WA", "TN", "NV", "SD", "WY", "AK", "NH"])
    def test_no_income_tax_states(self, state):
        """States with no income tax should return $0."""
        tax = calculate_state_tax(100000, state, "single")
        assert tax == 0

    @pytest.mark.parametrize("state,expected_rate", [
        ("AZ", 0.025),
        ("CO", 0.044),
        ("IL", 0.0495),
        ("IN", 0.0305),
        ("MI", 0.0425),
        ("NC", 0.0475),
        ("PA", 0.0307),
    ])
    def test_flat_tax_states(self, state, expected_rate):
        """Flat tax states should apply rate to full income."""
        income = 100000
        tax = calculate_state_tax(income, state, "single")
        expected = income * expected_rate
        assert tax == pytest.approx(expected, rel=0.01)

    def test_california_progressive(self):
        """California has progressive brackets up to 13.3%."""
        tax_50k = calculate_state_tax(50000, "CA", "single")
        tax_100k = calculate_state_tax(100000, "CA", "single")
        tax_500k = calculate_state_tax(500000, "CA", "single")

        assert tax_50k < tax_100k < tax_500k
        # CA at $100k should be around $4-6k
        assert 3000 < tax_100k < 7000

    def test_new_york_progressive(self):
        """New York has progressive brackets up to 10.9%."""
        tax = calculate_state_tax(100000, "NY", "single")
        # NY at $100k should be around $5-6k
        assert 4000 < tax < 7000

    def test_state_tax_case_insensitive(self):
        """State code should be case insensitive."""
        tax_upper = calculate_state_tax(100000, "CA", "single")
        tax_lower = calculate_state_tax(100000, "ca", "single")
        assert tax_upper == tax_lower

    def test_all_states_return_number(self, all_states):
        """All states should return a numeric tax value."""
        for state in all_states:
            tax = calculate_state_tax(100000, state, "single")
            assert isinstance(tax, (int, float))
            assert tax >= 0


class TestFICATax:
    """Tests for calculate_fica_tax function."""

    def test_fica_basic(self):
        """Basic FICA calculation."""
        result = calculate_fica_tax(100000)

        assert "ss_tax" in result
        assert "medicare_tax" in result
        assert "total_fica" in result

        # SS = 6.2% up to cap, Medicare = 1.45%
        assert result["ss_tax"] == pytest.approx(6200, rel=0.01)
        assert result["medicare_tax"] == pytest.approx(1450, rel=0.01)

    def test_fica_under_ss_cap(self):
        """Income under SS wage cap - full SS tax."""
        result = calculate_fica_tax(100000)
        # 6.2% of $100k = $6,200
        assert result["ss_tax"] == pytest.approx(6200, rel=0.01)

    def test_fica_over_ss_cap(self):
        """Income over SS wage cap ($168,600) - SS capped."""
        result = calculate_fica_tax(200000)
        # SS maxes at 6.2% of $168,600 = $10,453.20
        assert result["ss_tax"] == pytest.approx(10453, rel=0.02)
        # Medicare still applies to full income: 200000 * 1.45% = $2,900
        assert result["medicare_tax"] >= 2900

    def test_fica_additional_medicare(self):
        """Income over $200k triggers additional Medicare."""
        result = calculate_fica_tax(250000)
        # Additional 0.9% on income over $200k
        # Base Medicare: 250000 * 1.45% = 3625
        # Additional: 50000 * 0.9% = 450
        # Total Medicare ~ 4075
        assert result["medicare_tax"] > 4000

    def test_fica_total_equals_sum(self):
        """Total FICA should equal SS + Medicare."""
        result = calculate_fica_tax(100000)
        assert result["total_fica"] == pytest.approx(
            result["ss_tax"] + result["medicare_tax"],
            rel=0.01
        )


class TestChildTaxCredit:
    """Tests for calculate_child_tax_credit function."""

    def test_ctc_no_children(self):
        """No children = no credit."""
        credit = calculate_child_tax_credit(100000, 0, "single")
        assert credit == 0

    def test_ctc_one_child(self):
        """One child = $2,000 credit."""
        credit = calculate_child_tax_credit(100000, 1, "single")
        assert credit == 2000

    def test_ctc_two_children(self):
        """Two children = $4,000 credit."""
        credit = calculate_child_tax_credit(100000, 2, "single")
        assert credit == 4000

    def test_ctc_phaseout_single(self):
        """Credit phases out starting at $200k for single."""
        credit_under = calculate_child_tax_credit(199000, 2, "single")
        credit_over = calculate_child_tax_credit(250000, 2, "single")

        assert credit_under == 4000
        # $50k over threshold = $2,500 reduction
        assert credit_over == 4000 - 2500

    def test_ctc_phaseout_married(self):
        """Credit phases out starting at $400k for married."""
        credit_under = calculate_child_tax_credit(399000, 2, "married")
        credit_over = calculate_child_tax_credit(450000, 2, "married")

        assert credit_under == 4000
        # $50k over threshold = $2,500 reduction
        assert credit_over == 4000 - 2500

    def test_ctc_fully_phased_out(self):
        """Very high income = credit fully phased out."""
        credit = calculate_child_tax_credit(500000, 1, "single")
        # $300k over threshold = $15,000 reduction, but max credit is $2,000
        assert credit == 0


class TestBonusWithholding:
    """Tests for calculate_bonus_withholding function."""

    def test_bonus_withholding_basic(self):
        """Basic bonus withholding calculation."""
        result = calculate_bonus_withholding(10000, base_salary=80000)

        assert "gross_bonus" in result
        assert "federal_withholding" in result
        assert "fica" in result
        assert "net_bonus" in result

        assert result["gross_bonus"] == 10000
        # 22% federal flat rate
        assert result["federal_withholding"] == pytest.approx(2200, rel=0.01)

    def test_bonus_withholding_ss_under_cap(self):
        """Bonus when base salary under SS cap - full SS withholding."""
        result = calculate_bonus_withholding(20000, base_salary=100000)
        # SS applies to full bonus
        # 6.2% of $20k = $1,240
        # Medicare 1.45% of $20k = $290
        assert result["fica"] == pytest.approx(1530, rel=0.05)

    def test_bonus_withholding_ss_over_cap(self):
        """Bonus when base salary over SS cap - no SS on bonus."""
        result = calculate_bonus_withholding(20000, base_salary=180000)
        # SS cap ($176,100) already exceeded by base
        # Only Medicare applies: 1.45% of $20k = $290
        assert result["fica"] == pytest.approx(290, rel=0.05)

    def test_bonus_withholding_partial_ss(self):
        """Bonus when base salary partially under SS cap ($168,600)."""
        result = calculate_bonus_withholding(20000, base_salary=160000)
        # Only $8,600 of bonus is under cap (168600 - 160000)
        # SS: 6.2% of $8,600 = $533.20
        # Medicare: 1.45% of $20,000 = $290
        # Total FICA ~ $823
        assert result["fica"] == pytest.approx(823, rel=0.10)

    def test_bonus_net_positive(self):
        """Net bonus should always be positive."""
        result = calculate_bonus_withholding(10000, base_salary=100000)
        assert result["net_bonus"] > 0
        assert result["net_bonus"] < result["gross_bonus"]


class TestCivilianNet:
    """Tests for calculate_civilian_net function (integration)."""

    def test_civilian_net_returns_all_fields(self):
        """Should return all expected fields."""
        result = calculate_civilian_net(
            base_salary=100000,
            bonus_pct=15,
            total_equity=50000,
            state="VA",
            filing_status="single",
            annual_rsu_value=12500,
            num_children=0
        )

        expected_fields = [
            "gross_annual", "base_salary", "bonus_annual", "bonus_net",
            "rsu_annual", "rsu_net", "fed_tax", "state_tax", "fica_tax",
            "child_tax_credit", "total_tax", "net_annual", "net_monthly",
            "effective_tax_rate"
        ]

        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_civilian_net_gross_calculation(self):
        """Gross should equal base + bonus + RSU."""
        result = calculate_civilian_net(
            base_salary=100000,
            bonus_pct=15,
            total_equity=50000,
            state="VA",
            filing_status="single",
            annual_rsu_value=12500,
            num_children=0
        )

        expected_gross = 100000 + 15000 + 12500
        assert result["gross_annual"] == pytest.approx(expected_gross, rel=0.01)

    def test_civilian_net_with_children(self):
        """Child tax credit should reduce total tax."""
        result_no_kids = calculate_civilian_net(
            base_salary=100000, bonus_pct=0, total_equity=0,
            state="TX", filing_status="single", num_children=0
        )

        result_2_kids = calculate_civilian_net(
            base_salary=100000, bonus_pct=0, total_equity=0,
            state="TX", filing_status="single", num_children=2
        )

        # 2 kids = $4,000 less tax
        assert result_2_kids["total_tax"] < result_no_kids["total_tax"]
        assert result_2_kids["child_tax_credit"] == pytest.approx(4000, rel=0.01)

    def test_civilian_net_no_state_tax(self):
        """Texas should have no state tax."""
        result = calculate_civilian_net(
            base_salary=100000, bonus_pct=15, total_equity=0,
            state="TX", filing_status="single"
        )
        assert result["state_tax"] == 0

    def test_civilian_net_effective_rate_reasonable(self):
        """Effective tax rate should be reasonable (10-40%)."""
        result = calculate_civilian_net(
            base_salary=100000, bonus_pct=15, total_equity=0,
            state="CA", filing_status="single"
        )

        assert 0.10 < result["effective_tax_rate"] < 0.45

    def test_civilian_net_monthly_equals_annual_div_12(self):
        """Monthly should be annual / 12."""
        result = calculate_civilian_net(
            base_salary=100000, bonus_pct=15, total_equity=0,
            state="VA", filing_status="single"
        )

        assert result["net_monthly"] == pytest.approx(
            result["net_annual"] / 12,
            rel=0.01
        )
