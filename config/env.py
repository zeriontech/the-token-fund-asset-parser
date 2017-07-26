import os
import logging

logger = logging.getLogger(__name__)

STRUCTURE = {
    'bugsnag': {
        'api_key': 'BUGSNAG_API_KEY',
    },
    'kraken': {
        'key': 'KRAKEN_KEY',
        'secret': 'KRAKEN_SECRET',
    },
    'poloniex': {
        'key': 'POLONIEX_KEY',
        'secret': 'POLONIEX_SECRET',
    },
    'bitstamp': {
        'key': 'BITSTAMP_KEY',
        'secret': 'BITSTAMP_SECRET',
        'customer_id': 'BITSTAMP_CUSTOMER_ID',
    },
    'sheets': {
        'auth_provider_x509_cert_url': 'SHEETS_AUTH_PROVIDER_X509_CERT_URL',
        'auth_uri': 'SHEETS_AUTH_URI',
        'client_email': 'SHEETS_CLIENT_EMAIL',
        'client_id': 'SHEETS_CLIENT_ID',
        'client_x509_cert_url': 'SHEETS_CLIENT_X509_CERT_URL',
        'private_key': 'SHEETS_PRIVATE_KEY',
        'private_key_id': 'SHEETS_PRIVATE_KEY_ID',
        'project_id': 'SHEETS_PROJECT_ID',
        'sheet_id': 'SHEETS_SHEET_ID',
        'token_uri': 'SHEETS_TOKEN_URI',
        'type': 'SHEETS_TYPE',
    },
}

def _fill_structure(d):
    if type(d) is str:
        return os.environ.get(d).replace('\\\\n', '\n')
    res = {}
    for key, value in d.items():
        res[key] = _fill_structure(d[key])
    return res

def config_from_env():
    config = _fill_structure(STRUCTURE)

    logger.debug(str(config))
    return config

