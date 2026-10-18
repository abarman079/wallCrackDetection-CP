# Deferred topology and shift contracts

Implementation/evaluation in Phases04–05. No GT or unavailable model predictions were used in this notebook.

Structural metrics and failure definitions

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


Prediction-only uncertainty and decision policies

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


Domain shift and weighted analysis

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
