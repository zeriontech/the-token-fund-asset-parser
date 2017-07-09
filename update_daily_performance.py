#!/usr/bin/python3
import asyncio

from models.google_sheets_api import SheetsAPI
from models.etherscan import EtherscanAPI
from models.tokensupply import TokenSupplyAPI

from update_portfolio import update_portfolio

api = SheetsAPI()
etherscanAPI = EtherscanAPI()
tokenSupplyAPI = TokenSupplyAPI()

number_of_tokens = 0


def on_token_supply_fetched(supply):
    global number_of_tokens
    number_of_tokens = supply


def update_daily_performance():
    # Updates current portfolio
    # Uses same date as in portfolio for correct filtering
    global number_of_tokens
    date, portfolio = update_portfolio()

    assets_usd_price = sum([row[7] for row in portfolio])
    assets_btc_price = sum([row[8] for row in portfolio])
    assets_eth_price = sum([row[9] for row in portfolio])

    latest_token_prices = api.get_latest_token_prices()
    latest_token_supply = api.get_latest_token_supply()

    loop = asyncio.get_event_loop()

    future = tokenSupplyAPI.get_token_supply(loop, on_token_supply_fetched)
    loop.run_until_complete(future)

    row = [
        date,  # Date
        number_of_tokens,  # Token supply
        number_of_tokens - latest_token_supply,  # 12h change in token supply
        assets_usd_price,
        assets_btc_price,
        assets_eth_price,
        assets_usd_price / number_of_tokens,  # USD Token price
        assets_usd_price / number_of_tokens / latest_token_prices[0] - 1, # USD price 12h change
        assets_usd_price / number_of_tokens / 10.0 - 1,
        assets_btc_price / number_of_tokens,  # USD Token price
        assets_btc_price / number_of_tokens / latest_token_prices[1] - 1, # BTC price 12h change
        assets_btc_price / number_of_tokens / 0.010103 - 1,
        assets_eth_price / number_of_tokens,  # USD Token price
        assets_eth_price / number_of_tokens / latest_token_prices[2] - 1, # ETH price 12h change
        assets_eth_price / number_of_tokens / 0.206957 - 1,
    ]
    api.add_daily_performance_row(row)

if __name__ == '__main__':
    update_daily_performance()
