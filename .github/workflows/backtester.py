import pandas as pd
import numpy as np
import joblib
from datetime import datetime

def calculate_performance(trades):
    if not trades:
        return 0, []
    
    profits = []
    balance = 10000
    position = 0
    entry_price = 0
    
    for trade in trades:
        if trade[0] == 'BUY':
            position = balance * 0.01 / trade[2]
            entry_price = trade[2]
            balance -= position * entry_price
        else:
            balance += position * trade[2]
            profit_pct = (trade[2] - entry_price) / entry_price * 100
            profits.append(profit_pct)
            position = 0
    
    if position > 0:
        balance += position * trades[-1][2]
    
    roi = (balance - 10000) / 10000
    return roi, profits

def backtest():
    df = pd.read_csv('ml_ready_data.csv')
    model = joblib.load('trading_model.pkl')
    
    trades = []
    for i in range(100, len(df)):
        row = df.iloc[i]
        features = row.drop(['target', 'timestamp'])
        
        prediction = model.predict([features])[0]
        proba = model.predict_proba([features])[0][1]
        
        if prediction == 1 and proba > 0.6:
            if not trades or trades[-1][0] == 'SELL':
                trades.append(('BUY', row['timestamp'], row['close']))
        elif trades and trades[-1][0] == 'BUY':
            trades.append(('SELL', row['timestamp'], row['close']))
    
    roi, profits = calculate_performance(trades)
    
    # Salvar resultados
    with open('backtest_results.txt', 'w') as f:
        f.write(f"Backtest realizado em: {datetime.now()}\n")
        f.write(f"ROI Total: {roi:.2%}\n")
        f.write(f"Operações: {len(trades)//2}\n")
        f.write(f"Taxa de Acerto: {np.mean([p > 0 for p in profits]):.2%}\n")
        f.write(f"Lucro Médio por Operação: {np.mean(profits):.2f}%\n")
    
    return roi, trades

if __name__ == "__main__":
    roi, trades = backtest()
    print(f"Backtest completo! ROI: {roi:.2%}")
