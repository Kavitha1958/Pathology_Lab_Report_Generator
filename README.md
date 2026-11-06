# Pathology Lab Report Generator

CSV -> classify (normal / abnormal / critical) -> SQLite (lab.db) -> console report + web dashboard.

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py      # builds lab.db from sample.csv
python cli.py          # console report
python app.py          # dashboard at http://127.0.0.1:5000
```
Edit `sample.csv` and refresh the page: it re-imports automatically.

## CSV columns
patient_id, name, age, gender, test, result, unit, ref_low, ref_high, date
(one row per test; a patient can have many rows)

## Status rules
Inside the range = normal. Outside = abnormal. More than half a range-width outside = critical.
The patient's overall status is their worst test. mmol/L values for glucose and cholesterol and g/L hemoglobin are converted in `units.py`.
