# 💰 CompMe | Military-to-Civilian Compensation Analyzer

**CompMe V1.0** - The definitive financial modeling tool for service members evaluating civilian opportunities.

Reveals the "True Net" difference between Military Compensation (tax-advantaged) and Civilian Offers (taxable + equity). Solves the "Tax Trap" where a higher gross civilian salary can result in **lower** take-home pay.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)
![Status](https://img.shields.io/badge/Status-V1.0_Production-success.svg)

---

## 🚀 Key Features

### ✅ Official 2026 BAH Data
- **338 Duty Stations** with official DoD 2026 rates
- **All Ranks**: E-1 through O-6, including Warrant Officers
- **Searchable Dropdown**: Find your exact duty station instantly
- **No estimates, no guessing** - 100% real data

### 💰 True Net Compensation Engine
- Calculates **Regular Military Compensation (RMC)** with tax-free BAH/BAS
- Progressive Federal + State taxes for all 50 states + DC
- FICA (Social Security + Medicare) with wage base limits
- Shows exact civilian gross needed to match military net pay

### 📊 4-Year Wealth Projection
- **RSU Vesting Schedules** with 1-year cliff modeling
- **Risk Discounts** for private company equity (50% haircut)
- **Bonus Withholding** calculations (22% federal supplemental rate)
- Interactive Plotly charts showing cumulative wealth over time

### 🤖 AI Offer Letter Parser
- Paste raw offer text and auto-extract salary, bonus, equity
- Powered by GPT-4 via LangChain
- Supports multiple offer formats
- Pattern matching fallback for reliability

---

## 🏃 Quick Start (Local)

### Windows - One-Click Launch
```bash
# Double-click launch.bat
# OR run manually:
python -m streamlit run src/app.py
```

### Mac/Linux
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/compme.git
cd compme

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/app.py
```

App opens at `http://localhost:8502`

---

## 🌍 Cloud Deployment (Streamlit Cloud)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "V1.0 Official Release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/compme.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New App"** → Select `compme` repo
4. **CRITICAL**: Click **"Advanced Settings"** → **"Secrets"**
5. Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "sk-proj-..."
   ```
6. Click **"Deploy"**

**⚠️ NEVER commit your API key to the repo! Always use Streamlit Secrets.**

Your app will be live at: `https://YOUR_USERNAME-compme.streamlit.app`

---

## 📂 Project Structure

```
CompMe/
├── src/
│   ├── app.py                          # Main Streamlit dashboard
│   ├── engines/
│   │   ├── mil_engine.py               # RMC calculation
│   │   ├── civ_engine.py               # Tax + equity calculations
│   │   ├── bah_engine.py               # BAH lookup (2026 official data)
│   │   └── equity_engine.py            # RSU vesting + risk discounts
│   ├── ai/
│   │   └── parser.py                   # LLM offer letter extraction
│   ├── data/
│   │   ├── bah_2026_real.json          # Official 2026 BAH (338 locations)
│   │   ├── base_pay_2025.json          # DFAS pay tables
│   │   └── tax_brackets_mock.json      # 2025 tax brackets
│   └── utils/
│       ├── formatters.py               # Currency formatting
│       └── charts.py                   # Plotly visualizations
├── utils/
│   └── ingest_bah.py                   # Excel → JSON converter
├── requirements.txt                    # Python dependencies
├── launch.bat                          # Windows one-click launcher
├── .gitignore                          # Excludes .env, .venv, Excel files
└── README.md
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.10+
- **Data**: Pandas, official DoD Excel files → JSON
- **AI**: LangChain + OpenAI GPT-4
- **Charts**: Plotly interactive visualizations

---

## 🔑 Environment Variables

For local development, create a `.env` file:
```bash
OPENAI_API_KEY=sk-proj-...
```

**For cloud deployment**, use the Streamlit Cloud dashboard to set secrets. **NEVER commit `.env` to GitHub.**

---

## 📝 Version History

### V1.0 (Jan 2026) - Production Release
- ✅ Official 2026 BAH data (338 locations)
- ✅ All 50 states + DC tax calculations
- ✅ AI offer parser with GPT-4
- ✅ 4-year wealth projection charts
- ✅ Cloud deployment ready

---

## 📝 License

MIT

## 👨‍💻 Author

Built for service members making informed career decisions.

**Questions?** Open an issue or submit a PR!
