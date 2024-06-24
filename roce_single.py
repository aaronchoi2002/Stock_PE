import requests
import pandas as pd

# Your Financial Modeling Prep API key
api_key = "e3e1ef68f4575bca8a430996a4e11ed1"

# API URL templates
income_url_template = "https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={api_key}"
balance_sheet_url_template = "https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period=quarter&apikey={api_key}"
market_cap_url_template = "https://financialmodelingprep.com/api/v3/market-capitalization/{ticker}?limit=120&apikey={api_key}"

def fetch_financial_data(ticker):
    # Fetch income statement
    income_url = income_url_template.format(ticker=ticker, api_key=api_key)
    income_response = requests.get(income_url)
    income_data = income_response.json()
    income_df = pd.DataFrame(income_data)

    # Fetch balance sheet
    balance_sheet_url = balance_sheet_url_template.format(ticker=ticker, api_key=api_key)
    balance_sheet_response = requests.get(balance_sheet_url)
    balance_sheet_data = balance_sheet_response.json()
    balance_sheet_df = pd.DataFrame(balance_sheet_data)

    if not income_df.empty and not balance_sheet_df.empty:
        # Calculate EBIT (Earnings Before Interest and Taxes)
        EBIT = income_df.iloc[0]['ebitda'] - income_df.iloc[0]['depreciationAndAmortization']

        # Calculate TTM EBIT
        TTM_EBIT = income_df.head(4)['ebitda'] - income_df.head(4)['depreciationAndAmortization']
        TTM_EBIT = TTM_EBIT.sum()

        # Get the most recent cash and cash equivalents
        cash_equivalents = balance_sheet_df.iloc[0]['cashAndCashEquivalents']

        # Total debt
        total_debt = balance_sheet_df.iloc[0]['totalDebt']

        # Market capitalization
        market_cap_url = market_cap_url_template.format(ticker=ticker, api_key=api_key)
        market_cap_response = requests.get(market_cap_url)
        market_cap_data = market_cap_response.json()
        market_cap_df = pd.DataFrame(market_cap_data)
        market_cap_value = market_cap_df['marketCap'][0]

        # Enterprise value (EV)
        ev = market_cap_value + total_debt - cash_equivalents

        # Assume annual EBIT by multiplying the latest quarter's EBIT by 4
        annual_EBIT = TTM_EBIT 
        
        # annual_EBIT = ttm_eps

        # Earnings yield
        earnings_yield = annual_EBIT / ev if ev != 0 else 0

        # Get the most recent total non-current liabilities and stockholders' equity
        total_non_current_liabilities = balance_sheet_df.iloc[0]['totalNonCurrentLiabilities']
        stockholders_equity = balance_sheet_df.iloc[0]['totalStockholdersEquity']

        # Calculate ROCE (Return on Capital Employed)
        capital_employed = total_non_current_liabilities + stockholders_equity
        ROCE = annual_EBIT / capital_employed if capital_employed != 0 else 0

        # Create a dictionary to hold the financial data
        financial_data = {
            'ROCE': ROCE,
            'Earnings Yield': earnings_yield,
            'EBIT': EBIT,
            'Annual EBIT': annual_EBIT,
            'Total Non-Current Liabilities': total_non_current_liabilities,
            'Stockholders Equity': stockholders_equity,
            'Market Cap': market_cap_value,
            'Cash Equivalents': cash_equivalents,
            'Total Debt': total_debt
        }

        return financial_data
    else:
        return {}

# Example usage


ff= fetch_financial_data("MMM")
print(ff)
