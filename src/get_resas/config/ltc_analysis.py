from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_ltc_service_category import get_ltc_service_category
from get_resas.utils.get_pref_code import get_pref_code
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
    def _generate_categories_code(cls, matter_2: int) -> list[tuple[str, str]]:
        """大分類と中分類を生成"""
        match matter_2:
            case 102:
                # 要介護区分 大分類コードは0から8, 中分類コードは"-"
                broad_category_cd_list = [str(i) for i in range(0, 9)]
                middle_category_cd_list = ["-"] * len(broad_category_cd_list)
                return list(zip(broad_category_cd_list, middle_category_cd_list))
            case 201 | 202:
                return get_ltc_service_category()
            case 203 | 204 | 301:
                return [("-", "-")]
            case 101 | 302:
                # 介護サービス種（すべての中分類） 0-3, 000-300の組み合わせ
                return [(f"{i:01d}", f"{i*100:03d}") for i in range(0, 4)]
            case _:
                raise ValueError("matter_2が不正です")

    @classmethod
    def generate_req_model_list_by_pref(cls, matter_2: int):
        """都道府県単位のリクエストを作成
        都道府県コードが何かを入ってさえいれば全都道府県出力される
        """
        match matter_2:
            case 101:
                # 2014年から2021年まで毎年
                year_tuple = tuple(range(2014, 2022))
                disp_type_tuple = (1, 2)
            case 102:
                # 要介護区分
                category_cd_list = cls._generate_categories_code(matter_2)
                # 2006-2020年（毎年）
                year_tuple = tuple(range(2006, 2021))
                disp_type_tuple = (1, 2)
            case 201:
                year_tuple = (2021,)
                disp_type_tuple = (1, 2)
            case 202:
                year_tuple = tuple(range(2015, 2022))
                disp_type_tuple = (1, 2)
            case 203:
                year_tuple = tuple(range(2017, 2021))
                disp_type_tuple = (1, 2)
            case 204:
                year_tuple = tuple(range(2007, 2021))
                disp_type_tuple = (1, 2)
            case 301:
                year_tuple = tuple(range(2012, 2022))
                disp_type_tuple = (1,)
            case 302:
                year_tuple = tuple(range(2010, 2021))
                disp_type_tuple = (1, 2)
            case _:
                raise ValueError("matter_2が不正です")
        category_cd_list = cls._generate_categories_code(matter_2)
        req_model_list = []

        # 年 × 分類 × 表示タイプ でループ
        for year in year_tuple:
            for category_cd in category_cd_list:
                for disp_type in disp_type_tuple:
                    req_model_list.append(
                        cls(
                            params=LtcAnalysisParams(
                                year=year,
                                disp_type=disp_type,
                                matter_2=matter_2,
                                broad_category_cd=category_cd[0],
                                middle_category_cd=category_cd[1],
                                prefCode="1",  # 適当な値
                                cityCode="-",
                                insuranceCode="-",
                            )
                        )
                    )
        return req_model_list

    @classmethod
    def generate_req_model_list(cls, matter_2: int):
        """市町村単位のリクエストを作成
        市市町村単位の場合はprefCodeに入れた都道府県ごとに取得する必要がある
        （市町村コードは何を入れても都道府県が優先され、都道府県配下の市町村全て出力される）

        都道府県・二次医療圏の場合は何かを入れてさえいれば全部出力される

        イミフ仕様
        """
        match matter_2:
            case 201:
                category_cd_list = cls._generate_categories_code(matter_2)
                year_tuple = (2021,)
            case 202:
                category_cd_list = cls._generate_categories_code(matter_2)
                year_tuple = (2015, 2016, 2017, 2018, 2019, 2020, 2021)
            # 市町村単位の場合は201/202のみ
            case _:
                raise ValueError("matter_2が不正です")

        pref_code_list = get_pref_code()
        disp_type_tuple = (1, 2)
        req_model_list = []

        # 年 × 47都道府県 × 分類 × 表示タイプ でループ
        for year in year_tuple:
            for pref_code in pref_code_list:
                for category_cd in category_cd_list:
                    for disp_type in disp_type_tuple:
                        req_model_list.append(
                            cls(
                                params=LtcAnalysisParams(
                                    year=year,
                                    disp_type=disp_type,
                                    matter_2=matter_2,
                                    broad_category_cd=category_cd[0],
                                    middle_category_cd=category_cd[1],
                                    prefCode=str(pref_code),
                                    cityCode="01100",  # 適当な値
                                    insuranceCode="-",
                                )
                            )
                        )
        return req_model_list

    @classmethod
    def generate_req_model_list_by_insurer(cls, matter_2: int):
        """保険者コード単位のリクエストを作成
        市町村コードと保険者コードは適当な何かが入っていれば指定の都道府県コードの全ての保険者のデータが返ってくる
        """
        match matter_2:
            case 102:
                # 要介護区分
                category_cd_list = cls._generate_categories_code(matter_2)
                # 2006-2020年（毎年）
                year_tuple = tuple(range(2006, 2021))
                disp_type_tuple = (1, 2)
            case 301:
                category_cd_list = cls._generate_categories_code(matter_2)
                # 毎年と書いてあるがデータを見る限り3年毎ぽい(同じデータが連続している)
                year_tuple = tuple(range(2012, 2021))
                # 301: 介護保険料はdisp_type=2(2 : 65歳以上人口10万人あたり表示)では値が返ってこない
                disp_type_tuple = (1,)
            case 302:
                # 介護サービス種
                category_cd_list = cls._generate_categories_code(matter_2)
                year_tuple = tuple(range(2010, 2021))
                disp_type_tuple = (1, 2)
            # 保険者単位の場合は102/301/302のみ
            case _:
                raise ValueError("matter_2が不正です")

        pref_list = get_pref_code()
        req_model_list = []

        # 年×保険者単位×分類×表示タイプ
        for year in year_tuple:
            for pref_code in pref_list:
                for category_cd in category_cd_list:
                    for disp_type in disp_type_tuple:
                        req_model_list.append(
                            cls(
                                params=LtcAnalysisParams(
                                    year=year,
                                    disp_type=disp_type,
                                    matter_2=matter_2,
                                    broad_category_cd=category_cd[0],
                                    middle_category_cd=category_cd[1],
                                    prefCode=str(pref_code),
                                    cityCode="01100",  # 適当な値
                                    insuranceCode="01100",  # 適当な値
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

    注意点:
      - 都道府県・市区町村・保険者は値が入っていれば全部返ってくる（都道府県コードのみ有効）
      - 保険者の301(介護保険料)はdisp_type=2(2 : 65歳以上人口10万人あたりで表示する)では値が返ってこない
    """

    result: Result
