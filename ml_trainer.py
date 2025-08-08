import pandas as pd
import numpy as np
import joblib
import traceback
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from data_preprocessor import preprocess_data
from datetime import datetime

def send_telegram_alert(message):
    """Função para enviar alertas via Telegram"""
    bot_token = "7888207477:AAFSKnKaBuOPDWPPVp25f-2AEREsjXucxvA"
    chat_id = "1367800874"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return None

def load_and_prepare_data():
    """Carrega e prepara os dados para treinamento"""
    try:
        # Carregar dados históricos
        df = pd.read_csv('btc_data.csv')
        
        # Pré-processar dados
        df_processed = preprocess_data(df)
        
        if df_processed is None:
            raise ValueError("Pré-processamento retornou None")
            
        # Verificar dados mínimos
        if len(df_processed) < 500:
            raise ValueError(f"Dados insuficientes para treinamento: apenas {len(df_processed)} amostras")
            
        return df_processed
        
    except Exception as e:
        error_msg = f"❌ Erro no carregamento de dados: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None

def train_trading_model(df):
    """Treina o modelo de trading com validação cruzada temporal"""
    try:
        # Separar features e target
        X = df.drop(columns=['target', 'timestamp'])
        y = df['target']
        
        # Balancear classes com SMOTE
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X, y)
        
        # Validação Cruzada Temporal
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Parâmetros para otimização
        param_grid = {
            'n_estimators': [50, 100, 150],
            'max_depth': [5, 10, 15],
            'min_samples_split': [2, 5, 10]
        }
        
        # Criar e treinar modelo
        model = GridSearchCV(
            estimator=RandomForestClassifier(class_weight='balanced', random_state=42),
            param_grid=param_grid,
            cv=tscv,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        model.fit(X_res, y_res)
        
        # Melhores parâmetros
        best_params = model.best_params_
        best_score = model.best_score_
        
        # Treinar modelo final com todos os dados
        final_model = RandomForestClassifier(
            **best_params,
            class_weight='balanced',
            random_state=42
        )
        final_model.fit(X_res, y_res)
        
        return final_model, best_params, best_score
        
    except Exception as e:
        error_msg = f"❌ Erro no treinamento: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return None, None, 0

def evaluate_model(model, df):
    """Avalia o modelo em dados não vistos"""
    try:
        # Últimos 20% para teste
        test_size = int(len(df) * 0.2)
        test_df = df.iloc[-test_size:]
        
        X_test = test_df.drop(columns=['target', 'timestamp'])
        y_test = test_df['target']
        
        # Previsões
        y_pred = model.predict(X_test)
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        
        # Plotar matriz de confusão
        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Matriz de Confusão')
        plt.colorbar()
        tick_marks = np.arange(2)
        plt.xticks(tick_marks, ['Venda', 'Compra'])
        plt.yticks(tick_marks, ['Venda', 'Compra'])
        plt.ylabel('Real')
        plt.xlabel('Predito')
        
        for i in range(2):
            for j in range(2):
                plt.text(j, i, str(cm[i, j]), 
                         horizontalalignment="center",
                         color="white" if cm[i, j] > cm.max()/2 else "black")
        
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        plt.close()
        
        return accuracy, report, cm
        
    except Exception as e:
        error_msg = f"❌ Erro na avaliação: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return 0, "", None

def save_model_and_report(model, accuracy, best_params, report):
    """Salva o modelo e relatório de desempenho"""
    try:
        # Salvar modelo
        joblib.dump(model, 'trading_model.pkl')
        
        # Salvar metadados
        with open('model_report.txt', 'w') as f:
            f.write(f"Data do Treinamento: {datetime.now()}\n")
            f.write(f"Acurácia: {accuracy:.2%}\n")
            f.write(f"Melhores Parâmetros: {best_params}\n")
            f.write("\nRelatório de Classificação:\n")
            f.write(report)
            
        return True
    except Exception as e:
        error_msg = f"❌ Erro ao salvar modelo: {str(e)}"
        send_telegram_alert(error_msg)
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Passo 1: Carregar e preparar dados
    send_telegram_alert("⏳ Iniciando treinamento do modelo...")
    df = load_and_prepare_data()
    
    if df is None:
        send_telegram_alert("❌ Falha no carregamento de dados. Treinamento abortado!")
        exit(1)
    
    # Passo 2: Treinar modelo
    model, best_params, best_score = train_trading_model(df)
    
    if model is None:
        send_telegram_alert("❌ Falha no treinamento do modelo!")
        exit(1)
    
    # Passo 3: Avaliar modelo
    accuracy, report, cm = evaluate_model(model, df)
    
    # Passo 4: Salvar resultados
    success = save_model_and_report(model, accuracy, best_params, report)
    
    if success:
        send_telegram_alert(f"✅ Modelo treinado com sucesso!\nAcurácia: {accuracy:.2%}")
        send_telegram_alert(f"📊 Melhores parâmetros: {best_params}")
    else:
        send_telegram_alert("⚠️ Modelo treinado, mas falha ao salvar resultados!")
