import pandas as pd
import numpy as np

def safe_growth(series):
    """Calculate average QoQ growth rate from a series"""
    series = series.dropna()
    if len(series) < 2:
        return None
    growths = []
    for i in range(1, len(series)):
        prev = series.iloc[i-1]
        curr = series.iloc[i]
        if prev != 0 and prev is not None:
            growths.append((curr - prev) / abs(prev))
    return np.mean(growths) if growths else None

def score_trend(series, higher_is_better=True):
    """Score a metric 0-10 based on level and trend"""
    series = series.dropna()
    if len(series) < 2:
        return 5.0  # Neutral if not enough data

    latest    = series.iloc[-1]
    growth    = safe_growth(series)
    positive  = latest > 0

    score = 5.0  # Start neutral

    # Level component
    if higher_is_better:
        if positive:
            score += 2
        else:
            score -= 2
    else:
        if not positive:
            score += 2
        else:
            score -= 2

    # Trend component
    if growth is not None:
        if higher_is_better:
            if growth > 0.10:
                score += 3
            elif growth > 0.05:
                score += 2
            elif growth > 0:
                score += 1
            elif growth > -0.05:
                score -= 1
            else:
                score -= 2
        else:
            if growth < -0.10:
                score += 3
            elif growth < -0.05:
                score += 2
            elif growth < 0:
                score += 1
            elif growth < 0.05:
                score -= 1
            else:
                score -= 2

    return max(0, min(10, score))

def score_margin(series, higher_is_better=True):
    """Score a margin metric 0-10"""
    series = series.dropna()
    if len(series) < 2:
        return 5.0

    latest = series.iloc[-1]
    trend  = safe_growth(series)
    score  = 5.0

    # Level component — gross margin benchmarks
    if latest > 0.5:
        score += 3
    elif latest > 0.3:
        score += 2
    elif latest > 0.1:
        score += 1
    elif latest > 0:
        score += 0
    else:
        score -= 2

    # Trend component
    if trend is not None:
        if trend > 0.02:
            score += 2
        elif trend > 0:
            score += 1
        elif trend > -0.02:
            score -= 1
        else:
            score -= 2

    return max(0, min(10, score))

def calculate_scores(df):
    """Calculate all metric scores and return a results dict"""
    scores   = {}
    details  = {}
    last4    = df.tail(4)

    # ── Helper: get column safely ─────────────────────────────────
    def col(name):
        if name in df.columns:
            return last4[name]
        return pd.Series(dtype=float)

    # ── 1. ROE / ROIC (20%) ───────────────────────────────────────
    if "NetIncome" in df.columns and "TotalEquity" in df.columns:
        roe_series = last4["NetIncome"] / last4["TotalEquity"].replace(0, np.nan)
        roe_score  = score_trend(roe_series)
        latest_roe = roe_series.dropna().iloc[-1] if not roe_series.dropna().empty else None
        scores["ROE"]   = roe_score
        details["ROE"]  = f"{latest_roe*100:.1f}%" if latest_roe is not None else "N/A"
    else:
        scores["ROE"]   = 5.0
        details["ROE"]  = "N/A"

    # ── 2. Gross Margin (5%) ──────────────────────────────────────
    if "GrossProfit" in df.columns and "Revenue" in df.columns:
        gm_series = last4["GrossProfit"] / last4["Revenue"].replace(0, np.nan)
        gm_score  = score_margin(gm_series)
        latest_gm = gm_series.dropna().iloc[-1] if not gm_series.dropna().empty else None
        scores["GrossMargin"]  = gm_score
        details["GrossMargin"] = f"{latest_gm*100:.1f}%" if latest_gm is not None else "N/A"
    else:
        scores["GrossMargin"]  = 5.0
        details["GrossMargin"] = "N/A"

    # ── 3. Operating Income (5%) ──────────────────────────────────
    if "OperatingIncome" in df.columns:
        op_score = score_trend(col("OperatingIncome"))
        latest_op = col("OperatingIncome").dropna().iloc[-1] if not col("OperatingIncome").dropna().empty else None
        scores["OperatingIncome"]  = op_score
        details["OperatingIncome"] = f"${latest_op/1e9:.2f}B" if latest_op is not None else "N/A"
    else:
        scores["OperatingIncome"]  = 5.0
        details["OperatingIncome"] = "N/A"

    # ── 4. Net Income (5%) ────────────────────────────────────────
    if "NetIncome" in df.columns:
        ni_score  = score_trend(col("NetIncome"))
        latest_ni = col("NetIncome").dropna().iloc[-1] if not col("NetIncome").dropna().empty else None
        scores["NetIncome"]  = ni_score
        details["NetIncome"] = f"${latest_ni/1e9:.2f}B" if latest_ni is not None else "N/A"
    else:
        scores["NetIncome"]  = 5.0
        details["NetIncome"] = "N/A"

    # ── 5. EPS (5%) ───────────────────────────────────────────────
    if "EPS_Basic" in df.columns:
        eps_score  = score_trend(col("EPS_Basic"))
        latest_eps = col("EPS_Basic").dropna().iloc[-1] if not col("EPS_Basic").dropna().empty else None
        scores["EPS"]  = eps_score
        details["EPS"] = f"${latest_eps:.2f}" if latest_eps is not None else "N/A"
    else:
        scores["EPS"]  = 5.0
        details["EPS"] = "N/A"

    # ── 6. Free Cash Flow (10%) ───────────────────────────────────
    if "FreeCashFlow" in df.columns:
        fcf_score  = score_trend(col("FreeCashFlow"))
        latest_fcf = col("FreeCashFlow").dropna().iloc[-1] if not col("FreeCashFlow").dropna().empty else None
        # FCF Margin bonus
        if "Revenue" in df.columns and latest_fcf is not None:
            latest_rev = col("Revenue").dropna().iloc[-1] if not col("Revenue").dropna().empty else None
            if latest_rev and latest_rev != 0:
                fcf_margin = latest_fcf / latest_rev
                if fcf_margin > 0.15:
                    fcf_score = min(10, fcf_score + 1)
                elif fcf_margin < 0:
                    fcf_score = max(0, fcf_score - 1)
                details["FreeCashFlow"] = f"${latest_fcf/1e9:.2f}B (margin: {fcf_margin*100:.1f}%)"
            else:
                details["FreeCashFlow"] = f"${latest_fcf/1e9:.2f}B" if latest_fcf is not None else "N/A"
        else:
            details["FreeCashFlow"] = f"${latest_fcf/1e9:.2f}B" if latest_fcf is not None else "N/A"
        scores["FreeCashFlow"] = fcf_score
    else:
        scores["FreeCashFlow"]  = 5.0
        details["FreeCashFlow"] = "N/A"

    # ── 7. Operating Cash Flow (10%) ──────────────────────────────
    if "OperatingCashFlow" in df.columns:
        ocf_score  = score_trend(col("OperatingCashFlow"))
        latest_ocf = col("OperatingCashFlow").dropna().iloc[-1] if not col("OperatingCashFlow").dropna().empty else None
        scores["OperatingCashFlow"]  = ocf_score
        details["OperatingCashFlow"] = f"${latest_ocf/1e9:.2f}B" if latest_ocf is not None else "N/A"
    else:
        scores["OperatingCashFlow"]  = 5.0
        details["OperatingCashFlow"] = "N/A"

    # ── 8. Debt Metrics (10%) ─────────────────────────────────────
    if "LongTermDebt" in df.columns and "TotalEquity" in df.columns:
        de_series  = last4["LongTermDebt"] / last4["TotalEquity"].replace(0, np.nan)
        debt_score = score_trend(de_series, higher_is_better=False)
        latest_de  = de_series.dropna().iloc[-1] if not de_series.dropna().empty else None
        scores["Debt"]  = debt_score
        details["Debt"] = f"D/E: {latest_de:.2f}x" if latest_de is not None else "N/A"
    else:
        scores["Debt"]  = 5.0
        details["Debt"] = "N/A"

    # ── 9. Net Assets (10%) ───────────────────────────────────────
    if "TotalAssets" in df.columns and "TotalLiabilities" in df.columns:
        na_series  = last4["TotalAssets"] - last4["TotalLiabilities"]
        na_score   = score_trend(na_series)
        latest_na  = na_series.dropna().iloc[-1] if not na_series.dropna().empty else None
        scores["NetAssets"]  = na_score
        details["NetAssets"] = f"${latest_na/1e9:.2f}B" if latest_na is not None else "N/A"
    else:
        scores["NetAssets"]  = 5.0
        details["NetAssets"] = "N/A"

    # ── 10. Revenue Growth (15%) ──────────────────────────────────
    if "Revenue" in df.columns:
        rev_score  = score_trend(col("Revenue"))
        rev_growth = safe_growth(col("Revenue"))
        scores["RevenueGrowth"]  = rev_score
        details["RevenueGrowth"] = f"{rev_growth*100:.1f}% avg QoQ" if rev_growth is not None else "N/A"
    else:
        scores["RevenueGrowth"]  = 5.0
        details["RevenueGrowth"] = "N/A"

    # ── 11. Share Dilution bonus/penalty ─────────────────────────
    dilution_penalty = 0
    if "SharesBasic" in df.columns:
        shares_growth = safe_growth(col("SharesBasic"))
        if shares_growth is not None:
            if shares_growth > 0.03:
                dilution_penalty = -0.5
                details["ShareDilution"] = f"⚠️ Diluting +{shares_growth*100:.1f}% avg QoQ"
            elif shares_growth < 0:
                dilution_penalty = 0.3
                details["ShareDilution"] = f"✅ Buybacks {shares_growth*100:.1f}% avg QoQ"
            else:
                details["ShareDilution"] = f"Stable {shares_growth*100:.1f}% avg QoQ"

    # ── Weighted Final Score ──────────────────────────────────────
    weights = {
        "ROE":               0.20,
        "GrossMargin":       0.05,
        "OperatingIncome":   0.05,
        "NetIncome":         0.05,
        "EPS":               0.05,
        "FreeCashFlow":      0.10,
        "OperatingCashFlow": 0.10,
        "Debt":              0.10,
        "NetAssets":         0.10,
        "RevenueGrowth":     0.15,
    }

    weighted_score = sum(scores[k] * weights[k] for k in weights if k in scores)
    final_score    = max(0, min(10, weighted_score + dilution_penalty))

    # ── Verdict ───────────────────────────────────────────────────
    if final_score >= 7.5:
        verdict = "BUY"
        emoji   = "🟢"
    elif final_score >= 5.0:
        verdict = "HOLD"
        emoji   = "🟡"
    else:
        verdict = "SELL"
        emoji   = "🔴"

    return {
        "final_score": round(final_score, 1),
        "verdict":     verdict,
        "emoji":       emoji,
        "scores":      scores,
        "details":     details,
        "weights":     weights,
    }