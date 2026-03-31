import requests
from datetime import datetime

def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "sec-analyzer myemail@email.com"}
    response = requests.get(url, headers=headers)
    for entry in response.json().values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)

cik = get_cik("GME")
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
headers = {"User-Agent": "sec-analyzer myemail@email.com"}
facts = requests.get(url, headers=headers).json()["facts"]["us-gaap"]

for tag in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]:
    entries = facts.get(tag, {}).get("units", {}).get("USD", [])
    entries = [e for e in entries if e.get("form") in ["10-Q", "10-K"]]
    entries = sorted(entries, key=lambda x: x["end"])[-16:]
    if entries:
        print(f"\n=== {tag} ===")
        print(f"{'Form':<8} {'Start':<12} {'End':<12} {'Days':<6} {'Value'}")
        print("-" * 65)
        for e in entries:
            start = e.get("start", "N/A")
            end   = e["end"]
            days  = "N/A"
            if start != "N/A":
                days = str((datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days)
            print(f"{e['form']:<8} {start:<12} {end:<12} {days:<6} {e['val']:,}")