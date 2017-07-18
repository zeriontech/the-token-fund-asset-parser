import aiohttp
import json

from .fetcher import Fetcher


class ZCashAPI(Fetcher):

    _URL = 'https://api.zcha.in/v2/mainnet/accounts/{}'

    async def get_zcash_balance(self, loop, address, symbol='ZEC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            try:
                balance = float(response.get("balance", -1))
            except AttributeError as _:
                print("You provided wrong address!")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance