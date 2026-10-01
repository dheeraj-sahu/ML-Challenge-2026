def f05(true_ids, predicted_ids):
    true_ids, predicted_ids = set(true_ids), set(predicted_ids)
    if not true_ids and not predicted_ids:
        return 1.0
    if not true_ids or not predicted_ids:
        return 0.0
    precision = len(true_ids & predicted_ids) / len(predicted_ids)
    recall = len(true_ids & predicted_ids) / len(true_ids)
    return 0.0 if precision + recall == 0 else 1.25 * precision * recall / (0.25 * precision + recall)


def macro_f05(truth, predictions):
    return sum(f05(truth[key], predictions.get(key, [])) for key in truth) / max(1, len(truth))