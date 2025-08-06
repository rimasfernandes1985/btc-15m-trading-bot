import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
import traceback

def preprocess_data(df):
    try:
        # Verificar colunas necessárias
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Colunas faltando: {missing}")
            return None
            
        # Converter timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Remover valores NaN
        df = dropna(df)
        
        # Adicionar indicadores
        df = add_all_ta_features(
            df, 
            open="open", 
            high="high", 
            low="low", 
            close="close", 
            volume="volume",
            fillna=True
        )
        
        # Features adicionais
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(window=5).std()
        
        # Target
        df['target'] = np.where(
            df['close'].shift(-1) > df['close'] * 1.01, 1, 0
        )
        
        # Remover linhas sem target
        df = df.dropna(subset=['target'])
        
        # Selecionar colunas
        keep_cols = [col for col in df.columns if not col.startswith(('trend_psar', 'others'))]
        return df[keep_cols].copy()
    
    except Exception as e:
        print(f"Erro no pré-processamento: {e}")
        print(traceback.format_exc())
        return None
