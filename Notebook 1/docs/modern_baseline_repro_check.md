# Modern model reproducibility assessment

Documentation inspection is not reproduction. A PASS smoke result tests random tensor forward/backward and reloading an own random checkpoint, not accuracy, pretrained-weight rights, full training or supervisor approval.

| Model | Technical smoke | Local code license | Source identity |
|---|---|---|---|
| unetpp_effb3 | NOT_RUN | UNVERIFIED | NOT_RUN |
| scsegamba | NOT_RUN | UNVERIFIED | NOT_RUN |
| dmsrcrack | NOT_RUN | UNVERIFIED | NOT_RUN |
| segformer_b0 | NOT_RUN | Apache-2.0 | PACKAGE_VERSION_AND_SOURCE_HASH; git commit unavailable |
| unetpp_convnext_tiny | NOT_RUN | UNVERIFIED | NOT_RUN |

Input contract: B×3×448×448; segmentation output B×1×448×448 after the explicit SegFormer bilinear logit upsampling adapter. No silent resizing is permitted for other engines. DMSRCrack first tuple output is segmentation; second is boundary. SCSegamba custom operator and output semantics require pinned-source review.

Kaggle CPU/GPU support and memory are proven only by the actual model_checks/*.json results. Source pins, code license and pretrained-weight permission are separate. No dependency downgrade or CUDA compiler installation is automatic. If stacks conflict, use separately versioned environments and exchange hashed artifacts. Any failure must lead to repair, the declared technical/legal fallback before training, or a dated amendment; poor accuracy is not a fallback trigger.

The worker blocks network calls and uses random initialization. Third-party checkpoints are never unpickled. A deliberate one-step synthetic tensor optimization tests gradients and is not a full-data training experiment. SCSegamba may require dependencies unavailable in current Kaggle; that remains a BLOCKED result.
