# Decision D2 — exact conditional binomial finite-family procedure

Status: IMPLEMENTED_FOR_PLANNING; pending human mathematical sign-off G07. No real calibration has run.

Exact selective risk-control procedure and proof

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
