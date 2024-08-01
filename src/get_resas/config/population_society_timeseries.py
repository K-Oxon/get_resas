from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationSocietyTimeseriesParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )


class PopulationSocietyTimeseriesRequest(BaseRequestModel):
    """
    年齢階級別純移動数の時系列分析

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/society/forAgeClassLine.html
    """

    endpoint: str = "population/society/forAgeClassLine"
    params: PopulationSocietyTimeseriesParams

    @classmethod
    def generate_req_model_list(cls):
        pref_city_code_list = get_city_code()
        req_model_list = []
        for pref_code, city_code in pref_city_code_list:
            req_model_list.append(
                cls(
                    params=PopulationSocietyTimeseriesParams(
                        prefCode=pref_code, cityCode=city_code
                    )
                )
            )
        return req_model_list


"""
レスポンス情報
"""


class DataPoint(BaseModel):
    axisx: str = Field(..., description="年齢階級 e.g. 0～4歳→5～9歳")
    axisy: int = Field(..., description="移動数")


class DataSet(BaseModel):
    label: str = Field(..., description="期間 e.g. 1980年→1985年")
    data: list[DataPoint]


class Result(BaseModel):
    data: list[DataSet]


class PopulationSocietyTimeseriesResponse(BaseResponseModel):
    result: Result
