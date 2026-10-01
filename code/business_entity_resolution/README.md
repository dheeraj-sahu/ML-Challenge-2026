# NITDominars Business Entity Resolution

## Overview
This package resolves each Source 1 record to zero or more Source 2 and Source 3 records using local data only. It normalizes names and addresses, creates indexed blocking candidates, scores candidate pairs with numeric similarity and interaction features, and writes deterministic TSV outputs.

## Dataset and installation
Run from the `student_resource` directory with Python 3.10+:

```text
pip install -r code/business_entity_resolution/requirements.txt
python code/business_entity_resolution/src/main.py --root .
```

The expected input folders are `dataset/train` and `dataset/test`. No network access or external business data is used.

## Blocking and features
Source 2 and Source 3 records are indexed in SQLite. Candidate union uses exact compact name, exact compact address, and rare normalized name/address tokens, with a bounded prefix fallback. Very common blocks are capped to avoid Cartesian expansion. The final candidate list is filtered by inexpensive name/address evidence and is exactly the set scored by the classifier.

Features include normalized name and address similarity, token Jaccard scores, address-number agreement, country equality, exact normalized flags, and name/address interaction terms. Empty addresses and unseen country labels are supported.

## Model and validation
The model is scikit-learn `LogisticRegression` with `class_weight="balanced"` and a fixed seed. Training negatives are blocked candidates absent from the supplied ground truth. A held-out Source 1 sample is scored with macro entity-level F0.5; threshold selection favors precision and independently permits multiple links per Source 1 record.

The classifier is BSD-3-Clause licensed through scikit-learn and has no pretrained parameters or external model data.

## Outputs
`output/matching_results.tsv` contains one row for every test Source 1 ID. `output/candidate_pairs.tsv` contains the exact final candidate set passed to inference. Both preserve Source 1 order and use tab-separated fields.

Validate from `student_resource`:

```text
python utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir dataset/test
```

The expected result is `PASS`.
