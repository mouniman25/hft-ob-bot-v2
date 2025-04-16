import os
from dotenv import load_dotenv

def load_config():
    """Charge la configuration avec valeurs par défaut"""
    load_dotenv()
    return {
        'api_key': os.getenv('API_KEY'),
        'api_secret': os.getenv('API_SECRET'),
        'symbol': 'SOLUSDT',  # Format correct pour Binance
        'data_path': 'data/datasets/solusdt_historical_data.csv',
        'min_imbalance_threshold': 0.15,
        'initial_balance': 10000,
        'base_position_size': 0.01,
        'max_position': 0.1,
        'max_loss': -500
    }