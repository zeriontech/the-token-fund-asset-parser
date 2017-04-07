import aiohttp
import json

from .fetcher import Fetcher


class EtherscanAPI(Fetcher):

    _URL = 'https://api.etherscan.io/api?'

    async def get_ether_balance(self, loop, address, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=balance&address={}".format(address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response).get('result')
            amount = float(response) / 10 ** 18  # from wei to ETH
            callback('ETH', amount)

    async def get_tokens_balance(self, loop, address, token, decimals, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=tokenbalance&address={}&tokenname={}".format(address, token)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            message = response.get('message')
            if message == 'NOTOK':
                raise ValueError("{} doesn't exist".format(token))
            amount = float(response.get('result')) / (10 ** decimals)
            callback(token, amount)

    async def get_tokens_balance_by_address(self, loop, address, token, contract_address, decimals, callback):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=tokenbalance&contractaddress={}&address={}".format(contract_address, address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            message = response.get('message')
            if message == 'NOTOK':
                print("{} doesn't exist".format(token))
                return
            amount = float(response.get('result')) / (10 ** decimals)
            callback(token, amount)

    async def get_total_supply(self, loop, contract_address, callback):
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=tokensupply&contractaddress={}".format(contract_address)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            message = response.get('message')
            if message == 'NOTOK':
                print("can't read total supply from contract {}".format(contract_address))
                return
            amount = float(response.get('result'))
            callback(amount)
