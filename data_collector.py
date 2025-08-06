import ccxt
import pandas as pd
import requests
import traceback
from datetime import datetime
from data_preprocessor import preprocess_data

def send_telegram_alert(message):
    bot_token = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
    chat_id = "1367800874"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar alerta: {str(e)}")
        return None

def log_to_file(message, filename='error_log.txt'):
    """Registra mensagens de erro em arquivo"""
    try:
        with open(filename, 'a') as f:
            f.write(f"{datetime.now()} - {message}\n")
    except Exception as e:
        print(f"Falha ao registrar log: {str(e)}")

def safe_file_write(df, filename):
    """Salva DataFrame em arquivo CSV com tratamento de erros"""
    try:
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        error_msg = f"❌ Erro ao salvar {filename}: {str(e)}"
        send_telegram_alert(error_msg)
        log_to_file(error_msg)
        return False

# Configurar exchange
exchange = ccxt.kucoin({
    'enableRateLimit': True,
    'timeout': 30000
})

try:
    # Passo 1: Coletar dados
    send_telegram_alert("⏳ Iniciando coleta de dados...")
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=1000)
    df_raw = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'], unit='ms')
    
    # Passo 2: Salvar dados brutos
    try:
        existing = pd.read_csv('btc_data.csv')
        # Converter timestamps existentes para datetime
        existing['timestamp'] = pd.to_datetime(existing['timestamp'])
        # Combinar e remover duplicatas
        updated_raw = pd.concat([existing, df_raw]).drop_duplicates('timestamp')
        # Salvar
        if not safe_file_write(updated_raw, 'btc_data.csv'):
            send_telegram_alert("⚠️ Falha ao salvar btc_data.csv!")
    except FileNotFoundError:
        if not safe_file_write(df_raw, 'btc_data.csv'):
            send_telegram_alert("⚠️ Falha ao salvar btc_data.csv inicial!")
    
    send_telegram_alert("✅ Dados brutos do BTC atualizados!")
    
    # Passo 3: Pré-processamento
    send_telegram_alert("⏳ Iniciando pré-processamento...")
    ml_data = preprocess_data(df_raw.copy())
    
    if ml_data is not None:
        if safe_file_write(ml_data, 'ml_ready_data.csv'):
            send_telegram_alert("✅ Dados pré-processados para ML salvos!")
        else:
            send_telegram_alert("⚠️ Falha ao salvar ml_ready_data.csv!")
    else:
        send_telegram_alert("❌ Pré-processamento retornou None!")
        log_to_file("Preprocess_data retornou None")

except Exception as e:
    error_msg = f"❌ Erro fatal: {str(e)}\n{traceback.format_exc()}"
    send_telegram_alert(error_msg[:1000])  # Telegram tem limite de 4096 caracteres
    log_to_file(error_msg)
