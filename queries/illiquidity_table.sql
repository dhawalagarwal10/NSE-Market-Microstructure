SELECT symbol,
       ROUND(AVG(amihud_illiquidity), 8) as avg_illiquidity,
       ROUND(AVG(relative_spread), 6) as avg_spread,
       COUNT(*) as trading_days
FROM processed
GROUP BY symbol
ORDER BY avg_illiquidity DESC