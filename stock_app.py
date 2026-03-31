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
    
    # Format numeric columns with $ and commas
    format_dict = {}
    for col in df.columns:
        if col not in ["Date", "Ticker", "EPS_Basic", "EPS_Diluted"]:
            if df[col].dtype in ["float64", "int64"]:
                format_dict[col] = "${:,.0f}"

    if "EPS_Basic" in df.columns:
        format_dict["EPS_Basic"] = "${:,.2f}"
    if "EPS_Diluted" in df.columns:
        format_dict["EPS_Diluted"] = "${:,.2f}"

    st.dataframe(df.style.format(format_dict, na_rep=""), use_container_width=True)

    # ── CSV Download ──────────────────────────────────────────────
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{ticker}_financials.csv",
        mime="text/csv"
    )

# ── Quantitative Score ────────────────────────────────────────
    st.subheader("📊 Quantitative Scoring Model")

    from scorer import calculate_scores
    result = calculate_scores(df)

    # Final score display
    col_score, col_verdict = st.columns([1, 2])
    with col_score:
        st.metric("Overall Score", f"{result['final_score']} / 10")
    with col_verdict:
        if result["verdict"] == "BUY":
            st.success(f"{result['emoji']} Quantitative Verdict: {result['verdict']}")
        elif result["verdict"] == "HOLD":
            st.warning(f"{result['emoji']} Quantitative Verdict: {result['verdict']}")
        else:
            st.error(f"{result['emoji']} Quantitative Verdict: {result['verdict']}")

    # Score breakdown table
    categories = {
        "⭐ Quality": ["ROE", "GrossMargin", "OperatingIncome", "NetIncome", "EPS"],
        "💰 Cash Flow": ["FreeCashFlow", "OperatingCashFlow"],
        "⚠️ Risk": ["Debt", "NetAssets"],
        "📈 Growth": ["RevenueGrowth"],
    }

    for cat, metrics in categories.items():
        st.markdown(f"**{cat}**")
        rows = []
        for m in metrics:
            if m in result["scores"]:
                score = result["scores"][m]
                detail = result["details"].get(m, "N/A")
                weight = int(result["weights"].get(m, 0) * 100)
                bar = "🟩" * int(score) + "⬜" * (10 - int(score))
                rows.append({
                    "Metric": m,
                    "Score": f"{score:.1f}/10",
                    "Weight": f"{weight}%",
                    "Latest Value": detail,
                    "Visual": bar
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Share dilution note
    if "ShareDilution" in result["details"]:
        st.caption(f"Share Dilution: {result['details']['ShareDilution']}")

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