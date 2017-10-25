import aiohttp
import json

from .fetcher import Fetcher


class NemAPI(Fetcher):

    _URL = 'http://62.75.251.134:7890/account/get?address={}'

    _decimals = {
        'XEM': 6
    }

    async def get_nem_balance(self, loop, address, symbol='XEM', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            balance = 0
            try:
                balance = response.get('account').get('balance')
            except TypeError as _:
                print(response.get("error", 'Unknown NEM API error'))
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance / 10 ** self._decimals[symbol]
