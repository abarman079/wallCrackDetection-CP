# CrackSAFE-CP v3.3 — S5 GPU integration technical result

This is a **technical preflight**, not Phase-03 FULL training or scientific approval.

- Phase-03 original SHA-256: `3b9d1171e4de2f7ea1b2c29d836fbe45a2a6a7dc4584a671f695b7720b3d656f`
- S5 staged draft SHA-256: `cbbad8a5f04e1e2bdf1f4c651004c774a39e3900747f0a50033c6eb22e4fe8d3`
- Blueprint SHA-256: `2738247fc12f05bd1dd2cd0d85477bbd955d1b549593e732682538b9fc37e64e`
- CUDA device: Tesla T4
- S5 integration result: **THREE_ENGINE_GPU_PASS**

| Engine | Integrated synthetic GPU check |
|---|---|
| unetpp_convnext_tiny | PASS_REAL_GPU_SYNTHETIC_INTEGRATION |
| unetpp_effb3 | PASS_REAL_GPU_SYNTHETIC_INTEGRATION |
| segformer_b0 | PASS_REAL_GPU_SYNTHETIC_INTEGRATION |

The primary architecture slots remain U-Net++ EfficientNet-B3, SCSegamba,
and DMSRCrack. SegFormer-B0 is the first documented technical/permission
fallback; the adapted ConvNeXt-Tiny is second and is not identical to stock SMP.
Testing a fallback does **not** authorize its substitution.

Not accomplished here: source/weights permissions for all intended engines,
S5 frozen research protocol, committed source identity, Phase-02 FINAL, or real training.
No study dataset images, calibration labels, test labels, or checkpoints were exported.
