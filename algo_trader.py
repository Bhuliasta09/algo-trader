import os
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import ccxt

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- 1. CRYPTO SETUP & LOGIC ---
# Using Kraken to avoid US/GitHub Action Geo-blocks
exchange = ccxt.kraken({
    'apiKey': os.environ.get("EXCHANGE_API_KEY"),
    'secret': os.environ.get("EXCHANGE_SECRET"),
    'enableRateLimit': True,
})

CRYPTO_WATCHLIST = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

def get_crypto_score(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=20)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['RSI'] = ta.rsi(df['close'], length=14)
        current_rsi = df['RSI'].iloc[-1]

        tech_score = 0
        if current_rsi < 30:
            tech_score += 30 # Oversold (Strong Buy)
        elif 30 <= current_rsi <= 70:
            tech_score += 15 # Neutral
        return tech_score, current_rsi
    except Exception as e:
         print(f"Error fetching Crypto data for {symbol}: {e}")
         return 0, 0

# --- 2. STOCK OPTIONS SETUP & LOGIC ---
STOCK_WATCHLIST = ['SPY', 'QQQ', 'AAPL', 'NVDA']

def get_stock_score(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1mo")
        df['RSI'] = ta.rsi(df['Close'], length=14)
        current_rsi = df['RSI'].iloc[-1]

        # Determine Option Idea based on momentum
        option_idea = "CALL" if current_rsi > 50 else "PUT"
        return option_idea, current_rsi
    except Exception as e:
        print(f"Error fetching Stock data for {symbol}: {e}")
        return "NONE", 0

# --- 3. EVALUATE MARKETS ---
crypto_results = {sym: get_crypto_score(sym) for sym in CRYPTO_WATCHLIST}
stock_results = {sym: get_stock_score(sym) for sym in STOCK_WATCHLIST}

crypto_picks = sorted(crypto_results.items(), key=lambda x: x[1][0], reverse=True)[:3]

# --- 4. SEND DAILY DISCORD BROADCAST ---
# This ensures you always receive a message, regardless of whether a crypto trade executes.
discord_msg = "📊 **DAILY DUAL-MARKET SCANNER** 📊\n\n**🔹 Stock Options Setups:**\n"
for sym, data in stock_results.items():
    idea, rsi = data
    discord_msg += f"• **{sym}**: Bias = {idea} (RSI: {rsi:.1f})\n"

discord_msg += "\n**🔸 Crypto Trade Setups:**\n"
for sym, data in crypto_picks:
    score, rsi = data
    discord_msg += f"• **{sym}**: Score = {score} (RSI: {rsi:.1f})\n"

try:
    requests.post(WEBHOOK_URL, json={"content": discord_msg})
except Exception as e:
    print("Discord webhook failed:", e)

# --- 5. EXECUTE LIVE CRYPTO TRADES ---
# Enforces a $1,500 monthly budget via defensive allocation sizing
BUDGET = 1500
ALLOCATIONS = [0.10, 0.10, 0.10] # $150 max cap per ticker

for i, (symbol, data) in enumerate(crypto_picks):
    score, rsi = data
    if score >= 15:
        investment_usd = BUDGET * ALLOCATIONS[i]
        try:
            current_price = exchange.fetch_ticker(symbol)['last']
            amount_to_buy = investment_usd / current_price
            order = exchange.create_market_buy_order(symbol, amount_to_buy)
            print(f"Successfully bought {amount_to_buy} of {symbol}")

            # NEW: Send Discord Notification
            discord_message = {
                "content": f"✅ **TRADE EXECUTED:** Bought {amount_to_buy:.4f} {symbol} at ${current_price:.2f}"
            }
            requests.post(WEBHOOK_URL, json=discord_message)

        except Exception as e:
            print(f"Failed to execute trade for {symbol}: {e}")

        except Exception as e:
            print(f"Failed to execute trade for {symbol}: {e}")
