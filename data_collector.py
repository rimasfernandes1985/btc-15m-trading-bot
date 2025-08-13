import ccxt
import pandas as pd
import requests
import joblib
from datetime import datetime
from data_preprocessor import preprocess_data

def send_telegram_alert(message):
    bot_token = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
    chat_id = "1367800874"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url, timeout=10)
    except:
        pass

exchange = ccxt.kucoin({'enableRateLimit': True})

try:
    # Coleta de dados
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Salvar dados brutos
    try:
        existing = pd.read_csv('btc_data.csv')
        updated = pd.concat([existing, df]).drop_duplicates('timestamp')
        updated.to_csv('btc_data.csv', index=False)
    except FileNotFoundError:
        df.to_csv('btc_data.csv', index=False)
    
    # Pré-processamento
    ml_data = preprocess_data(df.copy())
    
    if ml_data is not None:
        ml_data.to_csv('ml_ready_data.csv', index=False)
        
        # Previsão com modelo
        try:
            model = joblib.load('trading_model.pkl')
            last_row = ml_data.iloc[[-1]].drop(columns=['target', 'timestamp'])
            prediction = model.predict(last_row)[0]
            proba = model.predict_proba(last_row)[0][1]
            
            if prediction == 1 and proba > 0.6:
                send_telegram_alert(
                    f"🚀 SINAL DE COMPRA (Conf: {proba:.2%})\n"
                    f"Preço: {df['close'].iloc[-1]:.2f} USD\n"
                    f"Hora: {datetime.now().strftime('%H:%M')}"
                )
        except Exception as e:
            send_telegram_alert(f"⚠️ Erro na previsão: {str(e)}")

except Exception as e:
    send_telegram_alert(f"❌ Erro geral: {str(e)}")
