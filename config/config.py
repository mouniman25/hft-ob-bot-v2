import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        'api_key': os.getenv('API_KEY'),
        'api_secret': os.getenv('API_SECRET'),
        'symbol': 'BTC/USDT',
        'websocket_url': 'wss://stream.binance.com:9443/ws',
        'min_imbalance_threshold': 0.25,
        'base_position_size': 0.001,
        'max_position': 0.1,
        'max_loss': -500,
        'min_training_samples': 1000,
        'retrain_interval': 3600,
        'initial_balance': 10000
    }