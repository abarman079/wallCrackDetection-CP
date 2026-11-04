# CrackSAFE-CP Phase03 — Kaggle guide and Phase04 handoff

Version 1.0.0 · Blueprint 3.3 · generated 2026-10-18.

## What this notebook does now

Import `CrackSAFE_CP_Phase03_Legacy_Modern_Baselines.ipynb` into Kaggle and run all cells with the default `RUN_MODE="SMOKE"`, `JOB="audit"`, Internet **Off**. The complete implementation is embedded: `phase03_core.py` is also supplied for inspection and version control, but is not a fourth required Kaggle input. The last executable cell creates, verifies and links one ALL_OUTPUTS ZIP and its SHA256 sidecar.

The expected scientific result today is **BLOCKED**. The pinned Phase02 public status reports: execution COMPLETED, partition PROVISIONAL, 121,794 observed files, 88,806 decoded images, one unresolved certification unit, zero eligible units, 44,616 pending quarantine rows, empty approved train/development manifests, no human approvals and `phase03_training_authorized=false`. These counts describe that audit, not independent examples or usable image/mask pairs. Integrity of private control bytes is not established by their public reports.

SMOKE performs two optimizer steps with a tiny explicitly synthetic adapter, checks primitives and checkpoint handling, and exercises the plotting functions. It does not fit a crack model, generate real development scores, rank engines, fit a real temperature or authorize Phase04. A blocked FULL run also finishes diagnostics and exports. Do not interpret `execution_status=COMPLETED` as scientific approval.

## Immutable source and upstream identities

Project source: [abarman079/wallCrackDetection-CP at dc52faf2929c9358ce36937c4a5131976c4fe8de](https://github.com/abarman079/wallCrackDetection-CP/tree/dc52faf2929c9358ce36937c4a5131976c4fe8de). The Phase03 implementation is newly generated and has no invented Git commit; that commit pins the **upstream contract** only.

| Logical artifact | Exact identity |
|---|---|
| Blueprint v3.3 | SHA256 `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e` |
| Phase01 run | `20261015T111557980168Z_d3a9b41a` |
| Phase01 ZIP | `CrackSAFE_CP_v3.3_phase01_control_20261015T111557980168Z_d3a9b41a.zip` |
| Phase01 outer SHA256 | `ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca` |
| Phase02 run | `20261018T050513552430Z_afc0e8ab` |
| Phase02 ZIP | `CrackSAFE_CP_v3.3_phase02_control_20261018T050513552430Z_afc0e8ab.zip` |
| Phase02 outer SHA256 | `9d87e629fa12d142bbb473384a7b932536edf59e33fd65c7e797c730349a7c99` |

The notebook verifies the outer checksum and canonical sidecar, safe member paths, CRC, schema/run/blueprint identity, manifest sidecar, registered payload sizes/hashes, `SHA256SUMS.sha256`, exact blueprint bytes, combined source/workflow digest, and consistency of the nested shared package. It imports upstream code only after these checks. Integrity streaming of held-out payload bytes is distinct from parsing labels; downstream sealed-role CSVs are never parsed.

## The three logical Kaggle inputs

1. **Existing extracted raw data:** private `abarman79/wall-crack-cp-datasets`. Reuse it; do not create new raw uploads. Former root `/kaggle/input/datasets/abarman79/wall-crack-cp-datasets/`. Recursive discovery finds the five folders below, or set `inputs_override.raw_root` to an observed mount.
2. **Exact Phase01 control plus sidecar**, or the byte-identical original embedded at `recovered_phase01_input/CrackSAFE_CP_v3.3_phase01_control_20261015T111557980168Z_d3a9b41a.zip` inside verified Phase02. The embedded original is independently compared with the pinned Phase01 digest; its provenance is recorded.
3. **Exact Phase02 control plus `.zip.sha256` sidecar.** Extracted public reports alone do not qualify.

| Collection directory | Previously observed filesystem-entry count |
|---|---:|
| `CRACK500 CrackTree200 GAPS384` | 18,887 |
| `CrackForest dataset(CFD)` | 547 |
| `DeepCrack` | 1,075 |
| `SDNET2018` | 56,092 |
| `crack segmentation dataset` | 45,193 |

The fifth folder is an aggregation; it creates no new original source or permission. Counts are not training-pair counts. Although there are three logical dependencies, the embedded Phase01 route needs only two physical dataset attachments.

**Kaggle ZIP extraction:** if uploading `.zip` causes extraction, attach an unchanged copy named `.zip.bin`. Keep the original canonical `.zip.sha256` whose line names `.zip`, not `.zip.bin`. The raw carrier bytes must have the same pinned hash. The notebook copies verified bytes to a writable temporary ZIP; it never reconstructs archives. A sidecar by itself is insufficient. Duplicate or stale discovered controls fail closed; remove them or use explicit observed `inputs_override.phase01_bundle` / `phase02_bundle` paths. An override selects a location, not a new trusted digest.

## Configuration and job sequence

Edit only the visible `CONFIG` cell. Defaults preserve 448-grid preprocessing, seeds, effective batch16, max100 epochs, warm-up5, patience15, AdamW weight decay.01, and common loss. `micro_batch` can be 2,4 or8, with accumulation to16; a final smaller batch is weighted by its actual image count and disclosed. Image normalization is fixed ImageNet mean/std for every engine, including random initialization. No automatic package installation or network access occurs.

| Setting | Use |
|---|---|
| `RUN_MODE` | `SMOKE` default; `FULL` still requires every real gate |
| `JOB` | `audit`, `train`, `ensemble`, or `select` |
| `ENGINE_ID`, `SEED` | One frozen roster engine and a main seed42/123/2026 |
| `resume_run_dir` | Existing writable **unsealed** interrupted run; otherwise `None` |
| `SESSION_BUDGET_HOURS`, `budget_buffer_minutes` | Explicit session time budget; default9h with20min reserve |
| `device`, `amp` | CUDA required for official model technical approval; AMP only when supported on CUDA |
| `reviewed_training_plan` | `{ "path": observed_private_path, "sha256": actual_reviewed_document_digest }` |
| `reviewed_future_phase02` | Optional similarly pinned, genuinely reviewed acceptance of a future FINAL control |
| `job_inputs` | List of `{ "run_dir": saved_run_path, "manifest_sha256": actual_digest }` |
| `max_prediction_cache_bytes` | Default8GiB; refuses truncation when development cache exceeds it |
| `max_saved_output_bytes` | Default20GiB conservative ceiling; adjust to your actual saved-output allowance |
| `output_root`, `export_root` | Defaults `/kaggle/working/cracksafe_cp/phase03` and `/kaggle/working` |

After genuine FINAL Phase02 and S5 approval:

1. Freeze the exact three-slot roster, per-engine initialization and learning rate **before comparative seed training**. Run offline official technical checks on synthetic 448 tensors. Permission/technical failures may justify only the declared fallback sequence; accuracy cannot.
2. Run `JOB="train"` once per engine/seed: three approved engines × seeds42/123/2026 = nine sequential jobs. Keep every valid seed. Save each completed Kaggle output version and its manifest digest. Optional seeds3407/8675309 require precommitment and remain individual runs; they never expand deployed M=3.
3. Use `JOB="ensemble"` for one engine with its three saved jobs in `job_inputs`, or directly use `JOB="select"` with all nine completed jobs. The latter reconstructs all three ensembles, fits each shared T, evaluates the same policy representatives, and freezes a primary only if qualified.
4. Preserve the verified final ALL_OUTPUTS ZIP and small control pair. Record the actual Kaggle version URL/ID externally. Files merely written to a running session are not durable saved outputs.

`learning_rate=1e-4` is the default single predeclared choice. A reviewed plan can select 3e-4, and can document at most two existing development-model-only LR trials from `[1e-4,3e-4]`. If two were performed, a separate reviewed selection record is required before main seed jobs. This notebook does not automatically run a hyperparameter sweep or allow performance-triggered architecture replacement. No exact MRC recipe is implemented because its coefficients/settings remain unrecovered; `recipe_id` must be `clean_common_loss`.

## Actual evidence contract — no generated signatures

These are **required fields**, not completed approval records. The notebook does not emit fake APPROVE documents. Keep the completed documents and supporting evidence private.

Every reviewed document is provided by path and SHA256. It must contain `decision=APPROVE`, a real `reviewer`, `signed_at`, substantive `rationale`, and `evidence={relative_path, sha256}` pointing to an existing document within the review directory. These are content-bound human attestations; the code checks presence and hashes, not cryptographic reviewer identity.

A future Phase02 acceptance additionally contains `blueprint_sha256`, `replaces_sha256` equal to the original Phase02 digest above, `run_id`, and `phase02_sha256` for the newly reviewed FINAL bundle. This does not waive any original Phase01 pin or Phase02 G02/G03/S2/S6 gate. The original current bundle remains immutable.

The reviewed S5 training plan requires:

| Field | Exact meaning |
|---|---|
| `gate_id` | `S5` |
| `phase02_sha256`, `phase03_code_sha256` | Actual approved bundle digest and SHA256 of the delivered core source, not notebook JSON |
| `role_hashes` | Exact five role CSV SHA256 values, keyed by `train`, `development_model`, `development_probability`, `development_policy`, `hard_negative_development` |
| `seeds` | `[42,123,2026]` |
| `preprocess`, `filter` | Exact objects exported in `configs/preprocessing.json` and `configs/operational_filter.json` |
| `recipe_id` | `clean_common_loss` |
| `before_comparative_training` | Actual pre-result commitment, recorded as `true` only when true |
| `approved_data_scope` | `ALL_FINAL_TRAIN_DEVELOPMENT` |
| `approved_original_sources` | Explicit permitted original source IDs, not collection names |
| `unit_original_source_ids` | Non-label mapping `{certification_unit_id: [original_source_id, ...]}` for every allowed learning unit; curator prepares/reviews this projection against the exact Phase02 control before training |
| `slots` | Ordered A/B/C objects with `slot` and `engine_id`; A must be `unetpp_effb3`; all IDs distinct |
| `engines` | Engine ID → the specification below |
| `optional_individual_seeds` | Optional precommitted subset of `[3407,8675309]` |
| `redistribution_approved_sample_ids` | Optional exact development sample IDs with genuine dissemination review; absent means no example-image export |

The non-label source projection avoids opening Phase02's certification-unit table, which contains representative labels. Unit-to-role assignments come from the approved sampling plan; the pinned Phase02 group and unit IDs share the same hash suffix. Phase03 checks that exact source rule before deriving the group barrier. Original-source permissions and external-source exclusion are checked against the reviewed non-label projection. A changed identity convention requires review; no fallback reads held-out labels.

Each engine specification requires:

- `code_permission="APPROVED"`, `source_rights="APPROVED"`; `license_path` plus `license_sha256` for actual source-license evidence.
- `packages`: exact installed versions. Pin torch/torchvision and, for SMP engines, segmentation-models-pytorch/timm; for SegFormer, transformers. Include every relevant upstream compiled dependency for SCSegamba/DMSRCrack. No placeholder version values are accepted.
- `initialization="RANDOM"` or `"GENERIC_PRETRAINED"`. Random is explicitly recorded. Generic weights additionally need `weights_permission="APPROVED"`, `exposure_status="GENERIC_NO_CRACK_TRAINING"`, actual `weights_path`, `weights_sha256`, and `weights_target` (`encoder` for compatible SMP encoder-only states; otherwise a strict complete base-model state dict). The adapter never silently ignores missing/unexpected keys. Crack-trained public weights are forbidden for clean comparators.
- `micro_batch` (2/4/8, default2) and `amp` (defaulttrue) are frozen per engine; train CONFIG must match them across all its seeds.
- `learning_rate`, `learning_rate_trials`: one or two declared values from1e-4/3e-4. Two trials require `lr_selection_review` with actual development_model role and chosen rate, plus the common reviewed-document fields.
- For official source-tree engines: `source_root`, actual40-hex `source_commit`, and `source_files=[{path,sha256},...]` covering **every Python source file** in that tree. Offline provenance must bind those files to the official commit; version and file hashes are rechecked before import.

A replaced slot also requires `replacement_reason` = `TECHNICAL_FAILURE` or `PERMISSION_FAILURE` and `failure_review={path,sha256}`. That actual reviewed document must name the failed primary `engine_id`, record `accuracy_used=false`, and reference real failure/permission evidence. First fallback is SegFormer-B0; second is U-Net++/ConvNeXt-Tiny. Missing failure evidence blocks substitution.

## Engine implementations and current limitations

| Engine | Actual adapter | Current validation claim |
|---|---|---|
| U-Net++/EfficientNet-B3 | Official SMP `UnetPlusPlus(encoder_name="efficientnet-b3", encoder_weights=None, classes=1)` | Implemented; package/CUDA forward-backward not executed in Work |
| SCSegamba | Official source `models.build_model`; binary decoder logits; common loss replaces paper loss recipe | Implemented conditional wrapper; selective-scan/mmcv/CUDA build NOT_RUN |
| DMSRCrack | Official `DMSRCrack(in_channels=3,num_classes=2)`; first returned refined segmentation logit; boundary probability excluded from common loss | Implemented conditional wrapper; DeformConv/CUDA and permission NOT_RUN; no license inferred from public availability |
| SegFormer-B0 | Official transformers B0 widths/depths, one binary head; bilinear logit upsample to448 | Implemented random B0 or explicitly approved strict local initialization; official runtime NOT_RUN |
| U-Net++/ConvNeXt-Tiny | SMP `tu-convnext_tiny`; actual encoder/decoder compatibility required | Conditional; unsupported encoders or 448 shapes produce BUILD_BLOCKED |

Official references: [SMP](https://github.com/qubvel-org/segmentation_models.pytorch), [SCSegamba](https://github.com/Karl1109/SCSegamba), [DMSRCrack](https://github.com/habeeb96/DMSRCrack), [transformers SegFormer](https://huggingface.co/docs/transformers/model_doc/segformer). These are implementation references, not proof of rights, installed compatibility, pretrained exposure clearance or reproduced paper accuracy. Work did not build heavy Mamba/CUDA dependencies or train any official engine.

Kaggle needs numpy, pandas, Pillow, scipy, scikit-image, matplotlib, pyarrow and PyTorch for the basic smoke path; IPython supplies FileLinks. Optional architecture dependencies must be staged offline in a compatible environment. Missing dependencies produce explicit errors/status, never automatic internet installation. No Work CPU package lock is presented as a validated Kaggle CUDA lock.

## Data, metrics and temperature

Only FINAL approved train and the three distinct development roles plus linked hard-negative development are allowed. `development.csv` is the compatibility union of the **three development manifests**, as specified by the blueprint; it is not extra data and does not include training. Hard-negative development is an alias subset of development-policy. All required roles must be nonempty. Unknown annotations, unauthorized zero masks, source rights, role mismatch, sample/group/unit overlap, mismatched hashes, held-out IDs, or unapproved source exposure block real loading.

The verified Phase02 module supplies native mask/image adapters, deterministic aspect-preserving RGB448 letterboxing, bilinear image and nearest-mask resize, valid padding, 8-connectivity, Zhang skeletonization and clDice. Binary/ignore semantics are validated; CFD MAT masks use the existing explicit adapter. GT cracks are never pruned by prediction-component rules.

Loss is an equal per-image mean of 0.5 valid-pixel BCEWithLogits +0.5 soft Dice (epsilon1e-6). Padding contributes neither loss nor metrics. Train augmentation is H/V flips,90-degree rotations and mild±10% brightness/contrast only. Curves disclose augmented training-image Dice separately from development representative-unit Dice.

For each complete engine, one shared positive T is fitted on development_probability by minimizing **mean image-level NLL of the three-member mean probability**. This is not mean member BCE. Optimization is bounded in log T to0.05–20, deterministic bounded SciPy scalar minimization, max80 evaluations. Failures/worse-than-unscaled optimization use T=1 with a recorded reason; missing data never yields a fabricated fit. Reliability uses15 equal bins, image-balanced ECE and separately reported valid-pixel counts. No historical T is transplanted.

Operational predictions use raw probability≥.55,8-connected component area≥20, mean probability≥.55 and skeleton count≥5. The mean-probability condition is redundant after raw thresholding and is explicitly identified as such. No closing, gap filling, dilation or GT pruning is performed.

All development evaluation uses the frozen representative per independent unit. Per-seed and ensemble raw/operational Dice, IoU and clDice are reported; positive metrics use positive units only. Hard-negative FP denominator is confirmed representative hard negatives. Zero/unknown denominators are NOT_EVALUABLE. Descriptive unit bootstrap95% intervals are not formal certification intervals. Full branch graph/LWBR/structural analysis remains Phase04.

The selection gate is operational positive IoU≥.56 and hard-negative false-valid-component rate≤.35. Passing engines rank by clDice; within1e-6 use lower FP, then lower synchronized median latency, then lexical engine ID. All three approved engines must have complete aligned records; no partial roster is ranked. None passing produces COMPLETE_NEGATIVE, not a fabricated primary.

## Checkpointing, resource limits and persistence

Checkpoints retain model, optimizer, scheduler, scaler, epoch, best score/patience/history, Python/NumPy/Torch/CUDA RNG, sampler generator/order/cursor, input/role/plan/code/config/environment identity and pending-accumulation state. Atomic temporary-write/checksum/rename plus sidecar protects against torn files. Durable checkpoints occur every100 optimizer steps, at every epoch and at a pre-buffer budget stop. A hard kill replays work after the most recent durable checkpoint; it does not claim to recover unsaved gradients. Checkpoints are taken only at completed optimizer boundaries.

Resume only an unsealed interrupted run with identical science/config/code/input/environment identities. The session duration/buffer and resume path are operational exceptions; scientific parameters are not. After a budget stop, save/export the entire interrupted run, copy it to writable storage in the next session and set `resume_run_dir`. Keep the run directory structure. Completed sealed runs cannot resume or be edited. Saved job assembly requires the same input/plan/code/environment identities and all main seeds, rejecting partial jobs and conflicting same-seed checkpoints.

Actual official checks require CUDA batch2 forward/backward, finite logits/gradients and reload equality. Measured parameter count, memory, training throughput and synchronized batch1 M3 inference are recorded only when run. Timing uses5 warm-ups and20 synchronized repetitions; it covers model forward + temperature + probability mean, excluding disk, preprocessing and CPU component filtering. Work CPU synthetic timing is not substituted for these fields.

Development caches hold float32 member logits and approved development truth/valid masks in per-image compressed shards. They are private, bounded by an explicit disk budget, and reused for the temperature optimizer instead of repeated GPU forwards. All-selected-engine inference is sequential; no distributed job is implied. An out-of-memory or deterministic-kernel failure remains a technical failure with logged evidence.

## Figures and outputs

All plotting functions are implemented. `figures/figures_manifest.csv` gives status/caption/source/role/code/config traceability. Currently the only nonsynthetic generated figure is the **methodology workflow**; real result figures are NOT_GENERATED_BLOCKED. The seven fixture PNGs live in `synthetic_test_figures/` and carry **SYNTHETIC — FUNCTIONAL TEST ONLY**. They must not be used as scientific result figures.

Future real figures cover same-unit engine comparison with CIs/n; per-seed loss and Dice curves; probability reliability/ECE/counts; HN tradeoff with both gate lines; hardware-specific measured efficiency; and aligned RGB/GT/probability/raw/operational examples. Example IDs are the first three lexical policy IDs before inspecting predictions. The optional failures figure uses the fixed IoU/false-valid rule within that fixed set, not visual cherry-picking. Missing redistribution permission prevents example export; the small control omits example images even when generated privately.

Every completed run produces configs, registry/table schemas, truthful empty-or-real metric tables, pending-or-real selection/ensemble JSON, prediction_index.parquet, environment, access log (unique path/role/action with read counts), gates, stage errors, manifest with external sidecar, catalog, SHA256SUMS, small private control ZIP, handoff guide and a final archive. Checkpoints and prediction caches stay outside the small control.

## Last-cell archive and storage fallback

The final executable cell normally writes:

- `/kaggle/working/CrackSAFE_CP_Phase03_ALL_OUTPUTS_<run_id>.zip`
- its exact `.zip.sha256` sidecar.

Interrupted snapshots append `_checkpoint_<manifest_hash8>`; this avoids overwriting earlier snapshots. Index CSV/JSON inside the ZIP lists saved payload paths/sizes/hashes. Index files exclude their own recursive hashes, but the exporter checks their bytes too and the outer sidecar covers the complete archive. It streams large files, uses ZIP_STORED for checkpoint/compressed formats, verifies all member hashes and CRC, and prints full paths, counts, bytes, checksum and FileLinks. Rerunning against identical inputs verifies the existing ZIP; changed payloads are rejected.

Disk is measured via `shutil.disk_usage`; saved-output usage includes export and run files without double counting. The configured ceiling is conservative and must reflect your actual account/session allowance; the code cannot query Kaggle's account quota. The quota guard allows space for the original run **and** its export. Raw inputs, private upstream controls/extractions, sealed/curator labels, secrets, temp/cache files, other runs and the ZIP itself are excluded.

If the full archive cannot fit, `FULL_ZIP_BLOCKED_STORAGE_<snapshot>.json` records measured bytes, budget and every omitted checkpoint/prediction part with exact path, size and SHA. A `COMPACT_OUTPUTS` archive contains that report and compact outputs if it fits. It is never labeled ALL_OUTPUTS. Fetch every separately pinned part from the same saved Kaggle version; the diagnostics explain how. If even compact export cannot fit, the report and small control remain linked. No existing run file is deleted to force export.

## Phase04 handoff

**Current authorization: NO.** First obtain a genuinely qualified frozen three-member primary engine, or retain the negative feasibility report. Later, Phase04 needs original Phase01/02 controls, the verified Phase03 small control, selected three checkpoints, exact inference code and dependencies, frozen T/preprocessing/filter, and approved development manifests/prediction shards. Reuse the existing raw mount. Keep held-out labels and source/target unlabeled pools unopened; those have later-phase contracts.

The convenience ALL_OUTPUTS archive is not a replacement control schema. Extract and attach the exact small control plus its sidecar; use `.zip.bin` carriers when needed. No Phase04–08 notebook is generated here, and no test/calibration evaluation function is exposed.
