"""Create (idempotently) the Atlas Vector Search index used by the mongodb search path.

Defines a vectorSearch index on `embedding` (cosine) plus a `companyId` filter field, then waits
until it is queryable. Run once after embeddings exist in the collection:

    ./.venv/bin/python -m scripts.create_mongo_index
"""
import os
import time

from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

URI = os.getenv("VKP_MONGO_URI", "mongodb://localhost:27017/vkp?directConnection=true")
DB = os.getenv("VKP_MONGO_DB", "vkp")
COLL = os.getenv("VKP_VECTOR_TABLE", "vec_all_minilm_l6_v2")
NAME = os.getenv("VKP_MONGO_VECTOR_INDEX", "vkp_vector_index")
DIM = int(os.getenv("VKP_VECTOR_DIM", "384"))


def main() -> None:
    coll = MongoClient(URI)[DB][COLL]
    existing = {i["name"] for i in coll.list_search_indexes()}
    if NAME in existing:
        print(f"index '{NAME}' already exists")
    else:
        coll.create_search_index(SearchIndexModel(
            name=NAME,
            type="vectorSearch",
            definition={"fields": [
                {"type": "vector", "path": "embedding", "numDimensions": DIM, "similarity": "cosine"},
                {"type": "filter", "path": "companyId"},
            ]},
        ))
        print(f"created index '{NAME}' on {DB}.{COLL}")

    for _ in range(60):
        idx = [i for i in coll.list_search_indexes() if i["name"] == NAME]
        if idx and idx[0].get("queryable"):
            print(f"index '{NAME}' is queryable")
            return
        time.sleep(2)
    print(f"index '{NAME}' created but not queryable yet (build still in progress)")


if __name__ == "__main__":
    main()
