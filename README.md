# AI-Enabled Operational Analytics & Data Quality Pipeline

A portfolio project designed to demonstrate end-to-end data analytics skills using Python, SQL, ETL, data modeling, data quality testing, anomaly detection, reporting, and visualization.

## Business Scenario

NovaRetail is a fictional U.S. e-commerce and distribution company. Leadership wants better visibility into revenue, profitability, returns, fulfillment performance, carrier performance, warehouse efficiency, and data quality.

This project builds an automated pipeline that:

1. Generates realistic synthetic operational data
2. Loads raw data into SQLite
3. Runs data-quality checks
4. Creates analytics-ready SQL views
5. Detects operational anomalies
6. Produces business recommendations
7. Displays KPIs and trends in a Streamlit dashboard
8. Includes automated tests with pytest

## Tech Stack

- Python
- SQL / SQLite
- Pandas
- NumPy
- Streamlit
- Plotly
- Pytest

## Project Structure

```text
ai_operational_analytics_project/
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── schema.sql
│   └── analytics_views.sql
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   ├── data_quality.py
│   └── anomaly_detection.py
├── tests/
│   └── test_data_quality.py
├── dashboard/
│   └── app.py
├── run_project.py
├── requirements.txt
└── README.md
```

## How to Run

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\\Scripts\\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate data and build the database

```bash
python run_project.py
```

This will:

- generate synthetic CSV files
- create `data/processed/novaretail.db`
- run data quality checks
- create SQL analytics views
- write anomaly results to `data/processed/anomalies.csv`

### 4. Run tests

```bash
pytest -q
```

### 5. Launch dashboard

```bash
streamlit run dashboard/app.py
```

## Key KPIs

- Revenue
- Profit
- Profit Margin
- Order Volume
- Average Order Value
- Return Rate
- Late Delivery Rate
- Carrier Performance
- Warehouse Performance
- Regional Revenue
- Product Category Performance

## Interview Talking Points

### Business problem

The goal was to improve operational decision-making by automating data preparation, validating source data, modeling analytical datasets, detecting operational issues, and presenting findings through an interactive dashboard.

### Data engineering

Raw CSV data is loaded into SQLite through a Python ETL pipeline. SQL views transform normalized operational tables into analytics-ready datasets.

### Data quality

The project checks for duplicate records, missing identifiers, invalid quantities, negative monetary values, broken relationships, and impossible shipment dates.

### Analytics

SQL and Python are used to analyze regional revenue, product performance, return rates, fulfillment delays, carriers, and warehouse operations.

### Automation

`run_project.py` orchestrates the full process from source-data generation to database creation, validation, and anomaly reporting.

### Testing

Pytest validates important data-quality rules to prevent inaccurate reporting.

### AI-enabled component

The anomaly-detection layer produces plain-English operational recommendations from detected KPI risks. In a production environment, this layer could be connected to an LLM or agentic workflow for richer root-cause summaries and automated operational actions.

## Example Business Questions

- Which region has the highest late-delivery rate?
- Which product category has the highest return rate?
- Which carrier is responsible for the most delays?
- Which warehouse is underperforming?
- Which products have weak margins?
- Are there suspicious data-quality problems in the source data?
- Which operational risks should management prioritize?

## Why This Project Fits a Data Analyst Role

This project demonstrates:

- SQL and Python
- ETL pipeline design
- analytical data modeling
- data quality validation
- business analytics
- automation
- software testing
- anomaly detection
- visualization
- operational decision support
