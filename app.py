from flask import Flask, jsonify, render_template

from report_engine import DB_PATH, DEFAULT_CSV, get_db, group_by_patient, import_csv

app = Flask(__name__)
_last_mtime = None


def sync_from_csv():
    """Re-import sample.csv whenever it changes, so the page stays live."""
    global _last_mtime
    mtime = DEFAULT_CSV.stat().st_mtime if DEFAULT_CSV.exists() else None
    if mtime != _last_mtime or not DB_PATH.exists():
        if mtime is not None:
            import_csv(DEFAULT_CSV)
        _last_mtime = mtime


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/patients")
def patients():
    sync_from_csv()
    conn = get_db()
    data = group_by_patient(conn)
    conn.close()
    summary = {"total": len(data)}
    for s in ("normal", "abnormal", "critical"):
        summary[s] = sum(1 for p in data if p["status"] == s)
    return jsonify({"summary": summary, "patients": data})


if __name__ == "__main__":
    app.run(debug=True)
