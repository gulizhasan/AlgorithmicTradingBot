import threading
from alpaca_trade_api import REST
import websocket
import json
import pandas as pd
from datetime import datetime
from time import sleep
import logging
import talib

# Configuration file for the keys and base URL
import config

# Setup logging
logging.basicConfig(filename='alpaca_bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Initialize Alpaca REST API client
try:
    api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)
    logging.info("Alpaca REST API client initialized successfully")
except Exception as e:
    logging.error(f"Error initializing Alpaca REST API client: {str(e)}")
    exit(1)

# Define trading parameters
symbols = ["AAPL", "MSFT", "GOOGL"]  # Add or remove symbols as needed
short_window = 20  # Short-term moving average window
long_window = 50   # Long-term moving average window
qty = 10           # Number of shares to buy/sell

# Initialize data storage for each symbol
historical_data = {symbol: pd.DataFrame(columns=["timestamp", "close"]) for symbol in symbols}
ema_short = {symbol: pd.Series() for symbol in symbols}
ema_long = {symbol: pd.Series() for symbol in symbols}
rsi_values = {symbol: pd.Series() for symbol in symbols}
macd_values = {symbol: pd.Series() for symbol in symbols}
macd_signal_values = {symbol: pd.Series() for symbol in symbols}

# Function to check if the market is open
def is_market_open():
    """
    Check if the market is currently open
    """
    clock = api.get_clock()
    return clock.is_open

def analyze_market_data(symbol, data):
    global historical_data, ema_short, ema_long, rsi_values, macd_values, macd_signal_values

    # Check if market is open before proceeding
    if not is_market_open():
        logging.info("Market is closed. Skipping analysis for now.")
        return

    try:
        # Add new data to historical_data for the specific symbol
        timestamp = datetime.fromtimestamp(data['t'] / 1000)
        close_price = data['c']
        historical_data[symbol] = historical_data[symbol].append({"timestamp": timestamp, "close": close_price}, ignore_index=True)

        # Ensure enough data for analysis for the specific symbol
        if len(historical_data[symbol]) >= long_window:
            # Calculate indicators (e.g., EMAs, RSI, MACD) for the specific symbol
            ema_short[symbol] = historical_data[symbol]['close'].ewm(span=short_window, adjust=False).mean()
            ema_long[symbol] = historical_data[symbol]['close'].ewm(span=long_window, adjust=False).mean()
            rsi_values[symbol] = talib.RSI(historical_data[symbol]['close'], timeperiod=14)
            macd_values[symbol], macd_signal_values[symbol], _ = talib.MACD(historical_data[symbol]['close'],
                                                                           fastperiod=12,
                                                                           slowperiod=26,
                                                                           signalperiod=9)

            # Implement trading strategy (logic to decide when to buy/sell) for the specific symbol
            if rsi_values[symbol].iloc[-1] < 30 and not position_open(symbol, 'long'):  # RSI Buy signal
                place_order(symbol, qty, "buy")
            elif rsi_values[symbol].iloc[-1] > 70 and position_open(symbol, 'long'):  # RSI Sell signal
                place_order(symbol, qty, "sell")
            
            if macd_values[symbol].iloc[-1] > macd_signal_values[symbol].iloc[-1] and not position_open(symbol, 'long'):  # MACD Buy signal
                place_order(symbol, qty, "buy")
            elif macd_values[symbol].iloc[-1] < macd_signal_values[symbol].iloc[-1] and position_open(symbol, 'long'):  # MACD Sell signal
                place_order(symbol, qty, "sell")
    except Exception as e:
        logging.error(f"Error analyzing market data for {symbol}: {str(e)}")

def position_open(symbol, position_type):
    try:
        positions = api.list_positions()
        for position in positions:
            if position.symbol == symbol and ((position_type == 'long' and int(position.qty) > 0) or (position_type == 'short' and int(position.qty) < 0)):
                return True
        return False
    except Exception as e:
        logging.error(f"Error checking open positions for {symbol}: {str(e)}")
        return False

def place_order(symbol, quantity, action):
    try:
        if action == "buy":
            api.submit_order(
                symbol=symbol,
                qty=quantity,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
            logging.info(f"Placed order to buy {quantity} shares of {symbol}")
        elif action == "sell":
            api.submit_order(
                symbol=symbol,
                qty=quantity,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
            logging.info(f"Placed order to sell {quantity} shares of {symbol}")
    except Exception as e:
        logging.error(f"Order placement failed for {symbol}: {str(e)}")

def on_message(ws, message):
    try:
        json_message = json.loads(message)
        for symbol in symbols:
            if 'data' in json_message and json_message['stream'] == f"AM.{symbol}":
                trade_data = json_message['data']
                analyze_market_data(symbol, trade_data)
    except Exception as e:
        logging.error(f"Error processing WebSocket message: {str(e)}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")

def on_open(ws):
    logging.info("WebSocket connection opened")
    try:
        auth_data = {
            "action": "authenticate",
            "data": {"key_id": config.API_KEY, "secret_key": config.SECRET_KEY}
        }
        ws.send(json.dumps(auth_data))
        listen_message = {
            "action": "listen",
            "data": {"streams": [f"AM.{symbol}" for symbol in symbols]}
        }
        ws.send(json.dumps(listen_message))
    except Exception as e:
        logging.error(f"Error during WebSocket connection opening: {str(e)}")

# WebSocket setup
socket = "wss://paper-api.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)

# Running the WebSocket in a separate thread
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.start()

# Main loop
try:
    while True:
        sleep(60)  # Main loop doing nothing, just staying alive
except KeyboardInterrupt:
    logging.info("Script interrupted by user.")
    ws.close()
except Exception as e:
    logging.error(f"Error in the main loop: {str(e)}")
