import aiohttp
import binascii
from time import time
import json
from hashlib import sha256
import hmac

from .fetcher import Fetcher


class BitstampAPI(Fetcher):

    _URL = 'https://www.bitstamp.net/api/v2/'
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
        message = str(nonce) + self._CUSTOMER_ID + self._KEY
        return hmac.new(
            key=self._SECRET.encode(),
            msg=message.encode(),
            digestmod=sha256
        ).hexdigest().upper()

    async def get_balances(self, loop, symbols, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            nonce = int(time())
            endpoint = self._URL + 'balance/'
            params = {
                'key': self._KEY,
                'signature': self._signature(nonce),
                'nonce': nonce
            }
            _response = await self._fetch_post(session=session, url=endpoint, data=params)
            if _response is None:
                raise Exception('bitstamp didn\'t response')
            response = json.loads(_response)
            balances = [(symbol, float(response.get(symbol.lower() + '_balance', 0))) for symbol in symbols]
            if callback is not None:
                callback(balances)
            return balances
