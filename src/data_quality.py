import pandas as pd

def run_quality_checks(data):
    results = []

    def add(check_name, table, passed, issue_count, description):
        results.append({
            "check_name": check_name,
            "table": table,
            "passed": bool(passed),
            "issue_count": int(issue_count),
            "description": description,
        })

    orders = data["orders"]
    order_items = data["order_items"]
    products = data["products"]
    customers = data["customers"]
    shipments = data["shipments"]
    returns = data["returns"]

    dup = orders["order_id"].duplicated().sum()
    add("Duplicate order IDs", "orders", dup == 0, dup, "Order IDs should be unique.")

    missing = orders["customer_id"].isna().sum()
    add("Missing customer IDs", "orders", missing == 0, missing, "Orders require a customer ID.")

    invalid_qty = (order_items["quantity"] <= 0).sum()
    add("Invalid quantities", "order_items", invalid_qty == 0, invalid_qty, "Quantity must be greater than zero.")

    invalid_price = (order_items["unit_price"] <= 0).sum()
    add("Invalid prices", "order_items", invalid_price == 0, invalid_price, "Unit price must be greater than zero.")

    bad_product_keys = (~order_items["product_id"].isin(products["product_id"])).sum()
    add("Broken product references", "order_items", bad_product_keys == 0, bad_product_keys, "Every item product ID must exist.")

    bad_customer_keys = (~orders["customer_id"].isin(customers["customer_id"])).sum()
    add("Broken customer references", "orders", bad_customer_keys == 0, bad_customer_keys, "Every order customer ID must exist.")

    s = shipments.copy()
    s["ship_date"] = pd.to_datetime(s["ship_date"])
    s["expected_delivery_date"] = pd.to_datetime(s["expected_delivery_date"])
    s["actual_delivery_date"] = pd.to_datetime(s["actual_delivery_date"])

    impossible = (s["actual_delivery_date"] < s["ship_date"]).sum()
    add("Impossible shipment dates", "shipments", impossible == 0, impossible, "Actual delivery cannot be before shipment.")

    neg_ship_cost = (shipments["shipping_cost"] < 0).sum()
    add("Negative shipping cost", "shipments", neg_ship_cost == 0, neg_ship_cost, "Shipping cost cannot be negative.")

    neg_refund = (returns["refund_amount"] < 0).sum()
    add("Negative refund amount", "returns", neg_refund == 0, neg_refund, "Refund amount cannot be negative.")

    return pd.DataFrame(results)
