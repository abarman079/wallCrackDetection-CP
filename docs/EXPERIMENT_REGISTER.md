# Experiment register — public view

This table records experiment *families*, not claimed completed jobs. Update after verifying each seed's private checkpoint SHA and actual public-safe metrics JSON. Never put private per-image rows here.

| Family | Phase | Cohort | Architecture / purpose | Seeds | Latest evidence | Scientific class |
|---|---|---|---|---|---|---|
| P01 preserved run | 01 | Audit inputs | Environment, source registry, fixed protocol | n/a | Completed run `20261015T111557980168Z_d3a9b41a` | Technical FULL |
| P02 preserved run | 02 | Raw audit inventory | Decoding, provenance, lineage/split audit | n/a | Completed run `20261018T050513552430Z_afc0e8ab` | Technical FULL; split provisional |
| P02 source-safe v2 | 02 | 13,459 candidates | Conservative split, 72 sampled diagnostic | 2026 diagnostic sampling | Diagnostic ZIP SHA `bde823...` | Technical only; masks unapproved |
| P03 original SMOKE | 03 | Synthetic/unit fixtures | Blueprint architecture adapter tests | n/a | Run `20261104T061629907173Z_68452d4f` | SMOKE only |
| P03 v4 model A | 03 | 6,771 train / 785 dev | U-Net++ EfficientNet-B3 | 42, 123, 2026 | Reported real job launches; final outputs pending | DEVELOPMENT |
| P03 v4 model B | 03 | Same | SegFormer-B0 technical fallback | 42, 123, 2026 | Reported real job launches; final outputs pending | DEVELOPMENT |
| P03 v4 model C | 03 | Same | Adapted U-Net++ ConvNeXt-Tiny fallback | 42, 123, 2026 | Reported real job launches; final outputs pending | DEVELOPMENT |
| P04–P08 | 04–08 | As allowed by gates | Topology, risk, certification and robustness | Protocol-dependent | No certified output in this snapshot | Planned/development contingent |

### Standard public per-seed result fields

Include `schema_version`, `phase`, `run_id`, `architecture`, `seed`, `cohort_public_id`, `train_count`, `dev_count`, `data_manifest_sha256`, `training_code_sha256`, `protocol_id`, `best_epoch`, `development_dice`, `development_cldice`, `checkpoint_best_sha256` (digest **only**), `checkpoint_last_sha256`, `evaluation_policy`, `execution_status`, `scientific_status`, and `evidence_reference` where available. **Never manufacture absent fields; use null or `NOT_AVAILABLE`.**

Previous separate DeepCrack 0.721743 Dice at epoch 56 and 600-image pilot Dice around 0.4134 at epoch 3 must remain in separately identified exploratory registers, not a ranked comparison against v4.
