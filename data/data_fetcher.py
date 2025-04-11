import os
import pandas as pd
from binance.client import Client
from datetime import datetime
from dotenv import load_dotenv
import asyncio

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Client(API_KEY, API_SECRET)

class DataFetcher:
    def __init__(self, symbol, interval, start_str, end_str):
        self.symbol = symbol
        self.interval = interval
        self.start_str = start_str
        self.end_str = end_str

    def fetch_historical_data(self):
        klines = client.futures_klines(
            symbol=self.symbol, 
            interval=self.interval, 
            start_str=self.start_str, 
            end_str=self.end_str
        )
        data = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
            'quote_asset_volume', 'number_of_trades', 
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        data['close'] = pd.to_numeric(data['close'])
        data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
        data.dropna(inplace=True)
        return data

async def main():
    fetcher = DataFetcher(
        symbol='SOLUSDT', 
        interval=Client.KLINE_INTERVAL_1MINUTE, 
        start_str='1 Jan 2021', 
        end_str='1 Jan 2022'
    )
    data = fetcher.fetch_historical_data()
    data.to_csv('C:/Users/pc/Desktop/hft_ob_bot/data/datasets/solusdt_historical_data.csv')
    print("Data fetched and saved to C:/Users/pc/Desktop/hft_ob_bot/data/datasets/solusdt_historical_data.csv")

if __name__ == "__main__":
    asyncio.run(main())
