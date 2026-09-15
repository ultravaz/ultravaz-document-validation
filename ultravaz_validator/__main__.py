"""CLI: read locally, validate, and emit metadata without copying input values."""

import argparse
import hashlib
import json
from pathlib import Path

from . import __version__, validate

MAX_BYTES = 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonstandard JSON constant")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    result = {"validator_version": __version__}
    try:
        with args.input.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    except OSError:
        result.update(valid=False, errors=[{"code": "unreadable_input"}])
        print(json.dumps(result))
        return 2
    if len(raw) > MAX_BYTES:
        result.update(valid=False, errors=[{"code": "input_too_large"}])
        print(json.dumps(result))
        return 2
    result.update(input_sha256=hashlib.sha256(raw).hexdigest(), input_bytes=len(raw))
    try:
        document = json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (ValueError, RecursionError):
        result.update(valid=False, errors=[{"code": "invalid_json"}])
        print(json.dumps(result))
        return 2
    errors = validate(document)
    result.update(valid=not errors, errors=errors)
    print(json.dumps(result))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
