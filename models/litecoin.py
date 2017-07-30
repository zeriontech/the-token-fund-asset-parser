import aiohttp

from .fetcher import Fetcher
import logging


class LitecoinAPI(Fetcher):

    _URL = 'http://explorer.litecoin.net/chain/Litecoin/q/addressbalance/{}'

    async def get_ltc_balance(self, loop, address, symbol='LTC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            try:
                amount = float(response)
            except Exception:
                logging.error('Litecoin balance fetching error')
                return
            if callback is not None:
                callback(symbol, amount)
        return symbol, amount
