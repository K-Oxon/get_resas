import json
import os
from pathlib import Path

from api_client import RESASAPIClient
from utils.get_pref_code import get_pref_code

ENDPOINT = "cities"
API_KEY = os.getenv("RESAS_API_KEY")
EXPORT_DATA_DIR = Path(__file__).parents[2] / "data"


def main():
    resas_client = RESASAPIClient(API_KEY)

    params_list = [{"prefCode": pref_code} for pref_code in get_pref_code()]
    results = resas_client.fetch_iter(ENDPOINT, params_list)
    print(f"total results size: {len(results)}")

    # jsonlで保存
    with open(EXPORT_DATA_DIR / "cities/cities.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
