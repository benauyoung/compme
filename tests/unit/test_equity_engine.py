"""
Unit tests for Equity Calculation Engine (equity_engine.py)
"""
import pytest
from engines.equity_engine import (
    CompanyStage,
    STAGE_DISCOUNTS,
    STAGE_DESCRIPTIONS,
    calculate_rsu_value,
    calculate_vesting_schedule,
    compare_equity_offers
)


class TestCompanyStage:
    """Tests for CompanyStage enum and discounts."""

    def test_stage_values(self):
        """Verify enum values."""
        assert CompanyStage.PUBLIC.value == "public"
        assert CompanyStage.PRE_IPO.value == "pre_ipo"
        assert CompanyStage.LATE_STAGE.value == "late_stage"
        assert CompanyStage.GROWTH.value == "growth"
        assert CompanyStage.EARLY.value == "early"

    def test_stage_discounts(self):
        """Verify discount percentages."""
        assert STAGE_DISCOUNTS[CompanyStage.PUBLIC] == 0.0
        assert STAGE_DISCOUNTS[CompanyStage.PRE_IPO] == 0.15
        assert STAGE_DISCOUNTS[CompanyStage.LATE_STAGE] == 0.30
        assert STAGE_DISCOUNTS[CompanyStage.GROWTH] == 0.50
        assert STAGE_DISCOUNTS[CompanyStage.EARLY] == 0.70

    def test_all_stages_have_descriptions(self):
        """All stages should have descriptions."""
        for stage in CompanyStage:
            assert stage in STAGE_DESCRIPTIONS
            assert len(STAGE_DESCRIPTIONS[stage]) > 0


class TestCalculateRSUValue:
    """Tests for calculate_rsu_value function."""

    def test_rsu_public_no_discount(self):
        """Public company gets 0% discount."""
        result = calculate_rsu_value(100000, 4, 0, True, CompanyStage.PUBLIC)

        assert result["total_grant_value"] == 100000
        assert result["adjusted_value"] == 100000
        assert result["risk_discount"] == 0

    def test_rsu_pre_ipo_15_discount(self):
        """Pre-IPO gets 15% discount."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.PRE_IPO)

        assert result["adjusted_value"] == 85000
        assert result["risk_discount"] == 15

    def test_rsu_late_stage_30_discount(self):
        """Late stage gets 30% discount."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.LATE_STAGE)

        assert result["adjusted_value"] == 70000
        assert result["risk_discount"] == 30

    def test_rsu_growth_50_discount(self):
        """Growth stage gets 50% discount."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.GROWTH)

        assert result["adjusted_value"] == 50000
        assert result["risk_discount"] == 50

    def test_rsu_early_70_discount(self):
        """Early stage gets 70% discount."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.EARLY)

        assert result["adjusted_value"] == pytest.approx(30000, rel=0.01)
        assert result["risk_discount"] == 70

    def test_rsu_zero_grant(self):
        """Zero grant should return zeros."""
        result = calculate_rsu_value(0, 4, 0, True)

        assert result["total_grant_value"] == 0
        assert result["adjusted_value"] == 0
        assert result["annualized_value"] == 0
        assert result["monthly_value"] == 0

    def test_rsu_negative_grant(self):
        """Negative grant should return zeros."""
        result = calculate_rsu_value(-10000, 4, 0, True)
        assert result["total_grant_value"] == 0

    def test_rsu_annualized_value(self):
        """Annualized value should be adjusted / vesting years."""
        result = calculate_rsu_value(100000, 4, 0, True, CompanyStage.PUBLIC)

        assert result["annualized_value"] == pytest.approx(25000, rel=0.01)

    def test_rsu_monthly_value(self):
        """Monthly value should be annualized / 12."""
        result = calculate_rsu_value(100000, 4, 0, True, CompanyStage.PUBLIC)

        assert result["monthly_value"] == pytest.approx(25000 / 12, rel=0.01)

    def test_rsu_custom_vesting_years(self):
        """Different vesting periods should work."""
        result_3yr = calculate_rsu_value(120000, 3, 0, True)
        result_4yr = calculate_rsu_value(120000, 4, 0, True)

        assert result_3yr["annualized_value"] == pytest.approx(40000, rel=0.01)
        assert result_4yr["annualized_value"] == pytest.approx(30000, rel=0.01)

    def test_rsu_legacy_is_public_true(self):
        """Legacy is_public=True should work."""
        result = calculate_rsu_value(100000, 4, 0, is_public_company=True)

        assert result["adjusted_value"] == 100000
        assert result["risk_discount"] == 0

    def test_rsu_legacy_is_public_false(self):
        """Legacy is_public=False should default to GROWTH (50%)."""
        result = calculate_rsu_value(100000, 4, 0, is_public_company=False)

        assert result["adjusted_value"] == 50000
        assert result["risk_discount"] == 50

    def test_rsu_stage_overrides_is_public(self):
        """Explicit company_stage should override is_public."""
        result = calculate_rsu_value(
            100000, 4, 0,
            is_public_company=False,
            company_stage=CompanyStage.PUBLIC
        )

        assert result["adjusted_value"] == 100000
        assert result["risk_discount"] == 0

    def test_rsu_liquidity_note_includes_discount(self):
        """Private company notes should mention discount."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.GROWTH)

        assert "50%" in result["liquidity_note"]
        assert "discount" in result["liquidity_note"].lower()

    def test_rsu_returns_company_stage(self):
        """Result should include company stage value."""
        result = calculate_rsu_value(100000, 4, 0, False, CompanyStage.LATE_STAGE)

        assert result["company_stage"] == "late_stage"


class TestCalculateVestingSchedule:
    """Tests for calculate_vesting_schedule function."""

    def test_vesting_schedule_4yr_standard(self):
        """Standard 4-year vesting with 1-year cliff."""
        schedule = calculate_vesting_schedule(100000, 4, 12, True)

        assert len(schedule) == 4

        # Year 1: 25% vests at cliff
        assert schedule[1]["vested_this_year"] == pytest.approx(25000, rel=0.01)
        assert schedule[1]["cumulative_vested"] == pytest.approx(25000, rel=0.01)

        # Year 4: 100% fully vested
        assert schedule[4]["cumulative_vested"] == pytest.approx(100000, rel=0.01)
        assert schedule[4]["remaining_unvested"] == pytest.approx(0, abs=1)

    def test_vesting_schedule_with_discount(self):
        """Vesting should apply risk discount."""
        schedule = calculate_vesting_schedule(100000, 4, 12, False, CompanyStage.GROWTH)

        # 50% discount = $50k adjusted
        assert schedule[4]["cumulative_vested"] == pytest.approx(50000, rel=0.01)

    def test_vesting_schedule_cumulative_increases(self):
        """Cumulative should increase each year."""
        schedule = calculate_vesting_schedule(100000, 4, 12, True)

        prev_cumulative = 0
        for year in range(1, 5):
            assert schedule[year]["cumulative_vested"] > prev_cumulative
            prev_cumulative = schedule[year]["cumulative_vested"]

    def test_vesting_schedule_remaining_decreases(self):
        """Remaining unvested should decrease each year."""
        schedule = calculate_vesting_schedule(100000, 4, 12, True)

        prev_remaining = 100000
        for year in range(1, 5):
            assert schedule[year]["remaining_unvested"] < prev_remaining
            prev_remaining = schedule[year]["remaining_unvested"]

    def test_vesting_schedule_3_year(self):
        """3-year vesting schedule."""
        schedule = calculate_vesting_schedule(90000, 3, 12, True)

        assert len(schedule) == 3
        assert schedule[1]["vested_this_year"] == pytest.approx(30000, rel=0.01)
        assert schedule[3]["cumulative_vested"] == pytest.approx(90000, rel=0.01)


class TestCompareEquityOffers:
    """Tests for compare_equity_offers function."""

    def test_compare_public_vs_public(self):
        """Compare two public company offers."""
        offer_a = {"total_grant": 100000, "vesting_years": 4, "is_public": True}
        offer_b = {"total_grant": 80000, "vesting_years": 4, "is_public": True}

        result = compare_equity_offers(offer_a, offer_b)

        assert result["winner"] == "Offer A"
        assert result["offer_a_monthly"] > result["offer_b_monthly"]

    def test_compare_public_vs_private(self):
        """Public offer may beat larger private offer due to discount."""
        offer_public = {"total_grant": 100000, "vesting_years": 4, "is_public": True}
        offer_private = {"total_grant": 150000, "vesting_years": 4, "is_public": False}

        result = compare_equity_offers(offer_public, offer_private)

        # Public: $100k, Private: $150k * 50% = $75k adjusted
        assert result["winner"] == "Offer A"

    def test_compare_same_value(self):
        """Equal adjusted values should tie."""
        offer_a = {"total_grant": 50000, "vesting_years": 4, "is_public": True}
        offer_b = {"total_grant": 100000, "vesting_years": 4, "is_public": False}

        result = compare_equity_offers(offer_a, offer_b)

        # Both have $50k adjusted value
        assert result["winner"] == "Tie"

    def test_compare_with_company_stage(self):
        """Compare using explicit company stages."""
        offer_a = {
            "total_grant": 100000,
            "vesting_years": 4,
            "company_stage": "pre_ipo"  # 15% discount
        }
        offer_b = {
            "total_grant": 100000,
            "vesting_years": 4,
            "company_stage": "early"  # 70% discount
        }

        result = compare_equity_offers(offer_a, offer_b)

        # A: $85k adjusted, B: $30k adjusted
        assert result["winner"] == "Offer A"

    def test_compare_different_vesting(self):
        """Different vesting periods affect monthly value."""
        offer_3yr = {"total_grant": 90000, "vesting_years": 3, "is_public": True}
        offer_4yr = {"total_grant": 100000, "vesting_years": 4, "is_public": True}

        result = compare_equity_offers(offer_3yr, offer_4yr)

        # 3yr: $30k/year = $2.5k/month
        # 4yr: $25k/year = $2.08k/month
        assert result["winner"] == "Offer A"
