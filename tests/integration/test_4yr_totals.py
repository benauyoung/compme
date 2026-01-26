"""
Integration tests for 4-year total calculations.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from engines.mil_engine import calculate_rmc
from engines.civ_engine import calculate_civilian_net
from engines.equity_engine import calculate_rsu_value, CompanyStage


def calculate_4yr_totals(mil_results: dict, civ_results: dict, equity_calc: dict) -> dict:
    """
    Replicate the 4-year calculation logic from app.py for testing.
    """
    tsp_match_annual = mil_results['base_pay_monthly'] * 0.05 * 12
    mil_4yr_total = mil_results['total_monthly'] * 48 + (tsp_match_annual * 4)

    equity_value = equity_calc.get('adjusted_value', 0) if equity_calc else 0
    civ_4yr_total = civ_results['net_monthly'] * 48 + equity_value

    return {
        'mil_4yr_total': mil_4yr_total,
        'civ_4yr_total': civ_4yr_total,
        'four_year_delta': civ_4yr_total - mil_4yr_total,
        'tsp_match_annual': tsp_match_annual
    }


class TestFourYearTotals:
    """Integration tests for 4-year wealth projections."""

    def test_4yr_totals_basic(self):
        """Basic 4-year total calculation."""
        mil_results = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=2000  # Use manual for consistent testing
        )

        civ_results = calculate_civilian_net(
            base_salary=80000,
            bonus_pct=10,
            total_equity=0,
            state="VA",
            filing_status="single",
            annual_rsu_value=0,
            num_children=0
        )

        equity_calc = {'adjusted_value': 0}

        totals = calculate_4yr_totals(mil_results, civ_results, equity_calc)

        assert totals['mil_4yr_total'] > 0
        assert totals['civ_4yr_total'] > 0
        assert 'four_year_delta' in totals
        assert 'tsp_match_annual' in totals

    def test_4yr_totals_with_equity(self):
        """4-year totals including equity vesting."""
        mil_results = calculate_rmc(
            rank="O-3",
            years_of_service=4,
            location="SAN DIEGO, CA",
            has_dependents=False,
            filing_status="single",
            manual_bah=3000
        )

        equity_calc = calculate_rsu_value(
            total_grant=200000,
            vesting_years=4,
            is_public_company=True
        )

        civ_results = calculate_civilian_net(
            base_salary=150000,
            bonus_pct=15,
            total_equity=200000,
            state="CA",
            filing_status="single",
            annual_rsu_value=equity_calc['annualized_value'],
            num_children=0
        )

        totals = calculate_4yr_totals(mil_results, civ_results, equity_calc)

        # With $200k equity, civilian should have significant advantage
        assert totals['civ_4yr_total'] > totals['mil_4yr_total']
        assert totals['four_year_delta'] > 0

    def test_4yr_totals_no_equity(self):
        """4-year totals without any equity."""
        mil_results = calculate_rmc(
            rank="E-5",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=1800
        )

        civ_results = calculate_civilian_net(
            base_salary=60000,
            bonus_pct=0,
            total_equity=0,
            state="TX",  # No state tax
            filing_status="single",
            annual_rsu_value=0,
            num_children=0
        )

        totals = calculate_4yr_totals(mil_results, civ_results, None)

        # Both should be positive
        assert totals['mil_4yr_total'] > 0
        assert totals['civ_4yr_total'] > 0

    def test_4yr_tsp_match_calculation(self):
        """TSP match should be 5% of base pay."""
        mil_results = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=2000
        )

        civ_results = calculate_civilian_net(
            base_salary=80000,
            bonus_pct=0,
            total_equity=0,
            state="VA",
            filing_status="single"
        )

        totals = calculate_4yr_totals(mil_results, civ_results, None)

        expected_tsp = mil_results['base_pay_monthly'] * 0.05 * 12
        assert totals['tsp_match_annual'] == pytest.approx(expected_tsp, rel=0.01)

    def test_4yr_military_includes_tsp(self):
        """Military 4-year should include TSP match."""
        mil_results = calculate_rmc(
            rank="E-6",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=2000
        )

        civ_results = calculate_civilian_net(
            base_salary=80000,
            bonus_pct=0,
            total_equity=0,
            state="VA",
            filing_status="single"
        )

        totals = calculate_4yr_totals(mil_results, civ_results, None)

        # 4-year should be more than just 48 * monthly
        base_4yr = mil_results['total_monthly'] * 48
        assert totals['mil_4yr_total'] > base_4yr


class TestScenarioComparisons:
    """Real-world scenario comparison tests."""

    def test_scenario_e5_vs_80k_texas(self):
        """E-5 vs $80k offer in Texas (no state tax)."""
        mil_results = calculate_rmc(
            rank="E-5",
            years_of_service=6,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=1800
        )

        civ_results = calculate_civilian_net(
            base_salary=80000,
            bonus_pct=10,
            total_equity=0,
            state="TX",
            filing_status="single",
            annual_rsu_value=0,
            num_children=0
        )

        totals = calculate_4yr_totals(mil_results, civ_results, None)

        # Both paths should yield substantial wealth over 4 years
        assert totals['mil_4yr_total'] > 200000
        assert totals['civ_4yr_total'] > 200000

    def test_scenario_o3_vs_150k_equity_california(self):
        """O-3 vs $150k + equity offer in California (high tax)."""
        mil_results = calculate_rmc(
            rank="O-3",
            years_of_service=4,
            location="SAN DIEGO, CA",
            has_dependents=False,
            filing_status="single",
            manual_bah=3200
        )

        equity_calc = calculate_rsu_value(200000, 4, 0, True)

        civ_results = calculate_civilian_net(
            base_salary=150000,
            bonus_pct=15,
            total_equity=200000,
            state="CA",
            filing_status="single",
            annual_rsu_value=equity_calc['annualized_value'],
            num_children=0
        )

        totals = calculate_4yr_totals(mil_results, civ_results, equity_calc)

        # Despite CA taxes, $150k + $200k equity should beat O-3
        assert totals['four_year_delta'] > 0

    def test_scenario_o5_vs_executive(self):
        """Senior O-5 vs executive offer."""
        mil_results = calculate_rmc(
            rank="O-5",
            years_of_service=18,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=True,
            filing_status="married",
            manual_bah=3500
        )

        equity_calc = calculate_rsu_value(500000, 4, 0, True)

        civ_results = calculate_civilian_net(
            base_salary=250000,
            bonus_pct=25,
            total_equity=500000,
            state="VA",
            filing_status="married",
            annual_rsu_value=equity_calc['annualized_value'],
            num_children=2
        )

        totals = calculate_4yr_totals(mil_results, civ_results, equity_calc)

        # Executive package should significantly beat O-5
        assert totals['four_year_delta'] > 200000

    def test_scenario_private_equity_discount(self):
        """Private company equity gets discounted."""
        mil_results = calculate_rmc(
            rank="E-6",
            years_of_service=8,
            location="NORFOLK/PORTSMOUTH, VA",
            has_dependents=False,
            filing_status="single",
            manual_bah=2200
        )

        # Public equity
        equity_public = calculate_rsu_value(100000, 4, 0, True)
        civ_public = calculate_civilian_net(
            base_salary=100000, bonus_pct=10, total_equity=100000,
            state="VA", filing_status="single",
            annual_rsu_value=equity_public['annualized_value']
        )
        totals_public = calculate_4yr_totals(mil_results, civ_public, equity_public)

        # Private equity (50% discount)
        equity_private = calculate_rsu_value(100000, 4, 0, False)
        civ_private = calculate_civilian_net(
            base_salary=100000, bonus_pct=10, total_equity=100000,
            state="VA", filing_status="single",
            annual_rsu_value=equity_private['annualized_value']
        )
        totals_private = calculate_4yr_totals(mil_results, civ_private, equity_private)

        # Public offer should be worth more
        assert totals_public['civ_4yr_total'] > totals_private['civ_4yr_total']
