import aiohttp

from .fetcher import Fetcher
import json
import logging


class LitecoinAPI(Fetcher):

    # _URL = 'http://explorer.litecoin.net/chain/Litecoin/q/addressbalance/{}'
    _URL = 'https://api.blockcypher.com/v1/ltc/main/addrs/{}/balance'
    async def get_ltc_balance(self, loop, address, symbol='LTC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            try:
                response = json.loads(response)
                amount = response.get('final_balance') / 10**8
            except Exception:
                logging.error('Litecoin balance fetching error')
                return symbol, None
            if callback is not None:
                callback(symbol, amount)
        return symbol, amount
