"""Unit normalisation: convert common SI units to the units labs usually report in."""

# (test keyword, source unit) -> (target unit, multiplier)
CONVERSIONS = {
    ("glucose", "mmol/l"): ("mg/dL", 18.016),
    ("cholesterol", "mmol/l"): ("mg/dL", 38.67),
    ("hemoglobin", "g/l"): ("g/dL", 0.1),
}


def normalize(test, unit, *values):
    """Return (unit, converted_values...). Values may be None."""
    key = (next((k for k in {t for t, _ in CONVERSIONS} if k in test.lower()), ""),
           (unit or "").strip().lower())
    if key in CONVERSIONS:
        new_unit, factor = CONVERSIONS[key]
        return (new_unit, *[None if v is None else round(v * factor, 2) for v in values])
    return (unit, *values)
