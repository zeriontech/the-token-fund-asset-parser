import aiohttp
import json

from .fetcher import Fetcher


class EtcChainAPI(Fetcher):

    _URL = 'https://etcchain.com/api/v1/getAddressBalance?address={}'

    async def get_etc_balance(self, loop, address, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response).get('balance')
            amount = float(response) / 10 ** 18  # from wei to ETC
            callback('ETC', amount)
