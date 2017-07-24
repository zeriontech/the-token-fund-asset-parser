import httplib2
import logging

from apiclient import discovery

logger = logging.getLogger(__name__)


class SheetsAPI:

    _SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    _CLIENT_SECRET_FILE = 'config/client_secret.json'
    _DISCOVERY_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    _PRICES_SHEET_NAME = 'Prices'
    _BALANCES_SHEET_NAME = 'Balances'
    _ADDRESSES_SHEET_NAME = 'Fund addresses'
    _PORTFOLIO_SHEET_NAME = 'Portfolio'
    # _PERFORMANCE_SHEET_NAME = 'Performance'
    _DAILY_PERFORMANCE_SHEET_NAME = 'Performance'
    _sheet_id = {
        _PRICES_SHEET_NAME: 348001345,
        _BALANCES_SHEET_NAME: 631390300,
        _ADDRESSES_SHEET_NAME: 719453274,
        _PORTFOLIO_SHEET_NAME: 1832139817,
        # _PERFORMANCE_SHEET_NAME: 2025694980,
        _DAILY_PERFORMANCE_SHEET_NAME: 0
    }
    _title_height = {
        _PRICES_SHEET_NAME: 2,
        _BALANCES_SHEET_NAME: 2,
        _ADDRESSES_SHEET_NAME: 1,
        _PORTFOLIO_SHEET_NAME: 1,
        # _PERFORMANCE_SHEET_NAME: 2,
        _DAILY_PERFORMANCE_SHEET_NAME: 3
    }

    def __init__(self, config):

        self._SHEET_ID = config['sheet_id']
        self._config = config
        self._credentials = self._get_credentials(config)
        http = self._credentials.authorize(httplib2.Http())
        self._service = discovery.build('sheets', 'v4', http=http,
                                        discoveryServiceUrl=self._DISCOVERY_URL, cache_discovery=False)

    def _get_credentials(self, config):
        from oauth2client.service_account import ServiceAccountCredentials
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(config, scopes=self._SCOPES)
        return credentials

    def _read_assets(self, page):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEET_ID,
            range='{}!B1:2'.format(page)
        ).execute()
        values = result.get('values', [[], []])
        return values

    def read_prices_assets(self):
        return self._read_assets(self._PRICES_SHEET_NAME)

    def read_balances_assets(self):
        return self._read_assets(self._BALANCES_SHEET_NAME)

    def read_addresses(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEET_ID,
            range='{0}!A{1}:C'.format(self._ADDRESSES_SHEET_NAME, self._title_height[self._ADDRESSES_SHEET_NAME] + 1)
        ).execute()
        values = result.get('values', [[], [], []])
        return [(v[2], v[1], v[0]) for v in values]

    def read_last_prices(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEET_ID,
            range='{}!B1:3'.format(self._PRICES_SHEET_NAME)
        ).execute()
        values = result.get('values', [[], [], []])
        prices = {}
        for name, symbol, price in zip(*values):
            currency = name.split()[-1].replace('(', '').replace(')', '')
            v = prices.get(symbol, {})
            v[currency] = float(price)
            prices[symbol] = v
        return prices

    def _add_rows(self, rows, page, inputOption='RAW'):
        result = self._service.spreadsheets().batchUpdate(
            spreadsheetId=self._SHEET_ID,
            body={
                'requests': [
                    {
                        'insertDimension': {
                            'range': {
                                'sheetId': self._sheet_id.get(page),
                                'dimension': 'ROWS',
                                'startIndex': self._title_height.get(page),
                                'endIndex': self._title_height.get(page) + len(rows)
                            },
                        }
                    }
                ]
            }
        ).execute()
        logger.debug(result)
        result = self._service.spreadsheets().values().append(
            spreadsheetId=self._SHEET_ID,
            range='{}!A1:1'.format(page),
            body={'range': '{}!A1:1'.format(page), 'majorDimension': 'ROWS', 'values': rows},
            valueInputOption=inputOption
        ).execute()
        logger.debug(result)

    def add_balances_row(self, row):
        self._add_rows([row], self._BALANCES_SHEET_NAME)

    def add_prices_row(self, row):
        # for prices convert them to numbers
        for index, value in enumerate(row[1:]):
            try:
                value = float(value)
            except:
                pass
            row[index + 1] = value
        self._add_rows([row], self._PRICES_SHEET_NAME, inputOption='USER_ENTERED')

    def add_daily_performance_row(self, row):
        self._add_rows([row], self._DAILY_PERFORMANCE_SHEET_NAME, inputOption='USER_ENTERED')

    def get_latest_token_supply(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEET_ID,
            range='{}!B4'.format(self._DAILY_PERFORMANCE_SHEET_NAME)
        ).execute()
        return float(result.get('values', [[]])[0][0])

    def get_latest_token_prices(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEET_ID,
            range='{0}!{1}:{1}'.format(self._DAILY_PERFORMANCE_SHEET_NAME,
                                       self._title_height[self._DAILY_PERFORMANCE_SHEET_NAME] + 1)
        ).execute()
        row = result.get('values', [[0] * 15])[0]
        return [float(row[6]), float(row[9]), float(row[12])]

    def add_portfolio(self, rows):
        self._add_rows(rows, self._PORTFOLIO_SHEET_NAME, inputOption='USER_ENTERED')
