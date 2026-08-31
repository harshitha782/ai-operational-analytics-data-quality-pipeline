from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

def generate_all(output_dir="data/raw", n_orders=50000):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    regions = ["Northeast", "South", "Midwest", "West"]
    states = {
        "Northeast": ["NY", "NJ", "MA", "PA"],
        "South": ["TX", "FL", "GA", "NC"],
        "Midwest": ["IL", "OH", "MI", "MN"],
        "West": ["CA", "WA", "AZ", "CO"],
    }

    # Customers
    n_customers = 8000
    cust_regions = RNG.choice(regions, n_customers, p=[0.22, 0.30, 0.23, 0.25])
    customers = pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(1, n_customers + 1)],
        "customer_name": [f"Customer {i}" for i in range(1, n_customers + 1)],
        "region": cust_regions,
        "signup_date": pd.to_datetime("2022-01-01") + pd.to_timedelta(
            RNG.integers(0, 1200, n_customers), unit="D"
        ),
    })
    customers["state"] = [RNG.choice(states[r]) for r in customers["region"]]
    customers = customers[["customer_id", "customer_name", "state", "region", "signup_date"]]

    # Products
    categories = ["Electronics", "Home", "Office", "Sports", "Beauty"]
    n_products = 120
    product_categories = RNG.choice(categories, n_products)
    costs = RNG.uniform(8, 300, n_products).round(2)
    markup = RNG.uniform(1.25, 2.4, n_products)
    products = pd.DataFrame({
        "product_id": [f"P{i:04d}" for i in range(1, n_products + 1)],
        "product_name": [f"Product {i}" for i in range(1, n_products + 1)],
        "category": product_categories,
        "unit_cost": costs,
        "list_price": (costs * markup).round(2),
    })

    # Warehouses
    warehouses = pd.DataFrame({
        "warehouse_id": ["W1", "W2", "W3", "W4"],
        "warehouse_name": ["East Hub", "South Hub", "Central Hub", "West Hub"],
        "region": regions,
    })

    # Orders
    order_dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
        RNG.integers(0, 365, n_orders), unit="D"
    )
    orders = pd.DataFrame({
        "order_id": [f"O{i:07d}" for i in range(1, n_orders + 1)],
        "customer_id": RNG.choice(customers["customer_id"], n_orders),
        "order_date": order_dates,
        "order_status": RNG.choice(["Completed", "Completed", "Completed", "Cancelled"], n_orders),
        "sales_channel": RNG.choice(["Web", "Mobile", "Marketplace"], n_orders, p=[0.55, 0.30, 0.15]),
        "payment_method": RNG.choice(["Card", "PayPal", "Wallet"], n_orders),
    })

    # Order items
    items = []
    item_id = 1
    product_index = products.set_index("product_id")
    for oid in orders["order_id"]:
        for _ in range(int(RNG.integers(1, 4))):
            pid = RNG.choice(products["product_id"])
            row = product_index.loc[pid]
            qty = int(RNG.integers(1, 5))
            discount = float(RNG.choice([0, 0, 0.05, 0.10, 0.15, 0.20]))
            price_noise = RNG.normal(1.0, 0.03)
            unit_price = max(1, float(row["list_price"]) * price_noise)
            items.append([
                f"OI{item_id:08d}", oid, pid, qty,
                round(unit_price, 2), discount
            ])
            item_id += 1
    order_items = pd.DataFrame(items, columns=[
        "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"
    ])

    # Customer order region map
    order_region = orders.merge(
        customers[["customer_id", "region"]], on="customer_id", how="left"
    )[["order_id", "region", "order_date"]]

    # Shipments
    carriers = ["Carrier A", "Carrier B", "Carrier C"]
    ship_rows = []
    warehouse_by_region = dict(zip(warehouses["region"], warehouses["warehouse_id"]))

    for i, row in order_region.iterrows():
        ship_date = row["order_date"] + pd.Timedelta(days=int(RNG.integers(0, 3)))
        expected_days = int(RNG.integers(2, 6))
        expected = ship_date + pd.Timedelta(days=expected_days)
        carrier = RNG.choice(carriers, p=[0.40, 0.35, 0.25])

        delay = int(max(0, RNG.normal(0.5, 1.2)))

        # Deliberately create a stronger operational problem:
        # Carrier B performs worse in the West.
        if row["region"] == "West" and carrier == "Carrier B":
            if RNG.random() < 0.38:
                delay += int(RNG.integers(2, 6))

        # Warehouse 3 occasional processing problems
        warehouse = warehouse_by_region.get(row["region"], "W3")
        if warehouse == "W3" and RNG.random() < 0.15:
            delay += int(RNG.integers(1, 4))

        actual = expected + pd.Timedelta(days=delay)
        shipping_cost = round(float(RNG.uniform(4, 25)), 2)

        ship_rows.append([
            f"S{i+1:07d}",
            row["order_id"],
            warehouse,
            carrier,
            ship_date,
            expected,
            actual,
            shipping_cost,
        ])

    shipments = pd.DataFrame(ship_rows, columns=[
        "shipment_id", "order_id", "warehouse_id", "carrier",
        "ship_date", "expected_delivery_date", "actual_delivery_date",
        "shipping_cost"
    ])

    # Returns - Electronics intentionally higher
    merged_items = order_items.merge(
        products[["product_id", "category"]], on="product_id", how="left"
    )
    return_rows = []
    return_id = 1
    order_date_map = orders.set_index("order_id")["order_date"].to_dict()

    for _, row in merged_items.iterrows():
        base_rate = 0.05
        if row["category"] == "Electronics":
            base_rate = 0.13
        if RNG.random() < base_rate:
            reason = RNG.choice([
                "Defective", "Wrong Item", "Not Needed",
                "Damaged", "Quality Issue"
            ])
            refund = round(
                row["quantity"] * row["unit_price"] * (1 - row["discount"]), 2
            )
            ret_date = order_date_map[row["order_id"]] + pd.Timedelta(
                days=int(RNG.integers(5, 35))
            )
            return_rows.append([
                f"R{return_id:07d}",
                row["order_id"],
                row["product_id"],
                ret_date,
                reason,
                refund,
            ])
            return_id += 1

    returns = pd.DataFrame(return_rows, columns=[
        "return_id", "order_id", "product_id",
        "return_date", "return_reason", "refund_amount"
    ])

    # Save clean-but-realistic synthetic data.
    datasets = {
        "customers.csv": customers,
        "products.csv": products,
        "warehouses.csv": warehouses,
        "orders.csv": orders,
        "order_items.csv": order_items,
        "shipments.csv": shipments,
        "returns.csv": returns,
    }

    for filename, df in datasets.items():
        df.to_csv(output / filename, index=False)

    return {name: len(df) for name, df in datasets.items()}

if __name__ == "__main__":
    counts = generate_all()
    print("Generated datasets:")
    for name, count in counts.items():
        print(f"{name}: {count:,} rows")
