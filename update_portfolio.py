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
                '=INDIRECT(ADDRESS(ROW();COLUMN() - 1))*INDIRECT(ADDRESS(ROW();COLUMN()-4))',
                '=INDIRECT(ADDRESS(ROW();COLUMN() - 2))*INDIRECT(ADDRESS(ROW();COLUMN()-4))',
                '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))*INDIRECT(ADDRESS(ROW();COLUMN()-4))',
                '=INDIRECT(ADDRESS(ROW();COLUMN() - 3))/sumif(A:A, INDIRECT(ADDRESS(ROW();1)), H:H)',
            ]
            api.add_portfolio_row(row)
    return date
    
if __name__ == '__main__':
    update_portfolio()
