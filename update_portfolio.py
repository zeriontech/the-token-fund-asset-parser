from datetime import datetime

from models.google_sheets_api import SheetsAPI
from balances_fetcher import fetch_balances
from prices_fetcher import fetch_prices

api = SheetsAPI()


def update_portfolio():

    asset_names, asset_symbols = api.read_balances_assets()
    balances = fetch_balances()
    prices = fetch_prices()
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    whole_usd_price = sum([balances.get(asset) * float(prices.get(asset)[0]) for asset in asset_symbols if balances.get(asset,0) > 0])

    portfolio = []

    for asset in asset_symbols:
        if balances.get(asset, 0) > 0:

            row = [
                date,
                asset_names[asset_symbols.index(asset)],
                asset,
                prices.get(asset)[0],
                prices.get(asset)[1],
                float(prices.get(asset)[1]) / float(prices.get('ETH')[1]),
                balances.get(asset),
                balances.get(asset) * float(prices.get(asset)[0]),
                balances.get(asset) * float(prices.get(asset)[1]),
                balances.get(asset) * (float(prices.get(asset)[1]) / float(prices.get('ETH')[1])),
                balances.get(asset) * float(prices.get(asset)[0]) / whole_usd_price,
            ]
            api.add_portfolio_row(row)
            portfolio.append(row)
    return date, portfolio
    
if __name__ == '__main__':
    update_portfolio()
