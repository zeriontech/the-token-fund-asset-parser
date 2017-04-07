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
    date = update_portfolio()

    loop = asyncio.get_event_loop()

    future = tokenSupplyAPI.get_token_supply(loop, on_token_supply_fetched)
    loop.run_until_complete(future)

    row = [
        date,  # Date
        number_of_tokens,  # Token supply
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 1))-INDIRECT(ADDRESS(ROW() + 1;COLUMN() - 1))',  # 12h change in token supply
        '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-3));Portfolio!H:H)',  # USD Portfolio value
        '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-4));Portfolio!I:I)',  # BTC Portfolio value
        '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-5));Portfolio!J:J)',  # ETH Portfolio value
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))/INDIRECT(ADDRESS(ROW();COLUMN() - 5))',  # USD Token price
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 1))/INDIRECT(ADDRESS(ROW() + 1;COLUMN() - 1)) - 1',  # USD price 12h change
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 2))/10 - 1',
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 5))/INDIRECT(ADDRESS(ROW();COLUMN() - 8))',  # BTC Token price
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 1))/INDIRECT(ADDRESS(ROW() + 1;COLUMN() - 1)) - 1',  # BTC price 12h change
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 2))/0.010103 - 1',
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 7))/INDIRECT(ADDRESS(ROW();COLUMN() - 11))',  # ETH Token price
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 1))/INDIRECT(ADDRESS(ROW() + 1;COLUMN() - 1)) - 1',  # ETH price 12h change
        '=INDIRECT(ADDRESS(ROW();COLUMN() - 2))/0.206957 - 1',
    ]
    api.add_daily_performance_row(row)

if __name__ == '__main__':
    update_daily_performance()
