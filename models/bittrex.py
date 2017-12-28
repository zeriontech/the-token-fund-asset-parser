import aiohttp
from time import time
import json
from hashlib import sha512
import hmac

from .fetcher import Fetcher


class BittrexAPI(Fetcher):
    _URL = 'https://bittrex.com/api/v1.1/'
    _KEY = None
    _SECRET = None

    def __init__(self, key, secret):
        if key is None or secret is None:
            raise EnvironmentError("Bittrex key and secret must be specified in configs")
        self._KEY = key
        self._SECRET = secret

    def _signature(self, query):
        message = query
        return hmac.new(
            key=self._SECRET.encode(),
            msg=message.encode(),
            digestmod=sha512
        ).hexdigest().upper()

    async def get_balances(self, loop, symbols, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            nonce = int(time())
            endpoint = self._URL + \
                       'account/getbalances?apikey={}&nonce={}'.format(self._KEY, nonce)
            signature = self._signature(endpoint)
            headers = {
                'apisign': signature
            }
            _response = await self._fetch(session=session, url=endpoint, headers=headers)
            balances = json.loads(_response).get('result', [])
            result = []
            for balance in balances:
                if balance['Currency'] in symbols:
                    result.append(
                        (balance['Currency'],
                         float(balance.get('Balance', 0)))
                    )
            if callback is not None:
                callback(result)
            return result
