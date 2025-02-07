import alpaca_trade_api as tradeapi
import config

api = tradeapi.REST(config.api_key, config.api_secret, config.BASE_URL, api_version="v2")


def create_connection():
    api = tradeapi.REST(config.api_key, config.api_secret, config.BASE_URL, api_version='v2')
    return api