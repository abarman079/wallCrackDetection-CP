# Leakage and curation report

Run `20261018T050513552430Z_afc0e8ab`, mode FULL; partition status PROVISIONAL.

- Examined images: 88806; logical raw sources: 5.
- Exact duplicate star edges: 24704; indexed near candidates: 13768.
- Conservative acquisition groups: 1; quarantine records: 44616.
- Perceptual-index truncated samples: 16304 (blocks unreviewed completeness).
- Every independent role manifest is disjoint by sample, split group and certification unit. Compatibility development and linked hard-negative development are the two documented aliases.

Byte and canonical decoded-pixel hashes establish exact content equivalence; masks are compared within image-equivalence groups to flag conflicts. Masks alone never establish image duplication. Near matches are only candidates, unioned conservatively until adjudicated. Five crop windows plus rotations/flips cannot detect every possible crop. Unknown acquisition/source provenance never creates an IID singleton. The aggregate collection is not an independent source. Original-source holdout follows transitive groups; unknown provenance cannot justify a zero-shot claim.

Remaining statistical and scientific limitations are in independence_assessment.md, population_contract.md, decision_gates.csv and the private curator review queue. A clean structural split validator result does not imply rights, labels, IID, scientific approval or adequate calibration capacity. No historical pair count was used as a current dataset count.
