# Notebook02 handoff — actual run 20261015T102408933036Z_d3a9b41a

Blueprint 3.3; schema1.0; core1.0.0; config SHA-256 `d3a9b41a929c12d9895cd41212ccd44400141939c6289d2f1a8325dc00f4355f`; combined implementation/workflow SHA-256 `8e8b168fdc81dd35beebdd1d6819ba96b3f1d7c5b47695aa9390275c8c1e44bc`. Run mode **FULL**. Global Phase01 status **BLOCKED** while relevant evidence/signatures remain pending. Data-audit readiness: **True**. This does not permit training or calibration.

## Exactly what to attach

| File or Bundle | Purpose | Generated Kaggle Location | Required for Notebook 02? | How to Attach |
|---|---|---|---|---|
| `CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip` | All small Phase01 controls, blueprint, roster, statistical design, manifests and shared code | `/kaggle/working/cracksafe_cp/phase01/run_20261015T102408933036Z_d3a9b41a/CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip` | Yes | Prefer attach this saved Notebook01 output version through Add Input; private dataset alternative below |
| `CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip.sha256` | Verify final immutable ZIP bytes | `/kaggle/working/cracksafe_cp/phase01/run_20261015T102408933036Z_d3a9b41a/CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip.sha256` | Yes | Keep next to the ZIP in the same attached output/dataset |
| `phase01_manifest.json`, its sidecar, `SHA256SUMS.sha256`, `artifact_catalog.json`, `NEXT_PHASE_INPUTS.md` | Internal fingerprints and contracts | Inside canonical ZIP and `/kaggle/working/cracksafe_cp/phase01/run_20261015T102408933036Z_d3a9b41a` | Required contents; no separate attachment if ZIP is present | Read from verified ZIP |
| `statistical_design.json`, `model_roster.json`, `config.json`, `blueprint_v3.3.md`, `cracksafe_core.zip`, schemas/gates/reports | Exact downstream methodology and code dependencies | Inside canonical ZIP | Yes as bundled contents | Do not download/reattach each separately |
| `abarman79/wall-crack-cp-datasets` | Raw archives; deliberately absent from the control ZIP | Discovered here: `/kaggle/input/datasets/abarman79/wall-crack-cp-datasets` | Yes, attach the same actual dataset version again | Kaggle Add Input → Your Datasets; verify archive SHA-256 |
| Original legacy evidence and field/permission documents | Resolve still-missing provenance if later supplied | Actual optional mounts recorded in ledgers | Optional for Phase02 initial audit; required before claims depending on them | Attach private evidence dataset; never fabricate replacements |

**Recommended path:** save Notebook01 with **Save Version → Save & Run All** (wording may differ), wait for completion, verify Output contains ZIP + sidecar, then add that exact output version to Notebook02. Kaggle official documentation supports attaching saved notebook outputs via Add Input. Record the actual notebook/version identifier; do not rely on mutable latest.

**Reliable fallback/portable archive:** create a **private Kaggle dataset** containing the canonical ZIP and sidecar only. Version it, attach it to Notebook02, and also attach the raw dataset. Use this if the output-version picker is unavailable or cannot pin the version. Check privacy. A local draft run alone is not persistence.

Actual mount slugs are discovered. Examples such as `/kaggle/input/<saved-notebook-output>/.../CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip` or `/kaggle/input/<phase01-control-dataset>/CrackSAFE_CP_v3.3_phase01_control_20261015T102408933036Z_d3a9b41a.zip` are examples only. Recursively discover the exact canonical basename plus sidecar; if more than one run matches, require an explicit choice. Never guess the mount directory.

## Critical artifact IDs and content hashes

| Artifact ID | SHA-256 | Bytes |
|---|---|---:|
| `phase01:blueprint_v3.3.md` | `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e` | 161911 |
| `phase01:config.json` | `df26752540f56556febf008a7e89a40dda12e088acf60d353f47b04c2180570b` | 880 |
| `phase01:statistical_design.json` | `995a94d9d309c5a3188a5bc8087d321a74c3130fb546a54ea7928f68eba4c635` | 5008 |
| `phase01:model_roster.json` | `b27dbc4f764684a1ca38c15425efd088082619e0a3d8557ca439b2ddf7ee9bce` | 8921 |
| `phase01:field_data_decision.md` | `e9004fbc47ce586c89715f44892a1add4808115054461bb63db1ca702722f3ae` | 965 |
| `phase01:decision_gates.csv` | `db6ba73137ed619e618533714544a910fc8062b30384841c25c665702f86eb53` | 6176 |
| `phase01:supervisor_decisions.md` | `b8ea2a7d150e8a520610bdb23046a728f535d2f6f23dcf7355e0c63f90fce5a6` | 2750 |
| `phase01:archive_inventory.csv` | `6efae9ad3c096f630fd5906fc7d07b8e3de63e2ef260b6afb6b467f94b817981` | 1740 |
| `phase01:dataset_discovery.json` | `a15b5a6472b1803db0ce22af6c3c1452c7faf7cc38a9e2b1a16a5ec9aad7e765` | 540 |
| `phase01:legacy_manifest.json` | `7e6fb638e9d3ec7eace53b43ceacac24e35a2f09aab7c67bc9838a50d8d43d8a` | 1487 |
| `phase01:missing_inputs.csv` | `66796e63e9e34e0eb659dd4293c689531991473079d77cca137446f928bd9b72` | 955 |
| `phase01:schemas.json` | `f7d25b29ec7b3763a0c54b860ae1b4b7e71f63978226cb95d2cc6e79f80b8569` | 8044 |
| `phase01:cracksafe_core.zip` | `c1cd2c886607c7d01a9e2cb11836189261e4fee3eb18be87368440a13a943252` | 39358 |

The outer ZIP hash is deliberately absent from this document because it is stored **outside** the ZIP in its sidecar. This document lists earlier payload hashes only; the final manifest hashes this document. Do not create a circular self-hash.

## What may proceed and what remains blocked

A FULL, hash-valid, schema-valid bundle with identifiable raw archives permits **Phase02 source/data auditing**, even if legacy checkpoints and later-model/GPU checks are missing. Unsafe or corrupt archive members remain quarantined; this permission is not permission to extract them. Missing expected archive names must be reconciled against actual source coverage; renames alone are not proof of missing data.

S1 exact design remains proposed until signed; S2 actual population, independent-unit definition and fixed count plan must be reviewed before the Phase02 calibration manifest is approved; S6 source rights/reviewer resources must be documented before benchmark use. S3/S4/S5/S7 and G07 apply before their later dependent activities. None is automatically signed by this notebook. The exact list of unresolved items is in missing_inputs.csv, decision_gates.csv and supervisor_decisions.md.

Never modify sealed outputs, hashes, blueprint bytes, code bundle or original input archives. Amendments create a new version/run with explicit provenance and invalidate dependent caches. If the current run is SMOKE, rerun FULL before treating the input fingerprints as complete. If mandatory outputs are missing or hashes disagree, stop the affected audit dependency and preserve the failure report.

## Phase02 execution order

1. Discover mounted control ZIP and sidecar; reject ambiguity rather than guess latest.
2. Verify ZIP fingerprint before safe extraction; validate paths, sizes and internal hashes.
3. Verify phase01_manifest schema/version and critical artifact hashes.
4. Resolve raw mounts by ZIP SHA256 or extracted-directory member/tree SHA256; no silent source substitution.
5. Read warnings, exclusions, source/permission ledgers and unresolved decisions.
6. Inventory pairs, decode validation, exact/decoded/perceptual hashes and source aggregation overlap.
7. Recover site/session/parent lineage; quarantine ambiguity; adjudicate masks and confirmed negatives.
8. Count independent units, choose population and fixed count plan with S2 review.
9. Create grouped partitions and label-blind representatives; freeze split/access manifests; no final calibration.
10. Export Phase02 artifacts, gates and next handoff.

Required detailed schemas and barriers are in phase02_contract.json, schemas.json and the embedded blueprint Section12. No model checkpoint is required to start Phase02. No Notebook02–08 implementation is included in this bundle.
