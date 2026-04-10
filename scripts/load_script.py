import json
import os
from pathlib import Path
import pymongo as pm

SE_DB = "seDB"
DEFAULT_URI = "mongodb://localhost:27017"

COLLECTIONS = ["countries", "states", "cities", "counties", "prompts", "puzzles"]

def get_client():
    uri = os.getenv("MONGO_URI", DEFAULT_URI)
    return pm.MongoClient(uri)

def load_seed_json():
    seed_path = Path(__file__).parent.parent / "seed" / "seed_data.json"
    with seed_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def upsert_many(col, docs, unique_key):
    for d in docs:
        if unique_key not in d:
            raise ValueError(f"Missing {unique_key} in doc: {d}")
        col.update_one({unique_key: d[unique_key]}, {"$set": d}, upsert=True)

def main():
    data = load_seed_json()
    client = get_client()
    db = client[SE_DB]

    keys = {
        "countries": "country_id",
        "states": "id",
        "cities": "id",
        "counties": "id",
        "prompts": "id",
        "puzzles": "id",
    }

    for name in COLLECTIONS:
        docs = data.get(name, [])
        if not docs:
            continue
        upsert_many(db[name], docs, keys[name])
        print(f"Seeded {name}: {len(docs)} docs")

    print("Done.")

if __name__ == "__main__":
    main()