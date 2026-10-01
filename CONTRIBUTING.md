# Contributing

## Setup

Use Python 3.10 or newer and install the pinned dependencies:

```text
pip install -r code/business_entity_resolution/requirements.txt
```

## Run the pipeline

From the `student_resource` directory:

```text
python code/business_entity_resolution/src/main.py --root .
```

The pipeline reads `dataset/train` and `dataset/test`, then writes results and
metrics to `output/`.

## Validate outputs

Run the submission validator before sharing results:

```text
python utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir dataset/test
```

Keep generated data and local caches out of commits. Changes should preserve the
TSV schemas described in `README.md` and should be tested with the smallest
available dataset sample before a full run.
