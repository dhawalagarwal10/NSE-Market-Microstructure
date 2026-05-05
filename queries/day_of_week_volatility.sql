SELECT 
  CASE day_of_week(date)
    WHEN 1 THEN '1-Monday'
    WHEN 2 THEN '2-Tuesday'
    WHEN 3 THEN '3-Wednesday'
    WHEN 4 THEN '4-Thursday'
    WHEN 5 THEN '5-Friday'
  END as day_name,
  ROUND(AVG(gk_volatility), 6) as avg_volatility
FROM processed
GROUP BY day_of_week(date)
ORDER BY day_of_week(date)