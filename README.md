# Assets Parser

Requires authorisation via etherionlab@gmail.com

## Config
See [sample.yml](configs/sample.yml)

## Server endpoints
* `/update_table`: updates the google sheet with actual information on balances, prices, etc.
    Returns JSON `{"status": "OK", "data": none}` on success

* `/token_price`: fetches the actual token price. Returns JSON `{"USD": 12.3, "BTC": 32.1, "ETH": 21.3, "token_supply": 1234"}` on success


## Scripts

First activate virtualenv by running:
`source env/bin/activate`

`python3 update_table_py` - updates prices, balances and portfolio of the fund.

 Balances fetcher works for following currencies:
 
 BTC, ETH, ETC, ICONOMI, GOLEM, MLN, HMQ, LH, REP, WAVES, GAME, ANT, BCAP, BAT, SNT, STORJ, SONM
 - Poloniex
 - Kraken
