from datetime import datetime

from models.coinmarketcap import CoinmarketcapAPI
from models.google_sheets_api import SheetsAPI

api = SheetsAPI()
coinmarketcap_api = CoinmarketcapAPI(150)

asset_symbols_set = set()
asset_names, asset_symbols = [[], []]
prices = {}


def on_assets_received(_assets):
    assets = []
    for asset in _assets:
        if asset.symbol == 'TIME':
            asset.symbol = 'LH'
        if asset.symbol in asset_symbols_set:
            assets.append(asset)
    # compose dict asset_symbol -> prices
    global prices
    for asset in assets:
        prices[asset.symbol] = asset.price_USD, asset.price_BTC
    # compose new line
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    row = [date]
    for name, symbol in zip(asset_names, asset_symbols):
        currency = name.split()[-1].replace('(', '').replace(')', '')
        price = prices.get(symbol, ('', ''))[0 if currency == 'USD' else 1]
        if price == '':
            price = '=INDIRECT(ADDRESS(ROW() + 1,COLUMN()))'
        row.append(price)
    api.add_prices_row(row)


def fetch_prices():
    global asset_names, asset_symbols, asset_symbols_set
    asset_names, asset_symbols = api.read_prices_assets()
    asset_symbols_set = set(asset_symbols)
    coinmarketcap_api.request_assets(on_assets_received)
    return prices
    
if __name__ == '__main__':
    fetch_prices()
