import ccxt
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

# Carregar variáveis
load_dotenv('btc-trader.env')

class KucoinTrader:
    def __init__(self, test_mode=True):
        self.exchange = ccxt.kucoin({
            'apiKey': os.getenv("KUCOIN_API_KEY"),
            'secret': os.getenv("KUCOIN_SECRET"),
            'password': os.getenv("KUCOIN_PASSPHRASE"),
            'enableRateLimit': True,
            'test': test_mode  # Modo sandbox - não opera com dinheiro real
        })
        self.test_mode = test_mode
        
    def get_balance(self, currency='USDT'):
        """Retorna saldo disponível"""
        try:
            balance = self.exchange.fetch_balance()
            return balance[currency]['free']
        except Exception as e:
            print(f"❌ Erro ao buscar saldo: {e}")
            return 0

    def execute_trade(self, signal, symbol='BTC/USDT', amount_percent=10):
        """Executa ordem de compra/venda baseada no sinal do ML"""
        if signal not in [0, 1]:
            print("⚠️ Sinal inválido. Nenhuma operação executada.")
            return None
        
        try:
            # Calcular quantidade baseada no saldo
            balance = self.get_balance('USDT')
            amount = (balance * amount_percent / 100) / self.exchange.fetch_ticker(symbol)['last']
            
            if amount <= 0:
                print("💰 Saldo insuficiente")
                return None
            
            # Executar ordem
            side = 'buy' if signal == 1 else 'sell'
            order = self.exchange.create_market_order(symbol, side, amount)
            
            # Log da operação
            mode = "TESTE" if self.test_mode else "REAL"
            print(f"🎯 Ordem {mode} executada: {side.upper()} {amount:.6f} BTC")
            
            return order
            
        except Exception as e:
            print(f"❌ Erro na ordem: {e}")
            return None

def predict_signal():
    """Faz previsão usando o modelo treinado"""
    try:
        # Carregar modelo e dados recentes
        model = joblib.load('trading_model.pkl')
        data = pd.read_csv('ml_ready_data.csv').tail(1)  # Últimos dados
        
        # Remover colunas não numéricas
        data = data.select_dtypes(include=[np.number])
        if 'signal' in data.columns:
            data = data.drop('signal', axis=1)
        
        # Fazer previsão
        prediction = model.predict(data)[0]
        confidence = model.predict_proba(data)[0].max()
        
        print(f"📊 Previsão: {prediction} (Confiança: {confidence:.2%})")
        return prediction
        
    except Exception as e:
        print(f"❌ Erro na previsão: {e}")
        return None

def send_telegram_alert(message):
    """Envia alerta para Telegram"""
    try:
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {'chat_id': chat_id, 'text': message}
        requests.post(url, json=params)
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

if __name__ == "__main__":
    print(f"🤖 Iniciando Trade Executor - {datetime.now()}")
    
    # Fazer previsão
    signal = predict_signal()
    if signal is None:
        print("❌ Não foi possível obter sinal")
        exit()
    
    # Executar trade
    trader = KucoinTrader(test_mode=True)  # ⚠️ SEMPRE TRUE POR ENQUANTO!
    order = trader.execute_trade(signal, amount_percent=5)  # 5% do saldo
    
    # Enviar alerta
    if order:
        message = f"🎯 ORDEM EXECUTADA (TESTE)\nSinal: {signal}\nMontante: 5% do saldo"
        send_telegram_alert(message)
    
    print("✅ Execução concluída!")
