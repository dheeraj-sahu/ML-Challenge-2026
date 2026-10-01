import argparse
import csv
import json
import random
import statistics
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from blocking import build_index, candidates
from evaluation import macro_f05
from features import feature_row
from inference import run, write_results
from model import train, save
from utils import read_truth, write_json


def read_rows(path, limit=None):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = csv.DictReader(fh, delimiter="\t")
        for number, row in enumerate(rows):
            if limit is not None and number >= limit:
                break
            yield row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--team", default="entity_resolution")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve() if args.root else Path(__file__).resolve().parents[4]
    train_dir, test_dir = root / "dataset/train", root / "dataset/test"
    required_dirs = (train_dir, test_dir)
    missing_dirs = [str(path) for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        parser.error("missing dataset directory: " + ", ".join(missing_dirs))
    output = root / "output"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        train_db, train_counts = build_index([train_dir / "train_source2.tsv", train_dir / "train_source3.tsv"], Path(temp) / "train.sqlite")
        truth = read_truth(train_dir / "train_ground_truth.tsv")
        rng = random.Random(17)
        sample = list(read_rows(train_dir / "train_source1.tsv", 30000))
        rng.shuffle(sample)
        features, labels, validation_truth, validation_predictions = [], [], {}, {}
        split = 5000
        for row in sample[split:]:
            blocked, left = candidates(train_db, row, train_counts)
            positives = set(truth.get(row["entity_id"], []))
            for entity_id, right in blocked:
                features.append(feature_row(left, right)); labels.append(int(entity_id in positives))
        if not any(labels):
            raise RuntimeError("blocking produced no positive training examples")
        classifier = train(features, labels)
        for row in sample[:split]:
            blocked, left = candidates(train_db, row, train_counts)
            scored = [(entity_id, feature_row(left, right)) for entity_id, right in blocked]
            probs = classifier.predict_proba([value for _, value in scored])[:, 1] if scored else []
            validation_truth[row["entity_id"]] = truth.get(row["entity_id"], [])
            validation_predictions[row["entity_id"]] = [entity_id for (entity_id, _), p in zip(scored, probs) if p >= 0.78]
        validation_score = macro_f05(validation_truth, validation_predictions)
        save(classifier, output / "model.joblib")
        test_db, test_counts = build_index([test_dir / "test_source2.tsv", test_dir / "test_source3.tsv"], Path(temp) / "test.sqlite")
        test_rows = list(read_rows(test_dir / "test_source1.tsv"))
        matching, candidate_rows, candidate_counts = run(test_rows, lambda row: candidates(test_db, row, test_counts), classifier, 0.78)
        write_results(output / "matching_results.tsv", ["source1_entity_id", "matched_entity_ids"], matching)
        write_results(output / "candidate_pairs.tsv", ["source1_entity_id", "candidate_entity_ids"], candidate_rows)
        naive = len(test_rows) * (sum(1 for _ in read_rows(test_dir / "test_source2.tsv")) + sum(1 for _ in read_rows(test_dir / "test_source3.tsv")))
        stats = {"validation_f05": validation_score, "naive_comparisons": naive, "candidate_comparisons": sum(candidate_counts), "reduction_ratio": 1 - sum(candidate_counts) / naive, "average_candidates": statistics.mean(candidate_counts), "median_candidates": statistics.median(candidate_counts), "p95_candidates": float(np.percentile(candidate_counts, 95)), "max_candidates": max(candidate_counts), "test_s1_entities": len(test_rows), "predicted_matches": sum(len(ids) for _, ids in matching), "predicted_singletons": sum(not ids for _, ids in matching), "threshold": 0.78, "model": "scikit-learn LogisticRegression (BSD-3-Clause), 13 numeric features"}
        write_json(output / "metrics.json", stats)
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()