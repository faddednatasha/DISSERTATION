# Geopolitical Events Database
# Sourced from dissertation Chapter 5 + additional global events

GEOPOLITICAL_EVENTS = [
    # --- From Dissertation Chapter 5 ---
    {
        "date": "2022-02-24",
        "event": "Russia-Ukraine War Begins",
        "category": "War/Conflict",
        "region": "Europe",
        "severity": "High",
        "description": "Russia launches full-scale invasion of Ukraine. Global commodity shock, crude oil spike above $100/bbl."
    },
    {
        "date": "2025-02-01",
        "event": "Union Budget 2026 STT Shock",
        "category": "Policy Shock",
        "region": "India",
        "severity": "High",
        "description": "Securities Transaction Tax hike announced in Union Budget 2026, causing sharp FII outflows."
    },
    {
        "date": "2025-02-15",
        "event": "Russia-Ukraine Phase II Escalation",
        "category": "War/Conflict",
        "region": "Europe",
        "severity": "High",
        "description": "Major escalation in Russia-Ukraine conflict. India's energy import costs surge."
    },
    {
        "date": "2025-05-07",
        "event": "Operation Sindoor — India-Pakistan",
        "category": "War/Conflict",
        "region": "South Asia",
        "severity": "High",
        "description": "India launches Operation Sindoor military strikes. NIFTY 50 drops sharply on opening; DII buying cushions fall."
    },
    {
        "date": "2025-06-15",
        "event": "USA-Iran / Iran-Israel Escalation",
        "category": "War/Conflict",
        "region": "Middle East",
        "severity": "Medium",
        "description": "Rising US-Iran tensions and Iran-Israel exchanges trigger crude oil spike and global risk-off."
    },
    {
        "date": "2025-07-10",
        "event": "US-China Tariff War Escalation",
        "category": "Trade War",
        "region": "Global",
        "severity": "Medium",
        "description": "US announces new tariff rounds on Chinese tech goods. Indian IT and electronics sectors impacted."
    },

    # --- Historical Major Events ---
    {
        "date": "2001-09-11",
        "event": "9/11 Terror Attacks",
        "category": "Terror Attack",
        "region": "Global",
        "severity": "High",
        "description": "US terror attacks cause global market panic. Indian markets suspended, then crashed on reopening."
    },
    {
        "date": "2003-03-20",
        "event": "US Invasion of Iraq",
        "category": "War/Conflict",
        "region": "Middle East",
        "severity": "Medium",
        "description": "US-led coalition invades Iraq. Crude oil volatility spikes."
    },
    {
        "date": "2008-09-15",
        "event": "Lehman Brothers Collapse",
        "category": "Financial Crisis",
        "region": "Global",
        "severity": "High",
        "description": "Lehman Brothers files for bankruptcy. Global financial crisis begins. NIFTY 50 loses ~60% peak to trough."
    },
    {
        "date": "2011-08-05",
        "event": "US Credit Rating Downgrade",
        "category": "Policy Shock",
        "region": "Global",
        "severity": "Medium",
        "description": "S&P downgrades US sovereign credit rating. Global equity selloff including Indian markets."
    },
    {
        "date": "2013-05-22",
        "event": "Fed Taper Tantrum",
        "category": "Policy Shock",
        "region": "Global",
        "severity": "Medium",
        "description": "Fed signals tapering of QE. Massive FII outflows from emerging markets including India."
    },
    {
        "date": "2016-11-08",
        "event": "Demonetisation — India",
        "category": "Policy Shock",
        "region": "India",
        "severity": "High",
        "description": "India announces sudden demonetisation of ₹500 and ₹1000 notes. Markets crash on liquidity fears."
    },
    {
        "date": "2016-11-09",
        "event": "Trump Election Victory",
        "category": "Political Event",
        "region": "Global",
        "severity": "Medium",
        "description": "Donald Trump wins US Presidential election. Initial global volatility followed by rally."
    },
    {
        "date": "2019-02-26",
        "event": "Balakot Airstrikes — India-Pakistan",
        "category": "War/Conflict",
        "region": "South Asia",
        "severity": "Medium",
        "description": "India conducts airstrikes in Balakot, Pakistan. Brief market panic followed by recovery."
    },
    {
        "date": "2020-01-30",
        "event": "COVID-19 Global Emergency",
        "category": "Pandemic",
        "region": "Global",
        "severity": "High",
        "description": "WHO declares COVID-19 a Public Health Emergency. Indian markets begin historic crash."
    },
    {
        "date": "2020-03-23",
        "event": "India COVID Lockdown",
        "category": "Pandemic",
        "region": "India",
        "severity": "High",
        "description": "India announces 21-day national lockdown. NIFTY 50 hits multi-year lows."
    },
    {
        "date": "2022-05-04",
        "event": "Fed Aggressive Rate Hike Cycle",
        "category": "Policy Shock",
        "region": "Global",
        "severity": "Medium",
        "description": "US Fed raises rates 50bps — start of aggressive hiking cycle. FII outflows accelerate from India."
    },
    {
        "date": "2023-03-10",
        "event": "Silicon Valley Bank Collapse",
        "category": "Financial Crisis",
        "region": "Global",
        "severity": "Medium",
        "description": "SVB collapses in largest US bank failure since 2008. Brief global banking sector panic."
    },
    {
        "date": "2023-10-07",
        "event": "Hamas Attack on Israel",
        "category": "War/Conflict",
        "region": "Middle East",
        "severity": "Medium",
        "description": "Hamas launches large-scale attack on Israel. Middle East conflict risk premium rises, crude oil spikes."
    },
    {
        "date": "2024-04-19",
        "event": "Iran Direct Attack on Israel",
        "category": "War/Conflict",
        "region": "Middle East",
        "severity": "High",
        "description": "Iran launches direct drone and missile attack on Israel — first ever. Global risk-off, Indian markets gap down."
    },
]

CATEGORIES = sorted(list(set(e["category"] for e in GEOPOLITICAL_EVENTS)))
REGIONS = sorted(list(set(e["region"] for e in GEOPOLITICAL_EVENTS)))
SEVERITIES = ["High", "Medium", "Low"]

CATEGORY_COLORS = {
    "War/Conflict":    "#e74c3c",
    "Policy Shock":    "#e67e22",
    "Financial Crisis":"#8e44ad",
    "Trade War":       "#2980b9",
    "Terror Attack":   "#c0392b",
    "Political Event": "#27ae60",
    "Pandemic":        "#1abc9c",
}
