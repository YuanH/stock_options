import yfinance as yf

def fetch_option_chain(ticker_symbol: str):
    """
    Fetch and display the option chain for a given stock ticker symbol.

    :param ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
    """
    # Fetch the stock data
    stock = yf.Ticker(ticker_symbol)
    

    # Get available expiration dates
    expiration_dates = stock.options
    print(f"Available expiration dates for {ticker_symbol}: {expiration_dates}")
    
    # Fetch option chain data for the first expiration date as an example
    if expiration_dates:
        first_date = expiration_dates[0]
        option_chain = stock.option_chain(first_date)
        
        print("\nCalls:")
        print(option_chain.calls)
        
        print("\nPuts:")
        print(option_chain.puts)
    else:
        print(f"No options data available for {ticker_symbol}.")

import yfinance as yf
import pandas as pd

def calculate_annualized_return(option_data, stock_price, days_to_expiration, type):
    """
    Calculate the annualized return for each option.
    
    :param option_data: DataFrame containing option data (calls or puts).
    :param stock_price: Current stock price.
    :param days_to_expiration: Days remaining to expiration.
    :return: DataFrame with an additional column for annualized return.
    """
    # Convert days to expiration to years
    years_to_expiration = days_to_expiration / 365
    print(option_data)
    # Calculate intrinsic value and potential annualized return
    # if type == "calls":
    #     option_data['Intrinsic Value'] = option_data['strike'].apply(lambda x: max(stock_price - x, 0))
    # else:
    #     option_data['Intrinsic Value'] = option_data['strike'].apply(lambda x: max(x - stock_price, 0))


    # Calculate annualized return: (premium - intrinsic value) / intrinsic value scaled by time
    # option_data['Annualized Return'] = (
    #     (option_data['lastPrice'] - option_data['Intrinsic Value']) / option_data['Intrinsic Value']
    # ) / years_to_expiration

    # (Returns divided by Capital at Risk) x (365 divided by Holding Period)
    option_data['Annualized Return'] = option_data['bid'] / option_data['strike'] / years_to_expiration * 100

    # Replace infinite or NaN values (e.g., for options with zero intrinsic value)
    option_data['Annualized Return'].replace([float('inf'), -float('inf')], 0, inplace=True)
    option_data['Annualized Return'].fillna(0, inplace=True)

    return option_data

def fetch_and_calculate_option_returns(ticker_symbol, file_handle):
    """
    Fetch option chain data and calculate annualized returns for each put/call option.

    :param ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
    """
    # Fetch the stock data
    stock = yf.Ticker(ticker_symbol)
    stock_price = stock.info['currentPrice']
    expiration_dates = stock.options

    if not expiration_dates:
        print(f"No options data available for {ticker_symbol}.")
        return

    # Fetch data for the first expiration date as an example
    first_date = expiration_dates[1]
    print(f"Fetching data for expiration date: {first_date}")
    option_chain = stock.option_chain(first_date)
    
    # Assume days to expiration is derived from the expiration date
    days_to_expiration = (pd.to_datetime(first_date) - pd.Timestamp.now()).days

    # Process call and put options
    calls = calculate_annualized_return(option_chain.calls, stock_price, days_to_expiration, "calls")
    calls.name = "Calls"

    puts = calculate_annualized_return(option_chain.puts, stock_price, days_to_expiration, "puts")
    puts.name = "Puts"

    file_handle.write(f"\n--- Ticker: {ticker_symbol} ---\n")
    file_handle.write(f"Stock Price: {stock_price}\n")
    file_handle.write(f"Expiration Date: {first_date}\n\n")

    file_handle.write("Calls with Annualized Returns:\n")
    file_handle.write(calls.to_string(index=False))
    file_handle.write("\n\n")

    file_handle.write("Puts with Annualized Returns:\n")
    file_handle.write(puts.to_string(index=False))
    file_handle.write("\n")


# Example usage
tickers = ["SOC", "AMR", "OXY", "TPH", "PHM", "AN"]
output_file = "option_returns.txt"
with open(output_file, "w") as file:
    for ticker in tickers:
        fetch_and_calculate_option_returns(ticker, file)

# Example usage
# fetch_option_chain("AMR")