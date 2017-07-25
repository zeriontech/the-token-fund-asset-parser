import aiohttp
from time import time
import json
from hashlib import sha256
import hmac

from .fetcher import Fetcher


class BitstampAPI(Fetcher):

    _URL = 'https://www.bitstamp.net/api/'
    _KEY = None
    _SECRET = None
    _CUSTOMER_ID = None

    def __init__(self, key, secret, customer_id):
        if key is None or secret is None:
            raise EnvironmentError("Bitstamp customer_id, key and secret must be specified in configs")
        self._KEY = key
        self._SECRET = secret
        self._CUSTOMER_ID = customer_id

    def _signature(self, nonce):
        message = nonce + self._CUSTOMER_ID + self._KEY
        return hmac.new(
            self._SECRET,
            msg=message,
            digestmod=sha256
        ).hexdigest().upper()

    async def get_balances(self, loop, symbols, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + 'balance'
            nonce = int(time())
            data = {
                'key': self._KEY,
                'signature': self._signature(nonce),
                "nonce": nonce
            }

            _response = await self._fetch_post(session=session, url=endpoint, data=data)
            if _response is None:
                raise Exception('bitstamp didn\'t response')
            response = json.loads(_response)
            if callback is not None:
                callback(response)
            return [response.get(symbol.lower(), 0) for symbol in symbols]
