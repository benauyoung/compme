import streamlit as st
from supabase import create_client, Client
from typing import Optional


def get_supabase_client() -> Optional[Client]:
    """
    Initialize Supabase client from Streamlit secrets.
    Returns None if secrets are not configured.
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
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
    Silently logs a compensation scenario to Supabase.
    
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
        client = get_supabase_client()
        if client is None:
            return False
        
        data = {
            'rank': rank,
            'location': location,
            'years_service': years,
            'civ_base': civ_base,
            'civ_equity': civ_equity,
            'monthly_delta': delta
        }
        
        client.table('scenarios').insert(data).execute()
        return True
        
    except Exception:
        # Silent failure - do not crash the app
        return False
