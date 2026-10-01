import json
from pathlib import Path


def read_truth(path):
    truth = {}
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            key, _, value = line.rstrip("\n").partition("\t")
            truth[key] = [item for item in value.split(",") if item]
    return truth


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")