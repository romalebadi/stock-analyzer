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
    """Back into Q4 = Annual - Q1 - Q2 - Q3 for flow statement items"""
    quarterly = {e["end"]: e["val"] for e in entries if e.get("form") == "10-Q"}
    annual    = {e["end"]: e["val"] for e in entries if e.get("form") == "10-K"}
    result = dict(quarterly)

    for ann_date, ann_val in annual.items():
        ann_year = ann_date[:4]
        q1 = q2 = q3 = None
        for q_date, q_val in quarterly.items():
            if q_date[:4] == ann_year or (
                q_date > f"{int(ann_year)-1}-06-30" and q_date < ann_date
            ):
                month = int(q_date[5:7])
                if month <= 3:
                    q1 = q_val
                elif month <= 6:
                    q2 = q_val
                elif month <= 9:
                    q3 = q_val

        known = sum(v for v in [q1, q2, q3] if v is not None)
        count = sum(1 for v in [q1, q2, q3] if v is not None)
        if count >= 2:
            result[ann_date] = ann_val - known

    return result

def extract_all_metrics(facts):
    """Extract every metric from SEC facts, classify, and return as dicts"""
    income_data   = {}
    balance_data  = {}
    cashflow_data = {}

    for tag, content in facts.items():
        units = content.get("units", {})
        unit_data = units.get("USD", units.get("shares", []))
        if not unit_data:
            continue

        entries = [
            e for e in unit_data
            if e.get("form") in ["10-Q", "10-K"] and "frame" not in e
        ]
        if not entries:
            continue

        entries = sorted(entries, key=lambda x: x["end"])

        # Get plain English label
        label = LABEL_MAP.get(tag, tag)
        category = classify_tag(tag)

        if category == "balance":
            # Point-in-time — just take last 16 values as-is
            recent = entries[-16:]
            data = {e["end"]: e["val"] for e in recent}
            if label not in balance_data:
                balance_data[label] = data

        elif category == "cashflow":
            derived = derive_quarterly(entries)
            derived = dict(sorted(derived.items())[-16:])
            if label not in cashflow_data:
                cashflow_data[label] = derived

        elif category == "income":
            derived = derive_quarterly(entries)
            derived = dict(sorted(derived.items())[-16:])
            if label not in income_data:
                income_data[label] = derived

    return income_data, balance_data, cashflow_data

def build_dataframe(facts, ticker):
    income_data, balance_data, cashflow_data = extract_all_metrics(facts)

    # Collect all dates
    all_dates = set()
    for d in [income_data, balance_data, cashflow_data]:
        for vals in d.values():
            all_dates.update(vals.keys())

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

    df = pd.DataFrame(rows)

    # Forward fill balance sheet columns
    for col in balance_data.keys():
        if col in df.columns:
            df[col] = df[col].ffill()

    # Calculate FreeCashFlow
    if "OperatingCashFlow" in df.columns and "CapEx" in df.columns:
        df["FreeCashFlow"] = df["OperatingCashFlow"] - df["CapEx"].fillna(0)

    # Drop rows where most columns are empty
    df = df.dropna(thresh=len(df.columns) // 3)

    # Keep last 12 rows
    df = df.tail(12).reset_index(drop=True)

    # Drop columns that are entirely empty
    df = df.dropna(axis=1, how="all")

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

    return df

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
    print(df[["Date", "Ticker", "Revenue", "NetIncome", "OperatingCashFlow"]].to_string(index=False))
    return df

if __name__ == "__main__":
    ticker = input("Enter a stock ticker: ")
    fetch_and_export(ticker)