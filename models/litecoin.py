import aiohttp
import json
import logging

from .fetcher import Fetcher

logger = logging.getLogger(__name__)


class LitecoinAPI(Fetcher):
    _URL = 'http://ltc.blockr.io/api/v1/address/balance/{}'

    async def get_ltc_balance(self, loop, address, symbol='LTC', callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL.format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            if response.get('status') != 'success':
                logger.error('LTC request failed:', response)
                return
            balance = float(response.get('data').get('balance'))
            multisig_balance = float(response.get('data').get('balance_multisig'))
            amount = balance + multisig_balance
            if callback is not None:
                callback(symbol, amount)
        return symbol, amount
