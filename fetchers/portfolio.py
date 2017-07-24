def fetch_portfolio(balances=None, prices=None):
    # Fetches portfolio
    whole_usd_price = sum([balances.get(symbol) * prices.get(symbol)['USD']
                           for symbol in balances.keys()
                           if balances.get(symbol, 0)
                           and prices.get(symbol, {'USD': 0})['USD'] > 0])

    portfolio = {}
    for symbol in balances.keys():
        if balances.get(symbol, 0) > 0:
            portfolio[symbol] = {
                'USD': balances.get(symbol) * float(prices.get(symbol).get('USD')),
                'BTC': balances.get(symbol) * float(prices.get(symbol).get('BTC')),
                'ETH': balances.get(symbol) * float(prices.get(symbol).get('BTC')) / float(
                    prices.get('ETH').get('BTC')),
                'share': balances.get(symbol) * float(prices.get(symbol).get('USD')) / whole_usd_price,
            }
    return portfolio
