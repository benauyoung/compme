import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(__file__))

from engines.mil_engine import calculate_rmc
from engines.civ_engine import calculate_civilian_net
from engines.equity_engine import calculate_rsu_value, calculate_vesting_schedule
from engines.bah_engine import bah_fetcher
from engines.db_engine import log_scenario
from ai.parser import parse_offer_text
from utils.formatters import format_currency, format_delta, annual_to_monthly
from utils.charts import render_wealth_chart, generate_executive_summary


st.set_page_config(
    page_title="CompMe - Military vs Civilian Compensation",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        background-color: #f8f9fa;
    }
    
    .positive {
        color: #10b981;
    }
    
    .negative {
        color: #ef4444;
    }
    
    /* Make tax and bonus detail metrics smaller - reduce all metric values globally */
    [data-testid="stMetricValue"] {
        font-size: 0.9rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    
    /* Ensure side-by-side bordered containers have equal heights */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 100%;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)


with st.expander("Enter Offer Letter", expanded=False):
    st.caption("Paste your full offer letter - AI will extract all compensation details")
    offer_text = st.text_area(
        "Offer Letter Text",
        height=200,
        placeholder="Paste your entire offer letter here - OpenAI will extract the details automatically!\n\nExample:\nBase Salary: $120,000\nSign-on Bonus: $10,000\nAnnual Bonus: 15%\nEquity Grant: $100,000 in RSUs vesting over 4 years",
        label_visibility="collapsed"
    )
    
    parse_button = st.button("Parse Offer", use_container_width=True, type="primary")
    
    if parse_button and offer_text:
        with st.spinner("Analyzing your offer letter..."):
            parsed = parse_offer_text(offer_text)
            st.session_state['parsed_data'] = parsed
            
            if parsed['parse_method'] == 'ai':
                st.success(f"AI Parser extracted {len(parsed['extracted_fields'])} fields (confidence: {parsed['parsing_confidence']:.0%})")
            else:
                st.info(f"Using pattern matching - extracted {len(parsed['extracted_fields'])} fields")
            
            with st.expander("View Parsed Data", expanded=False):
                st.json(parsed)

if 'parsed_data' not in st.session_state:
    st.session_state['parsed_data'] = None

st.markdown("<br>", unsafe_allow_html=True)

col_mil, col_civ = st.columns(2)

with col_mil:
    with st.container(border=True):
        st.subheader("Military Compensation")
        
        rank_options = [
            "E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9",
            "O-1", "O-2", "O-3", "O-4", "O-5", "O-6"
        ]
        rank = st.selectbox("Rank", rank_options, index=5)
        
        years_of_service = st.slider("Years of Service", min_value=0, max_value=30, value=6)
        
        has_dependents = st.checkbox("Have Dependents?", value=False)
        
        st.markdown("---")
        
        # Military Bonus (optional special pays, retention bonuses, etc)
        mil_annual_bonus = st.number_input("Annual Bonus/Special Pay ($)", min_value=0, max_value=100000, value=0, step=1000, help="Retention bonus, flight pay, hazard pay, etc.")
        
        st.markdown("---")
        
        # Duty Station Dropdown
        all_locations = bah_fetcher.get_all_locations()
        
        # Set default to Norfolk or San Diego if available
        default_location = "NORFOLK/PORTSMOUTH, VA"
        if default_location not in all_locations and len(all_locations) > 0:
            # Try San Diego
            default_location = "SAN DIEGO, CA"
            if default_location not in all_locations:
                default_location = all_locations[0]
        
        default_idx = all_locations.index(default_location) if default_location in all_locations else 0
        
        location = st.selectbox(
            "Select Duty Station",
            options=all_locations,
            index=default_idx,
            help="Official 2026 BAH rates for all duty stations"
        )
        
        # Optional manual override in expander for mobile
        with st.expander("Manual BAH Override", expanded=False):
            st.caption("Override official BAH data with custom amount")
            manual_override = st.checkbox("Enable Manual Override", value=False)
            
            if manual_override:
                manual_bah = st.number_input(
                    "Monthly BAH Amount ($)",
                    min_value=0,
                    max_value=10000,
                    value=2000,
                    step=50
                )
            else:
                manual_bah = None

with col_civ:
    with st.container(border=True):
        st.subheader("Civilian Offer")
        
        parsed = st.session_state.get('parsed_data')
        
        if parsed:
            default_base = int(parsed.get('base_salary', 100000))
            parsed_bonus_pct = parsed.get('annual_bonus_percent', 0)
            parsed_bonus_amt = parsed.get('annual_bonus_amount', 0)
            if (not parsed_bonus_pct or float(parsed_bonus_pct) == 0) and parsed_bonus_amt and default_base > 0:
                default_bonus_pct = int(round((float(parsed_bonus_amt) / float(default_base)) * 100))
            else:
                default_bonus_pct = int(parsed_bonus_pct) if parsed_bonus_pct else 15
            default_equity = int(parsed.get('equity_grant', 0))
            default_public = parsed.get('is_public_company', True)
        else:
            default_base = 100000
            default_bonus_pct = 15
            default_equity = 0
            default_public = True
        
        base_salary = st.number_input("Base Salary (Annual)", min_value=0, max_value=500000, value=default_base, step=5000)
        
        sign_on_bonus = st.number_input("Sign-On Bonus ($)", min_value=0, max_value=200000, value=0, step=5000, help="One-time signing bonus")
        
        bonus_pct = st.slider("Annual Bonus Target (%)", min_value=0, max_value=100, value=default_bonus_pct)
        
        civ_state = st.selectbox(
            "State of Residence",
            ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
             "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
             "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
             "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
             "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
            index=45,
            help="No income tax: AK, FL, NV, SD, TN, TX, WA, WY | Highest rates: CA, HI, NY, NJ"
        )
        
        with st.expander("Equity Package", expanded=default_equity > 0):
            total_equity = st.number_input("Total Equity Grant ($)", min_value=0, max_value=5000000, value=default_equity, step=10000)
            
            col_eq1, col_eq2 = st.columns(2)
            with col_eq1:
                vesting_years = st.number_input("Vesting Years", min_value=1, max_value=6, value=4)
            with col_eq2:
                is_public = st.checkbox("Public Company?", value=default_public, help="Private companies get 50% risk discount")
            
            if total_equity > 0:
                equity_calc = calculate_rsu_value(total_equity, vesting_years, 0, is_public)
                st.info(f"{equity_calc['liquidity_note']}")
                if equity_calc['risk_discount'] > 0:
                    st.warning(f"Applied {equity_calc['risk_discount']:.0f}% risk discount: ${format_currency(equity_calc['adjusted_value'])} adjusted value")

# Tax Filing Settings - shared section below inputs
st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Tax Filing Settings")
    col_tax1, col_tax2 = st.columns(2)
    
    with col_tax1:
        st.markdown("**Military Tax Filing**")
        filing_status_mil = st.radio("Filing Status", ["Single", "Married"], key="mil_filing", horizontal=True, label_visibility="collapsed")
    
    with col_tax2:
        st.markdown("**Civilian Tax Filing**")
        filing_status_civ = st.radio("Filing Status", ["Single", "Married"], key="civ_filing", horizontal=True, label_visibility="collapsed")

# Use civ_state as state variable
state = civ_state

# Calculate military results AFTER filing_status_mil is defined
mil_results = calculate_rmc(
    rank=rank,
    years_of_service=years_of_service,
    location=location,
    has_dependents=has_dependents,
    filing_status=filing_status_mil.lower(),
    manual_bah=manual_bah
)

# Calculate civilian results AFTER state and filing_status_civ are defined
if total_equity > 0:
    equity_calc = calculate_rsu_value(total_equity, vesting_years, 0, is_public)
    annual_rsu = equity_calc['annualized_value']
else:
    annual_rsu = 0

civ_results = calculate_civilian_net(
    base_salary=base_salary,
    bonus_pct=bonus_pct,
    total_equity=total_equity,
    state=state,
    filing_status=filing_status_civ.lower(),
    annual_rsu_value=annual_rsu
)

col_details1, col_details2 = st.columns(2)

with col_details1:
    with st.container(border=True):
        st.subheader("Military Tax and Bonus Details")
        
        mil_bonus_annual = mil_annual_bonus
        mil_fed_tax = mil_results.get('fed_tax', 0)
        mil_fica_tax = mil_results.get('fica_tax', 0)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Annual Bonus", format_currency(mil_bonus_annual))
            st.metric("Federal Tax (Annual)", format_currency(mil_fed_tax))
        with col_m2:
            st.metric("FICA (Annual)", format_currency(mil_fica_tax))
            st.metric("State Tax", "$0 (Tax-Free BAH/BAS)")

with col_details2:
    with st.container(border=True):
        st.subheader("Civilian Tax and Bonus Details")
        
        bonus_gross = civ_results.get('bonus_annual', 0)
        bonus_net = civ_results.get('bonus_net', 0)
        state_tax_annual = civ_results.get('state_tax', 0)
        state_tax_rate = civ_results.get('state_effective_rate', 0) * 100
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric("Annual Bonus (Gross)", format_currency(bonus_gross))
            st.metric("Annual Bonus (Net)", format_currency(bonus_net))
            st.metric("State Tax (Annual)", format_currency(state_tax_annual))
        with col_c2:
            st.metric("State Tax Rate", f"{state_tax_rate:.2f}%")
            st.metric("Federal Tax (Annual)", format_currency(civ_results.get('fed_tax', 0)))
            st.metric("FICA (Annual)", format_currency(civ_results.get('fica_tax', 0)))

st.markdown("<br>", unsafe_allow_html=True)

delta = mil_results['total_monthly'] - civ_results['net_monthly']
mil_4yr_total = mil_results['total_monthly'] * 48 + (mil_results['base_pay_monthly'] * 0.05 * 12 * 4)
if total_equity > 0:
    equity_calc_top = calculate_rsu_value(total_equity, vesting_years, 0, is_public)
    civ_4yr_total = civ_results['net_monthly'] * 48 + equity_calc_top['adjusted_value']
else:
    civ_4yr_total = civ_results['net_monthly'] * 48

four_year_delta = civ_4yr_total - mil_4yr_total
tax_efficiency = (1 - civ_results['effective_tax_rate']) * 100

# Silent data capture - log scenario to Supabase without UI feedback
fingerprint = f"{rank}_{location}_{years_of_service}_{base_salary}_{total_equity}"
if st.session_state.get('last_saved') != fingerprint:
    # Get offer letter text if it was submitted
    parsed_data = st.session_state.get('parsed_data')
    submitted_offer = parsed_data.get('raw_text', '') if parsed_data and isinstance(parsed_data, dict) else ''
    
    log_scenario(
        rank=rank,
        location=location,
        years=years_of_service,
        civ_base=base_salary,
        civ_equity=total_equity,
        delta=delta,
        offer_text=submitted_offer
    )
    st.session_state['last_saved'] = fingerprint

st.markdown("<br><br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Compensation Breakdown")
    
    # Month-to-Month and Year-to-Year Comparison
    comp_tab1, comp_tab2 = st.tabs(["Monthly Comparison", "Yearly Comparison"])
    
    with comp_tab1:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(
                "Military Monthly",
                format_currency(mil_results['total_monthly']),
                help="Tax-advantaged compensation (BAH/BAS not taxed)"
            )
        with col_m2:
            st.metric(
                "Civilian Monthly (After Tax)",
                format_currency(civ_results['net_monthly']),
                help="Take-home pay after federal, state, and FICA taxes"
            )
        with col_m3:
            delta_monthly = mil_results['total_monthly'] - civ_results['net_monthly']
            st.metric(
                "Monthly Delta",
                format_delta(delta_monthly),
                delta=delta_monthly,
                delta_color="normal"
            )
    
    with comp_tab2:
        mil_annual = mil_results['total_monthly'] * 12
        civ_annual = civ_results['net_monthly'] * 12
        
        # Add annual bonus for civilian
        if bonus_pct > 0:
            annual_bonus_amount = base_salary * (bonus_pct / 100)
            # Estimate ~40% tax on bonus
            civ_annual += annual_bonus_amount * 0.6
        
        # Add annual equity vesting if applicable
        if total_equity > 0:
            civ_annual += annual_rsu
        
        delta_annual = mil_annual - civ_annual
        
        col_y1, col_y2, col_y3 = st.columns(3)
        with col_y1:
            st.metric(
                "Military Annual",
                format_currency(mil_annual),
                help="Monthly compensation × 12 (excludes TSP match)"
            )
        with col_y2:
            st.metric(
                "Civilian Annual (After Tax)",
                format_currency(civ_annual),
                help="Includes after-tax bonus and annual equity vesting"
            )
        with col_y3:
            st.metric(
                "Annual Delta",
                format_delta(delta_annual),
                delta=delta_annual,
                delta_color="normal"
            )

st.markdown("<br>", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    with st.container(border=True):
        st.markdown("#### Military Breakdown")
        mil_chart = go.Figure(data=[
            go.Bar(
                x=['Base Pay', 'BAH', 'BAS'],
                y=[mil_results['base_pay_monthly'], mil_results['bah_monthly'], mil_results['bas_monthly']],
                marker_color=['#3b82f6', '#10b981', '#10b981'],
                text=[format_currency(mil_results['base_pay_monthly']), 
                      format_currency(mil_results['bah_monthly']),
                      format_currency(mil_results['bas_monthly'])],
                textposition='auto',
            )
        ])
        mil_chart.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis_title="Monthly $",
            showlegend=False
        )
        st.plotly_chart(mil_chart, use_container_width=True)

with col_chart2:
    with st.container(border=True):
        st.markdown("#### Civilian Breakdown")
        civ_base_monthly = base_salary / 12
        civ_bonus_monthly = civ_results['bonus_net'] / 12
        civ_rsu_monthly = civ_results.get('rsu_net', 0) / 12
        
        civ_chart = go.Figure(data=[
            go.Bar(
                x=['Base', 'Bonus', 'RSU'],
                y=[civ_base_monthly, civ_bonus_monthly, civ_rsu_monthly],
                marker_color=['#3b82f6', '#8b5cf6', '#ec4899'],
                text=[format_currency(civ_base_monthly), 
                      format_currency(civ_bonus_monthly),
                      format_currency(civ_rsu_monthly)],
                textposition='auto',
            )
        ])
        civ_chart.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis_title="Monthly $ (After Tax)",
            showlegend=False
        )
        st.plotly_chart(civ_chart, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Mobile-optimized: Use tabs instead of 3 columns
with st.container(border=True):
    tab_delta, tab_4yr = st.tabs(["Monthly Delta", "4-Year Total"])

with tab_delta:
    winner = "Military" if delta > 0 else "Civilian"
    st.metric(
        "Monthly Delta",
        format_delta(delta),
        help=f"{winner} Advantage"
    )
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.write(f"**Military Monthly:** {format_currency(mil_results['total_monthly'])}")
    with col_m2:
        st.write(f"**Civilian Monthly (After Tax):** {format_currency(civ_results['net_monthly'])}")

with tab_4yr:
    st.metric(
        "4-Year Upside",
        format_delta(four_year_delta),
        help="Cumulative Wealth Difference"
    )
    
    col_4y1, col_4y2 = st.columns(2)
    with col_4y1:
        st.markdown(f"### Military 4-Year Total")
        st.markdown(f"## {format_currency(mil_4yr_total)}")
    with col_4y2:
        st.markdown(f"### Civilian 4-Year Total")
        st.markdown(f"## {format_currency(civ_4yr_total)}")

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("4-Year Wealth Projection")
    st.caption("Visualizing the 1-Year Cliff Trap")

    if total_equity > 0:
        equity_calc = calculate_rsu_value(total_equity, vesting_years, 0, is_public)
        vesting_schedule_detail = calculate_vesting_schedule(total_equity, vesting_years, 12, is_public)
        
        cumulative_equity = {}
        cumulative = 0
        for year in range(5):
            if year == 0:
                cumulative_equity[year] = 0
            else:
                cumulative += vesting_schedule_detail.get(year, {}).get('vested_this_year', 0)
                cumulative_equity[year] = cumulative
    else:
        cumulative_equity = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

    tsp_match = mil_results['base_pay_monthly'] * 0.05 * 12

    wealth_fig = render_wealth_chart(
        mil_annual_net=mil_results['total_monthly'] * 12,
        civ_annual_net=civ_results['net_monthly'] * 12,
        equity_vesting_schedule=cumulative_equity,
        tsp_match_annual=tsp_match
    )

    st.plotly_chart(wealth_fig, use_container_width=True)

with st.container(border=True):
    col_4yr1, col_4yr2 = st.columns(2)
    with col_4yr1:
        mil_4yr = mil_results['total_monthly'] * 48 + (tsp_match * 4)
        st.metric("Military 4-Year Total", format_currency(mil_4yr))
    with col_4yr2:
        civ_4yr = civ_results['net_monthly'] * 48 + cumulative_equity.get(4, 0)
        st.metric("Civilian 4-Year Total", format_currency(civ_4yr))

if cumulative_equity.get(1, 0) == 0 and total_equity > 0:
    st.warning("**1-Year Cliff Alert**: No equity vests in Year 1. You're working the first year for base compensation only!")

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("About the Tax Advantage"):
    st.markdown("""
    ### Why Military Pay Goes Further
    
    Military compensation includes **tax-advantaged allowances** that don't count as taxable income:
    
    - **BAH (Basic Allowance for Housing)**: Tax-free housing allowance based on location and rank
    - **BAS (Basic Allowance for Subsistence)**: Tax-free food allowance
    
    **Example:** An E-6 with $40,000 base pay + $20,000 BAH is only taxed on the $40,000, 
    while a civilian making $60,000 is taxed on the full amount.
    
    This tool calculates the **true economic value** of keeping these tax advantages.
    """)


st.sidebar.markdown("## Settings")
st.sidebar.markdown("**Version:** 3.0.0 (Sprint 3 - Pro UI)")
st.sidebar.markdown("**Status:** Professional Dashboard")
st.sidebar.markdown("---")

if st.sidebar.button("Share Scenario", use_container_width=True, type="primary"):
    if total_equity > 0:
        equity_calc_summary = calculate_rsu_value(total_equity, vesting_years, 0, is_public)
    else:
        equity_calc_summary = {'adjusted_value': 0, 'annualized_value': 0, 'risk_discount': 0, 'liquidity_note': 'No equity'}
    
    exec_summary = generate_executive_summary(
        mil_results=mil_results,
        civ_results=civ_results,
        equity_calc=equity_calc_summary,
        rank=rank,
        base_salary=base_salary,
        total_equity=total_equity
    )
    
    st.sidebar.markdown("### Executive Summary")
    st.sidebar.markdown(exec_summary)
    st.sidebar.markdown("---")
    st.sidebar.info("Copy the text above to share with advisors, family, or forums.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Roadmap")
st.sidebar.markdown("- Sprint 1: Core Logic")
st.sidebar.markdown("- Sprint 2: AI Parser + Equity")
st.sidebar.markdown("- Sprint 3: Wealth Horizon")
st.sidebar.markdown("- Sprint 4: Smart BAH Lookup")
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Coverage")
st.sidebar.markdown("**BAH Bases:** 15 locations")
st.sidebar.markdown("- 6 Army bases")
st.sidebar.markdown("- 5 Navy bases")
st.sidebar.markdown("- 4 Air Force bases")
st.sidebar.markdown("- 2 Marine bases")
