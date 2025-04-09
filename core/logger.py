import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs", log_file=None):
        """Initialise le logger avec fichier et console."""
        self.logger = logging.getLogger('HFTBot')
        self.logger.setLevel(logging.INFO)

        # Format du log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler pour le fichier
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if log_file is None:
            log_file = f"{log_dir}/hft_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

if __name__ == "__main__":
    # Test du logger
    logger = Logger()
    logger.info("Logger initialized")
    logger.warning("This is a warning")
    logger.error("This is an error") 
