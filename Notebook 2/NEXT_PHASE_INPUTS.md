# Exact Phase03 handoff

Phase02 run: `20261018T050513552430Z_afc0e8ab`. Data partition status: **PROVISIONAL**. This handoff does not grant model training permission or scientific certification.

| Logical dependency | Exact artifact | How Phase03 must consume it |
|---|---|---|
| Phase01 controls | `CrackSAFE_CP_v3.3_phase01_control_20261015T111557980168Z_d3a9b41a.zip` + matching `.zip.sha256` | Pin successful run 20261015T111557980168Z_d3a9b41a; outer SHA-256 `ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca`; verify internals before loading code |
| Phase02 controls | `CrackSAFE_CP_v3.3_phase02_control_20261018T050513552430Z_afc0e8ab.zip` + matching `.zip.sha256` | Save Notebook02 output version or upload only this small private pair; read actual outer hash from its sidecar |
| Raw payload | Existing `abarman79/wall-crack-cp-datasets` extracted input | Reuse original mounted folders; resolve with data_shard_index.json and verify logical tree/file hashes; do not upload raw images to GitHub |
| Non-test training/development | train.csv, development_model.csv, development_probability.csv, development_policy.csv, linked hard_negative_development.csv | Require FINAL status, structural disjointness, approved labels/rights and downstream S5/model/code/weights permission + technical gates |
| Common methodology | verified Phase01 statistical_design.json, model_roster.json, blueprint and Phase02 cracksafe_core.zip | Preserve exact statistical implementation, 3-seed protocol and current model roster; no architecture/metric redesign |

`development.csv` is only the union of the three development subsets. `hard_negative_development.csv` is a linked subset of development_policy, not additional independent data. `source_unlabeled_pool.csv` and `target_unlabeled_pool.csv` are reserved and require their explicit approved protocol; never merge them with calibration/tests.

Calibration, internal/external/hard-negative/corruption tests and reserve groups remain held out. Their manifest labels/mask paths are removed. Other views of each held-out group remain reserved. `curator/sealed_labels.parquet`, full sample registry, detailed duplicate/annotation/lineage tables and the optional audit ZIP are curator-only, excluded from the Phase03 control ZIP. Do not add the curator archive to a training notebook. This is a procedural boundary: raw dataset owners can still inspect raw annotations.

Before training: resolve G02/G03/S2/S6 for FINAL data and separately complete S5/model-specific gates. A BLOCKED Phase02 report can accompany successful Python execution; inspect phase_status.json for execution_status, mode, count shortfalls and pending evidence. No later notebook has been generated here.

For GitHub: notebook, sanitized guide, source module and lightweight non-sensitive validation summaries only. Keep raw payloads, review identities/evidence, full registries, held-out labels, audit ZIPs and private controls out of the public repository. No GitHub write is performed by this notebook.
