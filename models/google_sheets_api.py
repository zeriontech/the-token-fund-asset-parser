import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class SheetsAPI:

    _SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    _CLIENT_SECRET_FILE = 'configs/client_secret.json'
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
        _ADDRESSES_SHEET_NAME: 0,
        _PORTFOLIO_SHEET_NAME: 1,
        # _PERFORMANCE_SHEET_NAME: 2,
        _DAILY_PERFORMANCE_SHEET_NAME: 3
    }

    def __init__(self, sheets_id='1kFi2uGX3RZYFj76cXNE93ys3hJY49XhHtPCj_Sc5nNE', app_name='Assets Parser'):
        self._SHEETS_ID = sheets_id
        self._APPLICATION_NAME = app_name
        self._credentials = self._get_credentials()
        http = self._credentials.authorize(httplib2.Http())
        self._service = discovery.build('sheets', 'v4', http=http,
                                        discoveryServiceUrl=self._DISCOVERY_URL)

    def _get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-assets_parser.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self._CLIENT_SECRET_FILE, self._SCOPES)
            flow.user_agent = self._APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def _read_assets(self, page):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEETS_ID,
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
            spreadsheetId=self._SHEETS_ID,
            range='{}!A2:C'.format(self._ADDRESSES_SHEET_NAME)
        ).execute()
        values = result.get('values', [[], [], []])
        return [(v[2], v[1], v[0]) for v in values]

    def read_last_prices(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEETS_ID,
            range='{}!B1:3'.format(self._PRICES_SHEET_NAME)
        ).execute()
        values = result.get('values', [[], [], []])
        prices = {}
        for name, symbol, price in zip(*values):
            currency = name.split()[-1].replace('(', '').replace(')', '')
            v = prices.get(symbol, [0, 0])
            v[currency == 'BTC'] = price
            prices[symbol] = v
        return prices

    def _add_row(self, row, page, inputOption='RAW'):
        result = self._service.spreadsheets().batchUpdate(
            spreadsheetId=self._SHEETS_ID,
            body={
                'requests': [
                    {
                        'insertDimension': {
                            'range': {
                                'sheetId': self._sheet_id.get(page),
                                'dimension': 'ROWS',
                                'startIndex': self._title_height.get(page),
                                'endIndex': self._title_height.get(page) + 1
                            }
                        }
                    }
                ]
            }
        ).execute()
        print(result)
        result = self._service.spreadsheets().values().append(
            spreadsheetId=self._SHEETS_ID,
            range='{}!A1:1'.format(page),
            body={'range': '{}!A1:1'.format(page), 'majorDimension': 'ROWS', 'values': [row]},
            valueInputOption=inputOption
        ).execute()
        print(result)

    def add_balances_row(self, row):
        self._add_row(row, self._BALANCES_SHEET_NAME)

    def add_prices_row(self, row):
        # for prices convert them to numbers
        for index, value in enumerate(row[1:]):
            try:
                value = float(value)
            except:
                pass
            row[index + 1] = value
        self._add_row(row, self._PRICES_SHEET_NAME, inputOption='USER_ENTERED')

    # def add_performance_row(self, row):
    #     self._add_row(row, self._PERFORMANCE_SHEET_NAME, inputOption='USER_ENTERED')

    def add_daily_performance_row(self, row):
        self._add_row(row, self._DAILY_PERFORMANCE_SHEET_NAME, inputOption='USER_ENTERED')

    def get_latest_token_supply(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEETS_ID,
            range='{}!B4'.format(self._DAILY_PERFORMANCE_SHEET_NAME)
        ).execute()
        return float(result.get('values', [[]])[0][0])

    def get_latest_token_prices(self):
        result = self._service.spreadsheets().values().get(
            spreadsheetId=self._SHEETS_ID,
            range='{0}!{1}:{1}'.format(self._DAILY_PERFORMANCE_SHEET_NAME,
                                       self._title_height[self._DAILY_PERFORMANCE_SHEET_NAME] + 1)
        ).execute()
        row = result.get('values', [[0] * 15])[0]
        return [float(row[6]), float(row[9]), float(row[12])]

    def add_portfolio_row(self, row):
        self._add_row(row, self._PORTFOLIO_SHEET_NAME, inputOption='USER_ENTERED')
