DROP VIEW IF EXISTS order_item_metrics;
CREATE VIEW order_item_metrics AS
SELECT
    oi.order_item_id,
    oi.order_id,
    o.order_date,
    c.customer_id,
    c.region,
    p.product_id,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    p.unit_cost,
    ROUND(oi.quantity * oi.unit_price * (1 - oi.discount), 2) AS revenue,
    ROUND(oi.quantity * p.unit_cost, 2) AS product_cost,
    ROUND(
        oi.quantity * oi.unit_price * (1 - oi.discount)
        - oi.quantity * p.unit_cost, 2
    ) AS gross_profit
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN products p ON oi.product_id = p.product_id;

DROP VIEW IF EXISTS shipment_metrics;
CREATE VIEW shipment_metrics AS
SELECT
    s.*,
    c.region,
    CAST(julianday(s.actual_delivery_date) - julianday(s.ship_date) AS INTEGER) AS delivery_days,
    CASE
        WHEN date(s.actual_delivery_date) > date(s.expected_delivery_date) THEN 1
        ELSE 0
    END AS is_late
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
LEFT JOIN customers c ON o.customer_id = c.customer_id;

DROP VIEW IF EXISTS return_metrics;
CREATE VIEW return_metrics AS
SELECT
    r.*,
    p.category,
    c.region
FROM returns r
LEFT JOIN products p ON r.product_id = p.product_id
LEFT JOIN orders o ON r.order_id = o.order_id
LEFT JOIN customers c ON o.customer_id = c.customer_id;
