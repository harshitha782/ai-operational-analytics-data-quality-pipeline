from pathlib import Path
import sqlite3
import subprocess
import sys

import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="NovaRetail Operations Analytics",
    layout="wide"
)

DB_PATH = Path("data/processed/novaretail.db")


# Build the database automatically if it does not exist.
# This is useful for Streamlit Cloud deployment.
if not DB_PATH.exists():
    with st.spinner("Preparing analytics data..."):
        result = subprocess.run(
            [sys.executable, "run_project.py"],
            capture_output=True,
            text=True
        )

    if result.returncode != 0:
        st.error("Failed to build the analytics database.")
        st.code(result.stderr)
        st.stop()

    if not DB_PATH.exists():
        st.error("Database was not created successfully.")
        st.stop()


con = sqlite3.connect(DB_PATH)


st.title("NovaRetail Operational Analytics")
st.caption("AI-Enabled Operational Analytics & Data Quality Pipeline")


# -----------------------------
# KPI SUMMARY
# -----------------------------
kpis = pd.read_sql_query(
    """
    SELECT
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(gross_profit), 2) AS gross_profit,
        ROUND(
            100.0 * SUM(gross_profit) / NULLIF(SUM(revenue), 0),
            2
        ) AS margin_pct,
        COUNT(DISTINCT order_id) AS orders,
        ROUND(
            SUM(revenue) / NULLIF(COUNT(DISTINCT order_id), 0),
            2
        ) AS avg_order_value
    FROM order_item_metrics
    """,
    con
).iloc[0]


late = pd.read_sql_query(
    """
    SELECT
        ROUND(100.0 * AVG(is_late), 2) AS late_rate
    FROM shipment_metrics
    """,
    con
).iloc[0, 0]


return_rate = pd.read_sql_query(
    """
    SELECT
        ROUND(
            100.0 * COUNT(DISTINCT r.return_id) /
            NULLIF((SELECT COUNT(*) FROM order_items), 0),
            2
        ) AS return_rate
    FROM returns r
    """,
    con
).iloc[0, 0]


c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Revenue", f"${kpis['revenue']:,.0f}")
c2.metric("Gross Profit", f"${kpis['gross_profit']:,.0f}")
c3.metric("Margin", f"{kpis['margin_pct']:.1f}%")
c4.metric("Orders", f"{int(kpis['orders']):,}")
c5.metric("Late Delivery", f"{late:.1f}%")
c6.metric("Return Rate", f"{return_rate:.1f}%")


st.divider()


# -----------------------------
# REVENUE ANALYSIS
# -----------------------------
monthly = pd.read_sql_query(
    """
    SELECT
        substr(order_date, 1, 7) AS month,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(gross_profit), 2) AS profit
    FROM order_item_metrics
    GROUP BY substr(order_date, 1, 7)
    ORDER BY month
    """,
    con
)


region = pd.read_sql_query(
    """
    SELECT
        region,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(gross_profit), 2) AS profit
    FROM order_item_metrics
    GROUP BY region
    ORDER BY revenue DESC
    """,
    con
)


left, right = st.columns(2)

with left:
    st.subheader("Monthly Revenue")

    st.plotly_chart(
        px.line(
            monthly,
            x="month",
            y="revenue",
            markers=True
        ),
        use_container_width=True
    )


with right:
    st.subheader("Revenue by Region")

    st.plotly_chart(
        px.bar(
            region,
            x="region",
            y="revenue"
        ),
        use_container_width=True
    )


# -----------------------------
# OPERATIONAL PERFORMANCE
# -----------------------------
carrier = pd.read_sql_query(
    """
    SELECT
        carrier,
        COUNT(*) AS shipments,
        ROUND(100.0 * AVG(is_late), 2) AS late_rate,
        ROUND(AVG(delivery_days), 2) AS avg_delivery_days
    FROM shipment_metrics
    GROUP BY carrier
    ORDER BY late_rate DESC
    """,
    con
)


category_returns = pd.read_sql_query(
    """
    SELECT
        p.category,
        COUNT(DISTINCT r.return_id) AS returns,
        COUNT(DISTINCT oi.order_item_id) AS items,
        ROUND(
            100.0 * COUNT(DISTINCT r.return_id) /
            NULLIF(COUNT(DISTINCT oi.order_item_id), 0),
            2
        ) AS return_rate
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    LEFT JOIN returns r
        ON oi.order_id = r.order_id
        AND oi.product_id = r.product_id
    GROUP BY p.category
    ORDER BY return_rate DESC
    """,
    con
)


left, right = st.columns(2)

with left:
    st.subheader("Carrier Late-Delivery Rate")

    st.plotly_chart(
        px.bar(
            carrier,
            x="carrier",
            y="late_rate"
        ),
        use_container_width=True
    )


with right:
    st.subheader("Return Rate by Category")

    st.plotly_chart(
        px.bar(
            category_returns,
            x="category",
            y="return_rate"
        ),
        use_container_width=True
    )


st.divider()


# -----------------------------
# OPERATIONAL RISK SUMMARY
# -----------------------------
st.subheader("Operational Risk Summary")

anomaly_path = Path("data/processed/anomalies.csv")

if anomaly_path.exists():
    anomalies = pd.read_csv(anomaly_path)

    if anomalies.empty:
        st.success("No material anomalies detected.")

    else:
        st.dataframe(
            anomalies,
            use_container_width=True,
            hide_index=True
        )

        for _, row in anomalies.iterrows():
            st.markdown(
                f"**{row['area']} — {row['severity']}**  \n"
                f"{row['finding']}  \n"
                f"**Recommended action:** {row['recommendation']}"
            )

else:
    st.info("Anomaly results are not available.")


st.divider()


# -----------------------------
# DATA QUALITY REPORT
# -----------------------------
st.subheader("Data Quality Report")

quality_path = Path("data/processed/data_quality_report.csv")

if quality_path.exists():
    quality = pd.read_csv(quality_path)

    st.dataframe(
        quality,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Data quality report is not available.")


con.close()