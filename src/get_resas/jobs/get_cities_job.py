from get_resas.api_client import RESASAPIClient
from get_resas.config.cities import CitiesRequest, CitiesResponse
from get_resas.utils.common_config import API_KEY


def get_cities_job() -> CitiesResponse:
    """
    市区町村一覧を取得する
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = CitiesRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list[0:2],
        response_model=CitiesResponse,
    )
    return response


if __name__ == "__main__":
    result = get_cities_job()
    print(len(result))
