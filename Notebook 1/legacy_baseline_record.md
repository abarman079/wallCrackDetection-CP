# Historical MRC reference — not a Phase01 result

The 1,356-case Phase12 and 1,695-case Phase14A populations must remain separate. These figures are inherited from v3.3, not measured here.

```json
{
  "evidence_level": "HISTORICAL_REFERENCE_NOT_REPRODUCED",
  "phase12": {
    "population_n": 1356,
    "crack_IoU": 0.581844,
    "crack_Dice": 0.722288,
    "no_crack_false_positive_rate": 0.045977,
    "temperature": 1.556495,
    "mask_threshold": 0.55
  },
  "phase14A": {
    "population_n": 1695,
    "crack_IoU": 0.582254,
    "crack_Dice": 0.722671,
    "no_crack_false_positive_count": 5,
    "no_crack_n": 218,
    "no_crack_false_positive_rate": 0.022936,
    "classification_precision": 0.996626,
    "classification_recall": 1.0,
    "classification_specificity": 0.977064,
    "classification_F1": 0.99831,
    "TP": 1477,
    "FP": 5,
    "TN": 213,
    "FN": 0,
    "Boundary_IoU": 0.343042,
    "clDice": 0.793017
  },
  "historical_split_counts_unverified": {
    "train": 9603,
    "validation": 1695,
    "combined": 11298
  },
  "external_claim_unverified": "Up to 72.9 percent decline; motivational historical statement only; dataset/metric basis not independently reproduced"
}
```

Found files: 0. A discovered filename and checksum do not authenticate its relationship to the historical experiment. No checkpoint was loaded, evaluated or trained. Frozen-checkpoint evaluation and clean retraining are separate Phase03 evidence tracks. Missing original files do not prove absence of historical leakage.
