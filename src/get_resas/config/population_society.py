from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationSocietyParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )


class PopulationSocietyRequest(BaseRequestModel):
    """
    年齢階級別純移動数
    データ提供: 2010-2022年（毎年）

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/society/forAgeClass.html
    """

    endpoint: str = "population/society/forAgeClass"
    params: PopulationSocietyParams

    @classmethod
    def generate_req_model_list(cls):
        """全パラメータの組み合わせを生成
        get_city_code()で出力される[tuple(prefCode, cityCode)]を利用
        """

        pref_city_code_list = get_city_code()
        req_model_list = []
        for pref_code, city_code in pref_city_code_list:
            req_model_list.append(
                cls(
                    params=PopulationSocietyParams(
                        prefCode=pref_code,
                        cityCode=city_code,
                    )
                )
            )
        return req_model_list

    @classmethod
    def generate_req_model_list_pref(cls):
        """都道府県コードのみのリクエストモデルを生成"""
        # 未実装
        pass


"""
レスポンス情報
"""


class AgeClassData(BaseModel):
    ageClass: int = Field(..., description="年齢階級コード")
    age: str = Field(..., description="年齢階級")
    value: int = Field(..., description="移動数")


class TotalData(BaseModel):
    value: int = Field(..., description="純移動数")


class YearData(BaseModel):
    """
    TODO: それぞれのAgeClassesが無い場合がある
    """

    year: int = Field(..., description="年")
    positiveAgeClasses: list[AgeClassData]
    negativeAgeClasses: list[AgeClassData]
    total: TotalData


class Result(BaseModel):
    data: list[YearData]


class PopulationSocietyResponse(BaseResponseModel):
    """
    年齢階級別純移動数
    2010-2022年（毎年）
    """

    result: Result
