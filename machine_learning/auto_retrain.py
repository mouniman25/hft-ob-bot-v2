import asyncio
import numpy as np
import os
import joblib
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from machine_learning.model_predictor import MLPredictor
from data.data_cleaner import DataCleaner
from core.ml_strategy import MLStrategy
from core.logger import Logger

class AutoRetrainer:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.predictor = MLPredictor()
        self.cleaner = DataCleaner()
        self.strategy = MLStrategy(config)
        self.training_data = []
        self.min_samples = config.get('min_training_samples', 1000)
        self.retrain_interval = config.get('retrain_interval', 3600)

    async def collect_training_data(self, order_book, executed_trade):
        cleaned_data = self.cleaner.process_order_book(order_book)
        features = self.strategy.prepare_features(cleaned_data, 
            self.strategy.calculate_imbalance(cleaned_data))
        label = 1 if executed_trade.get('profit', 0) > 0 else 0
        self.training_data.append((features, label))
        self.logger.info(f"Training sample added. Total: {len(self.training_data)}")

    async def retrain_model(self):
        if len(self.training_data) >= self.min_samples:
            X, y = zip(*self.training_data)
            self.predictor.train(X, y)
            # Save the model and encoder
            joblib.dump(self.predictor.model, 'C:/Users/pc/Desktop/hft_ob_bot/machine_learning/models/model.pkl')
            joblib.dump(self.predictor.encoder, 'C:/Users/pc/Desktop/hft_ob_bot/machine_learning/models/encoder.pkl')
            self.logger.info("Model and encoder saved.")
