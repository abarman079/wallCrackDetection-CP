# CrackSAFE-CP

**Component- and Topology-Aware Risk-Controlling Prediction for Selective Structural Crack Segmentation under Domain Shift**

[Research status](docs/RESEARCH_STATUS.md) · [Reproducibility](docs/REPRODUCIBILITY.md) · [Experiment register](docs/EXPERIMENT_REGISTER.md) · [Results & figures](docs/RESULTS_GUIDE.md) · [Supervisor review](SUPERVISOR_REVIEW.md)

CrackSAFE-CP is an MSc research and engineering repository investigating crack-mask segmentation, crack-component and branch topology, prediction-only uncertainty, selective prediction with exact two-risk control, and robustness under distribution shift. The **authoritative** scientific protocol is [the locked v3.3 blueprint](Notebook%201/blueprint_v3.3.md). The repository distinguishes **executed technical tests**, **actual exploratory training**, and **formal scientific certification**; these are not interchangeable.

> **Status as of 11 November 2026:** Phase-01 and Phase-02 technical audits are complete. Phase-02 independent-unit / annotation / source-rights requirements remain provisional. Phase-03 real **development-only** training is underway on a source-safe candidate split; no nine-job completion or certified FULL benchmark is claimed. Previous Phase-03 SMOKE results are retained as historical evidence.

## Phase-by-phase overview

| Official phase | Purpose | Evidence/status |
|---|---|---|
| [01](Notebook%201/) | Research design, literature, protocol, environment and provenance | Verified technical FULL audit; outstanding human scientific decisions remain recorded |
| [02](Notebook%202/) | Data inventory, lineage, masks and leakage-safe partitions | Technical FULL audit completed; source-safe candidate recovery and 72-pair diagnostic added; partitions **PROVISIONAL** |
| [03](Notebook%203/) | Common-protocol baselines, seeds and ensemble | Original official notebook: SMOKE verified; **separate real development experiments running**, not certified FULL |
| 04 | Branch/connectivity metrics, topology and structural endpoints | Development implementation follows eligible Phase-03 checkpoint evidence |
| 05 | Prediction-only uncertainty and risk scores | Development implementation planned; formal score freeze separately gated |
| 06 | Exact two-risk selective-prediction methodology and competitor | Engineering/synthetic work permitted; certified calibration remains gated |
| 07 | Internal/external and corruption/negative robustness | Genuine held-out tests remain sealed until eligible |
| 08 | Statistical analysis, figures, thesis/paper and reproducibility | Only completed, clearly labeled evidence is publishable |

See the [phase roadmap](docs/PHASE_ROADMAP.md) and [scientific status report](docs/RESEARCH_STATUS.md).

## Development cohort and actual experiments

Phase-02 recovered **13,459** technical image/mask candidates. A conservative corrected manifest placed **7,697** in provisional training and **945** in provisional development, quarantined **3,607** original source-test/validation records and **1,210** mixed-parent records. Technical review of **72** representative pairs found zero sample-level hash/mask-reconstruction errors, but **did not certify mask semantics**.

Because the `UNKNOWN` source masks raised visual concerns, the larger Phase-03 **development-only** cohort excludes **1,086** records, leaving **6,771 training** and **785 development** candidates. No original held-out test or calibration pixels were opened in this source-validation step. See the [Phase-02 public summary](Notebook%202/results/source_safe_v2/PUBLIC_SOURCE_SAFE_V2_SUMMARY_2026-11-11.json) and [Phase-02 public handoff](Notebook%202/docs/PHASE02_SOURCE_SAFE_DEVELOPMENT_HANDOFF_2026-11-11.md).

The active *exploratory* development roster is **U-Net++ EfficientNet-B3**, **SegFormer-B0**, and **adapted U-Net++ ConvNeXt-Tiny**, using seeds `42`, `123`, and `2026`. **SegFormer and adapted ConvNeXt are technical fallbacks, not the original SCSegamba/DMSRCrack architecture slots.** Training is being performed in three model-specific notebooks (one architecture per notebook; three seeds each). No completed nine-run score or ensemble freeze is asserted here. The [register](docs/EXPERIMENT_REGISTER.md) tracks evidence and run identities.

## Navigation

```text
Notebook 1/            Official Phase-01 notebook, code, protocol and selected evidence
Notebook 2/            Official Phase-02 audit, public results and safe preparatory tools
Notebook 3/            Official Phase-03 notebook and preserved SMOKE evidence
  development/v4/      Three model-specific development runners (separate from FULL)
  results/public/       Reviewed, publication-safe per-run summaries/figures

docs/                  Scientific status, methods, reproducibility and policies
scripts/               Validated public-result importer, indexer and checks
.github/workflows/     Public repository integrity checks
```

## Reproduce and inspect

1. Read the [v3.3 blueprint](Notebook%201/blueprint_v3.3.md) and [reproducibility guide](docs/REPRODUCIBILITY.md).
2. Review each official phase notebook and corresponding `docs/` and `results/` directories. The original official notebook is not replaced by development experiments.
3. Use public JSON/CSV/XLSX summaries and original aggregate research figures to inspect auditable results. Each new public run should state the data cohort, architecture, seed, source hash, method, best/last checkpoint SHA where available, and **scientific status**.
4. For full training reproduction, obtain **authorized** source datasets and privately retained manifests/checkpoints; the public repo deliberately does not include their bytes.
5. For technical verification, run `python scripts/check_public_repo.py` and `python scripts/build_public_results_index.py`.

## Public evidence and protected evidence

**Included:** notebooks with safe outputs cleared, Python sources, configuration/protocol descriptions, aggregate JSON/CSV/XLSX, original analysis plots in PNG/JPG (after rights and metadata review), synthetic test results, public SHA-256 digests and reproducibility notes.

**Excluded:** model weights and optimizer states (`.pt`, `.pth`, `.ckpt`), private ZIPs and lineage manifests, raw crack photographs/masks, contact sheets, source rights documentation, reviewer identities and reserved calibration/test records. **A small file is not automatically safe to publish.** See [data governance](docs/DATA_GOVERNANCE.md) and [results policy](docs/RESULTS_GUIDE.md).

## Research interpretation and reuse

This is research software, not a certified structural inspection system. No reliability/coverage guarantee is asserted without a valid frozen method, representative independent calibration and verified risk-control calculations. Publication of technical artifacts does not authorize third-party training data redistribution. [License/citation decision](docs/LICENSE_AND_CITATION.md) is pending research-owner review; no license is silently granted by this repository.
