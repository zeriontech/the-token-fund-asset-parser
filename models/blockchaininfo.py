import aiohttp
import json

from .fetcher import Fetcher


class BlockChainInfoAPI(Fetcher):

    _URL = 'https://blockchain.info/ru/address/{}?format=json'

    async def get_btc_balance(self, loop, address, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response).get('final_balance')
            amount = float(response) / 10 ** 8  # from satoshi to BTC
            callback('BTC', amount)
