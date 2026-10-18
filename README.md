# CrackSAFE-CP

**Component- and Topology-Aware Risk-Controlling Prediction for Selective Structural Crack Segmentation under Domain Shift**

This MSc research project studies structural crack segmentation, topology-aware uncertainty, selective inspection-support decisions, exact two-risk statistical control, and domain-shift robustness. The authoritative scientific specification is [Notebook 1/blueprint_v3.3.md](Notebook%201/blueprint_v3.3.md). It specifies exactly eight phases / eight Kaggle notebooks.

## Verified progress

| Phase | Status | Evidence / limitations |
|---|---|---|
| 01 — Design, literature, data inventory | **FULL technical execution complete** | Canonical preserved run `20261015T111557980168Z_d3a9b41a`; phase02 audit-ready; human approvals and model smoke checks remain pending |
| 02 — Data integrity, leakage, annotation, splits | **FULL technical execution complete; scientific status BLOCKED** | Run `20261018T050513552430Z_afc0e8ab`: 121,794 files inventoried, 88,806 decoded images, PROVISIONAL partitions, zero eligible certified units; provenance, grouping, annotations, source permissions and duplicate-retrieval caps still require resolution |
| 03 — Baselines and three-seed ensemble | **Not authorized for training** | Requires approved FINAL Phase-02 data splits, applicable S2/S5/S6 decisions, model/weights permissions and technical gates |
| 04–08 | Planned | Follow the locked v3.3 blueprint and phase exit gates |

Technical completion is not equivalent to independent data validity, supervisor approval, statistical certification or a conclusion about structural safety.

## Storage boundary

This **public** repository stores selected lightweight code, notebooks, tests, provenance metadata, and research documentation. Private Kaggle storage holds original images/masks, reviewer records, sealed test labels, full audit inventories, large control bundles, model checkpoints and training outputs. Do not commit raw data, full control ZIPs, private curator archives, credentials or held-out labels.

## Provenance

- The Phase-01 files under `Notebook 1/` are synchronized to the newer preserved FULL control bundle (`11:15:57 UTC` start), whose outer SHA-256 is `ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca`.
- Phase-02 FULL control-bundle SHA-256: `9d87e629fa12d142bbb473384a7b932536edf59e33fd65c7e797c730349a7c99`; data partitions remain PROVISIONAL.
- The original Phase-01 validation report refers to a pre-correction 47-cell notebook. The committed executable Phase-01 notebook was corrected to 49 cells; see `Notebook 1/docs/PHASE01_RUN_RECONCILIATION.md` for details.

The repository does not itself establish authorization to train or make formal risk-control claims.

## Repository layout

- [Phase 01](Notebook%201/README.md): notebook, source, design locks, documentation and run-specific small result records.
- [Phase 02](Notebook%202/README.md): notebook, audited implementation, documentation and small validation results; scientific gates still blocked.
- Future phases will follow the same `Notebook N/` pattern.

Within each phase, keep the executable notebook and downstream contracts at the top level; use `docs/` for reports and `results/run_<actual_id>/` for reproducible, non-sensitive outputs. Full Kaggle archives and private records are stored outside the public Git tree; any local copies live in an ignored `local_artifacts/` directory.
