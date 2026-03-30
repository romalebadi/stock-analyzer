import requests
import pandas as pd

def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "sec-analyzer myemail@email.com"}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    for entry in data.values():
        if entry["ticker"].upper() == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)
            print(f"Found CIK for {ticker.upper()}: {cik}")
            return cik
    
    print(f"Ticker {ticker} not found.")
    return None

def get_financial_data(cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {"User-Agent": "sec-analyzer myemail@email.com"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get("facts", {}).get("us-gaap", {})

# ── Plain English label mapping ───────────────────────────────────
LABEL_MAP = {
    # Income Statement
    "Revenues":                                                      "Revenue",
    "RevenueFromContractWithCustomerExcludingAssessedTax":           "Revenue",
    "CostOfGoodsAndServicesSold":                                    "CostOfRevenue",
    "CostOfRevenue":                                                 "CostOfRevenue",
    "GrossProfit":                                                   "GrossProfit",
    "ResearchAndDevelopmentExpense":                                 "R&D_Expense",
    "SellingGeneralAndAdministrativeExpense":                        "SG&A_Expense",
    "OperatingExpenses":                                             "OperatingExpenses",
    "OperatingIncomeLoss":                                           "OperatingIncome",
    "InterestExpense":                                               "InterestExpense",
    "InterestIncomeExpenseNet":                                      "InterestIncomeNet",
    "NonoperatingIncomeExpense":                                     "NonOperatingIncome",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "PreTaxIncome",
    "IncomeTaxExpenseBenefit":                                       "IncomeTaxExpense",
    "NetIncomeLoss":                                                 "NetIncome",
    "EarningsPerShareBasic":                                         "EPS_Basic",
    "EarningsPerShareDiluted":                                       "EPS_Diluted",
    "WeightedAverageNumberOfSharesOutstandingBasic":                 "SharesBasic",
    "WeightedAverageNumberOfDilutedSharesOutstanding":               "SharesDiluted",
    "ComprehensiveIncomeNetOfTax":                                   "ComprehensiveIncome",

    # Balance Sheet — Assets
    "Assets":                                                        "TotalAssets",
    "AssetsCurrent":                                                 "CurrentAssets",
    "AssetsNoncurrent":                                              "NonCurrentAssets",
    "CashAndCashEquivalentsAtCarryingValue":                         "Cash",
    "CashAndCashEquivalents":                                        "Cash",
    "ShortTermInvestments":                                          "ShortTermInvestments",
    "CashCashEquivalentsAndShortTermInvestments":                    "CashAndShortTermInvestments",
    "AccountsReceivableNetCurrent":                                  "AccountsReceivable",
    "InventoryNet":                                                  "Inventory",
    "PrepaidExpenseAndOtherAssetsCurrent":                           "PrepaidAndOtherCurrentAssets",
    "PropertyPlantAndEquipmentNet":                                  "PP&E_Net",
    "Goodwill":                                                      "Goodwill",
    "IntangibleAssetsNetExcludingGoodwill":                          "IntangibleAssets",
    "OtherAssetsNoncurrent":                                         "OtherNonCurrentAssets",
    "OperatingLeaseRightOfUseAsset":                                 "OperatingLeaseAsset",

    # Balance Sheet — Liabilities
    "Liabilities":                                                   "TotalLiabilities",
    "LiabilitiesCurrent":                                            "CurrentLiabilities",
    "LiabilitiesNoncurrent":                                         "NonCurrentLiabilities",
    "AccountsPayableCurrent":                                        "AccountsPayable",
    "AccruedLiabilitiesCurrent":                                     "AccruedLiabilities",
    "DeferredRevenueCurrent":                                        "DeferredRevenueCurrent",
    "ShortTermBorrowings":                                           "ShortTermDebt",
    "DebtCurrent":                                                   "ShortTermDebt",
    "LongTermDebt":                                                  "LongTermDebt",
    "LongTermDebtNoncurrent":                                        "LongTermDebt",
    "DeferredTaxLiabilitiesNoncurrent":                              "DeferredTaxLiabilities",
    "OperatingLeaseLiabilityNoncurrent":                             "OperatingLeaseLiabilityLT",
    "OtherLiabilitiesNoncurrent":                                    "OtherNonCurrentLiabilities",

    # Balance Sheet — Equity
    "StockholdersEquity":                                            "TotalEquity",
    "StockholdersEquityAttributableToParent":                        "TotalEquity",
    "CommonStockValue":                                              "CommonStock",
    "AdditionalPaidInCapital":                                       "AdditionalPaidInCapital",
    "RetainedEarningsAccumulatedDeficit":                            "RetainedEarnings",
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax":               "AOCI",
    "TreasuryStockValue":                                            "TreasuryStock",
    "CommonStockSharesOutstanding":                                  "SharesOutstanding",

    # Cash Flow
    "NetCashProvidedByUsedInOperatingActivities":                    "OperatingCashFlow",
    "NetCashProvidedByUsedInInvestingActivities":                    "InvestingCashFlow",
    "NetCashProvidedByUsedInFinancingActivities":                    "FinancingCashFlow",
    "PaymentsToAcquirePropertyPlantAndEquipment":                    "CapEx",
    "DepreciationDepletionAndAmortization":                          "D&A",
    "ShareBasedCompensation":                                        "StockBasedComp",
    "PaymentsForRepurchaseOfCommonStock":                            "ShareBuybacks",
    "PaymentsOfDividends":                                           "DividendsPaid",
    "ProceedsFromIssuanceOfCommonStock":                             "StockIssuanceProceeds",
    "ProceedsFromIssuanceOfLongTermDebt":                            "DebtIssuanceProceeds",
    "RepaymentsOfLongTermDebt":                                      "DebtRepayments",
    "PaymentsToAcquireBusinessesNetOfCashAcquired":                  "Acquisitions",
    "PaymentsToAcquireInvestments":                                  "InvestmentPurchases",
    "ProceedsFromSaleOfInvestments":                                 "InvestmentSales",
    "IncreaseDecreaseInAccountsReceivable":                          "ChangeInAccountsReceivable",
    "IncreaseDecreaseInInventories":                                 "ChangeInInventory",
    "IncreaseDecreaseInAccountsPayable":                             "ChangeInAccountsPayable",
}

# ── Statement classification ──────────────────────────────────────
INCOME_KEYWORDS = [
    "Revenue", "Income", "Loss", "Expense", "Profit", "Earning",
    "Sales", "Cost", "Gross", "Operating", "Interest", "Tax",
    "Comprehensive", "PerShare", "Diluted", "Basic", "Shares",
    "Nonoperating", "Depreciation", "Amortization"
]

BALANCE_KEYWORDS = [
    "Asset", "Liabilit", "Equity", "Cash", "Receivable", "Inventory",
    "Payable", "Debt", "Goodwill", "Intangible", "Property", "Plant",
    "Equipment", "Lease", "Deferred", "Stock", "Capital", "Retained",
    "Treasury", "Prepaid", "Investment"
]

CASHFLOW_KEYWORDS = [
    "NetCashProvided", "NetCashUsed", "Payments", "Proceeds",
    "Purchase", "Acquisition", "Repayment", "Issuance", "Dividends",
    "Repurchase", "IncreaseDecrease"
]

def classify_tag(tag):
    for kw in CASHFLOW_KEYWORDS:
        if kw in tag:
            return "cashflow"
    for kw in BALANCE_KEYWORDS:
        if kw in tag:
            return "balance"
    for kw in INCOME_KEYWORDS:
        if kw in tag:
            return "income"
    return None

def is_balance_sheet(tag):
    return classify_tag(tag) == "balance"

def derive_quarterly(entries):
    """Derive true quarterly values from a mix of standalone and YTD entries"""
    from datetime import datetime, timedelta

    standalone = {}
    ytd        = {}
    annual     = {}

    for e in entries:
        end   = e["end"]
        start = e.get("start", "")
        form  = e.get("form", "")

        if start:
            try:
                start_dt  = datetime.strptime(start, "%Y-%m-%d")
                end_dt    = datetime.strptime(end,   "%Y-%m-%d")
                span_days = (end_dt - start_dt).days
            except:
                continue

            def keep_best(d, key):
                if key not in d:
                    d[key] = e
                else:
                    existing = d[key]
                    if form == "10-K" and existing.get("form") != "10-K":
                        d[key] = e
                    elif form == existing.get("form") and e.get("filed", "") > existing.get("filed", ""):
                        d[key] = e

            if span_days >= 350:
                keep_best(annual, end)
            elif 111 <= span_days <= 349:
                keep_best(ytd, end)
            elif 70 <= span_days <= 110:
                keep_best(standalone, end)

        else:
            # No start date — classify by form type only
            # 10-K = annual, 10-Q = treat as standalone quarterly
            def keep_best_no_start(d, key):
                if key not in d:
                    d[key] = e
                elif e.get("filed", "") > d[key].get("filed", ""):
                    d[key] = e

            if form == "10-K":
                keep_best_no_start(annual, end)
            elif form == "10-Q":
                keep_best_no_start(standalone, end)

    # Extract values
    q_vals = {d: e["val"] for d, e in standalone.items()}
    result  = dict(q_vals)

    # Back into missing quarters from YTD entries
    for ytd_end in sorted(ytd.keys()):
        ytd_val      = ytd[ytd_end]["val"]
        ytd_start    = ytd[ytd_end].get("start", "")
        ytd_end_dt   = datetime.strptime(ytd_end, "%Y-%m-%d")

        if not ytd_start:
            continue

        ytd_start_dt = datetime.strptime(ytd_start, "%Y-%m-%d")
        covered = {
            d: v for d, v in result.items()
            if ytd_start_dt <= datetime.strptime(d, "%Y-%m-%d") < ytd_end_dt
        }

        if ytd_end not in result and len(covered) >= 1:
            known = sum(covered.values())
            result[ytd_end] = ytd_val - known

    # Back into Q4 from annual entries
    for ann_date, ann_entry in annual.items():
        ann_val = ann_entry["val"]
        ann_dt  = datetime.strptime(ann_date, "%Y-%m-%d")
        nine_months_ago = ann_dt - timedelta(days=275)

        relevant = {
            d: v for d, v in result.items()
            if nine_months_ago <= datetime.strptime(d, "%Y-%m-%d") < ann_dt
        }

        if len(relevant) >= 2:
            known  = sum(relevant.values())
            result[ann_date] = ann_val - known

    return result

def extract_all_metrics(facts):
    """Extract only meaningful metrics using a whitelist approach"""
    income_data   = {}
    balance_data  = {}
    cashflow_data = {}

    # ── Whitelist of tags we want ─────────────────────────────────
    income_tags = {
        "Revenue":        ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
        "CostOfRevenue":  ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold"],
        "GrossProfit":    ["GrossProfit"],
        "R&D_Expense":    ["ResearchAndDevelopmentExpense"],
        "SG&A_Expense":   ["SellingGeneralAndAdministrativeExpense"],
        "OperatingIncome":["OperatingIncomeLoss"],
        "InterestExpense":["InterestExpense"],
        "PreTaxIncome":   ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"],
        "IncomeTaxExpense":["IncomeTaxExpenseBenefit"],
        "NetIncome":      ["NetIncomeLoss"],
        "EPS_Basic":      ["EarningsPerShareBasic"],
        "EPS_Diluted":    ["EarningsPerShareDiluted"],
        "SharesBasic":    ["WeightedAverageNumberOfSharesOutstandingBasic"],
        "SharesDiluted":  ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    }

    balance_tags = {
        "TotalAssets":          ["Assets"],
        "CurrentAssets":        ["AssetsCurrent"],
        "Cash":                 ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents"],
        "ShortTermInvestments": ["ShortTermInvestments", "MarketableSecuritiesCurrent"],
        "AccountsReceivable":   ["AccountsReceivableNetCurrent"],
        "Inventory":            ["InventoryNet"],
        "PP&E_Net":             ["PropertyPlantAndEquipmentNet"],
        "Goodwill":             ["Goodwill"],
        "TotalLiabilities":     ["Liabilities"],
        "CurrentLiabilities":   ["LiabilitiesCurrent"],
        "AccountsPayable":      ["AccountsPayableCurrent"],
        "ShortTermDebt":        ["ShortTermBorrowings", "DebtCurrent"],
        "LongTermDebt":         ["LongTermDebt", "LongTermDebtNoncurrent"],
        "TotalEquity":          ["StockholdersEquity", "StockholdersEquityAttributableToParent"],
        "RetainedEarnings":     ["RetainedEarningsAccumulatedDeficit"],
    }

    cashflow_tags = {
        "OperatingCashFlow":  ["NetCashProvidedByUsedInOperatingActivities"],
        "InvestingCashFlow":  ["NetCashProvidedByUsedInInvestingActivities"],
        "FinancingCashFlow":  ["NetCashProvidedByUsedInFinancingActivities"],
        "CapEx":              ["PaymentsToAcquirePropertyPlantAndEquipment"],
        "D&A":                ["DepreciationDepletionAndAmortization"],
        "StockBasedComp":     ["ShareBasedCompensation"],
        "ShareBuybacks":      ["PaymentsForRepurchaseOfCommonStock"],
        "DividendsPaid":      ["PaymentsOfDividends"],
    }

    def get_entries(tags):
        for tag in tags:
            if tag not in facts:
                continue
            units = facts[tag].get("units", {})
            unit_data = units.get("USD", units.get("shares", []))
            entries = [e for e in unit_data if e.get("form") in ["10-Q", "10-K"]]
            if not entries:
                continue
            # Deduplicate by (start, end) keeping most recently filed
            seen = {}
            for e in entries:
                key = (e.get("start", ""), e["end"])
                if key not in seen or e.get("filed", "") > seen[key].get("filed", ""):
                    seen[key] = e
            return sorted(seen.values(), key=lambda x: x["end"])
        return []

    # Extract income metrics
    for label, tags in income_tags.items():
        entries = get_entries(tags)
        if entries:
            derived = derive_quarterly(entries)
            derived = dict(sorted(derived.items())[-16:])
            income_data[label] = derived

    # Extract balance sheet metrics
    for label, tags in balance_tags.items():
        entries = get_entries(tags)
        if entries:
            data = {e["end"]: e["val"] for e in entries}
            balance_data[label] = data

    # Extract cash flow metrics
    for label, tags in cashflow_tags.items():
        entries = get_entries(tags)
        if entries:
            derived = derive_quarterly(entries)
            derived = dict(sorted(derived.items())[-16:])
            cashflow_data[label] = derived

    return income_data, balance_data, cashflow_data

def build_dataframe(facts, ticker):
    income_data, balance_data, cashflow_data = extract_all_metrics(facts)

    # Collect all dates
    all_dates = set()
    for d in [income_data, balance_data, cashflow_data]:
        for vals in d.values():
            all_dates.update(vals.keys())

    # Only keep standard quarter-end dates
    valid_month_days = ["03-31", "06-30", "09-30", "12-31"]
    all_dates = {d for d in all_dates if any(d.endswith(md) for md in valid_month_days)}

    # Build rows
    rows = []
    for date in sorted(all_dates):
        row = {"Date": date, "Ticker": ticker.upper()}
        for label, vals in income_data.items():
            row[label] = vals.get(date)
        for label, vals in balance_data.items():
            row[label] = vals.get(date)
        for label, vals in cashflow_data.items():
            row[label] = vals.get(date)
        rows.append(row)

    # Use pd.concat to avoid fragmentation warning
    df = pd.DataFrame(rows)

    # Forward fill balance sheet columns
    for col in balance_data.keys():
        if col in df.columns:
            df[col] = df[col].ffill()

    # Calculate FreeCashFlow cleanly
    if "OperatingCashFlow" in df.columns and "CapEx" in df.columns:
        fcf = df["OperatingCashFlow"] - df["CapEx"].fillna(0)
        df = pd.concat([df, fcf.rename("FreeCashFlow")], axis=1)

    # Drop rows where most columns are empty
    df = df.dropna(thresh=len(df.columns) // 3)

    # Keep last 12 rows
    df = df.tail(12).reset_index(drop=True)

    # Drop columns that are entirely empty
    df = df.dropna(axis=1, how="all")

    # Drop columns where more than 40% of values are missing
    df = df.dropna(axis=1, thresh=int(len(df) * 0.6))

    # Put key columns first, rest follow
    priority_cols = [
        "Date", "Ticker",
        "Revenue", "CostOfRevenue", "GrossProfit", "R&D_Expense",
        "SG&A_Expense", "OperatingExpenses", "OperatingIncome",
        "InterestExpense", "PreTaxIncome", "IncomeTaxExpense", "NetIncome",
        "EPS_Basic", "EPS_Diluted",
        "TotalAssets", "CurrentAssets", "Cash", "CashAndShortTermInvestments",
        "AccountsReceivable", "Inventory", "PP&E_Net", "Goodwill",
        "TotalLiabilities", "CurrentLiabilities", "AccountsPayable",
        "ShortTermDebt", "LongTermDebt", "TotalEquity", "RetainedEarnings",
        "OperatingCashFlow", "InvestingCashFlow", "FinancingCashFlow",
        "CapEx", "FreeCashFlow", "D&A", "StockBasedComp",
        "ShareBuybacks", "DividendsPaid"
    ]

    front = [c for c in priority_cols if c in df.columns]
    rest  = [c for c in df.columns if c not in front]
    df = df[front + rest]

    return df.copy()

def fetch_and_export(ticker):
    print(f"\nFetching SEC data for {ticker.upper()}...")

    cik = get_cik(ticker)
    if not cik:
        return None

    facts = get_financial_data(cik)
    df = build_dataframe(facts, ticker)

    filename = f"{ticker.upper()}_financials.csv"
    df.to_csv(filename, index=False)

    print(f"\n✅ Done! Exported {len(df)} rows x {len(df.columns)} columns to {filename}")
    preview_cols = ["Date", "Ticker"] + [c for c in ["Revenue", "NetIncome", "OperatingCashFlow"] if c in df.columns]
    print(df[preview_cols].to_string(index=False))
    print(f"\nColumns pulled: {list(df.columns[:10])}...")
    return df

if __name__ == "__main__":
    ticker = input("Enter a stock ticker: ")
    fetch_and_export(ticker)