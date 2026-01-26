import plotly.graph_objects as go
from typing import Dict, List
from utils.design_system import get_chart_colors, get_chart_layout_defaults, COLORS


def render_wealth_chart(
    mil_annual_net: float,
    civ_annual_net: float,
    equity_vesting_schedule: Dict[int, float],
    tsp_match_annual: float = 0
) -> go.Figure:
    """
    Creates a 4-year wealth accumulation chart comparing military vs. civilian paths.
    Visualizes the "1-year cliff trap" where equity doesn't vest until Year 2.

    Args:
        mil_annual_net: Annual net military compensation
        civ_annual_net: Annual net civilian compensation (without equity)
        equity_vesting_schedule: Dict mapping year -> cumulative vested equity
        tsp_match_annual: Annual TSP matching contribution (default 0)

    Returns:
        Plotly figure object showing 4-year wealth comparison
    """
    chart_colors = get_chart_colors()
    layout_defaults = get_chart_layout_defaults()

    years = [0, 1, 2, 3, 4]

    mil_cumulative = []
    civ_cumulative = []

    for year in years:
        mil_wealth = (mil_annual_net * year) + (tsp_match_annual * year)
        mil_cumulative.append(mil_wealth)

        civ_base_wealth = civ_annual_net * year

        equity_vested = equity_vesting_schedule.get(year, 0)

        civ_total_wealth = civ_base_wealth + equity_vested
        civ_cumulative.append(civ_total_wealth)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years,
        y=mil_cumulative,
        mode='lines+markers',
        name='Military Path',
        line=dict(color=chart_colors['military'], width=3),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Year %{x}</b><br>Cumulative: $%{y:,.0f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=years,
        y=civ_cumulative,
        mode='lines+markers',
        name='Civilian Path',
        line=dict(color=chart_colors['civilian'], width=3),
        marker=dict(size=10, symbol='square'),
        hovertemplate='<b>Year %{x}</b><br>Cumulative: $%{y:,.0f}<extra></extra>'
    ))

    for year in [1, 2, 3, 4]:
        if year in equity_vesting_schedule and equity_vesting_schedule[year] > equity_vesting_schedule.get(year - 1, 0):
            vested_this_year = equity_vesting_schedule[year] - equity_vesting_schedule.get(year - 1, 0)
            fig.add_annotation(
                x=year,
                y=civ_cumulative[year],
                text=f"${vested_this_year:,.0f}<br>vests",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=chart_colors['equity'],
                ax=30,
                ay=-40,
                font=dict(size=10, color=chart_colors['equity'])
            )

    fig.update_layout(
        title={
            'text': "4-Year Wealth Accumulation: Military vs. Civilian",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': chart_colors['text']}
        },
        xaxis_title="Year",
        yaxis_title="Cumulative Wealth ($)",
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor=f"rgba(224, 229, 236, 0.9)"
        ),
        plot_bgcolor=chart_colors['background'],
        paper_bgcolor=chart_colors['background'],
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            gridcolor=chart_colors['grid'],
            linecolor=COLORS['shadow_dark']
        ),
        yaxis=dict(
            gridcolor=chart_colors['grid'],
            tickformat='$,.0f',
            linecolor=COLORS['shadow_dark']
        ),
        font=dict(
            family=layout_defaults['font']['family'],
            color=chart_colors['text']
        )
    )

    if civ_cumulative[1] == civ_cumulative[0] + (civ_annual_net * 1):
        fig.add_annotation(
            x=1,
            y=civ_cumulative[1],
            text="1-Year Cliff<br>No equity yet!",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=COLORS['error'],
            ax=-50,
            ay=-50,
            font=dict(size=12, color=COLORS['error'], family="Arial Black")
        )

    return fig


def render_breakeven_analysis(
    mil_monthly: float,
    civ_monthly: float,
    equity_annual: float
) -> go.Figure:
    """
    Creates a breakeven analysis chart showing when civilian offer overtakes military.

    Args:
        mil_monthly: Monthly military net pay
        civ_monthly: Monthly civilian net pay (without equity)
        equity_annual: Annual equity vesting value

    Returns:
        Plotly figure showing monthly comparison over 48 months
    """
    chart_colors = get_chart_colors()

    months = list(range(0, 49))

    mil_cumulative = [mil_monthly * month for month in months]
    civ_cumulative = []

    for month in months:
        year = month // 12
        civ_base = civ_monthly * month
        equity_vested = equity_annual * year
        civ_cumulative.append(civ_base + equity_vested)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=months,
        y=mil_cumulative,
        mode='lines',
        name='Military',
        line=dict(color=chart_colors['military'], width=2),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=civ_cumulative,
        mode='lines',
        name='Civilian',
        line=dict(color=chart_colors['civilian'], width=2),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))

    breakeven_month = None
    for month in months:
        if civ_cumulative[month] > mil_cumulative[month]:
            breakeven_month = month
            break

    if breakeven_month:
        fig.add_vline(
            x=breakeven_month,
            line_dash="dash",
            line_color=COLORS['error'],
            annotation_text=f"Breakeven: Month {breakeven_month}",
            annotation_position="top"
        )

    fig.update_layout(
        title="Break-Even Analysis: When Does Civilian Overtake Military?",
        xaxis_title="Month",
        yaxis_title="Cumulative Wealth ($)",
        hovermode='x unified',
        height=400,
        plot_bgcolor=chart_colors['background'],
        paper_bgcolor=chart_colors['background'],
        yaxis=dict(tickformat='$,.0f', gridcolor=chart_colors['grid']),
        xaxis=dict(gridcolor=chart_colors['grid']),
        showlegend=True
    )

    return fig


def generate_executive_summary(
    mil_results: Dict,
    civ_results: Dict,
    equity_calc: Dict,
    rank: str,
    base_salary: float,
    total_equity: float,
    location: str = "N/A"
) -> str:
    """
    Generates a professional executive summary for sharing with advisors or family.
    
    Args:
        mil_results: Military calculation results
        civ_results: Civilian calculation results
        equity_calc: Equity calculation results
        rank: Military rank
        base_salary: Civilian base salary
        total_equity: Total equity grant
        location: Base location or city
        
    Returns:
        Professional Markdown-formatted executive summary
    """
    mil_monthly = mil_results['total_monthly']
    civ_monthly = civ_results['net_monthly']
    delta = mil_monthly - civ_monthly
    
    winner = "Military" if delta > 0 else "Civilian Offer"
    delta_abs = abs(delta)
    
    tsp_match = mil_results['base_pay_monthly'] * 0.05 * 12 * 4
    four_year_mil = mil_monthly * 48 + tsp_match
    four_year_civ = civ_monthly * 48 + equity_calc.get('adjusted_value', 0)
    four_year_delta = abs(four_year_civ - four_year_mil)
    four_year_winner = "Civilian" if four_year_civ > four_year_mil else "Military"
    
    tax_burden = civ_results['total_tax']
    equity_value = equity_calc.get('adjusted_value', 0)
    
    summary = f"""
**CompMe Analysis: Executive Summary**

A ${base_salary:,.0f} civilian offer {"beats" if delta < 0 else "falls short of"} an {rank} military salary by **${delta_abs:,.0f}/month**, {"but requires" if delta < 0 else "while avoiding"} a **${tax_burden:,.0f} annual tax burden**.

**Monthly Comparison:**
- Military ({rank}): ${mil_monthly:,.0f}/month
- Civilian Offer: ${civ_monthly:,.0f}/month (after tax)
- **Winner: {winner}** (+${delta_abs:,.0f}/month)

**4-Year Wealth Projection:**
- Military Path: ${four_year_mil:,.0f} (includes 5% TSP match)
- Civilian Path: ${four_year_civ:,.0f} (includes equity vesting)
- **{four_year_winner} advantage:** ${four_year_delta:,.0f} over 4 years

**Key Financial Metrics:**
- Tax Efficiency: {(1 - civ_results['effective_tax_rate']) * 100:.1f}% (civilian after-tax retention)
- Equity Value (4-Year): ${equity_value:,.0f} (risk-adjusted)
- Tax Advantage (Military): ${mil_results['tax_advantage_monthly']:,.0f}/month from BAH/BAS

**Recommendation:**
{"The civilian offer provides significantly higher total compensation, but relies on equity performance." if delta < 0 and equity_value > 0 else "Consider long-term career goals, lifestyle preferences, and risk tolerance when making this decision."}

*Analysis generated by CompMe v3.0 | Verified 2025 data*
"""
    
    return summary.strip()


def generate_summary_text(
    mil_results: Dict,
    civ_results: Dict,
    equity_calc: Dict,
    rank: str,
    base_salary: float,
    total_equity: float
) -> str:
    """
    Generates a shareable text summary of the compensation comparison.
    Legacy format maintained for backward compatibility.
    
    Args:
        mil_results: Military calculation results
        civ_results: Civilian calculation results
        equity_calc: Equity calculation results
        rank: Military rank
        base_salary: Civilian base salary
        total_equity: Total equity grant
        
    Returns:
        Formatted text summary ready to copy-paste
    """
    mil_monthly = mil_results['total_monthly']
    civ_monthly = civ_results['net_monthly']
    delta = mil_monthly - civ_monthly
    
    winner = "Military" if delta > 0 else "Civilian"
    delta_abs = abs(delta)
    
    four_year_mil = mil_monthly * 48
    four_year_civ = civ_monthly * 48 + equity_calc.get('adjusted_value', 0)
    four_year_delta = four_year_civ - four_year_mil
    
    summary = f"""
═══════════════════════════════════════════════════════
COMPENSATION COMPARISON SUMMARY
═══════════════════════════════════════════════════════

MONTHLY BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Military ({rank})
   Base Pay:        ${mil_results['base_pay_monthly']:,.0f}
   BAH (Tax-Free):  ${mil_results['bah_monthly']:,.0f}
   BAS (Tax-Free):  ${mil_results['bas_monthly']:,.0f}
   Tax Advantage:   ${mil_results['tax_advantage_monthly']:,.0f}
   ─────────────────────────────────────
   Total Monthly:   ${mil_monthly:,.0f}

Civilian Offer
   Base Salary:     ${base_salary:,.0f}/year
   Monthly Net:     ${civ_monthly:,.0f}
   Annual Equity:   ${equity_calc.get('annualized_value', 0):,.0f}
   ─────────────────────────────────────
   Total Monthly:   ${civ_monthly:,.0f}

VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Monthly Winner:  {winner} (+${delta_abs:,.0f}/month)

4-Year Outlook:
   Military Path:   ${four_year_mil:,.0f}
   Civilian Path:   ${four_year_civ:,.0f}
   ─────────────────────────────────────
   Net Difference:  ${'+' if four_year_delta > 0 else ''}{four_year_delta:,.0f}

{'Private Equity Warning: ' + equity_calc['liquidity_note'] if equity_calc.get('risk_discount', 0) > 0 else ''}

KEY INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Tax Advantage: ${mil_results['tax_advantage_monthly']:,.0f}/month saved by tax-free allowances
• Effective Tax Rate (Civilian): {civ_results['effective_tax_rate']*100:.1f}%
• Equity Risk Discount: {equity_calc.get('risk_discount', 0):.0f}% applied

═══════════════════════════════════════════════════════
Generated by CompMe v2.0 | compme-tool.com
═══════════════════════════════════════════════════════
"""
    
    return summary.strip()
