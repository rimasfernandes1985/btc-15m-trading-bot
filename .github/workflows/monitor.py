import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def generate_report():
    # Carregar dados
    df = pd.read_csv('ml_ready_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Gráfico de preços
    plt.figure(figsize=(14, 7))
    plt.plot(df['timestamp'], df['close'], label='BTC/USDT', linewidth=2)
    plt.title('Histórico de Preços - Últimas 24h', fontsize=16)
    plt.xlabel('Horário', fontsize=12)
    plt.ylabel('Preço (USDT)', fontsize=12)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('price_chart.png', dpi=300)
    
    # Relatório HTML
    report = f"""
    <html>
    <head>
        <title>Relatório de Trading</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            h1 {{ color: #333; }}
            .info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Relatório Diário</h1>
        <p>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <div class="info">
            <h3>Dados Estatísticos</h3>
            <p>Período: {len(df)} candles (15min)</p>
            <p>Último preço: {df['close'].iloc[-1]:.2f} USDT</p>
        </div>
        
        <img src="price_chart.png" width="100%">
    </body>
    </html>
    """
    
    with open('report.html', 'w') as f:
        f.write(report)

if __name__ == "__main__":
    generate_report()
