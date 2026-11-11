# Phase-03 V4: three separate model-specific development notebooks

**This is a supplemental developmental implementation**, not an official FULL replacement for `../../CrackSAFE_CP_Phase03_Legacy_Modern_Baselines.ipynb`.

Three expected notebooks, each running seeds `42`, `123`, `2026`, one model per notebook:

- `Notebook_3A_U-NetPP_EfficientNetB3.ipynb`
- `Notebook_3B_SegFormerB0.ipynb`
- `Notebook_3C_ConvNeXtTiny_Adapted.ipynb`

These filenames describe locally prepared model-runner artifacts; their GitHub presence must be checked after upload. They share a verified provisional source-safe V4 cohort (**6,771 training / 785 development**) and immutable training-worker SHA `805ff45af895b1a728407f53921b969c0be66be3d521af85274849b73533d8d2` as reported in the launch logs.

The initial user-supplied Kaggle logs confirm actual launches of seeds 42 and 123 for all three engines; seed 2026 is queued. **No nine-job completion is claimed.** Completed per-seed development scores belong in `../../results/public/run_<id>/` only after review of actual logs/ZIP SHA and export integrity.

SegFormer-B0 is a development fallback for the SCSegamba slot; adapted U-Net++ ConvNeXt-Tiny is a fallback for DMSRCrack. Results must not be mislabeled as native SCSegamba/DMSRCrack experiments.

Attach the original Wall Crack-CP dataset and corrected Phase-02 v2 private manifest to the Kaggle notebooks. Do not publish those datasets/manifests here. Store checkpoint ZIPs privately with `.sha256` sidecars. The signed scientific Phase-02 eligibility gates remain blocked; this development roster is **not** an approved official-model benchmark.
