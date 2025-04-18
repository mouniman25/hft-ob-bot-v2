import ccxt.async_support as ccxt
from core.logger import Logger

class OrderExecutor:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.exchange = ccxt.binance({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True,
        })

    async def execute_order(self, signal):
        order_type = 'limit'
        if signal['side'] == 'buy':
            price = await self.get_best_bid()
        else:
            price = await self.get_best_ask()
        amount = self.calculate_position_size(signal)
        order = await self.exchange.create_order(
            symbol=self.config['symbol'],
            type=order_type,
            side=signal['side'],
            amount=amount,
            price=price
        )
        self.logger.info(f"Order executed: {order}")

    async def get_best_bid(self):
        ticker = await self.exchange.fetch_order_book(self.config['symbol'])
        return float(ticker['bids'][0][0])

    async def get_best_ask(self):
        ticker = await self.exchange.fetch_order_book(self.config['symbol'])
        return float(ticker['asks'][0][0])

    def calculate_position_size(self, signal):
        # Calculer la taille de la position en fonction du signal et de la configuration
        return 1  # Exemple simplifi�
