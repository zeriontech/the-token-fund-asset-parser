#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.options
import yaml
import json
import bugsnag
import os
import logging
from bugsnag.tornado import BugsnagRequestHandler
from update_table import update_table
from fetchers.token import fetch_token_supply
from fetchers.portfolio import fetch_portfolio

logger = logging.getLogger(__name__)

class BaseHandler(BugsnagRequestHandler):
    config = None

    def initialize(self, *args, **kwargs):
        self.config = kwargs.pop('config')
        super(BaseHandler, self).initialize(*args, **kwargs)

    def endpoint(self, _config):
        raise NotImplementedError()

    def get(self):
        self.set_header('Content-Type', 'application/json')
        try:
            result = self.endpoint(config)
            self.write(json.dumps({'status': 'OK',
                                   'data': result,
                                   }, indent=4))
        except Exception as e:
            self.set_status(500)
            bugsnag.notify(e)
            self.write(json.dumps({'status': 'ERROR',
                                   'data': str(e),
                                   }, indent=4))
            import traceback
            logger.error(traceback.format_exc())


class UpdateTableHandler(BaseHandler):
    def endpoint(self, _config):
        return update_table(_config)


class FetchTokenHandler(BaseHandler):
    def endpoint(self, _config):
        from models.google_sheets_api import SheetsAPI
        from fetchers.prices import fetch_prices
        from fetchers.balances import fetch_balances

        api = SheetsAPI(_config['sheets'])

        wallet = api.read_addresses()
        balances = fetch_balances(config, wallet)

        assets = api.read_prices_assets()
        last_prices = api.read_last_prices()

        prices = fetch_prices(assets[1])
        for symbol, price in last_prices.items():
            prices.setdefault(symbol, price)
        portfolio = fetch_portfolio(balances, prices)
        token_supply = fetch_token_supply()
        portfolio_value = {
            'USD': sum([value.get('USD') for value in portfolio.values()]) / token_supply,
            'BTC': sum([value.get('BTC') for value in portfolio.values()]) / token_supply,
            'ETH': sum([value.get('ETH') for value in portfolio.values()]) / token_supply,
            'token_supply': token_supply,
            'balances': balances
        }
        return portfolio_value


def make_app(config):
    return tornado.web.Application([
        (r"/update_table", UpdateTableHandler, {"config": config}),
        (r"/token_price", FetchTokenHandler, {"config": config}),
    ])

if __name__ == "__main__":
    tornado.options.define(name='config',
                           default=None,
                           type=str,
                           help='Path to YAML config file')
    tornado.options.parse_command_line()

    if tornado.options.options['config'] is not None:
        config = yaml.load(open(tornado.options.options['config']))
    else:
        from config.env import config_from_env
        config = config_from_env()

    bugsnag.configure(
        api_key=config['bugsnag']['api_key'],
        project_root=os.getcwd(),
    )
    app = make_app(config)
    app.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.current().start()
