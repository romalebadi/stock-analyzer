import requests
from datetime import datetime

def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "sec-analyzer myemail@email.com"}
    response = requests.get(url, headers=headers)
    for entry in response.json().values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)

cik = get_cik("TSLA")
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
headers = {"User-Agent": "sec-analyzer myemail@email.com"}
facts = requests.get(url, headers=headers).json()["facts"]["us-gaap"]

tag = "RevenueFromContractWithCustomerExcludingAssessedTax"
entries = facts.get(tag, {}).get("units", {}).get("USD", [])
entries = [e for e in entries if e.get("form") in ["10-Q", "10-K"]]
entries = sorted(entries, key=lambda x: x["end"])

# Show all 2023 entries
print(f"{'Form':<8} {'Start':<12} {'End':<12} {'Days':<6} {'Value'}")
print("-" * 65)
for e in entries:
    if "2023" in e["end"] or "2022" in e["end"]:
        start = e.get("start", "N/A")
        end   = e["end"]
        if start != "N/A":
            days = (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days
        else:
            days = "N/A"
        print(f"{e['form']:<8} {start:<12} {end:<12} {str(days):<6} {e['val']:,}")