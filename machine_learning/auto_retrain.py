import asyncio
import numpy as np
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
        self.retrain_interval = config.get('retrain_interval', 3600)  # 1 heure par défaut

    async def collect_training_data(self, order_book, executed_trade):
        cleaned_data = self.cleaner.process_order_book(order_book)
        features = self.strategy.prepare_features(cleaned_data, 
            self.strategy.calculate_imbalance(cleaned_data))
        
        # Label: 1 si profit positif, 0 sinon
        label = 1 if executed_trade.get('profit', 0) > 0 else 0
        
        self.training_data.append((features, label))
        self.logger.info(f"Training sample added. Total: {len(self.training_data)}")

    async def retrain_model(self):
        while True:
            await asyncio.sleep(self.retrain_interval)
            
            if len(self.training_data) >= self.min_samples:
                try:
                    X = np.vstack([sample[0] for sample in self.training_data])
                    y = np.array([sample[1] for sample in self.training_data])
                    
                    self.predictor.model.fit(X, y, epochs=10, batch_size=32, verbose=0)
                    self.predictor.save_model()
                    self.logger.info("Model retrained and saved")
                    
                    # Réinitialisation partielle des données (garde 50% pour stabilité)
                    self.training_data = self.training_data[len(self.training_data)//2:]
                except Exception as e:
                    self.logger.error(f"Retraining failed: {str(e)}")

    def start(self):
        asyncio.create_task(self.retrain_model()) 
