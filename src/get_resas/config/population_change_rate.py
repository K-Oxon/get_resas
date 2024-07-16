from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationChangeParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    addArea: str | None = Field(None, description="追加エリアコード 特に気にしない")


class PopulationChangeRequest(BaseRequestModel):
    """
    地域単位、年単位の人口増減率情報

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/sum/perYear.html
    """

    endpoint: str = "population/sum/perYear"
    params: PopulationChangeParams

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
                    params=PopulationChangeParams(
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


class LineData(BaseModel):
    year: int = Field(..., description="年")
    value: float = Field(..., description="総人口の比率")


class Line(BaseModel):
    boundaryYear: int = Field(..., description="実績値と将来の推計値の区切り年")
    data: list[LineData]


class ClassData(BaseModel):
    label: str = Field(..., description="老年人口 生産年齢人口 年少人口")
    value: float = Field(..., description="比率")


class BarData(BaseModel):
    year: int = Field(..., description="年")
    sum_: float = Field(
        ..., description="総人口の比率（折れ線の総人口の比率と同じデータ）", alias="sum"
    )
    class_: list[ClassData] = Field(..., alias="class")


class Bar(BaseModel):
    data: list[BarData]


class Result(BaseModel):
    line: Line
    bar: Bar


class PopulationChangeResponse(BaseResponseModel):
    """
    地域単位、年単位の人口増減率情報
    都道府県単位
    1965-2045年（5年毎）
    市区町村単位
    1985-2045年（5年毎）
    """

    result: Result
