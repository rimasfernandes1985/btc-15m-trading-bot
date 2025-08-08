import pandas as pd
import numpy as np
import joblib
import traceback
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import requests
from datetime import datetime

# Configurações do Telegram (SUAS CREDENCIAIS JÁ ESTÃO AQUI)
BOT_TOKEN = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
CHAT_ID = "1367800874"

def send_telegram_alert(message):
    """Envia alertas para seu Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar Telegram: {str(e)}")
        return None

def load_data():
    """Carrega e prepara os dados"""
    try:
        df = pd.read_csv('ml_ready_data.csv')
        
        if len(df) < 1000:
            raise ValueError(f"Dados insuficientes (apenas {len(df)} registros)")
            
        # Garantir que temos a coluna target
        if 'target' not in df.columns:
            raise ValueError("Coluna 'target' não encontrada")
            
        return df.dropna()
        
    except Exception as e:
        error_msg = f"❌ Falha ao carregar dados: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None

def train_model(df):
    """Treina o modelo com validação cruzada temporal"""
    try:
        X = df.drop(columns=['target', 'timestamp'])
        y = df['target']
        
        # Balanceamento de classes
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X, y)
        
        # Configuração do modelo
        model = RandomForestClassifier(
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        # Parâmetros para otimização
        params = {
            'n_estimators': [50, 100],
            'max_depth': [5, 10],
            'min_samples_split': [2, 5]
        }
        
        # Validação cruzada temporal
        tscv = TimeSeriesSplit(n_splits=3)
        grid = GridSearchCV(model, params, cv=tscv, scoring='accuracy', verbose=1)
        grid.fit(X_res, y_res)
        
        return grid.best_estimator_, grid.best_score_
        
    except Exception as e:
        error_msg = f"❌ Falha no treinamento: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None, 0

def save_results(model, accuracy):
    """Salva o modelo e relatório"""
    try:
        # Salvar modelo
        joblib.dump(model, 'trading_model.pkl')
        
        # Salvar metadados
        with open('model_metadata.txt', 'w') as f:
            f.write(f"Modelo treinado em: {datetime.now()}\n")
            f.write(f"Acurácia: {accuracy:.2%}\n")
            f.write(f"Features usadas: {model.n_features_in_}\n")
        
        return True
    except Exception as e:
        error_msg = f"❌ Falha ao salvar modelo: {str(e)}"
        send_telegram_alert(error_msg)
        return False

if __name__ == "__main__":
    send_telegram_alert("⏳ Iniciando treinamento do modelo...")
    
    # Passo 1: Carregar dados
    df = load_data()
    if df is None:
        exit(1)
    
    # Passo 2: Treinar modelo
    model, accuracy = train_model(df)
    if model is None:
        exit(1)
    
    # Passo 3: Salvar resultados
    if save_results(model, accuracy):
        send_telegram_alert(f"✅ Modelo treinado com sucesso!\nAcurácia: {accuracy:.2%}")
    else:
        send_telegram_alert("⚠️ Modelo treinado mas falha ao salvar!")
