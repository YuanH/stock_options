# stock_options

## Prerequisites

`pip install yfinance`
`pip install pandas`

## How to run this

Example code is in `option_chain.py`. Nothing fancy at the moment.

## To Dos

1. Add a downside protection column to the table (distance of current strike price +/- premium to current price)
2. Multiple output file formats (.csv, .txt etc.)
3. Integration with Google Sheets APIs
4. Include Naked Calls and Naked Puts (Personally, I don't like using margins)

## References

[How to Calculate Annualized Returns on Option Trades](https://www.great-option-trading-strategies.com/how-to-calculate-annualized-returns.html)