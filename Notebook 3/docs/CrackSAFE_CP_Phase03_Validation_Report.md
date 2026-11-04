# CrackSAFE-CP Phase03 — validation report

Generated 2026-10-18 · implementation1.0.0 · Blueprint3.3.

## Outcome

**PASS for the implemented offline synthetic engineering and blocked-run checks. Scientific status remains BLOCKED.** The final27-cell notebook (13 executable cells) ran sequentially in a fresh namespace for both default SMOKE/audit and FULL/train with missing private controls. Both completed exports with no unresolved stage exceptions, no real-data access, no real training, no real metrics, no real probability calibration and no primary ensemble. The missing-input/approval stages correctly reported BLOCKED rather than passing integrity or granting training permission.

This is not validation of trained models or published accuracy. Official CUDA training and any genuine FINAL-control end-to-end run remain NOT_RUN.

## Delivered artifact identities

| File | Bytes | SHA256 |
|---|---:|---|
| `CrackSAFE_CP_Phase03_Legacy_Modern_Baselines.ipynb` | 128,364 | `598c12e2a48403470dacc9a212ab96ef94c1a1c4e0ece0333343140363446de3` |
| `phase03_core.py` | 101,378 | `3b9d1171e4de2f7ea1b2c29d836fbe45a2a6a7dc4584a671f695b7720b3d656f` |
| `CrackSAFE_CP_Phase03_Kaggle_Guide_and_Phase04_Handoff.md` | 24,250 | `afb227bf92d2379008938412a230af81fd4c4369cba7eb45ece826d40f5cc026` |
| `CrackSAFE_CP_Phase03_README.md` | 1,792 | `81bb343c76fedfae96d69a8d48da9b27b35a1d33b1e8fc9bfa044a3c6683be8c` |

This report excludes its own recursive digest. The notebook embeds the exact core source above; its metadata and the executed run manifest match that hash. All executable cells compiled. Notebook JSON validates as nbformat4.5. The opening markdown visibly retains the inspection-support research boundary and later two-risk targets; this final prose-only addition does not change executable cells. The last executable cell calls `export_all_outputs` and displays archive/sidecar FileLinks.

## Actual execution evidence

| Check | Result |
|---|---|
| Sequential SMOKE, fresh Python namespace | PASS; 5.35s in this CPU environment |
| Sequential blocked FULL/train, fresh namespace | PASS; 5.26s; real training remained false |
| Actual Jupyter kernel | NOT RUN SUCCESSFULLY: attempted TCP then IPC startup; environment socket-permission errors terminated the kernels before kernel_info |
| In-process fallback | Used explicitly; not described as a kernel execution |
| In-notebook synthetic assertions | 22 PASS |
| Additional adversarial/storage/resume assertions | 35 PASS |
| Core/embedded-source identity and cell compilation | PASS |
| Official private Phase01/02 bytes | NOT MATERIALIZED OR USED in this Work validation; no genuine outer-integrity PASS claimed |
| Public blueprint bytes | Exact SHA256 matched `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e` |
| Actual official-engine GPU forward/backward/reload | NOT_RUN; no CUDA GPU |
| Real training, real T, real engine selection | NOT_RUN; scientific gates blocked |
| Real certification/test/held-out label loading | NOT_RUN; no corresponding evaluation API |
| Real source example images | NOT GENERATED; no source redistribution approval |

Latest validated SMOKE run: `run_20261018T095256392563Z_4f544b7d`. Latest blocked FULL run: `run_20261018T095302834473Z_77cc3e4c`. These are engineering test-run IDs, not scientific baselines.

The synthetic optimizer test is a single1×1 Conv2d, explicitly excluded from the engine roster. It performs exactly two functional optimizer steps. Additional checkpoint testing compares an uninterrupted AdamW/scheduler update against a resumed update with restored Python/NumPy/Torch RNG and sampler generator, requiring exact state equality. This tests CPU mechanics only; official model/GPU determinism is unverified until its actual technical gate.

## Export evidence

The SMOKE last cell wrote `CrackSAFE_CP_Phase03_ALL_OUTPUTS_20261018T095256392563Z_4f544b7d.zip` with **64 members**, **1,587,956 bytes** and SHA256 `72b86d5f8fdd6a0c640110efba64de80227b81cb60bf721134526dc27b4fbef7`. Reopening verified CRC and every indexed payload; the exporter also verifies both index files. Repeating the final cell returned the same archive hash. The archive is a local engineering-test artifact, not a scientific handoff or persistent Kaggle version.

Storage fixtures forced FULL_ZIP_BLOCKED_STORAGE, produced a clearly labeled COMPACT_OUTPUTS ZIP, listed the separately pinned synthetic checkpoint payload, and verified compact idempotence. Another fixture verified full-archive idempotence and refusal to accept a changed payload. Actual account quota was not queried: the exporter checks measured disk, current output bytes and a configurable conservative saved-output ceiling, reporting that limitation.

Synthetic control fixtures exercised safe paths, manifest/source/blueprint hashes and ZIP CRC. Their outer hashes were intentionally different from the official locks. A dedicated test proved that these fixtures are rejected under the real Phase02 digest. Successful fixture verification does not establish integrity of private archives not used in this validation.

## Guard and metric checks

| Assertion | Result |
|---|---|
| 448_letterbox_valid_padding | PASS |
| empty_negative_loss_finite_gradient | PASS |
| loss_reject_shape | PASS |
| loss_reject_nonfinite | PASS |
| loss_reject_empty_valid | PASS |
| component_area20_skeleton20_threshold055 | PASS |
| component_area19_rejected | PASS |
| diagonal_8_connectivity | PASS |
| area25_short_skeleton_rejected | PASS |
| GT_not_pruned_cldice | PASS |
| synthetic_adapter_checkpoint_reload | PASS |
| resume_identity_rejected | PASS |
| resume_rng_exact | PASS |
| bounded_ensemble_temperature | PASS |
| engine_selection_tie_protocol | PASS |
| valid_png_Fig03_01_engine_comparison.png | PASS |
| valid_png_Fig03_02_seed_training_curves.png | PASS |
| valid_png_Fig03_03_temperature_reliability.png | PASS |
| valid_png_Fig03_04_hard_negative_tradeoff.png | PASS |
| valid_png_Fig03_05_efficiency.png | PASS |
| valid_png_Fig03_06_prediction_examples.png | PASS |
| valid_png_Fig03_07_failure_cases.png | PASS |
| synthetic_role_fixture_accepts_structural_contract | PASS |
| role_guard_provisional | PASS |
| role_guard_empty_train | PASS |
| role_guard_sealed_role | PASS |
| role_guard_group_overlap | PASS |
| role_guard_unit_overlap | PASS |
| role_guard_unknown_label | PASS |
| role_guard_unauthorized_zero | PASS |
| role_guard_hn_not_alias | PASS |
| unit_assignment_heldout_exclusion | PASS |
| sealed_access_api_rejected | PASS |
| actual_PROVISIONAL_blocks_training | PASS |
| S5_review_missing_rejected | PASS |
| unknown_model_license_rejected | PASS |
| synthetic_optimizer_scheduler_rng_resume_exact | PASS |
| synthetic_control_full_integrity | PASS |
| fixture_rejected_by_real_digest | PASS |
| wrong_outer_hash_rejected | PASS |
| zip_bin_same_raw_bytes | PASS |
| duplicate_mounts_rejected | PASS |
| zip_bin_discovery | PASS |
| old_run_sidecar_rejected | PASS |
| unexpected_archive_name_rejected | PASS |
| sidecar_alone_is_no_archive | PASS |
| CRC_corruption_rejected | PASS |
| ZIP_traversal_rejected | PASS |
| storage_fallback_honest_label | PASS |
| compact_zip_idempotence | PASS |
| compact_lists_checkpoint_parts | PASS |
| full_zip_idempotence | PASS |
| full_zip_mutation_rejected | PASS |
| blocked_FULL_completes | PASS |
| resume_config_change_rejected | PASS |
| resume_code_change_rejected | PASS |
| sealed_run_resume_rejected | PASS |

The loader also implements strict original-source rights/external-source exclusion using a reviewed non-label unit-to-source projection, and validates the exact five role hashes against S5. Actual approved role/data loading could not be exercised because the current real controls remain PROVISIONAL. That integration remains a future gated check, not a passed scientific test.

## Figures

All seven plotting functions wrote valid300-dpi PNGs from mock data, carrying **SYNTHETIC — FUNCTIONAL TEST ONLY**. Synthetic figures stayed outside `figures/figures_manifest.csv`. A meaningful static workflow was generated as methodology only; the seven real-result figure entries are NOT_GENERATED_BLOCKED. Visual inspection of the workflow and reliability fixture confirmed readable layout and the explicit synthetic watermark. Other plotting functions were checked for valid PNG format, dimensions and resolution, not independently visually reviewed panel by panel.

No synthetic figure or dummy score is offered as a thesis result. Real example generation requires a fixed lexical selection and explicit dissemination approval. Full topology/branch/LWBR methods remain Phase04.

## Environment actually used

Python: `3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]`. GPU: `None`. CUDA: `None`. Driver: `None`. This was a CPU engineering environment, not a benchmark environment.

| Package | Observed version |
|---|---|
| Pillow | 12.3.0 |
| mamba-ssm | NOT INSTALLED |
| matplotlib | 3.10.8 |
| mmcv-full | NOT INSTALLED |
| mmengine | NOT INSTALLED |
| numpy | 2.3.5 |
| pandas | 2.2.3 |
| pyarrow | 26.0.0 |
| scikit-image | 0.26.0 |
| scipy | 1.17.0 |
| segmentation-models-pytorch | NOT INSTALLED |
| timm | NOT INSTALLED |
| torch | 2.14.1+cpu |
| torchvision | NOT INSTALLED |
| transformers | NOT INSTALLED |

Missing basic QA packages and CPU PyTorch were installed in this Work environment for validation. The delivered notebook itself does **not** install packages or access the internet. No unsupported claim is made that this CPU dependency set is a working SCSegamba/DMSRCrack CUDA stack.

## Upstream review and implementation coverage

Read at project commit `dc52faf2929c9358ce36937c4a5131976c4fe8de`: blueprint sections5–7/12 and Phase03, Phase01 source/model roster/statistical contract/topology design, Phase02 source/notebook/workflow/README/handoff and actual public phase_status report. The official SCSegamba build/decoder and DMSRCrack constructor/output were inspected to implement actual wrappers, rather than renaming a test CNN. The public project files supply implementation context; private control verification remains a runtime requirement.

Implemented future branches include all five named adapters; common valid-pixel loss; source-aware approved loaders; deterministic augmentation; resumable single-seed training; best/last checkpoint registry; verified multi-job assembly; bounded ensemble-NLL temperature fit; fixed operational masks; same-unit metrics and descriptive CIs; technical/permission-only fallback enforcement; selection/freeze; real-result plotting gates; and small/full exports. Their guarded real-data/CUDA integration has not been executed here. Source/license/weight permissions and real human approvals were neither inferred nor fabricated.

No Phase04–08 notebook, ninth notebook, formal certificate, calibration/test result or GitHub write was produced. Current Phase04 authorization is **NO**.
