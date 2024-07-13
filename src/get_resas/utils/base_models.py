from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class BaseRequestModel(BaseModel):
    """
    リクエストモデルの基底クラス
    """

    endpoint: str
    params: Optional[Dict[str, Any]] = None


class BaseResponseModel(BaseModel):
    """
    レスポンスモデルの基底クラス
    """

    message: Optional[str] = None
    result: Optional[List[Dict[str, Any]]] = None
