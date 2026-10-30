-- RetailPulse SQL cookbook starter queries
-- 1. Monthly sales and gross profit
SELECT strftime('%Y-%m', date) AS month,
       SUM(sales) AS net_sales,
       SUM(gross_profit) AS gross_profit,
       ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(sales), 0), 2) AS gross_margin_pct
FROM fact_sales
GROUP BY 1 ORDER BY 1;

-- 2. Top categories by sales
SELECT category, SUM(sales) AS net_sales
FROM fact_sales
GROUP BY category ORDER BY net_sales DESC;

-- 3. Store performance ranking
SELECT store_id, SUM(sales) AS net_sales,
       SUM(quantity) AS units_sold,
       SUM(gross_profit) AS gross_profit
FROM fact_sales
GROUP BY store_id ORDER BY net_sales DESC;

-- 4. Top SKUs by sales
SELECT sku_id, category, SUM(sales) AS net_sales,
       SUM(quantity) AS units_sold
FROM fact_sales
GROUP BY sku_id, category
ORDER BY net_sales DESC LIMIT 20;
