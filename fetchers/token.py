import asyncio

from models.tokensupply import TokenSupplyAPI


def fetch_token_supply():

    token_supply_api = TokenSupplyAPI()

    loop = asyncio.get_event_loop()

    coroutine = token_supply_api.get_token_supply(loop)
    number_of_tokens = loop.run_until_complete(coroutine)

    return number_of_tokens
