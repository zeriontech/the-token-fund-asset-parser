import socketIO_client
import json
import logging

from requests.exceptions import ConnectionError

from .fetcher import Fetcher

logger = logging.getLogger(__name__)

class ByteballAPI:
    _decimals = {
    "GBYTE" : 9
    }

    _URL = "https://explorer.byteball.org"

    def __init__(self, timeout=10):
        self._timeout = timeout

    async def get_balance(self, loop, address, token, callback=None):
        io = socketIO_client.SocketIO(self._URL)
        future = loop.create_future()
        io.once('addressInfo', lambda _data: future.set_result(_data))
        io.emit('start', {'type': "address", 'address': address})
        elapsed = 0
        while not future.done():
            try:
                io.wait(seconds=1)
                elapsed += 1
                if elapsed == self._timeout:
                    raise TimeoutError
            except Exception as e:
                logger.error('Could not fetch byteball balance:', e)
                return
        response = await future
        decimals = self._decimals.get(token, 0)
        amount = float(response.get('objBalance').get('bytes')) / (10 ** decimals)
        if callback is not None:
            callback(token, amount)
        return token, amount
