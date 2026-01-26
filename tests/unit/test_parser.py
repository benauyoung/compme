"""
Unit tests for Offer Letter Parser (parser.py)
"""
import pytest
from ai.parser import parse_offer_text, _mock_parse


class TestMockParser:
    """Tests for regex-based mock parser."""

    def test_parse_base_salary_with_dollar_sign(self):
        """Parse base salary with $ and commas."""
        text = "Your base salary will be $120,000 per year."
        result = _mock_parse(text)

        assert result["base_salary"] == 120000
        assert "base_salary" in result["extracted_fields"]

    def test_parse_base_salary_variations(self):
        """Parse different base salary formats."""
        texts = [
            "Base Salary: $100,000",
            "Annual base salary: $100,000",
            "Starting annual base salary: $100,000",
            "Your salary will be $100,000",
        ]

        for text in texts:
            result = _mock_parse(text)
            assert result["base_salary"] == 100000, f"Failed on: {text}"

    def test_parse_signing_bonus(self):
        """Parse signing bonus."""
        text = "You will receive a sign-on bonus: $25,000"
        result = _mock_parse(text)

        assert result["sign_on_bonus"] == 25000
        assert "sign_on_bonus" in result["extracted_fields"]

    def test_parse_signing_bonus_variations(self):
        """Parse different signing bonus formats."""
        texts = [
            "Sign-on bonus: $20,000",
            "Signing bonus: $20,000",
        ]

        for text in texts:
            result = _mock_parse(text)
            assert result["sign_on_bonus"] == 20000, f"Failed on: {text}"

    def test_parse_annual_bonus_percent(self):
        """Parse annual bonus as percentage."""
        text = "Your annual bonus: 15% of base salary."
        result = _mock_parse(text)

        assert result["annual_bonus_percent"] == 15
        assert "annual_bonus_percent" in result["extracted_fields"]

    def test_parse_bonus_percent_variations(self):
        """Parse different bonus percentage formats."""
        texts = [
            "Annual bonus: 20%",
            "Target bonus: 20%",
            "Bonus target: 20%",
            "Performance bonus: 20%",
        ]

        for text in texts:
            result = _mock_parse(text)
            assert result["annual_bonus_percent"] == 20, f"Failed on: {text}"

    def test_parse_annual_bonus_amount(self):
        """Parse annual bonus as dollar amount."""
        text = "Your annual bonus: $15,000 annually."
        result = _mock_parse(text)

        assert result["annual_bonus_amount"] == 15000
        assert "annual_bonus_amount" in result["extracted_fields"]

    def test_parse_equity_grant_dollars(self):
        """Parse equity grant as dollar value."""
        text = "You will receive an equity grant: $100,000"
        result = _mock_parse(text)

        assert result["equity_grant"] == 100000
        assert "equity_grant" in result["extracted_fields"]

    def test_parse_equity_shares(self):
        """Parse equity as number of RSUs."""
        text = "You will receive 2,500 RSUs vesting over 4 years."
        result = _mock_parse(text)

        assert result["equity_shares"] == 2500
        assert "equity_shares" in result["extracted_fields"]
        # Should estimate value at $50/share
        assert result["equity_grant"] == 125000

    def test_parse_private_company(self):
        """Detect private company from text."""
        text = "We are an exciting startup in the fintech space."
        result = _mock_parse(text)

        assert result["is_public_company"] == False

    def test_parse_public_company_default(self):
        """Default to public company if not mentioned."""
        text = "Base salary: $100,000"
        result = _mock_parse(text)

        assert result["is_public_company"] == True

    def test_parse_empty_input(self):
        """Empty input should return defaults."""
        result = _mock_parse("")

        assert result["base_salary"] == 0
        assert result["sign_on_bonus"] == 0
        assert result["annual_bonus_percent"] == 0
        assert result["equity_grant"] == 0
        assert len(result["extracted_fields"]) == 0

    def test_parse_no_matches(self):
        """Text with no comp info returns zeros."""
        text = "Thank you for interviewing with us. We enjoyed meeting you."
        result = _mock_parse(text)

        assert result["base_salary"] == 0
        assert len(result["extracted_fields"]) == 0

    def test_parse_confidence_score(self):
        """Confidence should scale with extracted fields."""
        result_empty = _mock_parse("")
        result_partial = _mock_parse("Base salary: $100,000")
        result_full = _mock_parse("""
            Base salary: $100,000
            Sign-on bonus: $10,000
            Annual bonus: 15%
            Equity grant: $50,000
        """)

        assert result_empty["parsing_confidence"] == 0
        assert result_partial["parsing_confidence"] > 0
        assert result_full["parsing_confidence"] > result_partial["parsing_confidence"]

    def test_parse_method_is_mock(self):
        """Mock parser should set parse_method to 'mock'."""
        result = _mock_parse("Base salary: $100,000")
        assert result["parse_method"] == "mock"


class TestParseOfferText:
    """Tests for main parse_offer_text function."""

    def test_parse_without_api_key(self):
        """Without API key, should use mock parser."""
        text = "Base salary: $100,000"
        result = parse_offer_text(text, api_key=None)

        assert result["parse_method"] == "mock"
        assert result["base_salary"] == 100000

    def test_parse_with_invalid_api_key(self):
        """Invalid API key should fall back to mock."""
        text = "Base salary: $100,000"
        result = parse_offer_text(text, api_key="")

        assert result["parse_method"] == "mock"

    def test_parse_stores_raw_text(self):
        """Result should include original text."""
        text = "Base salary: $100,000"
        result = parse_offer_text(text)

        assert result["raw_text"] == text

    def test_parse_full_offer_letter(self, sample_offer_letter_full):
        """Parse a complete offer letter."""
        result = parse_offer_text(sample_offer_letter_full)

        assert result["base_salary"] == 150000
        assert result["sign_on_bonus"] == 25000
        assert result["annual_bonus_percent"] == 20


class TestParseEdgeCases:
    """Edge case tests for parser."""

    def test_parse_case_insensitive(self):
        """Parser should be case insensitive."""
        text_lower = "base salary: $100,000"
        text_upper = "BASE SALARY: $100,000"
        text_mixed = "Base Salary: $100,000"

        for text in [text_lower, text_upper, text_mixed]:
            result = _mock_parse(text)
            assert result["base_salary"] == 100000, f"Failed on: {text}"

    def test_parse_no_spaces(self):
        """Handle text without spaces after colon."""
        text = "Base Salary:$100,000"
        result = _mock_parse(text)
        assert result["base_salary"] == 100000

    def test_parse_multiple_amounts(self):
        """Should extract first matching amount."""
        text = """
        Your compensation:
        Base salary: $100,000
        After promotion: $120,000
        """
        result = _mock_parse(text)
        # Should get first base salary mention
        assert result["base_salary"] == 100000

    def test_parse_large_numbers(self):
        """Handle large salary values."""
        text = "Base salary: $1,500,000"
        result = _mock_parse(text)
        assert result["base_salary"] == 1500000
