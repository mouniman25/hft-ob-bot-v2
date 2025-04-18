import asyncio
from core.ml_strategy import MLStrategy
from core.order_executor import OrderExecutor
from core.risk_manager import RiskManager
from core.logger import Logger
from data.data_fetcher import DataFetcher

class HFTBot:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.strategy = MLStrategy(config)
        self.executor = OrderExecutor(config)
        self.risk_manager = RiskManager(config)
        self.data_fetcher = DataFetcher(config)
        self.running = True

    async def start(self):
        self.logger.info("Starting HFT Bot...")
        while self.running:
            try:
                # Récupération des données de l'order book en temps réel
                order_book = await self.data_fetcher.get_order_book()
                # Analyse de la stratégie
                signal = await self.strategy.generate_signal(order_book)
                if signal:
                    # Exécution de l'ordre
                    if self.risk_manager.approve(signal):
                        await self.executor.execute_order(signal)
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(1)

    def stop(self):
        self.running = False
        self.logger.info("Bot stopped")

if __name__ == "__main__":
    config = {}  # Charger la configuration appropriée
    bot = HFTBot(config)
    asyncio.run(bot.start())
