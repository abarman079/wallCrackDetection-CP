# CrackSAFE-CP Phase02 — Kaggle guide, output inventory and Phase03 handoff

This guide accompanies `CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb`. It implements Phase02 only under the unchanged v3.3 blueprint. It audits data and prepares partitions; it does not train a model, perform risk certification, or grant scientific approvals.

## 1. Attach exactly two logical inputs

| Input | What to attach | What it provides |
|---|---|---|
| Raw data | Your existing private `abarman79/wall-crack-cp-datasets` dataset | The five already-extracted source collections |
| Phase01 controls | The pinned saved output of the successful Phase01 run, **or** a small private dataset containing the exact control ZIP and its sidecar | Verified shared code, source fingerprints, blueprint and scientific locks |

The required control pair is:

```text
CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip
CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip.sha256
```

Its locked outer SHA-256 is:

```text
3543b6c09bb4ce2c577d8632c825b6f12d423c0f881afb137457db313566708d
```

**Method A — saved notebook output.** In Kaggle's input-attachment interface, select your completed Phase01 notebook output and the version containing that exact successful run. Inspect its files to confirm the ZIP and sidecar are present. The source notebook itself or public GitHub reports are insufficient. Avoid attaching several copies of the same control pair.

**Method B — small private controls dataset.** Download only that ZIP and its matching sidecar from the successful Phase01 output. Put those two files in a private Kaggle dataset and attach it. Keep the ZIP intact as a file; do not replace it with a manually rebuilt archive. Inspect the mounted file list afterward. If your upload workflow expands the archive instead of retaining it, use Method A. Later, reviewed CSVs and their evidence documents can live in this same logical controls input.

You do not need to upload raw images again, convert the extracted folders to ZIPs, attach GitHub, or supply original legacy evidence that is currently unavailable. The original Phase01 run remains `BLOCKED` for later scientific reasons while `phase02_audit_ready=true` permits this initial data audit.

## 2. Recognize the raw layout

The previous actual root was `/kaggle/input/datasets/abarman79/wall-crack-cp-datasets/`. Automatic discovery searches below `/kaggle/input`; it does not assume a fixed mount depth.

| Logical collection directory | Phase01 filesystem-file count |
|---|---:|
| `CRACK500 CrackTree200 GAPS384` | 18,887 |
| `CrackForest dataset(CFD)` | 547 |
| `DeepCrack` | 1,075 |
| `SDNET2018` | 56,092 |
| `crack segmentation dataset` | 45,193 |
| **Total** | **121,794** |

These supplied Phase01 counts are filesystem entries, not verified image-mask pairs or independent observations. The aggregate collection is not a sixth or independent original source. The historical 11,298-pair figure is not used as an audited current count. The backward-compatible Phase01 `raw_archive_count=5` means logical sources, not five raw ZIPs.

## 3. Import and run the rehearsal

1. Create/import a Python notebook in Kaggle and upload the delivered `.ipynb` using the notebook import/upload option.
2. Set the accelerator to **None/CPU** and internet to **Off**. Attach the two inputs above. Kaggle interface wording can vary; use the input and version controls in your current editor.
3. Leave `run_mode='SMOKE'`. The default is at most 40 candidate images per collection, with their masks, plus bounded fingerprint sampling. Keep the integrity constants and helper cells unchanged.
4. Leave `raw_root` and `phase01_bundle` as `None` unless discovery reports a missing or ambiguous mount. If needed, copy the actual mounted paths from Kaggle's input browser into those configuration fields.
5. Run the notebook from top to bottom. Its helper cells define functions; the numbered execution stages then perform the work. The first stage checks installed dependencies without downloading packages.
6. Read the Stage01 verification, Stage02 source summary, decoding summary, primitive tests and final export summary. A successful rehearsal can finish with scientific status `BLOCKED` and partition status `PROVISIONAL`.

Dependencies are `numpy`, `pandas`, `Pillow`, `scipy`, `scikit-image`, and `pyarrow`. Their observed versions are recorded at runtime. If one is unavailable, use a Kaggle runtime that supplies it or install from locally attached offline wheels. No GPU, network download or model checkpoint is required.

The default output root is:

```text
/kaggle/working/cracksafe_cp/phase02/run_<run_id>/
```

The notebook prints the exact run directory. Nothing is written into the raw input dataset.

## 4. Run FULL and interpret the result

After SMOKE completes, change only `run_mode` to `FULL`, leave `resume_run_dir=None`, and restart/run from the beginning. Save a Kaggle version with the full execution and outputs. FULL streams a SHA-256 over every source member, reconstructs Phase01's exact ordered source digest, and audits every detected image/mask candidate.

The default uses two decode workers, 64-record batches, an eight-hour planning budget, a 30-minute export buffer, and a 2 GiB free-disk floor. These are conservative configuration values, not a promise about current Kaggle quotas or runtime duration. `resource_estimate.json` records a disk allowance; `check_budget` monitors elapsed time and free space. Adjust the session budget to your actual available runtime.

| Field/result | Meaning |
|---|---|
| `execution_status=COMPLETED` | Python stages and required export completed |
| `partition_status=PROVISIONAL` | Scientific use of the proposed partitions is not approved |
| `status=BLOCKED` | Inspect pending evidence, gates and capacity; this alone is not a Python crash |
| `execution_status=FAILED` | Inspect `stage_errors.json` and the named failing stage |
| `execution_status=PARTIAL_BUDGET` | Unsealed checkpoint/cache is available for a compatible resume |
| `phase03_audit_ready=true` | Full raw integrity audit completed; this does not authorize training |
| `phase03_training_authorized=false` | Phase03 must separately satisfy S5 and model permission/technical gates |
| `bundle_verification.json: PASS` | Control bundle hashes/CRC/manifest passed, not scientific certification |

With no human evidence supplied, many or all units may be ineligible, training/calibration CSVs may be empty, and all partitions remain provisional. That is an intentional result: the notebook does not manufacture provenance, negative labels, rights, reviewer decisions or IID observations.

## 5. Complete actual review work

Use `curator/review_queue.csv`, the private audit tables, `annotation_manual_v1.md` and the empty `review_templates/` CSVs. Review files are bound to stable IDs and image/mask hashes. Record actual reviewer identity, review time, relative evidence path and evidence-document SHA-256.

- **Pairing:** normalized image/mask paths, DeepCrack img/lab paths, CFD MATLAB ground-truth structures and source-specific CRACK500 JPEG/PNG pairs are supported. Unmatched or ambiguous layouts require an evidenced pair override. Unknown colored/ignore masks and nontrivial EXIF orientation remain quarantined.
- **Annotation:** a positive topology example needs a complete aligned segmentation mask. SDNET classification-positive images without pixel masks cannot become topology-labelled positives. Missing or all-zero masks are not automatically negatives. Expert-confirmed complete negatives can authorize virtual zero masks. Thin cracks and small ground-truth components are preserved.
- **Independent review:** a deterministic label-blind image subset of `min(N, max(ceil(0.20*N), 30))`, plus every disagreement, needs distinct reviewers. There is also a unit-level representative coverage check. Disagreement requires a distinct expert adjudicator and written resolution. Incomplete, disputed, occluded and uncertain labels remain unknown.
- **Lineage:** document original source, site, session, parent, original-image and crop relationships. Highest known acquisition groups are used conservatively; unknown acquisitions are not IID singletons. Shared parent facts are linked even when metadata completeness differs across records.
- **Rights:** provide a separate original-source rights record. Research use and redistribution have independent states. Include the actual license-text file and matching hash, source URL, conditions and reviewer resources. Kaggle hosting or aggregation does not grant permission.
- **Legacy exposure:** zero discovered Phase01 legacy files does not prove a fresh test set. `CLEAR` requires evidence.

Put completed CSVs and evidence documents under a directory in the same logical controls input. Set `evidence_dir` to its actual mounted location and start a new run. Never edit the raw images/masks in place; corrected raw annotations require a reviewed new data handoff.

The first reviewed run produces a concrete `plan_sha256` in `calibration_sampling_plan.json`. Human reviewers can then approve that exact plan through `approvals.csv`. A subsequent run with the same review evidence and plan-bound approvals can reach FINAL only if the technical requirements also pass. Changed annotation/lineage evidence changes the review basis and invalidates stale approval hashes. SMOKE can never finalize partitions.

## 6. Understand the partitions and feasibility report

A `split_group_id` identifies linked observations that cannot cross roles. A separate `certification_unit_id` identifies the proposed independent acquisition unit. There is one seeded, label-blind representative per held-out unit. Other views of the held-out group never enter training.

Source and target unlabeled pools use documented domains and label-blind group-ID draws before label-based allocation. Target sources must be explicitly declared through `external_source_ids`; UNKNOWN provenance is never silently called a target domain. Original-source external exclusion follows transitive duplicate/lineage groups, including aggregate copies.

After these allocations and hard-negative/corruption reservations, fixed reserves and the internal test are reserved before calibration. The actual remaining class counts are compared with **120 positive / 122 negative available-unit floors** and **300 / 300 preferred targets**. Exact shortfalls are recorded. The unchanged Phase01 accepted zero-failure minima of 60/122 are not substitute availability floors. No test borrowing, outcome-triggered additions, automatic low-data alternative or adaptive retry is implemented.

The default internal-test counts, reserves, unlabeled-pool counts and development fraction are reviewable planning proposals. Their approval is not implied by their presence in CONFIG. A fixed scientific population and sampling rationale remain necessary: curation and deduplication alone do not prove IID or future source-mixture stability.

| Role CSV | Meaning and access |
|---|---|
| `train.csv` | Training views from eligible development-side groups |
| `development_model.csv` | Model/hyperparameter development |
| `development_probability.csv` | Probability/temperature development |
| `development_policy.csv` | Policy/threshold development |
| `development.csv` | Compatibility union of the three development subsets |
| `hard_negative_development.csv` | Linked subset of `development_policy`, not an additional independent role |
| `calibration.csv` | Reserved representative units; labels/mask paths withheld |
| `internal_test.csv` | Independent final internal test groups |
| `external_positive_test.csv` | Unseen-original-source positive test groups |
| `hard_negative_test.csv` | Separately reserved expert-confirmed hard negatives |
| `source_unlabeled_pool.csv` | Separate documented source-domain units, labels withheld |
| `target_unlabeled_pool.csv` | Separate declared target-domain units, labels withheld |
| `reserve_pool.csv` | Fixed reservations and explicitly ineligible/excluded groups; not all rows are usable reserve data |
| `corruption_test.csv` | Distinct held-out parent units for the locked route B |

Development is divided 60/20/20 by groups, with rounding disclosed by actual counts. Small empty subsets are a capacity problem; the notebook does not borrow tests to conceal it. The shared development loader rejects PROVISIONAL and held-out manifests, verifies image and mask bytes, and supports explicit same-content directory mappings.

## 7. Complete output inventory

All files are under the printed run directory. “Control” means included in the Phase02 control ZIP; it does not mean publicly redistributable. “Private” means retained separately for the curator and excluded from the Phase03 control ZIP.

| Outputs | Purpose | Packaging |
|---|---|---|
| `dataset_registry.csv` | Original-source rights and provenance states | Control |
| `archive_inventory.csv`, `dataset_discovery.json`, `resource_estimate.json` | Source fingerprints, mount resolution and resource planning | Control |
| `file_inventory.parquet`, `raw_fingerprint_mismatches.csv` | Full raw member ledger and discrepancies | Private |
| `sample_registry.parquet`, `pairing_audit.csv` | Decoded sample inventory and pair problems | Private |
| `decode_summary.json` | Decode states and cache counters | Control |
| `exact_duplicates.csv`, `near_duplicates.csv`, `parent_lineage.csv`, `quarantine.csv` | Detailed duplicate, dependency and exclusion evidence | Private |
| `near_index_report.json`, `leakage_report.md` | Candidate-index limitations and leakage summary | Control |
| `mrc_reuse_decision.json`, `legacy_exposure_registry.csv` | Historical reuse limits and per-sample exposure | Decision: Control; registry: Private |
| `annotation_manual_v1.md`, `hard_negative_spec.md`, `hard_negative_categories.yaml` | Review instructions and locked category vocabulary | Control |
| `annotation_audit.csv`, `reviewer_agreement.csv` | Actual imported annotation decisions, ambiguity and agreement | Private |
| `population_contract.md`, `independence_assessment.md`, `certification_units.csv` | Proposed population and unit roster, with public roster labels removed | Control |
| `calibration_sampling_plan.json`, `data_card.md` | Actual capacity, fixed plan hash and use limitations | Control |
| All 14 role CSVs listed above | Proposed/final role assignments with explicit status | Control |
| `split_hashes.sha256`, `data_shard_index.json` | Split integrity and portable raw-data references; no copied image shards | Control |
| `metric_primitives_test_report.json`, `upstream_statistical_self_tests.json` | Minimal Phase02 primitives and unchanged Phase01 mathematical checks | Control |
| `cracksafe_core.zip`, `phase02_core.py`, `workflow_source.json` | Reusable code and source identity | Control |
| `config.json`, `run_identity.json`, `environment_snapshot.json`, `data_access_log.csv`, `stage_checkpoints.json` | Runtime configuration, provenance and progress | Control |
| `schemas.json`, `artifact_catalog.json` | Table schemas, row counts, file hashes, sizes and packaging decisions | Control |
| `decision_gates.csv`, `phase_status.json`, `stage_errors.json` | Technical execution and scientific approval states | Control |
| `phase02_manifest.json`, `phase02_manifest.sha256`, `SHA256SUMS.sha256` | Manifest and internal control checksums | Control |
| `NEXT_PHASE_INPUTS.md` | Run-specific Phase03 handoff | Control |
| `review_templates/README.md` and seven blank CSV templates | Pair, duplicate, lineage, annotation, adjudication, rights and approval imports | Control |
| `curator/review_queue.csv`, `curator/sealed_labels.parquet`, `curator/certification_units_private.parquet`, `curator/imported_review_records.json` | Private review queue, held-out ground truth and review records | Private |
| `upstream_controls/` | Verified blueprint, model roster, statistical design/checks, Phase02 contract and topology design when present upstream | Control |
| `phase01_verification.json` | Exact successful Phase01 handoff verification | Control |
| `CrackSAFE_CP_v3.3_phase02_control_<run_id>.zip` and `.zip.sha256` | Canonical small handoff pair | Outside itself |
| `CrackSAFE_CP_v3.3_phase02_PRIVATE_audit_<run_id>.zip` and `.zip.sha256` | Optional separate bundle of private audit artifacts | Private; controlled by `export_audit_zip` |
| `bundle_verification.json`, `SEALED.json` | Post-export verification and immutable-run seal | Outside control ZIP |
| `audit_cache.sqlite` and SQLite side files; `verified_phase01/` | Local decode cache and verified upstream extraction | Not included in handoff ZIP |

The catalog and manifest intentionally exclude circular self-hashes and outer ZIP hashes. The control ZIP sidecar provides its outer hash. Unbundled private artifacts still have provenance hashes in the manifest; a development notebook must not require their labels merely to verify its small controls.

## 8. Recovery and resume

| Problem | Next action |
|---|---|
| No exact Phase01 ZIP or sidecar | Attach the pinned saved output or unchanged private pair |
| Multiple matching control ZIPs | Remove duplicate mounts or set the exact `phase01_bundle` path |
| Raw root missing/ambiguous | Set `raw_root` to the actual extracted dataset root |
| Same source renamed | Set `source_directory_overrides`, e.g. `{'DeepCrack': 'actual_folder_name'}`; contents must still hash identically |
| Missing, extra or changed files | Inspect discrepancy records; restore the verified input or produce a reviewed new Phase01 handoff |
| Decode, ignore-value, EXIF or pairing problems | Review/quarantine; do not force a positive/negative label |
| Near-index caps reached | Inspect the affected groups; review stronger provenance or rerun defensible higher caps with sufficient resources |
| Session/disk budget reached | Retain the unsealed run/cache, restore resources and resume compatible configuration |
| Sealed-run resume attempted | Start a new run; sealed output is immutable |
| Scientific count or approval block | Complete evidence/acquire independent data or seek a documented pre-outcome amendment |

For an unsealed interruption, set `resume_run_dir` to that existing writable run directory and rerun from the top. Code, semantic configuration and review-evidence fingerprints must match. Raw bytes are checked again; cached decoding is reused only for matching image/mask/code keys. A changed mode, seed, data or review configuration requires a new run. Session budget and output location can change without changing scientific configuration.

If a Kaggle session is lost, its local cache may be lost too. To resume, restore the complete unsealed run, including its SQLite database and available side files, into the configured writable output tree from a saved private checkpoint. A read-only mounted folder cannot be used directly as `resume_run_dir`. Do not restore a sealed run as an editable checkpoint.

## 9. Exactly what Phase03 needs

1. The original pinned Phase01 ZIP and matching sidecar, retaining its model roster, blueprint and exact statistical design.
2. The new Phase02 **control ZIP and sidecar** from a saved Phase02 output version.
3. The same raw extracted dataset, resolved with `data_shard_index.json` and approved training/development manifests. No new raw-data upload or generated image shard is required.
4. FINAL data partitions with resolved G02/G03/S2/S6, plus Phase03's own S5, model code/weights permissions and technical checks before training.

Training/development receives only approved `train`, `development_model`, `development_probability`, `development_policy` and the linked hard-negative development subset. The shared code preserves the Phase01 statistical helpers and three-seed protocol. Later phases own full structural metrics, model evaluation and certification.

Do not attach the private audit ZIP, sealed labels, full annotation records or curator registries to a model-development notebook. The raw dataset owner can still inspect source annotations: the provided loader and manifests impose an operational access contract, not a cryptographic isolation system. Unlabeled pools remain separate and require their approved downstream protocol.

## 10. Small recommended GitHub list

For `Notebook 2/`, commit later:

- The delivered Phase02 `.ipynb`.
- This guide and the validation report.
- Runtime-exported `phase02_core.py` and `workflow_source.json`.
- A sanitized `metric_primitives_test_report.json` and a concise non-sensitive gate/capacity summary, if useful.

Keep raw data, masks, complete sample/duplicate registries, reviewer identities/evidence, private audit ZIPs, held-out labels and private controls out of the public repository. No GitHub changes were made.

Official navigation references: [Kaggle Notebooks documentation](https://www.kaggle.com/docs/notebooks) and [Kaggle Datasets documentation](https://www.kaggle.com/docs/datasets). The signed-in Kaggle interface and your private mounts were not accessed during notebook generation.
