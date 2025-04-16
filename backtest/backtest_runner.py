import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import load_config

import pandas as pd
import logging
from datetime import datetime
import json

# Importation des modules manquants
from core.ml_strategy import MLStrategy
from core.order_executor import OrderExecutor
from backtest.metrics import Metrics

class BacktestRunner:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.strategy = MLStrategy(config)
        self.executor = OrderExecutor(config)
        self.metrics = Metrics()

    def parse_order_book(self, order_book_str):
        """Parse l'order book avec gestion robuste des erreurs"""
        try:
            book = json.loads(order_book_str)
            book['timestamp'] = pd.to_datetime(book['timestamp'])
            # Standardisation des clés (qty/amount)
            for side in ['bids', 'asks']:
                for level in book[side]:
                    level['amount'] = level.get('qty', level.get('amount', 1.0))
            return book
        except Exception as e:
            self.logger.error(f"Erreur parsing: {str(e)}")
            return None

    async def run_backtest(self, data_path):
        """Exécute le backtest avec logging amélioré"""
        try:
            # Chargement des données
            data = pd.read_csv(
                data_path,
                converters={'order_book': self.parse_order_book}
            )
            
            if data.empty:
                self.logger.error("Fichier de données vide")
                return None

            trades = []
            initial_balance = self.config.get('initial_balance', 10000)
            
            for index, row in data.iterrows():
                try:
                    order_book = row['order_book']
                    if not order_book:
                        continue

                    # Génération du signal
                    signal = await self.strategy.generate_signal(order_book)
                    if not signal:
                        continue

                    # Exécution
                    price = order_book['asks'][0]['price'] if signal['side'] == 'buy' \
                           else order_book['bids'][0]['price']
                    
                    trades.append({
                        'timestamp': order_book['timestamp'],
                        'side': signal['side'],
                        'price': float(price),
                        'amount': self.executor.calculate_position_size(signal),
                        'profit': (order_book['asks'][0]['price'] - order_book['bids'][0]['price']) * 0.1
                    })

                except Exception as e:
                    self.logger.error(f"Ligne {index} - Erreur: {str(e)}")
                    continue

            if trades:
                self.logger.info(f"Backtest réussi - {len(trades)} trades")
                return self.metrics.calculate_metrics(trades, initial_balance)
            else:
                self.logger.warning("Aucun trade généré")
                return None

        except Exception as e:
            self.logger.error(f"Erreur backtest: {str(e)}")
            return None

if __name__ == "__main__":
    from config.config import load_config
    import logging
    
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    runner = BacktestRunner(config)
    
    data_path = os.path.join('data', 'datasets', 'solusdt_historical_data.csv')
    asyncio.run(runner.run_backtest(data_path))