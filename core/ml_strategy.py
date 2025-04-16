import numpy as np
import logging
from sklearn.ensemble import RandomForestClassifier
import joblib

class MLStrategy:
    def __init__(self, config):
        self.config = config
        self.min_imbalance_threshold = config.get('min_imbalance_threshold', 0.2)
        self.spread_threshold = config.get('spread_threshold', 0.002)
        self.model_confidence_threshold = config.get('model_confidence_threshold', 0.6)
        self.stop_loss_pct = config.get('STOP_LOSS_PCT', 0.003)
        self.profit_target_pct = config.get('PROFIT_TARGET_PCT', 0.005)
        self.position_size_pct = config.get('POSITION_SIZE_PCT', 0.01)
        self.cooldown_period = config.get('COOLDOWN_PERIOD', 3)
        self.model = joblib.load(config.get('model_path', 'models/rf_model.joblib'))
        self.logger = logging.getLogger(__name__)

    def calculate_features(self, order_book):
        bid_vol = sum([level['volume'] for level in order_book['bids'][:5]])
        ask_vol = sum([level['volume'] for level in order_book['asks'][:5]])
        bid_vol_top3 = sum([level['volume'] for level in order_book['bids'][:3]])
        ask_vol_top3 = sum([level['volume'] for level in order_book['asks'][:3]])
        prices = [level['price'] for level in order_book['bids'][:5] + order_book['asks'][:5]]
        
        features = {
            'desiquilibre_volume': (bid_vol - ask_vol) / (bid_vol + ask_vol),
            'volatilite_volume_bid': np.std([level['volume'] for level in order_book['bids'][:5]]) / np.mean([level['volume'] for level in order_book['bids'][:5]]),
            'volatilite_volume_ask': np.std([level['volume'] for level in order_book['asks'][:5]]) / np.mean([level['volume'] for level in order_book['asks'][:5]]),
            'ratio_liquidite_top3': bid_vol_top3 / ask_vol_top3,
            'momentum_prix': (prices[0] - prices[-1]) / prices[-1]
        }
        return features

    async def generate_signal(self, order_book):
        try:
            bid = order_book['bids'][0]['price']
            ask = order_book['asks'][0]['price']
            mid = (bid + ask) / 2
            spread = (ask - bid) / mid

            if spread > self.spread_threshold:
                return None

            features = self.calculate_features(order_book)
            imbalance = features['desiquilibre_volume']
            model_input = np.array(list(features.values())).reshape(1, -1)
            confidence = self.model.predict_proba(model_input)[0][1]

            if imbalance > self.min_imbalance_threshold and confidence > self.model_confidence_threshold:
                return {
                    'signal': 'LONG',
                    'confidence': confidence,
                    'profit_target': self.profit_target_pct,
                    'stop_loss': self.stop_loss_pct,
                    'quantity': self.position_size_pct
                }
            elif imbalance < -self.min_imbalance_threshold and confidence > self.model_confidence_threshold:
                return {
                    'signal': 'SHORT',
                    'confidence': confidence,
                    'profit_target': self.profit_target_pct,
                    'stop_loss': self.stop_loss_pct,
                    'quantity': self.position_size_pct
                }
            return None

        except Exception as e:
            self.logger.error(f"Erreur génération signal: {str(e)}")
            return None
