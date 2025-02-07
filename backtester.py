import pandas as pd
import xgboost as xgb
import ta  # Assicurati di avere la libreria TA-Lib o ta installata
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from trading import place_buy_order, place_sell_order

# Funzione per eseguire il backtest
def backtest(df):
    initial_balance = 100000  # Bilancio iniziale in USD
    balance = initial_balance
    cash = balance  # Liquidità disponibile per il trading
    shares = 0  # Numero di azioni detenute
    buy_price = 0  # Prezzo di acquisto
    buy_day = None  # Giorno dell'acquisto
    transaction_history = []  # Storia delle transazioni (acquisti/vendite)

    max_investment_percent = 0.40  # Percentuale massima del bilancio da investire

    # Add Technical Indicators
    df["SMA_50"] = ta.trend.sma_indicator(df["close"], window=50)  # 50-period Simple Moving Average
    df["SMA_200"] = ta.trend.sma_indicator(df["close"], window=200)  # 200-period Simple Moving Average
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)  # Relative Strength Index (RSI)
    df["MACD"] = ta.trend.macd(df["close"])  # Moving Average Convergence Divergence (MACD)
    df.dropna(inplace=True)  # Rimuovi i valori mancanti

    # Add XGBoost Predictions
    df["Target"] = df["close"].shift(-1)  # Previsione del prezzo di chiusura del giorno successivo
    df.dropna(inplace=True)

    X = df[["open", "high", "low", "volume", "SMA_50", "SMA_200", "RSI", "MACD"]]
    y = df["Target"]

    # Dividi i dati in training e test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Allena il modello XGBoost
    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X_train, y_train)

    # Previsione con XGBoost
    df["XGBoost_Prediction"] = model.predict(X)

    # Generazione dei segnali (BUY, SELL, HOLD)
    df["Signal"] = "HOLD"  # Segnale di default

    # Segnale BUY
    df.loc[
        (df["SMA_50"] > df["SMA_200"]) &  # Trend rialzista (SMA)
        (df["XGBoost_Prediction"] > df["close"]),  # Previsione di un aumento dei prezzi
        "Signal"
    ] = "BUY"

    # Segnale SELL
    df.loc[
        (df["SMA_50"] < df["SMA_200"]) &  # Trend ribassista (SMA)
        (df["XGBoost_Prediction"] < df["close"]),  # Previsione di una diminuzione dei prezzi
        "Signal"
    ] = "SELL"

    # Backtest logico
    for i in range(1, len(df)):
        signal = df["Signal"].iloc[i]  # Segnale di trading per il giorno corrente
        current_price = df["close"].iloc[i]  # Prezzo di chiusura del giorno corrente

        # Se il segnale è "BUY" e c'è liquidità disponibile
        if signal == "BUY" and cash > 0:
            max_investment = cash * max_investment_percent  # Investimento massimo
            num_shares_to_buy = max_investment // current_price  # Numero di azioni da acquistare
            if num_shares_to_buy > 0:
                shares += num_shares_to_buy  # Aumenta il numero di azioni detenute
                cash -= num_shares_to_buy * current_price  # Riduci la liquidità
                buy_price = current_price  # Registra il prezzo di acquisto
                buy_day = df.index[i]  # Registra il giorno di acquisto
                transaction_history.append({"date": buy_day, "action": "BUY", "price": current_price, "shares": num_shares_to_buy})
                place_buy_order('AAPL', num_shares_to_buy)  # Esegui l'ordine di acquisto

        # Se il segnale è "SELL" e ci sono azioni detenute
        elif signal == "SELL" and shares > 0:
            cash += shares * current_price  # Vendi tutte le azioni e aggiungi i proventi
            transaction_history.append({"date": df.index[i], "action": "SELL", "price": current_price, "shares": shares})
            shares = 0  # Reset azioni detenute
            buy_price = 0  # Reset prezzo di acquisto
            buy_day = None  # Reset giorno di acquisto
            place_sell_order('AAPL', shares)  # Esegui l'ordine di vendita

    # Calcola il valore finale del portafoglio
    final_value = cash + shares * df["close"].iloc[-1]
    total_profit = final_value - initial_balance  # Profitto totale
    total_operations = len(transaction_history)  # Numero di operazioni (BUY/SELL)
    buy_operations = len([x for x in transaction_history if x["action"] == "BUY"])
    sell_operations = len([x for x in transaction_history if x["action"] == "SELL"])

    # Calcola il ritorno medio per operazione
    avg_return_per_operation = total_profit / total_operations if total_operations > 0 else 0

    # Stampa i risultati
    print(f"Saldo iniziale: {initial_balance:.2f}")
    print(f"Saldo finale: {final_value:.2f}")
    print(f"Profitto totale: {total_profit:.2f}")
    print(f"Operazioni totali: {total_operations}")
    print(f"Operazioni di BUY: {buy_operations}")
    print(f"Operazioni di SELL: {sell_operations}")
    print(f"Azioni detenute: {shares}")
    print(f"Valore attuale per azione: {df['close'].iloc[-1]:.2f}")
    print(f"Ritorno medio per operazione: {avg_return_per_operation:.2f}")

    # Plot dei risultati
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df["close"], label="Prezzo Attuale", color="black", linewidth=1)

    buy_operations = [x for x in transaction_history if x["action"] == "BUY"]
    sell_operations = [x for x in transaction_history if x["action"] == "SELL"]

    buy_dates = [x['date'] for x in buy_operations]
    buy_prices = [x['price'] for x in buy_operations]
    sell_dates = [x['date'] for x in sell_operations]
    sell_prices = [x['price'] for x in sell_operations]

    plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="BUY", alpha=1, s=100)
    plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="SELL", alpha=1, s=100)

    plt.xlabel("Data")
    plt.ylabel("Prezzo")
    plt.title("Prezzo e Operazioni di Trading")
    plt.legend()
    plt.grid(True)
    plt.show()

# Esegui il backtest
# df è il DataFrame che contiene i dati storici dei prezzi
# backtest(df)

