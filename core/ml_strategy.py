import numpy as np
import logging

class MLStrategy:
    def __init__(self, config):
        self.config = config
        self.min_imbalance_threshold = config.get('min_imbalance_threshold', 0.2)
        self.logger = logging.getLogger(__name__)

    async def generate_signal(self, order_book):
        """Version simplifiée pour debug"""
        try:
            # Calcul d'imbalance simulé
            bid = order_book['bids'][0]['price']
            ask = order_book['asks'][0]['price']
            mid = (bid + ask) / 2
            imbalance = (ask - mid) / (ask - bid)
            
            # Logique de trading simplifiée
            if imbalance > self.min_imbalance_threshold:
                return {'side': 'buy', 'confidence': 0.7}
            elif imbalance < -self.min_imbalance_threshold:
                return {'side': 'sell', 'confidence': 0.7}
            return None

        except Exception as e:
            self.logger.error(f"Erreur génération signal: {str(e)}")
            return None