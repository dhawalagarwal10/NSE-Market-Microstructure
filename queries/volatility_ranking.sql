SELECT symbol,
       ROUND(AVG(gk_volatility), 6) as avg_volatility
FROM processed
WHERE gk_volatility IS NOT NULL
GROUP BY symbol
ORDER BY avg_volatility DESC