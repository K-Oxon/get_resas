from time import sleep

import httpx

from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


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
    ) -> dict[str, any] | None:
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
        logger.info(
            f"request params: {request_model.params.dict()}, response status code: {response.status_code}"
        )
        response.raise_for_status()  # エラーでも200で返ってくるのでほぼ意味無し
        if response_model:
            try:
                return response_model(**response.json()).dict()
            except Exception as e:
                logger.error(f"Validation error: {e}, input: {response.json()}")
                return response.json()
        else:
            return response.json()

    def fetch_iter(
        self,
        request_models: list[BaseRequestModel],
        with_params: bool = False,
        exclude_params_keys: list[str] | None = None,
        response_model: BaseResponseModel | None = None,
    ) -> list[any]:
        """リクエストモデルのリストを受け取り、レスポンスのresultをまとめて返す
        北方領土など200が帰ってきてもresultがNoneの場合があり、それはskip扱い

        Args:
            request_models (list[BaseRequestModel]): リクエストモデルのリスト
            with_params (bool, optional): リクエストパラメータをレスポンスに追加するか. Defaults to False.
            exclude_params_keys (list[str] | None, optional): 追加しないパラメータのキー. Defaults to None.
            response_model (BaseResponseModel | None, optional): レスポンスモデル. Defaults to None.

        Returns:
            list[any]: レスポンスのリスト
        """
        results = []
        for request_model in request_models:
            response = self.fetch_data(
                request_model,
                response_model=response_model if response_model else None,
            )
            if with_params:
                response = self._add_params_to_response(
                    response,
                    request_model.params.dict(),
                    exclude_params_keys=exclude_params_keys,
                )
            if isinstance(response["result"], list):
                results.extend(response["result"])
            elif response["result"] is None:
                pass
            else:
                results.append(response["result"])
            # 5 リクエスト/秒 に抑える
            sleep(0.2)
        return results

    def _add_params_to_response(
        self,
        response: dict[str, any],
        params: dict[str, any],
        exclude_params_keys: list[str] | None = None,
    ) -> dict[str, any]:
        """レスポンスにリクエストパラメータを追加する
        ★人口系データなどはリクエストしたパラメータを追加しないとなんのデータか判別不能なため

        Args:
            response (dict[str, any]): レスポンス
            params (dict[str, any]): リクエストパラメータ
            exclude_params_keys (list[str] | None, optional): 追加しないパラメータのキー. Defaults to None.

        Returns:
            dict[str, any]: リクエストパラメータを追加したレスポンス

        Example:
            response = {"message": None, "result": {"boudaryYear": 2020, "data": [...]}}
            params = {"prefCode": "1", "cityCode": "101100"}
            response = self._add_params_to_response(response, params)
            print(response)
            # => {"message": None, "result": {"boudaryYear": 2020, "data": [...], "prefCode": "1", "cityCode": "101100"}}
        """
        if exclude_params_keys:
            params = {k: v for k, v in params.items() if k not in exclude_params_keys}
        if isinstance(response["result"], dict):
            # ネストしたdictの場合は最上位階層に追加
            response["result"].update(params)
        elif isinstance(response["result"], list):
            # リストの場合はリストの各要素（一つ下の階層）に追加
            for item in response["result"]:
                if isinstance(item, dict):
                    item.update(params)
        return response
