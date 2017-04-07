import aiohttp
import json

from .fetcher import Fetcher


class WavesAPI(Fetcher):

    _URL = 'https://nodes.wavesnodes.com/addresses/balance/{}'

    async def get_waves_balance(self, loop, address, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response).get('balance')
            amount = float(response) / 10 ** 8
            callback('WAVES', amount)
