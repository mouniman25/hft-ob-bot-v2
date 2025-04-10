import numpy as np
from sklearn.ensemble import RandomForestClassifier
from data.data_cleaner import DataCleaner
from machine_learning.model_predictor import MLPredictor

class MLStrategy:
    def __init__(self, config):
        self.config = config
        self.predictor = MLPredictor()
        self.cleaner = DataCleaner()
        self.min_imbalance_threshold = config.get('min_imbalance_threshold', 0.2)
        self.model = RandomForestClassifier(n_estimators=100)

    async def generate_signal(self, order_book):
        cleaned_data = self.cleaner.process_order_book(order_book)
        imbalance = self.calculate_imbalance(cleaned_data)
        features = self.prepare_features(cleaned_data, imbalance)
        prediction = await self.predictor.predict(features)
        if prediction > 0.6 and imbalance > self.min_imbalance_threshold:
            return {"side": "buy", "confidence": prediction, "imbalance": imbalance}
        elif prediction < 0.4 and imbalance < -self.min_imbalance_threshold:
            return {"side": "sell", "confidence": 1-prediction, "imbalance": imbalance}
        return None

    def calculate_imbalance(self, order_book):
        bid_volume = sum([float(level['volume']) for level in order_book['bids'][:5]])
        ask_volume = sum([float(level['volume']) for level in order_book['asks'][:5]])
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)

    def prepare_features(self, order_book, imbalance):
        features = {
            'imbalance': imbalance,
            'spread': float(order_book['asks'][0]['price']) - float(order_book['bids'][0]['price']),
            'bid_depth': sum([float(l['volume']) for l in order_book['bids'][:10]]),
            'ask_depth': sum([float(l['volume']) for l in order_book['asks'][:10]])
        }
        return np.array([list(features.values())])

    def train_model(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
