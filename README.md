# Assets Parser

Requires authorisation via etherionlab@gmail.com

## Scripts

First activate virtualenv by running:
`source env/bin/activate`

`python update_performance.py` - updates prices, balances and portfolio of the fund.

You can also use these scripts separately:
 - `python balances_fetcher.py` - updates balances of addresses
 - `python prices_fetcher.py` - updates prices of assets if their names are in the top100 of most popular assets at coinmarketcup.com
 - `python update_portfolio.py` - update portfolio of the fund (all assets under control with their prices).
 
 Balances fetcher works for following currencies:
 
 BTC, ETH, ETC, ICONOMI, GOLEM, MLN, HMQ, LH, REP, WAVES, GAME, ANT, BCAP
 - Poloniex
 - Kraken
