from pathlib import Path
import sqlite3
import pandas as pd
from src.data_quality import run_quality_checks

TABLES = [
    "customers", "products", "warehouses", "orders",
    "order_items", "shipments", "returns"
]

def load_raw_data(raw_dir="data/raw"):
    raw_dir = Path(raw_dir)
    return {name: pd.read_csv(raw_dir / f"{name}.csv") for name in TABLES}

def build_database(raw_dir="data/raw", db_path="data/processed/novaretail.db"):
    data = load_raw_data(raw_dir)
    quality = run_quality_checks(data)

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db_path)

    schema_sql = Path("sql/schema.sql").read_text(encoding="utf-8")
    con.executescript(schema_sql)

    for table, df in data.items():
        df.to_sql(table, con, if_exists="append", index=False)

    views_sql = Path("sql/analytics_views.sql").read_text(encoding="utf-8")
    con.executescript(views_sql)
    con.commit()
    con.close()

    quality.to_csv("data/processed/data_quality_report.csv", index=False)
    return quality
