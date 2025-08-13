import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def generate_report():
    df = pd.read_csv('ml_ready_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Cálculo de métricas
    last_signal = "COMPRA" if df['target'].iloc[-1] == 1 else "NEUTRO"
    win_rate = df['target'].mean() if 'target' in df.columns else 0
    
    # Gráfico avançado
    plt.figure(figsize=(14, 10))
    
    # Preço
    plt.subplot(2, 1, 1)
    plt.plot(df['timestamp'], df['close'], label='Preço BTC', color='royalblue')
    plt.title(f'Monitor de Trading - Última Atualização: {datetime.now().strftime("%d/%m %H:%M")}')
    plt.ylabel('Preço (USDT)')
    plt.grid(True)
    
    # Sinais
    if 'target' in df.columns:
        signals = df[df['target'] == 1]
        plt.scatter(signals['timestamp'], signals['close'], 
                   color='green', marker='^', label='Sinais de Compra')
    
    plt.legend()
    
    # Volatilidade
    plt.subplot(2, 1, 2)
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(365)
    plt.plot(df['timestamp'], df['volatility'], color='purple')
    plt.ylabel('Volatilidade Anualizada')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('trading_report.png', dpi=150)
    
    # HTML
    html = f"""
    <html>
    <head><title>Relatório de Trading</title></head>
    <body>
        <h1>Relatório Completo</h1>
        <p>Último sinal: <strong>{last_signal}</strong></p>
        <p>Win rate histórico: <strong>{win_rate:.2%}</strong></p>
        <img src="trading_report.png" width="100%">
    </body>
    </html>
    """
    
    with open('report.html', 'w') as f:
        f.write(html)

if __name__ == "__main__":
    generate_report()
