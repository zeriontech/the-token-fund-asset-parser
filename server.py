#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.options
import yaml
import json
import bugsnag
import os
from bugsnag.tornado import BugsnagRequestHandler
from update_table import update_table
from fetchers.token import fetch_token_supply
from fetchers.portfolio import fetch_portfolio


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
                                   'data': e,
                                   }, indent=4))


class UpdateTableHandler(BaseHandler):
    def endpoint(self, _config):
        return update_table(_config)


class FetchTokenHandler(BaseHandler):
    def endpoint(self, _config):
        from models.google_sheets_api import SheetsAPI
        from fetchers.prices import fetch_prices
        from fetchers.balances import fetch_balances

        api = SheetsAPI(sheets_id=_config['sheets']['id'], secret_file=_config['sheets']['secret_file'])

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
            'USD': sum([value.get('USD') for value in portfolio.values()]),
            'BTC': sum([value.get('USD') for value in portfolio.values()]),
            'ETH': sum([value.get('USD') for value in portfolio.values()]),
            'token_supply': token_supply
        }
        return portfolio_value


def make_app(config):
    return tornado.web.Application([
        (r"/update_table", UpdateTableHandler, {"config": config}),
        (r"/token_price", FetchTokenHandler, {"config": config}),
    ])

if __name__ == "__main__":
    tornado.options.define(name='config',
                           default='configs/main.yml',
                           type=str,
                           help='Path to YAML config file')
    tornado.options.parse_command_line()

    config = yaml.load(open(tornado.options.options['config']))

    bugsnag.configure(
        api_key=config['bugsnag']['api_key'],
        project_root=os.getcwd(),
    )
    app = make_app(config)
    app.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.current().start()
