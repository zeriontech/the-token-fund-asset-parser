import asyncio
import time

from fetchers.balances import fetch_balances
from fetchers.prices import fetch_prices
from fetchers.portfolio import fetch_portfolio
from fetchers.token import fetch_token_supply
from models.google_sheets_api import SheetsAPI


def update_balances(api, config, date):
    # Update fund balances
    wallet = api.read_addresses()
    balances = fetch_balances(config, wallet)
    balances_assets = api.read_balances_assets()[1]

    balances_row = [date]
    for asset in balances_assets:
        balances_row.append(balances.get(asset, ''))
    api.add_balances_row(balances_row)

    return balances


def update_prices(api, date):
    # Update coin prices
    prices_assets = api.read_prices_assets()
    last_prices = api.read_last_prices()

    prices = fetch_prices(set(prices_assets[1]))
    prices_row = [date]

    for asset_name, asset_symbol in zip(prices_assets[0], prices_assets[1]):
        if asset_symbol not in prices.keys():
            # TODO: log unfetched price
            print('Warning: price of {} is not fetched'.format(asset_symbol))
            prices[asset_symbol] = last_prices.get(asset_symbol)
        price = prices.get(asset_symbol)
        currency = asset_name.split()[-1].replace('(', '').replace(')', '')
        prices_row.append(price[currency])
    api.add_prices_row(prices_row)

    return prices


def update_portfolio(api, date, balances, prices):
    # Update portfolio
    portfolio = fetch_portfolio(balances, prices)
    balances_names, balances_symbols = api.read_balances_assets()
    update = []
    for idx, symbol in enumerate(balances_symbols):
        if balances.get(symbol, 0) > 0:
            update.append([
                date,  # Update date
                balances_names[idx],  # Asset name
                symbol,  # Asset symbol
                prices.get(symbol).get('USD'),  # Asset USD price
                prices.get(symbol).get('BTC'),  # Asset BTC price
                float(prices.get(symbol).get('BTC')) / float(prices.get('ETH').get('BTC')),  # Asset ETH price
                balances.get(symbol),  # Asset balance
                portfolio.get(symbol).get('USD'),  # Asset USD value
                portfolio.get(symbol).get('BTC'),  # Asset BTC value
                portfolio.get(symbol).get('ETH'),  # Asset ETH value
                portfolio.get(symbol).get('share'),  # Asset % share
            ])
    api.add_portfolio(update)
    return portfolio


def update_daily_performance(api, date, portfolio):
    # Updates current portfolio

    initial_token_usd_price = 10.0
    initial_token_btc_price = 0.010103
    initial_token_eth_price = 0.206957

    portfolio_value = {
        'USD': sum([value.get('USD') for value in portfolio.values()]),
        'BTC': sum([value.get('USD') for value in portfolio.values()]),
        'ETH': sum([value.get('USD') for value in portfolio.values()]),
    }

    latest_token_prices = api.get_latest_token_prices()
    latest_token_supply = api.get_latest_token_supply()

    number_of_tokens = fetch_token_supply()

    row = [
        date,  # Date
        number_of_tokens,  # Token supply
        number_of_tokens - latest_token_supply,  # 12h change in token supply
        portfolio_value.get('USD'),  # Portfolio USD price
        portfolio_value.get('BTC'),  # Portfolio BTC price
        portfolio_value.get('ETH'),  # Portfolio ETH price
        portfolio_value.get('USD') / number_of_tokens,  # USD Token price
        portfolio_value.get('USD') / number_of_tokens / latest_token_prices[0] - 1,  # USD price 12h change
        portfolio_value.get('USD') / number_of_tokens / initial_token_usd_price - 1,  # USD price lifetime change
        portfolio_value.get('BTC') / number_of_tokens,  # USD Token price
        portfolio_value.get('BTC') / number_of_tokens / latest_token_prices[1] - 1,  # BTC price 12h change
        portfolio_value.get('BTC') / number_of_tokens / initial_token_btc_price - 1,  # BTC price lifetime change
        portfolio_value.get('ETH') / number_of_tokens,  # USD Token price
        portfolio_value.get('ETH') / number_of_tokens / latest_token_prices[2] - 1,  # ETH price 12h change
        portfolio_value.get('ETH') / number_of_tokens / initial_token_eth_price - 1,  # ETH price lifetime change
    ]
    api.add_daily_performance_row(row)

    return row


def update_table(config):
    api = SheetsAPI(sheets_id=config['sheets']['id'], secret_file=config['sheets']['secret_file'])
    date = time.strftime('%Y-%m-%d %H:%M %Z')
    balances = update_balances(api, config, date)

    prices = update_prices(api, date)

    portfolio = update_portfolio(api, date, balances, prices)

    update_daily_performance(api, date, portfolio)

if __name__ == "__main__":
    import tornado.options
    import yaml

    tornado.options.define(name='config',
                           default='configs/main.yml',
                           type=str,
                           help='Path to YAML config file')
    tornado.options.parse_command_line()

    config = yaml.load(open(tornado.options.options['config']))

    update_table(config)
