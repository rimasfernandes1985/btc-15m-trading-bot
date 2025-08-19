import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime

# Carregar dados pré-processados
def load_data():
    try:
        data = pd.read_csv('ml_ready_data.csv')
        print(f"Dados carregados: {data.shape[0]} amostras")
        return data
    except FileNotFoundError:
        print("Arquivo ml_ready_data.csv não encontrado!")
        return None

# Treinar modelo
def train_model():
    data = load_data()
    if data is None:
        return
    
    # Separar features (X) e target (y)
    X = data.drop('signal', axis=1)
    y = data['signal']
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Treinar modelo
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Avaliar
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Acurácia do modelo: {accuracy:.2%}")
    
    # Salvar modelo
    joblib.dump(model, 'trading_model.pkl')
    print("Modelo salvo como 'trading_model.pkl'")
    
    return accuracy

if __name__ == "__main__":
    print(f"Iniciando treinamento em {datetime.now()}")
    train_model()
    print("Treinamento concluído!")
