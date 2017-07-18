import aiohttp
from time import time
import json
from hashlib import sha512
import hmac

from .fetcher import Fetcher


class PoloniexAPI(Fetcher):

    _URL = 'https://poloniex.com/tradingApi'
    _KEY = None
    _SECRET = None

    def __init__(self, key, secret):
        if key is None or secret is None:
            raise EnvironmentError("Poloniex key and secret must be specified in configs")
        self._KEY = key
        self._SECRET = secret

    async def get_balances(self, loop, symbols, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            data = {
                "nonce": int(time()),
                "command": "returnCompleteBalances"
            }
            tosign = "&".join([i + '=' + str(data[i]) for i in data])
            sign = hmac.new(str.encode(self._SECRET), str.encode(tosign), sha512)
            headers = {
                'Sign': sign.hexdigest(),
                'Key': self._KEY
            }

            _response = await self._fetch_post(session=session, url=self._URL, data=data, headers=headers)
            if _response is None: raise Exception('poloniex didn\'t response')
            response = json.loads(_response)
            if callback is not None:
                callback(response)
            balances = []
            for symbol in symbols:
                _balance = response.get(symbol, {'available': '0.00000000', 'btcValue': '0.00000000',
                                                         'onOrders': '0.00000000'})
                balance = float(_balance['onOrders']) + float(_balance['available'])
                balances.append((symbol, balance))
            return balances
