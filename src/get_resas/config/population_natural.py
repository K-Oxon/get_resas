from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class PopulationNaturalParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    ageFrom: str = Field(
        ..., description="表示する年齢(開始) '-'（下限なし）5-85（5歳毎）"
    )
    ageTo: str = Field(
        ..., description="表示する年齢(終了) '-'（上限なし）4-89（5歳毎）"
    )


class PopulationNaturalRequest(BaseRequestModel):
    """
    地域単位、年単位の人口自然増減情報

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/population/nature.html
    """

    endpoint: str = "population/nature"
    params: PopulationNaturalParams

    @classmethod
    def generate_req_model_list(cls):
        """全パラメータの組み合わせを生成
        市町村 × (開始年齢, 終了年齢)の組み合わせ 約40000件
        """

        pref_city_code_list = get_city_code()
        # 開始年齢 5-85(5歳刻み)
        age_from_list = ["-"]
        age_from_list.extend([str(i) for i in range(5, 86, 5)])
        age_from_list.extend(["85"])  # 最後の"85"-"-" のために追加
        # 終了年齢 4-89(5歳刻み)
        age_to_list = [str(i) for i in range(4, 90, 5)]
        age_to_list.extend(["-"])
        if len(age_from_list) != len(age_to_list):
            raise ValueError("age_from_listとage_to_listの長さが異なります")
        # それぞれの順番の組み合わせを出力
        age_group_list: list[tuple[str, str]] = []
        for i in range(len(age_from_list)):
            age_group_list.append((age_from_list[i], age_to_list[i]))

        req_model_list = []
        for pref_code, city_code in pref_city_code_list:
            for age_from, age_to in age_group_list:
                req_model_list.append(
                    cls(
                        params=PopulationNaturalParams(
                            prefCode=pref_code,
                            cityCode=city_code,
                            ageFrom=age_from,
                            ageTo=age_to,
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
    yearRange: str = Field(
        ...,
        description="年度範囲 市区町村コードが-の場合は0、市区町村コードが-でない場合はyyyy-yyyyの形式",
    )
    year: int = Field(
        ...,
        description="年 市区町村コードが-の場合は年、市区町村コードが-でない場合はyearRangeの間の値（例:2000-2005の時2003）",
    )
    value: float = Field(..., description="	合計特殊出生率")


class Line(BaseModel):
    boundaryYear: int = Field(..., description="実績値と将来の推計値の区切り年")
    data: list[LineData]


class BarData(BaseModel):
    year: int = Field(..., description="年度")
    value: int = Field(..., description="人数(千人)")


class Bar(BaseModel):
    boundaryYear: int = Field(..., description="実績値と将来の推計値の区切り年")
    mandata: list[BarData]
    womandata: list[BarData]


class Result(BaseModel):
    line: Line
    bar: Bar


class PopulationNaturalResponse(BaseResponseModel):
    """
    地域単位、年単位の人口自然増減情報
    都道府県単位
    1980、1985-2021年（毎年）
    市区町村単位
    1980-2045年（5年毎）
    実績値は2020年まで、それ以降は推計値
    """

    result: Result
