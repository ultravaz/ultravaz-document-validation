import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ultravaz_validator import validate
from ultravaz_validator.__main__ import MAX_BYTES, main


def sample():
    return {
        "schema_version": "1.0",
        "document_id": "synthetic-001",
        "measurements": [{"id": "sample", "value": 1.2, "unit": "mm"}],
    }


class ValidationTests(unittest.TestCase):
    def test_valid_and_no_mutation(self):
        data = sample()
        original = copy.deepcopy(data)
        self.assertEqual(validate(data), [])
        self.assertEqual(data, original)

    def test_invalid_root(self):
        for value in (None, [], "text", 1):
            with self.subTest(value=value):
                self.assertTrue(validate(value))

    def test_each_missing_field(self):
        for key in sample():
            data = sample()
            del data[key]
            self.assertTrue(validate(data))
        for key in sample()["measurements"][0]:
            data = sample()
            del data["measurements"][0][key]
            self.assertTrue(validate(data))

    def test_unknown_fields(self):
        data = sample()
        data["unexpected"] = "synthetic"
        self.assertTrue(validate(data))
        data = sample()
        data["measurements"][0]["unexpected"] = True
        self.assertTrue(validate(data))

    def test_version_and_blank_identifier(self):
        for key, value in (("schema_version", 1), ("schema_version", "2.0"),
                           ("document_id", " "), ("document_id", None)):
            data = sample()
            data[key] = value
            self.assertTrue(validate(data))

    def test_measurements_shape(self):
        for value in ([], {}, None, [None]):
            data = sample()
            data["measurements"] = value
            self.assertTrue(validate(data))

    def test_duplicate_id_whitespace(self):
        data = sample()
        data["measurements"].append({"id": " sample ", "value": 1, "unit": "cm"})
        self.assertIn("duplicate_id", [e["code"] for e in validate(data)])

    def test_bad_measurement_values(self):
        for value in (True, False, None, "1", -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                data = sample()
                data["measurements"][0]["value"] = value
                self.assertTrue(validate(data))

    def test_zero_and_large_integer(self):
        for value in (0, 10 ** 400):
            data = sample()
            data["measurements"][0]["value"] = value
            self.assertEqual(validate(data), [])

    def test_units(self):
        for unit in ("mm", "cm", "mL"):
            data = sample()
            data["measurements"][0]["unit"] = unit
            self.assertEqual(validate(data), [])
        for unit in ("MM", "", [], {}, None):
            data = sample()
            data["measurements"][0]["unit"] = unit
            self.assertTrue(validate(data))

    def test_measurement_identifier(self):
        for identifier in (" ", None, 1):
            data = sample()
            data["measurements"][0]["id"] = identifier
            self.assertTrue(validate(data))


class CliTests(unittest.TestCase):
    def run_input(self, raw):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.json"
            path.write_bytes(raw)
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(path)])
            return code, json.loads(output.getvalue())

    def test_manifest(self):
        raw = json.dumps(sample()).encode()
        code, result = self.run_input(raw)
        self.assertEqual(code, 0)
        self.assertTrue(result["valid"])
        self.assertEqual(result["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["input_bytes"], len(raw))
        self.assertNotIn("synthetic-001", json.dumps(result))

    def test_invalid_structure(self):
        code, result = self.run_input(b'{}')
        self.assertEqual(code, 1)
        self.assertFalse(result["valid"])

    def test_malformed_and_duplicate_json(self):
        for raw in (b'{', b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}',
                    b'\xff'):
            code, result = self.run_input(raw)
            self.assertEqual(code, 2)
            self.assertEqual(result["errors"][0]["code"], "invalid_json")

    def test_deep_array_is_rejected(self):
        # Decoder recursion limits differ between supported Python versions.
        code, result = self.run_input(b'[' * 2000 + b']' * 2000)
        self.assertIn(code, (1, 2))
        self.assertFalse(result["valid"])

    def test_size_limit(self):
        code, result = self.run_input(b' ' * (MAX_BYTES + 1))
        self.assertEqual(code, 2)
        self.assertEqual(result["errors"][0]["code"], "input_too_large")

    def test_unreadable_input(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(Path(directory) / "missing.json")])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["errors"][0]["code"],
                             "unreadable_input")


if __name__ == "__main__":
    unittest.main()
