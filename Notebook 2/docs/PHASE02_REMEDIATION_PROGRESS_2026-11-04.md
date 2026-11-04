# CrackSAFE-CP v3.3 — Phase-02 Remediation Progress

**Date:** 4 November 2026
**Status:** Preliminary research investigation; scientific approval pending.

## 1. Verified Phase-02 execution

- Canonical FULL run: `20261018T050513552430Z_afc0e8ab`
- Filesystem members: 121,794
- Examined image records: 88,806
- Quarantine records: 44,616
- Eligible independent certification units: 0
- Data partitions: PROVISIONAL
- Training authorization: BLOCKED

The original FULL audit remains unchanged.

## 2. Subsequent dataset investigation

### SDNET2018

- 56,092 image filenames examined.
- All filenames matched the investigated naming patterns.
- 230 candidate parent-photo identifiers found.
- 50 filenames contained an additional `_2` suffix.
- Filename grouping is not proof of acquisition independence.
- Pixel-level segmentation masks are not supplied by this collection.

### CRACK500

Among 10,344 non-flagged records:

- 9,875 timestamp-formatted crop filenames.
- 219 IMG-formatted crop filenames.
- 195 possible full-photograph filenames.
- 55 remaining alternative filenames.

Original acquisition relationships require verification.

### Suspected model-generated outputs

- 1,957 records under `fphb_testresult`.
- 1,957 records under `crackforest_testresults`.
- Total: 3,914 suspected prediction-output records.

These are flagged for investigation, not automatically deleted.

### Annotation-viewing pilot

- 35 selected image/mask records displayed using a private Kaggle viewer.
- Image and mask integrity checks were performed during inspection.
- The pilot does not establish annotation validity or independent sampling.

## 3. Remaining scientific requirements

- Verify original-source identity and research-use permissions.
- Establish documented parent, site and acquisition relationships.
- Investigate unresolved duplicate candidates and prediction-output roles.
- Obtain genuine expert annotation reviews and adjudications.
- Resolve mask semantics and target-population eligibility.
- Demonstrate sufficient independent units for all required data roles.
- Obtain supervisor approvals G02, G03, S2 and S6.
- Produce a new FINAL Phase-02 control if the evidence supports it.
- Complete separate S5 model and training authorization.

## 4. Phase-03 training readiness

The Phase-03 SMOKE run passed its engineering checks.
No real model training or experimental segmentation results exist yet.

Phase-03 FULL training remains BLOCKED until a valid FINAL Phase-02
handoff and the required model-specific authorizations are available.

This report is a public-safe progress summary, not a scientific approval.
Private sample-level records, reviewer evidence and held-out labels
remain outside the public repository.
