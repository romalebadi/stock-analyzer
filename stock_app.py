import streamlit as st
import pandas as pd
import ollama
from stock_fetcher import fetch_and_export

st.set_page_config(page_title="SEC Stock Analyzer", page_icon="📈", layout="wide")

st.title("📈 SEC Financial Analyzer")
st.caption("Pulls real SEC filings and generates an AI buy/sell recommendation")

# ── Ticker Input ──────────────────────────────────────────────────
ticker = st.text_input("Enter a stock ticker", placeholder="e.g. AAPL, GME, MSFT").upper()

if ticker:
    with st.spinner(f"Fetching SEC data for {ticker}..."):
        df = fetch_and_export(ticker)

    if df is None or df.empty:
        st.error(f"Could not find SEC data for {ticker}. Try another ticker.")
        st.stop()

    st.success(f"✅ Loaded {len(df)} quarters of data for {ticker}")

    # ── Charts ────────────────────────────────────────────────────
    st.subheader("📊 Financial Trends")

    col1, col2, col3 = st.columns(3)

    with col1:
        if "Revenue" in df.columns:
            st.markdown("**Revenue**")
            st.line_chart(df.set_index("Date")["Revenue"])

    with col2:
        if "NetIncome" in df.columns:
            st.markdown("**Net Income**")
            st.line_chart(df.set_index("Date")["NetIncome"])

    with col3:
        if "FreeCashFlow" in df.columns:
            st.markdown("**Free Cash Flow**")
            st.line_chart(df.set_index("Date")["FreeCashFlow"])

    col4, col5, col6 = st.columns(3)

    with col4:
        if "GrossProfit" in df.columns:
            st.markdown("**Gross Profit**")
            st.line_chart(df.set_index("Date")["GrossProfit"])

    with col5:
        if "TotalAssets" in df.columns and "TotalLiabilities" in df.columns:
            st.markdown("**Assets vs Liabilities**")
            st.line_chart(df.set_index("Date")[["TotalAssets", "TotalLiabilities"]])

    with col6:
        if "Cash" in df.columns:
            st.markdown("**Cash**")
            st.line_chart(df.set_index("Date")["Cash"])

    # ── Data Table ────────────────────────────────────────────────
    st.subheader("📋 Raw Financial Data")
    st.dataframe(df, use_container_width=True)

    # ── CSV Download ──────────────────────────────────────────────
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{ticker}_financials.csv",
        mime="text/csv"
    )

    # ── AI Analysis ───────────────────────────────────────────────
    st.subheader("🤖 AI Buy/Sell Analysis")

    if st.button("Run AI Analysis", type="primary"):
        with st.spinner("Llama 3.1 is analyzing the data... (30-60 seconds)"):

            data_str = df.to_string(index=False)

            prompt = f"""
You are a financial analyst. Below is {ticker}'s quarterly financial data pulled from SEC filings.

{data_str}

Based on this data, please provide:
1. A brief trend analysis (revenue, income, cash flow, debt)
2. Key strengths and red flags
3. A clear BUY, HOLD, or SELL recommendation with reasoning

Be concise and direct. Format your response with clear sections.
"""
            response = ollama.chat(
                model="llama3.1",
                messages=[{"role": "user", "content": prompt}]
            )

            result = response["message"]["content"]

            # Show verdict badge
            if "BUY" in result.upper():
                st.success("🟢 AI Verdict: BUY")
            elif "SELL" in result.upper():
                st.error("🔴 AI Verdict: SELL")
            else:
                st.warning("🟡 AI Verdict: HOLD")

            st.markdown(result)