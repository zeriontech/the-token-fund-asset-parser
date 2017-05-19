import asyncio
from datetime import datetime

from models.coinmarketcap import CoinmarketcapAPI
from models.google_sheets_api import SheetsAPI
from models.european_cb import EuropeanCBAPI

api = SheetsAPI()
coinmarketcap_api = CoinmarketcapAPI(150)
europeanCB_api = EuropeanCBAPI()
asset_symbols_set = set()
asset_names, asset_symbols = [[], []]
prices = {}


def on_eur_rate_received(rate):
    global prices
    prices['EUR'] = rate, 0


def on_assets_received(_assets):
    global prices, asset_symbols_set
    assets = []
    for asset in _assets:
        if asset.symbol == 'TIME':
            asset.symbol = 'LH'
        if asset.symbol in asset_symbols_set:
            assets.append(asset)
    # compose dict asset_symbol -> prices
    for asset in assets:
        prices[asset.symbol] = asset.price_USD, asset.price_BTC


def fetch_prices():
    global asset_names, asset_symbols, asset_symbols_set
    asset_names, asset_symbols = api.read_prices_assets()
    asset_symbols_set = set(asset_symbols)

    loop = asyncio.get_event_loop()

    futures = [coinmarketcap_api.request_assets(loop, on_assets_received),
               europeanCB_api.get_eur_usd_exchange_rate(loop, on_eur_rate_received)]

    loop.run_until_complete(asyncio.gather(*futures))
    #
    # here all async requests already finished
    #

    global prices
    # compose new line
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    row = [date]
    for name, symbol in zip(asset_names, asset_symbols):
        currency = name.split()[-1].replace('(', '').replace(')', '')
        price = prices.get(symbol, ('', ''))[0 if currency == 'USD' else 1]
        if symbol == 'EUR' and currency == 'BTC':
            price = str(float(prices.get('BTC', (1, 1))[0]) / float(prices.get('EUR', (-1, -1))[0]))
        if price == '':
            price = '=INDIRECT(ADDRESS(ROW() + 1,COLUMN()))'
        row.append(price)
    api.add_prices_row(row)

    return api.read_last_prices()
    
if __name__ == '__main__':
    fetch_prices()
