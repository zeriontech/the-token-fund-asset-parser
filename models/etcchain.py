import aiohttp
import json

from .fetcher import Fetcher


class EtcChainAPI(Fetcher):

    _URL = 'https://etcchain.com/api/v1/getAddressBalance?address={}'

    async def get_etc_balance(self, loop, address, symbol='ETC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            try:
                balance = float(response.get('balance', -1))
            except TypeError as _:
                print("You provided wrong address!")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance
