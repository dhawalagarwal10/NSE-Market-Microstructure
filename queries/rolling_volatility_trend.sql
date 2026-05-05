SELECT symbol, date, rolling_20d_vol
FROM processed
WHERE symbol IN ('RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK')
  AND rolling_20d_vol IS NOT NULL
ORDER BY symbol, date