# CrackSAFE-CP Phase02 — implementation and validation report

**Result: all 39 top-level synthetic QA scenarios passed.** The delivered notebook contains 59 cells, including 29 executable code cells. Its Jupyter format, code syntax and execution order were validated. Complete synthetic SMOKE and small synthetic FULL workflows produced verified Phase02 control bundles and every mandatory output.

This is implementation validation, not a result from the private Kaggle dataset. No private Phase01 control ZIP or raw private dataset was accessed in Work. No model was trained, evaluated or certified. No real annotation, legal clearance, IID conclusion or supervisor approval is claimed.

## Delivered artifact identity

| Item | Value |
|---|---|
| Notebook | `CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb` |
| Notebook bytes | 193,555 |
| Notebook SHA-256 | `c2d389ed5619df11f6331ede419bcaec6cf3909d0887598224db1a8b000b52d9` |
| Embedded/exportable Phase02 core SHA-256 | `a8e8a1a27d1e195bfe9e1c371d49eb45e2d87e5b00c304dfbcbb96735d8d2511` |
| Format | nbformat 4.5; Python 3 kernel metadata |
| Locked blueprint | v3.3, unchanged |
| Blueprint SHA-256 | `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e` |
| Pinned real Phase01 run | `20261015T102408933036Z_d3a9b41a` |
| Required real Phase01 outer SHA-256 | `3543b6c09bb4ce2c577d8632c825b6f12d423c0f881afb137457db313566708d` |

An early notebook checkpoint was saved before implementation was completed. This report identifies the finished replacement. Phases03–08 were not generated and GitHub was not modified.

## Validation method and scope

The local harness constructed five synthetic extracted source directories containing 52 filesystem files and 27 candidate image records, including valid pairs, MATLAB masks, identical bytes, changed encodings, conflicting masks, crops, transformations, SDNET-style classification directories, an invalid image, ignore-valued masks, dimension mismatches and an orphan mask. Nested paths and a path-component ordering edge case tested the precise Phase01 fingerprint recipe.

A synthetic Phase01-like control bundle used the actual public Phase01 helper source as an implementation reference and a synthetic source ledger. The harness first proved that the production trust anchor rejects this fixture. Only the separate test harness substituted fixture outer/source hashes for subsequent synthetic execution; the delivered notebook retains the real user's fixed trust anchors and contains no fixture-bypass configuration.

All notebook code cells ran sequentially in an isolated Python namespace with those external fixture substitutions. This was **in-process cell execution**, not a remote Kaggle run or a separate Jupyter kernel process. The notebook's standard Jupyter JSON was also validated independently with nbformat.

A separate 1,840-unit metadata fixture tested allocation capacity and approval transitions. Its reviewer records, rights declarations and approvals were explicitly labelled synthetic test evidence. It demonstrated 300/300 calibration allocations after reservations, external-source exclusion including aggregate copies, disjoint target-unlabeled reservation, stale-signature rejection, and the difference between FINAL data partitions and training authorization. These counts are test inputs, not research observations.

Local Python: `3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]`.

| Dependency | Tested version |
|---|---|
| Pillow | 12.3.0 |
| numpy | 2.3.5 |
| pandas | 2.2.3 |
| pyarrow | 26.0.0 |
| scikit-image | 0.26.0 |
| scipy | 1.17.0 |

The existing Phase01 mathematical implementation is imported only after control integrity passes; its 20 built-in synthetic mathematical checks are rerun unchanged. Phase02 also runs nine limited preprocessing/metric primitive checks. These are included within workflow QA, not additional private-data experiments.

## Scenario results

| # | Scenario | Result |
|---:|---|---|
| 1 | Production trust anchor rejects synthetic bundle | PASS |
| 2 | Complete synthetic SMOKE workflow | PASS |
| 3 | Complete small synthetic FULL workflow | PASS |
| 4 | Five extracted source trees reconstruct exactly | PASS |
| 5 | CFD MAT and DeepCrack/CRACK500 adapters pair masks | PASS |
| 6 | Same bytes and re-encoded identical pixels linked | PASS |
| 7 | Conflicting masks quarantined | PASS |
| 8 | Transformed/cropped perceptual candidates exist | PASS |
| 9 | SDNET positives without segmentation remain ineligible | PASS |
| 10 | Empty masks do not promote negatives | PASS |
| 11 | Malformed, ignore-value and misaligned masks quarantined | PASS |
| 12 | Actual low capacity yields 120/122 shortfalls | PASS |
| 13 | No unapproved record enters train/development | PASS |
| 14 | Manifest JSON CSV and Parquet round trips | PASS |
| 15 | Control ZIP excludes private labels and heavy tables | PASS |
| 16 | Sealed run resume rejected | PASS |
| 17 | Unsealed resume reuses decode cache after rehashing input | PASS |
| 18 | Bad outer checksum rejected | PASS |
| 19 | ZIP traversal rejected | PASS |
| 20 | ZIP Windows absolute path rejected | PASS |
| 21 | Ambiguous Phase01 mount rejected | PASS |
| 22 | Missing control mount has actionable error | PASS |
| 23 | Added raw file is detected and reported | PASS |
| 24 | Label-free representative order is deterministic | PASS |
| 25 | Metric primitive suite | PASS |
| 26 | Every notebook code cell executes in order on synthetic input | PASS |
| 27 | Annotation imports, expert negatives, disagreement and stale evidence guards | PASS |
| 28 | Parent/site union and correlated crop grouping | PASS |
| 29 | Identical masks alone never merge different images | PASS |
| 30 | Capacity, source isolation, disjointness and FINAL vs PROVISIONAL approval path | PASS |
| 31 | Resume invalidates changed config or code | PASS |
| 32 | Internal payload corruption rejected despite matched outer fixture hash | PASS |
| 33 | CRC-corrupted ZIP rejected | PASS |
| 34 | Ambiguous extracted raw root rejected | PASS |
| 35 | Perceptual bucket/candidate caps remain deterministic and explicit | PASS |
| 36 | 20,000-hash bounded index microbenchmark | PASS |
| 37 | Budget interruption saves explicit resumable failure state | PASS |
| 38 | Research/redistribution separation and actual license-file integrity | PASS |
| 39 | Renamed extracted folder requires explicit mapping and unchanged hashes | PASS |

The bounded-index microbenchmark indexed 20,000 independent synthetic whole-image hashes in 2.962 seconds locally, with no cap truncation. It tested the index implementation only; it does not predict end-to-end performance on textured crack images, eleven query transforms, human-review workloads or Kaggle hardware.

## Implemented scientific and engineering safeguards

- The real successful Phase01 ZIP/sidecar are located recursively and pinned by outer SHA-256. Safe member paths, size limits, CRCs, internal payload hashes, manifest/blueprint/version, FULL/audit-ready state and exported code identity are verified before controlled import. Optional outside-ZIP seal files are not required inside it.
- Extracted folders are first-class inputs. The original Phase01 serializer and member ordering reconstruct the source tree fingerprint; mount names do not enter that digest. Full payload hashes are compared against the verified ledger. Missing, added, changed and inaccessible files fail explicitly. Same-content renamed folders require an explicit mapping.
- Image and mask decoding is batched and bounded. Source-specific pairing leaves ambiguous cases unresolved. Content hashing distinguishes byte duplicates, decoded-pixel duplicates, paired identities and mask conflicts. Identical masks alone never merge images.
- Perceptual candidate retrieval uses a bounded multi-index, not a full N×N comparison. Whole-image hashes are indexed once; rotations, flips and five crop windows are query variants. Overflows/caps are reported and excluded from unreviewed final use. Similarity is not treated as identity proof.
- Parent, crop, session and site links form conservative transitive groups. Unknown acquisition facts do not create IID singletons. Split IDs and certification-unit IDs remain distinct; each held-out group exports one eligible, label-blind representative.
- Actual annotation, duplicate, lineage, license and approval evidence is content-bound. Negative labels are never inferred from absent/all-zero masks or folder names. SDNET classification positives without segmentation masks remain ineligible for the topology endpoint. Double-review and disagreement/adjudication queues are explicit.
- Original-source research rights and redistribution are separate. License files are fingerprint-checked. The aggregate collection is not treated as a new independent source or as proof of upstream permission.
- Source/target unlabeled units are selected by label-blind IDs from documented domains before label-based split allocation. External-source groups and their aggregate copies remain out of development. Other held-out views never become training data.
- Every requested role CSV is created. Development compatibility/linked hard-negative aliases are checked as deliberate subset/union relationships. All independent roles are checked for sample/group/unit overlap. Proposed reservations precede calibration; exact floor and preferred-target shortfalls are visible.
- SMOKE is explicitly barred from FINAL status. FINAL requires full technical conditions and actual G02/G03/S2/S6 approvals bound to the concrete plan. S1/S3/S4/S5/S7 remain dependencies for the appropriate activities. S7 is the proposed 50% overall / 30% per-class automation criterion, not a sample-size rule or part of the guarantee.
- Aspect-preserving 448 letterbox, nearest-neighbor masks, valid-padding exclusion, 8-connected components, deterministic skeletonization and clDice edge cases are implemented. Ground-truth thin/small cracks are not pruned. The Phase04 branch/LWBR engine is not implemented here.
- Atomic outputs, resource checks, stage failure records, immutable seals and SQLite decode caching support restart. Resume rejects changed code/config/evidence and rechecks raw input bytes. Full data are never copied into generated shards.
- The small control ZIP excludes detailed private curator tables and held-out labels. Separate private audit output is optional. Manifest/catalog hashes cover unbundled provenance without requiring those labels in a development notebook. Exported bundles are verified before sealing.

## Important execution limits

1. The actual five private collections and successful private Phase01 bundle must be verified in Kaggle. Their real image counts, usable masks, duplicates, independent units, rights and class capacities remain unknown until that run and actual review.
2. Filename/path adapters cannot guarantee every unpublished folder layout. Unmatched pairs, unsupported MATLAB structures, color/ignore masks and orientation ambiguities need evidence-backed review or a versioned adapter change; they are not silently accepted.
3. Perceptual retrieval does not guarantee arbitrary-crop recall. Its limits, caps and unresolved candidates are explicit. Provenance remains necessary; uniqueness and curation do not establish IID.
4. Human review may leave many groups ineligible. Default no-evidence synthetic runs correctly completed with PROVISIONAL partitions and zero eligible calibration units; empty manifests are not replaced with invented samples.
5. The signed-in Kaggle UI, current account quotas, real runtime duration and private notebook mounts were not tested. Run SMOKE, inspect dependencies/paths, then run FULL and inspect the saved output version.
6. Manifest access rules are operational safeguards. A raw-dataset owner can still inspect original masks. The development loader refuses provisional/held-out use, but it is not a security sandbox.
7. Full review evidence, source permissions and a defensible class-conditional population/sampling rationale are required before scientific use. No calibration outcomes or model performance figures are produced by Phase02.

## Provenance and next step

The narrow public-code reference was `Notebook 1/phase01_core.py` in `abarman079/wallCrackDetection-CP` (retrieved Git blob `b47b541bf0d4ceacf77bdc5cfd90c7fefd3a2602`; local content SHA-256 `23178c4af342dff97e33a05bccaf6a51209a9df364175716414a7dfd74266dc6`). It was consulted to match the corrected extracted-folder fingerprint and shared-code contracts. It does not substitute for verification of the private pinned control bundle. No new comprehensive literature search or blueprint revision was performed.

Import the notebook in Kaggle, attach the two inputs, and run SMOKE. Use the accompanying Kaggle guide for FULL execution, evidence imports, the complete output inventory, exact Phase03 handoff and the recommended small GitHub tracked-file list.
