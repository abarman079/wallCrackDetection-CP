# Phase03 synthetic development runner — local reproduction

The supplementary development runner was executed against the exact SHA-256-locked original and S5 draft Phase03 source files from `CrackSAFE_P03_S5_VERIFIED_STAGE_20261107T184638Z.zip`.

- Original SHA-256: `3b9d1171e4de2f7ea1b2c29d836fbe45a2a6a7dc4584a671f695b7720b3d656f`.
- S5 draft SHA-256: `cbbad8a5f04e1e2bdf1f4c651004c774a39e3900747f0a50033c6eb22e4fe8d3`.
- Original Phase03 `synthetic_tests(ctx)`: **22 of 22 PASS** in a CPU-only local fixture.
- Previously uploaded GPU preflight archive: exact SHA-256 `ecdc137319daa288f92f38f00f52a5bbab9c843c68ad1a9760b802c75d1a16da`; intact and its `THREE_ENGINE_GPU_PASS` status validated.
- Local execution verifies software workflow only. Kaggle run remains to be executed.
- No real crack training, data labels, calibration, independent splits, or checkpoint-based research metrics were produced.

This must not be confused with official Phase03 FULL or Phase04 scientific authorization.
