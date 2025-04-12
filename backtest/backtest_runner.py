import sys
import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Ajout du chemin parent pour accéder aux modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        self.running = True

    def parse_order_book(self, order_book_data):
        """Convertit les données de l'order book en format structuré"""
        try:
            if isinstance(order_book_data, dict):
                return order_book_data
            elif isinstance(order_book_data, str):
                # Exemple de format attendu : "timestamp,open,high,low,close,volume..."
                data = pd.read_csv(order_book_data)
                return data.to_dict('records')[0]
            else:
                self.logger.error("Format d'order book non supporté")
                return None
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing : {str(e)}")
            return None

    async def run_backtest(self, historical_data_path):
        """Exécute le backtest sur les données historiques"""
        try:
            # Chargement des données
            self.logger.info(f"Chargement des données depuis : {historical_data_path}")
            data = pd.read_csv(historical_data_path)
            
            if data.empty:
                self.logger.error("Aucunes données trouvées dans le fichier")
                return None

            # Initialisation
            trades = []
            initial_balance = self.config.get('initial_balance', 10000)
            balance = initial_balance
            current_pnl = 0

            self.logger.info(f"Backtest initialisé avec un balance de : {initial_balance}")

            # Traitement des données
            for index, row in data.iterrows():
                try:
                    self.logger.debug(f"Traitement de la row {index}...")
                    # Parsing de l'order book
                    order_book = self.parse_order_book(row['order_book'])
                    if not order_book:
                        self.logger.warning(f"Aucun order book valide pour la row {index}")
                        continue

                    self.logger.debug(f"Order book parsed : {order_book}")

                    # Génération du signal
                    signal = await self.strategy.generate_signal(order_book)
                    if signal:
                        self.logger.debug(f"Signal reçu : {signal}")
                        # Exécution simulée
                        simulated_order = {
                            'side': signal['side'],
                            'price': float(order_book['asks'][0]['price']) if signal['side'] == 'buy' 
                                       else float(order_book['bids'][0]['price']),
                            'amount': self.executor.calculate_position_size(signal)
                        }

                        # Calcul du profit
                        profit = self.calculate_profit(simulated_order, order_book)
                        balance += profit
                        current_pnl += profit

                        # Enregistrement du trade
                        trades.append({
                            'timestamp': row['timestamp'],
                            'side': signal['side'],
                            'price': simulated_order['price'],
                            'amount': simulated_order['amount'],
                            'profit': profit
                        })

                        self.logger.info(f"Trade exécuté : {signal['side']} @ {simulated_order['price']} "
                                       f"Profit : {profit}")

                    self.logger.debug(f"Balance actuel : {balance}")
                    self.logger.debug(f"Current PNL : {current_pnl}")

                except Exception as e:
                    self.logger.error(f"Erreur lors du traitement de la row {index}: {str(e)}")
                    continue

            # Calcul des métriques
            if trades:
                metrics_result = self.metrics.calculate_metrics(trades, initial_balance)
                self.logger.info(f"Backtest terminé. Résultats finaux : {metrics_result}")
                
                # Sauvegarde des résultats
                df_results = pd.DataFrame(trades)
                output_path = os.path.join('backtest', 'reports', 'backtest_results.csv')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                df_results.to_csv(output_path, index=False)
                self.logger.info(f"Résultats sauvegardés dans : {output_path}")
                return metrics_result
            else:
                self.logger.warning("Aucun trade exécuté pendant le backtest")
                return None

        except Exception as e:
            self.logger.error(f"Erreur fatale lors du backtest : {str(e)}")
            return None

    def calculate_profit(self, order, order_book):
        """Calcule le profit d'une transaction"""
        try:
            # Calcul basé sur le prix d'exécution et le spread
            spread = float(order_book['asks'][0]['price']) - float(order_book['bids'][0]['price'])
            # Pour ce simulateur, nous supposons que le profit est basé sur le spread
            profit = order['amount'] * spread
            self.logger.debug(f"Profit calculé : {profit}")
            return profit
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du profit : {str(e)}")
            return 0

if __name__ == "__main__":
    from config import load_config
    config = load_config()
    runner = BacktestRunner(config)
    runner.run_backtest("data/datasets/solusdt_historical_data.csv")
