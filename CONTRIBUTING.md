# Contributing

Use synthetic data only. Do not submit patient information, private operational files, proprietary templates or secrets in code, issues, pull requests or attachments.

1. Describe the behavior you propose to change.
2. Add a synthetic regression test.
3. Run `python -m unittest discover -s tests -v`.
4. Update the documented input contract when needed.

Changes should be small and reviewed by a human. Do not treat model-generated expected results as verified ground truth. Passing tests does not establish clinical safety.

There are no third-party runtime dependencies in this prototype. Review licensing before adding any. Contributions are intended to be distributed under the repository's MIT license.

For security concerns, use a private reporting channel supplied by the repository owner. If none is available yet, request a private channel without posting sensitive details publicly.
