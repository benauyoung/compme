"""
Data validation tests for tax brackets and rates.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from engines.mil_engine import FEDERAL_TAX_BRACKETS
from engines.civ_engine import calculate_state_tax


class TestFederalTaxBrackets:
    """Validate federal tax bracket data."""

    def test_single_brackets_count(self):
        """Single filers should have 7 brackets."""
        assert len(FEDERAL_TAX_BRACKETS['single']) == 7

    def test_married_brackets_count(self):
        """Married filers should have 7 brackets."""
        assert len(FEDERAL_TAX_BRACKETS['married']) == 7

    def test_brackets_ascending_limits(self):
        """Bracket limits should be in ascending order."""
        for status in ['single', 'married']:
            brackets = FEDERAL_TAX_BRACKETS[status]
            prev_max = 0
            for bracket in brackets:
                assert bracket['max'] > prev_max
                prev_max = bracket['max']

    def test_brackets_ascending_rates(self):
        """Bracket rates should be in ascending order."""
        for status in ['single', 'married']:
            brackets = FEDERAL_TAX_BRACKETS[status]
            prev_rate = 0
            for bracket in brackets:
                assert bracket['rate'] >= prev_rate
                prev_rate = bracket['rate']

    def test_rate_bounds(self):
        """All rates should be between 0 and 0.40."""
        for status in ['single', 'married']:
            for bracket in FEDERAL_TAX_BRACKETS[status]:
                assert 0 <= bracket['rate'] <= 0.40

    def test_2025_single_brackets_values(self):
        """Verify 2025 single bracket values."""
        single = FEDERAL_TAX_BRACKETS['single']

        # 10% bracket
        assert single[0]['rate'] == 0.10
        assert single[0]['max'] == 11925

        # 12% bracket
        assert single[1]['rate'] == 0.12
        assert single[1]['max'] == 48475

        # 22% bracket
        assert single[2]['rate'] == 0.22
        assert single[2]['max'] == 103350

        # 37% top bracket
        assert single[6]['rate'] == 0.37

    def test_married_brackets_higher_than_single(self):
        """Married brackets should be roughly 2x single."""
        single = FEDERAL_TAX_BRACKETS['single']
        married = FEDERAL_TAX_BRACKETS['married']

        # Compare first few brackets
        for i in range(3):
            ratio = married[i]['max'] / single[i]['max']
            assert 1.8 < ratio < 2.2, f"Bracket {i} ratio: {ratio}"


class TestStateTaxCoverage:
    """Validate state tax data coverage."""

    @pytest.fixture
    def all_states(self):
        """All 50 states + DC."""
        return [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
            "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
            "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
            "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
            "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]

    def test_all_states_have_tax_calculation(self, all_states):
        """Every state should return a tax value without error."""
        for state in all_states:
            try:
                tax = calculate_state_tax(100000, state, "single")
                assert isinstance(tax, (int, float))
                assert tax >= 0
            except Exception as e:
                pytest.fail(f"State {state} failed: {e}")

    def test_no_income_tax_states_return_zero(self):
        """States with no income tax should return $0."""
        no_tax_states = ["TX", "FL", "WA", "TN", "NV", "SD", "WY", "AK", "NH"]

        for state in no_tax_states:
            tax = calculate_state_tax(100000, state, "single")
            assert tax == 0, f"{state} should have no income tax"

    def test_high_tax_states_return_substantial(self):
        """High-tax states should return significant amounts."""
        high_tax_states = ["CA", "NY", "NJ", "OR", "HI"]

        for state in high_tax_states:
            tax = calculate_state_tax(100000, state, "single")
            assert tax > 3000, f"{state} should have substantial tax"

    def test_state_tax_scales_with_income(self, all_states):
        """Tax should generally increase with income for all states."""
        for state in all_states:
            tax_50k = calculate_state_tax(50000, state, "single")
            tax_200k = calculate_state_tax(200000, state, "single")

            assert tax_200k >= tax_50k, f"{state} tax should increase with income"

    def test_married_vs_single_varies_by_state(self):
        """Some states have different married brackets."""
        states_to_check = ["CA", "NY", "VA", "MD"]

        for state in states_to_check:
            single = calculate_state_tax(100000, state, "single")
            married = calculate_state_tax(100000, state, "married")

            # Both should be valid numbers
            assert single >= 0
            assert married >= 0


class TestStateTaxRates:
    """Validate specific state tax rates."""

    def test_california_top_rate(self):
        """California has 13.3% top rate."""
        # At $1M income, should be paying close to top rate
        tax = calculate_state_tax(1000000, "CA", "single")
        effective_rate = tax / 1000000
        assert effective_rate > 0.10  # Should be over 10% effective

    def test_new_york_top_rate(self):
        """New York has progressive tax rates."""
        tax = calculate_state_tax(1000000, "NY", "single")
        effective_rate = tax / 1000000
        assert effective_rate > 0.05  # Should have substantial tax

    def test_north_carolina_flat_rate(self):
        """North Carolina has flat 4.75%."""
        tax = calculate_state_tax(100000, "NC", "single")
        assert tax == pytest.approx(4750, rel=0.01)

    def test_colorado_flat_rate(self):
        """Colorado has flat 4.4%."""
        tax = calculate_state_tax(100000, "CO", "single")
        assert tax == pytest.approx(4400, rel=0.01)

    def test_pennsylvania_flat_rate(self):
        """Pennsylvania has flat 3.07%."""
        tax = calculate_state_tax(100000, "PA", "single")
        assert tax == pytest.approx(3070, rel=0.01)


class TestFICALimits:
    """Validate FICA tax limits."""

    def test_ss_wage_base(self):
        """SS wage base should cap SS tax."""
        from engines.civ_engine import calculate_fica_tax

        # At exactly wage base ($168,600)
        result = calculate_fica_tax(168600)
        ss_at_cap = result['ss_tax']

        # Above wage base
        result = calculate_fica_tax(200000)
        ss_above_cap = result['ss_tax']

        # SS tax should be same at and above cap
        assert ss_at_cap == pytest.approx(ss_above_cap, rel=0.01)

    def test_medicare_additional_threshold(self):
        """Additional Medicare kicks in at $200k."""
        from engines.civ_engine import calculate_fica_tax

        result_under = calculate_fica_tax(199000)
        result_over = calculate_fica_tax(250000)

        # Medicare should be higher for income over $200k
        medicare_rate_under = result_under['medicare_tax'] / 199000
        medicare_rate_over = result_over['medicare_tax'] / 250000

        # Over threshold should have higher effective rate
        assert medicare_rate_over > medicare_rate_under
