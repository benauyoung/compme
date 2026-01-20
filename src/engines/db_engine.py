import streamlit as st
import httpx
from typing import Optional


def get_supabase_config() -> Optional[tuple[str, str]]:
    """
    Get Supabase configuration from Streamlit secrets.
    Returns (url, key) tuple or None if not configured.
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return (url, key)
    except Exception:
        return None


def log_scenario(
    rank: str,
    location: str,
    years: int,
    civ_base: float,
    civ_equity: float,
    delta: float
) -> bool:
    """
    Silently logs a compensation scenario to Supabase via REST API.
    
    This function captures user inputs without any UI feedback.
    If the database is unavailable or credentials are invalid,
    it fails silently without crashing the app.
    
    Args:
        rank: Military rank (e.g., "E-6", "O-3")
        location: Duty station name
        years: Years of service
        civ_base: Civilian base salary
        civ_equity: Civilian equity grant
        delta: Monthly delta (military - civilian)
        
    Returns:
        True if logged successfully, False otherwise (silent failure)
    """
    try:
        config = get_supabase_config()
        if config is None:
            print("❌ DEBUG: Supabase config not found - secrets not configured")
            return False
        
        url, key = config
        
        data = {
            'rank': rank,
            'location': location,
            'years_service': years,
            'civ_base': civ_base,
            'civ_equity': civ_equity,
            'monthly_delta': delta
        }
        
        print(f"✅ DEBUG: Attempting to insert: {data}")
        
        # Supabase REST API endpoint
        endpoint = f"{url}/rest/v1/scenarios"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        response = httpx.post(endpoint, json=data, headers=headers, timeout=5.0)
        
        if response.status_code in [200, 201]:
            print(f"✅ DEBUG: Insert successful! Status: {response.status_code}")
            return True
        else:
            print(f"❌ DEBUG: Insert failed. Status: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        # Silent failure - do not crash the app
        print(f"❌ DEBUG: Error logging scenario: {e}")
        return False
