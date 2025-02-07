import pandas as pd
from datetime import datetime, timedelta
from conn import create_connection

# Connessione all'API
api = create_connection()

def get_historical_data(symbol, start_date, end_date, timeframe='day'):
    """
    Recupera i dati storici di un titolo per un intervallo di tempo specificato.

    Parameters:
    symbol (str): Il simbolo del titolo (ad esempio "AAPL", "TSLA").
    start_date (str): La data di inizio in formato "YYYY-MM-DD".
    end_date (str): La data di fine in formato "YYYY-MM-DD".
    timeframe (str): Il timeframe dei dati, default è 'day' (giornaliero), ma puoi usare anche 'minute', 'hour', ecc.

    Returns:
    pd.DataFrame: Un DataFrame con i dati storici del titolo.
    """

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Recupera i dati storici utilizzando get_barset di Alpaca
    barset = api.get_barset(symbol, timeframe, start=start_date, end=end_date)

    # Convertiamo i dati in un DataFrame
    df = barset[symbol]
    data = {
        'timestamp': [bar.t for bar in df],
        'open': [bar.o for bar in df],
        'high': [bar.h for bar in df],
        'low': [bar.l for bar in df],
        'close': [bar.c for bar in df],
        'volume': [bar.v for bar in df]
    }

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)

    # Filtriamo i dati in base alle date di inizio e fine
    df = df[(df.index >= start_date) & (df.index <= end_date)]

    return df
