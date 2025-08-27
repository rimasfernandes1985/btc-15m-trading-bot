import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

def load_historical_data(file_path='btc_1m_historical.csv'):
    """Carrega dados históricos de 1min"""
    try:
        historical_data = pd.read_csv(file_path)
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
        historical_data = historical_data.sort_values('timestamp')
        print(f"📊 Dados históricos carregados: {len(historical_data)} velas de 1min")
        return historical_data
    except FileNotFoundError:
        print("⚠️ Arquivo histórico não encontrado. Usando apenas dados em tempo real.")
        return None

def resample_to_15min(historical_data):
    """Converte dados de 1min para 15min"""
    if historical_data is None:
        return None
        
    historical_data = historical_data.set_index('timestamp')
    data_15m = historical_data.resample('15T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    print(f"🔄 Convertido para: {len(data_15m)} velas de 15min")
    return data_15m.reset_index()

def fetch_realtime_data():
    """Busca dados em tempo real"""
    try:
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', limit=1000)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"❌ Erro ao buscar dados em tempo real: {e}")
        return None

def merge_data(historical_15m, realtime_data):
    """Combina dados históricos e tempo real"""
    if historical_15m is not None:
        # Combina todos os dados
        all_data = pd.concat([historical_15m, realtime_data], ignore_index=True)
        all_data = all_data.drop_duplicates('timestamp').sort_values('timestamp')
    else:
        all_data = realtime_data
        
    return all_data

def save_data(data, filename='btc_data.csv'):
    """Salva dados consolidados"""
    try:
        existing = pd.read_csv(filename)
        updated = pd.concat([existing, data]).drop_duplicates('timestamp')
        updated.to_csv(filename, index=False)
        print(f"💾 Dados salvos: {len(updated)} velas totais")
    except FileNotFoundError:
        data.to_csv(filename, index=False)
        print(f"💾 Novo arquivo criado: {len(data)} velas")

# Execução principal
try:
    print("🔄 Iniciando coleta de dados...")
    
    # 1. Carrega dados históricos
    historical_1m = load_historical_data()
    historical_15m = resample_to_15min(historical_1m) if historical_1m is not None else None
    
    # 2. Busca dados em tempo real
    realtime_data = fetch_realtime_data()
    
    if realtime_data is not None:
        # 3. Combina dados
        all_data = merge_data(historical_15m, realtime_data)
        
        # 4. Salva
        save_data(all_data)
        
        print("✅ Coleta concluída com sucesso!")
    else:
        print("❌ Falha na coleta de dados em tempo real")

except Exception as e:
    print(f"❌ Erro inesperado: {e}")
