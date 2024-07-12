from time import sleep
from typing import Any, Dict, List, Optional

import httpx


class RESASAPIClient:
    BASE_URL = "https://opendata.resas-portal.go.jp/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-KEY": self.api_key}
        self.client = httpx.Client()

    def fetch_data(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response = self.client.get(
            f"{self.BASE_URL}/{endpoint}", params=params, headers=self.headers
        )
        response.status_code
        response.raise_for_status()
        return response.json()

    def fetch_iter(self, endpoint: str, params_list: List[Dict[str, Any]]):
        results = []
        for params in params_list:
            response = self.fetch_data(endpoint, params)
            results.extend(response["result"])
            sleep(0.2)
        return results
