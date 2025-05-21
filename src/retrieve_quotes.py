import asyncio
from datetime import datetime
import os

import pytz
import yfinance as yf
import pandas as pd


async def retrieve_quotes():
    try:
        saved_files = os.listdir("ticker_quotes")
        saved_files = [file.replace(".csv", "") for file in saved_files]

        df = pd.read_csv("all_tickers/tickers.csv")
        tickers = df["ticker"].tolist()

        for index, ticker in enumerate(tickers):
            if ticker in saved_files:
                print(f"Ticker {ticker} already exists, skipping.")
                continue
            
            try:
                quote = yf.Ticker(ticker).history(period="1d", end=datetime.now(tz=pytz.utc).strftime("%Y-%m-%d"), start="1950-01-01")
            except Exception as e:
                print(f"Error retrieving data for {ticker}: {e}")
                continue
            
            if len(quote) > 90:
                quote.to_csv(f"ticker_quotes/{ticker}.csv", index=True)
                print(f"Ticker {ticker} quotes retrieved successfully with {len(quote)} entries, processed: {((index + 1)/len(tickers)) * 100:.2f}% complete.")
            else:
                print(f"Ticker {ticker} processed: {((index + 1)/len(tickers)) * 100:.2f}% complete.")

    except Exception as e:
        print(f"Error in retrieve_quotes: {e}")
        return None
    

if __name__ == "__main__":
    asyncio.run(retrieve_quotes())