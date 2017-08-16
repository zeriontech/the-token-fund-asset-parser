import asyncio

from models.coinmarketcap import CoinmarketcapAPI
from models.european_cb import EuropeanCBAPI

coinmarketcap_api = CoinmarketcapAPI(900)
europeanCB_api = EuropeanCBAPI()


def fetch_prices(assets):
    loop = asyncio.get_event_loop()

    futures = [coinmarketcap_api.request_assets(loop, assets),
               europeanCB_api.get_eur_usd_exchange_rate(loop)]

    _prices, euro_price = loop.run_until_complete(asyncio.gather(*futures))
    #
    # here all async requests already finished
    #

    prices = {}

    for asset in _prices:
        if asset.name == 'BatCoin':
            continue  # Bad coin
        if asset.name == 'iCoin':
            continue  # to avoid colision with Iconomi
        if asset.symbol == 'TIME':
            asset.symbol = 'LH'
        if asset.symbol in assets:
            prices[asset.symbol] = {'USD': asset.price_USD, 'BTC': asset.price_BTC}
    prices['EUR'] = {'USD': float(euro_price), 'BTC': float(euro_price) / prices.get('BTC').get('USD')}
    prices['USD'] = {'USD': 1.0, 'BTC': 1.0 / prices.get('BTC').get('USD')}
    return prices
