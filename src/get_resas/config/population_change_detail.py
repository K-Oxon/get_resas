from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationChangeDetailParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    addArea: str | None = Field(None, description="追加エリアコード 特に気にしない")


class PopulationChangeDetailRequest(BaseRequestModel):
    """
    地域単位、年単位の出生数・死亡数／転入数・転出数の情報

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/sum/estimate.html
    """

    endpoint: str = "population/sum/estimate"
    params: PopulationChangeDetailParams

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
                    params=PopulationChangeDetailParams(
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


class YearValue(BaseModel):
    year: int = Field(..., description="年")
    value: float = Field(..., description="人口(千人)")


class DataSet(BaseModel):
    label: str = Field(
        ..., description="ラベル + 総人口・転入数・転出数・出生数・死亡数"
    )
    data: list[YearValue]


class Result(BaseModel):
    boundaryYear: int = Field(..., description="実績値と将来の推計値の区切り年")
    data: list[DataSet]


class PopulationChangeDetailResponse(BaseResponseModel):
    """
    地域単位、年単位の出生数・死亡数／転入数・転出数の情報
    都道府県単位
        総人口: 1960-2045年（5年毎）
        転入数/転出数/出生数/死亡数: 1960-2021年（毎年）
    市区町村単位
        総人口: 1995-2045年（5年毎）
        転入数/転出数/出生数/死亡数: 1994-2021年（毎年）
    実績値は2021年まで、それ以降は推計値
    """

    result: Result
