# CrackSAFE-CP v3.3 — Phase-02 source-safe recovery and large development cohort

**Date:** 11 November 2026  
**Scope:** public-safe technical handoff, *not* approval of official Phase-02 FINAL.  
**Authoritative blueprint:** `CrackSAFE_MSc_Q1_Upgrade_Master_Blueprint_v3.3_8Phase_FINAL`.  
**Original Phase-02 technical FULL audit:** run `20261018T050513552430Z_afc0e8ab`, completed.

## 1. New Phase-02 technical evidence

- A previously completed recovery produced **13,459 unique technical candidate image/mask pairs**. They are not certified independent observations.
- The corrected source-safe v2 manifest retained **7,697 provisional training candidates** and **945 provisional development candidates**.
- It quarantined **3,607** records associated with original-source test/validation membership and **1,210** records with conflicting cross-role parent-group relationships; no raw reserved test or calibration pixels were accessed during the subsequent source-label check.
- The source-safe v2 metadata verified **970 train** and **189 development** *filename-derived parent proxies*, with exact image SHA-256 and parent-proxy role disjointness. These proxy groups do **not** establish independence of sites or camera sessions.
- A targeted visual/technical source-label diagnostic selected **72 pairs**, twelve across each of six source-hint categories. All 72 passed the selected image/mask byte-hash checks and provisional binary-mask reconstruction, with **zero technical errors**. This did **not** certify every pixel label or mask meaning.
- The `UNKNOWN` source-hint category had questionable or unusually broad masks in sampled visual diagnostics and remains excluded from the current developmental training selection pending proper mask-semantic resolution. This excluded **926 train** and **160 development** candidate records (total **1,086**).

## 2. Current source-safe large development cohort

| Role | Candidate count | Caveat |
|---|---:|---|
| Train | **6,771** | Provisional; no original source-test/calibration data |
| Development | **785** | Provisional; disjoint parent proxies and image hashes |
| `UNKNOWN` excluded | **1,086** | Pending mask-meaning review |
| Source test/validation quarantine | **3,607** | Never silently reintroduce into training |
| Mixed-parent quarantine | **1,210** | Never silently reintroduce into either role |

The V4 Phase-03 research-development runs use exactly these 6,771 / 785 candidates. The three separate model-specific notebooks train seeds `42`, `123`, and `2026` for:

- U-Net++ EfficientNet-B3 (architecture A);
- SegFormer-B0 (technical fallback, *not* original SCSegamba);
- adapted U-Net++ ConvNeXt-Tiny (technical fallback, *not* original DMSRCrack and not stock SMP).

The three 3-seed notebooks are development-only execution artifacts and **must not replace** the original official Phase-03 notebook or be represented as its FULL completion. Real checkpoint and model-score results should be committed only as public-safe summaries after each job actually completes. Keep private weight/checkpoint ZIPs with their SHA-256 sidecars outside this public repository.

## 3. Authenticity and integrity anchors

| Evidence artifact | SHA-256 |
|---|---|
| Phase-02 corrected source-safe v2 private ZIP | `14ff7b9f8e65b814adb249c1905ddf299fc60f888ec398c0f50016e7b8eca1cd` |
| Phase-02 source-label validation private ZIP | `bde823ef359de2fb83b320e5aea3af71b1b2a3ce406a5744419294488edf0f4c` |
| Prior recovery private archive (recorded in corrected manifest) | `3421d9024875df73b6d4c378e9aead21e9ebcc2255eade2b67536a2bd2dcd93d` |

The SHA-256 values identify privately retained evidence; they do **not** imply those files have been uploaded to GitHub. The public aggregate status JSON is at `Notebook 2/results/source_safe_v2/PUBLIC_SOURCE_SAFE_V2_SUMMARY_2026-11-11.json`.

## 4. Official blueprint gate status

- **G02:** BLOCKED — unresolved acquisition/site/session independence, complete annotation semantics, source and rights evidence.
- **G03:** BLOCKED — insufficient certified independent calibration and other reserved sampling units.
- **S2:** PENDING — fixed independent-unit sampling assumptions and evidence.
- **S6:** PENDING — source-rights/annotation reviewer resources.
- **S5:** GPU technical synthetic preflight passed for the three development model implementations; official architecture/permission roster remains separate.

The technical Phase-02 audit is completed. Scientific partitions remain `PROVISIONAL`, and official Phase-03 `FULL` training is **not authorized under v3.3**. Existing exploratory/development work can continue under its explicitly limited scope, without opening held-out labels or claiming a formal two-risk certificate.

## 5. Privacy and reproducibility policy

Only public aggregate counts, code, procedures and hashes belong in the public repository. Never publish private candidate CSVs, image/mask review worksheets, contact sheets, labelled reserved test data, raw datasets, source personal/rights documents, or checkpoint ZIPs. Public executable validation source can be committed under `Notebook 2/tools/` as a *preparation utility*, not an additional official numbered notebook.

The original official Phase-02 notebook, status and existing run results are unchanged by this addendum.
