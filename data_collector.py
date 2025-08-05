import ccxt  
import pandas as pd  
from datetime import datetime  

exchange = ccxt.kucoin()  # Exchange mais tolerante  

try:  
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=1000)  
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])  
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  

    # Salvar dados  
    try:  
        existing = pd.read_csv('btc_data.csv')  
        updated = pd.concat([existing, df]).drop_duplicates('timestamp')  
        updated.to_csv('btc_data.csv', index=False)  
    except:  
        df.to_csv('btc_data.csv', index=False)  

except Exception as e:  
    print(f"Erro: {e}")  # Para debug  
    try:
    # Seu código atual de coleta de dados...
    df.to_csv('btc_data.csv', index=False)
    print("Dados salvos com sucesso!")  # Log para debug
except Exception as e:
    print(f"Erro ao salvar dados: {e}")  # Identifica onde falhou
