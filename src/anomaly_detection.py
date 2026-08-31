import sqlite3
import pandas as pd

def detect_anomalies(db_path):
    con = sqlite3.connect(db_path)
    anomalies = []

    region_late = pd.read_sql_query("""
        SELECT region,
               COUNT(*) AS shipments,
               ROUND(100.0 * AVG(is_late), 2) AS late_rate
        FROM shipment_metrics
        GROUP BY region
        ORDER BY late_rate DESC
    """, con)

    if not region_late.empty:
        worst = region_late.iloc[0]
        if worst["late_rate"] > 15:
            anomalies.append({
                "severity": "High",
                "area": "Fulfillment",
                "finding": f"{worst['region']} has a {worst['late_rate']}% late-delivery rate.",
                "recommendation": "Review carrier and warehouse performance in this region."
            })

    carrier_late = pd.read_sql_query("""
        SELECT carrier,
               COUNT(*) AS shipments,
               ROUND(100.0 * AVG(is_late), 2) AS late_rate
        FROM shipment_metrics
        GROUP BY carrier
        ORDER BY late_rate DESC
    """, con)

    if not carrier_late.empty:
        worst = carrier_late.iloc[0]
        if worst["late_rate"] > 15:
            anomalies.append({
                "severity": "High",
                "area": "Carrier Performance",
                "finding": f"{worst['carrier']} has the highest late-delivery rate at {worst['late_rate']}%.",
                "recommendation": "Perform a carrier SLA review and consider shifting priority volume."
            })

    return_by_cat = pd.read_sql_query("""
        SELECT p.category,
               COUNT(DISTINCT r.return_id) AS returns,
               COUNT(DISTINCT oi.order_item_id) AS items,
               ROUND(100.0 * COUNT(DISTINCT r.return_id) /
                     NULLIF(COUNT(DISTINCT oi.order_item_id), 0), 2) AS return_rate
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN returns r
            ON oi.order_id = r.order_id
           AND oi.product_id = r.product_id
        GROUP BY p.category
        ORDER BY return_rate DESC
    """, con)

    if not return_by_cat.empty:
        worst = return_by_cat.iloc[0]
        if worst["return_rate"] > 8:
            anomalies.append({
                "severity": "Medium",
                "area": "Returns",
                "finding": f"{worst['category']} has the highest return rate at {worst['return_rate']}%.",
                "recommendation": "Investigate product quality, descriptions, packaging, and supplier defects."
            })

    margin = pd.read_sql_query("""
        SELECT category,
               ROUND(SUM(revenue),2) AS revenue,
               ROUND(SUM(gross_profit),2) AS profit,
               ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(revenue), 0), 2) AS margin_pct
        FROM order_item_metrics
        GROUP BY category
        ORDER BY margin_pct
    """, con)

    if not margin.empty:
        worst = margin.iloc[0]
        if worst["margin_pct"] < 20:
            anomalies.append({
                "severity": "Medium",
                "area": "Profitability",
                "finding": f"{worst['category']} has the lowest gross margin at {worst['margin_pct']}%.",
                "recommendation": "Review pricing, discounting, sourcing costs, and shipping economics."
            })

    con.close()
    return pd.DataFrame(anomalies)
