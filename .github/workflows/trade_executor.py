import ccxt
import joblib
import pandas as pd
from datetime import datetime

# Configuração da Exchange (Modo Paper Trading)
exchange = ccxt.kucoin({
    'apiKey': 'SUA_API_KEY',
    'secret': 'SUA_API_SECRET',
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def execute_trade(signal, price):
    try:
        if signal == "BUY":
            # Exemplo: Compra de 1% do capital
            balance = exchange.fetch_balance()['USDT']['free']
            amount = (balance * 0.01) / price
            exchange.create_market_buy_order('BTC/USDT', amount)
            
        elif signal == "SELL":
            position = exchange.fetch_positions(['BTC/USDT'])[0]
            exchange.create_market_sell_order('BTC/USDT', position['contracts'])
            
    except Exception as e:
        print(f"Erro na execução: {str(e)}")

if __name__ == "__main__":
    # Carregar última previsão
    df = pd.read_csv('ml_ready_data.csv').iloc[-1]
    model = joblib.load('trading_model.pkl')
    
    # Fazer previsão
    features = df.drop(['target', 'timestamp'])
    signal = "BUY" if model.predict([features])[0] == 1 else "HOLD"
    
    # Executar (modo paper trading)
    if signal == "BUY":
        execute_trade(signal, df['close'])
