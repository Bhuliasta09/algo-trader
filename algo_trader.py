import os
import requests
import ccxt
import pandas_ta as ta
import pandas as pd
from transformers import pipeline

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Initialize the blockchain/exchange connection
exchange = ccxt.binance({
    'apiKey': os.environ.get("EXCHANGE_API_KEY"),
    'secret': os.environ.get("EXCHANGE_SECRET"),
    'enableRateLimit': True,
})

# Define the crypto assets you want the bot to trade
WATCHLIST = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'LINK/USDT', 'ADA/USDT']
def get_crypto_score(symbol):
    try:
        # Fetch the last 20 days of market data from the exchange
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=20)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # Calculate RSI (Relative Strength Index)
        df['RSI'] = ta.rsi(df['close'], length=14)
        current_rsi = df['RSI'].iloc[-1]

        tech_score = 0
        if current_rsi < 30:
           tech_score += 30 # Oversold (Strong Buy)
        elif 30 <= current_rsi <= 70:
            tech_score += 15 # Neutral

        return tech_score
except Exception as e:
    print(f"Error fetching data for {symbol}: {e}")
    return 0
                
# Evaluate all coins in the watchlist
scores = {symbol: get_crypto_score(symbol) for symbol in WATCHLIST}
top_picks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

BUDGET = 1500
ALLOCATIONS = [0.10, 0.10, 0.10]

# Execute the trades
for i, (symbol, score) in enumerate(top_picks):
    # Only execute if the score indicates a favorable setup
    if score >= 15:
        investment_usd = BUDGET * ALLOCATIONS[i]

        try:
            # Get the current coin price to calculate the order size
            current_price = exchange.fetch_ticker(symbol)['last']
            amount_to_buy = investment_usd / current_price

            # LIVE TRADE EXECUTION
            order = exchange.create_market_buy_order(symbol, amount_to_buy)
            print(f"Successfully bought {amount_to_buy} of {symbol}")

except Exception as e:
    print(f"Failed to execute trade for {symbol}: {e}")
            print(f"Successfully bought {amount_to_buy} of {symbol}")
        except Exception as e:
            print(f"Failed to execute trade for {symbol}: {e}")
        "inline": False
    })

requests.post(WEBHOOK_URL, json={
    "username": "Algo-Trader",
    "embeds": [{
        "title": "🚨 Monthly Robinhood Allocations",
        "color": 5763719,
        "fields": embed_fields
    }]
})
