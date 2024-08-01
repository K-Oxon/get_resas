from get_resas.utils.base_models import BaseRequestModel, BaseResponseModel
from get_resas.utils.get_secondary_medical_code import get_secondary_medical_code
from pydantic import BaseModel, Field

"""
リクエスト情報
"""


class MedicalPatientFlowParams(BaseModel):
    year: int = Field(..., description="年")
    prefCode: int = Field(..., description="都道府県コード")
    secondaryMedicalCode: str = Field(..., description="二次医療圏コード")
    broadCategoryCode: str | None = Field(
        None,
        description="表示分類コード(大分類) 0: 病院病床（デフォルト設定）1: うち一般病床 2: うち療養病床",
    )


class MedicalPatientFlowRequest(BaseRequestModel):
    """
    流入患者数・流出患者数

    データ提供年
        都道府県単位
        2002-2020年（3年毎）
        二次医療圏単位
        2014-2020年（3年毎）

    """

    endpoint: str = "medicalWelfare/medicalAnalysis/circle"
    params: MedicalPatientFlowParams

    @classmethod
    def generate_req_model_list_pref(cls):
        pass

    @classmethod
    def generate_req_model_list_secondary_medical_code(cls):
        secondary_medical_code_list = get_secondary_medical_code()
        year_tuple = (2014, 2017, 2020)
        req_model_list = []
        for year in year_tuple:
            for prefCode, secondary_medical_code in secondary_medical_code_list:
                req_model_list.append(
                    cls(
                        params=MedicalPatientFlowParams(
                            year=year,
                            prefCode=prefCode,
                            secondaryMedicalCode=secondary_medical_code,
                            broadCategoryCode="0",
                        )
                    )
                )
        return req_model_list


"""
レスポンス情報
"""


class Data(BaseModel):
    oppPrefCode: str = Field(..., description="流入/流出 都道府県コード")
    oppPrefName: str = Field(..., description="流入/流出 都道府県名")
    oppSecondaryMedicalAreaCode: str = Field(
        ..., description="流入/流出 二次医療圏コード"
    )
    oppSecondaryMedicalAreaName: str = Field(..., description="流入/流出 二次医療圏名")
    value: float = Field(..., description="流入/流出 患者数（単位：千人）")
    rate: float = Field(..., description="流入/流出 流出比率")


class Result(BaseModel):
    indataSum: float = Field(..., description="流入患者数合計（単位：千人）")
    outdataSum: float = Field(..., description="流出患者数合計（単位：千人）")
    prefCode: str = Field(..., description="対象の都道府県コード")
    secondaryMedicalAreaCode: str = Field(..., description="二次医療圏コード")
    indata: list[Data] = Field(..., description="流入患者数情報")
    outdata: list[Data] = Field(..., description="流出患者数情報")


class MedicalPatientFlowResponse(BaseResponseModel):
    result: Result
