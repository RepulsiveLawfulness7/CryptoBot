import alpaca_trade_api as tradeapi
import pandas as pd
import ta
from datetime import datetime
from config import api_key, api_secret, BASE_URL


# Connect to Alpaca API
def connect_alpaca():
    api = tradeapi.REST(api_key, api_secret, BASE_URL, api_version='v2')
    return api


# Function to retrieve historical data for a symbol
def get_historical_data(symbol, start_date, end_date):
    """
    Ottieni i dati storici per un simbolo.
    """
    try:
        api = connect_alpaca()  # Connect to Alpaca API
        bars = api.get_bars(symbol,
                            tradeapi.rest.TimeFrame.Day,  # Timeframe giornaliero
                            start=start_date,
                            end=end_date).df
        return bars
    except Exception as e:
        print(f"Errore nel recupero dei dati: {e}")
        return None


# Function to add technical indicators to the data
def add_technical_indicators(df):
    # Calculate SMAs
    df["SMA_50"] = df['close'].rolling(window=50).mean()
    df["SMA_200"] = df['close'].rolling(window=200).mean()

    # Add RSI and MACD
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    df["MACD"] = ta.trend.macd(df["close"])


    df.dropna(inplace=True)  # Remove missing values
    return df

def add_xgboost_predictions(df):
    import xgboost as xgb
    from sklearn.model_selection import train_test_split

    df["Target"] = df["close"].shift(-1)  # Predict next day's closing price
    df.dropna(inplace=True)  # Remove missing values

    X = df[["open", "high", "low", "volume", "SMA_50", "SMA_200", "RSI", "MACD"]]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X_train, y_train)

    df["XGBoost_Prediction"] = model.predict(X)  # Predict using the trained model
    df["Signal"] = "HOLD"  # Default signal is "HOLD"

    # BUY signal:
    # - SMA_50 > SMA_200 (bullish trend)
    # - XGBoost Prediction > current price (future price expected to rise)
    # - RSI is not in overbought territory (RSI < 70)
    # - MACD histogram is positive (MACD line > Signal line)
    df.loc[
        (df["SMA_50"] > df["SMA_200"]) &  # Bullish trend condition (SMA)
        (df["XGBoost_Prediction"] > df["close"]),
        "Signal"
    ] = "BUY"

    # SELL signal:
    # - SMA_50 < SMA_200 (bearish trend)
    # - XGBoost Prediction < current price (future price expected to fall)
    # - RSI is not in oversold territory (RSI > 30)
    # - MACD histogram is negative (MACD line < Signal line)
    df.loc[
        (df["SMA_50"] < df["SMA_200"]) &  # Bearish trend condition (SMA)
        (df["XGBoost_Prediction"] < df["close"]),
        "Signal"
    ] = "SELL"
    return df
