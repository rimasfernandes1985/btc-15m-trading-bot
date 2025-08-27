import pandas as pd
import numpy as np
from ta import add_all_ta_features
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_historical_data():
    """Carrega dados históricos de 15min (2012-2025)"""
    try:
        historical_data = pd.read_csv('btc_15m_optimized.csv')
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
        historical_data = historical_data.sort_values('timestamp')
        print(f"📊 Dados históricos carregados: {len(historical_data)} velas de 15min")
        return historical_data
    except FileNotFoundError:
        print("⚠️ Arquivo histórico btc_15m_optimized.csv não encontrado")
        return None

def fetch_realtime_data():
    """Busca dados em tempo real (apenas se necessário)"""
    try:
        # Esta parte pode ser mantida para atualizações futuras
        print("⏰ Dados em tempo real desativados - usando apenas históricos")
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar dados em tempo real: {e}")
        return None

def calculate_technical_indicators(df):
    """Calcula indicadores técnicos"""
    print("📈 Calculando indicadores técnicos...")
    
    # Garantir que temos as colunas necessárias
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ Coluna {col} não encontrada")
            return df
    
    # Converter para float para evitar erros
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remover NaN
    df = df.dropna()
    
    # Indicadores básicos
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=20).std()
    
    # Médias móveis
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # Volume indicators
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    print(f"✅ {len(df.columns)} indicadores calculados")
    return df

def create_target_variable(df):
    """Cria variável target (sinal de compra/venda)"""
    print("🎯 Criando variável target...")
    
    # Sinal baseado no movimento futuro (5 velas à frente)
    df['future_close'] = df['close'].shift(-5)
    df['price_change'] = (df['future_close'] - df['close']) / df['close']
    
    # Classificação binária
    df['signal'] = np.where(df['price_change'] > 0.002, 1, 0)  # 0.2% de ganho
    
    # Remover últimas linhas sem futuro
    df = df.dropna()
    
    print(f"📊 Distribuição de sinais: {df['signal'].value_counts().to_dict()}")
    return df

def prepare_ml_data():
    """Prepara dados para machine learning"""
    print("\n" + "="*50)
    print("🤖 PREPARANDO DADOS PARA MACHINE LEARNING")
    print("="*50)
    
    # Carregar dados históricos
    historical_data = load_historical_data()
    if historical_data is None:
        print("❌ Não foi possível carregar dados históricos")
        return False
    
    # Calcular indicadores
    df_with_indicators = calculate_technical_indicators(historical_data)
    
    # Criar variável target
    ml_data = create_target_variable(df_with_indicators)
    
    # Selecionar colunas para ML
    feature_columns = [
        'open', 'high', 'low', 'close', 'volume',
        'returns', 'volatility',
        'sma_20', 'sma_50', 'ema_12', 'ema_26',
        'macd', 'macd_signal', 'macd_histogram',
        'rsi', 'bb_middle', 'bb_upper', 'bb_lower', 'bb_width',
        'volume_sma', 'volume_ratio'
    ]
    
    # Garantir que todas as colunas existem
    available_columns = [col for col in feature_columns if col in ml_data.columns]
    ml_data = ml_data[available_columns + ['signal', 'timestamp']]
    
    # Remover NaN
    ml_data = ml_data.dropna()
    
    # Salvar dados preparados
    ml_data.to_csv('ml_ready_data.csv', index=False)
    
    print(f"✅ Dados preparados para ML: {len(ml_data)} amostras")
    print(f"📊 Features: {len(available_columns)} colunas")
    print(f"💾 Salvo como: ml_ready_data.csv")
    
    return True

if __name__ == "__main__":
    success = prepare_ml_data()
    if success:
        print("\n🎉 PRÉ-PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("👉 Execute o ml_trainer.py para treinar o modelo")
    else:
        print("\n❌ FALHA NO PRÉ-PROCESSAMENTO")
