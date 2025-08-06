import ccxt
import pandas as pd
import requests
from datetime import datetime
from data_preprocessor import preprocess_data  # Importação do novo módulo

def send_telegram_alert(message):
    bot_token = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"  # Seu token real
    chat_id = "1367800874"  # Seu chat ID real
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()

# Configurar exchange (KuCoin para evitar bloqueios)
exchange = ccxt.kucoin()

try:
    # Coletar dados OHLCV
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
    
    send_telegram_alert("✅ Dados do BTC atualizados!")
    
    # PRÉ-PROCESSAMENTO PARA ML (NOVA SEÇÃO)
    ml_data = preprocess_data(df.copy())  # Usar cópia para segurança
    
    if ml_data is not None:
        # Salvar dados processados
        ml_data.to_csv('ml_ready_data.csv', index=False)
        send_telegram_alert("✅ Dados pré-processados para ML!")
    else:
        send_telegram_alert("⚠️ Falha no pré-processamento ML!")

except Exception as e:
    error_msg = f"❌ Erro no coletor: {str(e)}"
    send_telegram_alert(error_msg)
    print(error_msg)  # Log adicional para debug
