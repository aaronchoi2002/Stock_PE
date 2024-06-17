import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Your Financial Modeling Prep API key
api_key = "e3e1ef68f4575bca8a430996a4e11ed1"

# Streamlit app title
st.title('Historical PE Ratio Calculator')

# User input for stock ticker
ticker = st.text_input("Enter a stock ticker:", "AAPL")
period = st.number_input("Number of year PE record:", 5)

# Map to sector 
sector_mapping = {
    "Information Technology": "Technology",
    "Real Estate": "Real Estate",
    "Health Care": "Healthcare",
    "S&P 500 Index": "S&P 500 Index",
    "Consumer Discretionary": "Consumer Cyclical",
    "Materials": "Basic Materials",
    "Industrials": "Industrials",
    "Consumer Staples": "Consumer Defensive",
    "Communication Services": "Communication Services",
    "Utilities": "Utilities",
    "Financials": "Financial Services",
    "Energy": "Energy"
} 

# Fetch data button
if st.button('Fetch Data'):
    # Define the API endpoints for historical price and quarterly EPS
    price_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}"
    eps_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=160&apikey={api_key}"
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"


    # Send requests to the API
    price_response = requests.get(price_url)
    eps_response = requests.get(eps_url)
    profile_response = requests.get(profile_url)

    # Check if the requests were successful
    if price_response.status_code == 200 and eps_response.status_code == 200:
        # Load the price data into a DataFrame
        # price_data = price_response.json()
        # historical_prices = price_data['historical']
        # price_df = pd.DataFrame(historical_prices)
        # price_df['date'] = pd.to_datetime(price_df['date'])
        # price_df = price_df[['date', 'close']]


        end_date = datetime.now()
        start_date = end_date - timedelta(days=period*365)
        price_df = yf.download(ticker, start=start_date, end=end_date)
        price_df.reset_index(inplace=True)
        price_df = price_df[['Date', 'Close']]
        price_df.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)

        # Load the EPS data into a DataFrame
        eps_data = eps_response.json()
        eps_df = pd.DataFrame(eps_data)
        eps_df['date'] = pd.to_datetime(eps_df['date'])
        eps_df = eps_df[['date', 'eps']]

        # Sort EPS data in ascending order by date for rolling sum calculation
        eps_df = eps_df.sort_values(by='date')

        # Calculate the TTM EPS by summing the latest 4 quarters
        eps_df['ttm_eps'] = eps_df['eps'].rolling(window=4).sum()

        # Merge the price and TTM EPS data on the nearest date
        merged_df = pd.merge_asof(price_df.sort_values('date'), eps_df[['date', 'ttm_eps']], on='date', direction='backward')

        # Calculate the PE ratio
        merged_df['PE Ratio'] = merged_df['close'] / merged_df['ttm_eps']

        # Filter out rows with NaN values in PE Ratio
        merged_df = merged_df.dropna(subset=['PE Ratio'])

        # Calculate the median PE ratio
        median_pe = merged_df['PE Ratio'].median()

         # Calculate the average PE ratio
        average_pe = merged_df['PE Ratio'].mean()

        # Load the company profile data
        profile_data = profile_response.json()
        sector = profile_data[0]['sector']
        industry = profile_data[0]['industry']

        # Get the last PE TTM
        last_pe_ttm = merged_df.iloc[-1]['PE Ratio']

        # Get the last ttm_eps
        last_ttm_eps = merged_df.iloc[-1]['ttm_eps']

        # Display the last PE TTM value
        col1, col2= st.columns([2,1])
        with col1:
            st.write(f"**Sector:** {sector}")
            st.write(f"**Last PE:** {last_pe_ttm:.2f}")
        with col2:
            st.write(f"**Industry:** {industry}")
            st.write(f"**Last TTM EPS:** {last_ttm_eps:.2f}")
            

        # Plot the PE Ratio and median line using matplotlib
        plt.figure(figsize=(10, 6))
        plt.plot(merged_df['date'], merged_df['PE Ratio'], linestyle='-', label='PE Ratio')
        plt.axhline(y=median_pe, color='r', linestyle='--', label=f'Median PE Ratio: {median_pe:.2f}')
        plt.axhline(y=average_pe, color='g', linestyle='--', label=f'Average PE Ratio: {average_pe:.2f}')
        plt.title(f'Historical PE Ratio for {ticker}')
        plt.xlabel('Date')
        plt.ylabel('PE Ratio')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(plt)

        url = 'https://worldperatio.com/sp-500-sectors/'
        response = requests.get(url)
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            # Assuming the first table is the one we want
            df = tables[0]
        df= df[['Unnamed: 1_level_0', 'Unnamed: 2_level_0', 'Unnamed: 4_level_0','Historical P/E Average']]
        df.columns = df.columns.droplevel(0)
        df['S&P 500 Sector'] = df['S&P 500 Sector'].map(sector_mapping)
        
        # Get the relevant data for the sector
        sector_row = df[df['S&P 500 Sector'] == sector]
        if not sector_row.empty:
            current_pe = sector_row['P/E▾'].values[0]
            five_year_pe = sector_row['5 Years'].values[0]
            ten_year_pe = sector_row['10 Years'].values[0]

            # Display the P/E values
            col1, col2, col3= st.columns([1,1,1])
            with col1:
                st.write(f"**Sector Current P/E:** {current_pe}")
            with col2:
                st.write(f"**5-Year Average P/E:** {five_year_pe}")
            with col3:
                st.write(f"**10-Year Average P/E:** {ten_year_pe}")
        else:
            st.write("Sector data not found in the table.")

        st.markdown('[Sector PE reference](https://worldperatio.com/sp-500-sectors)')


    else:
        st.error(f"Failed to fetch data: {price_response.status_code}, {eps_response.status_code}")

