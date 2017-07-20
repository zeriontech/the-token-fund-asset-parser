import asyncio

from models.etherscan import EtherscanAPI
from models.blockchaininfo import BlockChainInfoAPI
from models.etcchain import EtcChainAPI
from models.waves import WavesAPI
from models.poloniex import PoloniexAPI
from models.kraken import KrakenAPI
from models.litecoin import LitecoinAPI
from models.zcash import ZCashAPI
from models.gamecredits import GameCreditsAPI
from models.dash import DashAPI
from models.ripple import RippleAPI
from models.maidcoin import MaidCoinAPI

ethAPI = EtherscanAPI()
btcAPI = BlockChainInfoAPI()
etcAPI = EtcChainAPI()
wavesAPI = WavesAPI()
gameCreditsAPI = GameCreditsAPI()
litecoinAPI = LitecoinAPI()
zcashAPI = ZCashAPI()
rippleAPI = RippleAPI()
dashAPI = DashAPI()
maidAPI = MaidCoinAPI()

balance_apis = {
    'BTC': btcAPI.get_btc_balance,
    'ETC': etcAPI.get_etc_balance,
    'WAVES': wavesAPI.get_waves_balance,
    'GAME': gameCreditsAPI.get_gamecredits_balance,
    'LTC': litecoinAPI.get_ltc_balance,
    'ZEC': zcashAPI.get_zcash_balance,
    'XRP': rippleAPI.get_ripple_balance,
    'DASH': dashAPI.get_dash_balance,
    'MAID': maidAPI.get_maid_balance,
}


def replace(symbol):
    if symbol == 'ICONOMI':
        return 'ICN'
    if symbol == 'GOLEM':
        return 'GNT'
    return symbol


def fetch_balances(config, wallet):
    poloniexAPI = PoloniexAPI(key=config['poloniex']['key'], secret=config['poloniex']['secret'])
    krakenAPI = KrakenAPI(key=config['kraken']['key'], secret=config['kraken']['secret'])

    poloniex_assets = set()
    kraken_assets = set()

    balances = {}

    loop = asyncio.get_event_loop()

    asset_futures = []
    for (symbol, place, address) in wallet:
        if place == 'Static':
            balances[replace(symbol)] = balances.get(replace(symbol), 0) + float(address)
            continue
        if place == "Poloniex":
            poloniex_assets.add(symbol)
            continue
        if place == "Kraken":
            kraken_assets.add(symbol)
            continue
        else:
            balance_func = balance_apis.get(symbol, ethAPI.get_balance)
            future = balance_func(loop, address, symbol)
        asset_futures.append(future)

    asset_futures.append(poloniexAPI.get_balances(loop, poloniex_assets))
    asset_futures.append(krakenAPI.get_balances(loop, kraken_assets))

    results = loop.run_until_complete(asyncio.gather(*asset_futures))

    # here all async requests already finished

    for result in results:
        if type(result) is list:
            for balance in result:
                symbol, amount = balance
                balances[replace(symbol)] = balances.get(replace(symbol), 0) + amount
        else:
            symbol, amount = result
            balances[replace(symbol)] = balances.get(replace(symbol), 0) + amount

    return balances
