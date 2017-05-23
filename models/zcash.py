import aiohttp
import json

from .fetcher import Fetcher


class ZCashAPI(Fetcher):

    _URL = 'https://api.zcha.in/v2/mainnet/accounts/{}'

    async def get_zcash_balance(self, loop, address, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            balance = -1

            try:
                balance = float(response.get("balance"))
            except AttributeError as _:
                print("You provided wrong address!")
            callback('ZEC', balance)
