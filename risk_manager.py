import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self):
        self.df = pd.read_csv('ml_ready_data.csv').tail(100)
        
    def calculate_volatility(self):
        returns = np.log(self.df['close'] / self.df['close'].shift(1))
        return returns.std() * np.sqrt(365 * 24 * 4)  # Volatilidade anualizada
        
    def get_position_size(self, balance):
        volatility = self.calculate_volatility()
        risk_factor = min(0.05 / volatility, 0.1)  # Máximo 10% do capital
        return balance * risk_factor
        
    def check_market_conditions(self):
        last_close = self.df['close'].iloc[-1]
        ema_20 = self.df['close'].ewm(span=20).mean().iloc[-1]
        return "HIGH" if last_close < ema_20 else "NORMAL"

if __name__ == "__main__":
    rm = RiskManager()
    print(f"Volatilidade: {rm.calculate_volatility():.2%}")
    print(f"Condição: {rm.check_market_conditions()}")
