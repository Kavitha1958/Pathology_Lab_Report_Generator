"""Core logic: read CSV -> classify -> store in SQLite -> group per patient."""
import csv
import sqlite3
from pathlib import Path

from units import normalize

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "lab.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
DEFAULT_CSV = BASE_DIR / "sample.csv"

ALIASES = {
    "patient_id": ("patient_id", "id"),
    "name": ("name", "patient_name"),
    "age": ("age",),
    "gender": ("gender", "sex"),
    "test": ("test", "test_name"),
    "result": ("result", "value"),
    "unit": ("unit", "units"),
    "ref_low": ("ref_low", "min", "range_low"),
    "ref_high": ("ref_high", "max", "range_high"),
    "date": ("date", "report_date"),
}
RANK = {"normal": 0, "abnormal": 1, "critical": 2}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _num(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def parse_csv(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = []
        for raw in csv.DictReader(f):
            clean = {k.strip().lower().replace(" ", "_"): (v or "").strip()
                     for k, v in raw.items() if k}
            rows.append({field: next((clean[a] for a in names if clean.get(a)), "")
                         for field, names in ALIASES.items()})
        return rows


def classify(value, low, high):
    if low is None or high is None:
        return "normal"
    if low <= value <= high:
        return "normal"
    span = (high - low) or 1
    distance = low - value if value < low else value - high
    return "critical" if distance > span * 0.5 else "abnormal"


def process_rows(rows):
    """Return (processed_rows, errors). Bad rows are skipped, never crash the run."""
    processed, errors = [], []
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        value = _num(r["result"])
        if not r["patient_id"] or not r["test"] or value is None:
            errors.append(f"Line {i}: missing patient_id, test or numeric result")
            continue
        unit, value, low, high = normalize(
            r["test"], r["unit"], value, _num(r["ref_low"]), _num(r["ref_high"]))
        processed.append({**r, "value": value, "unit": unit, "ref_low": low,
                          "ref_high": high, "status": classify(value, low, high)})
    return processed, errors


def save_results(conn, processed):
    """Replace stored data with the latest CSV contents."""
    conn.execute("DELETE FROM results")
    conn.execute("DELETE FROM patients")
    for r in processed:
        conn.execute("INSERT OR IGNORE INTO patients VALUES (?,?,?,?)",
                     (r["patient_id"], r["name"] or "Unknown", r["age"], r["gender"]))
        conn.execute(
            "INSERT INTO results (patient_id,test,value,unit,ref_low,ref_high,status,date)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (r["patient_id"], r["test"], r["value"], r["unit"],
             r["ref_low"], r["ref_high"], r["status"], r["date"]))
    conn.commit()


def import_csv(path=DEFAULT_CSV):
    """Parse + process + save in one call. Returns (patient_count, errors)."""
    processed, errors = process_rows(parse_csv(path))
    conn = get_db()
    init_schema(conn)
    save_results(conn, processed)
    conn.close()
    return len({r["patient_id"] for r in processed}), errors


def group_by_patient(conn):
    """One entry per patient with their tests and the worst status overall."""
    patients = {}
    for p in conn.execute("SELECT * FROM patients ORDER BY patient_id"):
        patients[p["patient_id"]] = {**dict(p), "tests": [], "status": "normal", "date": ""}
    for t in conn.execute("SELECT * FROM results ORDER BY id"):
        p = patients[t["patient_id"]]
        p["tests"].append(dict(t))
        p["date"] = t["date"] or p["date"]
        if RANK[t["status"]] > RANK[p["status"]]:
            p["status"] = t["status"]
    return list(patients.values())
