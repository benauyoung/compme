"""
Unit tests for Utility Formatters (formatters.py)
"""
import pytest
from utils.formatters import (
    format_currency,
    format_percentage,
    format_delta,
    annual_to_monthly,
    monthly_to_annual
)


class TestFormatCurrency:
    """Tests for format_currency function."""

    def test_format_currency_basic(self):
        """Basic currency formatting."""
        assert format_currency(1000) == "$1,000"
        assert format_currency(50000) == "$50,000"
        assert format_currency(1234567) == "$1,234,567"

    def test_format_currency_with_cents(self):
        """Currency with cents enabled."""
        assert format_currency(1000.50, show_cents=True) == "$1,000.50"
        assert format_currency(1234.99, show_cents=True) == "$1,234.99"

    def test_format_currency_rounds_without_cents(self):
        """Without cents, should round to whole number."""
        assert format_currency(1000.75) == "$1,001"
        assert format_currency(1000.25) == "$1,000"

    def test_format_currency_zero(self):
        """Zero should format correctly."""
        assert format_currency(0) == "$0"

    def test_format_currency_negative(self):
        """Negative values should show minus sign."""
        result = format_currency(-1000)
        assert "-" in result or "(" in result


class TestFormatPercentage:
    """Tests for format_percentage function."""

    def test_format_percentage_basic(self):
        """Basic percentage formatting."""
        assert format_percentage(15.5) == "15.5%"
        assert format_percentage(100) == "100.0%"

    def test_format_percentage_custom_decimals(self):
        """Custom decimal places."""
        # Note: 15.555 is represented as ~15.5549999... in floating point
        assert format_percentage(15.556, decimals=2) == "15.56%"
        assert format_percentage(15.555, decimals=0) == "16%"

    def test_format_percentage_zero(self):
        """Zero percentage."""
        assert format_percentage(0) == "0.0%"


class TestFormatDelta:
    """Tests for format_delta function."""

    def test_format_delta_positive(self):
        """Positive delta should have plus sign."""
        result = format_delta(1000)
        assert result == "+$1,000"

    def test_format_delta_negative(self):
        """Negative delta should have minus sign."""
        result = format_delta(-1000)
        assert "-" in result
        assert "1,000" in result

    def test_format_delta_zero(self):
        """Zero delta."""
        result = format_delta(0)
        assert "$0" in result

    def test_format_delta_with_cents(self):
        """Delta with cents."""
        result = format_delta(1000.50, show_cents=True)
        assert "+$1,000.50" == result


class TestAnnualMonthlyConversion:
    """Tests for annual/monthly conversion functions."""

    def test_annual_to_monthly(self):
        """Convert annual to monthly."""
        assert annual_to_monthly(120000) == 10000
        assert annual_to_monthly(60000) == 5000

    def test_monthly_to_annual(self):
        """Convert monthly to annual."""
        assert monthly_to_annual(10000) == 120000
        assert monthly_to_annual(5000) == 60000

    def test_round_trip_conversion(self):
        """Round trip should return original value."""
        original = 123456
        monthly = annual_to_monthly(original)
        back_to_annual = monthly_to_annual(monthly)
        assert back_to_annual == pytest.approx(original, rel=0.001)
