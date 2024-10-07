from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_industries_code import get_industries_code
from get_resas.utils.get_pref_code import get_pref_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class WagesByAgeIndustryParams(BaseModel):
    prefCode: str = Field(..., description="都道府県コード")
    sicCode: str = Field(..., description="産業大分類コード")
    simcCode: str = Field(..., description="産業中分類コード")
    wagesAge: str = Field(..., description="年齢区分")


class WagesByAgeIndustryRequest(BaseRequestModel):
    """
    一人当たり賃金(産業分類別、年齢別)

    説明: https://opendata.resas-portal.go.jp/docs/api/v1/municipality/wages/perYear.html

    注意点
      - 産業大分類コードは「-」を指定する（大中指定すると値が入ってない謎仕様）
    """

    endpoint: str = "municipality/wages/perYear"
    params: WagesByAgeIndustryParams

    @classmethod
    def generate_req_model_list(cls):
        pref_code_list = get_pref_code()
        industries_code_list = get_industries_code()
        # 1: 総数, 2: 〜19歳, ..., 13: 70歳〜
        wages_age_tuple = tuple(range(1, 14))
        req_model_list = []
        # 47都道府県 × 99産業分類 × 13年齢区分
        for pref_code in pref_code_list:
            for industries_code in industries_code_list:
                for wages_age in wages_age_tuple:
                    req_model_list.append(
                        cls(
                            params=WagesByAgeIndustryParams(
                                prefCode=str(pref_code),
                                sicCode="-",
                                simcCode=industries_code[1],
                                wagesAge=str(wages_age),
                            )
                        )
                    )
        return req_model_list


"""
レスポンス情報
"""


class DataPoint(BaseModel):
    year: int = Field(..., description="年度")
    value: float = Field(..., description="一人当たり賃金(万円)")


class Result(BaseModel):
    prefCode: int
    prefName: str
    sicName: str = Field(..., description="産業大分類名、取得できない場合は空文字")
    sicCode: str = Field(..., description="産業大分類コード、取得できない場合は空文字")
    simcName: str = Field(..., description="産業中分類名、取得できない場合は空文字")
    simcCode: str = Field(..., description="産業中分類コード、取得できない場合は空文字")
    data: list[DataPoint]


class WagesByAgeIndustryResponse(BaseResponseModel):
    """
    一人当たり賃金(産業分類別、年齢別)
    """

    result: Result
