import base64
import hashlib
import hmac
import json
import urllib.parse
from time import time

import aiohttp

from .fetcher import Fetcher


class KrakenAPI(Fetcher):

    _URL = 'https://api.kraken.com'
    _KEY = None
    _SECRET = None

    def __init__(self, key, secret):
        if key is None or secret is None:
            raise EnvironmentError("Kraken key and secret must be specified in configs")
        self._KEY = key
        self._SECRET = secret

    async def get_balances(self, loop, symbols, callback=None):
        urlpath = '/0/private/Balance'
        async with aiohttp.ClientSession(loop=loop) as session:
            nonce = int(1000 * time())

            data = {
                "nonce": nonce,
            }

            post_data = urllib.parse.urlencode(data)

            # Unicode-objects must be encoded before hashing
            encoded = (str(nonce) + post_data).encode()
            message = urlpath.encode() + hashlib.sha256(encoded).digest()

            signature = hmac.new(base64.b64decode(self._SECRET), message, hashlib.sha512)
            sign = base64.b64encode(signature.digest())

            headers = {
                'API-Sign': sign.decode(),
                'API-Key': self._KEY
            }

            response = await self._fetch_post(session=session, url=self._URL + urlpath, data=data, headers=headers)
            if response is None: raise Exception('kraken didn\'t response')
            result = json.loads(response).get('result', {})
            if callback is not None:
                callback(result)
            balances = []
            for symbol in symbols:
                prefix = 'Z' if symbol == 'EUR' or symbol == 'USD' else 'X'
                if symbol == 'BTC': symbol = 'XBT'
                if symbol == 'EOS': prefix = ''  # no idea why EOS doesn't have 'X' prefix
                balance = float(result.get(prefix + symbol, '0.0'))
                if symbol == 'XBT': symbol = 'BTC'
                balances.append((symbol, balance))
            return balances