import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from datetime import datetime

# Carregar dados pré-processados
def load_data():
    try:
        data = pd.read_csv('ml_ready_data.csv')
        print(f"Dados carregados: {data.shape[0]} amostras")
        return data
    except FileNotFoundError:
        print("Erro: Arquivo ml_ready_data.csv não encontrado!")
        print("Execute primeiro o data_preprocessor.py")
        return None

# Treinar modelo
def train_model():
    print(f"=== Iniciando Treinamento em {datetime.now()} ===")
    
    data = load_data()
    if data is None:
        return False
    
    # 👇 DIAGNÓSTICO (adicione estas linhas)
    print("\n=== DIAGNÓSTICO DOS DADOS ===")
    print(f"Colunas disponíveis: {list(data.columns)}")
    print(f"Tipos de dados:\n{data.dtypes}")
    
    # Remover colunas não numéricas (timestamp, etc.)
    non_numeric_cols = data.select_dtypes(include=['object', 'datetime']).columns
    if len(non_numeric_cols) > 0:
        print(f"Removendo colunas não numéricas: {list(non_numeric_cols)}")
        data = data.drop(columns=non_numeric_cols)
    
    # Verificar se há dados suficientes
    if len(data) < 100:
        print("Erro: Dados insuficientes para treinamento (mínimo 100 amostras)")
        return False
    
    # Verificar se a coluna 'signal' existe
    if 'signal' not in data.columns:
        print("❌ ERRO: Coluna 'signal' não encontrada!")
        return False
    
    # Separar features (X) e target (y)
    X = data.drop('signal', axis=1)
    y = data['signal']
    
    # Verificar se há valores NaN
    if X.isnull().any().any():
        print("⚠️  Removendo valores NaN...")
        X = X.dropna()
        y = y[X.index]
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Treinamento: {len(X_train)} amostras")
    print(f"Teste: {len(X_test)} amostras")
    
    # Treinar modelo
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    print("Treinando modelo...")
    model.fit(X_train, y_train)
    
    # Avaliar
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print("\n=== RESULTADOS ===")
    print(f"Acurácia: {accuracy:.2%}")
    print("\nRelatório Detalhado:")
    print(classification_report(y_test, predictions))
    
    # Salvar modelo
    joblib.dump(model, 'trading_model.pkl')
    print("\nModelo salvo como 'trading_model.pkl'")
    
    return True

if __name__ == "__main__":
    success = train_model()
    if success:
        print("✅ Treinamento concluído com sucesso!")
    else:
        print("❌ Falha no treinamento")
