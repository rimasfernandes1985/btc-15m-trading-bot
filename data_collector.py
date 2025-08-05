import ccxt
import pandas as pd
from datetime import datetime
import requests  # Adicionei no topo com outros imports

def send_telegram_alert(message):
    bot_token = "SEU_BOT_TOKEN"  # Substitua pelo seu token real
    chat_id = "SEU_CHAT_ID"      # Substitua pelo seu chat ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()

exchange = ccxt.kucoin()

try:
    # Coleta dados
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Salva dados
    try:
        existing = pd.read_csv('btc_data.csv')
        updated = pd.concat([existing, df]).drop_duplicates('timestamp')
        updated.to_csv('btc_data.csv', index=False)
    except:
        df.to_csv('btc_data.csv', index=False)
    
    # Notificação só se tudo der certo
    send_telegram_alert("✅ Dados do BTC atualizados com sucesso!")

except Exception as e:
    error_msg = f"❌ Falha na atualização: {str(e)}"
    send_telegram_alert(error_msg)  # Alerta de erro também!
    print(error_msg)  # Log adicional
