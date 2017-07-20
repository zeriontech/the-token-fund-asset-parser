import aiohttp
import json

from .fetcher import Fetcher


class DashAPI(Fetcher):

    _URL = 'https://api.blockcypher.com/v1/dash/main/addrs/{}'

    async def get_dash_balance(self, loop, address, symbol='DASH', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            balance = -1
            try:
                balance = response.get("final_balance") / 10 ** 8
            except TypeError as _:
                try:
                    err_mess = response.get("error")
                    print(err_mess)
                except Exception as _:
                    print("Something strange happened with Dash API.")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance