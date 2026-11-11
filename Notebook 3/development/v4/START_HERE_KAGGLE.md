# CrackSAFE Phase03 — Three notebooks, three seeds each (V4 safe split)

## Current 3×3 run
The existing 3×3 session already launched EfficientNet-B3 seed 42 and SegFormer-B0 seed 42. **Do not stop it just to switch notebook organization.** When it concludes or checkpoints have been exported, save the Kaggle version and the private model-specific job ZIPs with their .sha256 sidecars. If the session is stopped without saving, unexported work may be lost.

## Model-specific notebooks
- **3A:** U-Net++ EfficientNet-B3, seeds 42 / 123 / 2026.
- **3B:** SegFormer-B0, seeds 42 / 123 / 2026.
- **3C:** Adapted ConvNeXt-Tiny, seeds 42 / 123 / 2026.

These are three **Phase-03 development executions**, not three new numbered phases. They preserve original `CrackSAFE` V4 model definitions, 7,697/945 corrected manifest from which 6,771/785 are selected, data-access guards, 448 input, microbatch 2, effective batch 16, flips/90-degree rotations/brightness-contrast, 100 epochs, AdamW, warmup 5, cosine schedule, patience 15, and nine engine/seed experiment identities.

**Vital checkpoint compatibility:** Every notebook writes the exact same immutable V4 worker byte-for-byte (SHA256 `805ff45af895b1a728407f53921b969c0be66be3d521af85274849b73533d8d2`). The per-model scheduler runs in the calling notebook, leaving the worker's source hash, data/config identity and checkpoints unchanged. Do not edit the embedded source or training parameters.

## Kaggle setup
1. Create three **separate Kaggle notebooks** (one for each downloaded .ipynb). Each uses its own Kaggle session.
2. In every notebook choose **T4 ×2 GPU** and enable Internet only if pinned packages need installing. Kaggle must allow that many concurrent GPU sessions if you want simultaneous runs; otherwise run sequentially.
3. Add the original **Wall Crack-CP Datasets** and the exact **CrackSAFE_P02_Source_Split_Safety_Correction_v2_PRIVATE** private input (the expanded Kaggle dataset is supported).
4. For resumption, attach relevant private prior job ZIPs as Kaggle inputs: `CrackSAFE_P03_DEV_V4_LARGE_JOB_<model>_s42.zip`, `...s123.zip`, `...s2026.zip` as available. No more than one mounted copy of any engine/seed job archive. **Do not attach v3 or older pilot checkpoints**: changed protocol SHA prevents resuming them.
5. Run **the one code cell** in each respective notebook. It verifies all 7,556 selected image/mask hashes per independent session, executes 192 augmentation test cases and one model-specific real GPU preflight, then schedules only that model's three seeds. Two seeds may run concurrently on two GPUs; the third queues. Remaining work resumes from verified V4 job archives if attached.
6. Save Version, download and keep the PRIVATE job ZIPs and `.sha256` companions. Also preserve `CrackSAFE_P03_V4_LARGE_DEV_ALL_OUTPUTS.zip` or the explicitly named partial index ZIP and its `.sha256`. Do not rely exclusively on all-outputs ZIP if it is marked index-only.
7. Share the printed **SINGLE ENGINE DEVELOPMENT SUMMARY**, `PUBLIC_SINGLE_ENGINE_PROGRESS.json`, and any error log with ChatGPT. When all three notebooks have finished, collect all nine job ZIPs, then combine with a distinct Phase03 consolidation stage. Do not overwrite the original official Phase03 notebook.

## Scientific scope
The candidate split is provisional and uses parent proxies. Source test and calibration raw data are excluded. Technical checks are not proof of site-level independence. SegFormer and ConvNeXt remain documented developmental fallback candidates and are not official replacements for SCSegamba/DMSRCrack. No v3.3 risk certificate or FULL training status is claimed.
