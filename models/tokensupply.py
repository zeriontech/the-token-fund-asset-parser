import aiohttp
import json

from .fetcher import Fetcher


class TokenSupplyAPI(Fetcher):

    _URL = 'https://tkn.jwma.ru/api/stats'

    async def get_token_supply(self, loop, callback=None):
        async with aiohttp.ClientSession(loop=loop) as session:
            response = await self._fetch(session, self._URL)
            response = json.loads(response).get('count')
            amount = float(response)
            if callback is not None:
                callback(amount)
        return amount
