from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_pref_code import get_pref_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class CitiesRequestParams(BaseModel):
    prefCode: int = Field(..., description="都道府県コード")


class CitiesRequest(BaseRequestModel):
    """
    市区町村一覧を取得するためのパラメータのモデル

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/cities.html
    """

    endpoint: str = "cities"
    params: CitiesRequestParams

    @classmethod
    def generate_req_model_list(cls):
        """
        都道府県コードのリストを生成し、リクエストパラメータのリストを返す
        """
        return [
            cls(params=CitiesRequestParams(prefCode=pref_code))
            for pref_code in get_pref_code()
        ]


"""
レスポンス情報
"""


class City(BaseModel):
    prefCode: int
    cityCode: str
    cityName: str
    bigCityFlag: str


class CitiesResponse(BaseResponseModel):
    result: list[City]
