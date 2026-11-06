"""Create lab.db from schema.sql and load sample.csv."""
from report_engine import DEFAULT_CSV, import_csv

if __name__ == "__main__":
    count, errors = import_csv(DEFAULT_CSV)
    print(f"lab.db ready: {count} patients loaded from {DEFAULT_CSV.name}")
    for e in errors:
        print("  skipped ->", e)
