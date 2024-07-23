from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_city_code import get_city_code
from get_resas.utils.get_insurer_code import get_insurer_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class LtcAnalysisParams(BaseModel):
    """パラメータ情報
    名に一貫性が無くてマジでむかつく
    """

    year: int = Field(..., description="表示年")
    disp_type: int = Field(
        ..., description="1: 実数表示（デフォルト）, 2: 65歳以上人口10万人あたり"
    )
    sort_type: int = Field(2, description="1: 降順, 2: コード順")
    matter_2: int = Field(
        ..., description="表示内容 中分類 （101、102、201～204, 301, 302）"
    )
    broad_category_cd: str = Field(
        ..., description="表示分類コード(大分類) matter_2に対応させる"
    )
    middle_category_cd: str = Field(
        ..., description="表示分類コード(中分類) matter_2に対応させる"
    )
    prefCode: str = Field(..., description="都道府県コード")
    cityCode: str = Field(
        ..., description="市区町村コード 「すべての市区町村」を選択する場合は「-」"
    )
    insuranceCode: str = Field(
        ..., description="保険者コード 「すべての保険者」を選択する場合は「-」"
    )


class LtcAnalysisRequest(BaseRequestModel):
    """
    介護需給に関する地域ごとの実数

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/medicalWelfare/careAnalysis/chart.html
    """

    endpoint: str = "medicalWelfare/careAnalysis/chart"
    params: LtcAnalysisParams

    @classmethod
    def generate_req_model_list(cls, matter_2: int):
        """市町村単位のリクエストを作成"""
        match matter_2:
            case 201:
                broad_category_cd = "0"
                middle_category_cd = "000"
                year_tuple = (2021,)
            case 202:
                broad_category_cd = "0"
                middle_category_cd = "000"
                year_tuple = (2015, 2016, 2017, 2018, 2019, 2020, 2021)
            # 市町村単位の場合は201/202のみ
            case _:
                raise ValueError("matter_2が不正です")

        pref_code_list = get_city_code()
        disp_type_tuple = (1, 2)
        req_model_list = []

        for year in year_tuple:
            for pref_code, city_code in pref_code_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=LtcAnalysisParams(
                                year=year,
                                disp_type=disp_type,
                                matter_2=matter_2,
                                broad_category_cd=broad_category_cd,
                                middle_category_cd=middle_category_cd,
                                prefCode=pref_code,
                                cityCode=city_code,
                                insuranceCode="-",
                            )
                        )
                    )
        return req_model_list

    @classmethod
    def generate_req_model_list_by_insurer(cls, matter_2: int):
        """保険者コード単位のリクエストを作成"""
        match matter_2:
            case 102:
                # 要介護区分
                broad_category_cd = "0"
                middle_category_cd = "-"
                # 2006-2020年（毎年）
                year_tuple = tuple(range(2006, 2021))
            case 301:
                broad_category_cd = "-"
                middle_category_cd = "-"
                year_tuple = tuple(range(2012, 2021))
            case 302:
                # 介護サービス種
                broad_category_cd = "0"
                middle_category_cd = "000"
                year_tuple = tuple(range(2010, 2021))
            # 保険者単位の場合は102/301/302のみ
            case _:
                raise ValueError("matter_2が不正です")

        pref_city_insurer_code_list = get_insurer_code()
        disp_type_tuple = (1, 2)
        req_model_list = []

        # 年×保険者単位×表示タイプ
        for year in year_tuple:
            for pref_code, city_code, insurer_code in pref_city_insurer_code_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=LtcAnalysisParams(
                                year=year,
                                disp_type=disp_type,
                                matter_2=matter_2,
                                broad_category_cd=broad_category_cd,
                                middle_category_cd=middle_category_cd,
                                prefCode=pref_code,
                                cityCode=city_code,
                                insuranceCode=insurer_code,
                            )
                        )
                    )
        return req_model_list


"""
レスポンス情報
"""


class DataItem(BaseModel):
    code: str = Field(..., description="都道府県 or 市区町村 or 二次医療圏 コード")
    name: str = Field(..., description="都道府県 or 市区町村 or 二次医療圏 名称")
    value: int | float | None = Field(..., description="値 null有り")


class Result(BaseModel):
    """
    paramsは"matter_2"だが返り値は"matter2"
    """

    sort: str
    dispType: str
    matter1: str = Field(..., description="表示内容(大分類)")
    matter2: str = Field(..., description="表示内容(中分類)")
    broadCategoryCode: str
    middleCategoryCode: str
    year: str
    prefecture_cd: str = Field(..., description="対象の都道府県コード")
    municipality_cd: str = Field(..., description="対象の市区町村コード")
    insurance_cd: str = Field(..., description="対象の保険者コード")
    code: str = Field(
        ..., description="パラメータとして有効な 都道府県|市区町村|二次医療圏 のコード"
    )
    data: list[DataItem]


class LtcAnalysisResponse(BaseResponseModel):
    """
    介護需給に関する地域ごとの実数
    """

    result: Result
