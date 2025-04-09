import pandas as pd
import numpy as np
from core.ml_strategy import MLStrategy
from core.order_executor import OrderExecutor
from backtest.metrics import Metrics
from data.data_fetcher import DataFetcher
from core.logger import Logger

class BacktestRunner:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.strategy = MLStrategy(config)
        self.executor = OrderExecutor(config)  # Simulation mode
        self.metrics = Metrics()
        self.data_fetcher = DataFetcher(config)

    async def run_backtest(self, historical_data_path):
        # Chargement des données historiques (format: timestamp, order_book_snapshot)
        data = pd.read_csv(historical_data_path)
        trades = []
        initial_balance = self.config.get('initial_balance', 10000)
        balance = initial_balance
        
        for index, row in data.iterrows():
            order_book = self.parse_order_book(row['order_book'])
            signal = await self.strategy.generate_signal(order_book)
            
            if signal:
                # Simulation d'exécution
                simulated_order = {
                    'side': signal['side'],
                    'price': float(order_book['asks'][0]['price']) if signal['side'] == 'buy' 
                            else float(order_book['bids'][0]['price']),
                    'amount': self.executor.calculate_position_size(signal)
                }
                
                # Calcul simple du profit (à affiner selon votre marché)
                profit = self.calculate_profit(simulated_order, order_book)
                balance += profit
                trades.append({
                    'timestamp': row['timestamp'],
                    'side': signal['side'],
                    'price': simulated_order['price'],
                    'amount': simulated_order['amount'],
                    'profit': profit
                })
        
        # Calcul des métriques HFT
        metrics_result = self.metrics.calculate_metrics(trades, initial_balance)
        self.logger.info(f"Backtest completed. Final balance: {balance}")
        return metrics_result

    def parse_order_book(self, order_book_str):
        # À adapter selon le format de vos données historiques
        return json.loads(order_book_str)

    def calculate_profit(self, order, next_order_book):
        # Simulation simple: profit basé sur le prochain meilleur prix
        if order['side'] == 'buy':
            exit_price = float(next_order_book['bids'][0]['price'])
            return (exit_price - order['price']) * order['amount']
        else:
            exit_price = float(next_order_book['asks'][0]['price'])
            return (order['price'] - exit_price) * order['amount'] 
