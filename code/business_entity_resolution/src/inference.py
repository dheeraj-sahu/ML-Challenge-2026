import csv

from features import cheap_keep, feature_row


def run(rows, index, model, threshold):
    matching, candidate_rows, counts = [], [], []
    for row in rows:
        blocked, left = index(row)
        kept = []
        scored = []
        for entity_id, right in blocked:
            if cheap_keep(left, right):
                kept.append(entity_id)
                scored.append((entity_id, feature_row(left, right)))
        probabilities = model.predict_proba([features for _, features in scored])[:, 1] if scored else []
        matches = sorted(entity_id for (entity_id, _), score in zip(scored, probabilities) if score >= threshold)
        candidates = sorted(set(kept))
        matching.append((row["entity_id"], matches))
        candidate_rows.append((row["entity_id"], candidates))
        counts.append(len(candidates))
    return matching, candidate_rows, counts


def write_results(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        for entity_id, ids in rows:
            writer.writerow([entity_id, ",".join(ids)])