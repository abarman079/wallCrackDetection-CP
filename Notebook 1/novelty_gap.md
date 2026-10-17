# Literature positioning and remaining scientific gap

Research questions, hypotheses, and novelty

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


Verified literature positioning

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


Runtime verification is limited to reference_rechecks.csv. HTTP success does not establish scientific correctness, repository reproducibility, or legal permission. The reviewed source register is inherited explicitly. No broad new literature redesign was performed.
