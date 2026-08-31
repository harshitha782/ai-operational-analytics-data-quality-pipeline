from src.generate_data import generate_all
from src.pipeline import build_database
from src.anomaly_detection import detect_anomalies

def main():
    print("1) Generating synthetic operational data...")
    counts = generate_all()
    for name, count in counts.items():
        print(f"   {name}: {count:,} rows")

    print("\n2) Building SQLite database and analytics views...")
    quality = build_database()
    print(quality.to_string(index=False))

    print("\n3) Detecting operational anomalies...")
    anomalies = detect_anomalies("data/processed/novaretail.db")
    anomalies.to_csv("data/processed/anomalies.csv", index=False)

    if anomalies.empty:
        print("No material anomalies detected.")
    else:
        print(anomalies.to_string(index=False))

    print("\nProject build complete.")
    print("Run dashboard with:")
    print("streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()
