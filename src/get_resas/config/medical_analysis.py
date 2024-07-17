from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_pref_code import get_pref_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class MedicalAnalysisParams(BaseModel):
    year: int = Field(..., description="表示年")
    dispType: int | None = Field(
        None, description="1: 実数表示（デフォルト）, 2: 人口10万人あたり"
    )
    sort: int | None = Field(None, description="1: 降順, 2: コード順")
    matter2: int = Field(..., description="データ種別 （102、103、201～208）")
    broadCategoryCode: str = Field(..., description="大分類コード matter2に対応させる")
    middleCategoryCode: str = Field(..., description="中分類コード matter2に対応させる")
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    secondaryMedicalCode: str = Field(
        ..., description="二次医療圏コード 「すべての二次医療圏」を選択する場合は「-」"
    )


class MedicalAnalysisRequest(BaseRequestModel):
    """
    医療需給_地域間比較

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/medicalWelfare/medicalAnalysis/chart.html
    """

    endpoint: str = "medicalWelfare/medicalAnalysis/chart"
    params: MedicalAnalysisParams

    @classmethod
    def generate_req_model_list(cls, matter2: int):
        """市町村単位のリクエストを生成（市町村単位）
        市町村単位の場合はprefCodeに入れた都道府県ごとに取得する必要がある
        （市町村コードは何を入れても都道府県が優先され、都道府県配下の市町村全て出力される）

        都道府県・二次医療圏の場合は何かを入れてさえいれば全部出力される

        イミフ仕様
        """
        match matter2:
            # matter2が201-204の場合 -> 2002-2020年（3年毎）
            case 201 | 202 | 204:
                year_tuple = (2002, 2005, 2008, 2011, 2014, 2017, 2020)
                broad_category_code = "00"  # 全て
            case 203:
                year_tuple = (2002, 2005, 2008, 2011, 2014, 2017, 2020)
                broad_category_code = "-"
            # 205の場合 -> 2008-2020年（2年毎）
            case 205:
                year_tuple = (
                    2008,
                    2010,
                    2012,
                    2014,
                    2016,
                    2018,
                    2020,
                )
                broad_category_code = "00"
            # 206,208の場合 -> 2000-2020年（2年毎）
            case 206 | 208:
                year_tuple = (
                    2000,
                    2002,
                    2004,
                    2006,
                    2008,
                    2010,
                    2012,
                    2014,
                    2016,
                    2018,
                    2020,
                )
                broad_category_code = "-"
            case _:
                raise ValueError("matter2が不正です")
        pref_code_list = get_pref_code()
        disp_type_tuple = (1, 2)
        req_model_list = []
        # 年 × 47都道府県 × 表示タイプごとにリクエストモデルを生成
        for year in year_tuple:
            for pref_code in pref_code_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=MedicalAnalysisParams(
                                year=year,
                                dispType=disp_type,
                                sort=2,  # なぜか必要
                                matter2=matter2,
                                broadCategoryCode=broad_category_code,
                                middleCategoryCode="-",
                                prefCode=str(pref_code),
                                cityCode="01100",  # 適当な値でOK
                                secondaryMedicalCode="-",
                            )
                        )
                    )
        return req_model_list


"""
レスポンス情報
"""


class DataItem(BaseModel):
    code: str = Field(..., description="都道府県 or 市区町村 or 二次医療圏 コード")
    name: str = Field(..., description="都道府県 or 市区町村 or 二次医療圏 名")
    value: float = Field(..., description="値")


class Result(BaseModel):
    sort: str
    dispType: str
    matter1: str = Field(..., description="表示内容（１：医療需要、２：医療共有）")
    matter2: str
    broadCategoryCode: str
    middleCategoryCode: str
    year: str
    prefecture_cd: str = Field(..., description="対象の都道府県コード")
    municipality_cd: str = Field(..., description="対象の市区町村コード")
    secondary_medical_cd: str = Field(..., description="対象の二次医療圏コード")
    code: str = Field(
        ..., description="多分 有効な 都道府県|市区町村|二次医療圏 のコード"
    )
    data: list[DataItem]


class MedicalAnalysisResponse(BaseResponseModel):
    """
    医療需給_地域間比較
    """

    result: Result
