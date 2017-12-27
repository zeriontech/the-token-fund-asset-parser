import aiohttp
import json

from time import sleep
from .fetcher import Fetcher


class EtherscanAPI(Fetcher):

    _decimals = {
        'BCAP': 0,
        'HMQ': 8,
        'LH': 8,
        'STORJ': 8,
        'ANT': 18,
        'BAT': 18,
        'GNT': 18,
        'ICONOMI': 18,
        'MLN': 18,
        'REP': 18,
        'SNM': 18,
        'SNT': 18,
        'CVC': 8,
        'AE': 18,
        'QTUM': 18,
        'OMG': 18,
        'PAY': 18,
        'REQ': 18,
        'CND': 18
    }

    _contracts = {
        'HMQ': '0xcbcc0f036ed4788f63fc0fee32873d6a7487b908',
        'LH': '0x6531f133e6DeeBe7F2dcE5A0441aA7ef330B4e53',
        'GNT': '0xa74476443119A942dE498590Fe1f2454d7D4aC0d',
        'REP': '0x48c80F1f4D53D5951e5D5438B54Cba84f29F32a5',
        'MLN': '0xBEB9eF514a379B997e0798FDcC901Ee474B6D9A1',
        'ANT': '0x960b236A07cf122663c4303350609A66A7B288C0',
        'BCAP': '0xff3519eeeea3e76f1f699ccce5e23ee0bdda41ac',
        'STORJ': '0xb64ef51c888972c908cfacf59b47c1afbc0ab8ac',
        'SNT': '0x744d70FDBE2Ba4CF95131626614a1763DF805B9E',
        'BAT': '0x0D8775F648430679A709E98d2b0Cb6250d2887EF',
        'SNM': '0x983F6d60db79ea8cA4eB9968C6aFf8cfA04B3c63',
        'CVC': '0x41e5560054824ea6b0732e656e3ad64e20e94e45',
        'AE': '0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d',
        'QTUM': '0x9a642d6b3368ddc662CA244bAdf32cDA716005BC',
        'OMG': '0xd26114cd6EE289AccF82350c8d8487fedB8A0C07',
        'PAY': '0xB97048628DB6B661D4C2aA833e95Dbe1A905B280',
        'REQ': '0x8f8221afbb33998d8584a2b05749ba73c37a938a',
        'CND': '0xd4c435f5b09f855c3317c8524cb1f586e42795fa',
    }

    _URL = 'https://api.etherscan.io/api?apikey=YDXSHGZR3X169ZVGGEXKDPDBEUKAT5MJW2&'

    async def get_ether_balance(self, loop, address, callback=None):
        if address is None:
            raise ValueError("address must be specified")
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=balance&address={}".format(address)
            response = 0
            for i in range(5):
                response = await self._fetch(session, endpoint)
                try:
                    response = json.loads(response).get('result')
                    break
                except Exception:
                    sleep(1)
            amount = float(response) / 10 ** 18  # from wei to ETH
            if callback is not None:
                callback('ETH', amount)
        return 'ETH', amount

    async def get_tokens_balance(self, loop, address, token, decimals=None, callback=None):
        if address is None:
            raise ValueError("address must be specified")
        if decimals is None:
            decimals = self._decimals.get(token, 0)
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=tokenbalance&address={}&tokenname={}".format(address, token)
            response = await self._fetch(session, endpoint)
            response = json.loads(response)
            message = response.get('message')
            if message == 'NOTOK':
                raise ValueError("{} doesn't exist".format(token))
            amount = float(response.get('result')) / (10 ** decimals)
            if callback is not None:
                callback(token, amount)
            return token, amount

    async def get_tokens_balance_by_address(self, loop, address, token, contract_address=None, decimals=None, callback=None):
        if address is None:
            raise ValueError("address must be specified")
        if decimals is None:
            decimals = self._decimals.get(token, 0)
        if contract_address is None:
            contract_address = self._contracts.get(token)
        async with aiohttp.ClientSession(loop=loop) as session:
            endpoint = self._URL + "module=account&action=tokenbalance&contractaddress={}&address={}".format(
                contract_address, address)
            response = {}
            for i in range(5):
                response = await self._fetch(session, endpoint)
                try:
                    response = json.loads(response)
                    break
                except Exception:
                    sleep(1)
            message = response.get('message')
            if message == 'NOTOK':
                print("{} doesn't exist".format(token))
                return
            if response.get('result') is None:
                print('Etherscan didn\'t return the balance for', token)
                return token, 0
            amount = float(response.get('result')) / (10 ** decimals)
            if callback is not None:
                callback(token, amount)
            return token, amount

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

    async def get_balance(self, loop, address, token):
        if token == 'ICN':
            token = 'ICONOMI'
        if token == 'ETH':
            return await self.get_ether_balance(
                loop=loop,
                address=address
            )
        elif token in self._contracts.keys():
            return await self.get_tokens_balance_by_address(
                loop=loop,
                address=address,
                token=token,
                decimals=self._decimals.get(token, 0),
                contract_address=self._contracts.get(token)
            )
        else:
            return await self.get_tokens_balance(
                loop=loop,
                address=address,
                token=token,
                decimals=self._decimals.get(token, 0)
            )
