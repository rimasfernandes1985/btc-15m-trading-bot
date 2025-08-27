import ccxt
import pandas as pd
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv('btc-trader.env')

# Configuração da exchange
exchange = ccxt.kucoin({
    'apiKey': os.getenv("KUCOIN_API_KEY"),
    'secret': os.getenv("KUCOIN_SECRET"),
    'password': os.getenv("KUCOIN_PASSPHRASE"),
    'enableRateLimit': True
})

# Função de alerta (COMENTADA - notificações desativadas)
def send_telegram_alert(message):
    # bot_token = os.getenv("BOT_TOKEN")
    # chat_id = os.getenv("CHAT_ID")
    # url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    # requests.get(url).json()
    print(f"📧 Notificação (desativada): {message}")  # Apenas log interno

try:
    # 1. Coleta dados
    print("📊 Coletando dados BTC/USDT...")
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 2. Salva dados
    try:
        existing = pd.read_csv('btc_data.csv')
        updated = pd.concat([existing, df]).drop_duplicates('timestamp')
        updated.to_csv('btc_data.csv', index=False)
        print("💾 Dados atualizados no CSV")
    except FileNotFoundError:
        df.to_csv('btc_data.csv', index=False)
        print("💾 Novo arquivo CSV criado")

    # 3. Notificação (COMENTADA - desativada)
    # send_telegram_alert("✅ Dados do BTC atualizados!")

except ccxt.NetworkError as e:
    print(f"📵 Erro de rede: {str(e)}")
    # send_telegram_alert(f"📵 Falha na rede: {str(e)}")
except ccxt.ExchangeError as e:
    print(f"⚠️ Erro da exchange: {str(e)}")
    # send_telegram_alert(f"⚠️ Erro da exchange: {str(e)}")
except Exception as e:
    print(f"❌ Erro inesperado: {str(e)}")
    # send_telegram_alert(f"❌ Erro inesperado: {str(e)}")

print("✅ Execução concluída (notificações desativadas)")
