# Phase 02 — Supervisor results index

**Run:** `20261018T050513552430Z_afc0e8ab`
**Execution:** `COMPLETED` (FULL); **scientific status:** `BLOCKED`; **partitions:** `PROVISIONAL`
**Verified immutable control ZIP SHA-256:** `9d87e629fa12d142bbb473384a7b932536edf59e33fd65c7e797c730349a7c99`

## Figures (aggregate diagnostics, not model performance)

- [Annotation review categories](figures/decode_review_categories.png)
- [Independent calibration-unit shortfalls](figures/calibration_independent_unit_shortfall.png)

## Reports

- **Dataset inventory & provenance:** [data card](audit/data_card.md), [collection hashes](audit/archive_inventory.csv), [original-source rights states](audit/dataset_registry.csv)
- **Image validation:** [decode summary](audit/decode_summary.json), [leakage and curation report](audit/leakage_report.md), [near-duplicate index coverage](audit/near_index_report.json)
- **Independence:** [assessment](audit/independence_assessment.md), [population contract](audit/population_contract.md), [historical reuse decision](audit/mrc_reuse_decision.json)
- **Calibration:** [sanitized capacity summary](sampling/calibration_capacity_PUBLIC.json)
- **Scientific gates:** [decision gates](status/decision_gates.csv), [technical split validation](status/split_validation.json), [stage errors](status/stage_errors.json)
- **Reproducibility:** [upstream Phase-01 verification](provenance/phase01_verification.json), [upstream mathematical tests](validation/upstream_statistical_self_tests.json)

## Interpreting this run

- **121,794** raw filesystem members were inventoried across five mounted collections, and **88,806** image records were examined.
- **24,704** exact-duplicate linkage edges and **13,768** perceptual near-duplicate candidates were reported. Neither is a count of independent pairs. Near-index caps affected **16,304** samples; arbitrary crop recall is not guaranteed.
- Conservatively linked certification units: **1**; **eligible independent units: 0**. This does **not** mean that there was one actual acquisition session. Original source/parent/site/session evidence is unresolved.
- The calibration availability floors are **120 independent positives / 122 independent confirmed negatives**, preferred **300 / 300**. Current eligible count is **0 / 0**.
- Source rights, original-source lineage, annotation adjudication, mask encoding, duplicate completeness, fixed sampling plan and supervisor gates remain pending. No models were evaluated; no calibration/test outcomes were inspected.

**Public repository boundary:** No private `sample_registry.parquet`, `parent_lineage.csv`, `exact_duplicates.csv`, `near_duplicates.csv`, `quarantine.csv`, reviewer decisions, held-out IDs/labels, detailed role manifests, raw images, masks or full control/private ZIPs are published here. The private 44 MB evidence archive and the complete immutable controls remain in controlled storage. The public capacity JSON removes unit identifiers and roles.

**Research-use boundary:** This is a scientific audit, not a successful crack-segmentation result, approval to train, certification of a safety claim, or proof of population independence.
