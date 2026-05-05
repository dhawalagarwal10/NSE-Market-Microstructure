from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import DoubleType
import math

BUCKET = "nse-market-microstructure-dhawal"
RAW_PATH = f"s3a://{BUCKET}/raw/"
PROCESSED_PATH = f"s3a://{BUCKET}/processed/"

spark = SparkSession.builder \
    .appName("NSE Microstructure Metrics") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.access.key", "your_access_key") \
    .config("spark.hadoop.fs.s3a.secret.key", "your_secret_key") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.ap-south-1.amazonaws.com") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("Reading raw data from S3...")
df = spark.read.parquet(RAW_PATH)

df = df.withColumn("date", F.to_date(F.from_unixtime(F.col("date") / 1000)))

# ---- COMPUTE METRICS ----

# 1. daily log return
df = df.withColumn("log_return",
    F.log(F.col("close") / F.col("open"))
)

# 2. garman-Klass Volatility (daily)
df = df.withColumn("gk_volatility",
    F.sqrt(
        F.lit(0.5) * F.pow(F.log(F.col("high") / F.col("low")), 2) -
        F.lit(2 * math.log(2) - 1) * F.pow(F.log(F.col("close") / F.col("open")), 2)
    )
)

# 3. amihud Illiquidity Ratio
# absolute return divided by volume — higher means more illiquid
df = df.withColumn("amihud_illiquidity",
    F.abs(F.col("log_return")) / (F.col("volume") + F.lit(1))  # +1 avoids division by zero
)

# 4. relative Spread Proxy
df = df.withColumn("relative_spread",
    (F.col("high") - F.col("low")) / ((F.col("high") + F.col("low")) / F.lit(2))
)

# 5. rolling 20-day realised volatility (std of log returns)
window_20 = Window.partitionBy("symbol").orderBy("date").rowsBetween(-19, 0)

df = df.withColumn("rolling_20d_vol",
    F.stddev("log_return").over(window_20)
)

df_processed = df.select(
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "log_return",
    "gk_volatility",
    "amihud_illiquidity",
    "relative_spread",
    "rolling_20d_vol",
    "year"
)

print("Writing processed data to S3...")
df_processed.write \
    .mode("overwrite") \
    .partitionBy("symbol") \
    .parquet(PROCESSED_PATH)

print("Done. Processed data written to s3://processed/")
spark.stop()