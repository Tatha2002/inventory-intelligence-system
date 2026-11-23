
/*
===============================================================================
PROJECT: INVENTORY INTELLIGENCE WEB APPLICATION
DATABASE: PostgreSQL
FILE: sql_queries.sql

Purpose:
Demonstrate raw SQL queries used for inventory management, stock analysis, supplier management, reporting and dashboard analytics.

Stock Rule:
A product is considered low-stock when stock_quantity <= reorder_level
===============================================================================
*/

-- 1. LOW-STOCK PRODUCTS
-- Find products whose available stock is at or below reorder level.
SELECT p.id, p.sku, p.product_name, ib.stock_quantity, ib.reorder_level FROM inventory_product p INNER JOIN inventory_inventorybatch ib ON p.id = ib.product_id WHERE ib.stock_quantity <= ib.reorder_level AND p.is_discontinued = FALSE ORDER BY ib.stock_quantity ASC;

-- 2. WHERE WITH AND
-- Find active products with selling price greater than 500.
SELECT id, sku, product_name, selling_price FROM inventory_product WHERE is_discontinued = FALSE AND selling_price > 500;

-- 3. WHERE WITH OR
-- Find products that are discontinued or have a selling price above 2000.
SELECT id, sku, product_name, selling_price, is_discontinued FROM inventory_product WHERE is_discontinued = TRUE OR selling_price > 2000;

-- 4. LIKE CATEGORY SEARCH
-- Search categories containing the word 'Electronics'.
SELECT id, name FROM inventory_category WHERE name ILIKE '%Electronics%';

-- 5. BETWEEN PRICE RANGE
-- Find products having selling prices between 500 and 5000.
SELECT id, sku, product_name, selling_price FROM inventory_product WHERE selling_price BETWEEN 500 AND 5000 ORDER BY selling_price ASC;

-- 6. LIMIT AND ORDER BY
-- Display the 10 most expensive products.
SELECT id, sku, product_name, selling_price FROM inventory_product ORDER BY selling_price DESC LIMIT 10;

-- 7. FETCH VS LIMIT
-- Using LIMIT:
SELECT id, product_name, selling_price FROM inventory_product ORDER BY selling_price DESC LIMIT 5;

-- Using FETCH FIRST:
SELECT id, product_name, selling_price FROM inventory_product ORDER BY selling_price DESC FETCH FIRST 5 ROWS ONLY;

-- 8. COUNT PRODUCTS BY CATEGORY
-- Count the total products available in each category.
SELECT c.id, c.name AS category_name, COUNT(p.id) AS total_products FROM inventory_category c LEFT JOIN inventory_product p ON c.id = p.category_id GROUP BY c.id, c.name ORDER BY total_products DESC;

-- 9. SUM STOCK VALUE
-- Calculate the total inventory purchase value: Purchase Price * Available Quantity.
SELECT SUM(p.purchase_price * ib.stock_quantity) AS total_stock_value FROM inventory_product p INNER JOIN inventory_inventorybatch ib ON p.id = ib.product_id;

-- 10. MIN, MAX AND AVG SELLING PRICE
-- Calculate minimum, maximum and average product selling price.
SELECT MIN(selling_price) AS minimum_price, MAX(selling_price) AS maximum_price, ROUND(AVG(selling_price), 2) AS average_price FROM inventory_product;

-- 11. GROUP BY WAREHOUSE
-- Calculate total stock available in each warehouse.
SELECT w.id, w.name AS warehouse_name, SUM(ib.stock_quantity) AS total_stock, COUNT(ib.id) AS total_batches FROM inventory_warehouse w INNER JOIN inventory_inventorybatch ib ON w.id = ib.warehouse_id GROUP BY w.id, w.name ORDER BY total_stock DESC;

-- 12. HAVING LOW-STOCK THRESHOLD
-- Find warehouses having at least 5 low-stock inventory batches.
SELECT w.id, w.name AS warehouse_name, COUNT(ib.id) AS low_stock_batches FROM inventory_warehouse w INNER JOIN inventory_inventorybatch ib ON w.id = ib.warehouse_id WHERE ib.stock_quantity <= ib.reorder_level GROUP BY w.id, w.name HAVING COUNT(ib.id) >= 5 ORDER BY low_stock_batches DESC;

-- 13. INNER JOIN PRODUCTS WITH SUPPLIERS
-- Display products along with their supplier information.
SELECT p.id AS product_id, p.sku, p.product_name, p.brand, s.id AS supplier_id, s.supplier_code, s.name AS supplier_name FROM inventory_product p INNER JOIN inventory_supplier s ON p.supplier_id = s.id ORDER BY p.product_name;

-- 14. FULL OUTER JOIN PRODUCTS WITHOUT ORDERS
-- Identify products that do not have any matching order summary.
SELECT p.id AS product_id, p.sku, p.product_name, os.id AS order_summary_id, os.order_count FROM inventory_product p FULL OUTER JOIN inventory_ordersummary os ON p.id = os.product_id WHERE os.id IS NULL ORDER BY p.product_name;

-- 15. NATURAL JOIN
-- Demonstrate NATURAL JOIN using warehouse-wise stock summaries.
WITH warehouse_stock AS (SELECT warehouse_id, SUM(stock_quantity) AS total_stock FROM inventory_inventorybatch GROUP BY warehouse_id), warehouse_batches AS (SELECT warehouse_id, COUNT(*) AS total_batches FROM inventory_inventorybatch GROUP BY warehouse_id) SELECT warehouse_id, total_stock, total_batches FROM warehouse_stock NATURAL JOIN warehouse_batches ORDER BY warehouse_id;

-- 16. UNION ALL FOR REORDER AND DISCONTINUED PRODUCTS
-- Combine reorder-required and discontinued product records. UNION ALL preserves duplicate records.
SELECT p.id AS product_id, p.sku, p.product_name, 'REORDER REQUIRED' AS status FROM inventory_product p INNER JOIN inventory_inventorybatch ib ON p.id = ib.product_id WHERE ib.stock_quantity <= ib.reorder_level UNION ALL SELECT p.id AS product_id, p.sku, p.product_name, 'DISCONTINUED' AS status FROM inventory_product p WHERE p.is_discontinued = TRUE;

-- 17. INTERSECT FOR HIGH-RETURN AND LOW-STOCK PRODUCTS
-- Find products with at least 5 returns and at least one low-stock inventory batch.
SELECT p.id, p.sku, p.product_name FROM inventory_product p INNER JOIN inventory_ordersummary os ON p.id = os.product_id GROUP BY p.id, p.sku, p.product_name HAVING SUM(os.return_count) >= 5 INTERSECT SELECT p.id, p.sku, p.product_name FROM inventory_product p INNER JOIN inventory_inventorybatch ib ON p.id = ib.product_id GROUP BY p.id, p.sku, p.product_name HAVING SUM(CASE WHEN ib.stock_quantity <= ib.reorder_level THEN 1 ELSE 0 END) > 0;

-- 18. DASHBOARD: TOTAL LOW-STOCK PRODUCTS
-- Count distinct products requiring stock replenishment.
SELECT COUNT(DISTINCT p.id) AS low_stock_product_count FROM inventory_product p INNER JOIN inventory_inventorybatch ib ON p.id = ib.product_id WHERE ib.stock_quantity <= ib.reorder_level AND p.is_discontinued = FALSE;

-- 19. DASHBOARD: TOTAL COMPLAINTS
-- Count complaints recorded in the application.
SELECT COUNT(*) AS total_complaints FROM inventory_complaint;

-- 20. DASHBOARD: HIGH-RISK DEMAND PRODUCTS
-- Retrieve products identified as high reorder risk by the demand prediction module.
SELECT p.id, p.sku, p.product_name, dp.predicted_demand, dp.reorder_risk FROM inventory_product p INNER JOIN machine_learning_demandpredictionhistory dp ON p.id = dp.product_id WHERE UPPER(dp.reorder_risk) IN ('HIGH', 'HIGH_RISK', 'HIGH RISK') ORDER BY p.product_name;

-- 21. PRODUCT-WISE STOCK SUMMARY
-- Display total available stock for every product.
SELECT p.id, p.sku, p.product_name, COALESCE(SUM(ib.stock_quantity), 0) AS total_stock FROM inventory_product p LEFT JOIN inventory_inventorybatch ib ON p.id = ib.product_id GROUP BY p.id, p.sku, p.product_name ORDER BY p.product_name;

/*
===============================================================================
END OF SQL QUERIES
===============================================================================
*/
