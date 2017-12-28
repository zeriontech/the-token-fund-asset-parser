import aiohttp
from time import time
import json
from hashlib import sha256
import hmac

from .fetcher import Fetcher


class BinanceAPI(Fetcher):

    _URL = 'https://api.binance.com/api/v3/'
    _KEY = None
    _SECRET = None

    def __init__(self, key, secret):
        if key is None or secret is None:
            raise EnvironmentError("Binance key and secret must be specified in configs")
        self._KEY = key
        self._SECRET = secret

    def _signature(self, query):
        message = query
        return hmac.new(
            key=self._SECRET.encode(),
            msg=message.encode(),
            digestmod=sha256
        ).hexdigest().upper()

    async def get_balances(self, loop, symbols, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            nonce = int(time() * 1000)
            query = 'timestamp={}&recvWindow={}'.format(nonce, 30000)
            endpoint = self._URL + 'account?' + query
            headers = {
                'Accept': 'application/json',
                'X-MBX-APIKEY': self._KEY
            }
            signature = self._signature(query)
            endpoint += '&signature={}'.format(signature)
            _response = await self._fetch(session=session, url=endpoint, headers=headers)
            balances = json.loads(_response).get('balances', [])
            result = []
            for balance in balances:
                if balance['asset'] in symbols:
                    result.append(
                        (balance['asset'].lower(),
                         float(balance.get('locked', 0)) + float(balance.get('free', 0)))
                    )
            if callback is not None:
                callback(result)
            return result
