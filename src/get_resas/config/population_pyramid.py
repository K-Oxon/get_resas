from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationPyramidParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    yearLeft: int = Field(..., description="年度1 1980-2045 5年毎")
    yearRight: int = Field(..., description="年度2 1980-2045 5年毎")
    addArea: str | None = Field(None, description="追加エリアコード 特に気にしない")
    year: int = Field(
        ...,
        description="dummy yearLeftが色々悪さするのでparamsには無いがキーとして使う",
    )


class PopulationPyramidRequest(BaseRequestModel):
    """
    地域単位、年単位の人口ピラミッドデータ

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/composition/pyramid.html
    """

    endpoint: str = "population/composition/pyramid"
    params: PopulationPyramidParams

    @classmethod
    def generate_req_model_list(cls):
        """全パラメータの組み合わせを生成
        1980-2045 5年毎と、全市区町村を組み合わせてリクエストモデルを生成
        get_city_code()で出力される[tuple(prefCode, cityCode)]を利用
        """
        year_list = [
            1980,
            1985,
            1990,
            1995,
            2000,
            2005,
            2010,
            2015,
            2020,
            2025,
            2030,
            2035,
            2040,
            2045,
        ]
        pref_city_code_list = get_city_code()
        req_model_list = []
        for year in year_list:
            for pref_code, city_code in pref_city_code_list:
                req_model_list.append(
                    cls(
                        params=PopulationPyramidParams(
                            prefCode=pref_code,
                            cityCode=city_code,
                            yearLeft=year,
                            yearRight=1980,
                            year=year,
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


class AgeGroupData(BaseModel):
    class_: str = Field(..., description="年齢階級", alias="class")
    man: int = Field(..., description="男性人口(人)")
    manPercent: float = Field(..., description="男性人口(パーセント)")
    woman: int = Field(..., description="女性人口(人)")
    womanPercent: float = Field(..., description="女性人口(パーセント)")


class YearData(BaseModel):
    year: int = Field(..., description="指定された年")
    oldAgeCount: int = Field(..., description="65歳以上の老年人口(人)")
    oldAgePercent: int = Field(..., description="65歳以上の老年人口(パーセント)")
    middleAgeCount: int = Field(..., description="15歳～64歳の生産年齢人口(人)")
    middleAgePercent: int = Field(
        ..., description="15歳～64歳の生産年齢人口(パーセント)"
    )
    newAgeCount: int = Field(..., description="0歳～14歳の年少人口(人)")
    newAgePercent: int = Field(..., description="0歳～14歳の年少人口(パーセント)")
    data: list[AgeGroupData]


class Result(BaseModel):
    yearLeft: YearData = Field(..., description="年度1")
    yearRight: YearData = Field(..., description="年度2")


class PopulationPyramidResponse(BaseResponseModel):
    """
    地域単位、年単位の人口ピラミッドデータ
    """

    result: Result
