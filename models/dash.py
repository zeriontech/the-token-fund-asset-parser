import aiohttp
import json
import logging

from .fetcher import Fetcher

logger = logging.getLogger(__name__)


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
                    logger.error("No balance:", err_mess)
                except Exception as _:
                    logger.error("Something strange happened with Dash API.")
            if callback is not None:
                callback(symbol, balance)
        return symbol, balance
