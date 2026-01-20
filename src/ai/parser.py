import json
import os
from typing import Dict, Optional


def parse_offer_text(text_block: str, api_key: Optional[str] = None) -> Dict[str, any]:
    """
    Parse an offer letter using AI (OpenAI) or fallback to mock parsing.
    Automatically loads API key from environment if not provided.
    
    Args:
        text_block: Raw text from offer letter
        api_key: OpenAI API key (optional). If not provided, loads from .env
        
    Returns:
        Dictionary with extracted fields:
            - base_salary: float
            - sign_on_bonus: float
            - annual_bonus_percent: float
            - equity_grant: float
            - parse_method: 'ai' or 'mock'
            - parsing_confidence: float (0.0 to 1.0)
            - extracted_fields: list of field names successfully extracted
    """
    # Auto-load API key from environment if not provided
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == "" or api_key == "your_openai_api_key_here":
        print("⚠️ No OpenAI API key found - using regex fallback")
        return _mock_parse(text_block)
    
    print(f"✓ OpenAI API key found - attempting GPT-4 parsing...")
    try:
        result = _ai_parse(text_block, api_key)
        print(f"✓ AI parsing successful - extracted {len(result['extracted_fields'])} fields")
        return result
    except Exception as e:
        print(f"❌ AI parsing failed: {str(e)}")
        print("→ Falling back to regex parsing")
        return _mock_parse(text_block)


def _mock_parse(text_block: str) -> Dict[str, any]:
    """
    Mock parser for testing without API key.
    Uses simple keyword matching to extract numbers.
    """
    import re
    
    result = {
        "base_salary": 0,
        "sign_on_bonus": 0,
        "annual_bonus_percent": 0,
        "equity_grant": 0,
        "equity_shares": 0,
        "is_public_company": True,
        "parsing_confidence": 0.5,
        "extracted_fields": [],
        "parse_method": "mock"
    }
    
    text_lower = text_block.lower()
    
    base_patterns = [
        r'base salary[:\s]+\$([0-9,]+)',
        r'annual base salary[:\s]+\$([0-9,]+)',
        r'starting annual base salary[:\s]+\$([0-9,]+)',
        r'annual salary[:\s]+\$([0-9,]+)',
        r'salary of[:\s]+\$([0-9,]+)',
        r'salary will be \$([0-9,]+)',
    ]
    for pattern in base_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["base_salary"] = float(match.group(1).replace(',', ''))
            result["extracted_fields"].append("base_salary")
            break
    
    bonus_patterns = [
        r'sign[- ]?on bonus[:\s]+\$([0-9,]+)',
        r'signing bonus[:\s]+\$([0-9,]+)',
    ]
    for pattern in bonus_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["sign_on_bonus"] = float(match.group(1).replace(',', ''))
            result["extracted_fields"].append("sign_on_bonus")
            break
    
    bonus_pct_patterns = [
        r'annual bonus[:\s]+([0-9]+)%',
        r'target bonus[:\s]+([0-9]+)%',
        r'bonus target[:\s]+([0-9]+)%',
    ]
    for pattern in bonus_pct_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["annual_bonus_percent"] = float(match.group(1))
            result["extracted_fields"].append("annual_bonus_percent")
            break
    
    equity_patterns = [
        r'equity grant[:\s]+\$?([0-9,]+)',
        r'rsu grant[:\s]+\$?([0-9,]+)',
        r'stock grant[:\s]+\$?([0-9,]+)',
        r'equity package[:\s]+\$?([0-9,]+)',
    ]
    for pattern in equity_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["equity_grant"] = float(match.group(1).replace(',', ''))
            result["extracted_fields"].append("equity_grant")
            break
    
    shares_patterns = [
        r'([0-9,]+)\s+rsus',
        r'([0-9,]+)\s+shares',
        r'equity grant[:\s]+([0-9,]+)\s+rsus',
    ]
    for pattern in shares_patterns:
        match = re.search(pattern, text_lower)
        if match:
            shares = int(match.group(1).replace(',', ''))
            result["equity_shares"] = shares
            result["extracted_fields"].append("equity_shares")
            
            # If we have shares but no dollar value, estimate based on typical startup RSU value
            if result["equity_grant"] == 0 and shares > 0:
                # Assume $50/share as a conservative estimate (user can adjust)
                result["equity_grant"] = shares * 50
                result["extracted_fields"].append("equity_grant")
            break
    
    if "private" in text_lower or "startup" in text_lower:
        result["is_public_company"] = False
    
    result["parsing_confidence"] = len(result["extracted_fields"]) / 4.0
    
    return result


def _ai_parse(text_block: str, api_key: str) -> Dict[str, any]:
    """
    AI-powered parser using LangChain and OpenAI.
    Extracts structured compensation data from unstructured text.
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain.output_parsers import StructuredOutputParser, ResponseSchema
    except ImportError:
        print("LangChain not installed. Install with: pip install langchain langchain-openai")
        return _mock_parse(text_block)
    
    response_schemas = [
        ResponseSchema(name="base_salary", description="Annual base salary in dollars (number only, no commas or $)"),
        ResponseSchema(name="sign_on_bonus", description="One-time signing bonus in dollars (0 if not mentioned)"),
        ResponseSchema(name="annual_bonus_percent", description="Target annual bonus as percentage (e.g., 15 for 15%)"),
        ResponseSchema(name="equity_grant", description="Total equity grant value in dollars (0 if not mentioned)"),
        ResponseSchema(name="equity_shares", description="Number of RSU/stock shares granted (0 if not mentioned)"),
        ResponseSchema(name="is_public_company", description="true if publicly traded company, false if startup/private"),
    ]
    
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    
    prompt = PromptTemplate(
        template="""You are an expert at parsing job offer letters and extracting compensation details.

Extract the following information from this offer letter text. The letter may contain tables, formatted text, or mixed layouts.

IMPORTANT INSTRUCTIONS:
- Look for dollar amounts near keywords like "base salary", "annual salary", "starting salary"
- Sign-on bonus may be called "signing bonus" or "sign-on bonus"
- Annual bonus is often expressed as a percentage (e.g., "15%")
- RSUs/Stock may be expressed as number of shares (e.g., "2,500 RSUs") - if so, estimate value at $50/share
- If a field is not mentioned, use 0 for numbers or false for booleans

Offer Letter Text:
{text}

{format_instructions}

Return ONLY valid JSON, no explanations or additional text.""",
        input_variables=["text"],
        partial_variables={"format_instructions": format_instructions}
    )
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=api_key,
        verbose=True
    )
    
    chain = prompt | llm | output_parser
    
    try:
        parsed = chain.invoke({"text": text_block})
        
        result = {
            "base_salary": float(parsed.get("base_salary", 0)),
            "sign_on_bonus": float(parsed.get("sign_on_bonus", 0)),
            "annual_bonus_percent": float(parsed.get("annual_bonus_percent", 0)),
            "equity_grant": float(parsed.get("equity_grant", 0)),
            "equity_shares": int(parsed.get("equity_shares", 0)),
            "is_public_company": bool(parsed.get("is_public_company", True)),
            "parsing_confidence": 0.9,
            "extracted_fields": [k for k, v in parsed.items() if v not in [0, False, "0"]],
            "parse_method": "ai"
        }
        
        return result
        
    except Exception as e:
        print(f"OpenAI parsing failed: {str(e)}")
        return _mock_parse(text_block)
