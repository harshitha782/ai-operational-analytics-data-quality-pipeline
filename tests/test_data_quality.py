import pandas as pd
from src.data_quality import run_quality_checks

def clean_sample():
    return {
        "customers": pd.DataFrame({
            "customer_id": ["C1"],
            "customer_name": ["A"],
            "state": ["TX"],
            "region": ["South"],
            "signup_date": ["2025-01-01"]
        }),
        "products": pd.DataFrame({
            "product_id": ["P1"],
            "product_name": ["Widget"],
            "category": ["Office"],
            "unit_cost": [10.0],
            "list_price": [20.0]
        }),
        "orders": pd.DataFrame({
            "order_id": ["O1"],
            "customer_id": ["C1"],
            "order_date": ["2025-01-10"],
            "order_status": ["Completed"],
            "sales_channel": ["Web"],
            "payment_method": ["Card"]
        }),
        "order_items": pd.DataFrame({
            "order_item_id": ["OI1"],
            "order_id": ["O1"],
            "product_id": ["P1"],
            "quantity": [1],
            "unit_price": [20.0],
            "discount": [0.0]
        }),
        "shipments": pd.DataFrame({
            "shipment_id": ["S1"],
            "order_id": ["O1"],
            "warehouse_id": ["W1"],
            "carrier": ["Carrier A"],
            "ship_date": ["2025-01-11"],
            "expected_delivery_date": ["2025-01-14"],
            "actual_delivery_date": ["2025-01-13"],
            "shipping_cost": [5.0]
        }),
        "returns": pd.DataFrame({
            "return_id": [],
            "order_id": [],
            "product_id": [],
            "return_date": [],
            "return_reason": [],
            "refund_amount": []
        }),
    }

def test_clean_data_passes_all_checks():
    result = run_quality_checks(clean_sample())
    assert result["passed"].all()

def test_negative_quantity_is_detected():
    data = clean_sample()
    data["order_items"].loc[0, "quantity"] = -1
    result = run_quality_checks(data)
    row = result[result["check_name"] == "Invalid quantities"].iloc[0]
    assert row["passed"] == False
    assert row["issue_count"] == 1
