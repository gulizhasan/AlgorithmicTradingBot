
# Alpaca Trading Bot

## Description
This Alpaca Trading Bot is an automated stock trading software that utilizes the Alpaca Trade API. It's designed to execute trades based on technical analysis indicators such as Moving Averages, RSI (Relative Strength Index), and MACD (Moving Average Convergence Divergence).

## Features
- Real-time market data processing.
- Implements trading strategies based on technical indicators.
- Supports multiple stock symbols.
- Logging of trading activities and errors for review and analysis.

## Requirements
- Python 3.x
- Alpaca Trade API account
- Required Python libraries: `pandas`, `talib`, `websocket-client`, `alpaca-trade-api`

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/gulizhasan/AlgorithmicTradingBot
   ```
2. Navigate to the project directory:
   ```
   cd alpaca-trading-bot
   ```
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. Set up your Alpaca Trade API keys in the `config.py` file:
   ```python
   API_KEY = 'Your Alpaca API Key'
   SECRET_KEY = 'Your Alpaca Secret Key'
   BASE_URL = 'https://paper-api.alpaca.markets'  # Use the paper trading URL for testing
   ```
2. Adjust the trading parameters in the script as needed (e.g., `symbols`, `short_window`, `long_window`, `qty`).

## Usage
To start the trading bot, run the following command in the terminal:
```
python alpacaDemo.py
```

## Testing
To ensure the functionality of the bot, run the pytest tests:
```
pytest
```

## Disclaimer
This bot is for educational purposes only. Financial trading involves substantial risk, and it's important to understand these risks before using the software in a live environment.
