"""Deterministic structural checks for synthetic document examples."""

import math

__version__ = "0.1.0"
UNITS = frozenset({"mm", "cm", "mL"})


def validate(document):
    """Return errors; an empty list means structural validity, not clinical validity."""
    errors = []

    def issue(path, code):
        errors.append({"path": path, "code": code})

    if not isinstance(document, dict):
        issue("$", "expected_object")
        return errors
    required = {"schema_version", "document_id", "measurements"}
    if set(document) - required:
        issue("$", "unknown_fields")
    for key in sorted(required - set(document)):
        issue(key, "missing_field")
    if document.get("schema_version") != "1.0":
        issue("schema_version", "unsupported_version")
    identifier = document.get("document_id")
    if not isinstance(identifier, str) or not identifier.strip():
        issue("document_id", "expected_nonblank_string")
    measurements = document.get("measurements")
    if not isinstance(measurements, list) or not measurements:
        issue("measurements", "expected_nonempty_array")
        return errors
    seen = set()
    for index, item in enumerate(measurements):
        path = f"measurements[{index}]"
        if not isinstance(item, dict):
            issue(path, "expected_object")
            continue
        fields = {"id", "value", "unit"}
        if set(item) - fields:
            issue(path, "unknown_fields")
        for key in sorted(fields - set(item)):
            issue(f"{path}.{key}", "missing_field")
        name = item.get("id")
        if not isinstance(name, str) or not name.strip():
            issue(f"{path}.id", "expected_nonblank_string")
        elif name.strip() in seen:
            issue(f"{path}.id", "duplicate_id")
        else:
            seen.add(name.strip())
        value = item.get("value")
        if type(value) not in (int, float):
            issue(f"{path}.value", "expected_number")
        elif isinstance(value, float) and not math.isfinite(value):
            issue(f"{path}.value", "expected_finite_number")
        elif value < 0:
            issue(f"{path}.value", "expected_nonnegative_number")
        unit = item.get("unit")
        if not isinstance(unit, str) or unit not in UNITS:
            issue(f"{path}.unit", "unsupported_unit")
    return errors
