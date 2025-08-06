import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna

def preprocess_data(df):
    """
    Pré-processa dados de trading para Machine Learning
    
    Args:
        df (pd.DataFrame): DataFrame com colunas: timestamp, open, high, low, close, volume
        
    Returns:
        pd.DataFrame: DataFrame pré-processado com features técnicas e target
    """
    try:
        # Converter timestamp e ordenar
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Remover valores NaN
        df = dropna(df)
        
        # Adicionar todos os indicadores técnicos
        df = add_all_ta_features(
            df, 
            open="open", 
            high="high", 
            low="low", 
            close="close", 
            volume="volume",
            fillna=True
        )
        
        # Criar features derivadas
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(window=5).std()
        
        # Criar target (preço futuro +1%)
        df['target'] = np.where(
            df['close'].shift(-1) > df['close'] * 1.01, 1, 0
        )
        
        # Remover últimas linhas sem target
        df = df.dropna(subset=['target'])
        
        # Selecionar colunas relevantes
        keep_cols = [col for col in df.columns if not col.startswith(('trend_psar', 'others'))]
        df = df[keep_cols].copy()
        
        return df
    
    except Exception as e:
        print(f"Erro no pré-processamento: {e}")
        return None
