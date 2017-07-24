import aiohttp
import json
import logging

from .fetcher import Fetcher

logger = logging.getLogger(__name__)


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
                logger.error("Wrong address provided")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance
