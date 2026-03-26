import ollama
import pandas as pd

def analyze_stock(ticker):
    filename = f"{ticker.upper()}_financials.csv"
    
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"No data found for {ticker}. Run sec_fetcher.py first.")
        return
    
    # Drop fully empty rows and fill blanks
    df = df.dropna(how="all", subset=["Revenue", "NetIncome", "OperatingIncome", "FreeCashFlow", "TotalDebt"])
    df = df.fillna("N/A")
    
    # Format data as a readable table for the AI
    data_str = df.to_string(index=False)
    
    prompt = f"""
You are a financial analyst. Below is {ticker.upper()}'s quarterly financial data pulled from SEC filings.

{data_str}

Based on this data, please provide:
1. A brief trend analysis (revenue, income, cash flow, debt)
2. Key strengths and red flags
3. A clear BUY, HOLD, or SELL recommendation with reasoning

Be concise and direct. Format your response with clear sections.
"""

    print(f"\n🤖 Analyzing {ticker.upper()} with Llama 3.1...\n")
    print("-" * 50)
    
    response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(response["message"]["content"])
    print("-" * 50)

if __name__ == "__main__":
    ticker = input("Enter a stock ticker to analyze: ")
    analyze_stock(ticker)