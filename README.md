# 📈 Stock Analyzer

A free, fully local stock analysis tool that pulls real financial data directly from SEC EDGAR filings and uses AI to generate buy/sell recommendations — no paid APIs required.

## Features

- 🔍 Search any publicly traded US stock by ticker
- 📊 Pulls 12 quarters of financial data straight from SEC EDGAR (free, no API key needed)
- 📋 Exports full Income Statement, Balance Sheet, and Cash Flow data to CSV
- 📈 Interactive charts for Revenue, Net Income, Free Cash Flow, and more
- 🤖 AI-powered Buy/Hold/Sell recommendation using Llama 3.1 (runs 100% locally via Ollama)

## Tech Stack

- **Python** — core language
- **SEC EDGAR API** — free financial data source
- **Pandas** — data processing and CSV export
- **Streamlit** — web dashboard
- **Ollama + Llama 3.1** — local AI analysis (no API costs)

## Getting Started

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com) installed with Llama 3.1 pulled

### Installation

1. Clone the repo
```bash
   git clone https://github.com/romalebadi/stock-analyzer.git
   cd stock-analyzer
```

2. Create and activate a virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Pull the Llama 3.1 model
```bash
   ollama pull llama3.1
```

### Usage

Run the Streamlit dashboard:
```bash
streamlit run sec_app.py
```

Or run the data fetcher directly:
```bash
python sec_fetcher.py
```

## Data Source

All financial data is sourced from the [SEC EDGAR API](https://data.sec.gov) which is free and publicly available. No API key required.

## Disclaimer

This tool is for educational and research purposes only. Nothing here constitutes financial advice.