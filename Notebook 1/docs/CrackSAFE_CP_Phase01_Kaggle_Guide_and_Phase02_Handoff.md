# CrackSAFE-CP Phase 01 — execution guide and Phase 02 handoff

Notebook: **`CrackSAFE_CP_Phase01_Legacy_Design_Literature_Locks.ipynb`**  
Specification: **v3.3**, SHA-256 `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e`  
Prepared: **2026-10-15**  
Scope: **Notebook 01 only. No full-data model training, final calibration or final-test evaluation.**

## What is implemented

The notebook contains 47 Markdown/Python cells, including readable reusable helpers and staged execution. It embeds the exact supplied blueprint and exports it alongside the shared source. Ordinary execution uses CPU and Python's standard library; SciPy accelerates the exact-binomial calculations if available. No package installation, model-weight download or entire raw archive extraction is automatic.

It discovers actual archives; inspects ZIP safety and naming metadata; fingerprints inputs; records original legacy evidence or its absence; scans applicable historical split identifiers; exports the 22-reference literature register with explicit inherited provenance; implements the exact 26-bound statistical planning procedure; records model permissions and technical blockers; plans resources; chooses documented field Route A or default Route B; exports decision gates; and seals an independently verified control ZIP.

The optional model worker uses random tensors to test forward/backward, one synthetic optimization step, checkpoint save/reload and numerical reload agreement. That is a technical test, not an accuracy result, pretrained reproduction or full training. It has adapters for all five declared candidates, but unavailable dependencies, incompatible source code or missing permissions result in BLOCKED/NOT_RUN. Nothing automatically becomes training-approved.

## Run it in Kaggle

1. Download the actual `.ipynb` file supplied with this guide. Keep its filename.
2. Sign into your Kaggle account and open a new Python notebook. Use **File → Import Notebook**, or the notebook import/upload option shown in your editor, and select the downloaded file. Keep the notebook private if its outputs contain private research metadata.
3. In **Input → Add Input**, locate your dataset **`abarman79/wall-crack-cp-datasets`** under your datasets and attach the intended version. The notebook expects the usual `/kaggle/input/wall-crack-cp-datasets/` mount but discovers the actual directory and filenames.
4. Choose **Accelerator: None** for the ordinary inventory. Leave internet disabled initially. No GPU is needed for archive metadata, historical reports or the mathematics.
5. Read and edit the first configuration code cell. Leave unknown evidence fields empty. In particular, do not invent legacy paths, permissions, field reviewers or a Git commit.
6. Run a rehearsal with `'run_mode': 'SMOKE'`. It inventories archive central directories but does not hash complete raw ZIP bytes. It must not be treated as a completed research run.
7. Read the final summary and the reports. Correct missing dataset mounts or clearly wrong settings. Missing legacy evidence is expected and does not need to be “fixed” with invented files.
8. Set `'run_mode': 'FULL'`, keep `'resume_run_dir': None`, and **Run All**. FULL streams every relevant raw ZIP to calculate a complete SHA-256 fingerprint; allow time proportional to archive size. It still does not extract or evaluate image data.
9. Check that `stage_errors.json` is empty, the required reports exist, and `bundle_verification.json` says `PASS`. The final summary prints the exact run folder, ZIP, sidecar, run mode and `phase02_audit_ready` flag.
10. Choose **Save Version → Save & Run All**, or the equivalent complete-run save option in your current editor, and wait for it to finish. A saved background run creates its own timestamped run directory. Inspect the **saved version's Output**, not an earlier interactive run's path.
11. Find the canonical ZIP and its `.sha256` sidecar under the saved output folder. Preserve both. Confirm they remain available from the saved notebook version before closing the session.
12. Record the actual Kaggle notebook URL/version and raw dataset version in your research log. Return with the actual FULL-run control ZIP and sidecar when requesting Notebook 02.

Kaggle's official documentation describes saving notebook versions and attaching saved notebook outputs through Add Input. Current UI labels, accelerator availability and quotas can vary; inspect your own account. See [official notebook documentation](https://www.kaggle.com/docs/notebooks) and [efficient GPU guidance](https://www.kaggle.com/docs/efficient-gpu-usage). No fixed weekly GPU quota or session length is assumed by this notebook.

### Configuration choices

| Setting | Recommended initial value | Meaning |
|---|---|---|
| `run_mode` | `SMOKE`, then `FULL` | Diagnostic rehearsal versus complete input fingerprint inventory; neither runs certification |
| `input_root` | `/kaggle/input` | Read-only mounted inputs |
| `output_root` | `/kaggle/working/cracksafe_cp` | Generated control artifacts |
| `raw_dataset_hint` | `wall-crack-cp-datasets` | Directory-name discovery hint |
| `raw_roots` | `[]` | Optional exact directory list if discovery is ambiguous; use actual mounted paths |
| `network_checks` | `False` | Optional bounded HTTP checks of official references/repository metadata; no large datasets downloaded |
| `run_model_smoke` | `False` | Separate technical verification stage; remains required before a candidate is training-ready |
| `model_smoke_ids` | Declared five candidates | Narrow to the models you are technically checking in that run |
| `smoke_device` | `cpu` | Set `cuda` only after enabling a Kaggle GPU |
| `smoke_size` | `448` | Canonical shape; a reduced-size diagnostic cannot satisfy the 448-shape gate |
| `legacy_paths` | `[]` | Optional actual original legacy records; checkpoints are only fingerprinted |
| `legacy_split_manifests` | `[]` | Explicit applicable historical train/validation CSV paths |
| `repository_paths` / `model_pins` | `{}` | Reviewed local official source directories and matching exact commit SHAs |
| `model_permission_evidence` | `{}` | Actual permission/review document paths for a model; not a fabricated approval switch |
| `field_evidence_path` | `None` | Actual documented field package, otherwise Route B |
| `session_limit_hours` | `None` until checked | Record the live limit shown in your Kaggle account; reserve at least 30 minutes for export |
| `resume_run_dir` | `None` | Use an actual **unsealed** interrupted run only, with identical configuration and code |

Keep the initial path discovery simple. The notebook tries the dataset directory hint, then directories containing expected archive names. If all names and mount names differ, inspect your Input panel and provide the actual `raw_roots`. It will not silently treat unrelated ZIP files from other attached datasets as your raw collection.

### Optional model verification

Do the CPU inventory first. Then prepare a separate saved run with `run_model_smoke=True`, the selected model IDs, the intended device and 448 input size. A GPU is optional for trying a supported CPU model but is needed to establish the intended CUDA execution behavior and memory use. Turning on internet does not install packages by itself.

For the U-Net++ adapters, a reviewed `segmentation-models-pytorch` installation and its dependencies must be present. For SegFormer-B0, the worker uses an installed `transformers` package and a random B0 configuration. Installed package versions and Python-source fingerprints are recorded; an unavailable Git commit stays null or is explicitly labeled remote-only. The source library is an implementation choice, not a claim that the original MRC training recipe was recovered.

For SCSegamba and DMSRCrack, attach a reviewed source snapshot retaining a clean Git identity; configure its actual directory and matching 40-character commit SHA. Keep actual license evidence with it. A source snapshot whose identity cannot be verified remains blocked. DMSRCrack also needs actual permission evidence if no applicable license can be established. The notebook does not grant permission from a public GitHub listing.

SCSegamba's upstream environment lists an older Torch/CUDA stack and custom dependencies. Do not blindly downgrade the current Kaggle environment. The adapter invokes the upstream builder without running its training entry point and records import/operator/output failures. U-Net++/ConvNeXt encoder compatibility also must actually execute; the notebook does not silently change architectures to make a smoke test pass.

The worker prevents weight downloads. A random-initialization technical PASS leaves pretrained-weight rights, recipe equivalence, source review, resource fit and S5 approval unresolved. It records the raw and operational output shapes. SegFormer logits use explicit bilinear upsampling; DMSRCrack's first tuple output is treated as segmentation. Any unrecognized output contract is a blocker rather than a guess. No third-party pickle checkpoint is loaded.

Official implementation/documentation entry points: [SCSegamba](https://github.com/Karl1109/SCSegamba), [DMSRCrack](https://github.com/habeeb96/DMSRCrack), [SMP models](https://smp.readthedocs.io/en/latest/models.html), [SMP timm encoders](https://smp.readthedocs.io/en/latest/encoders_timm.html), and [Transformers](https://github.com/huggingface/transformers). Runtime checks must establish the exact version actually used.

### Optional legacy and field evidence

Recognized legacy CSV image-reference columns are `image_ref`, `image_path`, `filename`, `file_name`, `image` or `path`. The role comes from `role`, `split`, or a clearly named historical train/validation file. Optional `parent_id`, `original_id`, `parent_image_id`, `source_id` and `source` strengthen naming comparisons. Unknown or mixed final-test roles are rejected for this scan. Label values are not evaluated. Generic ambiguous split files remain candidates until applicability is established.

Field Route A requires an actual JSON file with `access_secured: true`, `permission_granted: true`, nonempty `responsible_reviewers` and `devices`, an ISO `capture_plan_date`, and actual `access_document`, `permission_document`, `capture_plan_document` paths under the input root. Those documents must exist. Their presence is recorded and hashed; it does not authenticate them or sign S6. Without the whole package, use Route B: external datasets, hard negatives and controlled corruptions.

### Restart and recovery

Each run has a unique path:

`/kaggle/working/cracksafe_cp/phase01/run_<UTC>_<config_hash8>/`

For an interrupted **unsealed** run still present in working storage, set `resume_run_dir` to that exact path and leave all other settings and source unchanged. FULL recomputes actual input fingerprints. A stage reuses cached results only when input/config/code/environment keys and output hashes match. Changed or damaged evidence causes recomputation. SMOKE does not reuse raw-data stages based on size/mtime guesses. Optional live network checks disable this cache reuse.

Once `SEALED.json` exists, the run is immutable. Start a new run to change configuration, enable model checks or add evidence. Do not edit artifacts inside an old ZIP. If working files were lost, recover a saved version/output dataset or rerun; a directory printed during an unsaved session is not proof of persistence. A saved output mounted under `/kaggle/input` remains read-only; do not point the writer there.

## Read the final status correctly

| Result | Meaning | Next action |
|---|---|---|
| `bundle_verification.json: PASS` | The small control bundle and its internal/outer hashes agree | Preserve it; this is not a scientific certificate |
| Global `phase_status.json: BLOCKED` | Required human approvals and/or later model evidence are still unresolved | Read the named blockers; do not convert them to PASS manually |
| `phase02_audit_ready: true` | A FULL run has required controls, exact math tests, identified hashed raw archives and no hidden stage failures | Phase 02 may perform source/data auditing under the recorded restrictions |
| `phase02_audit_ready: false` | SMOKE, missing/unreadable inputs, missing reports, or a stage failure prevents that readiness claim | Fix the specific dependency and create a new FULL run |
| `MISSING_INPUT` for legacy files | The original evidence was not attached/found | Retain historical-only reporting; no artificial reconstruction |
| Archive warning | Metadata suggests unsafe paths, ambiguous duplicate names, encryption, unsupported compression or suspicious sizes | Quarantine before any future extraction; Phase 02 investigates |
| Model `NOT_RUN` / `BLOCKED` | Execution was not attempted or could not satisfy prerequisites | Resolve technical/legal evidence before training; use only declared fallbacks |
| `PENDING_APPROVAL` | A human decision/signature is required | Obtain a real scoped decision later; report generation does not approve it |

A missing expected archive **name** can mean a rename, so it requires reconciliation with actual source coverage. It does not by itself prove that the source is absent. Conversely, seeing an archive does not establish valid labels, unique pairs, independent acquisitions or source permission.

Global BLOCKED and Phase 02 audit readiness can coexist. The notebook deliberately does not automatically approve S1–S7. Complete model reproduction and those decisions are prerequisites for the activities that depend on them, not a reason to fabricate evidence or prevent harmless source auditing.

## Statistical locks to preserve

- Primary family: `lambda00`–`lambda12`, two risks each, 26 one-sided bounds. `delta_cell=0.05/26`. `lambda13` is an explicit review-all branch.
- Targets: structural miss 0.10 and false structure 0.05. Bounds use **accepted observations within the relevant class**, not all images or reviewed losses set to zero.
- Available independent calibration-unit hard floor: 120 positive and 122 confirmed negative; preferred planning target 300 per class. These counts are unknown until Phase 02 audits independence.
- With zero failures, the exact **accepted-unit** minima are 60 positive and 122 negative. The120-positive available-data floor remains part of the project design. 300 available per class does not guarantee useful coverage.
- At zero accepted observations, displayed risk/UCB are null with `NOT_CERTIFIABLE`; the conservative computational bound is1. Review-all has zero coverage and undefined conditional risks.
- Choose maximum empirical coverage among policies whose **both** bounds pass; tie by lowest ID. Conditional risk is not assumed monotone as thresholds tighten.
- Fix model/preprocessing/temperature/scores/CDFs/acceptance rules/endpoints/population/N before calibration. No repeated ordinary fixed-sample retries after seeing failure. G07 independent mathematics/code sign-off is still required before Phase 06.
- The deployment topology score uses predictions only. Ground-truth structural losses remain separate. All-empty predictions are flagged; they do not prove certainty.
- ESS and domain-classifier AUC are diagnostics. They do not establish a weighted shift guarantee. External testing is empirical unless stronger theorem assumptions are independently justified.

The full exact definitions and proof are embedded unchanged in the exported blueprint and the relevant design documents.

## Complete Phase 01 output inventory

All paths below are relative to the actual printed run folder. Conditional folders appear only when their evidence/checks are available. A report may validly contain a missing-input status; a missing mandatory report is a software/evidence failure explicitly listed in `phase_status.json`.

| Output | Role / expected evidence |
|---|---|
| `legacy_manifest.json` | Separate historical facts, found original records and historical/frozen-checkpoint/clean-retraining evidence categories |
| `legacy_hashes.sha256` | Actual original-file hashes, or an explicit comment when no files exist |
| `legacy_baseline_record.md` | Historical 1,356-case and 1,695-case results kept separate; not reproduced |
| `missing_inputs.csv` | Missing evidence, what it blocks and required action |
| `preliminary_lineage_scan.csv` | Train/validation naming/parent candidates; header-only when unavailable |
| `preliminary_lineage_report.md` | Scan scope, applicability/schema errors and Phase 02 audit requirements |
| `literature_matrix.csv` | 22 references, required comparison fields, evidence limits and provenance |
| `novelty_gap.md` | Inherited research questions, closest overlap and defensible gap |
| `verified_references.bib` | Parseable conservative bibliography with per-entry inherited/current status |
| `rcps_decision_D2.md` | Exact finite-family conditional-binomial/LTT-compatible specification and proof |
| `statistical_design.json` | Machine-readable policy grid, targets, budgets, assumptions, sentinel and approval status |
| `sample_size_feasibility.csv` | Hypothetical minimum/coverage/error-count planning calculations |
| `planning_power.csv` | Conditional binomial passing probabilities at fixed hypothetical accepted N; not actual data or joint search power |
| `statistical_self_tests.json` | 20 deterministic mathematical checks; no empirical calibration results |
| `prediction_only_topology_design.md` | Preserved structural, inference-only score and shift contracts for later phases |
| `modern_baseline_repro_check.md` | Model documentation, execution scope, blockers and fallback rules |
| `model_roster.json` | Three candidate slots, declared fallbacks, seeds, slot status and no automatic training authorization |
| `repository_registry.csv` | Official repositories, actual/unknown commits, source hashes, license/weights/dependency/compatibility evidence |
| `model_checks/<model_id>.json` | Each of the five candidates' actual PASS/BLOCKED/NOT_RUN technical result |
| `model_checks/<model_id>_request.json` | Conditional: exact worker input/config for an attempted subprocess |
| `model_checks/<model_id>_process.json` | Conditional: subprocess outcome/stdout/stderr/timeout evidence |
| `model_smoke_worker.py` | Standalone bounded technical worker; no full-data training or third-party checkpoint load |
| `repository_evidence/*_files.json` | Conditional: local reviewed source file fingerprints |
| `repository_evidence/*_licenses.txt` | Conditional: actual installed/source license text retained for review |
| `repository_evidence/*_remote_head.json` | Conditional: current observed remote commit metadata; not proof of installed-source identity |
| `repository_evidence/*_remote_license.json` | Conditional: bounded official license metadata check |
| `resource_plan.csv` | Eight-phase and per-model budgets; provisional training estimates versus measured runtime/smoke values |
| `resource_plan_notes.md` | Memory/storage/session assumptions and checkpoint/recovery strategy |
| `field_data_decision.md` | Documented Route A or default Route B with no invented field claims |
| `field_evidence_inventory.json` | Actual field-document hashes or explicit missing prerequisites; S6 pending |
| `decision_gates.csv` | G01–G10 and model-specific gates with evidence, status, verifier, blockers and actions |
| `supervisor_decisions.md` | S1–S7 proposals/deadlines; no generated approval signatures |
| `archive_inventory.csv` | Discovered ZIP names/paths, SHA status, member/size totals and metadata safety status |
| `archive_members.csv` | Central-directory member metadata, naming hints and warning flags; no decoded pixels |
| `archive_warnings.csv` | Suspicious/duplicate/encrypted/unsupported/bomb-risk metadata and quarantine actions |
| `archive_expectations.csv` | Expected-name matches and missing/renamed hints |
| `archive_overlap_candidates.csv` | Weak cross-archive basename/size/CRC candidates; not full deduplication |
| `source_pattern_inventory.csv` | Filename-derived source/role hints and counts; not verified source identity |
| `dataset_discovery.json` | Actual mounts and discovery method; historical 11,298/11 expectations explicitly unverified |
| `input_fingerprints.json` | Complete content fingerprints in FULL; explicit missing raw hashes in SMOKE |
| `environment_snapshot.json` | Actual Python/packages, CPU/RAM/disk, GPU/driver/CUDA command results and timing |
| `data_access_log.csv` | Allowed metadata, legacy development identifiers and documentation accesses |
| `config.json` | Actual settings and schema version; no invented account/session data |
| `run_identity.json` | Actual run/time and source/config/blueprint identities |
| `blueprint_v3.3.md` | Exact embedded authoritative specification bytes |
| `phase01_core.py` | Readable versioned shared Python implementation |
| `workflow_source.json` | Exact staged execution source and instructions used for implementation hash |
| `cracksafe_core.zip` | Importable shared Python package, including tested exact-bound helpers |
| `schemas.json` | CSV columns/row counts/null rules/primary keys and schema links |
| `phase01_manifest.schema.json` | Machine-readable JSON manifest schema |
| `phase02_contract.json` | Required inputs, Phase 02 schemas, restrictions, blockers and execution sequence |
| `phase_status.json` | Honest global status, readiness scope, missing outputs and model results |
| `stage_errors.json` | Actual caught stage exceptions; should be `[]` in a clean software run |
| `NEXT_PHASE_INPUTS.md` | Runtime-specific attachment table, critical artifact IDs/hashes and exact handoff |
| `artifact_catalog.json` | Logical paths, IDs, sizes, hashes and requirements; no guessed Kaggle slugs |
| `phase01_manifest.json` | Common v3.3 manifest with input/output hashes, gates, environment and scope |
| `phase01_manifest.sha256` | Separate checksum of the final manifest; no self-hash recursion |
| `SHA256SUMS.sha256` | Payload/catalog/manifest checksum list; intentionally excludes itself |
| `CrackSAFE_CP_v3.3_phase01_control_<run_id>.zip` | Canonical small control bundle; includes shared code ZIP, excludes raw data/checkpoints |
| `CrackSAFE_CP_v3.3_phase01_control_<run_id>.zip.sha256` | Separate checksum of final ZIP bytes; kept outside the ZIP |
| `bundle_verification.json` | Verified outer hash, ZIP CRC and all manifest/hash-list entries; stored outside sealed bundle |
| `SEALED.json` | Marks finalized run as immutable and records bundle identity; outside bundle |
| `.stage_cache/<stage>.json` | Runtime-only resume records keyed by actual evidence and output hashes; excluded from control bundle |
| `reference_rechecks.csv` | Per-reference HTTP check/not-run/unavailable status; never confused with scientific review |
| `reference_register_inherited.md` | Exact inherited reference register and blueprint fingerprint |
| `reference_checks/<Rxx>.json` | Conditional bounded HTTP metadata/content fingerprint, not a new full-text scientific review |

No `phase01_bundle.zip` alias is generated; use the canonical filename. Temporary random model checkpoints are removed after their save/reload test and are not trained-model deliverables. The outer ZIP hash lives outside the ZIP; the manifest hashes payload files, while a separate sidecar hashes the manifest. This avoids circular hashes.

## Exact Notebook 02 attachments

Define `RUN` as the actual run folder printed by the saved FULL execution and `BUNDLE` as `CrackSAFE_CP_v3.3_phase01_control_<actual_run_id>.zip`. Do not replace `<actual_run_id>` by a guessed value.

| File or Bundle | Purpose | Generated Kaggle Location | Required for Notebook 02? | How to Attach |
|---|---|---|---|---|
| Canonical `BUNDLE` | All small Phase 01 control files, embedded blueprint and shared source | `RUN/BUNDLE` | Yes | Attach the exact saved Notebook 01 output version; private dataset alternative below |
| `BUNDLE.sha256` | Check the complete ZIP before use | `RUN/BUNDLE.sha256` | Yes | Preserve alongside ZIP in the same attached output/dataset |
| `phase01_manifest.json`, its sidecar, `SHA256SUMS.sha256`, `artifact_catalog.json`, `NEXT_PHASE_INPUTS.md` | Provenance and dependency verification | Inside `BUNDLE`, also individually under `RUN` | Required contents; **no separate attachment** when ZIP is attached | Notebook 02 reads these from the verified bundle |
| Blueprint, configuration, statistical design, roster, field decision, gates, schemas and `cracksafe_core.zip` | Exact scientific and software contracts | Inside `BUNDLE` | Required contents; **no separate attachment** | Keep them intact inside the canonical bundle |
| Raw dataset `abarman79/wall-crack-cp-datasets` | Actual images/masks and original archives | Same existing dataset mount, discovered at runtime | **Yes, attach again** | Add Input → your private dataset; use same actual version and check archive hashes |
| Original legacy/field/permission evidence, if available later | Resolve previously missing claims | Whatever actual evidence mount you attach | Optional for initial audit; required before dependent claims | Attach genuine private evidence; do not manufacture replacements |
| Trained model checkpoint | No role in Phase 02 source/data audit | None required | **No** | Do not wait for model training before auditing data |

### Recommended preservation route

Use **the exact saved Notebook 01 output version** as Notebook 02 input when Kaggle exposes that version in Add Input. This avoids manual file-copy errors and keeps the runtime outputs together. The official documentation supports reusing saved notebook outputs. Verify the ZIP and sidecar are present in the selected saved version.

For a portable fallback, create a **private Kaggle dataset** containing only `BUNDLE` and `BUNDLE.sha256`, save a dataset version and attach that to Notebook 02. Prefer this fallback when the notebook-output picker is unavailable or cannot pin the desired version. Keep a separate record of the source notebook/version. Do not duplicate all raw image archives into this control dataset.

Notebook 02 must still attach the original raw dataset separately. Small Phase 01 reports cannot replace raw images, masks and their source archives.

### Paths Notebook 02 may encounter

Examples only:

- `/kaggle/input/<saved-notebook-output>/cracksafe_cp/phase01/run_<...>/BUNDLE`
- `/kaggle/input/<phase01-control-dataset>/BUNDLE`
- `/kaggle/input/wall-crack-cp-datasets/<actual-archive-name>.zip`

The actual mount slug is not known in advance. Notebook 02 must discover the canonical bundle basename and matching sidecar, reject ambiguous multiple runs, then resolve raw archives against recorded content hashes. It must not assume that an uploaded ZIP name equals its mount-directory name.

### Required checks before Phase 02 work

1. Verify the outer ZIP SHA-256, then safe member paths and internal manifest/checksum entries. Confirm blueprint 3.3, phase 01, schema 1.0 and compatible shared-code version.
2. Require the complete critical design/provenance controls, an empty or resolved relevant `stage_errors.json`, and a FULL-run audit-readiness assessment.
3. Discover and hash the actual attached raw archives. An input hash mismatch is a new dataset version requiring reconciliation, not a reason to ignore the expected hash.
4. Read archive warnings and keep suspicious members quarantined. Phase 02 auditing may investigate warnings; it must not blindly extract them.
5. Read missing legacy evidence, historical exposure limits, field route and all unresolved S1–S7 decisions. Missing model checkpoints or GPU smoke do not prevent initial source/data auditing.
6. Before Phase 02's exit, resolve source rights, parent/group leakage, eligible labels/negative adjudication, actual independent counts and S2's population/unit/fixed-count decision. Human review is still necessary; the notebook does not sign it.
7. Keep original raw archives and sealed Phase 01 controls immutable. A methodological change needs a new version/amendment and invalidation of dependent caches.

### Concise Notebook 02 build specification

Build only `CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb` from the **actual executed** Phase 01 bundle, sidecar, authoritative blueprint and raw data mount. Validate every dependency first. Use the shared-code contract instead of rewriting inconsistent statistical helpers.

Then audit image/mask pairing and decode integrity; exact/decoded/perceptual duplicate candidates; source aggregation overlap; parent/site/session lineage; licenses; positive-mask credibility; confirmed-negative labels and historical exposure. Recover the highest dependence grouping. Choose one label-blind representative per defensible certification unit. Do not count all SDNET crops as independent originals or treat aggregation as another source.

Count actual eligible independent units and evaluate the 120/122 hard floor and preferred 300/300 plan without calibration outcomes. Prepare annotation/adjudication requirements and grouped partitions with an explicit curator/sealed-label access barrier. Do not train segmentation models, run final calibration, tune on final test results, or invent original legacy splits. Export Phase 02 gates, manifests, schemas and a new canonical control bundle.

The run-generated `NEXT_PHASE_INPUTS.md` supplies actual IDs and SHA-256 values. This guide supplies the workflow only; it does not invent hashes for your future Kaggle output.

## Copy-paste next-task prompt

> Build only `CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb` using the attached actual Phase 01 FULL-run control ZIP, matching SHA-256 sidecar and authoritative v3.3 blueprint. First verify the bundle, manifests, shared-code hash, schemas, readiness and unresolved decisions; read `NEXT_PHASE_INPUTS.md`. The raw dataset remains `abarman79/wall-crack-cp-datasets` and must be discovered and hash-matched in Kaggle. Implement the complete Phase 02 integrity, duplicate/lineage, source/permission, label/annotation, independent-unit and grouped-split audit. Preserve sealed final-test access barriers, the 120-positive/122-negative independent calibration floor and all pending approvals. Do not train models or run final calibration. Save the actual notebook early, test it, and deliver it with an execution guide and exact Phase 03 handoff. Report missing evidence honestly.
