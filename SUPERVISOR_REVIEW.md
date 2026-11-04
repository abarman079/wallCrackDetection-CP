# CrackSAFE-CP v3.3 â€” Supervisor review portal

**Research:** Component- and Topology-Aware Risk-Controlling Prediction for Selective Structural Crack Segmentation under Domain Shift.
**Repository:** https://github.com/abarman079/wallCrackDetection-CP
**Blueprint:** [locked v3.3](Notebook%201/blueprint_v3.3.md) â€” exactly eight phases / eight notebooks.

## How to inspect the completed technical work

| Phase | Executable notebook | Public results and figures | Kaggle notebook | Scientific status |
|---|---|---|---|---|
| 01 | [Notebook 1](Notebook%201/CrackSAFE_CP_Phase01_Legacy_Design_Literature_Locks.ipynb) | [Run 01 results index](Notebook%201/results/run_20261015T111557980168Z_d3a9b41a/RESULTS_INDEX.md) | [Kaggle Phase 01](https://www.kaggle.com/code/abarman79/cracksafe-cp-phase01-legacy-design-literature-lock) | FULL inventory completed; approvals pending |
| 02 | [Notebook 2](Notebook%202/CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb) | [Run 02 results index](Notebook%202/results/run_20261018T050513552430Z_afc0e8ab/RESULTS_INDEX.md) | [Kaggle Phase 02](https://www.kaggle.com/code/abarman79/cracksafe-cp-phase02-kaggle-archivecarrier-recover) | FULL technical audit completed; PROVISIONAL / BLOCKED |
| 03 | [Notebook 3](Notebook%203/CrackSAFE_CP_Phase03_Legacy_Modern_Baselines.ipynb) | [SMOKE results](Notebook%203/results/run_20261104T061629907173Z_68452d4f/RESULTS_INDEX.md) | [Kaggle Phase 03](https://www.kaggle.com/code/abarman79/cracksafe-cp-phase03-legacy-modern-baselines) | SMOKE PASS; real training BLOCKED |
| 04â€“08 | Planned | No results | â€” | Follow v3.3 gates |

*Kaggle URLs were provided by the project owner; their currently displayed versions were not externally accessible during this audit. These GitHub results correspond to the cryptographically verified archived runs listed below.*

**Phase-03 note:** Kaggle SMOKE run `20261104T061629907173Z_68452d4f` verified Phase-01/02 inputs, passed 22 synthetic engineering tests, and exported verified outputs. No real model training, empirical accuracy, ensemble selection or risk certification was performed.

## Phase-02 remediation update — 4 November 2026

Read the [Phase-02 Remediation Progress](Notebook%202/docs/PHASE02_REMEDIATION_PROGRESS_2026-11-04.md) for the latest dataset investigation, unresolved scientific requirements and training-readiness status.

## What has actually been demonstrated

- **Phase 01:** five extracted source collections inventoried; fixed statistical design and versioned handoff generated. External approvals and reproducibility evidence remain incomplete. **No model accuracy was measured.**
- **Phase 02:** FULL run `20261018T050513552430Z_afc0e8ab` processed **121,794 filesystem members**, examined **88,806 image records**, reported **44,616 quarantine records**, and completed the audit/export with **no stage errors**. However, available independent eligible certification units = **0**; splits are **PROVISIONAL**; **training is blocked**.
- Pending: source rights, original source and parent/site/session provenance, annotation and mask review, complete duplicate search, representative sampling/independence justification and supervisor approvals S2/S6/G02/G03. Model code/weights permissions and S5 training authorization are later requirements.

## Evidence integrity and provenance

| Source | Immutable run ID | Preserved outer ZIP SHA-256 |
|---|---|---|
| Phase-01 FULL control | `20261015T111557980168Z_d3a9b41a` | `ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca` |
| Phase-02 FULL control | `20261018T050513552430Z_afc0e8ab` | `9d87e629fa12d142bbb473384a7b932536edf59e33fd65c7e797c730349a7c99` |

The individual public results are copies or sanitized derivatives of immutable outputs; their GitHub organization is for review, not a replacement for the original sealed internal paths. PNG figures summarize *descriptive* counts; they are **not model-performance figures** and should not be described as evidence of improved segmentation or clinical/structural safety.

## Data protection, reproduction, and rights

The source datasets and complete per-image audits contain raw or potentially restricted research materials. The repository intentionally omits raw crack images, masks, full private audit ZIPs, reviewer identities, sample-level lineage and duplicate registries, held-out roles and labels, and model checkpoints. These remain in versioned controlled Kaggle storage; evidence is available to authorized reviewers subject to dataset licenses. No data-rights approval is implied by GitHub visibility or Kaggle hosting. Use the [Phase-02 handoff](Notebook%202/NEXT_PHASE_INPUTS.md) for the next dependency and gating status.
