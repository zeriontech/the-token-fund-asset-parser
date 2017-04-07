import asyncio
from datetime import datetime

from models.google_sheets_api import SheetsAPI

from models.etherscan import EtherscanAPI
from models.blockchaininfo import BlockChainInfoAPI
from models.etcchain import EtcChainAPI
from models.waves import WavesAPI
from models.poloniex import PoloniexAPI
from models.gamecredits import GameCreditsAPI

from configs import poloniex_keys

api = SheetsAPI()
ethAPI = EtherscanAPI()
btcAPI = BlockChainInfoAPI()
etcAPI = EtcChainAPI()
wavesAPI = WavesAPI()
gameCreditsAPI = GameCreditsAPI()
poloniexAPI = PoloniexAPI(poloniex_keys.KEY, poloniex_keys.SECRET)

addresses = {}
balances = {}

poloniex_assets = set()


def replace(symbol):
    if symbol == 'ICONOMI':
        return 'ICN'
    if symbol == 'GOLEM':
        return 'GNT'
    return symbol


def on_amount_received(symbol, amount):
    balances[replace(symbol)] = balances.get(replace(symbol), 0) + amount


def on_poloniex_balances_received(poloniex_balances):
    for asset in poloniex_assets:
        _balance = poloniex_balances.get(asset, {'available': '0.00000000', 'btcValue': '0.00000000', 'onOrders': '0.00000000'})
        balance = float(_balance['onOrders']) + float(_balance['available'])
        balances[replace(asset)] = balances.get(replace(asset), 0) + balance


def fetch_balances():
    global balances, addresses

    balances = {}
    # read addresses from the spreadsheet
    addresses = api.read_addresses()

    loop = asyncio.get_event_loop()

    asset_futures = []
    for (symbol, place, address) in addresses:
        if place == 'Static':
            balances[replace(symbol)] = balances.get(replace(symbol), 0) + float(address)
            continue
        if address == "Poloniex":
            poloniex_assets.add(symbol)
            continue
        if symbol == "ETH":
            future = ethAPI.get_ether_balance(loop,
                address=address,
                callback=on_amount_received)
        elif symbol == "BTC":
            future = btcAPI.get_btc_balance(loop,
                address=address,
                callback=on_amount_received)
        elif symbol == "ICN":
            future = ethAPI.get_tokens_balance(loop,
                address=address,
                token='ICONOMI',
                decimals=18,
                callback=on_amount_received)
        elif symbol == 'LH':
            future = ethAPI.get_tokens_balance_by_address(loop,
                address=address,
                token='LH',
                contract_address='0x6531f133e6DeeBe7F2dcE5A0441aA7ef330B4e53',
                decimals=8,
                callback=on_amount_received)
        elif symbol == 'GNT':
            future = ethAPI.get_tokens_balance_by_address(loop,
                address=address,
                token='GNT',
                contract_address='0xa74476443119A942dE498590Fe1f2454d7D4aC0d',
                decimals=18,
                callback=on_amount_received)
        elif symbol == "ETC":
            future = etcAPI.get_etc_balance(loop,
                address=address,
                callback=on_amount_received)
        elif symbol == "WAVES":
            future = wavesAPI.get_waves_balance(loop,
                address=address,
                callback=on_amount_received)
        elif symbol == "GAME":
            future = gameCreditsAPI.get_gamecredits_balance(loop,
                address=address,
                callback=on_amount_received)
        asset_futures.append(future)

    asset_futures.append(poloniexAPI.get_balances(loop, callback=on_poloniex_balances_received))
    loop.run_until_complete(asyncio.gather(*asset_futures))
    #
    # here all async requests already finished
    #

    asset_names, asset_symbols = api.read_balances_assets()

    # compose new line
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    row = [date]

    for symbol in asset_symbols:
        row.append(balances.get(symbol, ''))
    api.add_balances_row(row)
    return balances

if __name__ == '__main__':
    fetch_balances()
