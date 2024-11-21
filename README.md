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

Compared to last price, mark price provides an easier way to evaluate the current value of equities and options, especially thinly traded securities or option strategies with large bid/ask spreads.

For equities, mark represents one of the following:

- The last trade price of the regular session when the last trade price of the regular session is within the bid/ask spread.
- The bid price when the last trade price is less than the bid.
- The ask price when the last trade price is greater than the ask.
- The close price when the equity has no trades or prevailing bid on a specified date.

For options, mark is the midpoint between the bid and the ask.

## References

[How to Calculate Annualized Returns on Option Trades](https://www.great-option-trading-strategies.com/how-to-calculate-annualized-returns.html)