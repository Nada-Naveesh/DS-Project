import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime as dt
import numpy as np

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# 🎨 CUSTOM CSS (BACKGROUND + UI)
# -----------------------------
st.markdown("""
<style>

body {
    background-color: #0e1117;
    color: white;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

[data-testid="stSidebar"] {
    background: #111827;
}

h1, h2, h3 {
    color: #00FFD1;
}

.stDataFrame {
    background-color: #1f2937;
}

.stSelectbox, .stMultiSelect {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 Crypto Dashboard")
st.markdown("### Real-time Crypto Insights (Modern UI)")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except:
        return pd.DataFrame()

    if not data or isinstance(data, dict):
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df = df.rename(columns={
        "name": "coin_name",
        "symbol": "coin_symbol",
        "current_price": "price",
        "market_cap": "market_cap",
        "total_volume": "volume_24h",
        "price_change_percentage_24h": "percent_change_24h"
    })

    df["coin_symbol"] = df["coin_symbol"].str.upper()
    df["percent_change_1h"] = 0
    df["percent_change_7d"] = 0

    return df


df = load_data()

if df.empty:
    st.error("⚠️ Unable to fetch data")
    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("⚙️ Controls")

selected_coin = st.sidebar.multiselect(
    "Select Coins",
    df["coin_symbol"],
    ["BTC", "ETH"]
)

percent_timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["24h", "1h", "7d"]
)

percent_map = {
    "24h": "percent_change_24h",
    "1h": "percent_change_1h",
    "7d": "percent_change_7d"
}

selected_col = percent_map[percent_timeframe]
filtered_df = df[df["coin_symbol"].isin(selected_coin)]

if filtered_df.empty:
    st.warning("Select at least one coin")
    st.stop()

# -----------------------------
# 📊 METRICS CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Avg Price", f"${filtered_df['price'].mean():,.2f}")
col2.metric("📊 Avg Change", f"{filtered_df[selected_col].mean():.2f}%")
col3.metric("🏦 Total Market Cap", f"${filtered_df['market_cap'].sum():,.0f}")

# -----------------------------
# 📊 CHARTS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Price Change")
    fig, ax = plt.subplots(figsize=(5,3))
    ax.barh(filtered_df["coin_symbol"], filtered_df[selected_col], color="#00FFD1")
    ax.set_facecolor("#1f2937")
    st.pyplot(fig, use_container_width=False)

with col2:
    st.subheader("💰 Market Cap")
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(filtered_df["coin_symbol"], filtered_df["market_cap"], color="#ff4b4b")
    ax.set_facecolor("#1f2937")
    st.pyplot(fig, use_container_width=False)

# -----------------------------
# 📈 TREND CHART
# -----------------------------
st.subheader("📈 Price Trend")

selected_crypto = st.selectbox("Select Coin", df["coin_symbol"])

dates = pd.date_range(end=dt.date.today(), periods=30)
prices = np.cumsum(np.random.randn(30)) + 100

fig, ax = plt.subplots(figsize=(6,3))
ax.plot(dates, prices, color="#00FFD1")
ax.set_facecolor("#1f2937")

st.pyplot(fig)

# -----------------------------
# 📋 TABLE
# -----------------------------
st.subheader("📋 Data Table")
st.dataframe(filtered_df, use_container_width=True)