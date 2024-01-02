import math
import alpaca_backtrader_api
import alpaca_trade_api as tradeapi
import backtrader as bt
from datetime import datetime

class SMAStrategy(bt.Strategy):
    params = (
        ("short_period", 50),
        ("long_period", 200),
    )

    def __init__(self):
        self.short_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.long_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        # Check if data is available
        if self.data.close[0] is None or self.data.close[-1] is None:
            return

        # Check for NaN values
        if any(math.isnan(val) for val in [self.short_sma[0], self.long_sma[0]]):
            return

        print(f"Date: {self.data.datetime.date(0)}, Close: {self.data.close[0]}, Short SMA: {self.short_sma[0]}, Long SMA: {self.long_sma[0]}")

        if self.short_sma > self.long_sma:
            self.buy()
            print("Buy Signal")
        elif self.short_sma < self.long_sma:
            self.sell()
            print("Sell Signal")


if __name__ == "__main__":
    # Alpaca API credentials
    api_key = 'AKPXPQBL324SMW2VKHFN'
    api_secret = 'WxnhCpsgDu3ZPbxcNCsiM2igRPooaEXCHTjoaX1g'
    base_url = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

    # Create Alpaca data feed
    data = alpaca_backtrader_api.AlpacaData(
        dataname='AAPL',
        historical=True,
        fromdate=datetime(2021, 1, 1),
        todate=datetime(2022, 1, 1),
        timeframe=bt.TimeFrame.Days,
        historical_fill=True,
        backfill_start=False,
        historical_weekend=True,
    )

    # Initialize Backtrader Cerebro engine
    cerebro = bt.Cerebro()

    # Add Alpaca data feed to engine
    cerebro.adddata(data)

    # Add strategy to engine
    cerebro.addstrategy(SMAStrategy)

    # Set initial cash amount for backtesting
    cerebro.broker.set_cash(100000)

    # Set commission for Alpaca
    cerebro.broker.setcommission(commission=0.0)

    # Print starting cash amount
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue()}")

    # Run the backtest
    cerebro.run()

    # Print ending cash amount
    print(f"Ending Portfolio Value: {cerebro.broker.getvalue()}")
