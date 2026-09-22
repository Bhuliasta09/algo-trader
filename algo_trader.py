import os
import yfinance as yf
import requests
from transformers import pipeline
import pandas as pd
import ccxt
import pandas_ta as ta # for technical indicatoras

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# Connect to your crypto exchange
exchange = ccxt.binance({
    'apiKey': os.environ.get("EXCHANGE_API_KEY"),
    'secret': os.environ.get("EXCHANGE_SECRET"),
    'enableRateLimit': True,
})

WATCHLIST = ['BTC/USDT', ETH/USDT', 'SOL/USDT', 'LINK/USDT', 'ADA/USDT']
             
sentiment_analyzer = pipeline("text-classification", model="ProsusAI/finbert")

def get_stock_score(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    fund_score = 0
    try:
        info = ticker.info
def get_crypto_score(symbol, exchange):
    # Fetch historical blockchain/crypto data for technicals
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=20)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Calculate RSI (Relative Strength Index) for accuracy
    df['RSI'] = ta.rsi(df['close'], length=14)
    current_rsi = df['RSI'].iloc[-1]

    # Score based on RSI (Buy when oversold < 30, avoid when overbought > 70)
    tech_score = 0
    if current_rsi < 30:
        tech_score = 30
    elif 30 <= current_rsi <= 70:
        tech_score = 15

    # (Keep your FinBERT news sentiment logic here to add to tech_score)
        if news:
            headlines = [item['title'] for item in news[:5]]
            results = sentiment_analyzer(headlines)
            for res in results:
                if res['label'] == 'positive':
                    sentiment_score += 10
                elif res['label'] == 'negative':
                    sentiment_score -= 10
                sentiment_score = max(0, min(50, (sentiment_score / 2) + 25))
    except:
        pass

    return fund_score + sentiment_score

# Loop through your top picks and execute real trades
for i, (symbol, score) in enumerate(top_picks):
    # Only buy if the score passes a certain confidence threshold
    if score > 50:
        trade_allocation = BUDGET * ALLOCATIONS[i]

        # Fetch current price to calculate how much coin to buy
        current_price = exchange.fetch_ticker(symbol)['last']
        amount_to_buy = trade_allocation / current_price

        try:
            # Execute the market buy order on the blockchain/exchange
            order = exchange.create_market_buy_order(symbol, amount_to_buy)
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
