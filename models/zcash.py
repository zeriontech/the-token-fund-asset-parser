import aiohttp
import json
import logging

from .fetcher import Fetcher

logger = logging.getLogger(__name__)


class ZCashAPI(Fetcher):

    _URL = 'https://api.zcha.in/v2/mainnet/accounts/{}'

    async def get_zcash_balance(self, loop, address, symbol='ZEC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)

            try:
                balance = float(response.get("balance", -1))
            except AttributeError as _:
                logger.error("Wrong address provided")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance
