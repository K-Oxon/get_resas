from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from get_resas.utils.get_pref_code import get_pref_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationCompositionParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(..., description="市区町村コード")
    addArea: str | None = Field(None, description="追加エリアコード 特に気にしない")


class PopulationCompositionRequest(BaseRequestModel):
    """
    地域単位、年単位の年齢構成のデータ

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/composition/perYear.html
    """

    endpoint: str = "population/composition/perYear"
    params: PopulationCompositionParams

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
                    params=PopulationCompositionParams(
                        prefCode=pref_code, cityCode=city_code
                    )
                )
            )
        return req_model_list

    @classmethod
    def generate_req_model_list_pref(cls):
        """都道府県コードのみのリクエストモデルを生成"""
        pref_code_list = get_pref_code()
        req_model_list = []
        for pref_code in pref_code_list:
            req_model_list.append(
                cls(
                    params=PopulationCompositionParams(prefCode=pref_code, cityCode="-")
                )
            )
        return req_model_list


"""
レスポンス情報
"""


class PopulationDataPoint(BaseModel):
    year: int
    value: int
    rate: float | None = None


class PopulationCategory(BaseModel):
    label: str
    data: list[PopulationDataPoint]


class PopulationData(BaseModel):
    boundaryYear: int
    data: list[PopulationCategory]


class PopulationCompositionResponse(BaseResponseModel):
    """
    地域単位、年単位の年齢構成のデータ
    """

    result: PopulationData
