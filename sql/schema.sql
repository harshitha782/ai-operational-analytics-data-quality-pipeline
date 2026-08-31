DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS returns;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    state TEXT,
    region TEXT,
    signup_date TEXT
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_cost REAL,
    list_price REAL
);

CREATE TABLE warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT,
    region TEXT
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_date TEXT,
    order_status TEXT,
    sales_channel TEXT,
    payment_method TEXT
);

CREATE TABLE order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id TEXT,
    product_id TEXT,
    quantity INTEGER,
    unit_price REAL,
    discount REAL
);

CREATE TABLE shipments (
    shipment_id TEXT PRIMARY KEY,
    order_id TEXT,
    warehouse_id TEXT,
    carrier TEXT,
    ship_date TEXT,
    expected_delivery_date TEXT,
    actual_delivery_date TEXT,
    shipping_cost REAL
);

CREATE TABLE returns (
    return_id TEXT PRIMARY KEY,
    order_id TEXT,
    product_id TEXT,
    return_date TEXT,
    return_reason TEXT,
    refund_amount REAL
);
