import pandas as pd
import numpy as np
import joblib
import traceback
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
import requests
from datetime import datetime

# Configurações do Telegram
BOT_TOKEN = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
CHAT_ID = "1367800874"

def send_telegram_alert(message):
    """Envia alertas para seu Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=10)
    except:
        pass

def load_data():
    """Carrega e prepara os dados com verificação robusta"""
    try:
        df = pd.read_csv('ml_ready_data.csv')
        
        # Verificações críticas
        if len(df) < 1000:
            raise ValueError(f"Dados insuficientes (apenas {len(df)} registros)")
            
        if 'target' not in df.columns:
            raise ValueError("Coluna 'target' não encontrada")
            
        # Contar classes
        class_counts = df['target'].value_counts()
        send_telegram_alert(f"📊 Distribuição de classes:\n{class_counts.to_string()}")
        
        if min(class_counts) < 10:  # Mínimo de amostras por classe
            raise ValueError(f"Classe minoritária tem apenas {min(class_counts)} amostras")
            
        return df.dropna()
        
    except Exception as e:
        error_msg = f"❌ Falha no carregamento: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None

def train_model(df):
    """Treina o modelo com fallback para dados desbalanceados"""
    try:
        X = df.drop(columns=['target', 'timestamp'])
        y = df['target']
        
        # Tentar SMOTE apenas se tiver amostras suficientes
        if y.value_counts().min() > 5:
            smote = SMOTE(random_state=42, k_neighbors=min(5, y.value_counts().min()-1))
            X_res, y_res = smote.fit_resample(X, y)
            send_telegram_alert("🔁 Aplicado balanceamento SMOTE")
        else:
            X_res, y_res = X, y
            send_telegram_alert("⚠️ Dados desbalanceados - SMOTE omitido")
        
        # Configuração simplificada para primeira execução
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        # Validação cruzada temporal
        tscv = TimeSeriesSplit(n_splits=3)
        accuracies = []
        
        for train_idx, test_idx in tscv.split(X_res):
            X_train, X_test = X_res.iloc[train_idx], X_res.iloc[test_idx]
            y_train, y_test = y_res.iloc[train_idx], y_res.iloc[test_idx]
            
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            accuracies.append(accuracy_score(y_test, preds))
        
        avg_accuracy = np.mean(accuracies)
        return model, avg_accuracy
        
    except Exception as e:
        error_msg = f"❌ Falha no treinamento: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None, 0

def save_model(model, accuracy):
    """Salva o modelo e relatório simplificado"""
    try:
        joblib.dump(model, 'trading_model.pkl')
        
        with open('model_report.txt', 'w') as f:
            f.write(f"Modelo treinado em: {datetime.now()}\n")
            f.write(f"Acurácia média: {accuracy:.2%}\n")
            f.write(f"Features: {list(model.feature_names_in_)}\n")
        
        return True
    except Exception as e:
        send_telegram_alert(f"❌ Falha ao salvar modelo: {str(e)}")
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
    if save_model(model, accuracy):
        send_telegram_alert(f"✅ Modelo treinado!\nAcurácia: {accuracy:.2%}")
    else:
        send_telegram_alert("⚠️ Modelo treinado mas não salvo")
