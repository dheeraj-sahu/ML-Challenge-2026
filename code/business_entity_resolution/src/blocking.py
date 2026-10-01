import collections
import csv
import sqlite3
from pathlib import Path

from preprocessing import numbers, row_views


def build_index(paths, db_path):
    db = sqlite3.connect(str(db_path))
    db.executescript("PRAGMA journal_mode=MEMORY; PRAGMA synchronous=OFF; PRAGMA temp_store=MEMORY;")
    db.executescript("DROP TABLE IF EXISTS records; DROP TABLE IF EXISTS keys; CREATE TABLE records(id TEXT PRIMARY KEY, name TEXT, address TEXT, country TEXT); CREATE TABLE keys(key TEXT, id TEXT);")
    counts = collections.Counter()
    records_batch, keys_batch = [], []
    for path in paths:
        with open(path, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                view = row_views(row)
                records_batch.append((row["entity_id"], view["name"], view["address"], view["country"]))
                keys = {"n:" + view["name_compact"]} if view["name_compact"] else set()
                if view["address_compact"]:
                    keys.add("a:" + view["address_compact"])
                keys.update("t:" + token for token in view["name_tokens"] + view["address_tokens"])
                for key in keys:
                    counts[key] += 1
                    keys_batch.append((key, row["entity_id"]))
                if len(records_batch) >= 10000:
                    db.executemany("INSERT INTO records VALUES(?,?,?,?)", records_batch)
                    db.executemany("INSERT INTO keys VALUES(?,?)", keys_batch)
                    records_batch.clear()
                    keys_batch.clear()
        db.commit()
    if records_batch:
        db.executemany("INSERT INTO records VALUES(?,?,?,?)", records_batch)
        db.executemany("INSERT INTO keys VALUES(?,?)", keys_batch)
        db.commit()
    db.execute("CREATE INDEX records_id ON records(id)")
    db.execute("CREATE INDEX keys_key ON keys(key)")
    db.execute("CREATE INDEX keys_id ON keys(id)")
    db.commit()
    return db, counts


def candidates(db, row, counts, max_block=250):
    view = row_views(row)
    keys = []
    exact_keys = []
    if view["name_compact"]:
        key = "n:" + view["name_compact"]
        keys.append(key)
        exact_keys.append(key)
    if view["address_compact"]:
        key = "a:" + view["address_compact"]
        keys.append(key)
        exact_keys.append(key)
    keys.extend("t:" + token for token in view["name_tokens"] + view["address_tokens"])
    ids = set()
    for key in keys:
        if key in exact_keys or counts.get(key, 0) <= max_block:
            ids.update(value[0] for value in db.execute("SELECT id FROM keys WHERE key=?", (key,)))
    if not ids and view["name_compact"]:
        prefix = view["name_compact"][:7]
        ids.update(value[0] for value in db.execute("SELECT id FROM records WHERE replace(name,' ','') LIKE ? LIMIT 100", (prefix + "%",)))
    if not ids:
        return [], view
    placeholders = ",".join("?" for _ in ids)
    rows = db.execute("SELECT id,name,address,country FROM records WHERE id IN (" + placeholders + ")", tuple(ids)).fetchall()
    result = []
    for entity_id, name, address, country in rows:
        result.append((entity_id, {"name": name, "name_compact": name.replace(" ", ""), "name_tokens": name.split(), "address": address, "address_compact": address.replace(" ", ""), "address_tokens": address.split(), "numbers": numbers(address), "country": country}))
    return result, view