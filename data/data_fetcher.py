import os
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from dotenv import load_dotenv
import json
import sys

# Ajoutez le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class DataFetcher:
    def __init__(self, config):
        self.client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))
        self.symbol = config['symbol'].replace('/', '')
        self.data_path = os.path.abspath(config.get('data_path', 'data/datasets/solusdt_historical_data.csv'))

    def fetch_historical_data(self, days=1, interval='1m'):
        """Récupère les données OHLC et génère un order book simulé"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            klines = self.client.futures_klines(
                symbol=self.symbol,
                interval=interval,
                start_str=start_date.strftime('%d %b %Y'),
                end_str=end_date.strftime('%d %b %Y')
            )

            data = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])[['timestamp', 'open', 'high', 'low', 'close']]

            # Conversion des types
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close']:
                data[col] = pd.to_numeric(data[col])
            
            # Génération de l'order book simulé
            data['order_book'] = data.apply(self._generate_order_book, axis=1)
            
            # Sauvegarde
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            data.to_csv(self.data_path, index=False)
            
            print(f"Données sauvegardées dans {self.data_path}")
            return True

        except Exception as e:
            print(f"Erreur: {str(e)}")
            return False

    def _generate_order_book(self, row):
        """Génère un order book simulé avec volume"""
        spread = (row['high'] - row['low']) * 0.1
        return json.dumps({
            'timestamp': row['timestamp'].isoformat(),
            'bids': [{'price': float(row['low']), 'qty': 1.0}],
            'asks': [{'price': float(row['high']), 'qty': 1.0}],
            'last_price': float(row['close']),
            'volume': 100.0  # Volume simulé
        })

if __name__ == "__main__":
    # Utilisez un import absolu pour éviter le problème de relative import
    from config.config import load_config
    config = load_config()
    fetcher = DataFetcher(config)
    fetcher.fetch_historical_data()