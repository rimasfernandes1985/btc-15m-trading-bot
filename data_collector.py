import ccxt
import pandas as pd
from datetime import datetime
import requests
import time  # Adicionado para rate limit

# ===== CONFIGURAÇÕES =====
BOT_TOKEN = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"  # Substitua se necessário
CHAT_ID = "1367800874"
EXCHANGE = ccxt.kucoin({
    'enableRateLimit': True,  # Evita bloqueio por excesso de requests
    'timeout': 10000  # 10 segundos de timeout
})

# ===== FUNÇÃO DE ALERTA =====
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=params, timeout=10)
        response.raise_for_status()  # Levanta erro se HTTP falhar
    except Exception as e:
        print(f"Erro ao enviar alerta: {e}")

# ===== LÓGICA PRINCIPAL =====
try:
    # 1. Coleta dados
    ohlcv = EXCHANGE.fetch_ohlcv('BTC/USDT', '15m', limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 2. Salva dados (com tratamento robusto)
    try:
        existing = pd.read_csv('btc_data.csv')
        updated = pd.concat([existing, df]).drop_duplicates('timestamp')
        updated.to_csv('btc_data.csv', index=False)
    except FileNotFoundError:
        df.to_csv('btc_data.csv', index=False)
    except Exception as e:
        raise Exception(f"Erro ao salvar CSV: {e}")

    # 3. Notificação
    send_telegram_alert(f"✅ <b>BTC/USDT</b> atualizado em {datetime.now().strftime('%d/%m %H:%M')}")

except ccxt.NetworkError as e:
    send_telegram_alert(f"📵 <b>Falha na rede:</b> {str(e)}")
except ccxt.ExchangeError as e:
    send_telegram_alert(f"⚠️ <b>Erro na exchange:</b> {str(e)}")
except Exception as e:
    send_telegram_alert(f"❌ <b>Erro inesperado:</b> {str(e)}")
