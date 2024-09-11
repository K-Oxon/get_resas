from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_medical_injury_classification import (
    get_medical_injury_classification,
)
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
    def _generate_categories_code(cls, matter2: int) -> list[tuple[str, str]]:
        """matter2に対応する大分類と中分類を生成"""
        match matter2:
            case 102 | 103:
                # 傷病分類
                return get_medical_injury_classification()
            case 201 | 202:
                # 診療科分類（医療機関） "00"から"43"まで
                # 実は市町村単位では00（すべての診療科）しか存在しない
                broad_category_cd_list = [str(f"{i:02d}") for i in range(0, 44)]
                middle_category_cd_list = ["-"] * len(broad_category_cd_list)
                return list(zip(broad_category_cd_list, middle_category_cd_list))
            case 204:
                # 病床種類 "00"から"05"まで
                broad_category_cd_list = [str(f"{i:02d}") for i in range(0, 6)]
                middle_category_cd_list = ["-"] * len(broad_category_cd_list)
                return list(zip(broad_category_cd_list, middle_category_cd_list))
            case 205:
                # 主たる診療科分類（医師） "00"から"43"まで
                broad_category_cd_list = [str(f"{i:02d}") for i in range(0, 44)]
                middle_category_cd_list = ["-"] * len(broad_category_cd_list)
                return list(zip(broad_category_cd_list, middle_category_cd_list))
            case 207:
                # 病院・診療所別 "00"から "02"まで
                broad_category_cd_list = [str(f"{i:02d}") for i in range(0, 3)]
                middle_category_cd_list = ["-"] * len(broad_category_cd_list)
                return list(zip(broad_category_cd_list, middle_category_cd_list))
            case 203 | 206 | 208:
                return [("-", "-")]
            case _:
                raise ValueError("matter2が不正です")

    @classmethod
    def generate_req_model_list_prefecture(cls, matter2: int):
        """都道府県単位のリクエストを生成
        有効な都道府県コードを入れると47個の全ての都道府県のデータが取れる
        """
        match matter2:
            case 102 | 103 | 203 | 204:
                # 3年毎(2002-2020年)
                year_tuple = tuple(range(2002, 2021, 3))
            case 201 | 202:
                # 3年毎(2008-2020年)
                year_tuple = tuple(range(2008, 2021, 3))
            case 205:
                year_tuple = tuple(range(2008, 2021, 2))
            case 206 | 207 | 208:
                year_tuple = tuple(range(2000, 2021, 2))
            case _:
                raise ValueError("matter2が不正です")
        disp_type_tuple = (1, 2)
        category_cd_list = cls._generate_categories_code(matter2)

        req_model_list = []
        # 年 × 分類 × 表示タイプごとにリクエストモデルを生成
        for year in year_tuple:
            for category_cd in category_cd_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=MedicalAnalysisParams(
                                year=year,
                                dispType=disp_type,
                                sort=2,  # なぜか必要
                                matter2=matter2,
                                broadCategoryCode=category_cd[0],
                                middleCategoryCode=category_cd[1],
                                prefCode="1",  # 有効な適当な値
                                cityCode="-",
                                secondaryMedicalCode="-",
                            )
                        )
                    )
        return req_model_list

    @classmethod
    def generate_req_model_list_city(cls, matter2: int):
        """市町村単位のリクエストを生成
        市町村単位の場合はprefCodeに入れた都道府県ごとに取得する必要がある
        （市町村コードは何を入れても都道府県が優先され、都道府県配下の市町村全て出力される）

        201/202の場合はcategory_cd_listが("00", "-")のみ有効

        イミフ仕様
        """
        match matter2:
            # matter2が201-204の場合 -> 2002-2020年（3年毎）
            case 201 | 202 | 203 | 204:
                year_tuple = tuple(range(2002, 2021, 3))
            # 205の場合 -> 2008-2020年（2年毎）
            case 205:
                year_tuple = tuple(range(2008, 2021, 2))
            # 206,208の場合 -> 2000-2020年（2年毎）
            case 206 | 208:
                year_tuple = tuple(range(2000, 2021, 2))
            case _:
                raise ValueError("matter2が不正です")
        # 市町村単位の場合は全ての診療科のみ有効という仕様
        if matter2 == 201 or matter2 == 202:
            category_cd_list = [("00", "-")]
        else:
            category_cd_list = cls._generate_categories_code(matter2)
        pref_code_list = get_pref_code()
        disp_type_tuple = (1, 2)
        req_model_list = []
        # 年 × 47都道府県 × 分類 × 表示タイプごとにリクエストモデルを生成
        for year in year_tuple:
            for pref_code in pref_code_list:
                for category_cd in category_cd_list:
                    for disp_type in disp_type_tuple:
                        req_model_list.append(
                            cls(
                                params=MedicalAnalysisParams(
                                    year=year,
                                    dispType=disp_type,
                                    sort=2,  # なぜか必要
                                    matter2=matter2,
                                    broadCategoryCode=category_cd[0],
                                    middleCategoryCode=category_cd[1],
                                    prefCode=str(pref_code),
                                    cityCode="01100",  # 適当な値でOK
                                    secondaryMedicalCode="-",
                                )
                            )
                        )
        return req_model_list

    @classmethod
    def generate_req_model_list_secondary_medical_code(cls, matter2: int):
        """二次医療圏単位のリクエストを生成
        有効な都道府県、市町村、二次医療圏コードを入れると335個の全ての二次医療圏のデータが取れる

        """
        match matter2:
            case 102 | 201 | 202 | 203 | 204:
                year_tuple = (2014, 2017, 2020)  # 3年毎
            case 205 | 206 | 208:
                year_tuple = (2014, 2016, 2018, 2020)  # 2年毎
            case _:
                raise ValueError("matter2が不正です")
        disp_type_tuple = (1, 2)
        category_cd_list = cls._generate_categories_code(matter2)

        req_model_list = []
        # 年 × 分類 × 表示タイプごとにリクエストモデルを生成
        for year in year_tuple:
            for category_cd in category_cd_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=MedicalAnalysisParams(
                                year=year,
                                dispType=disp_type,
                                sort=2,  # なぜか必要
                                matter2=matter2,
                                broadCategoryCode=category_cd[0],
                                middleCategoryCode=category_cd[1],
                                prefCode="1",  # 有効な適当な値
                                cityCode="01202",  # 有効な適当な値
                                secondaryMedicalCode="0101",  # 有効な適当な値
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
