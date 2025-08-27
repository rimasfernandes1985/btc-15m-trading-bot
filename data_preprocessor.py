import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def process_large_historical_data(input_path='btc_1m_historical.csv', 
                                 output_path='btc_15m_historical.csv',
                                 sample_size=50000):
    """
    Processa grandes arquivos históricos de forma eficiente
    """
    print("📊 Processando dados históricos...")
    
    # Leitura em chunks para não sobrecarregar memória
    chunk_size = 100000
    processed_chunks = []
    
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        # Padroniza colunas
        chunk.columns = chunk.columns.str.lower().str.strip()
        
        # Converte timestamp
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'])
        
        # Ordena
        chunk = chunk.sort_values('timestamp')
        
        # Converte para 15min
        chunk = chunk.set_index('timestamp')
        chunk_15m = chunk.resample('15T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        processed_chunks.append(chunk_15m)
    
    # Combina todos os chunks processados
    final_data = pd.concat(processed_chunks)
    final_data = final_data.sort_index()
    
    # Remove duplicatas
    final_data = final_data[~final_data.index.duplicated(keep='last')]
    
    # Amostra recente (últimos X registros)
    recent_data = final_data.tail(sample_size)
    
    # Salva arquivo reduzido
    recent_data.to_csv(output_path)
    print(f"✅ Arquivo reduzido salvo: {len(recent_data)} velas de 15min")
    
    return recent_data

# Uso:
if __name__ == "__main__":
    data = process_large_historical_data(
        input_path='seu_arquivo_grande.csv',
        output_path='btc_15m_recent.csv',
        sample_size=50000  # Últimas 50k velas de 15min
# Arquivos grandes
*.csv
!btc_15m_recent.csv  # Exceto este
seu_arquivo_grande.csv
    )
