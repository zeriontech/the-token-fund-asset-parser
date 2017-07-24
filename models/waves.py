import aiohttp
import json

from .fetcher import Fetcher


class WavesAPI(Fetcher):

    _decimals = {
        'STA': 2,
    }

    _token_ids = {
        'STA': '3SdrmU1GGZRiZz12MrMcfUz4JksTzvcU25cLFXpZy1qz',
    }

    _URL = 'https://nodes.wavesnodes.com/'

    async def get_waves_balance(self, loop, address, symbol='WAVES', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + 'addresses/balance/{}'.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response).get('balance')
            amount = float(response) / 10 ** 8
            if callback is not None:
                callback(symbol, amount)
        return symbol, amount

    async def get_token_balance(self, loop, address, token, token_id=None, decimals=None, callback=None):
        if address is None:
            raise ValueError("address must be specified")
        if decimals is None:
            decimals = self._decimals.get(token, 0)
        if token_id is None:
            token_id = self._token_ids.get(token)
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + 'assets/balance/{}/{}'.format(address, token_id)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            amount = float(response.get('balance')) / (10 ** decimals)
            if callback is not None:
                callback(token, amount)
            return token, amount
