import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncio
import websockets
import json
import ccxt.async_support as ccxt
import pandas as pd
import os
from core.logger import Logger
from config.config import load_config


class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.websocket_url = config.get('websocket_url', 'wss://stream.binance.com:9443/ws')
        self.symbol = config['symbol'].lower().replace('/', '')
        self.order_book = {'bids': [], 'asks': []}
        self.running = False
        self.exchange = ccxt.binance({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True,
        })

    async def connect_websocket(self):
        subscription = {
            "method": "SUBSCRIBE",
            "params": [f"{self.symbol}@depth20@100ms"],
            "id": 1
        }
        
        async with websockets.connect(self.websocket_url) as websocket:
            await websocket.send(json.dumps(subscription))
            self.running = True
            self.logger.info(f"WebSocket connected for {self.symbol}")
            
            # Remplacement de "Standing" par une condition pour maintenir la connexion
            while self.running:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if 'bids' in data and 'asks' in data:
                        self.order_book = {
                            'bids': [{'price': p, 'volume': v} for p, v in data['bids']],
                            'asks': [{'price': p, 'volume': v} for p, v in data['asks']]
                        }
                except Exception as e:
                    self.logger.error(f"WebSocket error: {str(e)}")
                    await asyncio.sleep(1)

    async def get_order_book(self):
        if not self.running:
            asyncio.create_task(self.connect_websocket())
            await asyncio.sleep(1)
        return self.order_book

    def stop(self):
        self.running = False

    async def fetch_historical_order_book(self, limit=1000, output_file="data/datasets/order_book_history.csv"):
        """Récupère des données historiques d'order book et les sauvegarde."""
        snapshots = []
        self.logger.info(f"Fetching historical order book data for {self.config['symbol']}")
        
        try:
            for _ in range(limit):
                order_book = await self.exchange.fetch_order_book(self.config['symbol'], limit=20)
                snapshot = {
                    'timestamp': pd.Timestamp.now().isoformat(),
                    'order_book': json.dumps(order_book)
                }
                snapshots.append(snapshot)
                await asyncio.sleep(0.1)
                
            df = pd.DataFrame(snapshots)
            os.makedirs("data/datasets", exist_ok=True)
            df.to_csv(output_file, index=False)
            self.logger.info(f"Historical data saved to {output_file} ({len(snapshots)} snapshots)")
            return df
        
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data: {str(e)}")
            return None

    async def close(self):
        await self.exchange.close()


if __name__ == "__main__":
    config = load_config()
    fetcher = DataFetcher(config)
    
    async def main():
        await fetcher.fetch_historical_order_book(limit=1000)
        await fetcher.close()
    
    asyncio.run(main())
