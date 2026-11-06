"""
cli.py
------
Console entry point for the Pathology Lab Report Generator.

If no CSV path is supplied, sample.csv from the project folder is used.
Usage:  python cli.py [path/to/file.csv]
"""
import argparse
import sys
from pathlib import Path

from report_engine import DEFAULT_CSV, get_db, group_by_patient, import_csv


def main():
    parser = argparse.ArgumentParser(description="Pathology Lab Report Generator")
    parser.add_argument("csv", nargs="?", default=str(DEFAULT_CSV), help="CSV file to import")
    args = parser.parse_args()

    try:
        count, errors = import_csv(Path(args.csv))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    conn = get_db()
    for p in group_by_patient(conn):
        print(f"\n{p['name']} ({p['patient_id']})  {p['age']}{p['gender']}  -> {p['status'].upper()}")
        for t in p["tests"]:
            rng = f"{t['ref_low']}-{t['ref_high']}" if t["ref_low"] is not None else "n/a"
            print(f"  {t['test']:<18}{t['value']:>8} {t['unit'] or '':<10} range {rng:<12} {t['status']}")
    conn.close()

    print(f"\n{count} patients saved to lab.db")
    for e in errors:
        print("Skipped:", e)


if __name__ == "__main__":
    main()
