# Resource assumptions and recovery

Compute, storage, and recovery plan

### 14.1 Planning assumptions

No Kaggle hardware or quota was measured during this review. Current official notebook documentation was checked [R22]; saved-output capacity is documented as up to 20 GB, while actual account/session options must be checked at execution. Do not hardcode a promised weekly GPU quota, GPU model, or uninterrupted session duration. Set a configurable session time budget from the live UI and reserve at least 30 minutes for checkpoint/export.

Plan for one 16-GB-class GPU, mixed precision, microbatches 2–8, accumulation to effective batch 16, and sequential ensemble inference. Dual T4 availability does not imply 32 GB of pooled memory for one model. CPU-only data/graph/statistics phases should not consume GPU quota unnecessarily. Exact RAM/disk needs are measured from the actual archive inventory and a representative sample.

### 14.2 Provisional model budgets

These are conservative scheduling ranges for roughly 6,000–10,000 training images at 448 resolution and early-stopped training, **not benchmarks or performance promises**.

| Engine | Provisional hours/seed | Three seeds | Memory starting plan | Main uncertainty |
|---|---:|---:|---|---|
| U-Net++ / EfficientNet-B3 | 4–12 | 12–36 | AMP, batch 2–8, one GPU | Decoder memory, loss and augmentation |
| SCSegamba | 4–16 | 12–48 | AMP and measured kernel support | Selective-scan build/runtime, backend differences |
| DMSRCrack | 6–24 | 18–72 | AMP, start batch 2 | Dual encoder and unavailable optimizations |
| SegFormer-B0 fallback | 3–10 | 9–30 | AMP, batch 4–8 initially | Adapter/decoder implementation |
| U-Net++ / ConvNeXt-Tiny fallback | 5–18 | 15–54 | AMP, start batch 2 | Encoder/decoder compatibility |

A recovered MRC-recipe comparison beyond the common-loss engine is additional training, budgeted separately; its three-seed cost may add 12–36 provisional hours. If original MRC artifacts are insufficient, omit the exact-recipe claim rather than silently spend on an invented reconstruction. Two additional single-model seeds add two actual jobs per chosen engine; score-only controller baselines add inference/statistics, not new model training.

Replace estimates after Phase-01 profiling. For N training images, E effective epochs, measured throughput s images/sec, estimate `GPU_hours ≈ N*E/(3600*s) + validation + checkpoint + setup`, with a 25% scheduling allowance. Profile preprocessing and data-loader stalls, not only a synthetic forward pass. Record exact GPU/runtime and permitted model-specific deviations.

### 14.3 Eight-phase schedule

| Phase | GPU-hour planning range | Person-time range | Constraint |
|---|---:|---|---|
| 01 | 0–3 | 3–7 days | Repository smoke/profiling only |
| 02 | 0–4 | 1–3 weeks | Annotation and parent recovery dominate |
| 03 | 42–156 for three preferred common-loss engines | 2–6 weeks | Queue/quota and early-stopping variability; extra recipes/seeds separate |
| 04 | 1–6 if predictions cached | 4–8 days | Skeleton/graph work is mainly CPU |
| 05 | 0–5 with caches | 4–8 days | No architecture retraining |
| 06 | 1–5 | 3–7 days | One calibration/internal inference sweep |
| 07 | 3–15 | 1–3 weeks | External/corruption inference and annotation |
| 08 | 0–5 without new training | 1–3 weeks | Statistics/packaging/efficiency |

Base total is approximately 47–199 GPU hours before optional recipe comparisons, extra seeds, heavy literature comparators, or data acquisition. Allow roughly 10–20 focused weeks, longer if independent negatives or field permissions must be acquired. The resource table is a planning aid; measured Phase-01 estimates replace it. If only 10 GPU hours/week are available, divide measured total by 10 and allow overhead; do not pretend the project fits one notebook session.

### 14.4 Storage and reading

- Inspect ZIP central directories, uncompressed sizes, and required member lists before extraction. Reject unsafe traversal paths, encrypted/unreadable members, duplicate ambiguous names, and decompression bombs. Use one selective extraction cache or independent worker ZIP handles; do not load all images into RAM.
- Deduplicate before packaging data; keep immutable original archives mounted read-only. Prefer efficient JPEG/PNG or indexed shards over thousands of repeated extracted copies. No lossy mask compression.
- Chunk prediction outputs by split/source; compute operational masks and scalar scores in the canonical inference dtype before any compression. Float16 diagnostic probability caches may change threshold decisions near 0.55 and cannot be reused to recompute certified losses unless equivalence was checked before calibration.
- Three float16 448×448 probability maps for 11,298 images alone require about 13.6 GB decimal (12.7 GiB), before inputs, checkpoints, and caches. Nine-model maps and float32 logits can exceed a saved-output limit quickly. Persist per-unit scores/losses and necessary masks; retain only essential high-precision maps or regenerate from hashed checkpoints.
- Keep checkpoints and data shards separate from the small phase-control bundle. Do not keep both a full extracted dataset and a duplicate ZIP in `/kaggle/working` when storage is tight. Record free space before each job and fail early with a clear required-space estimate.
- Pin environments per architecture if upstream stacks conflict. Common exchange formats (weights metadata, predictions, score schemas) allow inference artifacts to connect phases without forcing incompatible CUDA stacks into one process.

### 14.5 Recovery and release

Use `RUN_MODE=SMOKE|FULL` and `JOB=engine/seed/stage`; smoke data can never overwrite full artifacts. Save best and resumable-last checkpoints; fixed checkpoint hashes remain immutable after selection. Cache keys include input, model, temperature, preprocessing, mask filter, score, and formula hashes. Test one interrupted-run recovery and one fresh-session reattachment before committing long runs. Keep private data/checkpoints in appropriate private storage; code repository contains manifests/configs/tests, not unlicensed data or oversized weights.

---


This run measured only the current environment and any explicitly enabled model smoke. Training estimates remain provisional because no representative data-loader/training benchmark was performed. Do not multiply one-step initialization/checkpoint time into a claimed measured training estimate. A future valid estimate is N*epochs/(3600*measured_training_images_per_second), plus validation/checkpoint/setup and 25% scheduling allowance.

Live session limit supplied: None hours. If null, read your current Kaggle UI before scheduling GPU work. No fixed weekly quota or GPU allocation is assumed. Two GPUs do not pool their memory automatically. Keep raw ZIPs mounted; no whole-dataset extraction in this phase.
