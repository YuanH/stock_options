from __future__ import annotations
from typing import List, Tuple
import yfinance as yf
import pandas as pd

def calculate_annualized_return(option_data: pd.DataFrame, stock_price: float, days_to_expiration: int, type: str) -> pd.DataFrame:
    """
    Calculate the annualized return for each option.
    
    :param option_data: DataFrame containing option data (calls or puts).
    :param stock_price: Current stock price.
    :param days_to_expiration: Days remaining to expiration.
    :return: DataFrame with an additional column for annualized return.
    """
    
    # Annualized Return = (Premium Collected divided by Capital at Risk) x (365 divided by Holding Period)
    # you can use 'lastPrice', 'bid', or 'ask' as your targeted premium
    if type == 'puts':
        # For cash secured puts, capital reserved = (strike price - premium) * 100 * Quantity
        # Return = premium collected / capital reserved
        option_data['Annualized Return'] = option_data['bid'] / (option_data['strike'] - option_data['bid']) * 365 / days_to_expiration * 100
        option_data['Distance Perc'] = (stock_price - option_data['bid'] - option_data['strike']) / stock_price
    elif type == 'calls':
        # For covered calls, return = premium collected / current stock price
        option_data["Annualized Return"] = option_data['bid'] / stock_price * 365 / days_to_expiration * 100
        option_data['Distance Perc'] = (option_data['strike'] + option_data['bid'] - stock_price) / stock_price * 100
    # Replace infinite or NaN values (e.g., for options with zero intrinsic value)
    option_data['Annualized Return'].replace([float('inf'), -float('inf')], 0, inplace=True)
    option_data['Annualized Return'].fillna(0, inplace=True)


    return option_data

def fetch_and_calculate_option_returns(ticker_symbol: str, return_filter: bool = False, in_the_money: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch option chain data and calculate annualized returns for each put/call option.

    :param ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA').
    :param return_filter: whether to implement a return filter
    :param in_the_money: whether to filter based on in the money
    :return: Two DataFrames, one with puts, one with calls
    """

    # Default Params for calls and puts return threshold
    calls_threshold: float = 7.0
    puts_threshold: float = 15.0

    # Fetch the stock data
    stock = yf.Ticker(ticker_symbol)
    stock_price = stock.info['currentPrice']
    expiration_dates = stock.options

    if not expiration_dates:
        print(f"No options data available for {ticker_symbol}.")
        return

    all_calls: List[pd.DataFrame] = []
    all_puts: List[pd.DataFrame] = []

    # Fetch data for the first expiration date as an example
    for date in expiration_dates:
        print(f"{ticker_symbol}: Fetching data for expiration date: {date}")
        option_chain = stock.option_chain(date)
        days_to_expiration: int = (pd.to_datetime(date) - pd.Timestamp.now()).days

        # Process call and put options
        calls: pd.DataFrame = calculate_annualized_return(option_chain.calls, stock_price, days_to_expiration, "calls")
        calls.name = "Calls"
        if return_filter:
            calls = calls[calls["Annualized Return"] > calls_threshold]
            
        if not in_the_money:
            calls = calls[calls["inTheMoney"] == False]
        calls["Expiration Date"] = date
        calls["Stock Price"] = stock_price
        all_calls.append(calls)

        puts: pd.DataFrame = calculate_annualized_return(option_chain.puts, stock_price, days_to_expiration, "puts")
        puts.name = "Puts"
        if return_filter:
            puts = puts[puts["Annualized Return"] > puts_threshold]
        if not in_the_money:
            puts = puts[puts["inTheMoney"] == False]
        puts["Expiration Date"] = date
        puts["Stock Price"] = stock_price
        all_puts.append(puts)
        
    # Combine all expiration dates into single tables
    combined_calls: pd.DataFrame = pd.concat(all_calls, ignore_index=True)
    combined_puts: pd.DataFrame = pd.concat(all_puts, ignore_index=True)

    return combined_puts, combined_calls

def build_pivot_table(data: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pivot table to display both bid price and annualized return together.
    
    :param data: DataFrame containing options data with expiration dates, strikes, bid, and annualized returns.
    :return: Multi-index pivot table.
    """
    # Pivot table creation
    pivot = pd.pivot_table(
        data,
        index='strike',  # Rows: Strike Prices
        columns='Expiration Date',  # Columns: Expiration Dates
        values=['bid', 'Annualized Return'],  # Values: Bid and Annualized Return
        aggfunc='mean'  # Aggregation function (e.g., mean if duplicates exist)
    )

    pivot = pivot.swaplevel(axis=1).sort_index(axis=1)
    # pivot = pivot.applymap(lambda x: f"{x:.2f}%" if isinstance(x, float) and 'Annualized Return' in str(x) else f"{x:.2f}")

    return pivot

if __name__ == "__main__":
    # Example usage
    # tickers = ["EBAY", "PAG", "AN", "HCC", "AMR", "TPH", "PHM", "TOL", "DAC", "SOC", "OXY", "GOOG"]
    #tickers = ['EBAY', "PAG", "AN", "HCC", "AMR", "TPH", "PHM", "TOL", "DAC", "OXY", "GOOG"]
    tickers = ['PDD']

    for ticker in tickers:
        puts, calls = fetch_and_calculate_option_returns(ticker, return_filter=True, in_the_money=False)
        output_file = f"{ticker}_option_returns.txt"
        with open(output_file, "w") as file:
            file.write(f"\n--- Ticker: {ticker} ---\n")
            
            file.write("Calls with Annualized Returns:\n")
            file.write(calls.to_string(index=False))
            file.write("\n\n")

            file.write("Puts with Annualized Returns:\n")
            file.write(puts.to_string(index=False))
            file.write("\n")

        puts_pivot = build_pivot_table(puts)
        calls_pivot = build_pivot_table(calls)

        puts_pivot.to_csv(f"{ticker}_puts_pivot.csv")
        calls_pivot.to_csv(f"{ticker}_calls_pivot.csv")