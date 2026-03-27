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

def extract_metric(facts, keys):
    for key in keys:
        if key in facts:
            units = facts[key].get("units", {})
            unit_data = units.get("USD", units.get("shares", []))
            quarterly = [
                entry for entry in unit_data
                if entry.get("form") in ["10-Q", "10-K"] and "frame" not in entry
            ]
            if quarterly:
                quarterly = sorted(quarterly, key=lambda x: x["end"])[-16:]
                return {entry["end"]: entry["val"] for entry in quarterly}
    return {}

def build_dataframe(facts, ticker):

    income_metrics = {
        "Revenue":           ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
        "CostOfRevenue":     ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
        "GrossProfit":       ["GrossProfit"],
        "OperatingExpenses": ["OperatingExpenses", "OperatingCostsAndExpenses"],
        "OperatingIncome":   ["OperatingIncomeLoss"],
        "NetIncome":         ["NetIncomeLoss"],
        "EPS_Basic":         ["EarningsPerShareBasic", "IncomeLossFromContinuingOperationsPerBasicShare"],
        "EPS_Diluted":       ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"],
    }
    

    balance_metrics = {
        "TotalAssets":        ["Assets"],
        "TotalLiabilities":   ["Liabilities"],
        "Cash":               ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents"],
        "AccountsReceivable": ["AccountsReceivableNetCurrent"],
        "Inventory":          ["InventoryNet"],
        "TotalEquity":        ["StockholdersEquity", "StockholdersEquityAttributableToParent"],
        "ShortTermDebt":      ["ShortTermBorrowings", "DebtCurrent"],
        "LongTermDebt":       ["LongTermDebt", "LongTermDebtNoncurrent"],
    }

    cashflow_metrics = {
        "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
        "InvestingCashFlow": ["NetCashProvidedByUsedInInvestingActivities"],
        "FinancingCashFlow": ["NetCashProvidedByUsedInFinancingActivities"],
        "CapEx":             ["PaymentsToAcquirePropertyPlantAndEquipment"],
    }

    all_metrics = {**income_metrics, **balance_metrics, **cashflow_metrics}

    # Extract all metrics
    extracted = {}
    all_dates = set()
    for label, keys in all_metrics.items():
        data = extract_metric(facts, keys)
        extracted[label] = data
        all_dates.update(data.keys())

    # Build rows
    rows = []
    for date in sorted(all_dates):
        row = {"Date": date, "Ticker": ticker.upper()}
        for label in all_metrics:
            row[label] = extracted[label].get(date, None)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Forward fill balance sheet items
    balance_cols = list(balance_metrics.keys())
    for col in balance_cols:
        if col in df.columns:
            df[col] = df[col].ffill()

    # Calculate Free Cash Flow
    if "OperatingCashFlow" in df.columns and "CapEx" in df.columns:
        df["FreeCashFlow"] = df["OperatingCashFlow"] - df["CapEx"].fillna(0)

    # Drop rows where more than half of income statement columns are empty
    income_cols = [c for c in income_metrics.keys() if c in df.columns]
    df = df[df[income_cols].notna().sum(axis=1) >= len(income_cols) // 2]

    # Keep only last 12 rows
    df = df.tail(12).reset_index(drop=True)

    # Column order
    cols = ["Date", "Ticker",
            "Revenue", "CostOfRevenue", "GrossProfit", "OperatingExpenses",
            "OperatingIncome", "NetIncome", "EPS_Basic", "EPS_Diluted",
            "TotalAssets", "TotalLiabilities", "Cash", "AccountsReceivable",
            "Inventory", "TotalEquity", "ShortTermDebt", "LongTermDebt",
            "OperatingCashFlow", "InvestingCashFlow", "FinancingCashFlow",
            "CapEx", "FreeCashFlow"]

    cols = [c for c in cols if c in df.columns]
    return df[cols]

def fetch_and_export(ticker):
    print(f"\nFetching SEC data for {ticker.upper()}...")

    cik = get_cik(ticker)
    if not cik:
        return None

    facts = get_financial_data(cik)
    df = build_dataframe(facts, ticker)

    filename = f"{ticker.upper()}_financials.csv"
    df.to_csv(filename, index=False)

    print(f"\n✅ Done! Exported to {filename}")
    print(df.to_string(index=False))
    return df

if __name__ == "__main__":
    ticker = input("Enter a stock ticker: ")
    fetch_and_export(ticker)