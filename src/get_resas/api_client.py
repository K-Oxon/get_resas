from time import sleep

import httpx

from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel


class RESASAPIClient:
    BASE_URL = "https://opendata.resas-portal.go.jp/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-KEY": self.api_key}
        self.client = httpx.Client()

    def fetch_data(
        self,
        request_model: BaseRequestModel,
        response_model: BaseResponseModel | None = None,
    ) -> dict[str, any]:
        """リクエストを送信し、レスポンスを返す

        Args:
            request_model (BaseRequestModel): リクエストに必要なendpointとparams
            response_model (BaseResponseModel | None, optional): レスポンスモデル. Defaults to None.

        Returns:
            dict[str, any]: レスポンス
        """
        response = self.client.get(
            f"{self.BASE_URL}/{request_model.endpoint}",
            params=request_model.params.dict(),
            headers=self.headers,
        )
        print(response.status_code)
        response.raise_for_status()
        if response_model:
            return response_model(**response.json()).dict()
        else:
            return response.json()

    def fetch_iter(
        self,
        request_models: list[BaseRequestModel],
        response_model: BaseResponseModel | None = None,
    ) -> list[any]:
        results = []
        for request_model in request_models:
            response = self.fetch_data(
                request_model,
                response_model=response_model if response_model else None,
            )
            results.extend(response["result"])
            sleep(0.2)
        return results
