import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from core.logger import Logger
from core.ml_strategy import MLStrategy
from core.order_executor import OrderExecutor
from backtest.metrics import Metrics
from data.data_fetcher import DataFetcher

class BacktestRunner:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.strategy = MLStrategy(config)
        self.executor = OrderExecutor(config)
        self.metrics = Metrics()
        self.data_fetcher = DataFetcher(config)

    async def run_backtest(self, historical_data_path):
        data = pd.read_csv(historical_data_path)
        trades = []
        initial_balance = self.config.get('initial_balance', 10000)
        balance = initial_balance
        for index, row in data.iterrows():
            order_book = self.parse_order_book(row['order_book'])
            signal = await self.strategy.generate_signal(order_book)
            if signal:
                simulated_order = {
                    'side': signal['side'],
                    'price': float(order_book['asks'][0]['price']) if signal['side'] == 'buy' 
                            else float(order_book['bids'][0]['price']),
                    'amount': self.executor.calculate_position_size(signal)
                }
                profit = self.calculate_profit(simulated_order, order_book)
                balance += profit
                trades.append({
                    'timestamp': row['timestamp'],
                    'side': signal['side'],
                    'price': simulated_order['price'],
                    'amount': simulated_order['amount'],
                    'profit': profit
                })
        metrics_result = self.metrics.calculate_metrics(trades, initial_balance)
        self.logger.info(f"Backtest completed. Final balance: {balance}")
        # Save the backtest results
        pd.DataFrame(trades).to_csv('C:/Users/pc/Desktop/hft_ob_bot/backtest/reports/backtest_results.csv')
        return metrics_result
