SELECT
  symbol,
  ROUND(AVG(gk_volatility), 6) as avg_gk_vol,
  ROUND(AVG(relative_spread), 6) as avg_spread,
  ROUND(AVG(gk_volatility) / NULLIF(AVG(relative_spread), 0), 4) as vol_to_spread_ratio
FROM processed
WHERE gk_volatility IS NOT NULL
GROUP BY symbol
ORDER BY vol_to_spread_ratio DESC