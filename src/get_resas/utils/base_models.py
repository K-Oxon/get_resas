from pydantic import BaseModel


class BaseRequestModel(BaseModel):
    """
    リクエストモデルの基底クラス
    """

    endpoint: str
    params: dict[str, any] | None = None

    class Config:
        arbitrary_types_allowed = True


class BaseResponseModel(BaseModel):
    """
    レスポンスモデルの基底クラス
    """

    message: str | None = None
    result: list[dict[str, any]] | None = None

    class Config:
        arbitrary_types_allowed = True
