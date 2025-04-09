import numpy as np
import pandas as pd
from core.logger import Logger

class Metrics:
    def __init__(self):
        self.logger = Logger()

    def calculate_metrics(self, trades, initial_balance):
        """Calcule les métriques HFT à partir d'une liste de trades."""
        if not trades:
            return {"error": "No trades to analyze"}

        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calcul du solde cumulé
        df['cumulative_profit'] = df['profit'].cumsum()
        final_balance = initial_balance + df['cumulative_profit'].iloc[-1]

        # 1. Winrate
        win_trades = len(df[df['profit'] > 0])
        total_trades = len(df)
        winrate = win_trades / total_trades if total_trades > 0 else 0

        # 2. Drawdown maximal
        df['balance'] = initial_balance + df['cumulative_profit']
        rolling_max = df['balance'].cummax()
        drawdown = rolling_max - df['balance']
        max_drawdown = drawdown.max()
        max_drawdown_pct = (max_drawdown / rolling_max) * 100 if rolling_max.max() > 0 else 0

        # 3. Ratio de Sharpe (simplifié, annualisé)
        returns = df['profit'] / initial_balance
        sharpe_ratio = (returns.mean() * np.sqrt(252)) / returns.std() if returns.std() != 0 else 0

        # 4. Latence simulée (temps moyen entre trades)
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
        avg_latency = df['time_diff'].mean()

        # 5. Profit Factor
        gross_profit = df[df['profit'] > 0]['profit'].sum()
        gross_loss = abs(df[df['profit'] < 0]['profit'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

        metrics = {
            'total_trades': total_trades,
            'winrate': winrate,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio,
            'avg_latency': avg_latency,
            'profit_factor': profit_factor,
            'final_balance': final_balance,
            'return_pct': ((final_balance - initial_balance) / initial_balance) * 100
        }

        self.logger.info(f"Metrics calculated: {metrics}")
        return metrics

    def export_report(self, metrics, filepath="backtest/reports/metrics_report.txt"):
        """Exporte les métriques dans un fichier."""
        with open(filepath, 'w') as f:
            f.write("Backtest Metrics Report\n")
            f.write("======================\n")
            for key, value in metrics.items():
                f.write(f"{key.replace('_', ' ').title()}: {value:.4f}\n")
        self.logger.info(f"Metrics report exported to {filepath}") 
