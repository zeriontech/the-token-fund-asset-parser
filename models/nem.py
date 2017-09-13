import aiohttp
import json

from .fetcher import Fetcher


class NemAPI(Fetcher):

    _URL = 'http://chain.nem.ninja/api3/account?address={}'

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
                for _balance in response.get("raw").get('balance'):
                    balance += _balance.get('sum', 0)
            except TypeError as _:
                print(response.get("error", 'Unknown NEM API error'))
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance / 10 ** self._decimals[symbol]
