from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_pref_code import get_pref_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationFutureParams(BaseModel):
    year: int = Field(2040, description="年 指定可能年度: 2040のみ")
    prefCode: int = Field(..., description="都道府県コード")


class PopulationFutureRequest(BaseRequestModel):
    """
    地域単位、年単位の2040年時点の将来人口推計情報
    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/future/cities.html
    """

    endpoint: str = "population/future/cities"
    params: PopulationFutureParams

    @classmethod
    def generate_req_model_list(cls) -> list[BaseRequestModel]:
        """全パラメータの組み合わせを生成"""
        return [
            cls(params=PopulationFutureParams(year=2040, prefCode=pref_code))
            for pref_code in get_pref_code()
        ]


"""
レスポンス情報
"""


class CityData(BaseModel):
    cityCode: str = Field(..., description="市区町村コード")
    cityName: str = Field(..., description="市区町村名")
    value: int = Field(..., description="推計人口")
    ratio: float = Field(..., description="若年女性人口減少率")


class Result(BaseModel):
    cities: list[CityData]


class PopulationFutureResponse(BaseResponseModel):
    result: Result
