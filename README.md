# 📉 Geopolitical Shock & Volatility Analyzer
### Indian Stock Market — Interactive Streamlit App

Inspired by the MBA Dissertation:
**"Time-Series Analysis of Market Liquidity and Volatility Clusters: An Econometric Investigation of the Indian Stock Market"**
— Aayushi Tewari, UPEs, 2026

---

## 🚀 Quick Start

### 1. Clone / Download the project
```bash
cd geopolitical_volatility_app
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app will open at **

---

## 📦 Project Structure

```
geopolitical_volatility_app/
│
├── app.py                  # Main Streamlit application
├── events_data.py          # Geopolitical events database (20+ events)
├── volatility_models.py    # GARCH, TARCH, Rolling Vol functions
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔧 Features

| Tab | What It Shows |
|---|---|
| 📈 Price & Events | Index price chart with geopolitical event markers overlaid |
| 🌊 Volatility Analysis | Rolling Std Dev vs GARCH(1,1) vs TARCH(1,1) comparison |
| 🔍 Event Impact Deep-Dive | Pre/post event returns & volatility change for each event |
| 📋 Model Parameters | GARCH & TARCH fitted coefficients with interpretation |

### Sidebar Controls
- Select index: NIFTY 50, BSE SENSEX, NIFTY Bank
- Date range picker (data from 2000 onwards)
- Filter events by category, region, severity
- Toggle GARCH / TARCH models
- Adjust rolling window and event impact window

---

## 🌍 Geopolitical Events Included

- 9/11 Terror Attacks (2001)
- US Invasion of Iraq (2003)
- Lehman Brothers Collapse (2008)
- Fed Taper Tantrum (2013)
- Demonetisation — India (2016)
- COVID-19 Global Emergency (2020)
- Russia-Ukraine War (2022, 2025)
- Operation Sindoor — India-Pakistan (2025)
- USA-Iran / Iran-Israel Escalation (2025)
- US-China Tariff War (2025)
- Union Budget 2026 STT Shock
- ...and more

---

## 📊 Volatility Models

### Rolling Standard Deviation
Simple historical volatility using a configurable rolling window (default 21 days = 1 month). Annualised × √252.

### GARCH(1,1) — Symmetric
Standard GARCH model. Assumes positive and negative shocks affect volatility equally. Good baseline.

### TARCH(1,1) — Asymmetric (GJR-GARCH)
Captures the **leverage effect** — negative shocks amplify volatility more than positive shocks.
The dissertation found γ = 0.1284 (p<0.001) on NIFTY 50, confirming bad news amplifies vol ~2.44× more.

---

## 🚢 Deploy to Streamlit Cloud (Free)

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Click **Deploy** — live URL in ~2 minutes!

---

## 💼 Freelance Use Cases

- Show this to fintech startups as a portfolio piece
- Offer custom versions for brokerages (add more indices, custom events)
- Extend with portfolio stress testing for wealth managers
- Add EPU index feed for macro research firms

---

## 🔮 Extend This App

Ideas to add next:
- [ ] EPU (Economic Policy Uncertainty) index overlay
- [ ] FII vs DII flow data
- [ ] Multi-index comparison (NIFTY vs S&P 500 vs DAX)
- [ ] PDF report export per event
- [ ] Live news feed integration via NewsAPI
- [ ] ML classifier — predict post-event direction

---

*Built with Python · Streamlit · yfinance · ARCH · Plotly*
