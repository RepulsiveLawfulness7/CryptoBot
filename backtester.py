import matplotlib.pyplot as plt
from data import get_historical_data, add_technical_indicators, add_xgboost_predictions


# Function to run backtest
def backtest(symbol, start_date, end_date):
    df = get_historical_data(symbol, start_date, end_date)
    df = add_technical_indicators(df)
    df = add_xgboost_predictions(df)

    # Initialize variables for backtest
    initial_balance = 100000
    balance = initial_balance
    cash = balance
    shares = 0
    buy_price = 0
    buy_day = None
    transaction_history = []

    max_investment_percent = 0.40  # Max amount to invest (40%)

    # Loop through DataFrame to execute the backtest
    for i in range(1, len(df)):
        signal = df["Signal"].iloc[i] # Retrieve the trading signal for the current day
        current_price = df["close"].iloc[i]# Get the current day's closing price

        # If the signal is "BUY" and cash is available
        if signal == "BUY" and cash > 0:
            max_investment = cash * max_investment_percent
            num_shares_to_buy = max_investment // current_price
            if num_shares_to_buy > 0:
                shares += num_shares_to_buy
                cash -= num_shares_to_buy * current_price
                buy_price = current_price
                buy_day = df.index[i]
                transaction_history.append(
                    {"date": buy_day, "action": "BUY", "price": current_price, "shares": num_shares_to_buy})

        elif signal == "SELL" and shares > 0:
            cash += shares * current_price
            transaction_history.append(
                {"date": df.index[i], "action": "SELL", "price": current_price, "shares": shares})
            shares = 0
            buy_price = 0
            buy_day = None


    final_value = cash + shares * df["close"].iloc[-1]
    total_profit = final_value - initial_balance
    total_operations = len(transaction_history)
    buy_operations = len([x for x in transaction_history if x["action"] == "BUY"])
    sell_operations = len([x for x in transaction_history if x["action"] == "SELL"])

    avg_return_per_operation = total_profit / total_operations if total_operations > 0 else 0

    print(f"Initial Balance: {initial_balance:.2f}")
    print(f"Final Balance: {final_value:.2f}")
    print(f"Total Profit: {total_profit:.2f}")
    print(f"Total Operations: {total_operations}")
    print(f"BUY Operations: {buy_operations}")
    print(f"SELL Operations: {sell_operations}")
    print(f"Shares Held: {shares}")
    print(f"Actual Value per Share: {df['close'].iloc[-1]:.2f}")
    print(f"Average Return per Operation: {avg_return_per_operation:.2f}")

    # Plot Results
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df["close"], label="Actual Price", color="black", linewidth=1)

    buy_operations = [x for x in transaction_history if x["action"] == "BUY"]
    sell_operations = [x for x in transaction_history if x["action"] == "SELL"]

    buy_dates = [x['date'] for x in buy_operations]
    buy_prices = [x['price'] for x in buy_operations]
    sell_dates = [x['date'] for x in sell_operations]
    sell_prices = [x['price'] for x in sell_operations]

    plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="BUY", alpha=1, s=100)
    plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="SELL", alpha=1, s=100)

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Price and Actual Trading Operations")
    plt.legend()
    plt.grid(True)
    plt.show()
