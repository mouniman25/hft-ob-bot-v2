import matplotlib.pyplot as plt
import pandas as pd

class Visualizer:
    def __init__(self):
        pass

    def plot_backtest_results(self, trades):
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df['cumulative_profit'] = df['profit'].cumsum()

        plt.figure(figsize=(12, 6))
        plt.plot(df['cumulative_profit'], label='Cumulative Profit')
        plt.xlabel('Time')
        plt.ylabel('Cumulative Profit')
        plt.title('Backtest Results')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # Example usage
    trades = [
        {'timestamp': '2021-01-01 00:00:00', 'side': 'buy', 'price': 10, 'amount': 1, 'profit': 0.5},
        {'timestamp': '2021-01-01 00:01:00', 'side': 'sell', 'price': 10.5, 'amount': 1, 'profit': 0.5},
        # Add more trades here
    ]
    visualizer = Visualizer()
    visualizer.plot_backtest_results(trades)
