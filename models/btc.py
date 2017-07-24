import aiohttp
import json

from .fetcher import Fetcher


class BtcAPI(Fetcher):

    _URL = 'https://blockexplorer.com/api/addr/{}/utxo?noCache=1'

    async def get_btc_balance(self, loop, address, symbol='BTC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            balance = sum([utxo['amount'] for utxo in response])
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance
