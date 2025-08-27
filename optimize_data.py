import pandas as pd
from datetime import datetime

def optimize_data(input_file='btc_data.txt', output_file='btc_15m_optimized.csv'):
    print("📦 Otimizando dados para GitHub...")
    
    # Lê o arquivo
    df = pd.read_csv(input_file)
    
    # Converte timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Ordena por tempo
    df = df.sort_values('timestamp')
    
    # Opcional: filtra dados recentes (últimos 2 anos)
    recent_cutoff = pd.Timestamp.now() - pd.DateOffset(years=2)
    df = df[df['timestamp'] >= recent_cutoff]
    
    # Converte para 15min
    df = df.set_index('timestamp')
    df_15m = df.resample('15T').agg({
        'open': 'first',
        'high': 'max', 
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Salva otimizado
    df_15m.to_csv(output_file, index=True)
    print(f"✅ Arquivo otimizado: {output_file}")
    print(f"📊 Tamanho: {len(df_15m)} velas de 15min")
    
    return df_15m

if __name__ == "__main__":
    optimize_data()
