from core.logger import Logger

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.logger = Logger()
        self.max_position = config.get('max_position', 1000)
        self.max_loss = config.get('max_loss', -500)
        self.current_position = 0
        self.current_pnl = 0

    def check_risk_limits(self):
        if abs(self.current_position) > self.max_position:
            self.logger.warning("Max position limit exceeded")
            return False
        if self.current_pnl < self.max_loss:
            self.logger.warning("Max loss limit exceeded")
            return False
        return True

    def update_position(self, order):
        if order['side'] == 'buy':
            self.current_position += order['amount']
        else:
            self.current_position -= order['amount']

    def update_pnl(self, profit):
        self.current_pnl += profit 
