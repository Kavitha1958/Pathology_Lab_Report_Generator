CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    age        TEXT,
    gender     TEXT
);

CREATE TABLE IF NOT EXISTS results (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL REFERENCES patients(patient_id),
    test       TEXT NOT NULL,
    value      REAL NOT NULL,
    unit       TEXT,
    ref_low    REAL,
    ref_high   REAL,
    status     TEXT NOT NULL CHECK (status IN ('normal','abnormal','critical')),
    date       TEXT
);
