# CrackSAFE-CP — MSc Thesis and Q1 Research Master Blueprint
## Version 3.3 FINAL research specification — eight phases / eight Kaggle notebooks

**Prepared:** 15 October 2026. **Literature review cutoff:** 15 October 2026.

**Full project title:** Component- and Topology-Aware Risk-Controlling Prediction for Selective Structural Crack Segmentation under Domain Shift.

**Legacy:** CrackSAFE-MRC. **New system:** CrackSAFE-CP. **Authoritative implementation document:** this file; no earlier blueprint is required to understand the project.

**Status:** Completed upgrade specification, with explicit proposed decisions requiring researcher/supervisor sign-off in Section 19. “FINAL” denotes a complete blueprint, not completed experiments, verified data access, or approved research results. No Kaggle notebook, dataset audit, model training, or real-data calibration has been performed as part of this upgrade. The attached v3.2 blueprint was read in full. Its historical numerical results are carried forward as user-provided records, not independently reproduced results.

**Principal correction:** retain the risk-control research identity, but replace the unsupported attribution of selective conditional-risk certification to a monotone RCPS search with an explicit finite-family, exact-binomial simultaneous confidence-bound procedure. This is a Learn-then-Test-compatible risk-controlling prediction procedure. Existing notebook filenames containing `RCPS` are retained for continuity; the manuscript must describe the actual procedure accurately.

**Immediate action:** Phase 01 coding can begin. Do not train models before the data and design gates pass. Final calibration remains locked until the independent-unit, sample-size, inference-only policy, and mathematics-to-code gates pass. Real-domain importance-weighted results are empirical unless their stronger assumptions are independently established.

---

## Contents

1. Research identity, scope, and critical review
2. Research questions, hypotheses, and novelty
3. Verified literature positioning
4. Legacy evidence and provenance
5. Data, independence, annotations, and split architecture
6. Segmentation engines, calibration, and common protocol
7. Structural metrics and failure definitions
8. Prediction-only uncertainty and decision policies
9. Exact selective risk-control procedure and proof
10. Domain shift and weighted analysis
11. Evaluation, comparisons, ablations, and statistics
12. Artifact contracts and notebook execution
13. Complete eight-phase specifications
14. Compute, storage, and recovery plan
15. Decision gates and contingencies
16. MSc and Q1 scope; manuscript requirements
17. Detailed v3.2 → v3.3 change register
18. Preservation and review traceability
19. Implementation readiness and approval decisions
20. Verified reference register
21. Version history and final checklist

---

## 1. Research identity, scope, and critical review

### 1.1 The scientific problem

Crack masks can have reasonable pixel overlap while missing branches, breaking centerlines, merging nearby structures, or hallucinating cracks on joints, stains, shadows, and textured surfaces. This research asks whether a frozen segmenter can be accompanied by an auditable controller that decides which images to automate while bounding two explicitly defined error probabilities on the automated subset.

The outputs are `ACCEPT_POSITIVE`, `ACCEPT_NO_CRACK`, `REVIEW`, and `REJECT_OUT_OF_SUPPORT`. Accepted masks support inspection; they do not diagnose structural safety, load capacity, crack severity, or maintenance urgency. Research targets of 10% branch-preservation failure and 5% false-structure failure are not engineering safety tolerances.

The central contribution is a reliability controller, not a new segmentation backbone. Preserve exactly eight major phases and eight notebook files. Multiple saved runs of the same notebook for different model/seed jobs are permitted and expected.

### 1.2 Strengths of v3.2 worth preserving

- Clear focus on selective inspection and two complementary risks, rather than a model zoo.
- Recognition of parent-image leakage, hard negatives, independent calibration/test data, and historical-population mixing.
- Binary primary endpoints, transparent review workload, a review-all escape policy, and negative-result reporting.
- Three independently trained ensemble members; frozen inference and score transforms.
- Structural synthetic tests, phase gates, fallbacks, hashes, and manuscript assets.
- Conditional scope for shift research and an early field-data decision.

### 1.3 Critical weaknesses corrected here

**Selective risk and multiplicity.** A nested acceptance set does not imply monotonically decreasing conditional error. Searching 13 policies with only a two-risk correction is not justified by the stated design. Section 9 supplies a direct argument with 26 simultaneous bounds, protecting the highest-coverage selection without a monotonicity assumption.

**Unresolved deployment score.** v3.2 separated `U_topo_eval` from `Q_topo_policy`, but did not finish the latter's construction. Its GT-dependent missing-value cases cannot drive real inference. Section 8 defines a symmetric ensemble branch-disagreement score on every valid image, including all-empty ensembles.

**False precision about independence.** Thousands of crops are not thousands of independent trials. Group splitting prevents direct leakage but does not, by itself, make all held-out patches independent. Section 5 defines the actual certification observation and restricts the claim to its sampling population.

**Calibration size and retry risk.** Eighty negative units are insufficient for the corrected 13-policy search even with zero observed failures. Outcome-triggered expansion of a fixed-sample calibration set can also introduce optional-stopping bias. Section 9 replaces both rules.

**Shift guarantees.** ESS and domain AUC are diagnostics, not proof of covariate shift, density-ratio accuracy, or support coverage. Passing them authorizes empirical analysis only. A separate known-weight construction illustrates what a valid stronger claim would require.

**Metric overinterpretation.** `LWBR >= 0.90` with 75% branch matching does not mean 90% of all centerline pixels are preserved and does not guarantee connectivity. The endpoint is retained but named and interpreted precisely; continuity and spurious topology remain mandatory complementary outcomes.

**Novelty and comparators.** Selective crack prediction, topology uncertainty, and joint mask/skeleton/uncertainty learning already exist. Add a risk-calibrated entropy control using the same frozen segmenter and statistical machinery; otherwise benefits could be due entirely to calibration rather than topology.

**Lifecycle inconsistencies.** Late ensemble expansion, test-driven ablations, unverified licenses, and formulas introduced after their first use can invalidate reproducibility. These are resolved by early contracts, bounded comparator scope, and an immutable deployed ensemble.

### 1.4 Evidence limits of this review

This is a focused primary-source literature review, not an exhaustive systematic review or a proof that no identical method exists. Publisher pages that blocked full text were supplemented only by original repositories, original preprints, and retrievable publisher metadata/abstracts. Such limitations are marked in Section 3. No paper's published score is treated as a common-protocol result. Citation and repository availability were checked; repositories were not installed or benchmarked in this task.

---

## 2. Research questions, hypotheses, and novelty

### 2.1 Defensible contribution hierarchy

**N1 — operational structural endpoints.** Define an auditable branch-preservation failure on crack-positive inspection units and a false-valid-component event on confirmed no-crack units. Distinguish these from pixel loss, predictive uncertainty, and structural safety.

**N2 — two-risk selective controller.** Instantiate exact finite-family risk control for both class-conditional automated risks, with explicit denominators, policy-search multiplicity, zero-denominator states, and practical sample-size accounting.

**N3 — prediction-only topology information.** Test whether ensemble branch disagreement adds useful coverage or failure capture beyond ordinary entropy under the same model, data, risk targets, and calibration procedure.

**N4 — honest validity boundaries.** Separate in-population certification, empirical external stress testing, and mathematically qualified shift correction. Audit hard negatives by source/category rather than claiming robustness from one favorable aggregate score.

These form an application/methodology contribution. Neither exact binomial inference, LTT, ensembles, nor skeletonization is claimed as a new statistical theorem. Journal strength depends on demonstrated engineering relevance and nontrivial incremental value.

### 2.2 Research questions and predeclared interpretation

| ID | Question | Evidence / decision rule |
|---|---|---|
| RQ1 | What survives the legacy lineage audit and clean retraining? | Separate historical, clean-retrained, and genuinely unseen legacy-model results. No directional hypothesis about a necessary performance drop. |
| RQ2 / H2 | Which reproducible engine offers the best development topology–negative-error–cost tradeoff? | Fixed base gate and selection rule; independent test comparison is descriptive/paired. |
| RQ3 / H3 | Does prediction-only topology disagreement improve detection of branch-preservation failures? | Primary paired AUROC difference versus predictive entropy on positive test units; report AUPRC and review capture. Report a 95% descriptive paired CI; confirmatory support requires a positive Bonferroni-adjusted 97.5% CI lower endpoint across the H3/H5 two-contrast family, with no material contradiction in operational measures. |
| RQ4 / H4 | Can the two-risk procedure certify nonzero automation? | Both calibration UCBs pass at the fixed targets; otherwise report `lambda13`. The mathematical validity is conditional on assumptions, not a hypothesis proven by a favorable test sample. |
| RQ5 / H5 | Does topology improve automation over risk-calibrated entropy? | Difference in independent-test coverage between two separately certified fixed systems, with class-specific coverage and paired CI; confirmatory superiority requires the adjusted 97.5% CI lower endpoint to exceed zero. No positive superiority claim if topology gives only a better accepted subset by censoring a class. |
| RQ6 | What fraction of failures is referred at 10%, 20%, and 30% review? | Ranking/workload analysis separate from certified policies. No assumption that a human fixes every referred failure. |
| RQ7 / H6 | How does shift change risk and review load? | Per-domain risks, workload, calibration drift, failure categories, and paired corruption effects; no universal direction assumed. |
| RQ8 / H7 | Do estimated weights improve target-domain empirical behavior? | Precommitted weighted empirical analysis and diagnostics; H7 is empirical, not a claim that AUC/ESS imply guarantee validity. |

H3 is preregistered against entropy, not whichever baseline happened to win the test AUROC table. Variance, confidence, and a reproducible structural-uncertainty comparator are secondary. Development H3 tables are exploratory design diagnostics; the final H3 assessment uses untouched test outputs after policy lock.

### 2.3 Primary, secondary, and operational endpoints

Primary deliverable: a selected policy with two simultaneous calibration upper bounds and its independent-test automated coverage, class-specific coverage, automated error counts, and uncertainty intervals.

Key secondary: unconditional crack Dice/IoU/clDice, accepted-case Dice with denominators, continuous skeleton coverage, branch metrics, false components, worst-domain results, and entropy-controller comparison. Worst-domain accepted Dice is demoted from co-primary: it can be improved simply by refusing hard domains. Domains with zero accepted positives are `N/A`, never silently omitted from a “worst-domain” claim.

Operational: review capture at fixed budgets; fraction accepted positive/no-crack; review and rejection rates; runtime and memory. A useful-coverage target of 50% overall and at least 30% in each class is a **proposed engineering utility criterion**, not part of the theorem. Report actual values regardless of whether that criterion is signed off or met.

---

## 3. Verified literature positioning

Reference IDs below resolve to primary links in Section 20. Repository availability is distinct from verified permission, successful reproduction, or runnable Kaggle compatibility.

| Work | Verified contribution and overlap | Code / evidence status at review | Consequence for CrackSAFE-CP |
|---|---|---|---|
| Bates et al., RCPS [R01] | Finite-sample high-probability control for risk-controlling prediction sets. | Original paper and official `aangelopoulos/rcps` repository verified. | Foundational context; do not transfer a monotone-risk argument to a changing selective denominator. |
| Angelopoulos et al., Learn then Test [R02] | Multiple-testing framework; includes binary selective classification and several risks. | Full original preprint and linked official code verified. | Appropriate framework for the explicit non-monotone finite-family procedure in Section 9. |
| Clopper–Pearson [R03] | Exact binomial confidence limits. | Original publisher DOI verified. | One-sided binary-risk UCB; no normal approximation or pixel-as-trial substitution. |
| Conformal Risk Control [R04] | Generalizes conformal calibration to monotone losses with an expectation guarantee. | Original preprint verified. | Distinguish expectation control from the calibration-sample high-probability statement needed here. |
| Gupta et al., NeurIPS 2023 [R05] | Structure-wise uncertainty using discrete Morse representations and learned/perturbed structural reasoning. | Full proceedings paper and official `struct-uncertainty` repository verified; license permission still needs checking. | Topology uncertainty itself is not new. Include a closest-comparator feasibility decision and acknowledge the different mechanism. |
| SelectSeg, RESS 2025 [R06] | Deep-ensemble uncertainty, filtering/noisy-label training, and selective crack prediction. | Publisher metadata/abstract and original repository verified; full publisher text unavailable in this review. | Closest selective-crack comparison. Do not claim first selective crack segmentation. Same-engine selective component adaptation is clearly labeled; full SelectSeg reproduction is conditional Q1 work. |
| SCSegamba, CVPR 2025 [R07] | Lightweight structure-aware visual state-space crack segmenter. | Original preprint and official repository; Apache-2.0 reported and license file visible. | Retain as modern lightweight candidate; benchmark actual kernels and memory. |
| DMSRCrack, Automation in Construction 2026 [R08] | CNN/Transformer dual-encoder multiscale refinement, including cross-domain evaluation. | DOI and author-linked implementation verified; no explicit license visible in inspected repository listing. | Retain conditional slot, not an unconditional reproducibility claim. SegFormer-B0 replaces it if Phase-01 permission/build gate fails. |
| TopoSAM, EAAI 2026, DOI with 2025 stem [R09] | SAM-based topology branch, cross-branch fusion, and background-adversarial twin learning for generalization. | Publisher title/abstract/DOI verified; full text blocked; no author-verified code repository established by the focused search. | Narrative comparator; absence of a verified code link is not proof that no code exists. No compulsory SAM training. |
| CrackMamba / Topology-aware Mamba, 2024 [R10] | Topology-aware Mamba crack architecture. | Original preprint and author repository verified. | Distinguish from SCSegamba. Literature comparator, not an extra mandatory architecture. |
| CrackGeoFM, 2026 [R11] | Joint masks, skeletons, and uncertainty through a crack-adapted foundation representation. | Original June 2026 preprint, publisher record, and original repository verified; repository says accepted, checkpoints include unresolved release placeholders. | Material novelty overlap. Restrict novelty to selective structural-risk certification and controlled comparisons; do not add a large foundation model to the core. |
| Deep ensembles [R12] | Independently trained predictors provide useful predictive uncertainty. | NeurIPS original paper verified. | Supports mechanism, not a guarantee that three members detect shared errors. |
| clDice [R13] | Skeleton/mask overlap for tubular structures with specific topology analysis. | CVPR paper and original code verified. | Retain structural evaluation. A high clDice score is not a safety certificate. |
| Conformal Semantic Image Segmentation, CVPRW 2024 [R14] | Post-hoc segmentation uncertainty using conformal risk control. | CVF record and original preprint verified. | Pixel/set-level segmentation control is prior work; compare risk units and guarantee types explicitly. |
| Controlling False Positives in Image Segmentation, 2025 preprint [R15] | Post-hoc confidence masks and false-positive control by shrinking masks. | Original preprint and stated code link verified at abstract level. | False-positive segmentation control alone is not novel; our dual class-conditional selective endpoint is different. |
| Tibshirani et al., covariate-shift conformal prediction [R16] | Weighted conformal inference with likelihood-ratio information under covariate shift. | Original paper verified. | Estimated embedding weights and diagnostics do not inherit exact coverage automatically. |
| Almeida et al., COPA 2025 [R17] | High-probability risk control under covariate shift via weighted LTT. | PMLR original record and original paper source verified. | Closest shift-theory anchor; apply only with its assumptions and the correct conditional-risk adaptation. |
| Zecchin et al., 2025 [R18] | Informativeness/generalization analysis of weighted conformal risk control. | Original preprint verified. | Different guarantee/objective from arbitrary selective class-conditional risk; not a substitute theorem. |
| UCrack-DA, 2025 [R19] | Multiscale unsupervised domain adaptation for surface crack segmentation. | Original publisher article verified; linked dataset does not establish model-code availability. | Domain adaptation is established; this project does not invent a UDA training method. |
| Active, anytime-valid RCPS, 2024 preprint [R20] | Sequential/active calibration with time-uniform validity. | Original preprint verified. | Explains why adaptive repeated calibration needs additional machinery; excluded from the fixed-sample core. |
| SDNET2018 [R21] | Image-level crack/no-crack dataset built from 230 parent images and many crops. | Original article and institutional dataset page; dataset page states CC BY 4.0. | Large crop count cannot solve independent-unit scarcity; positive labels are not segmentation masks. |

**Remaining gap, stated cautiously:** the sources reviewed do not establish the exact CrackSAFE-CP protocol: simultaneous finite-family control of accepted positive-unit branch-preservation failures and accepted negative-unit false structures, combined with prediction-only branch disagreement, parent-aware calibration, and explicit empirical/theoretical shift boundaries. This is a supported positioning judgment, not an absolute “first-ever” finding. Refresh the matrix before submission; exclude future/unverifiable titles rather than inventing entries.

Phase 01 exports a literature matrix with: `paper_id, year, venue, task, datasets, risk_unit, topology, uncertainty, selective_prediction, guarantee_type, class_conditioning, domain_shift, hard_negatives, multi_seed, code_url, license_status, evidence_level, closest_overlap, remaining_gap, verified_date`. The bibliography must not copy incorrect dates from repository BibTeX without checking the publication record.

---

## 4. Legacy evidence and provenance

### 4.1 Canonical historical reference

These are supplied v3.2 records, not newly verified measurements:

| Population | N | IoU (crack only) | Dice (crack only) | No-crack FP rate | Status |
|---|---:|---:|---:|---:|---|
| Legacy Phase-12 held-out calibrated subset | 1,356 | 0.581844 | 0.722288 | 0.045977 | Primary historical reference; subset of legacy validation, not a new independent test |
| Legacy Phase-14A full validation pool | 1,695 | 0.582254 | 0.722671 | 5/218 = 0.022936 | Supplementary historical analysis only |

Legacy model: U-Net++ / EfficientNet-B3; Boundary + clDice + Lovasz loss; temperature 1.556495; mask threshold 0.55. Preserve Phase-14A precision 0.996626, recall 1.000000, specificity 0.977064, F1 0.998310, TP/FP/TN/FN 1477/5/213/0, Boundary IoU 0.343042, and clDice 0.793017 in the historical record. The v3.2 reported external clean-SDNET FP maximum of 72.9% is motivation only until its source artifacts/population are recovered.

Suggested historical wording: Legacy CrackSAFE-MRC used U-Net++ with an EfficientNet-B3 encoder and topology-aware training, followed by temperature scaling and a 0.55 mask threshold. The 1,356-image Phase-12 subset gave IoU 0.5818, Dice 0.7223, and no-crack FP rate 0.0460. These are legacy validation evidence. Phase-14A uses a different population and is reported separately.

### 4.2 Three distinct model/evidence identities

1. `MRC_HISTORICAL`: original records; no statistical test against new results on another population.
2. `MRC_FROZEN_CHECKPOINT`: evaluate only where training exposure is known and disjoint. Unknown exposure means exploratory/historical status.
3. `MRC_CLEAN_RETRAIN`: retrain the architecture on the new approved training groups; this is the common-protocol baseline.

Do not assume that moving an old training image into a new test split makes the old checkpoint independent of it. Record `ever_used_for_training`, `ever_used_for_model_selection`, and `legacy_exposure_status`. Prefer previously unseen groups for new final evaluation. Previously inspected legacy validation data belong in training/development unless a supervisor accepts a transparently retrospective evaluation limitation.

Original legacy counts of 9,603 training images, 1,695 validation images, and 11,298 combined pairs are inventory expectations, not asserted current counts. Missing legacy artifacts do not get fabricated: export an explicit missing-input ledger and allow a historical-only baseline if necessary.

---

## 5. Data, independence, annotations, and split architecture

### 5.1 Expected Kaggle input and registry

Expected raw mount: `/kaggle/input/wall-crack-cp-datasets/`. Discover actual ZIP names recursively; never hardcode an unverified archive filename. Expected collections include CRACK500, CrackTree200, GAPs384, CFD/CrackForest, DeepCrack, SDNET2018, and a combined segmentation collection. Inventory archive entries before extraction.

The combined collection is an aggregation, not a new independent source. Retain original `source_dataset_id` after deduplication. Similar names such as DeepCrack can refer to distinct papers/datasets: resolve original provenance, version, image count, and masks before assigning a source. CFD here means CrackForest Dataset, not an unrelated Cityscapes-derived dataset.

Registry fields: `dataset_id, original_name, version, official_url, citation_id, access_date, license_url, license_text_hash, research_use_status, redistribution_status, label_type, material, acquisition_protocol, raw_count, unique_count, eligible_count, exclusion_count, native_resolution, parent_metadata_available, archive_sha256`. Public accessibility is not a license. An aggregation's license does not automatically license every original image. Share manifests and download instructions when redistribution is unsupported.

SDNET negative labels require adjudication before treating the entire mask as zero. Positive classification-only examples may support classification/qualitative analysis but cannot enter pixel/topology evaluation without independent segmentation annotation.

### 5.2 Audit order

1. Phase-01 quick scan of legacy filenames, prefixes, numeric stems, crop coordinates, and known split CSVs. If unavailable, report `UNAVAILABLE`, not “no leakage.”
2. Phase-02 byte SHA-256, decoded-pixel SHA-256, and image/mask pairing validation; differing encodings can represent identical images.
3. Perceptual hashes and frozen feature-neighbor retrieval identify candidates, not automatic equivalence. Flag transformed crops/resized copies; manually adjudicate ambiguous matches without model-performance information.
4. Use crop coordinates, parent files, source documentation, and visual evidence to reconstruct parent/augmentation families. Exact masks alone do not prove identical source images.
5. Union linked duplicates/parents into conservative groups before splitting. Flag conflicting masks/labels and quarantine until resolved.
6. Freeze exclusion reasons, linkage confidence, and unresolved candidates. Unknown lineage is not silently replaced with a unique filename.

Any cross-partition leakage invalidates independence for affected groups. The old `q > 10%` rule survives only as a workload escalation threshold: with `q = affected legacy validation images / verified legacy validation N`, `q > 0.10` triggers a full reconstruction. Even `0 < q <= 0.10` requires quarantine/rebuild; it does not license a partially contaminated final test. Use 1,695 as denominator only if verified.

### 5.3 Split group versus statistical observation

Use the highest documented dependence level: site/structure → capture session → parent image → original image. Crops and augmentations remain attached to that group. A `split_group_id` is a leakage-control identifier. A `certification_unit_id` is the actual independent draw used in Section 9; the two are recorded separately.

**Primary conservative observation rule:** sample one representative image from each independent acquisition group using a fixed seeded, label-blind choice among eligible images. If only a parent image and its patches are available, choose one fixed representative patch from that parent. If the original full parent is available and is the declared deployment input, use that original instead. Freeze this representation for the entire experiment; do not mix parent-level and patch-level observations opportunistically. The represented population is “a sampled image/patch from a sampled independent group,” not every pixel or every crop in a structure.

Other views of a held-out group remain held out and may be evaluated only in cluster-aware supplementary analyses. They cannot inflate certification n or enter training/development. If several sites supply many parents and residual site dependence is plausible, parent-level binomial claims require an explicit conditional-on-site acquisition model; absent that justification, use one site-level representative or make descriptive claims only. Three field sites cannot support a high-confidence population guarantee merely by producing thousands of crops.

Independent and identically distributed sampling **within each true class** is the operational assumption of the binomial core. Exchangeability alone is not asserted sufficient for this particular confidence interval. Dataset curation cannot prove IID; the data card must describe why the chosen sampling model is reasonable and its limitations.

### 5.4 Population contract and source holdouts

Define an internal reference population before training: eligible acquisition protocol, materials/sources, annotation rules, image representation, and source mixture within each class. Calibration and internal test must follow the same class-conditional sampling law. Prespecified positive/negative sample sizes may differ because risks are class-conditional; report balanced and empirical-mixture coverage, and avoid calling the artificial class mixture a deployment prevalence.

Within a class, draw groups randomly from the fixed source-mixture population. Do not enforce arbitrary per-source quotas and then use an IID pooled-binomial theorem without a corresponding stratified derivation. Source-specific diagnostics are descriptive unless separately powered and corrected.

An external source must be absent in training, development, and primary calibration, including copies hidden inside the combined collection. A fresh split of a previously used source is internal, not external. If all available sources were already used, obtain a new source or perform a predeclared leave-one-source-out retraining experiment; do not relabel contaminated evaluation as zero-shot generalization.

### 5.5 Required partitions and access permissions

| Manifest | Purpose / permitted use | Forbidden use |
|---|---|---|
| `train.csv` | Fit model weights and augmentations | Final certification/evaluation |
| `development_model.csv` | Checkpoint selection, limited tuning, debugging | Final inference claim |
| `development_probability.csv` | Fit probability temperature only | Final risk calibration |
| `development_policy.csv` | Engine selection, uncertainty transforms, endpoint characterization, OOD reference fitting | Final calibration/test evidence |
| `hard_negative_development.csv` | Predeclared negative subset linked to the appropriate development role | Borrowing its groups into final negatives |
| `calibration.csv` | One fixed-sample certification run after freeze | Fitting model, temperature, score definitions, or new thresholds |
| `internal_test.csv` | One frozen evaluation of all preregistered systems | Any method revision |
| `external_positive_test.csv` | True source-held-out positives with masks | Tuning or calibration |
| `hard_negative_test.csv` | Independently adjudicated final negative challenge set | Mining only final-model failures or tuning |
| `source_unlabeled_pool.csv` | Natural source-distribution covariates for density-ratio estimation | Risk labels or test reuse |
| `target_unlabeled_pool.csv` | Separate target groups for shift fitting/diagnostics | Reusing final target-test groups transductively |
| `reserve_pool.csv` | Fixed extra candidate units allocated before calibration-error access | Outcome-driven repeated enlargement of the same calibration run |
| `field_test.csv` or `corruption_test.csv` | Route fixed in Phase 01 | Opportunistic route switching |

`development.csv` is a compatibility union of the three development manifests; roles remain distinguishable. A suggested initial development subdivision is 60/20/20 by group. Exact counts depend on the Phase-02 audit, not assumed percentages that leave too few independent negatives. Where data cannot support three subdivisions, a preregistered shared-development design is acceptable because all development remains independent of calibration; report its model-selection optimism. The fixed test/calibration separation cannot be relaxed that way.

The curator may inspect labels to validate masks, class membership, and splits before sealing. “Unopened test” means no downstream model fitting, performance inspection, or human method revision from its images/labels. A single researcher cannot erase prior knowledge; retain a dated access log and disclose retrospective choices. Final annotations must be adjudicated without seeing method rankings.

### 5.6 Annotation and hard-negative benchmark

Freeze `annotation_manual_v1.md` before annotation: crack/background ambiguity, thin structures, minimum represented width by source/resolution, occlusion, discontinuities, junctions, borders, uncertain regions, label disagreement, and adjudication. Unknown regions are not zero-valued negatives.

Certification uses fully adjudicated binary-positive masks and confirmed all-background negatives. Cases with unresolved labels/ignore regions go to an uncertainty-label challenge subset with coverage/exclusion counts; they cannot silently disappear after a model makes an error. Source-only partial labels cannot certify full-image absence.

Hard negatives require category labels, at least one trained/expert no-crack adjudication, and capture/source metadata. Prespecify a random double-review subset, proposed `max(20%, 30 units)` capped by available N, plus all disagreements; record raw agreement and adjudication, not only a final consensus label. No automation may fabricate expert approval.

Categories: joint, expansion joint, grout/tile seam, stain, shadow, scratch, paint edge, water mark, cable/wire, rough texture, aggregate boundary, masonry joint, image border, vegetation/debris, compression artifact, other. Record material, light, camera/device if known, capture distance if known, native resolution, indoor/outdoor, site/source, reviewer, confidence, and license. Do not infer missing metadata.

Choose a source/category sample independently of final-model failure. A development-model-mined challenge subset is allowed only as separately labeled stress data with different prevalence. After final predictions, associate false components with artifact categories; do not curate final membership from those predictions. Category imbalance and ambiguous exclusions must be reported.

### 5.7 Field decision

Phase 01 records Route A only when access, permission, responsible annotators, devices, and a dated capture plan are genuinely secured. Aim for at least three sites and two devices where feasible, including positive/negative and indoor/outdoor examples. These are diversity goals, not independent-sample sufficiency.

Otherwise lock Route B: external sources, hard negatives, and controlled corruptions. Late field data is a new prospective amendment or supplemental set, not a replacement for an inconvenient external result. No field availability is asserted in this blueprint.

---

## 6. Segmentation engines, calibration, and common protocol

### 6.1 Bounded model roster

| Slot | Primary candidate | Rule |
|---|---|---|
| A | U-Net++ / EfficientNet-B3, clean retraining | Mandatory legacy architecture reference; recover original loss/config or explicitly label a reconstruction. |
| B | SCSegamba | Keep if legal/dependency/shape/forward-backward checks pass in Phase 01. |
| C | DMSRCrack | Conditional on Phase-01 license/permission and runnable training checks; public code alone is not enough. |
| Fallback | SegFormer-B0 | First substitute for a failed modern slot. |
| Second fallback | U-Net++ / ConvNeXt-Tiny | Use only if another slot fails and the encoder implementation is verified; never duplicate an identical model under two labels. |

No fourth mandatory architecture. A one-modern-engine MSc reduction is a clearly documented resource amendment requiring supervisor approval before comparative training; the preferred plan retains three slots. SCSegamba/DMSRCrack are not replaced because their preliminary accuracy is disappointing.

Phase-01 checks: source commit, exact license, dependency versions, pretrained-weight license and exposure, 448-resolution input/output, CPU/import test if supported, one GPU forward/backward batch, checkpoint reload, actual memory, and measured training throughput. A pass is not a reproduction of published accuracy. Record deviations from each paper.

SelectSeg is a controller/training comparator, not a mandatory fourth backbone. For the core, compare same-engine uncertainty selection and exact entropy risk control. For Q1, either reproduce its relevant inference component faithfully on compatible inputs, or document why it is unavailable and name an adaptation accurately. Full noisy-label selective training is a separate optional experiment, because this project is not primarily a noisy-annotation study. Gupta-style structural uncertainty receives the same predeclared feasibility assessment; no untested reimplementation may be called an official reproduction.

### 6.2 Training protocol

Use native RGB and a single documented deterministic spatial transform. Default is aspect-preserving resize to fit 448×448 and zero/background letterbox padding; mask resize uses nearest-neighbor; image interpolation and padding are fixed. Padding is excluded from scores/metrics. Every spatial threshold refers to this common evaluation grid. Training patches are sampled only inside training groups; evaluation has no stochastic crop or label-dependent tiling.

Native-resolution sliding-window evaluation is supplementary and requires its own fixed stitching/resampling contract; do not mix its pixel thresholds into the primary table.

Starting common training config: AdamW, learning rate 1e-4, weight decay 1e-2, effective batch 16 through accumulation, maximum 100 epochs, 5-epoch warm-up, cosine decay, and early stopping patience 15 on development-model crack Dice. Save earliest checkpoint on exact ties. These are **proposed reproducible defaults**, not recovered MRC settings or known optimal settings. Architectures may use documented paper-required differences with a matched maximum tuning budget of two development-only learning-rate trials (1e-4 and 3e-4). Freeze the choice before final multi-seed jobs.

Primary common loss: 0.5 binary cross-entropy + 0.5 soft Dice, evaluated only on valid pixels; empty-mask Dice uses a documented epsilon. This clean common-protocol track separates backbone effects from losses. A separate MRC-recipe row uses the recovered Boundary + clDice + Lovasz weights, implementation, and normalization; if missing, mark `RECIPE_UNRECOVERED` and do not fabricate coefficients. At least one topology-loss comparison is useful Q1 evidence, but its expense must be preregistered. Do not falsely describe common-loss U-Net++ as an exact MRC reproduction.

Allowed default augmentation: horizontal/vertical flips, 90-degree rotations, and mild brightness/contrast on training only. No aggressive elastic warp, MixUp/CutMix, synthesized negatives, or topology-altering augmentation in the primary protocol. Record model normalization and pretrained initialization. No crack-trained public checkpoint with possible test-source exposure may initialize a clean comparator; generic ImageNet pretraining must still be disclosed.

Main seeds: `[42, 123, 2026]`. Optional additional individual-model seeds: `[3407, 8675309]`. Seed-specific data-loader generators, augmentation randomness, mixed-precision state, and optimizer state are preserved. Repeat failed technical runs with the same seed after logged fixes; never discard a low-performing valid seed.

### 6.3 Probability calibration is separate from risk calibration

For each candidate engine, fit one shared positive temperature `T` to its three-member ensemble on `development_probability` only, minimizing mean image-level binary NLL over valid pixels. Use a fixed bounded one-dimensional optimization in log T with `0.05 <= T <= 20`; record optimizer, convergence, boundary hits, and the unscaled comparison. Group/image averaging avoids letting the largest image dominate. If fitting fails, use preregistered T=1 with a recorded failure, not an arbitrary manual value.

For member logits `z_m(i)`, define:

\[
p_m(i)=\sigma(z_m(i)/T),\qquad \bar p(i)=M^{-1}\sum_{m=1}^{M}p_m(i),\quad M=3.
\]

These probabilities are temperature-scaled model outputs; probability calibration quality is evaluated, not assumed. Do not transplant the historical T=1.556495 into a new model. A separately labeled exact legacy replay keeps its historical temperature.

Calibrate only before risk-policy freeze. T, thresholds, component filters, score transforms, and model weights never change after certification. Temperature fitting is not the Section-9 calibration and receives no risk-control guarantee.

### 6.4 Base gate and engine selection

Evaluate the three-member mean prediction on development-policy positives and adjudicated development hard negatives. The proposed inherited readiness gate is crack-only IoU ≥0.56 and false-valid-component rate ≤0.35. These thresholds are feasibility heuristics inherited from v3.2, not universal quality requirements for a new dataset.

Among passing engines choose highest development-policy clDice; tie within 1e-6 → lowest hard-negative false-valid-component rate; next tie → lowest median synchronized inference latency; final tie → lexical engine ID. Freeze before calibration/test access. Apply the same gates/selection unit to all engines and publish per-seed as well as ensemble metrics.

If none passes, inspect labels, preprocessing, loss, and training. Apply only the predeclared technical fallback or an explicit development-only amendment; do not proceed with a claim of useful automation merely by reviewing almost everything. A negative feasibility report is permitted. Changing a heuristic gate requires a dated rationale and supervisor review before calibration.

### 6.5 Ensemble lifecycle

The primary deployed controller always uses the same three seed checkpoints. A five-seed performance table means five individual training runs, not five independent realizations of the three-model ensemble. Optional seeds must have frozen configs and preferably finish training in Phase 03 before test access; Phase 08 aggregates their locked evaluations. Expanding M=3 to M=5 changes probabilities, scores, and the policy and therefore requires fresh calibration independent of that modification. It is not a free Phase-08 upgrade.

---

## 7. Structural metrics and failure definitions

### 7.1 Image/mask contract

On valid pixels, `B_raw(i) = 1[p_bar(i) >= 0.55]`. Use 8-connected foreground components and a fixed connectivity convention for all measurements. A component is operationally valid iff area ≥20 pixels, mean temperature-scaled probability ≥0.55, and skeleton pixel count ≥5. `B_op` is the union of those valid components.

The component-mean condition is retained for compatibility but is mathematically redundant when every retained raw pixel already has probability ≥0.55. Report this honestly; do not describe it as an independent false-positive suppression mechanism. There is no hidden closing, dilation, gap filling, branch pruning, or learned postprocessor.

Primary segmentation and structural-risk metrics use `B_op`; provide `B_raw` overlap metrics as a supplement to expose the effect of filtering. Evaluate members with the same operational rule when computing uncertainty. Never filter away small GT cracks by the predicted-component rule. GT mask positivity is any adjudicated crack foreground; very small labeled structures remain eligible and can reveal failure of the operational minimum-size rule.

### 7.2 Deterministic skeleton/branch graph

Use pinned `skimage.morphology.skeletonize(method="zhang")` on binary 2D masks. If the installed API differs, pin a compatible documented version; do not switch algorithms silently. Primary analysis has no branch pruning.

Graph procedure:

1. Construct an undirected skeleton-pixel graph. Orthogonal neighbors have edges; include a diagonal edge only when neither shared orthogonal neighbor is skeleton, preventing redundant tiny corner triangles. Freeze this convention in synthetic fixtures.
2. Degree-1 pixels are endpoints. Adjacent degree≥3 pixels form a junction cluster. Compress each cluster to a junction node; preserve its pixel membership.
3. Trace each unvisited non-junction path between endpoints/junction clusters exactly once, using lexicographic coordinates to break traversal ties.
4. A pure degree-2 closed cycle is one cyclic branch, with a deterministic lexicographic anchor. An isolated pixel is a singleton branch of length one. A component wholly inside a junction cluster is represented as one residual branch.
5. Partition all skeleton pixels into branches: assign endpoint/junction pixels shared by paths to the path with lexicographically smallest ordered path signature. Include any remaining node-only pixels as a residual branch. No pixel is double-counted. Discard any path record assigned zero pixels from the branch-length list while retaining its graph-edge metadata. Store node and path geometry separately for secondary connectivity analysis.

Primary branch length `|b|` is its assigned skeleton-pixel count, consistent with the inherited LWBR definition; it is not a physical length in millimeters. Eight-neighbor Euclidean edge length is supplementary. Store the raw graph and branch ownership so alternate graph packages cannot silently redefine the metric.

### 7.3 Matching tolerance

Primary tolerance `r=4` Euclidean pixels on the valid 448×448 evaluation grid is retained as an inherited benchmark convention, **not** justified by the unsupported claim that `r=2*minimum crack width` is universally correct. Minimum annotation width is still audited by source. Dilation uses a disk with distance ≤r, with no wraparound and no padding pixels.

Before model rankings are examined, inspect annotation resolution/registration and the plausibility of this tolerance on a fixed 20-image development subset stratified by source and thin/thick structures. Do not tune r to performance. If annotation evidence requires a different primary tolerance, enter proposed decision S3 in Section 19 and date an amendment before structural model comparisons; retain all radii `{2,4,6,8}` as sensitivity results. State the native-grid equivalent and how letterboxing affects scale. Tolerance sensitivity is especially important because large r can match nearby parallel branches incorrectly.

### 7.4 Ground-truth evaluation metrics

For GT branch b and predicted operational skeleton S:

\[
C_b=\frac{|b\cap\operatorname{Dilate}(S,r)|}{|b|},\qquad I_b=\mathbf1[C_b\ge0.75].
\]

\[
\operatorname{LWBR}=\frac{\sum_b |b|I_b}{\sum_b|b|},\qquad
\operatorname{SCR}=\frac{|S_y\cap\operatorname{Dilate}(S,r)|}{|S_y|}.
\]

LWBR weights entire matched branches; SCR measures continuous skeleton-pixel coverage. **LWBR ≥0.90 does not imply SCR ≥0.90**: if every branch is exactly 75% covered, LWBR is 1 although SCR is 0.75. Nor does matching rule out breaks, bridges, merges, or false branches. Therefore the certified claim must say “branch-preservation failure,” not “all topology errors” or “no more than 10% centerline loss.”

Primary crack-positive failure:

\[
L_{miss}(x,y)=\mathbf1[\operatorname{LWBR}(y,B_{op}(x))<0.90].
\]

Primary confirmed-negative failure:

\[
L_{false}(x)=\mathbf1[N_{valid}(x)\ge1].
\]

The underlying prediction and these events are policy-invariant; policies only select which images are automated. Ground truth computes loss after prediction, never the decision.

Default LWBR threshold remains 0.90. On development only report failure prevalence at `{0.75,0.80,0.85,0.90,0.95}`. A prevalence ≤5% or ≥95% triggers diagnosis, not automatic threshold relaxation. Verify annotation/metrics and scientific meaning first. Any change must precede calibration and record why the original endpoint was unsuitable; retain the original sensitivity row and mark S3 approval. A composite continuity/branch endpoint is an optional future amendment, not silently introduced here.

### 7.5 Mandatory secondary structural outcomes

- clDice using the original definition; separate raw/operational masks and report empty-set conventions.
- SCR; branch recall; reverse-direction branch preservation precision; spurious predicted-branch rate.
- Split count: a GT component overlaps (within r) at least two predicted valid components. Merge count: a predicted component overlaps at least two GT components. Report count and rate with applicable component denominators; matching proximity alone does not establish a topological bijection.
- Longest unmatched contiguous run along each GT branch, normalized by branch length; wrap a loop when calculating its longest gap.
- Endpoint/junction localization/count disagreement and false bridges, as secondary outcomes with explicit correspondence rules before use.
- On negative units: valid false components/image, largest false-component area, total false skeleton pixels, category and source.

Endpoint/junction location matching uses maximum-cardinality bipartite matching within radius r, tie-broken by minimum total Euclidean distance then coordinate order; component split/merge counts use the overlap graph above. Avoid declaring these optional details “implemented” until tests exist.

### 7.6 Edge cases

| Situation | Evaluation rule | Inference uncertainty rule |
|---|---|---|
| Positive GT, empty operational prediction | LWBR=0, SCR=0, `L_miss=1` | Use prediction-only score normally; never exclude a failure because its score is low |
| Confirmed empty GT | Miss metrics `N/A`; include in false-structure risk | Score remains defined without consulting GT |
| Nonempty GT but extraction produces no branches | Metric bug / quarantine before evaluation; no automatic miss-risk exclusion | No GT access |
| All member operational masks empty | Evaluate loss normally from GT | `U_topo_policy=0`, status `ALL_MEMBERS_EMPTY`; this denotes agreement, not certainty of correctness |
| Ensemble-mean mask empty but any member nonempty | Positive loss remains fully counted | Disagreement computed from member branches |
| Single pixel / short GT branch / loop | Explicit branches as above; no GT pruning | Same deterministic graph procedure |
| Both masks empty | Overlap Dice/IoU=1 for an all-image descriptive aggregate, but excluded from crack-only summaries; structural metrics `N/A` | No fabricated positive decision |
| Empty GT, nonempty prediction | Dice/IoU=0; false risk uses valid components | Prediction-only scores |
| Invalid/decode-failed input or nonfinite score | Count exclusion/failure reason; no numeric score imputation | Route `REVIEW`; data rejection is not proof of OOD |

### 7.7 Required synthetic verification

Perfect line, Y branch, 5-pixel gap, two components, loop, empty pair, spurious branch, bridge/merge, equal pixel count with altered connectivity, singleton, diagonal staircase, adjacent junction pixels, missing small component, all-empty members, and one-member-only branch. Test thresholds exactly at 20/5/0.55/0.75/0.90 and at neighboring values. A 5-pixel gap may be covered by r=4 dilation; tests must reflect that limitation, not assume every visible break triggers LWBR failure.

Add an explicit fixture demonstrating `LWBR=1, SCR=0.75`, and a bridge fixture with high LWBR but a merge error. These prevent overclaiming what the endpoint measures. Hand-checked expectations, formula IDs, function names, and fixtures are registered before real structural output is trusted.

---

## 8. Prediction-only uncertainty and decision policies

### 8.1 Ordinary uncertainty

Normalized predictive entropy:

\[
h(i)=\frac{-\bar p(i)\log\bar p(i)-(1-\bar p(i))\log(1-\bar p(i))}{\log2}.
\]

Use float64 for scalar reductions; clip probability only for logs with epsilon 1e-7. Primary image score is the mean of the largest `ceil(0.10*N_valid_pixels)` entropy values. This fixed top-decile aggregation reduces background dilution and is defined on empty-mask images. It is frozen, not selected by an AUROC competition. Global mean entropy is a required secondary baseline. Predictive entropy is total predictive uncertainty, not pure epistemic uncertainty.

Other comparisons: top-decile ensemble variance using population divisor M; confidence score `mean_top_decile(1-max(p_bar,1-p_bar))`; boundary entropy if a prediction-derived boundary exists, with explicit empty-boundary fallback to global entropy; optional MC dropout only with a supported dropout architecture and fixed pass count. None replaces the primary entropy baseline after viewing performance.

### 8.2 Primary topology score — complete and label free

For each of M=3 member operational masks, extract skeleton `S_m` and branches `B_m`. For each branch b from member m, compute its preservation against every **other** member:

\[
c_{b,\ell}=\frac{|b\cap\operatorname{Dilate}(S_\ell,r)|}{|b|},\qquad
d_b=1-\frac{1}{M-1}\sum_{\ell\ne m}\mathbf1[c_{b,\ell}\ge0.75].
\]

\[
U_{topo}^{policy}(x)=
\begin{cases}
\displaystyle\frac{\sum_m\sum_{b\in B_m}|b|d_b}{\sum_m\sum_{b\in B_m}|b|}, & \sum_m\sum_b|b|>0,\\
0, & \text{all member operational skeletons are empty}.
\end{cases}
\]

This symmetric, length-weighted leave-one-member-out score lies in [0,1]. No GT, consensus-GT matching, or class label enters it. A branch predicted by only one member receives uncertainty 1; the same branch in every member receives 0. Shared branches appear once per member by design; denominator semantics must be reported. This is a project-specific score to be validated, not claimed as a proven optimal estimator or a reproduction of Gupta's method.

Using every member's branch set avoids the consensus-mask blind spot in which a branch disappears from the mean prediction and is never scored. It still cannot detect a branch confidently missed by every member or a false crack unanimously hallucinated. Record `all_members_empty`, `mean_mask_empty`, member valid-component counts, total evidence length, and `topology_score_status` to quantify that limitation.

The GT-referenced quantity `U_topo_eval` may be calculated for diagnostic branch analyses and is `N/A` without GT branches. It never supplies `Q_topo`, never masks H3 evaluation cases, and never appears in the deployed input signature. For H3, every eligible positive test unit, including all-empty false negatives, remains in the score/label pairs.

### 8.3 Percentile transforms

For either primary raw score u, fit on `development_policy` valid inputs only:

\[
Q(u)=\frac{\#\{u_j<u\}+0.5\#\{u_j=u\}}{N_{dev}}.
\]

This midrank CDF is label-free at transform time, deterministic, bounded in [0,1], and tie-aware. Persist exact sorted score values, score/formula versions, valid/excluded N, class/source counts, development hash, float precision, tie comparison rule, and timestamp. Freeze exact floating equality for ties after the deterministic score computation; do not use ad hoc epsilon bins on test data. Quantized export requires a new fixed comparison rule and equivalence check before calibration.

The same transform handles zero topology scores for all-empty inputs. Missing scores from a computation failure cause review; they are not median-imputed or treated as certain. Percentile scaling is not probability calibration.

### 8.4 Policy family and decision precedence

Retain the original 13 paired thresholds and explicit sentinel:

| Policy ID | tau_topo | tau_base | force_review_all |
|---|---:|---:|---|
| lambda00 | 1.00 | 1.00 | false |
| lambda01 | 0.95 | 1.00 | false |
| lambda02 | 0.95 | 0.95 | false |
| lambda03 | 0.90 | 0.95 | false |
| lambda04 | 0.90 | 0.90 | false |
| lambda05 | 0.85 | 0.90 | false |
| lambda06 | 0.85 | 0.85 | false |
| lambda07 | 0.80 | 0.85 | false |
| lambda08 | 0.80 | 0.80 | false |
| lambda09 | 0.75 | 0.80 | false |
| lambda10 | 0.75 | 0.75 | false |
| lambda11 | 0.70 | 0.75 | false |
| lambda12 | 0.70 | 0.70 | false |
| lambda13 | 0.00 | 0.00 | true |

Decision precedence:

1. If `force_review_all`, return REVIEW for every input; log quality/shift flags separately.
2. If input invalid or any required score nonfinite, return REVIEW with reason.
3. If a frozen, enabled out-of-support rule flags the input/batch, return REJECT_OUT_OF_SUPPORT.
4. If `Q_topo > tau_topo OR Q_base > tau_base`, return REVIEW.
5. Otherwise, if `N_valid >= 1`, return ACCEPT_POSITIVE; else ACCEPT_NO_CRACK.

Equality at a threshold is accepted. `lambda13` is an explicit branch, not an ordinary `(0,0)` threshold test. The primary internal certification configuration has the statistical OOD rejection rule **disabled**; invalid-input review remains part of the policy. A separately enabled OOD filter creates a different acceptance function and cannot inherit the unfiltered certificate without recalibration or inclusion in the predeclared certified family.

Let `A_lambda=1` for either ACCEPT state and 0 for REVIEW/REJECT. Acceptance sets are nested as thresholds fall, but conditional risks need not be monotone. For example, removing 10 easy cases from a set of 20 cases with 2 errors raises the accepted error rate from 2/20 to 2/10. Filtering by uncertainty has no mathematical obligation to remove errors first.

### 8.5 Entropy and topology comparison policies

For the mandatory separately calibrated entropy controller, use 13 thresholds `tau_j=1-0.025*j` for j=0,…,12, ignore Q_topo, and keep the same masks, quality checks, sentinel, and two risk constraints. This family is defined now and not tuned to final test coverage. It receives its own labeled 95% family-wise certificate; **the main and entropy certificates are not jointly 95% across methods**. They are reported separately and never used to select a new “best” deployed system after calibration. A joint-across-method claim would require reallocating the budget over 26 policies (52 risk bounds) before calibration.

Topology-only, global-entropy, variance, and fixed-threshold baselines are empirical by default. Fixed-review-budget comparisons use the same frozen raw scores and deterministic score/ID tie handling. They do not get formal target fields unless separately preregistered and certified. Clearly distinguish entropy heuristic selection from entropy risk control in every table.

---

## 9. Exact selective risk-control procedure and proof

### 9.1 Population and estimands

Condition on all pre-calibration training/development decisions. Each eligible observation is the independent inspection unit fixed in Section 5. Let Y=1 mean an adjudicated positive mask and Y=0 a confirmed negative. For j in the 13 non-null policies:

\[
R_{miss}(j)=P(L_{miss}=1\mid A_j=1,Y=1),\qquad
R_{false}(j)=P(L_{false}=1\mid A_j=1,Y=0).
\]

These are risks **among automated cases in a true class**. They are not precision among predicted positives, false-discovery rate, risk conditional on a particular image, or per-site guarantees. Class membership is used for assessment/calibration only, not for inference decisions.

For class k and policy j define:

\[
n_{jk}=\sum_i\mathbf1[Y_i=k]A_j(X_i),\quad
e_{jk}=\sum_i\mathbf1[Y_i=k]A_j(X_i)L_k(X_i,Y_i),\quad
\hat R_{jk}=e_{jk}/n_{jk}\quad(n_{jk}>0).
\]

REVIEW and REJECT are excluded from these denominators, but included in total workload/coverage counts. Accepted no-crack output on a positive is fully included in miss risk. Accepted-positive output on a confirmed negative is fully included in false risk.

### 9.2 Simultaneous one-sided exact bounds

Primary targets remain `alpha_miss=0.10`, `alpha_false=0.05`, and `delta_total=0.05`. Let `K=13`, risks=2, and:

\[
\delta_{cell}=\frac{0.05}{2K}=\frac{0.05}{26}=0.0019230769230769232.
\]

For integer failure count e and accepted count n:

\[
U(e,n;d)=
\begin{cases}
1,&n=0\ \text{or}\ e=n,\\
\operatorname{BetaQuantile}(1-d;e+1,n-e),&0\le e<n.
\end{cases}
\]

For n=0 the internal bound is 1 for conservative computation; display the conditional risk and UCB as `N/A — no automated observations` and status `NOT_CERTIFIABLE`. Never show a conditional-risk estimate of zero. For n>0, compute the exact bound even when it cannot pass; distinguish `FAILS_TARGET` from a missing/invalid bound.

When e=0, use the numerically stable identity `U=-expm1(log(d)/n)`. Cross-check the beta quantile with an exact binomial-tail test: a target alpha passes iff `BinomCDF(e,n,alpha) <= d`, subject to floating-point boundary safeguards. No normal/Wald interval, ESS-adjusted binomial n, or bootstrap bound substitutes for this certification rule.

### 9.3 Why adaptive policy selection is valid here

This is the project-specific application of exact binomial inference and finite-family simultaneous coverage, supported by [R02–R03]. For each **fixed** j and k, conditional on n_jk accepted observations from IID class-k draws, their binary losses are IID Bernoulli with parameter R_jk. Thus the one-sided bound undercovers with probability at most delta_cell, also after averaging over random n_jk. Independence between different policies' error counts is unnecessary.

A union bound over 13×2 cells gives probability at least 0.95 that all non-null population risks with positive acceptance probability are simultaneously at most their UCBs. On that event, selecting any policy with both UCBs below their targets is valid, including selection by maximum calibration coverage. The score thresholds need not produce monotone risks. This directly resolves the conditional denominator; setting reviewed losses to zero and dividing by all applicable units would answer a different question.

Let S be the set of policies that pass both bounds. If S is nonempty choose maximum empirical overall automated coverage, tie-break by smallest numeric policy ID. If S is empty choose `lambda13`. The formal statement is:

\[
P\{\hat j=13\ \text{or}\ [R_{miss}(\hat j)\le0.10\ \land\ R_{false}(\hat j)\le0.05]\}\ge0.95.
\]

It is not a statement that the undefined conditional risk of review-all equals zero, nor a claim that conditional on successfully certifying the error probability of certification is 5%. The randomness in this statement is the fixed-sample calibration draw, with the trained system fixed.

### 9.4 Assumptions and limits

1. Independent and identically distributed certification observations within each class from the declared population; fixed class sample sizes are allowed.
2. Model, preprocessing, temperature, score definitions/CDFs, policy family, endpoint definitions, and quality/OOD rules frozen independently of calibration outcomes.
3. Accurate, complete adjudicated labels and reliable loss computation; no selective exclusion of failures.
4. Fixed-sample analysis with no outcome-triggered repeated looks or adaptive reserve expansion.
5. Future population class-conditionals match the calibration population for the claimed risks. External domains are not assumed to satisfy this.

No guarantee is made for arbitrary dependence, unseen acquisition shifts, all subgroups simultaneously, individual images, or human-review correctness. Family-wise correction protects policy search, not mistakes in labels or the population model.

### 9.5 Sample-size correction and feasibility table

For zero failures, the minimum **automated independent observations in the relevant class** is:

\[
n_{min}(\alpha,d)=\left\lceil\frac{\log d}{\log(1-\alpha)}\right\rceil.
\]

For the primary 13-policy procedure:

| Observed automated failures | Minimum accepted positives for U≤0.10 | Minimum accepted negatives for U≤0.05 |
|---:|---:|---:|
| 0 | 60 | 122 |
| 1 | 82 | 167 |
| 2 | 101 | 205 |
| 5 | 150 | 306 |

These values were numerically checked for this blueprint using the beta quantile and integer search; they are planning math, not results from crack data. Eighty accepted negatives with zero failures yield U≈0.07520, so the old 80-unit floor cannot certify 5% under this search.

Phase-02 hard feasibility floor for the primary configuration: at least **120 positive and 122 negative independent calibration observations before filtering**, preserving the original positive floor while correcting the negative impossibility. This is only a lower bound on available data. The actual selection gate requires enough accepted observations for both exact bounds to pass.

Recommended planning target: **300 positives and 300 confirmed negatives**, preferably more. At 50% class coverage, only 150 per class remain; even one negative failure may then prevent certification. Plan n using development-only anticipated class coverage and error rates, and publish a power/feasibility table for n, acceptance rate, and true error rate. Do not advertise 300 as a guarantee of useful coverage.

Certification units, not images/crops/pixels, count toward these numbers. SDNET2018's parent limitation may make the recommended plan impossible with current archives alone. Additional independently acquired negatives or a transparently weaker design may be necessary.

### 9.6 Fixed-sample reserve and low-data contingencies

Before calibration-error labels/metrics are read, use the data audit and development-only feasibility analysis to choose the total calibration N, any reserve allocation, and a fixed acquisition stopping rule based on counts/time—not certification outcomes. Freeze a single final manifest and run certification once.

After seeing a failed certificate, do **not** append reserve units and repeatedly re-run ordinary fixed-sample intervals until success. Valid alternatives are: (a) report no certified automation; (b) a new independent prospective experiment with a preallocated cross-attempt error budget; or (c) a separately reviewed time-uniform method [R20]. Options (b)/(c) are not part of the primary run.

If available independent negatives cannot reach 122, the primary family is blocked. Before any calibration outcome is inspected, supervisor-proposed low-data alternative S2 is to select **one** policy using development only, then certify its two risks with d=0.025 each. Zero failures then need 36 accepted positives and 72 accepted negatives. This is a different, smaller-search study, not a post-failure escape; it does not retrospectively rescue the 13-policy result. Retain the primary study's limitation in the report.

Sensitivity targets `alpha_miss∈{0.05,0.10,0.15}`, `alpha_false∈{0.02,0.05,0.10}` are interpreted using the same simultaneous UCBs for the same frozen policy family. Comparing multiple prespecified alpha values against that already simultaneous confidence surface does not itself introduce new risk parameters. It does not allow changing the scientific primary target or adding policies/models after calibration.

### 9.7 Selection/status pseudocode specification

For each lambda00–lambda12, calculate both n/e/U values. Status is `NOT_CERTIFIABLE` for zero accepted observations, invalid data, or insufficient theoretical minimum accepted count; still export any computable U. For valid sufficient counts, label each risk `PASS` if U≤alpha and `FAILS_TARGET` otherwise. A policy is jointly eligible only with PASS for both. `lambda13` is recorded separately as `REVIEW_ALL`, coverage 0, risks/UCBs null.

Output fields include `policy_id, risk_name, n_applicable, n_automated, failures, risk_hat, ucb, alpha, delta_cell, status, coverage_class, coverage_overall, review_rate, reject_rate, family_hash, certificate_scope`. For nonzero counts below the minimum, display the numerical U along with `NOT_CERTIFIABLE_INSUFFICIENT_N`; do not hide why it fails.

### 9.8 Independent test is an evaluation, not the calibration guarantee

Freeze selected policy JSON and all its dependency hashes before reading internal-test predictions with labels. Report empirical risk, accepted n, failure count, two-sided exact 95% CI, and a separately labeled `empirical_above_target` flag. A finite test estimate can exceed alpha even when the population risk is below alpha; a favorable estimate cannot prove assumptions or establish a 95% certificate by itself.

The calibration UCB is not a confidence interval calculated from test data. If a formal simultaneous two-risk test confidence statement is desired, use prespecified adjusted one-sided test intervals and label the distinct confidence budget. Primary reporting uses ordinary descriptive test intervals and no claim of joint coverage across domains/models.

If lambda13 is selected, plot coverage=0 as an annotated review-all marker with risk undefined. Never connect it to an invented risk=0 point or integrate it as a genuine selective-risk observation. Unconditional base metrics and all workload counts still appear.

---

## 10. Domain shift and weighted analysis

### 10.1 Three evidence levels

| Level | Analysis | Permitted conclusion |
|---|---|---|
| I | Internal reference population, Section-9 assumptions | High-probability two-risk certification for the declared frozen system |
| II | External source, hard negatives, field/corruptions, estimated density ratios | Empirical robustness/weighted estimates; no inherited guarantee |
| III | Correct known/bounded weights or rigorously bounded estimation error, stable conditional labels, support, independent fitting, valid conditional-risk proof | Explicit theorem-qualified target-risk statement for that particular setting |

Phase 07 must execute Level-II analysis for the Q1 track even if diagnostics fail. Level III is optional and separately gated. This replaces the invalid implication “ESS/AUC pass → weighted guarantee.”

### 10.2 Shift diagnostics and inference actions

Extract frozen encoder embeddings with a defined pooling layer and normalization. Fit standardized logistic regression on separate source/target-unlabeled groups, with a fixed regularization grid and group-cross-validated assessment. Source samples must represent the source distribution whose density ratio is being estimated, not an undocumented artificial class mixture. Record domain sampling priors pi_S, pi_T.

With q(x)=P(domain=T|embedding(x)):

\[
\hat w(x)=\frac{q(x)}{1-q(x)}\frac{\pi_S}{\pi_T},\qquad
ESS=\frac{(\sum_i\hat w_i)^2}{\sum_i\hat w_i^2}.
\]

Use out-of-fold domain predictions for diagnostic AUC; freeze the final fitted classifier before applying it to calibration/test covariates. Keep target test groups separate from target-unlabeled fitting. Cross-fitting does not solve misspecification, feature information loss, or concept shift.

Retain original heuristic warning thresholds `ESS/n >=0.30` and cross-validated domain AUC≤0.85. Report uncertainty for AUC and avoid treating a point estimate at the threshold as proof. Compute ESS overall and **within each accepted true-class subset**, plus maximum, median, p95, coefficient of variation, raw/normalized weight summaries, and clipped fraction. A weak domain classifier can have AUC≈0.5 despite severe undetected shift; global ESS can hide poor overlap in accepted negatives.

An optional input-level OOD score uses distance to a fixed training-embedding reference, standardized on development, with a prespecified 99th-development-percentile cutoff. This is a heuristic OOD flag, not a support test. Batch ESS/AUC failure can trigger a predeclared batch-wide review/reject recommendation; it does not identify exactly which image is out of support. `REJECT_OUT_OF_SUPPORT` is an operational label meaning “outside the validated operating domain according to this heuristic,” not a mathematically proven statement.

Internal primary certification leaves this extra filter disabled. Report separately the frozen-policy transfer and the OOD-filtered variant because filtering changes the conditional accepted population and can even increase its error risk.

### 10.3 Estimated-weight empirical experiment

For a fixed policy and class k:

\[
\hat R^w_k(j)=\frac{\sum_{i:Y_i=k}\hat w_i A_j(X_i)L_k(X_i,Y_i)}{\sum_{i:Y_i=k}\hat w_i A_j(X_i)}.
\]

A zero denominator is `NOT_ESTIMABLE`. Do not replace n by ESS in a Clopper–Pearson calculation: fractional weighted events are not binomial trials. Use group-bootstrap uncertainty as **empirical** uncertainty only; it does not repair density-ratio bias.

Primary empirical analysis uses raw estimated weights, with numerical probability clipping `[1e-6,1-1e-6]` flagged and reported. Fixed upper clipping at 5, 10, and 20 is supplementary, describing changed weighting targets/bias rather than restoring validity. Do not pick clipping from target-label results.

Compare unweighted and weighted empirical calibration-risk estimates against independently observed target risks for every frozen policy. A heuristic weighted selector may maximize calibration weighted coverage subject to weighted empirical risks≤targets, but receives `EMPIRICAL_ONLY`, no certification flag, and an honest comparison showing optimistic selection risk. If diagnostics fail, keep all results and mark `DIAGNOSTIC_NO_GO`; recommend review/reject without claiming successful risk control.

### 10.4 A valid known-weight optional construction

This project-specific conservative derivation makes the mathematical distinction explicit; it is not a claim that real-domain weights are known. Let source P and target Q satisfy Q(Y|X)=P(Y|X), Q_X absolutely continuous with respect to P_X, and known `w(X)=dQ_X/dP_X` with a fixed finite bound `0<=w<=W`. Use the natural source distribution P as reference, even if calibration class counts are selected separately.

For class k, under P(X|Y=k), define `Z_jk=w*A_j*L_k` and `V_jk=w*A_j`. Their expectation ratio equals the target conditional automated risk because the class-prior normalizing constant cancels. For n_k independent class-k calibration observations, both variables lie in [0,W]. For K fixed policies and a separate shift-family budget delta_shift=0.05, set:

\[
\epsilon_k=W\sqrt{\frac{\log(4K/\delta_{shift})}{2n_k}},\qquad
U^Q_{jk}=\min\left(1,\frac{\bar Z_{jk}+\epsilon_k}{\bar V_{jk}-\epsilon_k}\right)
\]

only when the denominator lower bound is positive; otherwise set internal U=1 and status `NOT_CERTIFIABLE`. Two one-sided Hoeffding deviations per policy/class and a union bound over 4K events justify simultaneous ratio bounds. This is conservative, may be vacuous, and does not require monotone selective risk. [R17] motivates comparison with sharper weighted methods, but this exact ratio derivation must not be described as that paper's unchanged algorithm.

Known bounds must hold over the source support; the maximum observed weight is not a known global W. Clipping unknown larger weights changes the estimand. For estimated weights, one would need an additional valid uniform estimation-error bound (and its error budget) or an appropriate proven alternative, with independent estimator fitting. Passing diagnostics does not supply such a bound. Density ratios in a compressed embedding equal full-input ratios only with an additional sufficiency condition; otherwise even known embedding ratios need not reweight loss correctly.

An inexpensive Q1 theory check can use a fully specified synthetic covariate-shift population with known bounded w and Bernoulli failure mechanisms. Evaluate repeated calibration draws against analytically known risks to check implementation and conservativeness. This is a simulation validation, not field robustness evidence. It is optional, never a substitute for mandatory real external testing.

---

## 11. Evaluation, comparisons, ablations, and statistics

### 11.1 Required comparison tracks

| Track | Systems | Data / fairness rule |
|---|---|---|
| Backbone quality | Three clean candidate engines, individual seeds and ensembles | Same audited splits, resolution, budget, metric implementation; distinguish common-loss and recovered-recipe rows |
| Heuristic selective prediction | Fixed threshold, entropy, global entropy, variance, topology only, joint score | Same frozen primary ensemble and operational masks; matched review workloads |
| Risk control | Joint topology+entropy controller; entropy-only controller with separate certificate | Same calibration observations, two endpoints, number of non-null candidates, confidence level, and independent test |
| Closest literature | SelectSeg inference component and Gupta comparator if feasible | Name adaptations precisely; never compare incompatible published numbers as if rerun |
| Shift | Frozen in-domain policy, empirical weighted policy, OOD-filtered variant | Separate target unlabeled fitting and labeled testing; guarantee scope explicit |

For a joint-score ranking outside the certified family use `max(Q_topo,Q_base)`; entropy-only uses Q_base. This fixed ranking is for workloads/AURC, not the paired policy staircase. Ties use a seeded sample-ID hash fixed before test; no label-dependent tie handling.

At review fraction b, review the top `ceil(b*N)` scores, report actual fraction, and compute failure capture = reviewed base failures / all base failures. Report positive and negative failure capture separately; a zero failure denominator is `N/A`. These are retrospective workload curves, not new certified operating points chosen from test labels.

### 11.2 Metric accounting

Dice=`2TP/(2TP+FP+FN)` and IoU=`TP/(TP+FP+FN)` are calculated per image over valid pixels, then macro-averaged at the declared inspection unit. Report micro pixel aggregates only as a separate table. Precision/recall and image-level detection metrics have separate labels and denominators. Do not mix image-level detection F1 with segmentation Dice.

For clDice define `Tprec=|S_pred intersect GT|/|S_pred|`, `Tsens=|S_GT intersect prediction|/|S_GT|`, and `clDice=2*Tprec*Tsens/(Tprec+Tsens)` when both denominators and sum are positive. Positive GT plus empty prediction gives 0; negative GT is excluded from crack-only clDice. Declare both-empty as `N/A` for topology, even when descriptive all-image Dice is 1. Boundary IoU uses mask boundary bands of width 2 evaluation-grid pixels for both GT and prediction, intersection divided by union; test that band generation and border handling match the definition. It is secondary, not another tuned tolerance.

Report image/group counts and pixel counts, before/after component filtering, by source/domain and class. Accepted-case metrics must always accompany unconditional base metrics, coverage, review, and rejects. Score quality includes AUROC/AUPRC for the exact branch-preservation event on positives, and false-component event on negatives. If either event class is absent, those discrimination metrics are `N/A` with counts.

AURC uses cumulative failure fractions after sorting least uncertain first. Use normalized trapezoidal integration over observed positive coverage values, report the coverage interval, and never fabricate a risk value at coverage zero. Primary AURC is class-specific; an overall combined event uses a clearly stated class mixture. AURC is descriptive and does not certify a policy.

### 11.3 Statistics

- Freeze a statistical analysis plan before test evaluation: primary contrasts, units, domains, bootstrap seed, replication count, multiplicity, missingness, and plot/table outputs.
- Use 2,000 paired bootstrap replicates by highest plausible independent group for descriptive metric differences. Resample the same groups for both methods. For IID representative units, this reduces to unit bootstrap; for supplemental multi-image analyses, resample groups and retain their images.
- Report mean/SD across individual training seeds separately from uncertainty across test units. Three models inside one ensemble are not three independent ensemble experiments. No seed×image pseudoreplication.
- With very few independent sites, bootstrap confidence intervals are unstable; publish site-level results and leave-one-site-out sensitivity without claiming that more resampling fixes limited diversity.
- Primary H3 AUROC contrast and H5 coverage contrast form a family of two planned empirical superiority tests; use Holm adjustment if reporting p-values. Include paired CI and effect size; do not interpret an unadjusted CI as an adjusted simultaneous claim. If a confirmatory claim requires simultaneous intervals, use Bonferroni 97.5% intervals for these two contrasts.
- McNemar is restricted to independent paired binary outcomes on the same units; class-specific conditional automated denominators differ between policies, so McNemar on selectively filtered subsets is generally inappropriate. Use paired group bootstrap for those risk/coverage differences.
- Calibration confidence budget, inferential comparison multiplicity, and exploratory subgroup reporting are separate; a corrected p-value does not create a risk certificate.

### 11.4 Ablation contract

Preregister the complete list in Phase 05, compute frozen variants in Phases 06–07, and assemble in Phase 08. Mandatory controller ablations reuse cached outputs: joint scores → entropy only; joint scores → topology only; exact control → workload-matched heuristic; component filtering on/off **evaluated against the same primary failure endpoint**; no review; OOD filtering on/off externally. Disabling a risk constraint is an explicitly uncertified diagnostic of what the constraint protects, never a valid two-risk controller.

Changing the endpoint (e.g., dropping branch preservation or the false-structure definition) is a sensitivity analysis about the question, not evidence that a method improves the original target. Postprocessor changes also change L and predictions and cannot inherit the primary certificate. Geometry/radius/area/length sensitivities use `r={2,4,6,8}`, area `{10,20,30}`, skeleton pixels `{3,5,10}`; the primary settings remain unchanged.

Do not retrain extra architectures for score-only ablations. No calibration/test-driven choice among ablations becomes a new primary model. A genuinely new model after seeing test results needs a new untouched evaluation population.

### 11.5 Field/corruption and failure taxonomy

Route B uses deterministic non-geometric corruptions on frozen external/internal-test base images: brightness factors `{0.7,1.0,1.3}`, contrast `{0.7,1.0,1.3}`, Gaussian noise SD `{0.01,0.03,0.05}` on [0,1] intensities, Gaussian blur sigma `{0.5,1.0,2.0}`, JPEG quality `{90,60,30}`. Apply one corruption at a time plus clean baseline; fix order, library implementation, RGB conversion, clipping, and noise seeds. Masks remain unchanged. These are proposed controlled stress levels, not a claim of exhaustive real-weather realism. Each variant retains its original group ID; variants never increase independent n.

Taxonomy schema: `failure_id, sample_id, unit_id, domain, true_class, category, accepted_or_reviewed, policy_id, raw_scores, score_ranks, severity_for_model, reviewer, notes`. False-negative categories: hairline, low contrast, shadowed, overexposed, border, occluded, branching, dense network, short crack, textured background. Topology categories: break, missed/spurious branch, split, merge, bridge, endpoint displacement, junction error. Use the Section-5 negative categories.

Tag every hard-negative false positive; all major accepted false negatives; and a fixed random stratified sample of reviewed failures (proposed up to 100 per outcome/domain, with all if fewer). This prevents subjective cherry-picking of attractive failure figures. Human-review capture is measured; human correction accuracy/time requires a separate study and is not assumed.

---

## 12. Artifact contracts and notebook execution

### 12.1 Roots and packages

Raw input mount remains `/kaggle/input/wall-crack-cp-datasets/`. Per-run output root:

`/kaggle/working/cracksafe_cp/phaseXX/run_<UTC>_<config_hash8>/`.

Every phase publishes an immutable small control bundle `CrackSAFE_CP_v3.3_phaseXX_control_<run_id>.zip`, a `phaseXX_manifest.json`, and a `NEXT_PHASE_INPUTS.md`. Large data shards, prediction shards, and checkpoints are separate named artifacts registered by hash; do not duplicate all raw archives in every bundle. Actual Kaggle mounted dataset slugs differ from filenames: export `artifact_catalog.json` with configurable mount-to-logical-path resolution, not guessed mount paths.

Shared reusable code is a versioned `cracksafe_core.zip` (or wheel) containing the tested Python modules; it is an implementation artifact generated during the notebook project, not a ninth notebook. Each downstream notebook checks the code hash. Formula/config changes require an amendment and invalidation of dependent artifacts.

### 12.2 Common manifest schema

Every `phaseXX_manifest.json` has:

```json
{
  "schema_version": "1.0",
  "blueprint_version": "3.3",
  "blueprint_sha256": "computed_actual_hash",
  "phase": "XX",
  "run_id": "actual_run_id",
  "created_utc": "actual_timestamp",
  "status": "PASS_OR_BLOCKED_OR_COMPLETE_NEGATIVE",
  "scope": "MSC_OR_Q1",
  "config_sha256": "computed_actual_hash",
  "code_sha256": "computed_actual_hash",
  "git_commit": null,
  "seeds": [],
  "input_artifacts": [],
  "output_artifacts": [],
  "gate_results": [],
  "amendment_ids": [],
  "environment_file": "environment_snapshot.json",
  "access_log_file": "data_access_log.csv"
}
```

The sample values above are schema placeholders, never acceptable as real hashes or timestamps. Each artifact entry: `artifact_id, relative_path, sha256, byte_size, media_type, schema_version, producing_run_id, required_by, privacy/license_status`. A manifest lists hashes of its payload files; its own hash is stored in a separate sidecar to avoid self-hash recursion. A ZIP sidecar hashes the final immutable ZIP. Record actual environment, CUDA/driver/GPU, package versions, CPU/RAM, start/end time, and exit status; use null when no Git commit exists rather than inventing one.

### 12.3 Required table schemas

| Artifact | Minimum columns |
|---|---|
| `sample_registry.parquet` | sample_id, source_id, archive/member path, decoded_hash, image_hash, mask_hash, parent_id, site/session IDs, split_group_id, certification_unit_id, role, class, mask_status, native/eval shape, license_status, legacy_exposure_status, exclusion_reason |
| Split CSVs | sample_id, unit_id, group_id, source_id, image_ref, mask_ref or sealed_label_ref, true_class for curator, selection_seed, role, split_version |
| `checkpoint_registry.csv` | engine_id, recipe_id, seed, checkpoint_ref, SHA256, train/development hashes, config/code/environment hashes, load_test_pass, pretraining_provenance |
| `prediction_index.parquet` | sample_id, unit_id, engine_id, member/ensemble ID, checkpoint hash, preproc/T/filter hash, prediction-shard reference, inference dtype, score-version hash, creation time |
| `unit_scores.parquet` | sample_id, unit_id, U_base, U_topo_policy, Q_base, Q_topo, topology_status, N_valid, quality_status, formula_version, transform_hash; **no GT needed** |
| `unit_losses.parquet` | sample_id, unit_id, true_class, LWBR, SCR, L_miss nullable, L_false nullable, annotation_version, metric_version |
| `policy_decisions.parquet` | sample_id, unit_id, policy_id, decision, automated, reason, policy/config hashes |
| `selected_policy.json` | family hash, chosen policy, targets, delta_cell, risk/count/UCB/status rows, calibration hash, code/model/preprocess/T/score hashes, claim population, confidence scope, selection timestamp |
| `decision_gates.csv` | gate_id, phase, requirement, evidence_ref, verifier, status, failure_action, signed_at, amendment_ref |
| `claims_ledger.csv` | claim_id, exact proposed wording, population, supporting output/table, assumptions, guarantee_status, limitations, reviewer_status |

Use null plus a reason for undefined values, not 0, empty strings, or nonstandard JSON NaN. Every table has unique keys and a documented schema version. Final losses and prediction-only scores are separate tables joined only by stable unit IDs.

### 12.4 Data-access barrier and resume contract

Each phase declares allowed split roles. Phases 01–05 cannot invoke a final-test evaluation function; Phase 06 calibration runs before an explicit policy-freeze marker enables internal-test evaluation; Phase 07 unlocks external labels only after target fitting is frozen. Accidental exposure is logged and its consequence assessed, not hidden by rerunning a notebook.

All expensive jobs are idempotent and keyed by input/config/code hashes. Resume only when they match. Atomic temporary write → checksum → rename prevents truncated checkpoints from appearing complete. Checkpoints preserve model, optimizer, scheduler, scaler, epoch, sampler/RNG state, best-score history, and manifest hashes. Export small gates/logs early, checkpoint at each epoch and before the session time buffer, and verify reattachment from a fresh session. Saving locally is not proof of persistence until a Kaggle version/output dataset has been committed.

---

## 13. Complete eight-phase specifications

Every phase below has an objective, inputs, activities, code components, outputs, dependencies, quality checks, exit gate, failure action, and explicit handoff. Every output list inherits the common manifest, checksums, environment snapshot, access log, control ZIP, artifact catalog, and `NEXT_PHASE_INPUTS.md` from Section 12.

### Phase 01 — Legacy, literature, and design locks

**Notebook:** `CrackSAFE_CP_Phase01_Legacy_Design_Literature_Locks.ipynb`

**Objective/scope:** establish what is known, feasible, and approved before data/model work; MSc and Q1 mandatory.

**Inputs:** this blueprint; raw archive directory; optional actual legacy train/validation CSVs, metrics, configs, and checkpoint references; evidence links; current Kaggle environment. Only the blueprint is required to generate the notebook in a later task; its runtime must explicitly request/locate actual data and report missing artifacts.

**Activities:** inventory archives without full extraction; hash blueprint/legacy records; quick lineage scan; verify recent literature and scope without repeating unrelated historical documents; write the Section-9 statistical specification; benchmark modern-model imports and one forward/backward/reload; record repository/license status; freeze three slots/fallbacks; choose actual field Route A/B; measure resource assumptions; list pending supervisor decisions and exposure restrictions. No full training.

**Code components:** configuration dataclass/schema; mount discovery; streaming SHA256; ZIP inventory/validation; filename-lineage scanner; reference registry loader; environment/profiling helper; exact-bound sample-size calculator; gate/manifest writer. Optional GPU smoke section is resumable separately from CPU inventory.

**Required outputs:** `legacy_manifest.json`, `legacy_hashes.sha256`, `legacy_baseline_record.md`, `missing_inputs.csv`, `preliminary_lineage_scan.csv`, `preliminary_lineage_report.md`, `literature_matrix.csv`, `novelty_gap.md`, `verified_references.bib`, `rcps_decision_D2.md` (actual exact-binomial/LTT-compatible procedure), `statistical_design.json`, `sample_size_feasibility.csv`, `modern_baseline_repro_check.md`, `model_roster.json`, `repository_registry.csv`, `resource_plan.csv`, `field_data_decision.md`, `decision_gates.csv`, `supervisor_decisions.md`, `phase01_manifest.json`.

**Dependencies:** none. **Checks:** historical values/populations not mixed; raw count expectations not asserted; all 14 primary policies enumerated; d=.05/26 matches formulas; missing licenses/legacy files explicit; field access not invented.

**Exit gate:** artifacts are complete; statistical implementation route specified; baseline slots/fallbacks and field route decided from evidence; unresolved approvals marked blocking for the relevant later stage. Missing legacy weights permit a documented historical-only baseline. Unresolved modern-slot permission blocks that slot and activates its declared fallback before training.

**Failure action:** produce a `BLOCKED` manifest with concrete missing input/action; do not manufacture a pass. Legal/technical fallback choices precede accuracy results. Phase-02 inventory can proceed when it does not depend on an unresolved later-model choice.

**Handoff to 02:** phase01 control ZIP, raw dataset mount, blueprint, roster, annotation/source audit requirements, independent-unit and sample-size design, field decision. No model checkpoint is required by Phase 02.

### Phase 02 — Data integrity, sampling, and annotation

**Notebook:** `CrackSAFE_CP_Phase02_Data_Leakage_Splits_Annotation.ipynb`

**Objective/scope:** create an auditable data and sampling foundation; MSc/Q1 mandatory.

**Inputs:** phase01 bundle and approved decisions; raw archives; legacy exposure metadata; actual reviewer annotations if available. **Activities:** verify image/mask pairing; stream deduplication; reconstruct parents; resolve source licenses; quarantine ambiguities; annotate using the pre-frozen manual; define internal/external population; create representative certification units and all split roles; allocate reserves before outcomes; assess calibration feasibility; package deduplicated data shards; seal final partitions.

**Code components:** safe ZIP reader/extractor; decoded-image hashing; candidate duplicate retrieval; group graph/union-find; image-mask validator; reproducible split/representative sampler; schema and group-disjointness validator; annotation import/adjudication checks; lightweight raw/operational-mask, skeleton, and clDice helper tests needed by Phase 03. Branch-risk modules are not yet applied to real results.

**Required outputs:** `dataset_registry.csv`, `sample_registry.parquet`, `archive_inventory.csv`, `exact_duplicates.csv`, `near_duplicates.csv`, `parent_lineage.csv`, `quarantine.csv`, `leakage_report.md`, `mrc_reuse_decision.json`, `legacy_exposure_registry.csv`, `annotation_manual_v1.md`, `annotation_audit.csv`, `reviewer_agreement.csv`, `hard_negative_spec.md`, `hard_negative_categories.yaml`, `population_contract.md`, `independence_assessment.md`, `certification_units.csv`, every Section-5 split CSV, `calibration_sampling_plan.json`, `split_hashes.sha256`, `data_card.md`, `data_shard_index.json`, `metric_primitives_test_report.json`, initial `cracksafe_core.zip`, `phase02_manifest.json`.

**Dependencies:** 01. **Checks:** no cross-role group/duplicate leakage; source holdouts exclude aggregation copies; test units not exposed to legacy models; positive/no-crack labels valid; selected representatives were label-blind; count groups separately from files; calibration ≥120 positive and ≥122 negative independent observations for primary-family feasibility; no test-derived reserve.

**Exit gate:** population and independence model acceptable; labels and source permissions adequate; hashes sealed; final fixed calibration size/reserve allocation chosen independently of outcomes; prerequisites to Phase-03 metric gate tested. A lack of enough independent units yields an explicit infeasibility result, even if file counts are large.

**Failure action:** quarantine/rebuild, recover lineage, acquire independent negatives, obtain actual annotations, or present S2 low-data design for approval **before** calibration outcomes. Do not borrow final hard negatives or call unlabeled background pixels negative images. If method can be developed while data collection continues, its status remains “development only; certification blocked.”

**Handoff to 03:** phase01+02 control bundles, data shards or raw archives with index, all non-test training/development manifests, code bundle, roster, common-protocol config. Keep final-test label material sealed.

### Phase 03 — Clean baselines and immutable ensemble

**Notebook:** `CrackSAFE_CP_Phase03_Legacy_Modern_Baselines.ipynb`

**Objective/scope:** select a credible frozen segmentation engine under a common protocol; MSc/Q1 mandatory.

**Inputs:** 01/02 control bundles, training/development images and masks, pinned upstream source/wheels/pretrained generic weights, approved training configs. **Activities:** smoke one batch, run three seeds per approved slot as resumable jobs, select each checkpoint on development-model, fit shared temperature per engine on development-probability, evaluate the base gate/engine ranking on development-policy and hard negatives, freeze selected three-member ensemble. Run optional extra seeds now when committed; do not change deployed M.

**Code components:** source-specific data adapters; common training/evaluation loop or faithfully wrapped upstream loop; deterministic seed handling; checkpoint/restart manager; ensemble inference; temperature fitter; operational-mask metrics; latency profiler; gate selector. A separate legacy-recipe run must have its cost/config explicitly registered.

**Required outputs:** `configs/`, `checkpoints/` in separate large artifacts, `checkpoint_registry.csv`, `per_seed_metrics/`, `training_history/`, `probability_calibration.json`, `baseline_summary.csv`, `topology_summary.csv`, `hard_negative_dev_summary.csv`, `efficiency_preliminary.csv`, `primary_engine_selection.json`, `primary_ensemble_manifest.json`, `ensemble_smoke_test.json`, `prediction_index.parquet`, `training_plan_frozen.json`, `phase03_manifest.json`.

**Dependencies:** 01/02. **Checks:** no calibration/test loading; three valid aligned members; identical preprocessing; all seeds retained; checkpoint exposure and hashes known; gate on ensemble matches ranking; recovered and common-loss recipes not conflated; resume/reload works.

**Exit gate:** one engine passes readiness gate; primary engine, three checkpoints, temperature, preprocessing, and valid-component filters are fixed; complete seed records and resource measurements exist.

**Failure action:** debug and apply declared technical fallback or approved development-only training amendment. If the gate remains unmet, report baseline infeasibility; do not calibrate an improvised replacement chosen from final results.

**Handoff to 04:** phase02/03 control bundles, selected three checkpoints, development images/masks and cached predictions, pinned inference code, temperature/filter/preprocessing config. Nonselected checkpoints remain archived for final backbone comparisons.

### Phase 04 — Structural metrics and ordinary uncertainty

**Notebook:** `CrackSAFE_CP_Phase04_Structural_Metrics_Uncertainty_Foundation.ipynb`

**Objective/scope:** make structural endpoints exact and tested before topology-score validation; MSc/Q1 mandatory.

**Inputs:** 02/03 bundles, selected ensemble, development data/predictions, annotation audit, early primitive tests. **Activities:** materialize formulas and formula-to-code registry first; implement graph/branch rules; run all synthetic edge cases before real metrics; lock r from annotation convention and record sensitivity; characterize LWBR event thresholds without silently relaxing them; compute standard entropy/variance/confidence; freeze failure taxonomy.

**Code components:** deterministic skeleton graph, branch pixel ownership, dilation/matching, LWBR/SCR and secondary metrics, exact operational mask, score aggregations, tests, plots, versioned feature cache. Phase-03 clDice/filter helpers are imported, not reimplemented incompatibly.

**Required outputs:** `method/formulas.md`, `method/formulas.tex`, `method/formula_to_code_registry.csv`, `tests/test_structural_metrics.py`, `tests/synthetic_expected_values.csv`, `synthetic_test_report.csv`, `skeleton_config.json`, `metric_contract.json`, `radius_sensitivity.csv` and PNG, `lwbr_event_threshold_sensitivity.csv` and PNG, `lwbr_threshold_amendment.md` only if required, `structural_metrics_dev.parquet`, `ordinary_uncertainty_dev.parquet`, `failure_taxonomy.yaml`, `failure_annotation_template.csv`, updated `cracksafe_core.zip`, `phase04_manifest.json`.

**Dependencies:** 02/03. **Checks:** empty predictions count as misses; positive one-pixel/loop cases remain eligible; no GT filtering excuses small cracks; exact threshold behavior; graph length accounting; high-LWBR/low-continuity counterexamples documented; uncertainty has no label input.

**Exit gate:** all synthetic tests pass; formulas/config/code agree; primary r and LWBR threshold frozen; annotation-driven amendments signed where required; ordinary scores ready; no final-data access.

**Failure action:** fix metric code and invalidate dependent development caches; if scientific endpoint changes are proposed, document before calibration. Do not work around a test failure by dropping difficult masks.

**Handoff to 05:** phase03/04 control bundles, selected ensemble or consistent cached development maps, metric code/tests, risk-definition candidates, raw ordinary scores, failure taxonomy, source/annotation manifest hashes.

### Phase 05 — Prediction-only topology and preregistration

**Notebook:** `CrackSAFE_CP_Phase05_Topology_Uncertainty_Risk_Preregistration.ipynb`

**Objective/scope:** freeze deployable scores, policies, comparisons, and analysis before certification; MSc/Q1 mandatory.

**Inputs:** 02–04 bundles, development-only ensemble predictions, optional comparator adapters. **Activities:** implement symmetric member-branch score; test all-empty and missing-branch scenarios; compare entropy and topology with GT joined only for evaluation; fit frozen midrank transforms; write main and entropy families; preregister endpoints, ablations, seeds, workloads, shift settings, statistics, calibration N, and access barrier; prepare exact-bound code and calibration simulations.

**Code components:** prediction-only `score_image(predictions, config)` function with no GT parameter; score serialization/CDF; policy evaluator; exact binomial bounds and selector; finite-sample numerical fixtures; no-GT integration test; deterministic workload ranking. Tests assert changing GT while keeping model predictions fixed does not change any score/decision.

**Required outputs:** `topology_uncertainty_definition.md`, `topology_uncertainty_dev.parquet`, `uncertainty_comparison.csv`, `failure_detection_metrics.csv`, `risk_definition_v1.md`, `percentile_transform.json`, `policy_family_v1.csv`, `entropy_policy_family_v1.csv`, `primary_endpoints_v1.md`, `statistical_analysis_plan.md`, `ablation_plan.csv`, `shift_analysis_plan.json`, `calibration_freeze.json`, `h3_development_report.md`, `tests/test_risk_control.py`, `statistical_verification_report.md`, `formula_to_code_registry.csv` update, `preregistration_bundle.sha256`, `phase05_manifest.json`.

**Dependencies:** 02–04. **Checks:** no calibration outcomes accessed; no GT in inference signatures; main family K=13; entropy certificate separately scoped; same primary endpoints for fair comparisons; all seeds/checkpoints frozen; alpha/delta and sample floors consistent; no risk=0 for sentinel.

**Exit gate:** 05→06 mathematical/code review by researcher and adviser/technical reviewer passes; independent-unit/sample plan accepted; fixed N locked; assumptions and exact selector match tests. Topology may lose to entropy on development and still proceed as an honest hypothesis test; it cannot be redesigned using final test data.

**Failure action:** remain in development; correct score/statistical implementation; document a negative development result. An approval or data shortage must appear as `BLOCKED`, not as a silently deferred condition.

**Handoff to 06:** phase02–05 controls, calibrated three-member engine or inference artifacts, frozen code/formulas/transforms, main/entropy policies, calibration data, sealed internal test, all approved preregistration and access hashes.

### Phase 06 — Exact risk control and independent internal test

**Notebook:** `CrackSAFE_CP_Phase06_RCPS_Selective_Internal_Test.ipynb`

**Objective/scope:** execute the core two-risk experiment once; MSc/Q1 mandatory.

**Inputs:** all frozen 02–05 artifacts; fixed calibration and untouched internal-test populations. **Activities:** verify gate/hashes; produce calibration predictions/scores/losses; calculate all 26 exact UCBs for the primary family and separately the entropy family; select or review-all; write immutable selection certificates; only then evaluate internal test and preregistered baselines/ablations. Export descriptive curves without selecting a new test-informed policy.

**Code components:** split access guard; deterministic inference/cache; scores/losses join validator; exact UCB/selection; certificate writer; one-time test runner; grouped descriptive statistics; plotting from table artifacts.

**Required outputs:** `calibration_unit_scores.parquet`, `calibration_unit_losses.parquet`, `rcps_calibration_results.csv`, `entropy_calibration_results.csv`, `selected_policy.json`, `entropy_selected_policy.json`, `calibration_certificate.md`, `internal_unit_scores.parquet`, `internal_unit_losses.parquet`, `policy_decisions.parquet`, `internal_test_results.csv`, `risk_coverage.csv`, `selective_baseline_comparison.csv`, `preregistered_ablation_internal.csv`, `internal_failures.csv`, `h3_h4_h5_decision_report.md`, `figures/`, `phase06_manifest.json`.

**Dependencies:** 02–05, especially mathematical sign-off. **Checks:** accepted denominators correct; every failure counted; exact bounds match independent binomial-tail calculation; n=0 and lambda13 handled; no reserve retry; calibration and test timestamps ordered; both methods use same loss/model data; confidence scopes labeled.

**Exit gate:** calibrated selection or documented review-all plus complete independent evaluation, with no post-hoc tuning. `COMPLETE_NEGATIVE` is legitimate if no automation certifies; it is not positive evidence of a useful controller. A positive operational result also needs meaningful coverage and clear advantage/limitation versus entropy.

**Failure action:** implementation errors invalidate affected outputs and require a documented rerun of unchanged analysis; method changes after seeing outcomes require a new prospective experiment. Data insufficiency produces the prespecified negative result, not a recycled test set.

**Handoff to 07:** phase03–06 controls, selected frozen policies and checkpoint artifacts, metric/uncertainty code, external and HN manifests, separate source/target-unlabeled pools, field/corruption and shift-analysis plan. Internal-test outcomes do not authorize changing the external method.

### Phase 07 — External, hard-negative, and shift evaluation

**Notebook:** `CrackSAFE_CP_Phase07_External_HardNegative_Shift_RCPS.ipynb`

**Objective/scope:** assess transfer and validity limits. MSc: external positives, final hard negatives, and committed field/corruption route. Q1: also execute empirical weighted analysis and document formal-extension eligibility.

**Inputs:** frozen 02–06 artifacts, independent external positive/HN data, chosen field/corruption manifest, source/target-unlabeled fitting pools. **Activities:** freeze domain classifier/diagnostics using unlabeled pools; run unmodified accepted-policy transfer; evaluate negatives by category; execute the chosen route; compare empirical weighting and separately labeled rejection variant; optionally run known-weight simulation; annotate failures after recording predictions.

**Code components:** frozen inference; corruption generator with linked group IDs; embedding extraction; group-CV logistic regression; density-ratio/ESS diagnostics; weighted ratio calculator; optional known-weight conservative bounds; failure annotation importer; per-domain tables.

**Required outputs:** `external_positive_results.csv`, `hard_negative_results.csv`, `hard_negative_category_summary.csv`, `field_or_corruption_results.csv`, `external_unit_scores.parquet`, `external_unit_losses.parquet`, `external_policy_decisions.parquet`, `shift_diagnostics.csv`, `domain_classifier_metrics.json`, `domain_model_artifact/`, `importance_weights.parquet`, `ess_report.json`, `weighted_empirical_results.csv`, `weighted_rcps_results.csv` (compatibility table with explicit `claim_status`, never a misleading certification name alone), `shift_go_nogo_decision.md`, `weighted_theory_eligibility.md`, `external_failures.csv`, `preregistered_ablation_external.csv`, optional `known_weight_simulation.csv`, `phase07_manifest.json`.

**Dependencies:** 02–06. **Checks:** source isolation; unlabeled/test disjointness; group rather than corruption-count N; category labels adjudicated; weights fit independently; no use of ESS as binomial n; empirical and theorem-qualified rows distinct; rejection does not inherit the old certificate.

**Exit gate:** all mandatory route components complete; weighted Q1 experiment either executed empirically or has documented data/diagnostic infeasibility; no unsupported guarantee under arbitrary shift. AUC/ESS failure is retained evidence. Optional Level-III failure does not block an honest Q1 study, but limits its claims.

**Failure action:** report degraded transfer, sparse categories, inadequate support, or failed assumptions. Do not delete target domains or relabel them “invalid” simply because performance is poor. New target-labeled recalibration is an optional separate experiment with new independent target test data.

**Handoff to 08:** phase01–07 control manifests, all final per-unit/seed/baseline/ablation tables, frozen prediction indexes, checkpoints needed for efficiency only, annotation/failure records, runtime logs, and claims ledger inputs.

### Phase 08 — Statistics, ablation assembly, and publication package

**Notebook:** `CrackSAFE_CP_Phase08_Final_Ablation_Statistics_Q1_Package.ipynb`

**Objective/scope:** synthesize reproducible evidence; MSc requires three-seed statistics and reproducibility; Q1 requires full planned analyses and submission assets.

**Inputs:** 01–07 immutable outputs, preregistered statistics/ablation plan, optional already frozen additional seed results. **Activities:** assemble all variants without new model selection; compute paired group intervals/effects and adjusted tests; summarize training variation separately; measure complete end-to-end efficiency; complete taxonomy; generate manuscript tables/figures directly from artifacts; produce model/data cards, reproducibility guide, and an optional inspection-support demo after scientific freeze.

**Code components:** validated joins; statistics/bootstrap/permutation scripts; table/figure generators; latency/memory benchmark; claims-to-evidence checker; artifact validator; minimal inference demo wrapper. No new training/tuning logic is introduced here to improve observed final outcomes.

**Required outputs:** `final_multiseed_results.csv`, `ensemble_result.json`, `final_ablation.csv`, `confidence_intervals.csv`, `statistical_tests.csv`, `efficiency.csv`, `failure_taxonomy_final.csv`, `claims_ledger.csv`, `paper_tables/`, `paper_figures/`, `supplement/`, `reproducibility/` containing requirements locks/environment/configs/split and checkpoint manifests/tests/scripts/CITATION.cff/license notices/README, optional `demo/`, `thesis_asset_manifest.csv`, `q1_asset_manifest.csv`, `limitations_and_negative_results.md`, `phase08_manifest.json`.

**Dependencies:** 01–07. **Checks:** every claim traces to population-specific outputs; historical rows separate; no resampling of crops as independent; no seed-count inflation; no fabricated risk value at zero coverage; all references/permissions current; downloadable artifacts reopen and hashes match.

**Exit gate:** conclusions, uncertainty, limitations, reproducibility assets, and three-seed evidence complete. Five seeds are encouraged if planned/feasible but not a substitute for independent samples. Q1 submission readiness is assessed against Section 16, never promised as acceptance.

**Failure action:** fix assembly/code bugs, disclose missing evidence, or delay a claim/submission. New scientific changes require a new study version and appropriate untouched evaluation; they cannot silently replace v3.3 results.

**Final handoff:** complete reproducibility package and thesis/manuscript assets. Demo outputs show image, probability, operational mask, components, scores, decision, reason, and certificate scope; no structural-safety verdict.

---

## 14. Compute, storage, and recovery plan

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

## 15. Decision gates and contingency register

| Gate | Evidence / verifier | Pass requirement | Failure action |
|---|---|---|---|
| G01 design and provenance | Phase-01 documents; researcher/adviser | Source records, statistical correction, roster/fallbacks, field route, actual missing inputs recorded | Resolve documents/permissions; do not invent approval |
| G02 independence and licensing | Audit, data card, curator | No unresolved cross-split lineage; eligible labels and independent-unit rationale | Quarantine/rebuild/acquire data |
| G03 sample feasibility | Sampling plan; script + adviser | ≥120 positive/≥122 negative independent calibration observations for primary plan; fixed N chosen before outcomes | Acquire units, approved development-first single-policy alternative, or certification blocked |
| G04 baseline readiness | Development metrics; script | At least one frozen engine passes IoU .56 / HN .35 heuristic gate | Debug, declared fallback, dated amendment, or negative feasibility |
| G05 metrics and observability | Synthetic/no-GT tests; technical reviewer | All edge cases and structural interpretations correct | Fix and invalidate caches |
| G06 preregistration | Hashes + access log; researcher | Scores/families/endpoints/models/N/statistics/shift plan frozen | Remain in development |
| G07 05→06 math/code agreement | Exact-bound tests and reviewed proof | 26 primary bounds, accepted denominators, no monotonicity assumption, valid sampler, sentinel and optional-stopping rules | Block final calibration until corrected |
| G08 internal experiment | Frozen certificate + results | Complete positive or negative result; no test tuning | Report no certification or invalidate contaminated result |
| G09 external/weighted claims | Source audit, diagnostics, claim ledger | Required external/HN/route tests; weighted evidence level labeled | Keep negative result; no unsupported guarantee |
| G10 reproducibility/publication | Final manifests; researcher/adviser | Every central claim reproducible and population-specific | Fix assets or narrow/delay claims |

| Contingency | Trigger | Required response |
|---|---|---|
| C1 major legacy leakage | Verified overlap q>10% | Full grouped reconstruction; historical claims restricted |
| C2 any lesser leakage | Any overlapping parent/duplicate | Quarantine affected groups and rebuild; never treat ≤10% leakage as acceptable |
| C3 too few calibration units | Corrected independent-unit floor or projected accepted N unavailable | Collect before final N freeze; S2 only before calibration outcomes; no test borrowing |
| C4 no passing UCB | Both-risk selection set empty | lambda13; report why; no repeated fixed-sample enlargement |
| C5 H3 unsupported | Topology fails to improve on entropy | Report negative result and shared-empty/shared-hallucination failures; retain controller contribution only to extent supported |
| C6 H5/utility weak | Excess review or low coverage in one class | Report class coverage and limits; do not claim practical automation from global averages |
| C7 estimated-weight diagnostics fail | ESS/AUC warning or extreme weights | Empirical/no-go result; review/reject recommendation; do not claim theorem validity |
| C8 modern model fails build/permission | Phase-01 reproducibility gate | Predeclared fallback before training; no accuracy-driven replacement |
| C9 no field access | No secured plan by Phase-01 exit | Route B with external/HN/corruption tests |
| C10 test exposure or post-freeze method change | Access log or hash mismatch | Quarantine affected claim; retain original experiment; new independent evaluation for revised method |
| C11 OOM/session/storage failure | Resource checks | Smaller microbatch/accumulation, resumed identical job, data sharding; record changes; no silent image-resolution change |
| C12 sparse/ambiguous annotations | Uncertain GT/no-crack status | Adjudicate or predeclared challenge subset; no fabricated masks/reviewer sign-off |

---

## 16. MSc versus Q1 scope and manuscript requirements

### 16.1 Essential MSc track

Complete all eight phases at their core scope: data/lineage/licenses; reproducible clean baselines; three-member ensemble; exact structural metrics; prediction-only scores; main and entropy two-risk procedures; independent internal evaluation; source-held-out positives and hard negatives; committed field/corruption route; three-seed descriptive variability; grouped uncertainty intervals; efficiency and reproducibility. A documented failure to certify is scientifically legitimate, though it narrows the positive contribution.

Do not remove the entropy-controller comparator, independence audit, or test separation to save compute. Reduce optional model retraining, high-resolution figures, demo complexity, or extra seeds first.

### 16.2 Additional Q1 evidence

- Strong closest-method positioning, refreshed near submission; faithful feasible comparator or transparent availability limitation.
- Preregistered controller ablations and meaningful class/domain coverage.
- Category-aware expert-adjudicated negative benchmark; describe any limited sample diversity.
- Completed empirical shift-weighting analysis, with negative results and theory boundary; a formal real-domain weighted guarantee is **not** mandatory or presumed.
- Five individual-model seeds where committed and affordable; three honest seeds may remain with limitations. Do not fabricate five independent ensembles.
- Paired group inference, end-to-end CPU/GPU cost, reproducible tables/figures, and clearly delimited engineering claims.
- Field evidence is valuable when secured, but a strong predeclared corruption/external route is permitted; it does not establish field safety.

### 16.3 Optional extensions, not silently added to core

Known-weight simulation or theorem-qualified weighted controller; new independently labeled target recalibration with its own target test; full SelectSeg noisy-label training; Gupta structural comparator if its dependency/permission budget supports it; 5-member ensemble as a separately calibrated study; native-resolution tiling; prospective human-review workload/correction study. Each needs its own preregistration/amendment and resources.

Excluded: structural severity/capacity/safety diagnosis, drone/LiDAR acquisition systems, a new backbone/foundation model, full UDA-method invention, LLM integration, enterprise/mobile product engineering. Demo is a small final wrapper only.

### 16.4 Publication story and required assets

Story: pixel overlap is insufficient → define observable engineering-oriented failure proxies → audit independence and negative cases → freeze a capable segmenter → compare ordinary and structural uncertainty fairly → certify selected automated class risks with explicit limitations → expose failure under external shift.

Required tables: source/lineage and independent counts; literature gap; clean backbone metrics; uncertainty detection; calibration certificate with n/e/U and delta_cell; independent-test risk/coverage with intervals; entropy-controlled comparison; hard-negative categories; domain/shift diagnostics; fixed-workload capture; ablations; seed and efficiency results. Historical MRC gets its own population-labeled table.

Required figures: data/phase flow; method flow distinguishing prediction-only and GT evaluation paths; representative synthetic counterexamples; risk–coverage and workload curves; per-domain/categorical risks and coverage; selected real failures with sampling rule; resource/latency breakdown. A figure claiming uncertainty improvement must include all-empty failures and not only images with predicted branches.

Candidate venues remain Reliability Engineering & System Safety, Automation in Construction, Computer-Aided Civil and Infrastructure Engineering, Advanced Engineering Informatics, and Engineering Applications of Artificial Intelligence. These are thematic candidates, not verified current-quartile rankings or acceptance recommendations. Check current scope/indexing/quartiles and submission rules when selecting a journal; no Q1 acceptance is promised.

Allowed wording: “two-risk certification under the stated IID class-conditional sampling assumptions”; “selective inspection support”; “branch-preservation proxy”; “external stress test”; “empirical importance-weighted comparison.” Prohibited without stronger evidence: “guaranteed under arbitrary shift,” “safe structure,” “all topology errors controlled,” “domain invariant,” “first-ever,” “state of the art,” or “human review eliminates all errors.”

---

## 17. Detailed v3.2 → v3.3 change register

Classification: **A** critical correction; **B** high-value scientific improvement; **C** implementation improvement; **D** optional extension. “Required” refers to implementing the corrected blueprint; it does not pretend that proposed supervisor decisions have already been approved. Effort is incremental relative to v3.2 and is qualitative unless explicitly measured. Project-specific mathematical deductions/design choices are labeled **Derivation/design**, not falsely attributed to a paper.

| ID / class | Area | Previous Design | New Design | Added/Modified/Removed | Reason / supporting evidence | Expected benefit | Additional effort | Affected Phase | Requirement |
|---|---|---|---|---|---|---|---|---|---|
| V01 A | Statistical foundation | Generic Bates RCPS/UCB attribution for conditional selective risks | Exact binomial simultaneous bounds, LTT-compatible finite-family proof | REPLACE | Changing denominators break the claimed monotonicity shortcut; [R01–R03], Section 9 derivation | Valid stated estimand | Low coding; statistical review | 01,05,06 | Mandatory; S1 review |
| V02 A | Search multiplicity | delta=.025 per risk while searching 13 policies | delta_cell=.05/26 across policy×risk cells | MODIFY | Union-bound protection for adaptive highest-coverage selection; [R02–R03] | Honest simultaneous confidence | Negligible compute; larger data need | 01,02,05,06 | Mandatory |
| V03 A | Calibration floor | 120 positives / 80 negatives before filtering | 120/122 hard feasibility floor; exact accepted-count gate; 300/300 planning target | REPLACE | Numerical exact-bound calculation; 80 zero-error negatives give U≈.0752 | Avoid impossible 5% claims | Potentially substantial independent-negative collection | 01,02,06 | Mandatory; S2 feasibility |
| V04 A | Reserve pool | Expand when UCB is vacuous, then rerun | Allocate before outcomes; one fixed N; new prospective/error-budgeted study for later retries | MODIFY | Fixed-sample inference is not anytime-valid [R20]; design derivation | Avoid optional-stopping bias | Low coding; may require new data | 02,05,06 | Mandatory |
| V05 A | Independent unit | Site/parent wording but image/group counting ambiguous | One prespecified representative per independent group; separate grouping and statistical units | REPLACE | Binomial sampling requirement; SDNET parent/crop structure [R21] | Prevent pseudoreplication | Medium audit; may reduce feasible N | 02,06,07,08 | Mandatory; S2 review |
| V06 A | Deployment topology | GT/consensus branch ambiguity and GT-dependent missingness | Symmetric prediction-only leave-one-member-out branch disagreement | REPLACE | GT unavailable in deployment; structural uncertainty prior art [R05]; project design | Executable inference without leakage | Medium graph/testing work; no retraining | 04,05 | Mandatory; S3 review |
| V07 A | Empty predictions | Evaluation NA rules could omit failure-scoring cases | All-empty prediction score 0 with flag; all positive failures stay in H3/risk analysis | MODIFY | Agreement is observable; correctness is not; design | Avoid survivor bias and forced-certainty interpretations | Low | 04–07 | Mandatory |
| V08 A | Shift guarantee | ESS≥.3n and AUC≤.85 lead toward weighted claim | Diagnostics only; empirical weighting default; separate sufficient-assumption gate | REPLACE | [R16–R18]; bounded/accurate ratios and stable conditionals required | Defensible robustness conclusions | Low additional compute; more precise reporting | 01,07,08 | Mandatory; S4 review |
| V09 A | Weighted bound | Weighted risk/UCB not fully specified | No ESS-as-binomial n; explicit conditional weighted ratio; optional known-weight ratio UCB | MODIFY | Section-10 derivation; [R17] | Prevent invalid weighted certification | Low core; optional simulation | 05,07 | Mandatory separation; optional formal extension |
| V10 A | LWBR meaning | 0.90 described as at most 10% branch length missed | Preserve branch-preservation endpoint, correct interpretation, require SCR/gap/merge evidence | MODIFY | Counterexample in Section 7; [R13] supports complementary geometry | Claim matches measured failure | Low CPU | 04–08 | Mandatory |
| V11 B | Tolerance | r=2*w_min described as principled | r=4 inherited convention plus annotation audit and fixed radius sensitivity | MODIFY | Width does not establish registration tolerance; design | Avoid unsupported metric justification | Low annotation review | 02,04 | Mandatory documentation; S3 changes only |
| V12 A | GT small objects | Short-component filtering ambiguously shared with GT | Operational filtering for predictions only; all adjudicated GT positives retained | MODIFY | Prevent evaluation endpoint deleting real misses; design | Honest thin/small-crack accounting | Low | 02,04,06 | Mandatory |
| V13 C | Graph edge cases | Endpoints/junctions/loops listed but algorithm incomplete | Deterministic pixel graph, junction compression, loop/singleton and ownership rules | ADD | Implementation determinism; design | Reproducible branch counts/lengths | Medium CPU/testing | 04 | Mandatory |
| V14 B | Ordinary uncertainty | Predictive entropy fixed, image aggregation left open | Top-decile mean frozen; global entropy secondary | MODIFY | Sparse-crack background dilution; explicit project design | Testable scalar on every image | Negligible compute | 04,05 | Mandatory proposed default; S3 review |
| V15 A | Temperature | Historical operating settings inherited; new engine probability scaling ambiguous | Fit shared engine T on development-probability; legacy T only for historical replay | MODIFY | Different models have different logits; [R12] context, design | Coherent probabilities and frozen inference | Low CPU/inference | 03 | Mandatory |
| V16 B | Statistical comparator | Formal controller compared mainly with heuristic entropy | Add same-engine separately risk-calibrated entropy family | ADD | Isolate topology benefit from ordinary statistical calibration; [R02,R06] | Stronger novelty test without another backbone | Low CPU; no extra training | 05,06,08 | Mandatory |
| V17 A | Cross-method confidence | No explicit budget for multiple controllers | Separate certificates and confidence scopes; joint method claim requires 52 bounds | ADD | Simultaneous-inference accounting; derivation | Prevent inflated multi-system guarantee | Negligible | 05,06,08 | Mandatory |
| V18 A | Review-all / no denominator | lambda13 and NOT_CERTIFIABLE already added | Preserve; distinguish undefined risk, insufficient n, failed target; formal abstain-or-control statement | KEEP + CLARIFY | Correct zero denominator semantics [R02] | Faithful negative result | Low | 05,06 | Mandatory |
| V19 A | Test interpretation | Test target “violation” could imply theorem failure | Separate empirical exceedance, test CI, population guarantee, and assumption validity | MODIFY | Finite-test variation; derivation | Avoid false proof/refutation | Low | 06–08 | Mandatory |
| V20 A | OOD rejection | Reject action not fully defined or certificate-scoped | Primary OOD disabled; explicit optional heuristic; filtered system distinct | MODIFY | Filtering changes conditional risk | No inherited unsupported certificate | Low/medium embedding work | 05,07 | Mandatory separation |
| V21 A | Ensemble lifecycle | Five-seed final confirmation in Phase 08 ambiguous | Freeze deployed M=3; extra individual seeds planned early; no post-test expansion | MODIFY | New ensemble changes selected system | Preserve calibration independence | Lower unexpected retraining cost | 03,05,08 | Mandatory |
| V22 B | Novelty | Broad topology/selective/controller gap | Narrow claim against SelectSeg, Gupta, TopoSAM, CrackGeoFM, weighted LTT | MODIFY | Verified 2024–2026 and foundational sources [R05–R19] | More defensible contribution | Medium literature/analysis | 01,05,08 | Mandatory |
| V23 C | Model roster | Three main architectures plus fallbacks | Preserve bounded roster; DMSRCrack permission caveat; technical fallback before accuracy | KEEP + CLARIFY | Official repositories [R07–R08]; no license assumed | Feasible, transparent comparison | Phase-01 smoke effort | 01,03 | Mandatory; S5 freeze |
| V24 B | Training fairness | Common training details under-specified | Common-loss track, separate recovered MRC recipe, limited tuning budget and fixed resolution | ADD | Separate architecture, loss, and legacy effects; design | Interpretable baselines | Possible extra recipe jobs if chosen | 01,03 | Mandatory protocol; S5 approval |
| V25 A | Historical MRC | Canonical two populations separated | Preserve all numbers, mark unverified records, add exposure-aware clean-retrain identities | KEEP + MODIFY | Source blueprint provenance; no new artifact verification | Prevent optimistic legacy/test mixing | Medium audit | 01–03,08 | Mandatory |
| V26 A | Source/dataset leakage | Grouped split/duplicate checks | Add decoded hashes, aggregation source identities, unknown lineage restrictions, legacy exposure | MODIFY | Same originals can occur in several archives | Stronger independent evaluation | Medium data work | 01,02 | Mandatory |
| V27 A | SDNET and labels | Hard negatives and rare negatives recognized | Positive classification labels cannot become masks; negatives require adjudication | CLARIFY | Original SDNET task/provenance [R21] | Valid endpoint labels | Annotation effort | 02,07 | Mandatory |
| V28 B | Hard-negative curation | Categories + expert review + metadata | Preserve plus label-blind final membership, separate mined challenge set, double-review rule | MODIFY | Prevent final-model failure selection bias | Credible benchmark and annotation audit | Moderate human review | 02,07 | Mandatory; S6 staffing |
| V29 A | Primary endpoints | Worst-domain accepted Dice co-primary | Certification/coverage primary; unconditional and accepted metrics plus class coverage secondary | MODIFY | Accepted Dice can be inflated by selective exclusion | Honest utility assessment | Low | 05–08 | Mandatory; S7 utility approval |
| V30 B | Hypothesis definitions | H3 strongest baseline vs entropy inconsistent | Entropy precommitted; independent-test H3; paired contrasts and negative results | MODIFY | Prevent comparator cherry-picking | Clear falsifiable test | Low statistics | 05,06,08 | Mandatory |
| V31 A | Ablation timing | Ablations designed/run late | Preregister in 05, evaluate frozen variants in 06/07, assemble in 08 | MODIFY | Prevent test-driven method selection | Reproducible causal comparisons | Usually lower compute via caches | 05–08 | Mandatory |
| V32 C | Phase dependency | Formulas later than some metric use; handoffs broad | Early tested metric primitives, full structural contract in 04, explicit ten-part phase specs | MODIFY | Remove lifecycle/circular dependencies | Implementable eight-notebook pipeline | Low/medium scaffolding | 01–08 | Mandatory |
| V33 C | Artifact management | ZIP/manifests mentioned generically | Schemas, stable IDs, separate score/loss tables, hashes, code bundle, mount catalog | ADD | Precise downstream contracts | Reliable restarts and audit | Medium one-time code | 01–08 | Mandatory |
| V34 C | Resource plan | Broad 62–180h initial estimate | Model-specific provisional ranges, measured throughput refresh, map-storage math | MODIFY | Kaggle output constraints [R22], engineering calculation | More realistic budget | Low profiling | 01,03,08 | Mandatory |
| V35 C | Failure recovery | Save/checkpoint general advice | Atomic writes, RNG/optimizer resume, smoke/full separation, fresh-session attach test | ADD | Prevent incomplete/lost or incompatible outputs | Less wasted GPU work | Low/medium | 01–08 | Mandatory |
| V36 B | Field route | Early A/B decision | Preserve, tie to actual permissions; no claim that three sites suffice for certification | KEEP + CLARIFY | Independent-unit design | Honest field relevance | Depends on actual access | 01,02,07 | Mandatory route; S6 |
| V37 A | Statistical repetition | Seeds and clusters mentioned | Distinguish ensemble members, seed repeats, acquisition groups, corruption replicas | MODIFY | Avoid pseudoreplication | Credible CIs and comparisons | Low analysis | 03,07,08 | Mandatory |
| V38 D | Weighted theory | Conditional Q1 guarantee tied to diagnostics | Optional known-weight simulation/theorem, optional independent target recalibration | REPLACE | [R16–R18]; stronger data/theory needed | Useful extension without overclaiming | Small simulation to substantial new labels | 07 | Optional; S4 |
| V39 D | Extra technologies | Severity/LiDAR/new backbone/LLM/platform removed | Preserve exclusions; no additional compulsory architectures | KEEP | Protect focused MSc feasibility | Time for core science | Reduces scope | All | Mandatory scope boundary |
| V40 B | Readiness and approvals | Global frozen-design language | Explicit proposed decisions and stage-specific blockers | ADD | A completed blueprint is not approved or executed research | Concrete reviewable next step | Low | 01,05,08 | Mandatory |

**Removed from the core specification:** the unsupported monotone-selective-risk argument; two-risk-only correction for a 13-policy search; 80-negative sufficiency implication; outcome-driven reserve retries; GT-conditioned deployment score; automatic weighted guarantee after AUC/ESS gates; late silent ensemble expansion; accepted Dice as standalone co-primary success; and universal safety/domain-invariance claims.

**Preserved:** project identity, exactly eight notebook filenames, two binary risks, primary alpha values and total 95% confidence goal, all 13 original paired thresholds, explicit review-all, `NOT_CERTIFIABLE` exclusion, 0.55/20/5 operational component constants, 75% branch matching and 0.90 LWBR threshold unless scientifically amended, three-member ensemble, bounded backbone roster/fallbacks, independent internal/external/HN evaluation, field-route commitment, failure taxonomy, negative-result reporting, legacy numbers/population distinction, and reproducibility/manuscript outputs.

---

## 18. Preservation and review traceability

This mapping retains the substantive requirements from all v3.2 review rounds without preserving invalid details merely because they were labeled frozen.

| Earlier requirement group | v3.3 location / artifact |
|---|---|
| One declared statistical procedure, binary risks, selective denominators | Sections 9 and 13 Phase 01/05/06; `rcps_decision_D2.md`, `statistical_design.json` |
| Branch matching, radius, skeleton, component validity, early formulas/tests | Sections 7 and 13 Phase 02/04; `metric_contract.json`, formulas, synthetic fixtures |
| Review-all, zero prediction/GT cases, NOT_CERTIFIABLE | Sections 7–9; explicit decision/status logic and tests |
| Two frozen score sources and empirical-CDF metadata | Section 8; `percentile_transform.json`, prediction-only score schema |
| Base gate, modern reproducibility, fallback, resource refresh | Sections 6/14 and Phases 01/03 |
| Preliminary lineage, legacy reuse, major/minor leakage | Sections 4/5/15 and Phases 01/02 |
| Calibration floor/rare negatives/reserve contingency | Section 9.5–9.6; corrected accepted-count logic and fixed-N sampling plan |
| Hard-negative categories/expert review/metadata and manual first | Section 5.6; `annotation_manual_v1.md`, `hard_negative_spec.md` |
| Field Route A/B, MSc/Q1 split of Phase 07, weighted experiment | Sections 5.7/10/13/16; explicit empirical-versus-theory status |
| Primary endpoints and failure taxonomy before final evaluation | Sections 2/11/13 Phase 05; preregistration and taxonomy files |
| H3/H4 negative-result plans and all gate registers | Sections 2/15; hypothesis reports and `decision_gates.csv` |
| Canonical MRC row and no poster/population mixing | Section 4; historical-only record and clean-retrained identities |
| 05→06 mathematical verification | Section 9 and G07; proof, exact-bound cross-check, adviser/technical review |
| Multi-seed/statistics/efficiency/demo/manuscript outputs | Sections 11/13 Phase 08/14/16; no implicit fifth-member update |

No important v3.2 requirement is discarded without a change-register explanation. The corrected statistical/observability rules supersede contradictory wording in older blueprints.

---

## 19. Implementation readiness and unresolved decisions

### 19.1 Current status

**Can coding begin? Yes — Phase 01.** This blueprint contains a concrete primary statistical route and an integrated implementation specification. It does not require a new theory discovery before writing the inventory, design, metrics, or bound code.

**Can final certification begin now? No.** Real data counts/independence/labels have not been verified, no runnable implementation exists yet, and the required pre-calibration sign-offs and tests have not occurred. These are stage gates, not reasons to delay creating the Phase-01 notebook after this blueprint is reviewed.

**Is the core mathematical method unresolved?** The primary finite-family binomial argument is explicitly specified. Its applicability to the eventual dataset and its implementation remain to be checked. A general real-domain estimated-weight guarantee remains blocked; the core study does not depend on obtaining it.

**Exact next notebook filename:** `CrackSAFE_CP_Phase01_Legacy_Design_Literature_Locks.ipynb`.

### 19.2 Proposed decisions requiring researcher/supervisor review

| Decision | Concrete recommendation | Approval status / deadline | What it blocks |
|---|---|---|---|
| S1 statistical correction | Adopt Section-9 exact conditional binomial bounds with delta=.05/26, finite-family selection, and explicit LTT-compatible naming | Proposed; review in Phase 01 and technical sign-off before Phase 06 | Final certification; invalid v3.2 shortcut is not an acceptable alternative |
| S2 sampling/data budget | Approve actual certification unit and reference population; target 300/300 when feasible; choose main family or pre-calibration one-policy alternative only after independent-count audit | Proposed; Phase-02 exit / before calibration outcomes | Calibration manifest and strength of claims |
| S3 endpoint/score specification | Retain precise LWBR failure, use prediction-only symmetric branch score and top-decile entropy, r=4 benchmark convention with annotation audit | Proposed; Phase-04/05 freeze before calibration | Structural endpoint/score lock; changes require dated rationale |
| S4 shift scope | Mandatory Q1 empirical weighted analysis; theorem-qualified real-domain weighting optional and blocked without sufficient assumptions | Proposed; Phase-01 scope and Phase-05 plan | Formal shift claims only, not core MSc coding |
| S5 training/roster | Three candidate slots, technical fallbacks, common-loss comparison plus recovered MRC recipe only if available/budgeted | Proposed; Phase-01/03 training freeze | Full model-comparison runs |
| S6 annotation/field resources | Secure actual expert reviewer and field route; otherwise Route B; confirm rights for every source | Unverified; Phase-01/02 | Benchmark label credibility and field route |
| S7 utility criterion | Use ≥50% overall and ≥30% each-class automation as practical discussion targets, with empirical counts/CIs | Proposed; Phase-05 preregistration | Strong utility-success wording, not statistical validity |

Implementation may encode these recommended settings while recording status as `PROPOSED`, but must not automatically generate “approved by supervisor” or pass a sign-off gate. No approval is requested merely to produce this completed review document; it is the concrete material for that later discussion.

### 19.3 Remaining research risks

Independent negative scarcity is the largest feasibility risk. Dataset source reuse may leave no truly external source. Small/thin GT annotations may make the inherited component minimum and branch endpoint unsuitable. The three-member ensemble may agree on systematic errors. Topology may add no value over entropy. The conservative multiplicity correction may return review-all. DMSRCrack or closest-comparator permission/build constraints may force fallback or limit comparison. Few field sites weaken generalization evidence. Weighted estimates can fail under label/annotation or feature-sufficiency shift. Q1 novelty remains empirical and conditional on comparison quality.

None of these is resolved by a longer model list, more pixels counted as observations, or a favorable single test number. The design explicitly permits negative findings and narrower conclusions.

### 19.4 Eight-phase handoff summary

| Phase | Main output | Main gate |
|---:|---|---|
| 01 | Legacy/design/literature, roster, field and resource decisions | Actual evidence and unresolved approvals recorded |
| 02 | Source/lineage audit, annotations, independent units, sealed splits | Valid labels, independence, and calibration feasibility |
| 03 | Clean baselines and frozen calibrated three-member engine | Base readiness and reproducible checkpoints |
| 04 | Tested structural metrics and ordinary uncertainty | Correct edge cases and metric interpretation |
| 05 | Prediction-only topology, score transforms, policies, preregistration | Inference observability and math/code sign-off |
| 06 | Exact two-risk selection and untouched internal evaluation | Certified nonzero automation or honest review-all |
| 07 | External/HN/field-or-corruption and weighted empirical evidence | No unsupported shift guarantee |
| 08 | Statistics, ablations, efficiency, reproducibility, manuscript assets | Every claim traceable to the correct population |

---

## 20. Verified reference register

Links below are primary papers, publishers/proceedings, author repositories, or official documentation. Access date for this focused review is 2026-10-15. “Verified” means the stated identity/evidence was retrieved, not that every experiment or repository was reproduced. A publisher search record/abstract is marked as such when full text was blocked. Never cite a search snippet from a different paper's “related articles” as if it described the target paper.

- **[R01]** Bates, S.; Angelopoulos, A.; Lei, L.; Malik, J.; Jordan, M. I. *Distribution-Free, Risk-Controlling Prediction Sets*. Journal of the ACM, 2021. [DOI: 10.1145/3478535](https://doi.org/10.1145/3478535); [original preprint](https://arxiv.org/abs/2101.02703); [official code](https://github.com/aangelopoulos/rcps). Original preprint and repository verified; publisher full text blocked. Do not use the erroneous “JACM 2024” shorthand found in some later summaries.
- **[R02]** Angelopoulos, A. N.; Bates, S.; Candès, E. J.; Jordan, M. I.; Lei, L. *Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control*. [Original preprint, arXiv:2110.01052](https://arxiv.org/abs/2110.01052); [full text examined](https://arxiv.org/html/2110.01052v5); [official code](https://github.com/aangelopoulos/ltt). In particular, Sections 2.3–2.4 and 3.2 address multiple testing, multiple risks, and selective classification. Cite the exact publication/version used in implementation, not an inferred journal date.
- **[R03]** Clopper, C. J.; Pearson, E. S. *The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial*. Biometrika 26(4), 404–413, 1934. [DOI: 10.1093/biomet/26.4.404](https://doi.org/10.1093/biomet/26.4.404). Publisher bibliographic record verified; full article access restricted. The one-sided specification here is given explicitly and numerically checked.
- **[R04]** Angelopoulos, A. N.; Bates, S.; Fisch, A.; Lei, L.; Schuster, T. *Conformal Risk Control*. [Original preprint, arXiv:2208.02814](https://arxiv.org/abs/2208.02814). Use the verified version's exact guarantee rather than treating every conformal method as a high-probability selective-risk theorem.
- **[R05]** Gupta, S.; Zhang, Y.; Hu, X.; Prasanna, P.; Chen, C. *Topology-Aware Uncertainty for Image Segmentation*. NeurIPS 2023. [Proceedings paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/19ded4cfc36a7feb7fce975393d378fd-Paper-Conference.pdf); [original preprint](https://arxiv.org/abs/2306.05671); [official implementation](https://github.com/Saumya-Gupta-26/struct-uncertainty). Conference year is 2023 even where repository citation text uses 2024.
- **[R06]** Zhang, C.; Bahrami, M.; Mishra, D. K.; Yuen, M. M. F.; Yu, Y.; Zhang, J. *SelectSeg: Uncertainty-based selective training and prediction for accurate crack segmentation under limited data and noisy annotations*. Reliability Engineering & System Safety 259, 110909, 2025. [DOI: 10.1016/j.ress.2025.110909](https://doi.org/10.1016/j.ress.2025.110909); [publisher record](https://www.sciencedirect.com/science/article/pii/S0951832025001127); [author implementation](https://github.com/zhangchen553/SelectSeg). Publisher metadata/abstract and repository inspected; repository describes a four-stage process. Permission/license needs Phase-01 confirmation.
- **[R07]** Liu, H.; Jia, C.; Shi, F.; Cheng, X.; Chen, S. *SCSegamba: Lightweight Structure-Aware Vision Mamba for Crack Segmentation in Structures*. CVPR 2025. [Original preprint](https://arxiv.org/abs/2503.01113); [official repository](https://github.com/Karl1109/SCSegamba). Repository identifies Apache-2.0; pin an actual commit/license before reuse.
- **[R08]** Al-Sameai, H.; Saleh, R. A. A.; de Moura, J.; Akay, R. *Dual-encoder Multi-Scale Refinement network for robust crack segmentation across diverse domains*. Automation in Construction 188, 107004, 2026. [DOI: 10.1016/j.autcon.2026.107004](https://doi.org/10.1016/j.autcon.2026.107004); [publisher record](https://www.sciencedirect.com/science/article/pii/S0926580526002451); [official repository](https://github.com/habeeb96/DMSRCrack). Bibliographic identity corroborated by publisher and repository; no explicit license found in the inspected root listing. No legal conclusion is inferred from that absence.
- **[R09]** Li, X.; Yu, S.; Xiao, S.; Lin, X.; Zhao, Z. *A topology-aware segment anything model for domain-invariant crack segmentation*. Engineering Applications of Artificial Intelligence 166, 113688, 2026. [DOI: 10.1016/j.engappai.2025.113688](https://doi.org/10.1016/j.engappai.2025.113688); [publisher record](https://www.sciencedirect.com/science/article/pii/S0952197625037200). Title/abstract/DOI checked; full text unavailable in this review. An official code location was not established. Do not substitute a different SAM repository from related-article snippets.
- **[R10]** Zuo, X.; Sheng, Y.; Shen, J.; Shan, Y. *Topology-aware Mamba for Crack Segmentation in Structures*. 2024. [Original preprint](https://arxiv.org/abs/2410.19894); [publisher record](https://www.sciencedirect.com/science/article/pii/S0926580524005818); [author repository](https://github.com/shengyu27/CrackMamba). Keep distinct from SCSegamba.
- **[R11]** Agyei Kyem, B.; Asamoah, J. K.; Denteh, E.; Aboah, A. *Multi-Task Crack Foundation Model for Engineering-Reliable Crack Representation and Topology Preservation in Civil Infrastructure*. 2026. [Original preprint, arXiv:2606.05641](https://arxiv.org/abs/2606.05641); [publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0926580526004310); [original CrackGeoFM repository](https://github.com/Blessing988/CrackGeoFM). Original abstract, publisher record, and repository inspected. No DOI or released pretrained checkpoint is invented where the inspected repository contains a placeholder. Confirm final author spelling/bibliographic details from the paper when exporting BibTeX.
- **[R12]** Lakshminarayanan, B.; Pritzel, A.; Blundell, C. *Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles*. NeurIPS 2017. [Proceedings](https://papers.neurips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html); [original preprint](https://arxiv.org/abs/1612.01474). This project implements ordinary independent ensembles; it does not claim to reproduce every training detail of the original work.
- **[R13]** Shit, S. et al. *clDice — A Novel Topology-Preserving Loss Function for Tubular Structure Segmentation*. CVPR 2021. [CVF paper](https://openaccess.thecvf.com/content/CVPR2021/html/Shit_clDice_-_A_Novel_Topology-Preserving_Loss_Function_for_Tubular_Structure_CVPR_2021_paper.html); [original code](https://github.com/jocpae/clDice).
- **[R14]** Mossina, L.; Dalmau, J.; Andéol, L. *Conformal Semantic Image Segmentation: Post-hoc Quantification of Predictive Uncertainty*. CVPR Workshops, 2024, 3574–3584. [CVF record](https://openaccess.thecvf.com/content/CVPR2024W/SAIAD/html/Mossina_Conformal_Semantic_Image_Segmentation_Post-hoc_Quantification_of_Predictive_Uncertainty_CVPRW_2024_paper.html); [original preprint](https://arxiv.org/abs/2405.05145). Publisher metadata and preprint record checked.
- **[R15]** Mossina, L.; Friedrich, C. *Controlling False Positives in Image Segmentation via Conformal Prediction*. 2025 preprint. [Original record](https://arxiv.org/abs/2511.15406); [code linked in abstract](https://github.com/deel-ai-papers/conseco). Abstract-level review; do not assert peer-reviewed venue or an identical selective-risk theorem.
- **[R16]** Tibshirani, R. J.; Barber, R. F.; Candès, E. J.; Ramdas, A. *Conformal Prediction Under Covariate Shift*. NeurIPS 2019. [Original preprint](https://arxiv.org/abs/1904.06019). Likelihood-ratio assumptions matter; estimated ratios require additional qualifications.
- **[R17]** Almeida, D. C.; Bravo, J.; Bono, J.; Bizarro, P.; Figueiredo, M. A. T. *High Probability Risk Control Under Covariate Shift*. COPA 2025, PMLR 266:133–152. [Official proceedings](https://proceedings.mlr.press/v266/almeida25a.html); [author-hosted original paper](https://research.feedzai.com/oshuzuxa/2025/10/high_probability_risk_control_under_covariate_shift.pdf). Paper inspected, including conditional-risk and weight-estimation discussions. No official repository was established in the inspected paper.
- **[R18]** Zecchin, M.; Hellström, F.; Park, S.; Shamai, S.; Simeone, O. *Generalization and Informativeness of Weighted Conformal Risk Control Under Covariate Shift*. 2025. [Original preprint](https://arxiv.org/abs/2501.11413). Original abstract verified; do not infer its assumptions from its title.
- **[R19]** *UCrack-DA: A Multi-Scale Unsupervised Domain Adaptation Method for Surface Crack Segmentation*. Remote Sensing 17(12), 2101, 2025. [Original publisher article](https://www.mdpi.com/2072-4292/17/12/2101). Publisher abstract/metadata verified. The reported UAV-Crack dataset link is not proof that UCrack-DA implementation code is released.
- **[R20]** Xu, Z.; Karampatziakis, N.; Mineiro, P. *Active, anytime-valid risk controlling prediction sets*. 2024 preprint. [Original record](https://arxiv.org/abs/2406.10490). Included to distinguish sequential validity from the fixed-sample design; not adopted in the core.
- **[R21]** SDNET2018 original dataset/article. [Institutional dataset page](https://digitalcommons.usu.edu/all_datasets/48/); [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6247444/). The source reports 230 captured originals and over 56,000 crops; the dataset page states CC BY 4.0. The user's actual archive counts, parent recovery, and selected negative counts remain unverified.
- **[R22]** Kaggle official [Notebooks documentation](https://www.kaggle.com/docs/notebooks) and [efficient GPU usage guidance](https://www.kaggle.com/docs/efficient-gpu-usage). Official documentation search content checked; some rendered pages expose limited machine-readable text. Live account quota/hardware/session limits must be recorded in Phase 01.

### Review coverage and exclusions

The review covered named crack comparators, topology-preserving metrics/uncertainty, deep ensembles, exact class-conditional selective risk, conformal/RCPS/LTT distinctions, high-probability and weighted shift methods, annotation/parent dependence, and Kaggle execution. Original sources from 2024–2026 were prioritized alongside necessary foundations. Unverified new titles and search results that only reproduced another article's related-content text were not used to establish novelty or performance. Future implementation should refresh source availability, not assume the present review has installed every repository.

---

## 21. Version history and final consistency checklist

### Version history

- **v3.0 (inherited history):** eight-phase reliability-centered design with design/annotation/statistics gates.
- **v3.1 (inherited history):** explicit review-all sentinel, empty-mask/LWBR clarifications, committed ensemble entropy and length-weighted topology intent, reserve/phase-scope clarifications.
- **v3.2, 26 August 2026 (source document):** NOT_CERTIFIABLE eligibility rule, 05→06 mathematical verification gate, no-branch topology clarifications; otherwise preserved earlier locks.
- **v3.3, 15 October 2026 (this document):** substantive statistical correction, prediction-only topology construction, independent-unit and fixed-calibration design, source/label/legacy exposure controls, precise metric claims, weighted-guarantee separation, fair entropy calibration comparator, updated 2024–2026 positioning, explicit phase/artifact contracts, feasible resource/recovery plan, and proposed-decision register. Detailed changes V01–V40 appear in Section 17.

### Blueprint-level verification completed for this deliverable

- Complete attached v3.2 text read, including all eight phases and review traceability sections.
- All eight notebook filenames preserved; each phase specifies the ten requested implementation elements.
- Primary risk targets, 13 non-null policies, sentinel, 26-bound budget, and sample-size arithmetic cross-checked.
- Prediction-only scores/decisions separated from GT evaluation; all-empty and no-denominator cases specified.
- Calibration selection and test evaluation distinguished; optional stopping and model changes explicitly addressed.
- Weighted empirical claims separated from theorem-qualified extensions; no AUC/ESS sufficiency claim retained.
- Input/output dependencies and mandatory artifact roles checked; important v3.2 requirements mapped in Section 18.
- Sources and evidence levels recorded; no invented real-data results, runtime measurements, repository reproduction, or supervisor approvals.

### Checks still required during implementation

- Actual archive contents, licenses, annotations, parent grouping, independent-unit counts, and model exposure.
- Actual repository commits, dependencies, permissions, GPU/RAM usage, and notebook runtime limits.
- Synthetic metric and exact-bound code tests; fresh-session reproducibility; technical/supervisor sign-off.
- Preregistered data/model/score/family hashes before final calibration; real certificate only after valid execution.
- Prospective evidence for any formal shift guarantee; primary Q1 evidence remains empirical under real external shifts unless stronger conditions are met.

**Final research rule:** preserve the original experiment, report its failures, and make any new scientific choice prospectively. A rigorous negative result is preferable to an apparently successful result produced by changing the population, denominator, endpoint, confidence budget, or policy after seeing outcomes.

**End of the complete v3.3 master blueprint.**




