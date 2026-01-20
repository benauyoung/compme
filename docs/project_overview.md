# CompMe - Project Overview

## Vision Statement

**CompMe** is a plug-and-play compensation analysis tool designed to help military service members make informed career transition decisions by comparing the **true economic value** of military compensation against civilian job offers.

### The Problem

Military compensation is fundamentally different from civilian pay:

- **Military**: Base Pay + Tax-Free Allowances (BAH, BAS) + Benefits
- **Civilian**: Fully Taxable Salary + Bonus + Equity + Benefits

Service members often undervalue their military compensation because they don't account for the **Tax Advantage**—the reality that allowances like BAH and BAS are not subject to federal or state income tax. A dollar of military pay goes further than a dollar of civilian pay.

### The Solution

CompMe provides a transparent, side-by-side comparison that:

1. **Calculates True Military Value**: Uses the RMC (Regular Military Compensation) formula to show the real purchasing power of military pay
2. **Adjusts for Tax Reality**: Applies federal, state, and FICA taxes to civilian offers to show actual take-home pay
3. **Demystifies Equity**: Breaks down vesting schedules and liquidity constraints for RSU/stock grants
4. **Reveals the Delta**: Shows the monthly spending power difference in clear, actionable terms

### Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Dashboard                      │
│                          (app.py)                            │
└──────────────────┬──────────────────────┬───────────────────┘
                   │                      │
        ┌──────────▼──────────┐  ┌────────▼─────────┐
        │   Military Engine   │  │  Civilian Engine  │
        │   (mil_engine.py)   │  │  (civ_engine.py)  │
        └──────────┬──────────┘  └────────┬──────────┘
                   │                      │
        ┌──────────▼──────────────────────▼──────────┐
        │        Data Layer (JSON Mocks)              │
        │  • bah_2025_mock.json                       │
        │  • tax_brackets_mock.json                   │
        └─────────────────────────────────────────────┘
```

### Technical Philosophy

1. **Transparency Over Complexity**: Every calculation must be explainable and verifiable
2. **Speed to Market**: Streamlit enables rapid iteration without sacrificing UX
3. **Documentation First**: Code changes are logged, functions are documented, handoffs are seamless
4. **Modular Design**: Engines are isolated, data is centralized, UI is independent

### Sprint Roadmap

**Sprint 1 (Days 1-2)**: Napkin Math MVP
- Hardcoded RMC calculations
- Basic tax estimates (flat 25%)
- Working UI showing realistic numbers

**Sprint 2 (Days 3-4)**: Smart Data Layer
- AI agent for dynamic BAH lookup
- Real-time state tax API integration
- Accurate calculations for any location

**Sprint 3 (Days 5-6)**: Equity & Ambiguity Engine
- 4-year vesting schedule visualization
- Public vs. private stock liquidity toggle
- Bonus tax trap calculator

**Sprint 4 (Day 7+)**: AI Offer Scanner
- PDF upload for offer letters
- Claude/OpenAI extraction of salary/equity
- One-click auto-population

### Success Metrics

- **Accuracy**: Tax calculations within 2% of real-world results
- **Speed**: Page load < 2 seconds
- **Usability**: No training required—instant comprehension
- **Impact**: Service members can make data-driven career decisions

---

**Status**: Sprint 1 - Infrastructure Complete  
**Last Updated**: 2026-01-20  
**Maintainer**: Development Team
