# NSE Nifty 50 Market Microstructure

A data engineering project that builds a full pipeline from raw NSE equity data to a Metabase dashboard. The goal was to compute real market microstructure metrics on Nifty 50 stocks and make them queryable and visual.

---

## What it does

Pulls daily OHLCV data for 49 Nifty 50 stocks from NSE via yfinance, lands it in a three-layer AWS S3 data lake, runs PySpark transformations on AWS Glue to compute four microstructure metrics, catalogs the output with AWS Glue and Athena, and surfaces everything in a Metabase dashboard.

---

## Pipeline

```
yfinance (NSE data)
    -> ingest_nse.py
    -> S3 raw layer (Parquet, partitioned by symbol and year)
    -> AWS Glue Crawler (schema catalog, Hive-compatible)
    -> AWS Glue PySpark job (metric computation)
    -> S3 processed layer
    -> AWS Athena (SQL queries)
    -> Metabase dashboard
```

---

## Metrics

**Garman-Klass Volatility**
Uses the full OHLC range rather than just close-to-close returns. More information means a better volatility estimate. Formula: sqrt(0.5 * ln(H/L)^2 - (2*ln(2)-1) \* ln(C/O)^2)

**Amihud Illiquidity Ratio**
Measures how much the price moves per unit of trading volume. A high value means the stock is illiquid and small trades have a large price impact. Formula: |daily_return| / volume

**Relative Spread Proxy**
Approximates the bid-ask spread using the daily price range. Formula: (High - Low) / ((High + Low) / 2)

**Rolling 20-Day Realised Volatility**
Standard deviation of daily log returns over a 20-day rolling window.

---

## Project structure

```
nse-market-microstructure/
|
|-- ingestion/
|   |-- ingest_nse.py
|
|-- transformation/
|   |-- transform_microstructure.py
|
|-- queries/
|   |-- volatility_ranking.sql
|   |-- rolling_volatility_trend.sql
|   |-- illiquidity_table.sql
|   |-- day_of_week_volatility.sql
|   |-- volatility_vs_spread.sql
|
|-- dashboard.png
|-- requirements.txt
|-- README.md
```

---

## AWS setup

**S3 bucket structure**

```
nse-market-microstructure-[name]/
    raw/
        symbol=RELIANCE/year=2026/data.parquet
        symbol=TCS/year=2026/data.parquet
        ...
    processed/
        symbol=RELIANCE/data.parquet
        ...
    athena-results/
```

**Glue Catalog**
Database: `nse_market_db`
Tables: `raw`, `processed`
Crawler pointed at `s3://bucket/raw/` and `s3://bucket/processed/`

**Athena**
Query engine on top of S3. All SQL queries in the `queries/` folder run directly on Athena against the processed layer.

**Glue PySpark job**
The transformation script runs as a Glue 5.1 job. IAM role handles S3 access. No local Spark setup needed.

---

## Running it

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure AWS credentials:

```bash
aws configure
```

Run ingestion (pulls last 90 days of data for 49 Nifty 50 stocks):

```bash
python ingestion/ingest_nse.py
```

The transformation job runs on AWS Glue. Upload `transformation/transform_microstructure.py` to a Glue ETL job and run it from the AWS console.

---

## Key findings

LTIM, DIVISLAB, and ULTRACEMCO came out as the most illiquid Nifty 50 stocks by Amihud ratio. These are high-priced, lower-float names where trades have a noticeable price impact.

Wednesday showed marginally lower average volatility compared to Monday and Tuesday across the full Nifty 50 sample.

IT sector stocks like TCS, Infosys, and HCL clustered at high volatility but low spread, meaning they move a lot but are still cheap to trade. Energy and cement names showed the opposite.

---

## Tech stack

- Python 3.11, pandas, yfinance, pyarrow, boto3
- AWS S3, AWS Glue (PySpark 3.5, Glue version 5.1), AWS Athena
- Metabase 0.60 (community edition)

---

## Cost

The entire build cost USD 0.55 on AWS free tier for April 2026. Glue job runs were the only real charge at USD 0.46. S3 storage runs under USD 0.01 per month at this data volume. Athena queries were free.
