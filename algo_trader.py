import os
import yfinance as yf
import requests
from transformers import pipeline
import pandas as pd
from io import StringIO

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# Fetch the top 50 highly liquid stocks from the S&P 500
print("Fetching dynamic ticker list...")
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0 Safari/537.36"}
html = requests.get(url, headers=headers).text
table = pd.read_html(StringIO(html))[0]
WATCHLIST = table[table['CIK'].notnull()]['Symbol'].tolist()[:50]

sentiment_analyzer = pipeline("text-classification", model="ProsusAI/finbert")

def get_stock_score(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    fund_score = 0
    try:
        info = ticker.info
        calc = (info.get('profitMargins', 0) * 100) - (info.get('debtToEquity', 100) / 10)
        fund_score = max(0, min(50, calc))
    except:
        pass

    sentiment_score = 0
    try:
        news = ticker.news
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

scores = {symbol: get_stock_score(symbol) for symbol in WATCHLIST}
top_picks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

BUDGET = 1500
ALLOCATIONS = [0.10, 0.10, 0.10]

embed_fields = []
for i, (symbol, score) in enumerate(top_picks):
    investment = BUDGET * ALLOCATIONS[i]
    embed_fields.append({
        "name": f"#{i+1}: {symbol}",
        "value": f"**Buy: ${investment:.2f}** | Score: {score:.1f}/100",
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
