import yfinance as yf
import pandas as pd
import boto3
import io
from datetime import datetime, timedelta

# config
BUCKET_NAME = "nse-market-microstructure-dhawal"
s3_client = boto3.client("s3", region_name="ap-south-1")

NIFTY50 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
    "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
    "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "WIPRO",
    "HCLTECH", "POWERGRID", "NTPC", "ONGC", "JSWSTEEL",
    "TATACONSUM", "TECHM", "ADANIENT", "COALINDIA",
    "BAJAJFINSV", "DIVISLAB", "DRREDDY", "EICHERMOT", "GRASIM",
    "HEROMOTOCO", "HINDALCO", "INDUSINDBK", "M&M", "CIPLA",
    "ADANIPORTS", "APOLLOHOSP", "BAJAJ-AUTO", "BRITANNIA", "BPCL",
    "HDFCLIFE", "SBILIFE", "SHRIRAMFIN", "TRENT", "LTIM"
]

def fetch_and_upload(symbol, start_date, end_date):
    ticker = f"{symbol}.NS"
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            print(f"No data for {symbol}")
            return

        # flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.columns = df.columns.str.lower()
        df = df.rename(columns={"date": "date", "open": "open", "high": "high",
                                 "low": "low", "close": "close", "volume": "volume"})
        df["symbol"] = symbol
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df["month"] = pd.to_datetime(df["date"]).dt.month
        df_to_upload = df.drop(columns=["symbol", "year", "month"])
        df_to_upload = df_to_upload.copy()
        df_to_upload['date'] = df_to_upload['date'].astype('datetime64[us]')
        key = f"raw/symbol={symbol}/year={df['year'].iloc[0]}/data.parquet"
        buffer = io.BytesIO()
        df_to_upload.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=buffer.getvalue()
        )
        print(f"Uploaded {symbol} — {len(df_to_upload)} rows")

    except Exception as e:
        print(f"Error for {symbol}: {e}")

if __name__ == "__main__":
    end = datetime.today()
    start = end - timedelta(days=90)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    print(f"Fetching data from {start_str} to {end_str}")
    for symbol in NIFTY50:
        fetch_and_upload(symbol, start_str, end_str)
    print("Done. Check your S3 bucket.")