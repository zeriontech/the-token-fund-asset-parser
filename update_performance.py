#!/usr/bin/python3
# import asyncio
#
# from models.google_sheets_api import SheetsAPI
# from models.etherscan import EtherscanAPI
# from models.tokensupply import TokenSupplyAPI
#
# from update_portfolio import update_portfolio
#
# api = SheetsAPI()
# etherscanAPI = EtherscanAPI()
# tokenSupplyAPI = TokenSupplyAPI()
#
# number_of_tokens = 0
#
#
# def on_token_supply_fetched(supply):
#     global number_of_tokens
#     number_of_tokens = supply
#
#
# def update_performance():
#     # Updates current portfolio
#     # Uses same date as in portfolio for correct filtering
#     date = update_portfolio()
#
#     loop = asyncio.get_event_loop()
#
#     future = tokenSupplyAPI.get_token_supply(loop, on_token_supply_fetched)
#
#     loop.run_until_complete(future)
#
#     row = [
#         date,  # Date
#         number_of_tokens,  # Token supply
#         '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-2));Portfolio!H:H)',  # USD Portfolio value
#         '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-3));Portfolio!I:I)',  # BTC Portfolio value
#         '=sumif(Portfolio!A:A;INDIRECT(ADDRESS(ROW();COLUMN()-4));Portfolio!J:J)',  # ETH Portfolio value
#         '10' if number_of_tokens == 0 else '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))/INDIRECT(ADDRESS(ROW();COLUMN() - 4))',  # USD Token price
#         '=10 / Prices!B3' if number_of_tokens == 0 else '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))/INDIRECT(ADDRESS(ROW();COLUMN() - 5))',  # BTC Token price
#         '=10 / Prices!D3' if number_of_tokens == 0 else '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))/INDIRECT(ADDRESS(ROW();COLUMN() - 6))',   # ETH Token price
#     ]
#     api.add_performance_row(row)
#
# if __name__ == '__main__':
#     update_performance()
