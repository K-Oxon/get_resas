import dlt

from get_resas.api_client import RESASAPIClient
from get_resas.config.cities import CitiesRequest, CitiesResponse
from get_resas.utils.common_config import API_KEY
from get_resas.utils.logger import get_my_logger

logger = get_my_logger(__name__)


@dlt.resource(
    name="cities", primary_key=["prefCode", "cityCode"], write_disposition="merge"
)
def get_cities_job() -> list[any]:
    """
    市区町村一覧を取得する
    """
    api_client = RESASAPIClient(api_key=API_KEY)
    req_model_list = CitiesRequest.generate_req_model_list()
    response = api_client.fetch_iter(
        request_models=req_model_list[0:2],
        response_model=CitiesResponse,
    )
    yield response


def get_cities_pipeline() -> dlt.Pipeline:
    pipeline = dlt.pipeline(
        pipeline_name="cities",
        destination="bigquery",
        dataset_name="resas_api_data",
        export_schema_path="src/get_resas/dlt_schemas/export",
    )
    load_info = pipeline.run(get_cities_job)
    logger.info(load_info)
    return pipeline


if __name__ == "__main__":
    # データ取得のみ
    data = get_cities_job()
    print(list(data)[0:2])

    # データロードまで実行
    # get_cities_pipeline()
