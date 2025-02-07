import alpaca_trade_api as tradeapi
import config

# Crea la connessione all'API di Alpaca
def create_connection():
    api = tradeapi.REST(config.api_key, config.api_secret, config.BASE_URL, api_version="v2")
    return api

# Funzione per inviare un ordine di acquisto
def place_buy_order(symbol, qty):
    api = create_connection()
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"Ordine di acquisto {qty} {symbol} inviato con successo.")
    except Exception as e:
        print(f"Errore durante l'invio dell'ordine di acquisto: {e}")

# Funzione per inviare un ordine di vendita
def place_sell_order(symbol, qty):
    api = create_connection()
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        print(f"Ordine di vendita {qty} {symbol} inviato con successo.")
    except Exception as e:
        print(f"Errore durante l'invio dell'ordine di vendita: {e}")
