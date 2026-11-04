# CrackSAFE-CP Phase02 data card

Blueprint v3.3, run 20261018T050513552430Z_afc0e8ab. Existing private source: abarman79/wall-crack-cp-datasets. Five extracted source collections; zero raw ZIPs required. Full source bytes are never copied into outputs. Phase01 logical raw_archive_count=5 is not a ZIP count.

Observed filesystem members: 121794. Examined image records: 88806. Adjudicated class counts at image level: {'UNKNOWN': 88806}. Proposed certification units: 1. Actual independent-unit availability and shortfalls are in calibration_sampling_plan.json; image/crop counts are not independent observations.

Uses: curator data quality, provenance, leakage and provisional scientific planning. Prohibited automatic conclusions: legal clearance, correct labels from folder names, IID from unique hashes, calibration certification, zero-shot generalization, reproduced legacy metrics or model performance. Rights are per original source. Redistribution remains separately reviewed even if private research use is permitted.

Preprocessing primitives: native pixel orientation is retained; nontrivial EXIF requires review. RGB image conversion, binary masks, 448 aspect-preserving letterbox, nearest-neighbor mask resize and explicit valid-padding mask. No small-ground-truth-component pruning. Mask formats with unknown color/ignore semantics remain quarantined.

SMOKE audits a deterministic bounded image subset and never certifies full integrity or final splits. FULL hashes every source member and audits every detected image/mask candidate. Unknown/partial/missing labels and unmapped pairing cases are retained as explicit review/exclusion records. No data collection or representativeness claim is inferred from file naming.
