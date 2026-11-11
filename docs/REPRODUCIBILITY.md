# Reproducibility and immutable run identity

The authoritative [v3.3 blueprint](../Notebook%201/blueprint_v3.3.md) defines the phase methods, exclusions and scientific gates. Do not substitute newer code or provisional data for an older run's claimed protocol identity.

## Environment used for reported Kaggle Phase-03 V4 development startup

- Kaggle GPU: up to two NVIDIA Tesla T4 devices; each worker receives one GPU.
- `segmentation-models-pytorch==0.5.0`, `timm==1.0.30`, `transformers==5.20.2`.
- Training image size: `448×448`; microbatch `2`; effective batch `16` via accumulation `8`.
- Optimizer: AdamW, base learning rate `1e-4`, weight decay `0.01`.
- 5 warmup epochs; max 100 epochs; patience 15; selected model best/last checkpoints in private Kaggle.
- Training augmentations: horizontal/vertical flips, 90° rotations, mild brightness/contrast; development data **not** augmented.
- Seeds `42`, `123`, `2026` per model. Actual trained epochs and results must come from verified logged output.

These are execution settings for *development experiments*, not scientific authorization to open held-out data. The v4 embedded immutable worker hash reported by the actual launch is `805ff45af895b1a728407f53921b969c0be66be3d521af85274849b73533d8d2`.

## Run preservation

Store `best` and `last` checkpoint bytes, optimizer and RNG state, progress, epoch metrics, logs, code/config snapshot, input-source hash, cohort public ID, seed, model architecture name and exact SHA-256 sidecars in **private** storage. A public summary can contain cryptographic digests and aggregate scores but not raw private data.

For a resumed run, verify its protocol and artifact hashes; never resume a model under a different source split/augmentation. If an interruption corrupts the latest working checkpoint, restore a verified portable job archive. Never silently recalculate finished runs.

## Lightweight public checks

```powershell
python scripts/check_public_repo.py
python scripts/build_public_results_index.py
python scripts/check_public_repo.py
```

The CI job runs the publication checks on GitHub automatically. Full GPU training is **not** a CI requirement because it requires user-mounted licensed data and controlled private evidence.

## Phase-03 to Phase-04 development handoff

Complete each of the nine jobs, verify per-model/seed development outputs, archive the private models, publish labeled aggregate summaries, then freeze the development model/ensemble protocol before making any Phase-04 development comparisons. The original official FULL/ensemble roster still requires blueprint-specific eligibility.
