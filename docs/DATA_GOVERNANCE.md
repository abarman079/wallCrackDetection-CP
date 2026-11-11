# Data governance, access barriers and rights

The repo is public; the training-data and independent-calibration evidence is not. Size alone is **not** an adequate publishing policy.

## Public

Blueprint, general research code, safe Kaggle scripts/notebooks, provenance hashes, aggregate counts, per-seed development summaries (after verification), synthetic tests, original aggregate plots, and research/limitations documentation.

## Private / restricted

Raw images and masks, per-image sample IDs, source-relative paths, face/people/geolocation metadata, unreviewed negative annotations, duplicate and parent-family registries, validation contact sheets, reserved source-test / calibration identities or labels, source-rights paperwork, reviewer identities and **all full control/checkpoint ZIP archives**. Store with restricted access and SHA-256 sidecars.

## Data access in this project

- The original Phase-02 technical audit completed, but source/site/session grouping and annotation semantics remain provisional.
- Phase-02 source-safe selection **quarantined** source test/validation membership and conflicting parent candidates before training.
- The 72-pair source-label visual/technical diagnostic accessed selected training/development candidate pairs only; source held-out/test and calibration pixel data remained unopened in that diagnostic.
- V4 training uses the five named candidate sources; `UNKNOWN` source records are excluded pending semantic resolution.
- The filename parent proxy is **not** an independent site or observation guarantee.

## Public-file admission checklist

Before publication, check actual dataset/image licensing, subject privacy, absence of private labels/paths, permitted split role, mask semantics, report annotations, metrics origin and file metadata (including EXIF/GPS). The automated script detects common mistakes but cannot establish copyright or data-subject authorization. Any uncertainty means **keep private**.

## Scientific gates

G02/G03 and S2/S6 remain unresolved. Technical completion or an advisor's general approval of using ChatGPT does **not** itself satisfy the blueprint's explicit independent data/annotation/rights conditions.
