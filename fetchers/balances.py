import asyncio

from models.etherscan import EtherscanAPI
from models.blockchaininfo import BlockChainInfoAPI
from models.btc import BtcAPI
from models.etcchain import EtcChainAPI
from models.waves import WavesAPI
from models.poloniex import PoloniexAPI
from models.kraken import KrakenAPI
from models.bitstamp import BitstampAPI
from models.litecoin import LitecoinAPI
from models.zcash import ZCashAPI
from models.gamecredits import GameCreditsAPI
from models.dash import DashAPI
from models.ripple import RippleAPI
from models.maidcoin import MaidCoinAPI
from models.byteball import ByteballAPI
from models.nem import NemAPI

ethAPI = EtherscanAPI()
btcAPI = BlockChainInfoAPI()
#  btcAPI = BtcAPI()
etcAPI = EtcChainAPI()
wavesAPI = WavesAPI()
gameCreditsAPI = GameCreditsAPI()
litecoinAPI = LitecoinAPI()
zcashAPI = ZCashAPI()
rippleAPI = RippleAPI()
dashAPI = DashAPI()
maidAPI = MaidCoinAPI()
byteballAPI = ByteballAPI()
nemAPI = NemAPI()

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
    'STA': wavesAPI.get_token_balance,
    'GBYTE': byteballAPI.get_balance,
    'XEM': nemAPI.get_nem_balance,
}


def replace(symbol):
    if symbol == 'ICONOMI':
        return 'ICN'
    if symbol == 'GOLEM':
        return 'GNT'
    return symbol


def fetch_balances(config, wallet):
    poloniex_api = PoloniexAPI(
        key=config['poloniex']['key'],
        secret=config['poloniex']['secret']
    )
    kraken_api = KrakenAPI(
        key=config['kraken']['key'],
        secret=config['kraken']['secret']
    )
    bitstamp_api = BitstampAPI(
        customer_id=config['bitstamp']['customer_id'],
        key=config['bitstamp']['key'],
        secret=config['bitstamp']['secret']
    )

    poloniex_assets = set()
    kraken_assets = set()
    bitstamp_assets = set()

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
        if place == "Bitstamp":
            bitstamp_assets.add(symbol)
            continue
        if place == "Address":
            balance_func = balance_apis.get(symbol, ethAPI.get_balance)
            future = balance_func(loop, address, symbol)
            asset_futures.append(future)
            continue
        print('Unknown place!')

    asset_futures.append(poloniex_api.get_balances(loop, poloniex_assets))
    asset_futures.append(kraken_api.get_balances(loop, kraken_assets))
    asset_futures.append(bitstamp_api.get_balances(loop, bitstamp_assets))

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
