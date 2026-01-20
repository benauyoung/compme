# CompMe - Developer Handoff Guide

Welcome to the CompMe project! This document will help you get up to speed quickly.

---

## 🎯 What is CompMe?

CompMe is a compensation comparison tool that helps military service members evaluate civilian job offers by accounting for the **tax advantage** of military allowances (BAH/BAS). It provides a transparent, side-by-side comparison of military vs. civilian take-home pay.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Basic understanding of Streamlit

### Setup Steps

```bash
# 1. Navigate to project directory
cd c:\Users\Benjamin\Desktop\Projects\CompMe

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run src/app.py

# 4. Open browser to http://localhost:8501
```

That's it! You should see the CompMe dashboard.

---

## 📁 Project Structure

```
CompMe/
├── src/
│   ├── app.py                      # Main Streamlit application (START HERE)
│   ├── engines/
│   │   ├── mil_engine.py           # Military compensation calculations
│   │   └── civ_engine.py           # Civilian compensation calculations
│   ├── data/
│   │   ├── bah_2025_mock.json      # BAH rates for top 5 bases
│   │   └── tax_brackets_mock.json  # Federal and state tax data
│   └── utils/
│       └── formatters.py           # Currency and percentage formatting
├── docs/
│   ├── project_overview.md         # High-level architecture and vision
│   ├── session_log.md              # Detailed changelog (READ THIS SECOND)
│   └── handoff_template.md         # This file
├── requirements.txt                # Python dependencies
├── README.md                       # Standard project README
├── .env.example                    # Environment variable template
└── .gitignore                      # Git ignore rules
```

---

## 🔑 Key Concepts

### The Tax Advantage

Military service members receive:
- **Base Pay** (taxable)
- **BAH** - Basic Allowance for Housing (NOT taxable)
- **BAS** - Basic Allowance for Subsistence (NOT taxable)

**Example**: An E-6 with:
- $40,000 base pay
- $20,000 BAH
- $5,000 BAS

Only pays taxes on the $40,000, while a civilian earning $65,000 pays taxes on the full amount.

### RMC Formula

```
RMC = Base Pay + BAH + BAS + Tax Advantage Value
```

The **Tax Advantage Value** is the amount of additional taxable income a civilian would need to match the military member's purchasing power after taxes.

---

## 🧩 Code Architecture

### Data Flow

```
User Input (Streamlit)
    ↓
app.py orchestrates
    ↓
    ├──→ mil_engine.calculate_rmc()
    │       ├── get_base_pay()
    │       ├── get_bah_rate()
    │       ├── get_bas_rate()
    │       └── calculate_tax_advantage()
    │
    └──→ civ_engine.calculate_civilian_net()
            ├── calculate_federal_tax()
            ├── calculate_state_tax()
            ├── calculate_fica_tax()
            └── calculate_bonus_withholding()
    ↓
Results displayed in UI
```

### Key Functions

#### Military Engine (`mil_engine.py`)

| Function | Purpose | Status |
|----------|---------|--------|
| `load_bah_data()` | Loads BAH rates from JSON | ✅ Implemented |
| `get_base_pay(rank, yos)` | Returns base pay for rank/years | ⏳ Placeholder |
| `get_bah_rate(zip, rank, deps)` | Returns BAH for location | ⏳ Placeholder |
| `get_bas_rate(rank)` | Returns BAS for rank | ⏳ Placeholder |
| `calculate_tax_advantage(...)` | Core differentiator | ⏳ Placeholder |
| `calculate_rmc(...)` | Main orchestrator | ⏳ Placeholder |

#### Civilian Engine (`civ_engine.py`)

| Function | Purpose | Status |
|----------|---------|--------|
| `load_tax_data()` | Loads tax brackets from JSON | ✅ Implemented |
| `calculate_federal_tax(...)` | Progressive bracket calc | ⏳ Placeholder |
| `calculate_state_tax(...)` | State-specific taxes | ⏳ Placeholder |
| `calculate_fica_tax(...)` | Social Security + Medicare | ⏳ Placeholder |
| `calculate_bonus_withholding(...)` | 22% supplemental rate | ⏳ Placeholder |
| `calculate_equity_vesting(...)` | 4-year vest schedule | ⏳ Placeholder |
| `calculate_civilian_net(...)` | Main orchestrator | ⏳ Placeholder |

---

## 📊 Data Sources

### Mock Data (Current)

**BAH Rates** (`bah_2025_mock.json`):
- 5 bases: Norfolk, San Diego, JBLM, Fort Hood, Fort Bragg
- Ranks: E-1 to O-6
- With/without dependents rates

**Tax Data** (`tax_brackets_mock.json`):
- Federal tax brackets (single/married filing status)
- FICA rates (Social Security + Medicare)
- 5 state tax rates: VA, CA, WA, TX, NC

### Future Data Sources (Sprint 2+)

- **BAH**: AI agent queries DFAS.mil for real-time rates
- **State Taxes**: SmartAsset API or similar
- **Base Pay Tables**: Scraped from official DoD sources

---

## 🏃 Sprint Status

### ✅ Sprint 1: Napkin Math MVP (Current)
- [x] Project scaffolding
- [x] UI skeleton
- [x] Mock data files
- [ ] RMC calculation logic
- [ ] Basic civilian tax logic
- [ ] End-to-end test with sample inputs

### ⏳ Sprint 2: Smart Data Layer
- [ ] AI agent for BAH lookup
- [ ] Real-time state tax API
- [ ] Dynamic data refresh

### ⏳ Sprint 3: Equity Engine
- [ ] 4-year vesting visualization
- [ ] Public vs. private stock toggle
- [ ] Bonus tax trap calculator

### ⏳ Sprint 4: AI Offer Scanner
- [ ] PDF upload capability
- [ ] Claude/OpenAI extraction
- [ ] Auto-populate civilian fields

---

## 🛠️ Development Workflow

### Making Changes

1. **Read the session log**: Check `docs/session_log.md` for recent changes
2. **Update the code**: Make your changes
3. **Test locally**: Run `streamlit run src/app.py` and verify
4. **Document your work**: Update `session_log.md` with:
   - Timestamp
   - Task description
   - Technical decisions
   - Any open questions

### Adding New Features

1. **Plan first**: Update `project_overview.md` if architecture changes
2. **Write docstrings**: Every function needs a docstring explaining the math
3. **Add tests**: (When we add pytest in future sprints)
4. **Update README**: If user-facing changes

### Code Style

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use type hints for function parameters and returns
- **Formatting**: Follow PEP 8 (consider using `black` formatter)
- **Comments**: Explain *why*, not *what*

---

## 🐛 Common Issues

### Issue: Streamlit won't start
**Solution**: Check Python version (`python --version`). Must be 3.10+.

### Issue: Missing dependencies
**Solution**: Run `pip install -r requirements.txt` again.

### Issue: Mock data not loading
**Solution**: Verify you're running from project root, not `src/` directory.

### Issue: UI shows $0 everywhere
**Solution**: This is expected! Engine functions are placeholders. See Sprint 1 tasks.

---

## 📝 Documentation Requirements

Every time you complete a significant task:

1. **Add a session log entry** in `docs/session_log.md`
2. **Update docstrings** for any new functions
3. **Update project_overview.md** if architecture changes

---

## 🎓 Learning Resources

### Streamlit
- Official Docs: https://docs.streamlit.io
- API Reference: https://docs.streamlit.io/library/api-reference

### Military Pay
- DFAS Pay Tables: https://www.dfas.mil/militarymembers/payentitlements/Pay-Tables/
- BAH Rates: https://www.defensetravel.dod.mil/site/bahCalc.cfm
- BAS Rates: https://www.dfas.mil/militarymembers/payentitlements/bas/

### Tax Calculations
- IRS Tax Brackets: https://www.irs.gov/filing/federal-income-tax-rates-and-brackets
- FICA Rates: https://www.ssa.gov/oact/cola/cbb.html

---

## 🆘 Getting Help

### Questions About the Code?
1. Check `docs/session_log.md` for context on recent changes
2. Check `docs/project_overview.md` for architecture decisions
3. Look for inline comments and docstrings in the code

### Questions About Military Pay?
- Review `docs/project_overview.md` → "The Tax Advantage" section
- Check the mock data files for sample values

### Questions About Next Steps?
- Check `docs/session_log.md` → "Next Steps" section
- Review Sprint roadmap in `docs/project_overview.md`

---

## ✅ Checklist: "Am I Ready?"

Before you start coding, make sure you can answer:

- [ ] I understand what RMC (Regular Military Compensation) is
- [ ] I know the difference between BAH and BAS
- [ ] I understand why military allowances are tax-advantaged
- [ ] I can run the Streamlit app locally
- [ ] I've read the session log and know what's been completed
- [ ] I know which Sprint we're currently in

If you checked all boxes, you're ready to contribute! 🚀

---

**Last Updated**: 2026-01-20  
**Maintainer**: Development Team  
**Questions?**: Check session_log.md or project_overview.md first!
