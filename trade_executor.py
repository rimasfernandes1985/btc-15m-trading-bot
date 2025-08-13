import ccxt
import joblib
import pandas as pd
import time
from datetime import datetime

# Configuração da Exchange (Modo Paper Trading)
exchange = ccxt.kucoin({
    'apiKey': 'SUA_API_KEY',
    'secret': 'SUA_API_SECRET',
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def get_current_position():
    positions = exchange.fetch_positions(['BTC/USDT'])
    return positions[0]['contracts'] if positions else 0

def execute_trade(signal, current_price):
    try:
        balance = exchange.fetch_balance()['USDT']['free']
        position = get_current_position()
        
        if signal == "BUY" and position == 0:
            amount = (balance * 0.01) / current_price  # 1% do capital
            exchange.create_market_buy_order('BTC/USDT', amount)
            return f"Compra executada: {amount:.6f} BTC"
            
        elif signal == "SELL" and position > 0:
            exchange.create_market_sell_order('BTC/USDT', position)
            return f"Venda executada: {position:.6f} BTC"
            
        return "Nenhuma operação necessária"
        
    except Exception as e:
        return f"Erro na execução: {str(e)}"

if __name__ == "__main__":
    # Carregar dados e modelo
    df = pd.read_csv('ml_ready_data.csv').iloc[-1]
    model = joblib.load('trading_model.pkl')
    
    # Fazer previsão
    features = df.drop(['target', 'timestamp'])
    prediction = model.predict([features])[0]
    proba = model.predict_proba([features])[0][1]
    
    # Executar apenas se confiança > 65%
    if prediction == 1 and proba > 0.65:
        result = execute_trade("BUY", df['close'])
        with open('trade_log.txt', 'a') as f:
            f.write(f"{datetime.now()}: {result}\n")
