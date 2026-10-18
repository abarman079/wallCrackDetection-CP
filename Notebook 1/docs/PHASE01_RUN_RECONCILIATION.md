# Phase-01 execution / repository reconciliation

**Reference run:** `20261015T111557980168Z_d3a9b41a` (2026-10-15, 11:15:57–11:35:18 UTC). This run is the verified Phase-01 upstream bundle used for the successful Phase-02 audit, in place of the older 10:24:08 run whose original control ZIP was no longer available.

**Control ZIP SHA-256:** `ac13d28e73a04825bcf77434de8a6b82ba051f1e1e5d94065901ef867d9f92ca`.

**Scientific design:** CrackSAFE-CP v3.3, blueprint SHA-256 `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e`. No statistical targets or methodology changed during ZIP-recovery or Git synchronization.

**Phase-01 technical evidence:** `run_mode=FULL`, `phase02_audit_ready=true`, `statistical_self_tests=PASS`, `missing_mandatory_outputs=[]`, `raw_input_layout=EXTRACTED_DIRECTORY`, 5 raw source collections. Overall status remains `BLOCKED` because human approvals and later model gates were not completed. The corresponding v3.3 Phase-02 control reports verify this specific upstream run.

**Document version note:** `CrackSAFE_CP_Phase01_Validation_Report.md` describes earlier local validation of a 47-cell draft. The revised executable `.ipynb` committed to GitHub has 49 cells and supports extracted Kaggle directories. The historical validation report is retained for provenance rather than silently revised to imply later validation.

**Storage:** The immutable control archive is retained outside public GitHub. The sidecar `.zip.sha256` is a reproducibility pointer; it does not replace the original ZIP when running downstream phases.
