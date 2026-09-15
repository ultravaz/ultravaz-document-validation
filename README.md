# Ultra Vaz Document Validation Toolkit

A small Python prototype for deterministic validation and provenance of structured document inputs. Built as a standalone project; it does not contain or depend on the private clinic application.

**Status:** initial prototype, not clinically validated. No public adoption or grant award is claimed.

## What works

- Checks a deliberately small, documented JSON input format.
- Rejects missing or unknown fields, duplicate measurement identifiers, non-finite numbers and unsupported units.
- Produces a SHA-256 fingerprint of the exact input bytes in the CLI result.
- Runs locally using only the Python standard library. No network calls, AI service, API key or paid subscription is needed.

A valid result means only that the input passes these structural rules. It does **not** mean the content is factually or medically correct. This is not a diagnostic system, a privacy scanner, or a replacement for professional review.

## Quick start

Requires Python 3.10 or newer. From this repository's root:

```sh
python -m ultravaz_validator examples/valid.json
python -m ultravaz_validator examples/invalid.json
python -m unittest discover -s tests -v
```

The CLI prints a JSON result to standard output and does not write report files.
Exit codes: `0` valid, `1` validation failed, `2` unreadable input or invalid JSON.
The invalid example is intentionally expected to fail.

## Input contract (version 1.0)

The root must be an object with exactly these fields:

| Field | Rule |
| --- | --- |
| `schema_version` | String `"1.0"` |
| `document_id` | Nonblank string (use a synthetic identifier in public examples) |
| `measurements` | Nonempty array of measurement objects |

Each measurement must have exactly `id`, `value`, and `unit`.
Identifiers must be nonblank and unique after trimming whitespace (case-sensitive).
Values must be finite, nonnegative JSON numbers; booleans are not numbers.
Supported units: `mm`, `cm`, `mL`. Units are checked, not converted; clinical ranges and cross-field relationships are not checked.
Unknown fields and duplicate JSON object keys are rejected.

The input limit is 1 MiB. Error results do not echo measurement values.
The manifest records the input byte hash, byte count, validator version and validation outcome. A hash identifies bytes; it does not prove their origin, anonymity, or correctness. Reformatting JSON changes its byte hash.

## Privacy and contributions

Only synthetic examples belong in this repository. Never add patient records, images, credentials, private templates or operational logs. The validator does not anonymize input. Keep private data outside the repository even if ignored by Git.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing.

## Roadmap — not implemented

- Configurable field rules and additional provenance relationships.
- Reproducible evaluation of AI-generated structured outputs using synthetic cases.
- Optional developer tooling and broader failure-mode benchmarks.

These are future plans, not features in this release. Changes require review and tests; model-generated output is not ground truth.

## Português

Protótipo independente para validar dados estruturados e registrar sua impressão digital SHA-256. Os exemplos são fictícios. Não gera diagnósticos, não interpreta imagens e não comprova precisão clínica. As instruções acima funcionam também no PowerShell do Windows. Não publique dados da clínica.

## License

MIT — see [LICENSE](LICENSE). Applies only to this standalone repository, not to the private clinic application or third-party materials.
