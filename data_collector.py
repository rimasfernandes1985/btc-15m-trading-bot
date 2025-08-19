import ccxt
import pandas as pd
import requests
from datetime import datetime
from data_preprocessor import preprocess_data

# Configurações
BOT_TOKEN = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
CHAT_ID = "1367800874"
exchange = ccxt.kucoin({'enableRateLimit': True})

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=10)
    except:
        pass

def calculate_risk_level(current_price):
    """Calcula níveis de risco com base na volatilidade recente"""
    df = pd.read_csv('btc_data.csv').tail(20)
    volatility = df['close'].std()
    return {
        'stop_loss': current_price * 0.995,
        'take_profit': current_price * 1.01,
        'risk_score': min(volatility / current_price * 100, 5)  # Score 0-5
    }

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
                risk = calculate_risk_level(df['close'].iloc[-1])
                send_telegram_alert(
                    f"🚀 SINAL FORTE DE COMPRA\n"
                    f"Confiança: {proba:.2%}\n"
                    f"Preço: {df['close'].iloc[-1]:.2f} USD\n"
                    f"Stop Loss: {risk['stop_loss']:.2f}\n"
                    f"Take Profit: {risk['take_profit']:.2f}\n"
                    f"Risco: {risk['risk_score']:.1f}/5"
                )
        except Exception as e:
            send_telegram_alert(f"⚠️ Erro na previsão: {str(e)}")

except Exception as e:
    send_telegram_alert(f"❌ Erro crítico: {str(e)}")
